import sqlite3
import os
import logging
import threading
import time
from typing import List, Dict, Any

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.core.window import Window

# Configurar el registro (logging) para mostrar mensajes limpios en consola
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

if platform != 'android':
    # Simular resolución de teléfono móvil para pruebas en PC
    Window.size = (400, 700)

# ==========================================
# FASE 1 OPTIMIZADA: CAPA DE DATOS (SQLite)
# ==========================================

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Establece y retorna una conexión a la base de datos usando la ruta dinámica."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str) -> None:
    """Inicializa la base de datos de manera segura."""
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS white_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_name TEXT UNIQUE NOT NULL,
                app_name TEXT NOT NULL,
                authorized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_name TEXT NOT NULL,
                app_name TEXT NOT NULL,
                permission_violation TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        logging.info("Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        logging.error(f"Error al inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def add_to_whitelist(db_path: str, package_name: str, app_name: str) -> None:
    """Añade una app a la lista blanca liberando la conexión en finally."""
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO white_list (package_name, app_name)
            VALUES (?, ?)
        ''', (package_name, app_name))
        conn.commit()
        logging.info(f"Añadido a lista blanca: {app_name} ({package_name})")
    except sqlite3.IntegrityError:
        logging.warning(f"La app {app_name} ({package_name}) ya estaba en la lista blanca.")
    except sqlite3.Error as e:
        logging.error(f"Error al añadir a la lista blanca: {e}")
    finally:
        if conn:
            conn.close()

def get_whitelist(db_path: str) -> List[str]:
    """Obtiene el listado de paquetes autorizados manejando el cierre seguro."""
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT package_name FROM white_list')
        rows = cursor.fetchall()
        return [row['package_name'] for row in rows]
    except sqlite3.Error as e:
        logging.error(f"Error al obtener la lista blanca: {e}")
        return []
    finally:
        if conn:
            conn.close()

def log_alert(db_path: str, package_name: str, app_name: str, permission: str, risk_level: str) -> None:
    """Registra una alerta en el historial forense liberando correctamente la conexión."""
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO security_alerts (package_name, app_name, permission_violation, risk_level)
            VALUES (?, ?, ?, ?)
        ''', (package_name, app_name, permission, risk_level))
        conn.commit()
        logging.info(f"ALERTA GUARDADA: {app_name} - Permiso: {permission}")
    except sqlite3.Error as e:
        logging.error(f"Error al registrar alerta: {e}")
    finally:
        if conn:
            conn.close()


# ==========================================
# FASE 2 & 3: UI KIVYMD Y MOTOR HÍBRIDO (PYJNIUS)
# ==========================================

KV = '''
MDScreenManager:
    DashboardScreen:
    HistoryScreen:

<DashboardScreen>:
    name: 'dashboard'
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Anti-Spyware SMS Monitor"
            elevation: 2
            pos_hint: {"top": 1}
            right_action_items: [["history", lambda x: app.change_screen('history')]]

        MDBoxLayout:
            orientation: 'vertical'
            padding: "24dp"
            spacing: "24dp"
            pos_hint: {"center_x": .5, "center_y": .5}
            
            Widget:
                size_hint_y: 1

            MDLabel:
                id: status_label
                text: "Sistema en Espera"
                halign: "center"
                theme_text_color: "Primary"
                font_style: "H4"

            MDFillRoundFlatButton:
                id: scan_btn
                text: "Iniciar Escaneo"
                font_size: "18sp"
                pos_hint: {"center_x": .5}
                size_hint_x: 0.8
                on_release: app.start_scan_thread()

            MDRaisedButton:
                text: "Ver Historial de Alertas"
                pos_hint: {"center_x": .5}
                size_hint_x: 0.8
                md_bg_color: app.theme_cls.error_color
                on_release: app.change_screen('history')

            Widget:
                size_hint_y: 1

<HistoryScreen>:
    name: 'history'
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Historial de Amenazas"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: app.change_screen('dashboard')]]

        MDScrollView:
            MDList:
                id: history_list
'''

class DashboardScreen(MDScreen):
    pass

class HistoryScreen(MDScreen):
    pass

class AlertListItem(TwoLineAvatarIconListItem):
    """Elemento visual para representar una amenaza."""
    pass

class TrustActionBtn(IconRightWidget):
    """Botón que se agregará a la lista para autorizar aplicaciones."""
    pass

