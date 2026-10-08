# 🔐 Checklist de seguridad - Steam Optimizer

Principio base: **los datos que no se guardan no se pueden filtrar.**
La app solo consulta datos públicos de Steam y no almacena nada del usuario.

## Ahora (setup del proyecto)
- [x] `.env` está en `.gitignore` antes del primer commit
- [x] `venv/` está en `.gitignore`

## Al conectar con la API de Steam
- [x] La API key vive solo en `.env` (nunca en el código ni en JavaScript del navegador)
- [x] Existe un `.env.example` con los nombres de las variables, sin valores reales
- [x] Todas las llamadas a Steam las hace Flask (servidor), no el navegador
- [x] No se guarda ningún dato del usuario (sin base de datos, sin logs con Steam IDs)
- [x] Los errores de `requests` se capturan para que la URL (con la API key) no salga en mensajes
- [ ] **PENDIENTE:** revocar la API key expuesta en una conversación y generar otra

## Al crear el formulario
- [x] Se valida la entrada: Steam ID de 17 dígitos (falta aceptar nombre de perfil, si se añade)
- [x] Nunca se piden contraseñas de Steam
- [x] Se mantiene el escapado automático de Jinja2 (no usar `|safe` con datos externos)
- [x] Mensajes de error genéricos, sin detalles internos
- [ ] Revisar la ruta temporal `/demo` y borrarla antes de publicar
- [ ] Google Fonts: el navegador del visitante pide la fuente a Google (decidir si se acepta,
  se alojan los archivos de la fuente en `static/`, o se usa una fuente del sistema)

## Antes de publicar
- [ ] `debug=False` en producción
- [ ] HTTPS activo en el hosting
- [ ] Dependencias actualizadas (`pip list --outdated`)
- [ ] Nota de privacidad visible: "No almacenamos ningún dato. Solo consultamos tu perfil público de Steam"
- [ ] Repaso del historial de Git: ninguna clave subida por error (si ocurre, regenerarla)

## Si en el futuro se añade login
- [ ] Usar "Sign in through Steam" (OpenID); nunca gestionar contraseñas propias
