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

# (list) Application requirements
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pyjnius,sqlite3

# (str) Supported orientations
orientation = portrait
fullscreen = 1

# ==========================================
# Configuración de Android
# ==========================================
android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.private_storage = True

# Permisos para el análisis forense de SMS
android.permissions = android.permission.READ_SMS, android.permission.RECEIVE_SMS

[buildozer]
log_level = 2
warn_on_root = 1