class ASSMApp(MDApp):
    # Mock Data para modo PC / Fallback
    mock_apps_data = [
        {'package_name': 'com.whatsapp', 'app_name': 'WhatsApp', 'permissions': ['android.permission.INTERNET', 'android.permission.READ_SMS']},
        {'package_name': 'com.google.android.apps.messaging', 'app_name': 'Mensajes de Google', 'permissions': ['android.permission.RECEIVE_SMS', 'android.permission.READ_SMS']},
        {'package_name': 'com.instagram.android', 'app_name': 'Instagram', 'permissions': ['android.permission.INTERNET', 'android.permission.CAMERA']},
        {'package_name': 'com.flashlight.pro.free', 'app_name': 'Linterna Pro', 'permissions': ['android.permission.CAMERA', 'android.permission.READ_SMS']},
        {'package_name': 'com.candy.crush.clone', 'app_name': 'Juego Gratis', 'permissions': ['android.permission.INTERNET', 'android.permission.RECEIVE_SMS']}
    ]

    def build(self):
        # Configuramos tema de KivyMD
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # DEFINICIÓN DE RUTA SEGURA PARA ENTORNO MÓVIL
        if platform == 'android':
            self.db_path = os.path.join(self.user_data_dir, 'assm_database.db')
        else:
            self.db_path = 'assm_database.db'
            
        # Inicializamos base de datos y whitelist
        init_db(self.db_path)
        add_to_whitelist(self.db_path, 'com.whatsapp', 'WhatsApp')
        add_to_whitelist(self.db_path, 'com.google.android.apps.messaging', 'Mensajes de Google')
        
        # Cargamos interfaz gráfica
        return Builder.load_string(KV)

    def change_screen(self, screen_name):
        self.root.current = screen_name

    def start_scan_thread(self):
        """Inicia el escaneo bloqueando el botón para evitar condiciones de carrera."""
        dashboard = self.root.get_screen('dashboard')
        dashboard.ids.status_label.text = "Analizando..."
        dashboard.ids.status_label.theme_text_color = "Secondary"
        dashboard.ids.scan_btn.disabled = True # Protección anti-spam

        # Limpiamos el historial viejo
        self.root.get_screen('history').ids.history_list.clear_widgets()

        thread = threading.Thread(target=self.scan_apps_simulation)
        thread.daemon = True
        thread.start()

    def scan_apps_simulation(self):
        """Motor híbrido que detecta Android o hace fallback a PC."""
        logging.info("\n--- Iniciando Escaneo Híbrido (Worker Thread) ---")
        suspicious_apps = []
        whitelist_packages = get_whitelist(self.db_path)
        CRITICAL_PERMISSIONS = ['android.permission.READ_SMS', 'android.permission.RECEIVE_SMS']
        
        if platform == "android":
            logging.info("Plataforma Android detectada. Iniciando escaneo nativo vía Pyjnius...")
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                current_activity = PythonActivity.mActivity
                PackageManager = autoclass('android.content.pm.PackageManager')
                package_manager = current_activity.getPackageManager()
                
                flags = PackageManager.GET_PERMISSIONS
                installed_packages = package_manager.getInstalledPackages(flags)
                
                if installed_packages:
                    # En Java, installed_packages es un List de objetos PackageInfo
                    for i in range(installed_packages.size()):
                        package_info = installed_packages.get(i)
                        package_name = package_info.packageName
                        
                        # Extraer nombre legible de la app
                        app_name = package_manager.getApplicationLabel(package_info.applicationInfo).toString()
                        
                        # Array de strings de permisos solicitados
                        permissions = package_info.requestedPermissions
                        
                        if permissions is not None:
                            for perm in permissions:
                                if perm in CRITICAL_PERMISSIONS:
                                    if package_name not in whitelist_packages:
                                        log_alert(self.db_path, package_name, app_name, perm, 'CRITICAL')
                                        suspicious_apps.append({
                                            'package_name': package_name,
                                            'app_name': app_name
                                        })
                                        break
            except Exception as e:
                logging.error(f"Error crítico en la extracción nativa de Android: {e}")
        else:
            logging.info("Plataforma no-Android (PC). Usando Mock Data (Fallback)...")
            time.sleep(1.5)  # Efecto visual de carga
            
            for app in self.mock_apps_data:
                package = app.get('package_name', 'Unknown')
                name = app.get('app_name', 'Unknown')
                permissions = app.get('permissions', [])
                
                if permissions is not None:
                    for perm in permissions:
                        if perm in CRITICAL_PERMISSIONS:
                            if package not in whitelist_packages:
                                log_alert(self.db_path, package, name, perm, 'CRITICAL')
                                suspicious_apps.append(app)
                                break
        
        # Schedule the UI update safely on the main thread
        Clock.schedule_once(lambda dt: self.update_ui_after_scan(suspicious_apps))

    def update_ui_after_scan(self, suspicious_apps):
        """Callback ejecutado en el hilo principal para renderizar resultados."""
        dashboard = self.root.get_screen('dashboard')
        history_list = self.root.get_screen('history').ids.history_list
        dashboard.ids.scan_btn.disabled = False # Reactivamos el botón

        if suspicious_apps:
            dashboard.ids.status_label.text = f"¡Amenazas Detectadas! ({len(suspicious_apps)})"
            dashboard.ids.status_label.theme_text_color = "Error"
            
            for app in suspicious_apps:
                item = AlertListItem(
                    text=f"[color=#ff0000]{app['app_name']}[/color]",
                    secondary_text=app['package_name']
                )
                
                icon_left = IconLeftWidget(
                    icon="alert-circle", 
                    theme_text_color="Custom", 
                    text_color=(1, 0, 0, 1)
                )
                item.add_widget(icon_left)
                
                icon_right = TrustActionBtn(
                    icon="shield-check",
                    theme_text_color="Custom",
                    text_color=(0, 0.7, 0, 1),
                    on_release=lambda x, p=app['package_name'], n=app['app_name'], i=item: self.trust_app(p, n, i)
                )
                item.add_widget(icon_right)
                
                history_list.add_widget(item)
        else:
            dashboard.ids.status_label.text = "Dispositivo Seguro"
            dashboard.ids.status_label.theme_text_color = "Primary"

    def trust_app(self, package_name, app_name, item_widget):
        """Agrega a whitelist de forma segura y actualiza la UI."""
        add_to_whitelist(self.db_path, package_name, app_name)
        
        history_list = self.root.get_screen('history').ids.history_list
        history_list.remove_widget(item_widget)
        
        remaining_alerts = len(history_list.children)
        dashboard = self.root.get_screen('dashboard')
        
        if remaining_alerts == 0:
            dashboard.ids.status_label.text = "Dispositivo Seguro"
            dashboard.ids.status_label.theme_text_color = "Primary"
        else:
            dashboard.ids.status_label.text = f"¡Amenazas Detectadas! ({remaining_alerts})"

if __name__ == '__main__':
    ASSMApp().run()
