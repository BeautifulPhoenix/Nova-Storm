#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para la gestión de la base de datos de memoria
Implementa una interfaz con SQLite para almacenar información persistente
"""

import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

logger = logging.getLogger('nova.memory.database')

class MemoryDatabase:
    """Clase para manejar la base de datos de memoria de Nova"""
    
    def __init__(self, db_path: str = "./data/memory.db"):
        """
        Inicializa la conexión con la base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Inicializar la base de datos
        self._connect()
        self._create_tables()
    
    def _connect(self) -> bool:
        """
        Establece la conexión con la base de datos
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
            self.cursor = self.conn.cursor()
            logger.info(f"Conexión establecida con la base de datos: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al conectar con la base de datos: {str(e)}")
            return False
    
    def _create_tables(self) -> None:
        """
        Crea las tablas necesarias si no existen
        """
        try:
            # Tabla de conversaciones
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    nova_response TEXT NOT NULL,
                    sentiment TEXT,
                    topics TEXT
                )
            ''')
            
            # Tabla de información personal del usuario
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_info (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0
                )
            ''')
            
            # Tabla de preferencias y configuración
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            self.conn.commit()
            logger.info("Tablas creadas correctamente")
        except sqlite3.Error as e:
            logger.error(f"Error al crear tablas: {str(e)}")
    
    def close(self) -> None:
        """
        Cierra la conexión con la base de datos
        """
        if self.conn:
            self.conn.close()
            logger.info("Conexión con la base de datos cerrada")
    
    def save_conversation(self, user_message: str, nova_response: str, 
                         sentiment: Optional[str] = None, 
                         topics: Optional[List[str]] = None) -> int:
        """
        Guarda una conversación en la base de datos
        
        Args:
            user_message: Mensaje del usuario
            nova_response: Respuesta de Nova
            sentiment: Sentimiento detectado (opcional)
            topics: Lista de temas detectados (opcional)
            
        Returns:
            int: ID de la conversación guardada, o -1 si hay error
        """
        try:
            timestamp = datetime.now().isoformat()
            topics_json = json.dumps(topics) if topics else None
            
            self.cursor.execute('''
                INSERT INTO conversations (timestamp, user_message, nova_response, sentiment, topics)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, user_message, nova_response, sentiment, topics_json))
            
            self.conn.commit()
            conversation_id = self.cursor.lastrowid
            logger.debug(f"Conversación guardada con ID: {conversation_id}")
            return conversation_id
        except sqlite3.Error as e:
            logger.error(f"Error al guardar conversación: {str(e)}")
            return -1
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene las conversaciones más recientes
        
        Args:
            limit: Número máximo de conversaciones a obtener
            
        Returns:
            List[Dict]: Lista de conversaciones recientes
        """
        try:
            self.cursor.execute('''
                SELECT * FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = self.cursor.fetchall()
            conversations = []
            
            for row in rows:
                conv = dict(row)
                # Convertir topics de JSON a lista si existe
                if conv['topics']:
                    conv['topics'] = json.loads(conv['topics'])
                conversations.append(conv)
            
            return conversations
        except sqlite3.Error as e:
            logger.error(f"Error al obtener conversaciones recientes: {str(e)}")
            return []
    
    def save_user_info(self, key: str, value: str, category: str, 
                      confidence: float = 1.0) -> bool:
        """
        Guarda o actualiza información del usuario
        
        Args:
            key: Clave de la información (ej: 'nombre', 'comida_favorita')
            value: Valor asociado
            category: Categoría de la información (ej: 'personal', 'preferencias')
            confidence: Nivel de confianza de la información (0.0 a 1.0)
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Intentar actualizar si la clave ya existe
            self.cursor.execute('''
                INSERT OR REPLACE INTO user_info (key, value, category, timestamp, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (key, value, category, timestamp, confidence))
            
            self.conn.commit()
            logger.debug(f"Información de usuario guardada: {key}={value}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al guardar información de usuario: {str(e)}")
            return False
    
    def get_user_info(self, key: Optional[str] = None, 
                     category: Optional[str] = None) -> Union[Dict, List[Dict]]:
        """
        Obtiene información del usuario
        
        Args:
            key: Clave específica a buscar (opcional)
            category: Categoría a filtrar (opcional)
            
        Returns:
            Union[Dict, List[Dict]]: Información del usuario
        """
        try:
            if key:
                # Buscar por clave específica
                self.cursor.execute('''
                    SELECT * FROM user_info WHERE key = ?
                ''', (key,))
                row = self.cursor.fetchone()
                return dict(row) if row else {}
            elif category:
                # Buscar por categoría
                self.cursor.execute('''
                    SELECT * FROM user_info WHERE category = ?
                    ORDER BY timestamp DESC
                ''', (category,))
            else:
                # Obtener toda la información
                self.cursor.execute('''
                    SELECT * FROM user_info
                    ORDER BY category, key
                ''')
            
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error al obtener información de usuario: {str(e)}")
            return [] if key is None else {}
    
    def save_preference(self, key: str, value: str) -> bool:
        """
        Guarda una preferencia o configuración
        
        Args:
            key: Clave de la preferencia
            value: Valor de la preferencia
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            timestamp = datetime.now().isoformat()
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO preferences (key, value, timestamp)
                VALUES (?, ?, ?)
            ''', (key, value, timestamp))
            
            self.conn.commit()
            logger.debug(f"Preferencia guardada: {key}={value}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error al guardar preferencia: {str(e)}")
            return False
    
    def get_preference(self, key: str) -> str:
        """
        Obtiene el valor de una preferencia
        
        Args:
            key: Clave de la preferencia
            
        Returns:
            str: Valor de la preferencia o cadena vacía si no existe
        """
        try:
            self.cursor.execute('''
                SELECT value FROM preferences WHERE key = ?
            ''', (key,))
            
            row = self.cursor.fetchone()
            return row['value'] if row else ""
        except sqlite3.Error as e:
            logger.error(f"Error al obtener preferencia: {str(e)}")
            return ""
    
    def get_all_preferences(self) -> Dict[str, str]:
        """
        Obtiene todas las preferencias
        
        Returns:
            Dict[str, str]: Diccionario con todas las preferencias
        """
        try:
            self.cursor.execute('''
                SELECT key, value FROM preferences
            ''')
            
            rows = self.cursor.fetchall()
            return {row['key']: row['value'] for row in rows}
        except sqlite3.Error as e:
            logger.error(f"Error al obtener todas las preferencias: {str(e)}")
            return {}
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca conversaciones que contengan el texto especificado
        
        Args:
            query: Texto a buscar
            limit: Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de conversaciones que coinciden con la búsqueda
        """
        try:
            search_pattern = f"%{query}%"
            
            self.cursor.execute('''
                SELECT * FROM conversations
                WHERE user_message LIKE ? OR nova_response LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (search_pattern, search_pattern, limit))
            
            rows = self.cursor.fetchall()
            conversations = []
            
            for row in rows:
                conv = dict(row)
                if conv['topics']:
                    conv['topics'] = json.loads(conv['topics'])
                conversations.append(conv)
            
            return conversations
        except sqlite3.Error as e:
            logger.error(f"Error al buscar conversaciones: {str(e)}")
            return []