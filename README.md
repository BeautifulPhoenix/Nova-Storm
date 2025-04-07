# Nova - Asistente IA

Nova es un proyecto de asistente virtual con personalidad, que integra múltiples tecnologías para crear una experiencia interactiva, emocional y realista.

## Características

- **Interacción por voz** bidireccional (STT y TTS)
- **Memoria emocional** para recordar conversaciones y preferencias
- **Avatar 3D** animado y reactivo
- **Personalidad cálida y empática** basada en modelos de lenguaje
- **Funcionamiento local** sin dependencia de servicios en la nube

## Estructura del Proyecto

```
/nova
  /backend
    - ai_handler.py      # Comunicación con Ollama
    - personality.py     # Gestión de la personalidad de Nova
  /voice
    - speech_to_text.py  # Conversión de voz a texto (Whisper)
    - text_to_speech.py  # Conversión de texto a voz (XTTS/Coqui)
  /memory
    - memory_manager.py  # Gestión de la memoria emocional
    - database.py        # Interfaz con la base de datos
  /interface
    - app.py             # Aplicación principal (Flask/Streamlit)
    - static/            # Recursos estáticos (CSS, JS)
    - templates/         # Plantillas HTML
  /avatar
    - model_handler.py   # Gestión del modelo 3D
    - animations.py      # Control de animaciones
  - main.py              # Punto de entrada principal
  - config.py            # Configuración global
  - requirements.txt     # Dependencias del proyecto
```

## Requisitos

- Python 3.8+
- Ollama (instalado localmente)
- Modelos de voz (Whisper, XTTS/Coqui)
- Navegador web moderno con soporte WebGL
- Micrófono y altavoces

## Instalación

```bash
# Clonar el repositorio
git clone [url-del-repositorio]
cd nova

# Instalar dependencias
pip install -r requirements.txt

# Configurar Ollama (asegúrate de tener Ollama instalado)
# Descargar el modelo deseado, por ejemplo:
# ollama pull nous-hermes:7b

# Ejecutar la aplicación
python main.py
```

## Uso

Al iniciar la aplicación, se abrirá una interfaz web donde podrás:

1. Ver el avatar 3D de Nova
2. Hablar con ella usando el micrófono
3. Ver la transcripción de la conversación
4. Escuchar sus respuestas por voz

## Desarrollo

Este proyecto está en desarrollo activo. Las próximas características incluyen:

- Mejora de las expresiones faciales del avatar
- Ampliación de la memoria emocional
- Optimización del rendimiento
- Modo de llamada en tiempo real