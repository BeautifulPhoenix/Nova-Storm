# Despliegue de Nova Storm en Vercel

Este documento explica cómo se ha configurado Nova Storm para su despliegue en Vercel y qué limitaciones existen en este entorno.

## Configuración realizada

Se han creado/modificado los siguientes archivos para permitir el despliegue en Vercel:

1. `vercel.json` - Configuración principal para Vercel
2. `vercel_main.py` - Punto de entrada específico para Vercel
3. `requirements-vercel.txt` - Dependencias compatibles con el entorno serverless
4. `.env` - Variables de entorno (no se sube a Vercel, se configuran en el dashboard)
5. Modificaciones en `nova/interface/app.py` para detectar el entorno de Vercel

## Limitaciones en Vercel

Al desplegar Nova Storm en Vercel, existen las siguientes limitaciones:

1. **Componentes de voz deshabilitados**: Las funcionalidades de reconocimiento de voz (STT) y síntesis de voz (TTS) no están disponibles en Vercel, ya que requieren acceso a hardware local (micrófono y altavoces).

2. **Archivos de audio**: No se pueden generar ni servir archivos de audio dinámicamente en el entorno serverless.

3. **WebSockets limitados**: La funcionalidad de WebSockets (SocketIO) puede tener limitaciones en Vercel debido a la naturaleza serverless del entorno.

4. **Conexión con Ollama**: La aplicación se conecta a una instancia externa de Ollama, ya que no se puede ejecutar Ollama localmente en Vercel.

## Variables de entorno en Vercel

Configura las siguientes variables de entorno en el dashboard de Vercel:

- `OLLAMA_API_URL`: URL de la API de Ollama (ej: http://92.177.226.9:11434/api/chat)
- `SECRET_KEY`: Clave secreta para Flask
- `VERCEL`: Establecer a "1" para indicar que estamos en entorno de Vercel

## Uso en desarrollo local

Para desarrollo local, sigue utilizando el archivo `main.py` original:

```bash
python main.py
```

Para probar la configuración de Vercel localmente:

```bash
python vercel_main.py
```

## Notas adicionales

- La base de datos SQLite se reiniciará con cada despliegue, ya que Vercel no mantiene estado entre ejecuciones.
- Considera migrar a una base de datos externa (MongoDB, PostgreSQL) para persistencia de datos.
- Para una experiencia completa con todas las funcionalidades, se recomienda ejecutar la aplicación localmente.