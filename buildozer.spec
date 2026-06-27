[app]

# (str) Title of your application
title = ASSM Monitor

# (str) Package name
package.name = assm_monitor

# (str) Package domain (needed for android packaging)
package.domain = org.dijin.analysis

# (str) Source code directory
source.dir = .

# (list) Source files to include (extensions)
source.include_exts = py,png,jpg,kv,atlas,db

# (str) Application version
version = 1.0

# ==============================================================================
# REQUERIMIENTOS: Dejamos python3 limpio para que la rama elegida maneje su versión nativa
# ==============================================================================
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pyjnius,sqlite3

# (str) Supported orientations
orientation = portrait
fullscreen = 1

# ==============================================================================
# EL PUNTO DE EQUILIBRIO: Forzamos una rama de lanzamiento moderna pero ultra-estable.
# Tiene soporte AAB para Buildozer y usa Python 3.11 interno para evitar el error de C.
# ==============================================================================
p4a.branch = release-2024.01.21

# ==========================================
# CONFIGURACIÓN ESPECÍFICA DE ANDROID
# ==========================================
android.api = 33
android.minapi = 24
android.build_tools_version = 33.0.2
android.accept_sdk_license = True
android.ndk = 25b
android.ndk_api = 24
android.private_storage = True

# Permisos para el análisis forense de SMS
android.permissions = android.permission.READ_SMS, android.permission.RECEIVE_SMS

[buildozer]
log_level = 2
warn_on_root = 1
