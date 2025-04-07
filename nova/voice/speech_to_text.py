#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para el reconocimiento de voz (Speech-to-Text)
Utiliza faster-whisper para convertir la voz del usuario en texto
"""

import logging
import numpy as np
import pyaudio
import threading
import time
import wave
from pathlib import Path
from typing import Optional, Callable, Dict, Union

# Intentar importar faster-whisper, con manejo de error si no está instalado
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("faster-whisper no está instalado. El reconocimiento de voz no estará disponible.")
    logging.info("Instala faster-whisper con: pip install faster-whisper")

logger = logging.getLogger('nova.speech_to_text')

class SpeechToText:
    """Clase para manejar la conversión de voz a texto"""
    
    def __init__(self, model_size: str = "base", device: str = "cpu", 
                compute_type: str = "int8", language: str = "es"):
        """Inicializa el sistema de reconocimiento de voz
        
        Args:
            model_size: Tamaño del modelo Whisper (tiny, base, small, medium, large)
            device: Dispositivo para inferencia (cpu, cuda, auto)
            compute_type: Tipo de cómputo (float16, int8)
            language: Código de idioma para el reconocimiento (es, en, etc.)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.model = None
        self.is_listening = False
        self.audio_thread = None
        self.callback = None
        
        # Configuración de audio
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.silence_threshold = 300  # Umbral para detectar silencio
        self.silence_duration = 1.5   # Segundos de silencio para considerar fin de habla
        
        # Inicializar el modelo si está disponible
        if WHISPER_AVAILABLE:
            self._load_model()
        else:
            logger.warning("No se pudo inicializar el modelo de reconocimiento de voz")
    
    def _load_model(self) -> None:
        """Carga el modelo Whisper"""
        try:
            logger.info(f"Cargando modelo Whisper {self.model_size} en {self.device}...")
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type
            )
            logger.info("Modelo Whisper cargado correctamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo Whisper: {str(e)}")
            self.model = None
    
    def start_listening(self, callback: Optional[Callable[[str], None]] = None) -> bool:
        """Inicia la escucha continua del micrófono
        
        Args:
            callback: Función a llamar cuando se detecte texto (opcional)
            
        Returns:
            bool: True si se inició correctamente, False en caso contrario
        """
        if not WHISPER_AVAILABLE or self.model is None:
            logger.error("No se puede iniciar la escucha: modelo no disponible")
            return False
        
        if self.is_listening:
            logger.warning("Ya se está escuchando. Detén la escucha actual primero.")
            return False
        
        self.callback = callback
        self.is_listening = True
        self.audio_thread = threading.Thread(target=self._listen_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        logger.info("Escucha de voz iniciada")
        return True
    
    def stop_listening(self) -> None:
        """Detiene la escucha del micrófono"""
        self.is_listening = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)
            logger.info("Escucha de voz detenida")
    
    def _listen_loop(self) -> None:
        """Bucle principal de escucha y procesamiento de audio"""
        audio = pyaudio.PyAudio()
        
        try:
            # Abrir stream de audio
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            logger.info("Micrófono abierto y listo para escuchar")
            
            while self.is_listening:
                # Capturar audio hasta detectar silencio
                frames, is_speech_detected = self._capture_speech(stream)
                
                if is_speech_detected and frames:
                    # Guardar audio temporal y transcribir
                    temp_file = self._save_temp_audio(frames)
                    text = self._transcribe_audio(temp_file)
                    
                    if text and self.callback:
                        self.callback(text)
                
                # Pequeña pausa para evitar uso excesivo de CPU
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error en el bucle de escucha: {str(e)}")
        finally:
            # Limpiar recursos
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            audio.terminate()
    
    def _capture_speech(self, stream) -> tuple:
        """Captura audio hasta detectar silencio
        
        Args:
            stream: Stream de audio abierto
            
        Returns:
            tuple: (frames de audio, booleano indicando si se detectó habla)
        """
        frames = []
        silent_chunks = 0
        silent_threshold = int(self.silence_duration * self.rate / self.chunk)
        is_speech = False
        
        # Escuchar hasta detectar silencio prolongado después de habla
        while self.is_listening:
            data = stream.read(self.chunk, exception_on_overflow=False)
            frames.append(data)
            
            # Convertir a array y calcular volumen
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_data).mean()
            
            # Detectar si hay habla o silencio
            if volume > self.silence_threshold:
                is_speech = True
                silent_chunks = 0
            elif is_speech:
                silent_chunks += 1
                
                # Si hay suficiente silencio después de habla, terminar
                if silent_chunks > silent_threshold:
                    break
            
            # Si llevamos muchos frames sin habla, reiniciar
            if len(frames) > 300 and not is_speech:  # ~10 segundos sin habla
                return [], False
        
        return frames, is_speech
    
    def _save_temp_audio(self, frames) -> str:
        """Guarda los frames de audio en un archivo temporal
        
        Args:
            frames: Lista de frames de audio capturados
            
        Returns:
            str: Ruta al archivo temporal
        """
        # Crear directorio temporal si no existe
        temp_dir = Path("./temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Generar nombre de archivo único
        temp_file = str(temp_dir / f"speech_{int(time.time())}.wav")
        
        # Guardar audio en formato WAV
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
        
        return temp_file
    
    def _transcribe_audio(self, audio_file: str) -> str:
        """Transcribe un archivo de audio a texto
        
        Args:
            audio_file: Ruta al archivo de audio
            
        Returns:
            str: Texto transcrito
        """
        if not self.model:
            logger.error("No se puede transcribir: modelo no disponible")
            return ""
        
        try:
            logger.debug(f"Transcribiendo archivo: {audio_file}")
            segments, info = self.model.transcribe(
                audio_file, 
                language=self.language,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Unir todos los segmentos en un solo texto
            text = " ".join([segment.text for segment in segments])
            text = text.strip()
            
            logger.info(f"Transcripción completada: '{text}'")
            return text
            
        except Exception as e:
            logger.error(f"Error al transcribir audio: {str(e)}")
            return ""
    
    def transcribe_file(self, file_path: str) -> str:
        """Transcribe un archivo de audio existente
        
        Args:
            file_path: Ruta al archivo de audio
            
        Returns:
            str: Texto transcrito
        """
        if not WHISPER_AVAILABLE or self.model is None:
            logger.error("No se puede transcribir: modelo no disponible")
            return ""
        
        return self._transcribe_audio(file_path)