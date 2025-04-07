#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación principal de Nova - Interfaz web con Flask
Integra todos los módulos (IA, voz, memoria, avatar) en una interfaz interactiva
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit

from nova.backend.ai_handler import OllamaHandler
from nova.backend.personality import NovaPersonality
from nova.voice.speech_to_text import SpeechToText
from nova.voice.text_to_speech import TextToSpeech
from nova.memory.memory_manager import MemoryManager

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nova.interface')

# Inicializar la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nova_secret_key')
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuración de rutas de archivos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = Path(__file__).resolve().parent / 'static'
TEMPLATES_DIR = Path(__file__).resolve().parent / 'templates'
DATA_DIR = BASE_DIR / 'data'

# Asegurar que los directorios existan
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / 'audio').mkdir(exist_ok=True)
(DATA_DIR / 'temp').mkdir(exist_ok=True)

# Inicializar componentes de Nova
ai_handler = OllamaHandler(
    api_url="http://localhost:11434/api/chat",
    model_name="openchat"  # Utilizando el modelo OpenChat
)
personality = NovaPersonality()
speech_to_text = SpeechToText(model_size="base", language="es")
text_to_speech = TextToSpeech(language="es")
memory_manager = MemoryManager(db_path=str(DATA_DIR / "memory.db"))

# Variables globales para la sesión actual
current_session = {
    "conversation_history": [],
    "last_response": "",
    "is_listening": False
}

@app.route('/')
def index():
    """Página principal de la aplicación"""
    return render_template('index.html')

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """Endpoint para enviar un mensaje a Nova"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400
    
    # Obtener contexto de memoria relevante
    memory_context = memory_manager.get_memory_for_context(user_message)
    
    # Preparar el historial de conversación para el modelo
    conversation_history = [
        {"role": "user", "content": msg["user"]}
        if i % 2 == 0 else
        {"role": "assistant", "content": msg["nova"]}
        for i, msg in enumerate(current_session["conversation_history"])
    ]
    
    # Obtener el prompt de sistema con la personalidad de Nova
    system_prompt = personality.get_system_prompt()
    
    # Si hay contexto de memoria, agregarlo al prompt de sistema
    if memory_context:
        system_prompt += f"\n\nRecuerda esta información sobre {personality.user_name}:\n{memory_context}"
    
    # Enviar mensaje a Ollama
    response = ai_handler.send_message(
        message=user_message,
        conversation_history=conversation_history,
        system_prompt=system_prompt
    )
    
    nova_response = response.get("response", "Lo siento, no pude procesar tu mensaje.")
    
    # Guardar la conversación en la memoria
    memory_manager.save_conversation(user_message, nova_response)
    
    # Actualizar el historial de conversación
    current_session["conversation_history"].append({"user": user_message, "nova": nova_response})
    current_session["last_response"] = nova_response
    
    # Generar audio de respuesta
    audio_path = str(DATA_DIR / "audio" / f"response_{int(datetime.now().timestamp())}.wav")
    text_to_speech.save_to_file(nova_response, audio_path)
    
    return jsonify({
        "response": nova_response,
        "audio_url": f"/audio/{os.path.basename(audio_path)}"
    })

@app.route('/api/start_listening', methods=['POST'])
def start_listening():
    """Inicia la escucha del micrófono"""
    if current_session["is_listening"]:
        return jsonify({"status": "already_listening"})
    
    def speech_callback(text):
        """Callback para cuando se detecta texto en el audio"""
        socketio.emit('speech_detected', {"text": text})
    
    success = speech_to_text.start_listening(callback=speech_callback)
    current_session["is_listening"] = success
    
    return jsonify({"status": "started" if success else "error"})

@app.route('/api/stop_listening', methods=['POST'])
def stop_listening():
    """Detiene la escucha del micrófono"""
    if not current_session["is_listening"]:
        return jsonify({"status": "not_listening"})
    
    speech_to_text.stop_listening()
    current_session["is_listening"] = False
    
    return jsonify({"status": "stopped"})

@app.route('/api/get_conversation_history', methods=['GET'])
def get_conversation_history():
    """Obtiene el historial de conversación actual"""
    return jsonify({
        "history": current_session["conversation_history"],
        "count": len(current_session["conversation_history"])
    })

@app.route('/api/clear_conversation', methods=['POST'])
def clear_conversation():
    """Limpia el historial de conversación actual"""
    current_session["conversation_history"] = []
    return jsonify({"status": "cleared"})

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Sirve archivos de audio generados"""
    return send_from_directory(str(DATA_DIR / "audio"), filename)

@socketio.on('connect')
def handle_connect():
    """Maneja la conexión de un cliente por WebSocket"""
    logger.info(f"Cliente conectado: {request.sid}")
    emit('status', {"status": "connected"})

@socketio.on('disconnect')
def handle_disconnect():
    """Maneja la desconexión de un cliente"""
    logger.info(f"Cliente desconectado: {request.sid}")

@socketio.on('send_message')
def handle_message(data):
    """Maneja mensajes enviados por WebSocket"""
    user_message = data.get('message', '')
    
    if not user_message:
        emit('error', {"message": "Mensaje vacío"})
        return
    
    # Procesar el mensaje (reutilizando la lógica de send_message)
    response_data = send_message().get_json()
    
    # Emitir la respuesta a todos los clientes
    emit('nova_response', response_data, broadcast=True)

def create_app():
    """Crea y configura la aplicación Flask"""
    return app

if __name__ == '__main__':
    # Ejecutar la aplicación
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)