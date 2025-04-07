#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nova - Asistente Virtual IA
Punto de entrada para Vercel
"""

import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz esté en el path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Importar la aplicación desde el módulo interface
from nova.interface.app import create_app

# Crear la aplicación para Vercel
app = create_app()

# Esta es la aplicación que Vercel ejecutará
# No usamos socketio.run() aquí porque no es compatible con serverless