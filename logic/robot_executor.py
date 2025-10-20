
import robot
import threading
import subprocess
import os
import sys
import json
import time
import ast
from datetime import datetime, timezone
from robot.rebot import rebot_cli
from logic import db_handler # Importamos el manejador de la BD
from robot.api import TestSuiteBuilder
import glob
import socket


TEST_DIRECTORY = "tests"



class TestOutputListener:
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, app_ref):
        self.app_ref = app_ref
        # Basic Config
        self.modules = None
        self.tp1_info = None
        self.tp2_info = None
        self.num_inputs = 0
        self.num_outputs = 0
        self.command_ranges = None
        # SNMP Config attributes
        self.snmp_agent_state = None
        self.traps_enable_state = None
        self.tpu_snmp_port = None
        self.snmp_v1_v2_enable = None
        self.snmp_v1_v2_read = None
        self.snmp_v1_v2_set = None
        self.snmp_v3_enable = None
        self.snmp_v3_read_user = None
        self.snmp_v3_read_pass = None
        self.snmp_v3_read_auth = None
        self.snmp_v3_write_user = None
        self.snmp_v3_write_pass = None
        self.snmp_v3_write_auth = None
        self.hosts_config = None
        # Input Activation attributes
        self.input_activation_state = None
        self.input_info = None
        # Chronological Register attributes
        self.chronological_log = None
        # Alignment attributes
        self.loop_state_1 = None
        self.loop_state_2 = None
        self.blocking_state_1 = None
        self.blocking_state_2 = None
        self.loop_module_name_1 = None
        self.loop_module_name_2 = None
        self.loop_type_1 = None
        self.loop_type_2 = None
        self.blocking_module_name_1 = None
        self.blocking_module_name_2 = None
        # IBTU ByTones attributes
        self.ibtu_tx_tones = None
        self.ibtu_rx_tones = None
        self.ibtu_tx_scheme = None
        self.ibtu_tx_guard_freq = None
        self.ibtu_rx_scheme = None
        self.ibtu_rx_guard_freq = None


        
    def log_message(self, message):
        msg_text = message.message.strip()

        # --- Lógica de GUI_STATUS y GUI_ERROR (debe ir primero) ---
        if msg_text.startswith("GUI_ERROR:"):
            error_msg = msg_text.split(":", 1)[1].strip()
            self.app_ref.gui_queue.put(('main_status', f"Error: {error_msg}", "red"))
            return

        if msg_text.startswith("GUI_STATUS:"):
            status_update = msg_text.split(":", 1)[1].strip()
            self.app_ref.gui_queue.put(('snmp_status', status_update))
            return
            
        if msg_text.startswith("GUI_ALARMS::"):
            json_part = msg_text.split("::", 1)[1]
            try:
                self.alarms_data = json.loads(json_part)
            except json.JSONDecodeError as e:
                error_msg = f"Error al procesar datos JSON de alarmas: {e}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
            return # Salimos para no procesar más
            
        
        # --- Lógica para variables normales (nivel INFO) ---
        if message.level == 'INFO':
            parsers = {
                '${Detected_Module_List}': 'modules',
                '${Tp1_info}': 'tp1_info',
                '${Tp2_info}': 'tp2_info',
                '${local_teleprotection_commands_list}': 'command_ranges',
                '${input_count}': 'num_inputs',
                '${output_count}': 'num_outputs',
                '${snmp_agent_state}': 'snmp_agent_state',
                '${traps_enable_state}': 'traps_enable_state',
                '${tpu_snmp_port}': 'tpu_snmp_port',
                '${snmp_v1_v2_enable}': 'snmp_v1_v2_enable',
                '${snmp_v1_v2_read}': 'snmp_v1_v2_read',
                '${snmp_v1_v2_set}': 'snmp_v1_v2_set',
                '${snmp_v3_enable}': 'snmp_v3_enable',
                '${snmp_v3_read_user}': 'snmp_v3_read_user',
                '${snmp_v3_read_pass}': 'snmp_v3_read_pass',
                '${snmp_v3_read_auth}': 'snmp_v3_read_auth',
                '${snmp_v3_write_user}': 'snmp_v3_write_user',
                '${snmp_v3_write_pass}': 'snmp_v3_write_pass',
                '${snmp_v3_write_auth}': 'snmp_v3_write_auth',
                '${retrieved_hosts}': 'hosts_config',
                '${Current_State}': 'input_activation_state',
                '${INPUT_INFO}': 'input_info',
                '${Loop_State_1}': 'loop_state_1',
                '${Loop_State_2}': 'loop_state_2',
                '${Loop_ModuleName_1}': 'loop_module_name_1',
                '${Loop_ModuleName_2}': 'loop_module_name_2',
                '${Loop_Type_1}': 'loop_type_1',
                '${Loop_Type_2}': 'loop_type_2',
                '${Blocking_State_1}': 'blocking_state_1',
                '${Blocking_State_2}': 'blocking_state_2',
                '${Blocking_ModuleName_1}': 'blocking_module_name_1',
                '${Blocking_ModuleName_2}': 'blocking_module_name_2',
                '${IBTU_TX_TONES}': 'ibtu_tx_tones',
                '${IBTU_RX_TONES}': 'ibtu_rx_tones',
                '${IBTU_TX_SCHEME}': 'ibtu_tx_scheme',
                '${IBTU_TX_GUARD_TONE_FREQ}': 'ibtu_tx_guard_freq',
                '${IBTU_RX_SCHEME}': 'ibtu_rx_scheme',
                '${IBTU_RX_GUARD_TONE_FREQ}': 'ibtu_rx_guard_freq',

            }
            for key, attr in parsers.items():
                if key in msg_text and '=' in msg_text:
                    if msg_text.find(key) < msg_text.find('='):
                        self._parse_and_set(msg_text, attr)
                        return

        # --- Lógica para el cronológico (nivel WARN) ---
        elif message.level == 'WARN':
            if msg_text.startswith("GUI_DATA::"):
                json_part = msg_text.split("::", 1)[1]
                try:
                    parsed_value = ast.literal_eval(json_part)
                    self.chronological_log = parsed_value
                except Exception as e:
                    error_msg = f"Error al procesar datos del cronológico: {e}"
                    self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
        
    def _parse_and_set(self, text, attribute):
        """Helper to parse a string and set an attribute."""
        try:
            value_part = text.split('=', 1)[1].strip()
            parsed_value = ast.literal_eval(value_part)
            setattr(self, attribute, parsed_value)
        except (ValueError, SyntaxError, IndexError):
            value_str = text.split('=', 1)[1].strip()
            setattr(self, attribute, value_str)
        except Exception as e:
            print(f"Listener Error: Could not parse or set '{attribute}'. Details: {e}")



