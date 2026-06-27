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
# REQUERIMIENTOS LIMPIOS
# ==============================================================================
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pyjnius,sqlite3

# (str) Supported orientations
orientation = portrait
fullscreen = 1

# ==============================================================================
# CONTROL DE ENTORNO SEGURO
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

# ==============================================================================
# SOLUCIÓN PARA XIAOMI 15T: Compilamos en arquitectura moderna de 64 bits
# ==============================================================================
android.archs = armeabi-v7a arm64-v8a

# Permisos para el análisis forense de SMS
android.permissions = android.permission.READ_SMS, android.permission.RECEIVE_SMS

[buildozer]
log_level = 2
warn_on_root = 1
