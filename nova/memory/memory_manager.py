#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para la gestión de la memoria emocional de Nova
Implementa la lógica para recordar información del usuario y conversaciones pasadas
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple

from nova.memory.database import MemoryDatabase

logger = logging.getLogger('nova.memory.memory_manager')

class MemoryManager:
    """Clase para gestionar la memoria emocional de Nova"""
    
    def __init__(self, db_path: str = "./data/memory.db"):
        """
        Inicializa el gestor de memoria
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db = MemoryDatabase(db_path)
        self.categories = {
            "personal": ["nombre", "edad", "cumpleaños", "trabajo", "hobbies"],
            "preferencias": ["comida", "música", "películas", "libros", "colores"],
            "relación": ["aniversario", "lugares", "momentos", "regalos", "planes"],
            "emocional": ["estado_ánimo", "preocupaciones", "alegrías", "miedos", "sueños"]
        }
        logger.info("Gestor de memoria inicializado")
    
    def save_conversation(self, user_message: str, nova_response: str) -> int:
        """
        Guarda una conversación y extrae información relevante
        
        Args:
            user_message: Mensaje del usuario
            nova_response: Respuesta de Nova
            
        Returns:
            int: ID de la conversación guardada
        """
        # Analizar sentimiento básico (implementación simple)
        sentiment = self._analyze_sentiment(user_message)
        
        # Extraer temas de la conversación
        topics = self._extract_topics(user_message)
        
        # Guardar la conversación
        conversation_id = self.db.save_conversation(
            user_message=user_message,
            nova_response=nova_response,
            sentiment=sentiment,
            topics=topics
        )
        
        # Extraer y guardar información del usuario
        self._extract_and_save_user_info(user_message)
        
        return conversation_id
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Analiza el sentimiento básico del texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            str: Sentimiento detectado (positivo, negativo, neutral)
        """
        # Palabras positivas y negativas en español
        positive_words = ["feliz", "contento", "alegre", "genial", "excelente", "bueno", "increíble", 
                         "maravilloso", "fantástico", "encantado", "amo", "adoro", "me gusta"]
        
        negative_words = ["triste", "enojado", "molesto", "terrible", "horrible", "malo", "pésimo", 
                         "fatal", "odio", "detesto", "no me gusta", "preocupado"]
        
        # Contar ocurrencias
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        # Determinar sentimiento
        if positive_count > negative_count:
            return "positivo"
        elif negative_count > positive_count:
            return "negativo"
        else:
            return "neutral"
    
    def _extract_topics(self, text: str) -> List[str]:
        """
        Extrae temas básicos del texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            List[str]: Lista de temas detectados
        """
        # Temas comunes en español
        topic_keywords = {
            "trabajo": ["trabajo", "empleo", "oficina", "jefe", "compañeros", "proyecto"],
            "familia": ["familia", "padres", "hermanos", "hijos", "pareja"],
            "salud": ["salud", "enfermedad", "médico", "hospital", "dolor"],
            "entretenimiento": ["película", "serie", "música", "concierto", "juego", "videojuego"],
            "comida": ["comida", "restaurante", "cocinar", "receta", "cena", "almuerzo"],
            "viajes": ["viaje", "vacaciones", "hotel", "playa", "montaña", "turismo"],
            "tecnología": ["tecnología", "computadora", "teléfono", "app", "software", "internet"],
            "educación": ["estudios", "universidad", "escuela", "aprender", "curso", "profesor"]
        }
        
        detected_topics = []
        text_lower = text.lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _extract_and_save_user_info(self, text: str) -> None:
        """
        Extrae y guarda información del usuario a partir del texto
        
        Args:
            text: Texto del usuario a analizar
        """
        # Patrones para extraer información personal
        patterns = {
            # Formato: (categoría, clave, patrón regex)
            "personal": [
                ("nombre", r"me llamo ([A-Za-zÁáÉéÍíÓóÚúÑñ\s]+)"),
                ("edad", r"tengo (\d+) años"),
                ("cumpleaños", r"mi cumpleaños es (el )?([0-9]{1,2} de [a-zA-Z]+)"),
                ("trabajo", r"trabajo (en|como) ([A-Za-zÁáÉéÍíÓóÚúÑñ\s]+)"),
            ],
            "preferencias": [
                ("comida", r"mi comida favorita es ([A-Za-zÁáÉéÍíÓóÚúÑñ\s]+)"),
                ("música", r"me gusta (escuchar|la música) ([A-Za-zÁáÉéÍíÓóÚúÑñ\s]+)"),
                ("color", r"mi color favorito es (el )?([A-Za-zÁáÉéÍíÓóÚúÑñ\s]+)"),
            ],
            "emocional": [
                ("estado_ánimo", r"me siento ([A-Za-zÁáÉéÍíÓóÚúÑñ\s]+)"),
                ("preocupaciones", r"estoy preocupado por ([A-Za-zÁáÉéÍíÓóÚúÑñ\s,.]+)"),
            ]
        }
        
        # Buscar coincidencias y guardar información
        for category, pattern_list in patterns.items():
            for key, pattern in pattern_list:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    # El último grupo de captura contiene la información
                    value = matches.group(matches.lastindex).strip()
                    self.db.save_user_info(key, value, category)
                    logger.debug(f"Información extraída: {category}.{key} = {value}")
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict]:
        """
        Obtiene las conversaciones más recientes
        
        Args:
            limit: Número máximo de conversaciones a obtener
            
        Returns:
            List[Dict]: Lista de conversaciones recientes
        """
        return self.db.get_recent_conversations(limit)
    
    def get_user_info_summary(self) -> Dict[str, Dict[str, str]]:
        """
        Obtiene un resumen de la información del usuario organizada por categorías
        
        Returns:
            Dict[str, Dict[str, str]]: Información del usuario por categorías
        """
        all_info = self.db.get_user_info()
        
        # Organizar por categorías
        summary = {}
        for info in all_info:
            category = info['category']
            key = info['key']
            value = info['value']
            
            if category not in summary:
                summary[category] = {}
            
            summary[category][key] = value
        
        return summary
    
    def search_memory(self, query: str) -> Dict[str, List]:
        """
        Busca en toda la memoria (conversaciones e información)
        
        Args:
            query: Texto a buscar
            
        Returns:
            Dict[str, List]: Resultados de la búsqueda por categoría
        """
        # Buscar en conversaciones
        conversations = self.db.search_conversations(query)
        
        # Buscar en información de usuario
        all_info = self.db.get_user_info()
        matching_info = []
        
        for info in all_info:
            if query.lower() in info['value'].lower() or query.lower() in info['key'].lower():
                matching_info.append(info)
        
        return {
            "conversations": conversations,
            "user_info": matching_info
        }
    
    def get_memory_for_context(self, user_message: str, max_items: int = 3) -> str:
        """
        Genera un contexto de memoria relevante para la conversación actual
        
        Args:
            user_message: Mensaje actual del usuario
            max_items: Número máximo de elementos de memoria a incluir
            
        Returns:
            str: Contexto de memoria formateado para incluir en el prompt
        """
        context_parts = []
        
        # Extraer temas del mensaje actual
        current_topics = self._extract_topics(user_message)
        
        # Buscar conversaciones relacionadas con los temas actuales
        related_conversations = []
        for topic in current_topics:
            topic_convs = self.db.search_conversations(topic, limit=2)
            related_conversations.extend(topic_convs)
        
        # Limitar a las más recientes si hay demasiadas
        if related_conversations:
            related_conversations = related_conversations[:max_items]
            context_parts.append("Conversaciones previas relacionadas:")
            for conv in related_conversations:
                context_parts.append(f"- Usuario: {conv['user_message']}")
                context_parts.append(f"- Nova: {conv['nova_response']}")
        
        # Obtener información relevante del usuario
        user_info = self.get_user_info_summary()
        if user_info:
            context_parts.append("\nInformación sobre el usuario:")
            for category, items in user_info.items():
                if items:  # Solo incluir categorías con información
                    context_parts.append(f"- {category.capitalize()}:")
                    for key, value in items.items():
                        context_parts.append(f"  * {key}: {value}")
        
        # Unir todo el contexto
        memory_context = "\n".join(context_parts)
        
        return memory_context
    
    def close(self) -> None:
        """
        Cierra la conexión con la base de datos
        """
        self.db.close()