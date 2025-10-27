import json
import os
from robot.libraries.BuiltIn import BuiltIn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

class BrowserManager:
    
    _main_session_id = None

    # Utilizamos tecnica de MonkeyPatching para conectar a una sesion existente
    def conectar_a_navegador_existente(self, session_alias, session_file_path):
        """
        Conecta a una sesión de navegador existente (sin crear nuevas ventanas), usando un alias y un path de archivo de la sesion.
        """
        try:
            selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
            builtin = BuiltIn()

            # Cargamos info de la sesión
            # session_file_path = os.path.abspath(session_file_path)
            with open(session_file_path, 'r') as f:
                session_data = json.load(f)

            executor_url = session_data['executor_url']
            session_id = session_data['session_id']
            # BrowserManager._main_session_id = session_id  # No hace falta si no usamos cleanup_ghost_drivers

            # *** Truco: crear Remote sin lanzar newSession ***
            original_execute = webdriver.Remote.execute

            def new_execute(self, command, params=None):
                if command == "newSession":
                    return {
                        "value": {
                            "sessionId": session_id,
                            "capabilities": {}
                        }
                    }
                return original_execute(self, command, params)

            webdriver.Remote.execute = new_execute

            driver = webdriver.Remote(
                command_executor=executor_url,
                options=ChromeOptions()
            )
            driver.session_id = session_id

            # Restauramos método original
            webdriver.Remote.execute = original_execute

            # Registramos el driver sin abrir nada nuevo
            alias = session_alias
            selenium_lib._drivers.register(driver, alias)
            builtin.run_keyword('Switch Browser', alias)

            builtin.log(f"DEBUG: Conectado a sesión {alias} existente: {session_id}", "INFO")
            
        except FileNotFoundError:
            BuiltIn().fatal_error(f"Suite Setup (Conectar a Sesión {session_alias}) falló: No se encontró el archivo de sesión en '{session_file_path}'")
        except Exception as e:
            BuiltIn().fatal_error(f"Suite Setup (Conectar a Sesión {session_alias}) falló al procesar '{session_file_path}': {e}")

    def cleanup_ghost_drivers(self):
        """
        Cierra cualquier navegador 'fantasma' que no corresponda a la sesión principal.
        """
        try:
            selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
            builtin = BuiltIn()
            
            if not BrowserManager._main_session_id:
                builtin.log("DEBUG: No hay sesión principal registrada, se omite limpieza.", "INFO")
                return

            # Clonamos los alias para iterar con seguridad
            all_aliases = list(selenium_lib._drivers._aliases.keys())
            if len(all_aliases) <= 1:
                builtin.log("DEBUG: Solo hay una sesión activa, sin limpieza necesaria.", "INFO")
                return

            for alias in all_aliases:
                try:
                    builtin.run_keyword('Switch Browser', alias)
                    driver = selenium_lib.driver  # ✅ acceso directo al driver actual
                    
                    if driver.session_id != BrowserManager._main_session_id:
                        builtin.log(f"DEBUG: Cerrando navegador fantasma con alias '{alias}'.", "INFO")
                        driver.quit()
                        
                        # ✅ Eliminar alias manualmente de la caché interna
                        if alias in selenium_lib._drivers._aliases:
                            del selenium_lib._drivers._aliases[alias]
                        
                        if driver in selenium_lib._drivers._connections:
                            selenium_lib._drivers._connections.remove(driver)

                except Exception as inner_e:
                    builtin.log(f"WARNING: No se pudo limpiar alias '{alias}': {inner_e}", "WARN")

            # Regresamos al navegador principal
            builtin.run_keyword('Switch Browser', 'main_session')

        except Exception as e:
            BuiltIn().fatal_error(f"Test Setup (cleanup) falló: {e}")
            
    def cerrar_sesion_principal_y_salir(self, session_alias):
        """
        Cierra de forma definitiva la sesión principal del navegador usando driver.quit().
        """
        try:
            builtin = BuiltIn()
            
            # 1. Aseguramos que estamos en el navegador principal
            builtin.log(f"--- DEBUG (Python): Intentando Switch Browser a alias: {session_alias} ---", "INFO")
            builtin.run_keyword('Switch Browser', session_alias)
            
            # 2. Obtenemos su instancia de webdriver
            selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
            driver = selenium_lib.driver
            
            # 3. Usamos el método más potente para cerrar todo
            driver.quit()
            
            builtin.log(f"--- DEBUG (Python): 'driver.quit()' ejecutado para {session_alias}. Sesión finalizada. ---", "INFO")
        except Exception as e:
            BuiltIn().log(f"Error durante el cierre definitivo de la sesión (alias={session_alias}): {e}", "WARN")
