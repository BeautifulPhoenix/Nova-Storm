#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nova - Asistente Virtual IA
Punto de entrada principal para la aplicación
"""

import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz esté en el path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Importar la aplicación desde el módulo interface
from nova.interface.app import create_app, socketio

def main():
    """Función principal para iniciar la aplicación"""
    print("Iniciando Nova - Asistente Virtual IA...")
    
    # Crear y ejecutar la aplicación
    app = create_app()
    
    # Configurar el puerto (por defecto 8000 para evitar conflicto con AirPlay en macOS)
    port = int(os.environ.get('PORT', 8000))
    
    # Iniciar el servidor
    print(f"Servidor iniciado en http://localhost:{port}")
    print("Presiona Ctrl+C para detener la aplicación")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()