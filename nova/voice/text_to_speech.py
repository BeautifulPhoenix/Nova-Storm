#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para la síntesis de voz (Text-to-Speech)
Utiliza Coqui TTS para convertir texto en voz natural femenina
"""

import logging
import os
import time
import numpy as np
import sounddevice as sd
from pathlib import Path
from typing import Optional, Union, Dict

# Intentar importar TTS, con manejo de error si no está instalado
try:
    import torch
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logging.warning("TTS no está instalado. La síntesis de voz no estará disponible.")
    logging.info("Instala TTS con: pip install TTS")

logger = logging.getLogger('nova.text_to_speech')

class TextToSpeech:
    """Clase para manejar la conversión de texto a voz"""
    
    def __init__(self, model_name: str = "tts_models/es/css10/vits", 
                 speaker: Optional[str] = None,
                 language: str = "es",
                 device: str = "cpu"):
        """
        Inicializa el sistema de síntesis de voz
        
        Args:
            model_name: Nombre del modelo TTS a utilizar
            speaker: ID del hablante para modelos multi-hablante
            language: Código de idioma para la síntesis
            device: Dispositivo para inferencia (cpu, cuda)
        """
        self.model_name = model_name
        self.speaker = speaker
        self.language = language
        self.device = device
        self.tts = None
        self.sample_rate = 22050  # Frecuencia de muestreo estándar para TTS
        
        # Inicializar el modelo si está disponible
        if TTS_AVAILABLE:
            self._load_model()
        else:
            logger.warning("No se pudo inicializar el modelo de síntesis de voz")
    
    def _load_model(self) -> None:
        """Carga el modelo TTS"""
        try:
            logger.info(f"Cargando modelo TTS {self.model_name} en {self.device}...")
            self.tts = TTS(model_name=self.model_name, progress_bar=False).to(self.device)
            logger.info("Modelo TTS cargado correctamente")
            
            # Verificar si el modelo soporta múltiples hablantes
            if self.speaker and hasattr(self.tts, 'speakers') and self.tts.speakers:
                if self.speaker not in self.tts.speakers:
                    available_speakers = self.tts.speakers[:5]  # Mostrar solo los primeros 5 para no saturar el log
                    logger.warning(f"Hablante '{self.speaker}' no disponible. Opciones: {available_speakers}...")
                    self.speaker = self.tts.speakers[0]  # Usar el primer hablante disponible
                    logger.info(f"Usando hablante: {self.speaker}")
            
        except Exception as e:
            logger.error(f"Error al cargar el modelo TTS: {str(e)}")
            self.tts = None
    
    def synthesize(self, text: str, output_file: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Sintetiza texto a voz
        
        Args:
            text: Texto a convertir en voz
            output_file: Ruta donde guardar el audio (opcional)
            
        Returns:
            np.ndarray: Array de audio si no se especifica archivo de salida
                       None si se guarda en archivo o hay error
        """
        if not TTS_AVAILABLE or self.tts is None:
            logger.error("No se puede sintetizar: modelo TTS no disponible")
            return None
        
        try:
            logger.debug(f"Sintetizando texto: '{text[:50]}...'")
            
            # Preparar argumentos para la síntesis
            kwargs = {"text": text, "language": self.language}
            
            # Agregar speaker si el modelo lo soporta
            if self.speaker and hasattr(self.tts, 'speakers') and self.tts.speakers:
                kwargs["speaker"] = self.speaker
            
            # Sintetizar con o sin archivo de salida
            if output_file:
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
                
                # Sintetizar y guardar en archivo
                self.tts.tts_to_file(**kwargs, file_path=output_file)
                logger.info(f"Audio guardado en: {output_file}")
                return None
            else:
                # Sintetizar y devolver array
                wav = self.tts.tts(**kwargs)
                return np.array(wav)
                
        except Exception as e:
            logger.error(f"Error al sintetizar texto: {str(e)}")
            return None
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Sintetiza y reproduce el texto inmediatamente
        
        Args:
            text: Texto a convertir en voz y reproducir
            blocking: Si es True, espera a que termine la reproducción
            
        Returns:
            bool: True si se reprodujo correctamente, False en caso contrario
        """
        # Sintetizar el texto
        audio_array = self.synthesize(text)
        
        if audio_array is None:
            return False
        
        try:
            # Reproducir el audio
            sd.play(audio_array, self.sample_rate)
            
            # Si es bloqueante, esperar a que termine
            if blocking:
                sd.wait()
            
            return True
        except Exception as e:
            logger.error(f"Error al reproducir audio: {str(e)}")
            return False
    
    def save_to_file(self, text: str, file_path: str) -> bool:
        """
        Sintetiza texto y lo guarda en un archivo
        
        Args:
            text: Texto a convertir en voz
            file_path: Ruta donde guardar el archivo de audio
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Crear directorio temporal si no existe
            output_dir = os.path.dirname(os.path.abspath(file_path))
            os.makedirs(output_dir, exist_ok=True)
            
            # Sintetizar y guardar
            result = self.synthesize(text, output_file=file_path)
            
            # Verificar si el archivo se creó correctamente
            if os.path.exists(file_path):
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error al guardar audio en archivo: {str(e)}")
            return False
    
    def get_available_models(self) -> Dict:
        """
        Obtiene los modelos TTS disponibles
        
        Returns:
            Dict: Diccionario con los modelos disponibles por idioma
        """
        if not TTS_AVAILABLE:
            return {}
        
        try:
            return TTS.list_models()
        except Exception as e:
            logger.error(f"Error al obtener modelos disponibles: {str(e)}")
            return {}