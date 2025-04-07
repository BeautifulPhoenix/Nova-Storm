# Despliegue de Nova Storm en Vercel

## Cambios realizados para compatibilidad con Vercel

Se han realizado los siguientes ajustes para garantizar la compatibilidad con el entorno serverless de Vercel:

1. **Configuración de Python 3.9**: Se ha especificado Python 3.9 como versión de runtime en `vercel.json` para asegurar la compatibilidad con todas las dependencias.

2. **Ajuste de dependencias**: 
   - Se ha eliminado `sqlite-utils` ya que no está disponible en Vercel. La aplicación utiliza el módulo `sqlite3` estándar de Python.
   - Se ha limitado la versión de `numpy` a `<1.22.0` para garantizar compatibilidad con Python 3.9.
   - Se ha limitado la versión de `pandas` a `<2.0.0` para garantizar compatibilidad con Python 3.9.

3. **Modo de ejecución**: La aplicación está configurada para ejecutarse en modo serverless, sin utilizar `socketio.run()` que no es compatible con este entorno.

## Instrucciones de despliegue

1. Asegúrate de tener una cuenta en Vercel y el CLI de Vercel instalado:
   ```bash
   npm install -g vercel
   ```

2. Desde el directorio raíz del proyecto, ejecuta:
   ```bash
   vercel
   ```

3. Sigue las instrucciones en pantalla para completar el despliegue.

## Pruebas locales

Para probar la configuración de Vercel localmente:

```bash
python vercel_main.py
```

## Solución de problemas

Si encuentras errores relacionados con dependencias durante el despliegue:

1. Verifica que estás utilizando Python 3.9 como se especifica en `vercel.json`.
2. Comprueba que las versiones de las dependencias en `requirements-vercel.txt` son compatibles con Python 3.9.
3. Revisa los logs de despliegue en la consola de Vercel para identificar errores específicos.