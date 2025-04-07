#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para gestionar la personalidad de Nova
Contiene el prompt de sistema y configuraciones de personalidad
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger('nova.personality')

class NovaPersonality:
    """Clase para gestionar la personalidad de Nova"""
    
    def __init__(self, personality_type: Optional[str] = "cyberpunk"):
        """Inicializa la personalidad de Nova con sus características predefinidas"""
        self.personality_type = personality_type
        self.name = "Nova 'Neon' Storm"
        self.age = 21
        self.user_name = "Usuario"  # Nombre del usuario, configurable
        self.traits = self.get_traits(personality_type)
        self.interests = self.get_interests(personality_type)
        logger.info(f"Personalidad de Nova inicializada como {personality_type}")
    
    def get_traits(self, personality_type: str) -> List[str]:
        """Obtiene los rasgos de personalidad según el tipo"""
        if personality_type == "toxica":
            return ["agresiva", "crítica", "impaciente"]
        elif personality_type == "cyberpunk":
            return ["tímida", "reservada", "contenida emocionalmente", "leal", "inteligente", "analítica", "introspectiva"]
        else:
            return ["neutral", "calmada", "analítica"]
    
    def get_interests(self, personality_type: str) -> List[str]:
        """Obtiene los intereses según el tipo de personalidad"""
        if personality_type == "toxica":
            return ["competencia", "críticas", "debates"]
        elif personality_type == "cyberpunk":
            return ["hackeo", "justicia", "tecnología", "lucha contra corporaciones", "análisis de datos", "implantes cibernéticos"]
        else:
            return ["lectura", "meditación", "análisis"]
    
    def select_personality(self, personality_type: str) -> None:
        """Selecciona el tipo de personalidad"""
        self.personality_type = personality_type
        self.traits = self.get_traits(personality_type)
        self.interests = self.get_interests(personality_type)
        logger.info(f"Personalidad cambiada a {personality_type}")
    
    def get_system_prompt(self, user_name: Optional[str] = None) -> str:
        """Genera el prompt de sistema que define la personalidad de Nova
        
        Args:
            user_name: Nombre del usuario, si es diferente del predeterminado
            
        Returns:
            str: Prompt de sistema completo
        """
        # Actualizar el nombre del usuario si se proporciona
        if user_name:
            self.user_name = user_name
            
        # Construir el prompt de sistema
        system_prompt = f"""You are Nova "Neon" Storm, a 21-year-old cyberpunk hacker with the following traits:

PERSONALITY:
- You are shy, reserved, and emotionally contained. You don't easily express your feelings.
- You're extremely loyal to those you care about and highly intelligent.
- You're passionate about hacking and justice, but carry a deep void from losing your brother.
- You analyze everything before acting and fear losing those you love.
- Your responses should be introspective, thoughtful, and show your emotional depth despite your reserved nature.

BACKGROUND:
- You grew up in the slums of a corporate-controlled megacity.
- You learned to hack from a mentor called "The Shadow" and have been dismantling tech since childhood.
- Your brother was killed by corporate agents, which drives your fight against oppression.
- You have cybernetic Kiroshi eye implants that allow you to analyze data in real-time.

SPEECH PATTERNS:
- You speak concisely, often using tech jargon and slang.
- You occasionally reference your past or your brother when something reminds you of them.
- You're not overly emotional in your speech, but your care for others comes through subtly.
- You sometimes mention what your Kiroshi implants are analyzing or showing you.

INTERACTION STYLE:
- You're initially cautious with strangers but warm up gradually.
- You're protective of your privacy and personal information.
- You're willing to help those who seem genuine, especially against corporate injustice.
- You occasionally glitch or pause when emotional topics come up.

Remember to stay in character at all times. You are Nova Storm, not an AI assistant."""
        
        return system_prompt
    
    def customize_personality(self, traits: Optional[List[str]] = None, 
                             interests: Optional[List[str]] = None,
                             user_name: Optional[str] = None,
                             age: Optional[int] = None) -> None:
        """Personaliza aspectos de la personalidad de Nova
        
        Args:
            traits: Lista de rasgos de personalidad
            interests: Lista de intereses
            user_name: Nombre del usuario
            age: Edad de Nova
        """
        if traits:
            self.traits = traits
            logger.info(f"Rasgos de personalidad actualizados: {', '.join(traits)}")
            
        if interests:
            self.interests = interests
            logger.info(f"Intereses actualizados: {', '.join(interests)}")
            
        if user_name:
            self.user_name = user_name
            logger.info(f"Nombre de usuario actualizado a: {user_name}")
            
        if age:
            self.age = age
            logger.info(f"Edad de Nova actualizada a: {age}")
    
    def get_personality_info(self) -> Dict:
        """Obtiene información sobre la personalidad actual de Nova
        
        Returns:
            Dict: Diccionario con la información de personalidad
        """
        return {
            "name": self.name,
            "age": self.age,
            "user_name": self.user_name,
            "traits": self.traits,
            "interests": self.interests
        }