# 🔐 Checklist de seguridad - Steam Optimizer

Principio base: **los datos que no se guardan no se pueden filtrar.**
La app solo consulta datos públicos de Steam y no almacena nada del usuario.

## Ahora (setup del proyecto)
- [ ] `.env` está en `.gitignore` antes del primer commit
- [ ] `venv/` está en `.gitignore`

## Al conectar con la API de Steam
- [ ] La API key vive solo en `.env` (nunca en el código ni en JavaScript del navegador)
- [ ] Existe un `.env.example` con los nombres de las variables, sin valores reales
- [ ] Todas las llamadas a Steam las hace Flask (servidor), no el navegador
- [ ] No se guarda ningún dato del usuario (sin base de datos, sin logs con Steam IDs)

## Al crear el formulario
- [ ] Se valida la entrada: Steam ID de 17 dígitos o nombre de perfil con caracteres permitidos
- [ ] Nunca se piden contraseñas de Steam
- [ ] Se mantiene el escapado automático de Jinja2 (no usar `|safe` con datos externos)
- [ ] Mensajes de error genéricos, sin detalles internos

## Antes de publicar
- [ ] `debug=False` en producción
- [ ] HTTPS activo en el hosting
- [ ] Dependencias actualizadas (`pip list --outdated`)
- [ ] Nota de privacidad visible: "No almacenamos ningún dato. Solo consultamos tu perfil público de Steam"
- [ ] Repaso del historial de Git: ninguna clave subida por error (si ocurre, regenerarla)

## Si en el futuro se añade login
- [ ] Usar "Sign in through Steam" (OpenID); nunca gestionar contraseñas propias