def _run_robot_test(app_ref, test_name, variables=None, on_success=None, on_pass_message="Test Passed!", on_fail_message="Test Failed!", preferred_filename=None, output_filename=None, log_file="log.html", report_file="report.html", suppress_gui_updates=False):
    """Generic function to run a robot test."""
    session_file_path = os.path.abspath("session.json")
    if not app_ref.browser_process or not os.path.exists(session_file_path):
        app_ref.gui_queue.put(('main_status', "Error: No hay una sesión activa. Por favor, conéctese primero.", "red"))
        app_ref.gui_queue.put(('enable_buttons', None))
        return

    robot_script_path = _find_test_file(app_ref, test_name, preferred_filename=preferred_filename)
    if not robot_script_path:
        app_ref.gui_queue.put(('main_status', f"Error: Test case '{test_name}' not found.", "red"))
        app_ref.run_button_state(is_running=False)
        return

    ip = app_ref.entry_ip.get()
    all_variables = [f"IP_ADDRESS:{ip}"]
    if variables:
        all_variables.extend(variables)


    output_file = output_filename if output_filename else "output.xml" # Para usar el nombre único
    result_code = -1 # Valor por defecto en caso de error

    listener = TestOutputListener(app_ref)
    
    # Logica Semaforo pull alarmas
    app_ref.is_main_task_running = True # Luz roja
    try:
        result_code = robot.run(
            robot_script_path,
            test=test_name,
            variable=all_variables,
            outputdir="test_results",
            output=output_file,
            log=log_file, report=report_file, 
            listener=listener,
            stdout=None, stderr=None
        )
        # Si el test pasó y por el argumento de on_success nos pasan la función callback. como puede ser create_gui_update_callback(message_type, attr_names)
        if result_code == 0 and on_success:
            on_success(listener)    

        if not suppress_gui_updates: # Solo actualiza la GUI si no es una ejecución del planificador. 
            if result_code == 0:
                app_ref.gui_queue.put(('main_status', f"Status: {on_pass_message} (PASS)", "#2ECC71"))
            else:
                app_ref.gui_queue.put(('main_status', f"Status: {on_fail_message} (FAIL)", "#E74C3C"))
            
            
    except Exception as e:
        if not suppress_gui_updates:
            app_ref.gui_queue.put(('main_status', f"Critical Error: {e}", "#E74C3C"))
            
    finally: 
        app_ref.is_main_task_running = False # Luz verde Semaforo Monitoreo Alarmas
        if not suppress_gui_updates:    
            app_ref.gui_queue.put(('enable_buttons', None))
        
    return result_code




# ***** MANEJO DE LA SESIÓN DEL NAVEGADOR *****
def _start_browser_process_thread(app_ref):
    """Starts the browser process in a separate thread."""
    app_ref.run_button_state(is_running=True)
    threading.Thread(target=_execute_start_browser, args=(app_ref,), daemon=True).start()

