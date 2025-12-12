import customtkinter as ctk
import tkinter as tk
import robot
import threading
import subprocess
import os
import sys
import glob
import io
import re
import json
import socket
import queue
import time
from pathlib import Path
from robot.api import TestSuiteBuilder
import time
from tomlkit import key

from Trap_Receiver_GUI_oriented import Trap_Receiver_GUI_oriented

import sqlite3
from datetime import datetime, timezone
from robot.rebot import rebot_cli
# Para poder abrir archivos
from tkinter import filedialog

# directorio donde está app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos para llegar a la raíz del proyecto
project_root = os.path.dirname(current_dir)

# para el widget Treeview (Tabla)
from tkinter import ttk

# ruta a la carpeta tests
tests_dir = os.path.join(project_root, 'tests')

if tests_dir not in sys.path:   # Añadimos la carpeta tests al sys.path para poder importar MyKeywords
    sys.path.insert(0, tests_dir)
    
import MyKeywords  
    
    

# *******************IMPORTS DE OTRAS PARTES DEL PROYECTO*************************
import gui.ui_sidebar as ui_sidebar
import gui.ui_tab_scheduler as ui_tab_scheduler
import gui.ui_tab_equipment as ui_tab_equipment
import gui.ui_tab_monitoring as ui_tab_monitoring
import gui.ui_tab_alignment as ui_tab_alignment
import gui.ui_tab_alarms as ui_tab_alarms

import logic.db_handler as db_handler
import logic.robot_executor as robot_executor

# import tests.MyKeywords as MyKeywords

from logic.scheduler_controller import SchedulerController
from logic.equipment_controller import EquipmentController
from logic.monitoring_controller import MonitoringController
from logic.alignment_controller import AlignmentController
from logic.snmp_controller import SNMPController
from logic.trap_listener_controller import TrapListenerController
from logic.alarms_controller import AlarmsController





# --- CONFIGURATION ---
TEST_DIRECTORY = "tests"

class ModernTestRunnerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # *** INYECCIÓN DE DEPENDENCIA ***
        # La app se mete a sí misma dentro del módulo de Robot.
        MyKeywords.ACTIVE_APP_REF = self
        # ******* 1. INICIALIZACIÓN DE LA VENTANA PRINCIPAL *******
        self.title("ZIV TPU-1 Test Bench")
        self.geometry("1100x850") 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ************ 2. INICIALIZACIÓN DEL ESTADO Y DATOS ************
        self.sessions = {
            'A': {'ip': None, 'process': None, 'status': 'Desconectado', 'session_file': os.path.abspath("session_A.json")},
            'B': {'ip': None, 'process': None, 'status': 'Desconectado', 'session_file': os.path.abspath("session_B.json")}
        }
        self.active_session_id = 'A' # 'A' o 'B'
        self.is_main_task_running = False    # Para indicar al hilo que hace pull para comprobar alarmas si hay algun otro test ejecutandose y así no interferir.
        
        # *** LISTENER ***
        # self.is_snmp_listener_running = False   # Flag para el estado del listener

        # self.trap_receiver = Trap_Receiver_GUI_oriented()
        # self.snmp_listener_thread = None
        
        self.trap_listeners = {
            'A': {
                'trap_receiver': Trap_Receiver_GUI_oriented(),
                'listener_thread': None,
                'is_running': False,
                'port_widget': None, 
                'start_button': None,
                'stop_button': None,
                'status_label': None,
                'trap_display_widget': None, 
                'filter_entry_widget': None,
                'show_all_button': None,
                'filter_button': None,
                'reset_button': None,
                'main_frame': None # Contiene todos los widgets de esta sesión
            },
            'B': {
                'trap_receiver': Trap_Receiver_GUI_oriented(),
                'listener_thread': None,
                'is_running': False,
                'port_widget': None,
                'start_button': None,
                'stop_button': None,
                'status_label': None,
                'trap_display_widget': None,
                'filter_entry_widget': None,
                'show_all_button': None,
                'filter_button': None,
                'reset_button': None,
                'main_frame': None # Contiene todos los widgets de esta sesión
            }
        }
        
        self.active_listener_view = 'A' # Vista del listener que tenemos activo. Similar a "active_session_id"
        
        self.gui_queue = queue.Queue()
        
        # Diccionario para almacenar el estado de la GUI PARA CADA SESIÓN! _create_default_gui_data_state nos devuelve la estructura de datos que necesitamos inicializar.
        self.session_gui_data = {
            'A': self._create_default_gui_data_state(),
            'B': self._create_default_gui_data_state()
        }
        
        
        # MAPAS DE DATOS Y CONFIGURACIONES
        self.test_variable_map = {
            # --- Tests de Configuración Básica ---
            "List Detected Modules": [],
            "List assigned Modules and Commands assigned": [],
            "Assign Prioritized Detected Modules": ["TP1", "TP2"],
            "Command Number Assignments": [
                "TP1_TX_Command_Number_NUM_COMMANDS", 
                "TP1_RX_Command_Number_NUM_COMMANDS", 
                "TP2_TX_Command_Number_NUM_COMMANDS", 
                "TP2_RX_Command_Number_NUM_COMMANDS"
            ],
            "Open_BasicConfiguration+Configure Display Time Zone": ["Time_zone"],

            # --- Tests de Asignación de Comandos ---
            "Log and Save Teleprotection Commands and Inputs/Outputs": [],
            "Program Command Assignments": [
                "tx_matrix_str", 
                "rx_matrix_str", 
                "tx_list_str", 
                "rx_list_str"
            ],

            # --- Tests de SNMP ---
            "Retrieve Full SNMP Configuration": [],
            "Execute Full SNMP Configuration": [
                "SNMP_AGENT_STATE", "TRAPS_ENABLE_STATE", "TPU_SNMP_PORT", 
                "SNMP_V1_V2_ENABLE", "SNMP_V1_V2_READ", "SNMP_V1_V2_SET", 
                "SNMP_V3_ENABLE", "SNMP_V3_READ_USER", "SNMP_V3_READ_PASS", 
                "SNMP_V3_READ_AUTH", "SNMP_V3_WRITE_USER", "SNMP_V3_WRITE_PASS", 
                "SNMP_V3_WRITE_AUTH", "HOSTS_CONFIG_STR"
            ],

            # --- Tests de Alineación (Alignment) ---
            "Input Activation": ["ACTIVATE_DEACTIVATE", "DURATION", "INPUTS_LIST"],
            "Retrieve Inputs Activation State": [],
            "Current Loop and Blocking State": [],
            "Program Teleprotection Loop": [
                "LOOP_TELEPROTECTION_NUMBER", 
                "ACTIVATE_DEACTIVATE_LOOP", 
                "LOOP_TYPE", 
                "LOOP_DURATION"
            ],
            "Program Teleprotection Blocking": [
                "BLOCKING_TELEPROTECTION_NUMBER", 
                "ACTIVATE_DEACTIVATE_BLOCKING", 
                "BLOCKING_DURATION"
            ],
            # --- Tests HIL ---
            "Send Input Command": ["RASPBERRY_PI_IP: COMMAND_STR:PULSE_BATCH,<t>,<pin_id1>,<pin_id2>,... NETWORK_PROFILE:NOISE"],
            # "Ejecutar Rafaga De Rendimiento": ["NUM_PULSES: CHANNEL: PULSE_DURATION: LOOP_DELAY:"], # Antiguo, para un solo canal
            "Ejecutar Rafaga De Rendimiento": ["CHANNELS_TO_TEST: NUM_PULSES: PULSE_DURATION: LOOP_DELAY: NETWORK_PROFILE:NOISE"],
            "Ejecutar Rafaga GUI": ["CHANNELS_STR: NUM_PULSES: PULSE_DURATION: LOOP_DELAY: NETWORK_PROFILE:NOISE"],
            "Escenario 4: Prueba de Sensibilidad PWM" : ["CHANNELS_TO_TEST: START: END: NETWORK_PROFILE:NOISE"],
            "Ejecutar Rafaga De Rendimiento Funcional": ["CHANNELS_TO_TEST: NUM_PULSES: PULSE_DURATION: LOOP_DELAY: MAX_LATENCY_THRESHOLD: NETWORK_PROFILE:NOISE"],
            
            # --- Tests Inyeccion Ruido Netstorm---
            # "Escenario WP3: Activar Perfil NOISE en Netstorm": ["NETSTORM_IP: NETSTORM_VNC_PASS:"],
            # "Escenario WP3: Activar Perfil CLEAN en Netstorm": ["NETSTORM_IP: NETSTORM_VNC_PASS:"],
            
            # --- Tests de Registro Cronológico ---
            "Retrieve Chronological Register": [],
            "Delete Chronological Register": [],
            "Capture Last Chronological Log Entries": [
                "EXPECTED_NUM_ENTRIES", 
                "EVENT_ALARM_FILTER", 
                "CHRONO_ORDER"
            ],

            # --- Tests de Módulo IBTU BYTONES ---
            "Retrieve IBTU ByTones Full Configuration": [],
            "Program IBTU ByTones S1 General": [
                "RX_OPERATION_MODE", 
                "LOCAL_PERIODICITY", 
                "REMOTE_PERIODICITY", 
                "SNR_THRESHOLD_ACTIVATION", 
                "SNR_THRESHOLD_DEACTIVATION"
            ],
            "Program IBTU ByTones S2 Frequencies": [
                "TX_SCHEME", "TX_GUARD_FREQUENCY", "TX_APPLICATION_TYPE_LIST_STR", 
                "TX_FREQUENCY_LIST_STR", "RX_SCHEME", "RX_GUARD_FREQUENCY", 
                "RX_APPLICATION_TYPE_LIST_STR", "RX_FREQUENCY_LIST_STR"
            ],
            "Program IBTU ByTones S3 Levels": [
                "BY_TONES_INPUT_LEVEL", 
                "BY_TONES_POWER_BOOSTING", 
                "BY_TONES_OUTPUT_LEVEL"
            ],
            
            "Retrieve IBTU FFT Full Configuration": [],
            "Program IBTU FFT S1 General": [
                "LOCAL_PERIODICITY", "REMOTE_PERIODICITY",
                "SNR_THRESHOLD_ACTIVATION", "SNR_THRESHOLD_DEACTIVATION",
                "RX_OPERATION_MODE_LIST_STR"
            ],
            "Program IBTU FFT S2 General": [
                "TX_BW", "TX_GUARD_FREQ", "TX_APPLICATION_MODE_LIST_STR",
                "RX_BW", "RX_GUARD_FREQ", "RX_APPLICATION_MODE_LIST_STR"
            ],
            "Program IBTU FFT S3 General": [
                "INPUT_LEVEL", "POWER_BOOSTING", "OUTPUT_LEVEL"
            ],
            
        }

        # DICCIONARIO DE MAPEO DE ACTUALIZACIÓN DE GUI
        # Asocia un nombre de test con el mensaje de la cola y los atributos del listener necesarios.
        self.test_gui_update_map = {
            # Candidatos normales
            "List Detected Modules": ('modules_display', ['modules']),
            "List assigned Modules and Commands assigned": ('assigned_modules_display', ['tp1_info', 'tp2_info']),
            "Log and Save Teleprotection Commands and Inputs/Outputs": ('command_assignment_grids', ['command_ranges', 'num_inputs', 'num_outputs']),
            "Retrieve Inputs Activation State": ('update_input_activation_display', ['input_activation_state', 'input_info']),
            "Capture Last Chronological Log Entries": ('update_chrono_log_display', ['chronological_log']),
            "Scrape And Return Alarms": ('update_alarms_display', ['alarms_data']),
            
            # Casos Especiales (pasarán el listener completo)
            "Current Loop and Blocking State": ('update_alignment_states', ['listener']),
            "Retrieve Full SNMP Configuration": ('full_snmp_config_display', ['listener']),
            "Retrieve IBTU ByTones Full Configuration": ('update_ibtu_full_config', ['listener']),
            "Retrieve IBTU FFT Full Configuration": ('update_ibtu_fft_config', ['ibtu_fft_data']),

        }
