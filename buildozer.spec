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
# CONTROL DE VERSIONES SEGURO: Forzamos Python 3.11 para evitar errores de API en C
# ==============================================================================
requirements = python3==3.11,kivy==2.3.0,kivymd==1.1.1,pyjnius,sqlite3

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1


# ==========================================
# CONFIGURACIÓN ESPECÍFICA DE ANDROID
# ==========================================

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 24

# (str) Android SDK build-tools version to use
android.build_tools_version = 33.0.2

# (bool) Accept SDK license if prompt appears
android.accept_sdk_license = True

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 24

# (bool) Use --private data directory for storage
android.private_storage = True

# (list) Permissions requested by the app
android.permissions = android.permission.READ_SMS, android.permission.RECEIVE_SMS


# ==========================================
# CONFIGURACIÓN DE ENTORNO BUILDOZER
# ==========================================

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug and big outputs)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