def _execute_start_browser(app_ref):
    """Executes start_browser.robot to open and maintain the browser session."""
    if app_ref.browser_process:
        app_ref.gui_queue.put(('main_status', "Aviso: Ya hay una sesión activa.", "orange"))
        app_ref.gui_queue.put(('enable_buttons', None))
        return
    
    app_ref.gui_queue.put(('session_status', "Conectando...", "orange"))
    
    session_file_path = os.path.abspath("session.json")
    if os.path.exists(session_file_path):
        os.remove(session_file_path)

    ip = app_ref.entry_ip.get()
    command = [
        sys.executable, '-m', 'robot',
        '--outputdir', 'test_results',
        '--log', 'None', '--report', 'None',
        '--variable', f'IP_ADDRESS:{ip}',
        '--variable', f'SESSION_FILE_PATH:{session_file_path}',
        os.path.join(TEST_DIRECTORY, 'start_browser.robot')
    ]
    
    app_ref.browser_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    session_file_found = False
    timeout = 50 # segundos
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(session_file_path):
            session_file_found = True
            break
        if app_ref.browser_process.poll() is not None:
            break 
        time.sleep(0.5)

    if session_file_found:
        app_ref.gui_queue.put(('session_status', "Conectado", "green"))
        app_ref.gui_queue.put(('main_status', "Sesión iniciada. Listo para ejecutar acciones.", "white"))
        # app_ref.session_controller.start_keep_alive()   # Llamamos al creador del hilo "_keep_alive_loop", que se ejecutará cada 15s
    else:
        app_ref.gui_queue.put(('session_status', "Error", "red"))
        app_ref.gui_queue.put(('main_status', "Error: No se pudo iniciar la sesión. Revise la consola.", "red"))
        stdout, stderr = app_ref.browser_process.communicate()
        print("--- STDOUT del proceso del navegador ---")
        print(stdout)
        print("--- STDERR del proceso del navegador ---")
        print(stderr)
        # Si el tiempo se agota, nos aseguramos de terminar el proceso para que no quede huérfano.
        if app_ref.browser_process.poll() is None: # Si el proceso todavía está corriendo
            app_ref.browser_process.terminate()
        app_ref.browser_process = None

    app_ref.gui_queue.put(('enable_buttons', None))

def _stop_browser_process_thread(app_ref):
    """Stops the browser process in a separate thread."""
    app_ref.run_button_state(is_running=True)
    threading.Thread(target=_execute_stop_browser, args=(app_ref,), daemon=True).start()
    
def _execute_stop_browser(app_ref):
    """Executes a robot script to close all browser windows and then cleans up."""
    # app_ref.session_controller.stop_keep_alive()
    session_file_path = os.path.abspath("session.json")
    # Comprobamos si hay alguna sesion activa que haga falta cerrar.
    if not app_ref.browser_process:
        app_ref.gui_queue.put(('main_status', "Aviso: No hay ninguna sesión activa para cerrar.", "orange"))
        app_ref.gui_queue.put(('enable_buttons', None))
        return
    
    try:
        # Ejecutamos el script "close_all_browsers.robot"
        robot.run(
            os.path.join(TEST_DIRECTORY, 'close_all_browsers.robot'),
            output=None, log=None, report=None,
            stdout=None, stderr=None
        )
    except Exception as e:
        app_ref.gui_queue.put(('main_status', f"Error al cerrar la sesión: {e}", "red"))
        print(f"Error ejecutando close_all_browsers.robot, se terminará el proceso a la fuerza. Error: {e}")
        
    
    finally: # Limpieza final, se haya producido un error o no.
        if app_ref.browser_process:
            app_ref.browser_process.terminate()
            app_ref.browser_process = None
            
        if os.path.exists(session_file_path):
            os.remove(session_file_path)

        app_ref.gui_queue.put(('main_status', "Sesión del navegador cerrada.", "white"))
        app_ref.gui_queue.put(('session_status', "Desconectado", "orange"))
        app_ref.gui_queue.put(('enable_buttons', None))

    
# ****** METODOS VARIOS DE UTILIDAD *****
def _read_test_names(robot_file_path):
    try:
        suite = TestSuiteBuilder().build(robot_file_path)
        return [test.name for test in suite.tests]
    except Exception as e:
        print(f"Error reading {robot_file_path}: {e}")
        return []

def _discover_and_load_tests(app_ref, directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)
        with open(os.path.join(directory, "example_tests.robot"), "w") as f:
            f.write("*** Settings ***\nLibrary    OperatingSystem\n\n*** Test Cases ***\nExample Test\n    Log To Console    Hello from example test\n")
    search_pattern = os.path.join(directory, '*.robot')
    robot_files = glob.glob(search_pattern)
    return {file: _read_test_names(file) for file in robot_files}

def _find_test_file(app_ref, test_name, preferred_filename=None):
    """Finds the .robot file that contains a specific test case, optionally in a preferred file."""
    if preferred_filename:
        full_path = os.path.join(TEST_DIRECTORY, preferred_filename)
        tests_to_check = test_name if isinstance(test_name, list) else [test_name]
        if full_path in app_ref.tests_data and all(t in app_ref.tests_data[full_path] for t in tests_to_check):
            return full_path
    
    tests_to_check = test_name if isinstance(test_name, list) else [test_name]
    for file_path, test_list in app_ref.tests_data.items():
        if all(t in test_list for t in tests_to_check):
            return file_path
    return None

