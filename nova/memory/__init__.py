# Módulo de memoria emocional para Nova
# Este paquete gestiona el almacenamiento y recuperación de información del usuario

from nova.memory.memory_manager import MemoryManager
from nova.memory.database import MemoryDatabase

__all__ = ['MemoryManager', 'MemoryDatabase']