# **************************************************************************************************************

        self.timezone_map = {
            "UTC": "0", "(UTC+1)Lisboa": "1", "(UTC+2)Madrid": "2", "(UTC+2)Paris": "3", "(UTC+2)Oslo": "4",
            "(UTC+2)Warsaw": "5", "(UTC+2)Stockholm": "6", "(UTC+3)Helsinki": "7", "(UTC+3)Athens": "8",
            "(UTC+3)Moscow": "9", "(UTC+7)Jakarta": "10", "(UTC+8)Perth": "11", "(UTC+9.5)Adelaide": "12",
            "(UTC+10)Sidney": "13", "(UTC+12)Wellington": "14", "(UTC-10)Honolulu": "15",
            "(UTC-3)Buenos Aires": "16", "(UTC-5)Bogotá": "17", "(UTC-8)Anchorage": "18"
        }
        self.trap_mode_map = { "V.1 Trap": '0', "V.2c Trap": '1', "V.2c Inform": '2', "V.3 Trap": '3', "V.3 Inform": '4' }
        self.trap_mode_map_rev = {v: k for k, v in self.trap_mode_map.items()}
        self.duration_map = { "Permanente": "0", "10 segundos": "10", "30 segundos": "30", "60 segundos": "60", "10 minutos": "600" }
        self.loop_type_map = { "NONE": "0", "INTERNAL": "1", "LINE": "2" }
        self.loop_type_map_rev = {v: k for k, v in self.loop_type_map.items()}
        
        # IBTU_ByTones
        self.ibtu_rx_op_mode_map = {"Normal": "0", "Telesignalling": "1"}
        self.ibtu_app_type_map = {"Blocking": "0", "Permissive": "1", "Direct": "2"}
        self.ibtu_app_type_map_rev = {v: k for k, v in self.ibtu_app_type_map.items()}
        self.ibtu_scheme_map = {"2+2 (1)": "0", "3+1 (1)": "1", "3+1 (2)": "2", "2+2 (2)": "4"}
        self.ibtu_scheme_map_rev = {v: k for k, v in self.ibtu_scheme_map.items()}
        
        self.ibtu_freq_map = {
            "Blocking": ["0", "1200", "1260", "1380", "1440", "1500", "1560", "1620", "1680", "1740", "1860", "1920", "1980", "2040", "2100", "2160", "2220", "2340", "2400", "2460", "2520", "2580", "2640", "2700", "2820", "2880", "2940", "3000", "3060", "3120", "3180", "3300", "3360", "3420", "3480", "3540", "3600", "3660", "3780", "3800"],
            "Permissive": ["0", "480", "540", "600", "660", "720", "780", "900", "960", "1020", "1080", "1140", "1200", "1260", "1380", "1440", "1500", "1560", "1620", "1680", "1740", "1860", "1920", "1980", "2040", "2100", "2160", "2220", "2340", "2400", "2460", "2520", "2580", "2640", "2700", "2820", "2880", "2940", "3000", "3060", "3120", "3180", "3300", "3360", "3420", "3480", "3540", "3600", "3660", "3780", "3800"],
            "Direct": ["0", "420", "480", "540", "600", "660", "720", "780", "900", "960", "1020", "1080", "1140", "1200", "1260", "1380", "1440", "1500", "1560", "1620", "1680", "1740", "1860", "1920", "1980", "2040", "2100", "2160", "2220", "2340", "2400", "2460", "2520", "2580", "2640", "2700", "2820", "2880", "2940", "3000", "3060", "3120", "3180", "3300", "3360", "3420", "3480", "3540", "3600", "3660", "3780", "3800"]
        }
        all_freqs = set()
        for freq_list in self.ibtu_freq_map.values():
            all_freqs.update(freq_list)
        self.all_ibtu_frequencies = sorted(list(all_freqs), key=int)

        # IBTU FFT
        # Para coger el valor corresondiente a la clave en formato leído y pasarselo al archivo .robot
        self.fft_bw_map = {"1 kHz": "1", "2 kHz": "2", "4 kHz": "3"}
        self.fft_rx_op_mode_map = {"Normal": "0", "Telesignalling": "1"}
        self.fft_app_mode_map = {"Blocking": "0", "Permissive": "1", "Direct": "2"}

        # El listener nos pasa el valor en formato numerico y accediendo al diccionario _rev correspondiente obtenemos el valor (formato legible) de la clave correspondiente. 
        self.fft_bw_map_rev = {v: k for k, v in self.fft_bw_map.items()}
        self.fft_rx_op_mode_map_rev = {v: k for k, v in self.fft_rx_op_mode_map.items()}
        self.fft_app_mode_map_rev = {v: k for k, v in self.fft_app_mode_map.items()}
        
        # LISTAS PARA WIDGETS Y ESTADO
        self.tx_checkboxes, self.rx_checkboxes, self.tx_logic_checkboxes, self.rx_logic_checkboxes = [], [], [], []
        self.host_widgets, self.input_activation_checkboxes, self.log_buttons = [], [], []
        self.inputs_are_active, self.activation_timer = None, None
        self.loop1_widgets, self.loop2_widgets, self.blocking1_widgets, self.blocking2_widgets = {}, {}, {}, {}
        self.alignment_timers = {}
            # IBTU ByTones
        self.ibtu_tx_table_widgets, self.ibtu_rx_table_widgets = [], []
        self.tx_command_groups, self.rx_command_groups = {}, {}
            # IBTU FFT
        self.fft_rx_op_mode_combos = []
        self.fft_tx_app_mode_combos = []
        self.fft_rx_app_mode_combos = []
        
        
        # INICIALIZACIONES PARA EL PLANIFICADOR
        self.task_sequence = []
        self.selected_task_index = -1
        self.task_widgets = [] # Para guardar las filas de la lista visual
        self.args_frame = None
        self.task_session_selector = None
        
        self.task_oid_label = None
        self.task_oid_entry = None
        
        # ********* 3. CARGA DE DATOS EXTERNOS *********
        self.tests_data = robot_executor._discover_and_load_tests(self, TEST_DIRECTORY)
        
        # ********* 4. INICIALIZACIÓN DE CONTROLADORES *********
        self.scheduler_controller = SchedulerController(self)
        self.equipment_controller = EquipmentController(self)
        self.monitoring_controller = MonitoringController(self)
        self.alignment_controller = AlignmentController(self)
        self.snmp_controller = SNMPController(self)
        self.trap_listener_controller = TrapListenerController(self)
        self.alarms_controller = AlarmsController(self)
        # self.session_controller = SessionController(self)
        
        # ********* 5. CREACIÓN DE LA GUI *********
        ui_sidebar.create_sidebar(self)
        self._create_content_frames()
        
        # ******** 6. CONFIGURACIÓN FINAL Y BUCLE PRINCIPAL ********
        self._select_section(self.section_buttons["EQUIPMENT"], "EQUIPMENT")
        self.process_gui_queue()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
     

    def _create_gui_update_callback(self, session_id, message_type, attr_names):
        """ Fábrica que crea y devuelve una función de callback personalizada (session_id AÑADIDO para saber qué sesión origina los datos) """
        # Comprobamos si es un caso especial que requiere el listener completo
        if attr_names == ['listener']:
            def callback_special(listener):
                self.gui_queue.put((message_type, session_id, listener))    # En este caso, no envía una tupla ni tampoco ningun parametro, sino todos los objectos contenidos en el listener 
            return callback_special
    
        def callback(listener):
            params = []
            print(f"DEBUG CALLBACK (Sesión {session_id}): Intentando leer atributos: {attr_names}")
            for attr in attr_names:
                value = getattr(listener, attr, 'ATTRIBUTE_NOT_FOUND')
                print(f"DEBUG CALLBACK (Sesión {session_id}): Atributo '{attr}' = {value}")
                params.append(value)

            # Comprobar si se encontró algo que no sea el valor por defecto
            if 'ATTRIBUTE_NOT_FOUND' in params:
                print(f"ERROR CALLBACK (Sesión {session_id}): No se encontraron todos los atributos para {message_type}")
                # self.gui_queue.put(tuple([message_type] + params)) # Envía con error
                return # No envía nada si falta un atributo

            print(f"DEBUG CALLBACK (Sesión {session_id}): Poniendo en cola: {tuple([message_type, session_id] + params)}")            
            self.gui_queue.put(tuple([message_type, session_id] + params))
        return callback
    
           
    def process_gui_queue(self):
        """ Process messages from the thread-safe queue to update the GUI. """
        try:
            while not self.gui_queue.empty(): # Mientras haya mensajes en la cola
                message = self.gui_queue.get_nowait()
                
                print(f"DEBUG EN COLA: {message}") # DEBUG
                msg_type = message[0]
                
                # *** MENSAJES GLOBALES ***
                if msg_type == 'main_status':
                    self._update_status(message[1], message[2])
                    
                elif msg_type == 'session_status_A':   
                    self._update_session_status('A', message[1], message[2])    # Le pasamos como primer argumento "session_id" 'A' o 'B' correspondiente.
                    
                elif msg_type == 'session_status_B':
                    self._update_session_status('B', message[1], message[2])    # Le pasamos como primer argumento "session_id" 'A' o 'B' correspondiente.
                    
                elif msg_type == 'snmp_listener_status':
                    session_id = message[1]
                    status_text = message[2]
                    color = message[3]
                    ui_tab_monitoring._update_snmp_listener_status(self, session_id, status_text, color)
                    
                    
                elif msg_type == 'enable_buttons':
                    self.run_button_state(is_running=self.is_main_task_running)
                elif msg_type == 'debug_log':
                    self._update_debug_log(message[1])
                elif msg_type == 'scheduler_log':
                    ui_tab_scheduler._update_scheduler_log(self, message[1], message[2])       
                elif msg_type == 'show_burst_report_window':
                    # message[2] = header, message[3] = rows, message[4] = filename
                    ui_tab_monitoring.open_burst_report_window(self, message[2], message[3], message[4])      # Omitimos message[1] ya que no necesitamos el session_id en este caso
                elif msg_type == 'show_functional_report_window':
                    # message[2] = summary_text, message[3] = header, message[4] = rows, message[5] = filename
                    ui_tab_monitoring.open_functional_report_window(self, message[2], message[3], message[4], message[5])      # Omitimos message[1] ya que no necesitamos el session_id en este caso
                elif msg_type == 'show_breakpoint_window':
                    # args: _, header, rows, folder_name
                    ui_tab_monitoring.open_breakpoint_window(self, message[2], message[3], message[4])      # Omitimos message[1] ya que no necesitamos el session_id en este caso
                
                
                
                
                
                # *** MENSAJES DE DATOS (con session_id)*** Consideraremos a partir de aqui message[1] como session_id
                else:
                    try:    # Intentamos extraer session_id y lo validamos
                        session_id = message[1]
                        if session_id not in self.session_gui_data: # Comprobamos que la clave 'A' o 'B' exista dentro del diccionario "session_gui_data" que contiene todos los datos de cada sesion
                            print(f"ERROR: Mensaje '{msg_type}' recibido con session_id desconocido: {session_id}")
                            continue
                    except IndexError:
                        print(f"ERROR: Mensaje de datos '{msg_type}' recibido SIN session_id.")
                        continue
                    
                    is_active = (session_id == self.active_session_id)  # is_active = '1' si la sesion activa coincide con la que nos pasan por la cola.
                    
                    if msg_type == 'modules_display':
                        modules_list = message[2]   # Guardamos datos en la variable local para pasarsela a la función correspondiente
                        self.session_gui_data[session_id]['modules_list'] = modules_list     # Guardamos datos en la variable global dek diccionario de datos de la sesion
                        
                        # Comprobamos que estemos en la sesion activa antes de actualizar los datos
                        if is_active:
                            ui_tab_equipment._update_modules_display(self, modules_list)
                        
                        
                    elif msg_type == 'assigned_modules_display':
                        # Guardamos localmente
                        tp1_info = message[2]
                        tp2_info = message[3]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['tp1_info'] = tp1_info
                        self.session_gui_data[session_id]['tp2_info'] = tp2_info
                        if is_active:
                            ui_tab_equipment._update_assigned_modules_display(self, tp1_info, tp2_info)
        
                    elif msg_type == 'command_assignment_grids':
                        # Guardamos localmente
                        command_ranges = message[2]
                        num_inputs = message[3]
                        num_outputs = message[4]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['command_ranges'] = command_ranges
                        self.session_gui_data[session_id]['num_inputs'] = num_inputs
                        self.session_gui_data[session_id]['num_outputs'] = num_outputs

                        if is_active:
                            ui_tab_equipment._update_command_assignment_grids(self, command_ranges, num_inputs, num_outputs)
                        
                    elif msg_type == 'full_snmp_config_display':
                        # Guardamos localmente
                        listener_data = message[2]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['snmp_config_listener_data'] = listener_data
                        
                        if is_active:
                            ui_tab_monitoring._update_full_snmp_config_display(self, listener_data)
                            
                    elif msg_type == 'update_input_activation_display':
                        # FGuardamos localmente
                        input_state = message[2]
                        input_info = message[3]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['input_activation_state'] = input_state
                        self.session_gui_data[session_id]['input_info'] = input_info

                        if is_active:
                            ui_tab_alignment._update_input_activation_display(self, input_state, input_info)
                            
                    elif msg_type == 'program_inputs_success':
                        ui_tab_alignment._handle_program_inputs_success(self, message[2], message[3], message[4])
                        
                    elif msg_type == 'update_chrono_log_display':
                        # Guardamos locaalmente
                        log_entries = message[2]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['chronological_log_entries'] = log_entries

                        if is_active:
                            ui_tab_monitoring._update_chrono_log_display(self, log_entries) 

                    elif msg_type == 'update_alignment_states':
                        # Guardamos localmente
                        listener_data = message[2]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['alignment_states_listener_data'] = listener_data

                        if is_active:
                            ui_tab_alignment._update_alignment_states(self, listener_data)
                        
                        
                        
                    elif msg_type == 'program_alignment_success':
                        # Aqui no hay datos para guardar. Lo procesamos solo si la sesion activa coincide con la que nos pasan.
                        if is_active:
                            self.alignment_controller._handle_program_alignment_success(*message[2:])
                            
                    elif msg_type == 'update_ibtu_full_config':
                        # Guardamos localmente
                        listener_data = message[2]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['ibtu_config_listener_data'] = listener_data

                        if is_active:
                            ui_tab_equipment._update_ibtu_full_config_display(self, listener_data)

                    elif msg_type == 'update_alarms_display':
                        # Guardamos localmente
                        alarms_data = message[2]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['alarms_data'] = alarms_data

                        if is_active:
                            ui_tab_alarms.update_alarms_display(self, alarms_data)
                            
                    elif msg_type == 'update_correlation_display':
                        # message[1] = chrono_text_report
                        # message[2] = trap_text_report
                        # message[3] = result
                        # message[4] = color
                        # Este es un evento. Lo procesamos si la sesion activa es la que nos pasan por la cola.
                        if is_active:
                            # ui_tab_monitoring._update_correlation_display(self, message[2], message[3], message[4], message[5])
                            # Los datos están en message[2] en adelante...
                            ui_tab_monitoring._update_correlation_display(self, *message[2:])

                    elif msg_type == 'update_verification_report_display':
                    # message[2] = formatted_text
                    # message[3] = filepath
                        ui_tab_monitoring._update_verification_report_display(self, message[2], message[3])        
                            


                    elif msg_type == 'update_ibtu_fft_config':
                        # Guardamos localmente
                        fft_config_data = message[2]
                        # Guardamos globalmente
                        self.session_gui_data[session_id]['ibtu_fft_config_data'] = fft_config_data
                        if is_active:
                            # message[1] contendrá el diccionario fft_config_data
                            ui_tab_equipment._update_ibtu_fft_config_display(self, fft_config_data)

                    else:
                        print(f"ADVERTENCIA: Mensaje de cola no reconocido o mal formateado: {msg_type}")
        except queue.Empty:
            pass    # Si no hay mensajes no hacemos nada
        finally:
            self.after(100, self.process_gui_queue) # Comprobamos nuevos mensajes en la cola cada 100ms
            
            
    def _create_content_frames(self):
        """Creates the content frames for each main section."""
        self.content_frames = {}
        self.content_frames["FILES"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        ctk.CTkLabel(self.content_frames["FILES"], text="FILES Content", font=ctk.CTkFont(size=18)).pack(pady=20, padx=20)
        
        self.content_frames["UPDATING"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        ctk.CTkLabel(self.content_frames["UPDATING"], text="UPDATING Content", font=ctk.CTkFont(size=18)).pack(pady=20, padx=20)

        self.content_frames["SCHEDULER"] = ui_tab_scheduler.create_scheduler_tab(self)

        self.content_frames["EQUIPMENT"] = ui_tab_equipment.create_equipment_tab(self)

        self.content_frames["MONITORING"] = ui_tab_monitoring.create_monitoring_tab(self)

        self.content_frames["ALIGNMENT"] = ui_tab_alignment.create_alignment_tab(self)
        
        self.content_frames["ALARMS"] = ui_tab_alarms.create_alarms_tab(self)

    def _create_tab_view(self, parent, tabs):
        """Helper function to create a CTkTabview."""
        tab_view = ctk.CTkTabview(parent, corner_radius=8)
        for tab_name in tabs:
            tab_view.add(tab_name)
        return tab_view
    
    def on_closing(self):
        """Handles the window closing event to ensure cleanup for all active sessions."""
        for session_id, session_info in self.sessions.items():
            if session_info['process']:
                print(f"INFO: Attempting to close session {session_id}...")
                try:
                    robot_executor._execute_stop_browser(self)
                except Exception as e:
                    print(f"ERROR: Could not initiate cleanup for session {session_id}: {e}")
            
            else:
                print(f"INFO: Session {session_id} was not active, skipping cleanup.")
            
        self.destroy()      

           
    def set_active_context(self, value):
        """Llamado por el CTkSegmentedButton para cambiar el equipo activo."""
        session_map = {"Equipo A": "A", "Equipo B": "B"}
        new_session_id = session_map.get(value, 'A')
        
        if new_session_id == self.active_session_id:
            return  # Si estamos en la misma sesion que nos pasan para cambiar -> NO HACEMOS NADA!
        
        self.active_session_id = new_session_id
        print(f"Sesion activa cambiada a: {self.active_session_id}")
        
        self._update_gui_from_active_session()  # Funcion para refrescar todos los widgets de la GUI con los nuevos datos.
        
        self.run_button_state(is_running=self.is_main_task_running)           
         
    def _update_debug_log(self, text):
        """Appends text to the debug log display."""
        self.debug_log_display.configure(state="normal")
        self.debug_log_display.insert("end", text + "\n")
        self.debug_log_display.configure(state="disabled")
        self.debug_log_display.see("end")


    def _create_tab_view(self, parent, tabs):
        """Helper function to create a CTkTabview."""
        tab_view = ctk.CTkTabview(parent, corner_radius=8)
        for tab_name in tabs:
            tab_view.add(tab_name)
        return tab_view


  


    def _create_info_row(self, parent, label_text):
        """Helper to create a label-value row for displaying info."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10)
        ctk.CTkLabel(frame, text=label_text, width=80, anchor="w").pack(side="left")
        value_label = ctk.CTkLabel(frame, text="-", anchor="w", font=ctk.CTkFont(weight="bold"))
        value_label.pack(side="left")
        return value_label
    
    def _create_info_entry_row(self, parent, label_text):
        """Helper to create a label-entry row for input."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame, text=label_text, width=80, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(frame, width=60)
        entry.pack(side="left")
        return entry

    def _create_command_header_row(self, parent, tp_text):
        """Helper to create a header row for the command assignment grids."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=2)
        label = ctk.CTkLabel(frame, text=f"{tp_text}: ...", anchor="w")
        label.pack(fill="x")
        return label
    
    
    def _select_section(self, selected_button, section_name):
        """Manages the view change in the content panel."""
        for button in self.section_buttons.values():
            button.configure(fg_color=("gray75", "gray25") if button != selected_button else button.cget("hover_color"))
        
        for frame in self.content_frames.values():
            frame.grid_forget()

        current_frame = self.content_frames[section_name]
        current_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def run_button_state(self, is_running):
        # Con la siguiente linea podemos configurar estado botones de la sesion activa guardada en active_session_id.
        print(f"DEBUG: Checking context {self.active_session_id}")
        active_session_info = self.sessions[self.active_session_id] # Nos quedamos con los valores de la clave ({A o B} = active_session_id) del diccionario
        session_active = active_session_info['process'] is not None     # Nos quedamos con el estado de la sesion activa.
        print(f"DEBUG: Is session {self.active_session_id} active? {session_active}")
        
            # *** LÓGICA DE ESTADOS ***
        # Estado para botones que deben estar ACTIVOS cuando NO se está ejecutando nada (idle).
        idle_state = "normal" if session_active and not is_running else "disabled"
        print(f"DEBUG: Calculated idle_state: {idle_state}")
        # Estado para botones que deben estar ACTIVOS SÓLO MIENTRAS se está ejecutando algo (running).
        running_state = "normal" if session_active and is_running else "disabled"
        
        if is_running:
            self.gui_queue.put(('main_status', "Status: Running...", "orange"))


        # *** CONFIGURACION DE BOTONES DE SESIÓN (A y B por separado) - Habilitacion/Deshabilitacion ***
        # A:
        if hasattr(self, 'connect_button_A'):  # Solo si el widget ya ha sido credo...
            session_A_active = self.sessions['A']['process'] is not None
            # Si la sesion está activa ->
                # -> Boton de conectar deshabilitado. Si no lo está, habilitado.
            self.connect_button_A.configure(state="disabled" if session_A_active else "normal")
                # -> Boton de desconectar habilitado. Si no lo está, deshabilitado.
            self.disconnect_button_A.configure(state="normal" if session_A_active else "disabled")

        # B:
        if hasattr(self, 'connect_button_B'):  # Solo si el widget ya ha sido credo...
            session_B_active = self.sessions['B']['process'] is not None
            # Si la sesion está activa ->
                # -> Boton de conectar deshabilitado. Si no lo está, habilitado.
            self.connect_button_B.configure(state="disabled" if session_B_active else "normal")
                # -> Boton de desconectar habilitado. Si no lo está, deshabilitado.
            self.disconnect_button_B.configure(state="normal" if session_B_active else "disabled")


        # Botones de ejecución de tests
        # Por defecto, todos los botones de acción principal utilizaran el tipo de estado idle (accionables si hay sesión y no hay nada corriendo)
        self.list_modules_button.configure(state=idle_state)
        self.assign_modules_button.configure(state=idle_state)
        self.view_assigned_button.configure(state=idle_state)
        self.program_commands_button.configure(state=idle_state)
        self.program_timezone_button.configure(state=idle_state)
        if hasattr(self, 'refresh_assignments_button'): self.refresh_assignments_button.configure(state=idle_state)
        if hasattr(self, 'program_assignments_button'): self.program_assignments_button.configure(state=idle_state)
        if hasattr(self, 'retrieve_inputs_button'): self.retrieve_inputs_button.configure(state=idle_state)
        if hasattr(self, 'program_inputs_button'): self.program_inputs_button.configure(state=idle_state)
        if hasattr(self, 'hil_pulse_button'): self.hil_pulse_button.configure(state=idle_state)
        if hasattr(self, 'capture_last_entries_button'): self.capture_last_entries_button.configure(state=idle_state)
        if hasattr(self, 'clear_chrono_button'): self.clear_chrono_button.configure(state=idle_state)
        if hasattr(self, 'query_snmp_config_button'): self.query_snmp_config_button.configure(state=idle_state)
        if hasattr(self, 'program_snmp_config_button'): self.program_snmp_config_button.configure(state=idle_state)
        if hasattr(self, 'refresh_alignment_button'): self.refresh_alignment_button.configure(state=idle_state)
        if hasattr(self, 'query_ibtu_fft_button'): self.query_ibtu_fft_button.configure(state=idle_state)

    # Scheduler Buttons
        scheduler_idle_state= "normal" if not is_running else "disabled"
        scheduler_running_state = "normal" if is_running else "disabled"   #??
    
        if hasattr(self, 'run_sequence_button'):
            self.run_sequence_button.configure(state=scheduler_idle_state) # El botón de ejecutar usa 'scheduler_idle_state'. Solo podremos darle al boton cuando no haya nada corriendo.
        if hasattr(self, 'stop_sequence_button'):
            self.stop_sequence_button.configure(state=scheduler_running_state) # El botón de detener usa 'scheduler_running_state'. Solo podemos darle al boton cuando haya algo corriendo (por ejemplo los tests del mismo planificador).
        
    # *** SNMP LISTENER *** _ With dual Session Listener
        # BOTONES DE INICIAR Y PARAR LISTENER
        for session_id in ['A', 'B']:   # Asignamos 'A' a session_id en la 1a iteración y 'B' en la 2a iteración
            listener_info = self.trap_listeners.get(session_id)
            if listener_info:
                is_listener_running = listener_info['is_running']
                
                # No se puede iniciar si ya está corriendo O si una tarea principal está corriendo
                start_state = "disabled" if is_listener_running or is_running else "normal"
                # Solo se puede parar si está corriendo Y no hay una tarea principal corriendo
                stop_state = "normal" if is_listener_running and not is_running else "disabled"
                 
                if listener_info['start_button']:   # Comprobamos que el boton de start exista
                    listener_info['start_button'].configure(state=start_state)
                if listener_info['stop_button']:    # Comprobamos que el boton de stop exista
                    listener_info['stop_button'].configure(state=stop_state)
                    
        # BOTONES DEL VISUALIZADOR DE TRAPS
        viewer_state = "normal"    # Los botones de Refrescar, Filtrar traps etc estaran disponibles siempre!
        for s_id in ['A', 'B']:
            listener_info = self.trap_listeners[s_id]
            
            if listener_info['show_all_button']:        # Comprobamos que el boton de mostrar todos los traps exista.
                listener_info['show_all_button'].configure(state=viewer_state)
            if listener_info['filter_button']:          # Comprobamos que el boton de fitrar traps exista.
                listener_info['filter_button'].configure(state=viewer_state)
            if listener_info['reset_button']:       # Comprobamos que el boton de reset todos los traps exista.
                listener_info['reset_button'].configure(state=viewer_state)  
            
    # Para los botones de log, solo necesitan que no haya algo corriendo. No es necesario sesion activa
        for btn in self.log_buttons:   
            btn.configure(state="normal" if not is_running else "disabled")

    # Widgets Logic for Alignment Tab (Activate Inputs...)
        if is_running: # Para evitar que intentemos hacer cambios mientras algo está corriendo, bloqueamos todo. Independientemente que tengamos o no una sesion activa. Es decir, los botones de activar/desactivar loops/bloqueos no se actualizaran. 
            for widgets in [self.loop1_widgets, self.loop2_widgets, self.blocking1_widgets, self.blocking2_widgets]:
                if widgets:
                    widgets['activate_button'].configure(state="disabled")
                    widgets['deactivate_button'].configure(state="disabled")
                    widgets['duration_combo'].configure(state="disabled")
                    if 'type_combo' in widgets:
                        widgets['type_combo'].configure(state="disabled")
        elif session_active:
            for widgets_dict, is_loop_flag in [(self.loop1_widgets, True), (self.loop2_widgets, True), 
                                                (self.blocking1_widgets, False), (self.blocking2_widgets, False)]:  # En cada iteracion le vamos pasando el conjunto de widgets junto al valor que queremos que tenga is_loop_flag
                if widgets_dict:    # Si el conjunto de widgets existen, los actualizamos con _update_alignment_row_ui
                    is_active = "Activo" in widgets_dict['status_label'].cget("text")   # Comprobamos que la clave status_label del conjunto de widgets que estamos iterando sea "Activo". Si no lo es, la variable is_active será false.->
                                                                                        # -> En definitiva, comprobamos el estado del conjunto de widgets, si están o no activos 
                    ui_tab_alignment._update_alignment_row_ui(widgets_dict, is_active, is_loop_flag)    # _update_alignment_row_ui se encargara de actualizar los botones (habilitará o deshabilitará) ->
                                                                                                        # -> en funcion del estado de los loops o bloqueos (si encuentra el texto "Activo" deberá deshabilitar activate_button)
        else:
            for widgets in [self.loop1_widgets, self.loop2_widgets, self.blocking1_widgets, self.blocking2_widgets]:
                if widgets:
                    widgets['activate_button'].configure(state="disabled")
                    widgets['deactivate_button'].configure(state="disabled")
                    widgets['duration_combo'].configure(state="disabled")
                    if 'type_combo' in widgets:
                        widgets['type_combo'].configure(state="disabled")


# ************************************************************************************
    def update_trap_history_display(self, trap_rows, filepath):
        """Recibe los datos de la BD y actualiza la caja de texto."""
        
        # Actualizamos la etiqueta con el nombre del archivo cargado
        self.db_viewer_file_label.configure(text=f"Mostrando: {os.path.basename(filepath)}")

        self.db_display_textbox.configure(state="normal")
        self.db_display_textbox.delete("1.0", "end")

        if not trap_rows:
            self.db_display_textbox.insert("1.0", "El archivo de la base de datos está vacío.")
        else:
            for row in trap_rows:
                timestamp, event, source, varbinds_str = row
                log_entry = f"[{timestamp}] - {event} desde {source}\n"

                # Formatear los varbinds para que sean legibles
                try:
                    varbinds = json.loads(varbinds_str)
                    for key, value in varbinds.items():
                        # Extraer solo el nombre del OID para que sea más corto
                        simple_key = key.split('::')[-1]
                        log_entry += f"  - {simple_key}: {value}\n"
                except json.JSONDecodeError:
                    log_entry += f"  - Varbinds (raw): {varbinds_str}\n"
                log_entry += "---\n"
                self.db_display_textbox.insert("end", log_entry)

        self.db_display_textbox.configure(state="disabled")
        self._update_status(f"Historial de '{os.path.basename(filepath)}' cargado.", "white")
        

# ****** VARIOS MÉTODOS AUXILIARES ********
    def _update_gui_from_active_session(self):
        """
        Refresca toda la GUI para que coincida con los datos almacenados
        para la sesión (self.active_session_id) que acaba de ser seleccionada.
        """
        session_id = self.active_session_id
        try:
            data = self.session_gui_data[session_id]
        except KeyError:
            print(f"Error: No se encontraron datos de GUI para la sesión {session_id}")
            # Si no conseguimos recuperar los datos de la sesion, asignaremos a data una estructura de datos LIMPIA! Por lo que se refrescará borrando todos los datos que habian antes.
            data = self._create_default_gui_data_state()

        print(f"Refrescando la GUI con los datos de la Sesión {session_id}...")

        # *** Equipment Tab: Basic Config ***
        # Estas funciones pueden actualizar con listas vacias? En caso de que entremos en el except anterior.
        ui_tab_equipment._update_modules_display(self, data['modules_list'])
        ui_tab_equipment._update_assigned_modules_display(self, data['tp1_info'], data['tp2_info'])
        
        # *** Equipment Tab: Command Assign ***
        # La función puede manejar 'None' o 0?
        ui_tab_equipment._update_command_assignment_grids(self, data['command_ranges'], data['num_inputs'], data['num_outputs'])
        
        # *** Equipment Tab: Module Config (IBTU ByTones) ***
        # La función _update_ibtu_full_config_display puede manejar 'None'?
        ui_tab_equipment._update_ibtu_full_config_display(self, data['ibtu_config_listener_data'])

        # *** Equipment Tab: Module Config (IBTU FFT) *** 
  
        fft_data = data['ibtu_fft_config_data'] if data['ibtu_fft_config_data'] is not None else {}      # Pasamos un dict vacío si no hay datos para evitar errores .get()
        ui_tab_equipment._update_ibtu_fft_config_display(self, fft_data)

        # *** Monitoring Tab: Chrono Log *** 
        # La función puede manejar 'None'?
        ui_tab_monitoring._update_chrono_log_display(self, data['chronological_log_entries'])
        
        snmp_listener_data = data['snmp_config_listener_data']
        
        print(f"DEBUG SNMP REFRESH: El valor en data['snmp_config_listener_data'] es: {repr(snmp_listener_data)}")


        # ***  Monitoring Tab: SNMP *** 
        # La función _update_full_snmp_config_display puede manejar 'None'?
        ui_tab_monitoring._update_full_snmp_config_display(self, snmp_listener_data)
        
        # ***  Alignment Tab *** 
        # Las funciones pueden manejar 'None'?
        ui_tab_alignment._update_input_activation_display(self, data['input_activation_state'], data['input_info'])
        ui_tab_alignment._update_alignment_states(self, data['alignment_states_listener_data'])
        
        # ***  Alarms Tab *** 
        # La función puede manejar 'None'¿
        ui_tab_alarms.update_alarms_display(self, data['alarms_data'])
        
        print(f"Refresco de GUI para Sesión {session_id} completado.")
        
        
    def copy_to_clipboard(self, text):
        """Copies the given text to the clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self._update_status(f"'{text}' copiado al portapapeles.", "white")
        
    def _populate_debug_log_tab(self, tab_frame):
        """Populates the Debug Log tab."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        
        self.debug_log_display = ctk.CTkTextbox(tab_frame, state="disabled", wrap="none")
        self.debug_log_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
    def _update_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)
        
    def _update_session_status(self, session_id, message, color):
        """Actualiza la etiqueta de estado para la Sesión A o B."""
        if session_id == 'A':
            #  widgets session_status_label_A/B creados en ui_sidebar.py
            if hasattr(self, 'session_status_label_A'): # hasattr asegura que solo se intente hacer el .configure widgets que ya han sido creados
                self.session_status_label_A.configure(text=f"Estado: {message}", text_color=color)
            self.sessions['A']['status'] = message
            
        elif session_id == 'B':
            if hasattr(self, 'session_status_label_B'):
                self.session_status_label_B.configure(text=f"Estado: {message}", text_color=color)
            self.sessions['B']['status'] = message


    def _build_grid(self, parent_frame, row_prefix, num_rows, num_cols, checkbox_list):
        """Helper function to build a single checkbox grid."""
        io_header = ctk.CTkLabel(parent_frame, text="E/S", font=ctk.CTkFont(weight="bold", size=10))
        io_header.grid(row=0, column=0, padx=5, pady=2)

        for i in range(1, num_cols + 1):
            parent_frame.grid_columnconfigure(i, weight=0)
            header = ctk.CTkLabel(parent_frame, text=str(i), font=ctk.CTkFont(weight="bold", size=10))
            header.grid(row=0, column=i, padx=2, pady=2)
        
        for r in range(num_rows):
            row_list = []
            label_text = f"{row_prefix} {r+1}-"
            label = ctk.CTkLabel(parent_frame, text=label_text, font=ctk.CTkFont(size=11))
            label.grid(row=r+1, column=0, padx=(5, 10), pady=1, sticky="e")
            
            for c in range(num_cols):
                checkbox = ctk.CTkCheckBox(parent_frame, text="", width=16) 
                checkbox.grid(row=r+1, column=c+1, padx=2, pady=1)
                row_list.append(checkbox)
            checkbox_list.append(row_list)
            
    def _get_test_case_arguments(self, test_name):
        """
        Consulta el diccionario de mapeo para obtener los argumentos de un test.
        """
        # Si no encuentra el test_name, devuelve una lista vacía por defecto [].
        return self.test_variable_map.get(test_name, [])

    def _open_log_file(self):
        """Opens the generated log.html file in the browser."""
        log_path = os.path.abspath(os.path.join("test_results", "log.html"))
        if os.path.exists(log_path):
            try:
                if os.name == 'nt': os.startfile(log_path)
                elif sys.platform == 'darwin': subprocess.Popen(['open', log_path])
                else: subprocess.Popen(['xdg-open', log_path])
            except Exception as e:
                self.gui_queue.put(('main_status', f"Error opening log: {e}", "red"))
        else:
            self.gui_queue.put(('main_status', "Status: log.html file not found", "red"))

    def _get_local_ip(self):
        """Tries to determine the local IP address of the machine."""
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            if s:
                s.close()
        return IP

    def _set_local_ip(self):
        """Gets the local IP and sets it in the SNMP listener IP entry."""
        local_ip = self._get_local_ip()
        self.snmp_ip_entry.delete(0, "end")
        self.snmp_ip_entry.insert(0, local_ip)


    def _create_default_gui_data_state(self):
        """Crea un diccionario con el estado inicial a inicializar vacío para los datos de la GUI."""
        return {
            # Datos de Equipment -> Basic Config
            "modules_list": [],
            "tp1_info": (None, ["", ""]), # (Nombre_Modulo, [TX, RX])
            "tp2_info": (None, ["", ""]),

            # Datos de Equipment -> Command Assign
            "command_ranges": None,
            "num_inputs": 0,
            "num_outputs": 0,
            "tx_checkbox_states": None,
            "rx_checkbox_states": None,
            "tx_logic_states": None,
            "rx_logic_states": None,

            # Datos de Equipment -> IBTU ByTones
            "ibtu_config_listener_data": None, # Guardará el objeto listener completo

            # Datos de Equipment -> IBTU FFT
            "ibtu_fft_config_data": None, # Guardará el diccionario de config

            # Datos de Monitoring -> Chrono Log
            "chronological_log_entries": None, # Guardará las entradas

            # Datos de Monitoring -> SNMP
            "snmp_config_listener_data": None, # Guardará el objeto listener completo

            # Datos de Alignment
            "input_activation_state": None,
            "input_info": None,
            "alignment_states_listener_data": None, # Guardará el listener completo

            # Datos de Alarms
            "alarms_data": None
        }



    # Llamadas procedentes de controller, dirigidas a archivos de la carpeta gui
    def start_alignment_countdown(self, duration, key):
        ui_tab_alignment._alignment_countdown(self, duration, key)
        
    def update_task_sequence_display(self):
        ui_tab_scheduler._update_task_sequence_display(self)
        
    def update_trap_display(self, traps_data, session_id):
        """Actualiza el visor de traps para una sesión específica."""
        listener_info = self.trap_listeners.get(session_id)
        
        if listener_info and listener_info['trap_display_widget']:
            ui_tab_monitoring.update_trap_display(listener_info['trap_display_widget'], traps_data)
        else:
            print(f"ERROR: No trap display widget found for session {session_id}")
            
    def _select_task_in_sequence(self, index_to_select):
        """
        Pide a la GUI del planificador que resalte una tarea específica por su índice.
        Esta función actúa como un "puente" al controlador.
        """
        # Delegamos la llamada a la función real, que está en ui_tab_scheduler.py
        try:
            ui_tab_scheduler._select_task_in_sequence(self, index_to_select)
        except Exception as e:
            print(f"ERROR: No se pudo seleccionar la tarea en la GUI: {e}")
            
            