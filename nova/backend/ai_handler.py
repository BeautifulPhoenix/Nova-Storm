#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para manejar la comunicación con Ollama API
Gestiona el envío y recepción de mensajes con el modelo de IA
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Union

logger = logging.getLogger('nova.ai_handler')

class OllamaHandler:
    """Clase para manejar la comunicación con la API de Ollama"""
    
    def __init__(self, api_url: str, model_name: str):
        """Inicializa el manejador de Ollama
        
        Args:
            api_url: URL de la API de Ollama (ej: http://localhost:11434/api/chat)
            model_name: Nombre del modelo a utilizar (ej: nous-hermes:7b)
        """
        self.api_url = api_url
        self.model_name = model_name
        self.session = requests.Session()
        logger.info(f"Inicializado OllamaHandler con modelo {model_name}")
        
        # Verificar conexión con Ollama
        self._check_connection()
    
    def _check_connection(self) -> bool:
        """Verifica la conexión con Ollama
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        # Intentar primero con la URL original
        if self._try_connection():
            return True
            
        # Si falla, intentar con la IP alternativa
        if 'localhost' in self.api_url:
            alt_api_url = self.api_url.replace('localhost', '92.177.226.9')
            logger.info(f"Intentando conexión alternativa con: {alt_api_url}")
            
            # Guardar la URL original
            original_url = self.api_url
            
            # Probar con la URL alternativa
            self.api_url = alt_api_url
            if self._try_connection():
                logger.info(f"Usando conexión alternativa: {alt_api_url}")
                return True
            else:
                # Restaurar la URL original si también falla
                self.api_url = original_url
                
        logger.error("No se pudo conectar con Ollama en ninguna de las URLs configuradas")
        logger.info("Asegúrate de que Ollama está en ejecución y accesible en la URL configurada.")
        return False
        
    def _try_connection(self) -> bool:
        """Intenta conectar con Ollama en la URL actual
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Extraer la URL base sin el endpoint específico
            base_url = self.api_url.split('/api/')[0]
            response = self.session.get(f"{base_url}/api/tags")
            response.raise_for_status()
            
            # Verificar si el modelo está disponible
            models = response.json().get('models', [])
            model_available = any(self.model_name in model.get('name', '') for model in models)
            
            if not model_available:
                logger.warning(f"El modelo {self.model_name} no está disponible en Ollama. "
                              f"Puede que necesites descargarlo con 'ollama pull {self.model_name}'")
            else:
                logger.info(f"Conexión exitosa con Ollama. Modelo {self.model_name} disponible.")
            
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al conectar con Ollama: {str(e)}")
            return False
    
    def send_message(self, message: str, conversation_history: Optional[List[Dict]] = None, 
                    system_prompt: Optional[str] = None) -> Dict:
        """Envía un mensaje al modelo y obtiene su respuesta
        
        Args:
            message: Mensaje a enviar al modelo
            conversation_history: Historial de conversación previo (opcional)
            system_prompt: Prompt de sistema para definir el comportamiento (opcional)
            
        Returns:
            Dict: Respuesta del modelo con el texto generado
        """
        if conversation_history is None:
            conversation_history = []
        
        # Preparar el payload para la API
        payload = {
            "model": self.model_name,
            "messages": conversation_history + [{"role": "user", "content": message}],
            "stream": False
        }
        
        # Agregar el prompt de sistema si se proporciona
        if system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": system_prompt})
        
        logger.debug(f"Enviando mensaje a Ollama: {message[:50]}...")
        
        try:
            response = self.session.post(self.api_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extraer la respuesta del modelo
            assistant_message = result.get('message', {}).get('content', '')
            logger.debug(f"Respuesta recibida de Ollama: {assistant_message[:50]}...")
            
            return {
                "response": assistant_message,
                "model": self.model_name,
                "raw_response": result
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error al comunicarse con Ollama: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "response": "Lo siento, no puedo responder en este momento."}
    
    def stream_message(self, message: str, conversation_history: Optional[List[Dict]] = None,
                     system_prompt: Optional[str] = None):
        """Envía un mensaje al modelo y obtiene su respuesta en streaming
        
        Args:
            message: Mensaje a enviar al modelo
            conversation_history: Historial de conversación previo (opcional)
            system_prompt: Prompt de sistema para definir el comportamiento (opcional)
            
        Yields:
            str: Fragmentos de texto de la respuesta del modelo
        """
        if conversation_history is None:
            conversation_history = []
        
        # Preparar el payload para la API
        payload = {
            "model": self.model_name,
            "messages": conversation_history + [{"role": "user", "content": message}],
            "stream": True
        }
        
        # Agregar el prompt de sistema si se proporciona
        if system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": system_prompt})
        
        logger.debug(f"Iniciando streaming de mensaje a Ollama: {message[:50]}...")
        
        try:
            response = self.session.post(self.api_url, json=payload, stream=True)
            response.raise_for_status()
            
            # Procesar la respuesta en streaming
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        content = chunk.get('message', {}).get('content', '')
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        logger.warning(f"Error al decodificar respuesta de streaming: {line}")
                        continue
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en streaming con Ollama: {str(e)}"
            logger.error(error_msg)
            yield "Lo siento, no puedo responder en este momento."