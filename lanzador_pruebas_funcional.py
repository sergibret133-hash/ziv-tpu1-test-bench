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
import ast
import json
import socket
import queue
import time # Importado para pequeñas pausas
from pathlib import Path
from robot.api import TestSuiteBuilder
from PIL import Image
from Trap_Receiver_GUI_oriented import Trap_Receiver_GUI_oriented



import sqlite3
from datetime import datetime, timezone
from robot.rebot import rebot_cli

# --- CONFIGURATION ---
TEST_DIRECTORY = "tests"
# --- END CONFIGURATION ---

class ModernTestRunnerApp(ctk.CTk):

    # Listener class to capture test results directly from Robot Framework
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


    def __init__(self):
        super().__init__()

        self.title("Teleprotection Test Interface")
        self.geometry("1100x850") 

        self.browser_process = None

        self.trap_receiver = Trap_Receiver_GUI_oriented()
        self.snmp_listener_thread = None

        # ---Scheduler Test variables---
        self.test_variable_map = {
            "Input Activation": [
                "${ACTIVATE_DEACTIVATE}", 
                "${DURATION}", 
                "${INPUTS_LIST}"
            ],
            "Retrieve Inputs Activation State": [], # Este test no necesita variables
            # --- Añade aquí otros tests y sus variables cuando los crees ---
        }

            # DICCIONARIO DE MAPEO DE ACTUALIZACIÓN DE GUI
    # Asocia un nombre de test con el mensaje de la cola y los atributos del listener necesarios.
        self.test_gui_update_map = {
            "Retrieve Inputs Activation State": ('update_input_activation_display', ['input_activation_state', 'input_info']),
            # EJEMPLOS PARA FUTURO:
            # "Current Loop and Blocking State": ('update_alignment_states', ['listener']),
            # "Retrieve Full SNMP Configuration": ('full_snmp_config_display', ['listener']),
        }
        
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

        self.tx_checkboxes, self.rx_checkboxes, self.tx_logic_checkboxes, self.rx_logic_checkboxes = [], [], [], []
        self.host_widgets, self.input_activation_checkboxes, self.log_buttons = [], [], []
        self.inputs_are_active, self.activation_timer = None, None
        self.loop1_widgets, self.loop2_widgets, self.blocking1_widgets, self.blocking2_widgets = {}, {}, {}, {}
        self.alignment_timers = {}
        self.ibtu_tx_table_widgets, self.ibtu_rx_table_widgets = [], []
        self.tx_command_groups, self.rx_command_groups = {}, {}
        
        self.gui_queue = queue.Queue()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tests_data = self._discover_and_load_tests(TEST_DIRECTORY)

        self._create_sidebar()
        self._create_content_frames()
        
        self.process_gui_queue()

        self._select_section(self.section_buttons["EQUIPMENT"], "EQUIPMENT")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
        # --- INICIALIZACIONES PARA EL PLANIFICADOR (NUEVO) ---
        self.task_sequence = []
        self.selected_task_index = -1
        self.task_widgets = [] # Para guardar las filas de la lista visual
        
        self.db_path = 'snmp_traps.db' # Guardamos la ruta como una variable de instancia. Lo hacemos ya que sino tendríamos problema con SQL ya que no permite compartir y conectarse a la base de datos desde hilos secundarios
        self.initialize_database()
        

    def initialize_database(self):
        """Crea la conexión a la BD y la tabla si no existen."""
        conn = sqlite3.connect(self.db_path) # Crea una conexión local
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_received TEXT NOT NULL,
                source_address TEXT NOT NULL,
                event_type TEXT NOT NULL,
                varbinds_json TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente.") 


    def save_traps_to_db(self, traps_list):
        """Guarda una lista de traps en la base de datos, gestionando su propia conexión."""
        if not traps_list:
            return
        try:
            conn = sqlite3.connect(self.db_path)    # Crea una conexión local nueva para este hilo. De esta forma evitamos problemas de concurrencia
            cursor = conn.cursor()
            for trap in traps_list:
                varbinds_str = json.dumps(trap.get('varbinds_dict', {}))
                cursor.execute(
                    "INSERT INTO traps (timestamp_received, source_address, event_type, varbinds_json) VALUES (?, ?, ?, ?)",
                    (trap['timestamp_received_utc'], trap['source_address'], trap['event_type'], varbinds_str)
                )
            conn.commit()
            conn.close() # Cierra la conexión al terminar
            self.gui_queue.put(('main_status', f"Guardados {len(traps_list)} traps nuevos en la BD.", "cyan"))
        except Exception as e:
            self.gui_queue.put(('main_status', f"Error al guardar traps en la BD: {e}", "red"))
            

    def _create_sidebar(self):
        """Creates the side navigation panel with the main buttons."""
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="TPU Automation", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        session_frame = ctk.CTkFrame(self.sidebar_frame)
        session_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        session_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(session_frame, text="SESIÓN", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5,0))
        self.connect_button = ctk.CTkButton(session_frame, text="Conectar", command=self._start_browser_process_thread)
        self.connect_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.disconnect_button = ctk.CTkButton(session_frame, text="Desconectar", command=self._stop_browser_process_thread, state="disabled")
        self.disconnect_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.session_status_label = ctk.CTkLabel(session_frame, text="Estado: Desconectado", text_color="orange")
        self.session_status_label.grid(row=2, column=0, columnspan=2, pady=(0,5))

        self.section_buttons = {}
        sections = ["FILES", "UPDATING", "EQUIPMENT", "MONITORING", "ALIGNMENT", "SCHEDULER"]

        for i, section_name in enumerate(sections):
            button = ctk.CTkButton(self.sidebar_frame, text=section_name)
            button.configure(command=lambda b=button, n=section_name: self._select_section(b, n))
            button.grid(row=i+2, column=0, padx=20, pady=10, sticky="ew")
            self.section_buttons[section_name] = button

        try:
            logo_image_data = Image.open("logo.png")
            logo_image = ctk.CTkImage(dark_image=logo_image_data, light_image=logo_image_data, size=(140, 140))
            logo_label = ctk.CTkLabel(self.sidebar_frame, image=logo_image, text="")
            logo_label.grid(row=11, column=0, padx=20, pady=10)
        except FileNotFoundError:
            print("Logo file ('logo.png') not found. Skipping logo display.")

        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="v1.4 - Desarrollo", anchor="w")
        self.version_label.grid(row=12, column=0, padx=20, pady=(10, 20))


    def _create_content_frames(self):
        """Creates the content frames for each main section."""
        self.content_frames = {}
        self.content_frames["FILES"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        ctk.CTkLabel(self.content_frames["FILES"], text="FILES Content", font=ctk.CTkFont(size=18)).pack(pady=20, padx=20)
        
        self.content_frames["UPDATING"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        ctk.CTkLabel(self.content_frames["UPDATING"], text="UPDATING Content", font=ctk.CTkFont(size=18)).pack(pady=20, padx=20)

        self.content_frames["SCHEDULER"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._populate_scheduler_tab(self.content_frames["SCHEDULER"])


        self.content_frames["EQUIPMENT"] = self._create_tab_view(parent=self, tabs=["Basic Configuration", "Command Assignment", "Module Configuration"])
        self._populate_basic_config_tab(self.content_frames["EQUIPMENT"].tab("Basic Configuration"))
        self._populate_command_assignment_tab(self.content_frames["EQUIPMENT"].tab("Command Assignment"))
        self._populate_module_config_tab(self.content_frames["EQUIPMENT"].tab("Module Configuration"))

        self.content_frames["MONITORING"] = self._create_tab_view(parent=self, tabs=["SNMP", "Chronological Register", "Historial de Traps (BD)"])
        self._populate_snmp_tab(self.content_frames["MONITORING"].tab("SNMP"))
        self._populate_chrono_register_tab(self.content_frames["MONITORING"].tab("Chronological Register"))
        self._populate_db_viewer_tab(self.content_frames["MONITORING"].tab("Historial de Traps (BD)"))

        self.content_frames["ALIGNMENT"] = self._create_tab_view(parent=self, tabs=["Loops Blocking", "Input Activation"])
        self._populate_loops_blocking_tab(self.content_frames["ALIGNMENT"].tab("Loops Blocking"))
        self._populate_input_activation_tab(self.content_frames["ALIGNMENT"].tab("Input Activation"))
        



    def _create_tab_view(self, parent, tabs):
        """Helper function to create a CTkTabview."""
        tab_view = ctk.CTkTabview(parent, corner_radius=8)
        for tab_name in tabs:
            tab_view.add(tab_name)
        return tab_view

    def _populate_basic_config_tab(self, tab_frame):
        """Populates the 'Basic Configuration' tab with its widgets."""
        tab_frame.grid_columnconfigure(0, weight=1)

        ip_frame = ctk.CTkFrame(tab_frame)
        ip_frame.grid(row=0, column=0, pady=(10, 5), padx=20, sticky="ew")
        ctk.CTkLabel(ip_frame, text="Terminal IP Address:").pack(side="left", padx=(10,5), pady=10)
        self.entry_ip = ctk.CTkEntry(ip_frame, placeholder_text="Ex: 10.212.40.87")
        self.entry_ip.pack(side="left", padx=(0,10), pady=10, expand=True, fill="x")
        self.entry_ip.insert(0, "10.212.40.87")

        main_scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Funcionalidades de Configuración Básica")
        main_scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_scroll_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)

        list_modules_frame = ctk.CTkFrame(main_scroll_frame)
        list_modules_frame.grid(row=0, column=0, pady=10, sticky="ew")
        ctk.CTkLabel(list_modules_frame, text="1. Listar Módulos en el Equipo", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.list_modules_button = ctk.CTkButton(list_modules_frame, text="Listar Módulos Instalados", command=self._run_list_modules_thread)
        self.list_modules_button.pack(pady=10)
        self.modules_result_frame = ctk.CTkScrollableFrame(list_modules_frame, label_text="Módulos Detectados", height=150)
        self.modules_result_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self._update_modules_display([])

        assign_modules_frame = ctk.CTkFrame(main_scroll_frame)
        assign_modules_frame.grid(row=1, column=0, pady=10, sticky="ew")
        ctk.CTkLabel(assign_modules_frame, text="2. Asignar Módulos Priorizados", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        tp1_frame = ctk.CTkFrame(assign_modules_frame, fg_color="transparent")
        tp1_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(tp1_frame, text="Módulo Prioridad 1 (TP1):", width=180).pack(side="left")
        self.entry_tp1 = ctk.CTkEntry(tp1_frame, placeholder_text="Nombre del módulo, ej: IDTU (1)")
        self.entry_tp1.pack(side="left", expand=True, fill="x")

        tp2_frame = ctk.CTkFrame(assign_modules_frame, fg_color="transparent")
        tp2_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(tp2_frame, text="Módulo Prioridad 2 (TP2):", width=180).pack(side="left")
        self.entry_tp2 = ctk.CTkEntry(tp2_frame, placeholder_text="Nombre del módulo, ej: IPTU (1)")
        self.entry_tp2.pack(side="left", expand=True, fill="x")
        
        self.assign_modules_button = ctk.CTkButton(assign_modules_frame, text="Asignar Módulos Priorizados", command=self._run_assign_modules_thread)
        self.assign_modules_button.pack(pady=15)

        view_assigned_frame = ctk.CTkFrame(main_scroll_frame)
        view_assigned_frame.grid(row=2, column=0, pady=10, sticky="ew")
        ctk.CTkLabel(view_assigned_frame, text="3. Consultar y Programar Órdenes", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.view_assigned_button = ctk.CTkButton(view_assigned_frame, text="Consultar Configuración Actual", command=self._run_view_assigned_thread)
        self.view_assigned_button.pack(pady=10)
        
        assigned_display_container = ctk.CTkFrame(view_assigned_frame, fg_color="transparent")
        assigned_display_container.pack(fill="x", expand=True, padx=10)
        assigned_display_container.grid_columnconfigure((0, 1), weight=1)
        
        tp1_display_frame = ctk.CTkFrame(assigned_display_container)
        tp1_display_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        ctk.CTkLabel(tp1_display_frame, text="Teleprotección 1", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.tp1_module_label = self._create_info_row(tp1_display_frame, "Módulo:")
        self.tp1_tx_entry = self._create_info_entry_row(tp1_display_frame, "Órdenes TX:")
        self.tp1_rx_entry = self._create_info_entry_row(tp1_display_frame, "Órdenes RX:")

        tp2_display_frame = ctk.CTkFrame(assigned_display_container)
        tp2_display_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        ctk.CTkLabel(tp2_display_frame, text="Teleprotección 2", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.tp2_module_label = self._create_info_row(tp2_display_frame, "Módulo:")
        self.tp2_tx_entry = self._create_info_entry_row(tp2_display_frame, "Órdenes TX:")
        self.tp2_rx_entry = self._create_info_entry_row(tp2_display_frame, "Órdenes RX:")
        
        self.program_commands_button = ctk.CTkButton(view_assigned_frame, text="Programar Nuevas Órdenes", command=self._run_program_commands_thread)
        self.program_commands_button.pack(pady=(15,10))
        
        timezone_frame = ctk.CTkFrame(main_scroll_frame)
        timezone_frame.grid(row=4, column=0, pady=10, sticky="ew")
        ctk.CTkLabel(timezone_frame, text="4. Configurar Zona Horaria", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        tz_selector_frame = ctk.CTkFrame(timezone_frame, fg_color="transparent")
        tz_selector_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(tz_selector_frame, text="Zona Horaria:", width=180).pack(side="left")
        self.timezone_selector = ctk.CTkComboBox(tz_selector_frame, values=list(self.timezone_map.keys()))
        self.timezone_selector.pack(side="left", expand=True, fill="x")
        self.timezone_selector.set("(UTC+2)Madrid")

        self.program_timezone_button = ctk.CTkButton(timezone_frame, text="Programar Zona Horaria", command=self._run_configure_timezone_thread)
        self.program_timezone_button.pack(pady=15)

        status_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        status_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.status_label = ctk.CTkLabel(status_frame, text="Status: Ready", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(pady=5)
        log_button = ctk.CTkButton(status_frame, text="📂 Open Last Report (log.html)", state="disabled", command=self._open_log_file)
        log_button.pack(pady=5)
        self.log_buttons.append(log_button)

    def _populate_command_assignment_tab(self, tab_frame):
        """Populates the 'Command Assignment' tab with its widgets."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)
        
        control_frame = ctk.CTkFrame(tab_frame)
        control_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.refresh_assignments_button = ctk.CTkButton(control_frame, text="Consultar Configuración de Entradas/Salidas y Comandos", command=self._run_log_command_info_thread)
        self.refresh_assignments_button.pack(pady=10)

        container = ctk.CTkScrollableFrame(tab_frame, label_text="Asignación de Comandos")
        container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        tx_section_frame = ctk.CTkFrame(container)
        tx_section_frame.grid(row=0, column=0, sticky="nsew", pady=(0,20))
        ctk.CTkLabel(tx_section_frame, text="ASSIGNMENT OF INPUTS TO COMMANDS (TX)", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.tx_header_frame = ctk.CTkFrame(tx_section_frame, fg_color=("gray85", "gray15"))
        self.tx_header_frame.pack(fill="x", padx=10, pady=(5,0))
        self.tx_tp1_header_label = self._create_command_header_row(self.tx_header_frame, "Teleprotection (1)")
        self.tx_tp2_header_label = self._create_command_header_row(self.tx_header_frame, "Teleprotection (2)")
        
        self.tx_grid_frame = ctk.CTkFrame(tx_section_frame)
        self.tx_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)

        rx_section_frame = ctk.CTkFrame(container)
        rx_section_frame.grid(row=1, column=0, sticky="nsew", pady=(10,0))
        ctk.CTkLabel(rx_section_frame, text="ASSIGNMENT OF COMMANDS(RX) TO OUTPUTS", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        self.rx_header_frame = ctk.CTkFrame(rx_section_frame, fg_color=("gray85", "gray15"))
        self.rx_header_frame.pack(fill="x", padx=10, pady=(5,0))
        self.rx_tp1_header_label = self._create_command_header_row(self.rx_header_frame, "Teleprotection (1)")
        self.rx_tp2_header_label = self._create_command_header_row(self.rx_header_frame, "Teleprotection (2)")

        self.rx_grid_frame = ctk.CTkFrame(rx_section_frame)
        self.rx_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.program_assignments_button = ctk.CTkButton(tab_frame, text="Programar Asignaciones", command=self._run_program_assignments_thread)
        self.program_assignments_button.grid(row=2, column=0, padx=20, pady=(10,20))

        log_button = ctk.CTkButton(tab_frame, text="📂 Open Last Report (log.html)", state="disabled", command=self._open_log_file)
        log_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="s")
        self.log_buttons.append(log_button)

        self._update_command_assignment_grids(None, 0, 0)

    def _populate_module_config_tab(self, tab_frame):
        """Populates the 'Module Configuration' tab with sub-tabs for each module."""
        module_names = ["IBTU_ByTones", "IBTU_DualTone", "IBTU_FFT", "IBTU_FSK", "ICPT", "IDTU", "IOCS", "IOCT", "IOTU"]
        
        module_tab_view = self._create_tab_view(tab_frame, module_names)
        module_tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        for module_name in module_names:
            sub_tab = module_tab_view.tab(module_name)
            sub_tab.grid_columnconfigure(0, weight=1)
            sub_tab.grid_rowconfigure(0, weight=1)

            if module_name == "IBTU_ByTones":
                self._populate_ibtu_bytones_tab(sub_tab)
            else:
                placeholder_frame = ctk.CTkFrame(sub_tab, fg_color="transparent")
                placeholder_frame.grid(row=0, column=0, sticky="nsew")
                ctk.CTkLabel(placeholder_frame, text=f"Configuración para {module_name}\n(En desarrollo)", 
                             font=ctk.CTkFont(size=16)).pack(expand=True)

            log_button = ctk.CTkButton(sub_tab, text="📂 Open Last Report (log.html)", state="disabled", command=self._open_log_file)
            log_button.grid(row=1, column=0, padx=20, pady=20, sticky="s")
            self.log_buttons.append(log_button)

    def _populate_ibtu_bytones_tab(self, tab_frame):
        """Populates the IBTU_ByTones configuration tab."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1) 

        scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Configuración de IBTU por Tonos")
        scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        general_frame = ctk.CTkFrame(scroll_frame)
        general_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        general_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(general_frame, text="General", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5,10), sticky="w")
        
        ctk.CTkLabel(general_frame, text="Reception operation mode:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ibtu_rx_op_mode = ctk.CTkComboBox(general_frame, values=list(self.ibtu_rx_op_mode_map.keys()))
        self.ibtu_rx_op_mode.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(general_frame, text="LOCAL Automatic Link Test Periodicity (h):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.ibtu_local_periodicity = ctk.CTkEntry(general_frame, placeholder_text="0-24")
        self.ibtu_local_periodicity.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(general_frame, text="REMOTE Automatic Link Test Periodicity (h):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.ibtu_remote_periodicity = ctk.CTkEntry(general_frame, placeholder_text="0-24")
        self.ibtu_remote_periodicity.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(general_frame, text="Activation Threshold for low Snr Ratio Alarm (dB):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.ibtu_snr_activation = ctk.CTkEntry(general_frame, placeholder_text="0-18")
        self.ibtu_snr_activation.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(general_frame, text="Deactivation Threshold for low Snr Ratio Alarm (dB):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.ibtu_snr_deactivation = ctk.CTkEntry(general_frame, placeholder_text="2-20")
        self.ibtu_snr_deactivation.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        program_s1_button = ctk.CTkButton(general_frame, text="Programar Sección General", command=self._run_program_ibtu_s1_thread)
        program_s1_button.grid(row=6, column=0, columnspan=2, pady=10, padx=10)

        freq_frame = ctk.CTkFrame(scroll_frame)
        freq_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        freq_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(freq_frame, text="Frequencies", font=ctk.CTkFont(weight="bold")).pack(pady=(5,10))
        
        top_control_frame = ctk.CTkFrame(freq_frame)
        top_control_frame.pack(fill="x", padx=10, pady=10)
        retrieve_button = ctk.CTkButton(top_control_frame, text="Consultar Configuración IBTU", command=self._run_retrieve_ibtu_config_thread)
        retrieve_button.pack(pady=10, padx=10, fill="x")

        tx_rx_container = ctk.CTkFrame(freq_frame, fg_color="transparent")
        tx_rx_container.pack(fill="x", expand=True)
        tx_rx_container.grid_columnconfigure((0,1), weight=1)

        tx_frame = ctk.CTkFrame(tx_rx_container)
        tx_frame.grid(row=0, column=0, padx=(0,5), sticky="nsew")
        ctk.CTkLabel(tx_frame, text="TRANSMISSION", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.ibtu_tx_tone_widgets = self._create_tone_section(tx_frame, is_tx=True)

        rx_frame = ctk.CTkFrame(tx_rx_container)
        rx_frame.grid(row=0, column=1, padx=(5,0), sticky="nsew")
        ctk.CTkLabel(rx_frame, text="RECEPTION", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.ibtu_rx_tone_widgets = self._create_tone_section(rx_frame, is_tx=False)

        program_s2_button = ctk.CTkButton(freq_frame, text="Programar Frecuencias", command=self._run_program_ibtu_s2_thread)
        program_s2_button.pack(pady=10, padx=10)

        levels_frame = ctk.CTkFrame(scroll_frame)
        levels_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        levels_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(levels_frame, text="Levels", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5,10), sticky="w")
        
        ctk.CTkLabel(levels_frame, text="Input Level (dBm):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ibtu_input_level = ctk.CTkEntry(levels_frame, placeholder_text="-40 a 0")
        self.ibtu_input_level.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(levels_frame, text="Power Boosting (dB):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.ibtu_power_boosting = ctk.CTkEntry(levels_frame, placeholder_text="0 a 6")
        self.ibtu_power_boosting.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(levels_frame, text="Output Level (dBm):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.ibtu_output_level = ctk.CTkEntry(levels_frame, placeholder_text="-30 a 0")
        self.ibtu_output_level.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        program_s3_button = ctk.CTkButton(levels_frame, text="Programar Niveles", command=self._run_program_ibtu_s3_thread)
        program_s3_button.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

    def _create_tone_section(self, parent, is_tx):
        """Helper to create the UI for TX or RX tone configuration with both scrollbars."""
        widgets = {}
        
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.pack(fill="x", padx=5, pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(controls_frame, text="Scheme:").grid(row=0, column=0, padx=(5,0), pady=5, sticky="w")
        widgets['scheme_combo'] = ctk.CTkComboBox(controls_frame, values=list(self.ibtu_scheme_map.keys()))
        widgets['scheme_combo'].grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(controls_frame, text="Guard Tone:").grid(row=1, column=0, padx=(5,0), pady=5, sticky="w")
        widgets['guard_combo'] = ctk.CTkComboBox(controls_frame, values=self.all_ibtu_frequencies)
        widgets['guard_combo'].grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", padx=5, pady=5)
        widgets['copy_button'] = ctk.CTkButton(button_frame, text="Copy")
        widgets['copy_button'].pack(side="left", padx=5)
        widgets['reset_button'] = ctk.CTkButton(button_frame, text="Reset")
        widgets['reset_button'].pack(side="left", padx=5)
        
        table_container = ctk.CTkFrame(parent)
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        bg_color = table_container.cget("fg_color")
        if isinstance(bg_color, (list, tuple)):
            bg_color = bg_color[1] if ctk.get_appearance_mode() == "Dark" else bg_color[0]

        canvas = tk.Canvas(table_container, bg=bg_color, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        v_scrollbar = ctk.CTkScrollbar(table_container, orientation="vertical", command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        h_scrollbar = ctk.CTkScrollbar(table_container, orientation="horizontal", command=canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        table_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        canvas.create_window((0, 0), window=table_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        table_frame.bind("<Configure>", on_frame_configure)
        
        widgets['table_frame'] = table_frame

        headers = ["Tone", "Command activated", "Command transmitted", "Application Type", "Frequency (Hz)"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(table_frame, text=header, font=ctk.CTkFont(weight="bold"))
            header_label.grid(row=0, column=i, padx=10, pady=5)
            table_frame.grid_columnconfigure(i, minsize=140)

        return widgets

    def _update_ibtu_tones_table(self, tone_widgets, tone_data, is_tx):
        """Populates the tones table with data and stores the interactive widgets."""
        table_frame = tone_widgets['table_frame']
        
        for widget in table_frame.winfo_children():
            if widget.grid_info()['row'] > 0:
                widget.destroy()
        
        table_widgets_list = self.ibtu_tx_table_widgets if is_tx else self.ibtu_rx_table_widgets
        command_groups = self.tx_command_groups if is_tx else self.rx_command_groups
        table_widgets_list.clear()
        command_groups.clear()

        if not tone_data:
            ctk.CTkLabel(table_frame, text="No data retrieved.").grid(row=1, column=0, columnspan=5, pady=10)
            return

        for i, row_data in enumerate(tone_data):
            row = i + 1
            row_widgets = {}
            
            command_transmitted = str(row_data[2])
            row_widgets['command'] = command_transmitted
            
            ctk.CTkLabel(table_frame, text=row_data[0]).grid(row=row, column=0, padx=5, pady=2)
            ctk.CTkLabel(table_frame, text=row_data[1]).grid(row=row, column=1, padx=5, pady=2)
            ctk.CTkLabel(table_frame, text=command_transmitted).grid(row=row, column=2, padx=5, pady=2)
            
            app_type_combo = ctk.CTkComboBox(table_frame, values=list(self.ibtu_app_type_map.keys()))
            app_type_combo.grid(row=row, column=3, padx=5, pady=2)
            row_widgets['app_type'] = app_type_combo
            
            freq_combo = ctk.CTkComboBox(table_frame, values=["..."])
            freq_combo.grid(row=row, column=4, padx=5, pady=2)
            row_widgets['freq'] = freq_combo

            table_widgets_list.append(row_widgets)

            if command_transmitted not in command_groups:
                command_groups[command_transmitted] = []
            command_groups[command_transmitted].append(row_widgets)

        for i, row_widgets in enumerate(table_widgets_list):
            app_type_combo = row_widgets['app_type']
            freq_combo = row_widgets['freq']
            
            app_type_combo.configure(command=lambda v, idx=i, tx=is_tx: self._on_tone_setting_change(v, idx, 'app_type', tx))
            freq_combo.configure(command=lambda v, idx=i, tx=is_tx: self._on_tone_setting_change(v, idx, 'freq', tx))

            row_data = tone_data[i]
            if len(row_data) >= 5:
                app_type_val = str(row_data[3])
                app_type_str = self.ibtu_app_type_map_rev.get(app_type_val, "Blocking")
                app_type_combo.set(app_type_str)
                self._update_frequency_options(app_type_str, freq_combo)
                freq_val = str(row_data[4])
                freq_combo.set(freq_val)

    def _on_tone_setting_change(self, new_value, row_index, widget_type, is_tx):
        """Callback to handle changes in app_type or frequency and synchronize linked rows."""
        table_widgets = self.ibtu_tx_table_widgets if is_tx else self.ibtu_rx_table_widgets
        command_groups = self.tx_command_groups if is_tx else self.rx_command_groups
        
        if row_index >= len(table_widgets):
            return

        source_row_widgets = table_widgets[row_index]
        command_key = source_row_widgets['command']
        linked_widgets = command_groups.get(command_key, [])

        for row in linked_widgets:
            if widget_type == 'app_type':
                row['app_type'].set(new_value)
                self._update_frequency_options(new_value, row['freq'])
            elif widget_type == 'freq':
                row['freq'].set(new_value)
        
        if row_index == 0 and widget_type == 'app_type':
            guard_combo = self.ibtu_tx_tone_widgets['guard_combo'] if is_tx else self.ibtu_rx_tone_widgets['guard_combo']
            self._update_guard_tone_options(new_value, guard_combo)

    def _update_frequency_options(self, selected_app_type, freq_combo):
        """Callback to update the frequency combobox based on the application type."""
        freq_list = self.ibtu_freq_map.get(selected_app_type, [])
        current_freq = freq_combo.get()
        freq_combo.configure(values=freq_list)
        if current_freq not in freq_list:
            freq_combo.set(freq_list[0] if freq_list else "")
            
    def _update_guard_tone_options(self, selected_app_type, guard_combo):
        """Callback to update the guard tone combobox based on the first tone's application type."""
        freq_list = self.ibtu_freq_map.get(selected_app_type, [])
        current_guard_freq = guard_combo.get()
        guard_combo.configure(values=freq_list)
        if current_guard_freq not in freq_list:
            guard_combo.set(freq_list[0] if freq_list else "")

    def _update_options_for_first_tone(self, selected_app_type, guard_combo, freq_combo):
        """A special callback for the first tone's app_type, updating both its own freq and the guard tone."""
        self._update_guard_tone_options(selected_app_type, guard_combo)
        self._update_frequency_options(selected_app_type, freq_combo)
            
    def _populate_snmp_tab(self, tab_frame):
        """Populates the SNMP tab with its sub-tabs."""
        snmp_tab_view = self._create_tab_view(tab_frame, ["Receptor de Traps", "Diccionario de Traps", "Configuración SNMP"])
        snmp_tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._populate_snmp_receiver_tab(snmp_tab_view.tab("Receptor de Traps"))
        self._populate_snmp_dictionary_tab(snmp_tab_view.tab("Diccionario de Traps"))
        self._populate_snmp_config_tab(snmp_tab_view.tab("Configuración SNMP"))

    def _populate_snmp_receiver_tab(self, tab_frame):
        """Populates the SNMP Receiver sub-tab with its widgets."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)

        config_frame = ctk.CTkFrame(tab_frame)
        config_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(config_frame, text="Dirección IP del Listener:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ip_line_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        ip_line_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ip_line_frame.grid_columnconfigure(0, weight=1)
        
        self.snmp_ip_entry = ctk.CTkEntry(ip_line_frame, placeholder_text="0.0.0.0")
        self.snmp_ip_entry.grid(row=0, column=0, sticky="ew")
        
        self.copy_ip_button = ctk.CTkButton(ip_line_frame, text="Usar IP Local", command=self._set_local_ip, width=100)
        self.copy_ip_button.grid(row=0, column=1, padx=(10, 0))

        ctk.CTkLabel(config_frame, text="Puerto del Listener:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.snmp_port_entry = ctk.CTkEntry(config_frame, placeholder_text="171")
        self.snmp_port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.snmp_port_entry.insert(0, "171")
        
        self.start_listener_button = ctk.CTkButton(config_frame, text="Iniciar Listener", command=self._start_snmp_listener_thread)
        self.start_listener_button.grid(row=3, column=0, pady=10, padx=5, sticky="ew")

        self.stop_listener_button = ctk.CTkButton(config_frame, text="Detener Listener", command=self._stop_snmp_listener_thread)
        self.stop_listener_button.grid(row=3, column=1, pady=10, padx=5, sticky="ew")

        self.snmp_listener_status_label = ctk.CTkLabel(config_frame, text="Listener: Detenido", text_color="red")
        self.snmp_listener_status_label.grid(row=4, column=0, columnspan=2, pady=(0, 5))

        self.trap_display = ctk.CTkTextbox(tab_frame, state="disabled")
        self.trap_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        controls_frame = ctk.CTkFrame(tab_frame)
        controls_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        controls_frame.grid_columnconfigure((0,1,2), weight=1)

        self.show_all_traps_button = ctk.CTkButton(controls_frame, text="Refrescar Traps", command=self._show_all_traps)
        self.show_all_traps_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        filter_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.snmp_filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="Filtrar por texto...")
        self.snmp_filter_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.filter_traps_button = ctk.CTkButton(filter_frame, text="Filtrar", width=60, command=self._filter_traps)
        self.filter_traps_button.pack(side="left")

        self.reset_traps_button = ctk.CTkButton(controls_frame, text="Borrar Traps Almacenados", command=self._reset_traps)
        self.reset_traps_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def _populate_snmp_dictionary_tab(self, tab_frame):
        """Populates the SNMP Trap Dictionary sub-tab."""
        label = ctk.CTkLabel(tab_frame, text="Diccionario de Traps SNMP", font=ctk.CTkFont(size=16, weight="bold"))
        label.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(tab_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        trap_dictionary = {
            "tpu1cNotifyConfigModification": "Notificación de modificación de configuración.",
            "tpu1cNotifyModuleError": "Notificación de error en un módulo.",
            "tpu1cNotifyReceiverBlocked": "Notificación de bloqueo del receptor.",
            "tpu1cNotifySyncLoss": "Notificación de pérdida de sincronismo.",
            "tpu1cNotifyIPLinkFault": "Notificación de fallo en el enlace IP.",
            "tpu1NotifyIpSyncLoss": "Notificación de pérdida de sincronismo IP.",
            "tpu1cNotifyIpTxTrans": "Notificación de transición en la transmisión IP.",
            "tpu1cNotifyMeanTranferDelay": "Notificación de retardo medio de transferencia.",
            "tpu1cNotifyFrameDelayVariation": "Notificación de variación en el retardo de trama (Jitter).",
            "tpu1cNotifyFrameLossRatio": "Notificación de ratio de pérdida de tramas.",
            "tpu1cNotifyGenRemAlarm": "Notificación de alarma remota general.",
            "tpu1cNotifyOutputCircuits": "Notificación de cambio de estado en los circuitos de salida.",
            "tpu1cNotifyInputCircuits": "Notificación de cambio de estado en los circuitos de entrada.",
            "tpu1cNotifyCommandTx": "Notificación de transmisión de un comando.",
            "tpu1cNotifyCommandRx": "Notificación de recepción de un comando."
        }
        
        for name, desc in trap_dictionary.items():
            self._create_dictionary_entry(scroll_frame, name, desc)

    def _create_dictionary_entry(self, parent, name, description):
        """Creates a single entry for the trap dictionary display."""
        entry_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20"))
        entry_frame.pack(fill="x", pady=4, padx=5)
        entry_frame.grid_columnconfigure(0, weight=1)
        
        name_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        name_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5,0))
        name_frame.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(name_frame, text=name, font=ctk.CTkFont(weight="bold"))
        name_label.grid(row=0, column=0, sticky="w")
        
        copy_button = ctk.CTkButton(name_frame, text="Copiar", width=50, command=lambda n=name: self.copy_to_clipboard(n))
        copy_button.grid(row=0, column=1, sticky="e", padx=(10,0))

        desc_label = ctk.CTkLabel(entry_frame, text=description, wraplength=600, justify="left", anchor="w")
        desc_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,5))

    def copy_to_clipboard(self, text):
        """Copies the given text to the clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self._update_status(f"'{text}' copiado al portapapeles.", "white")


    def _populate_snmp_config_tab(self, tab_frame):
        """Populates the new SNMP Configuration sub-tab with all its widgets."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)

        scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Configuración General SNMP")
        scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        agent_frame = ctk.CTkFrame(scroll_frame)
        agent_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.snmp_agent_state_cb = ctk.CTkCheckBox(agent_frame, text="Enable SNMP Agent", font=ctk.CTkFont(weight="bold"), command=self._toggle_snmp_config_visibility)
        self.snmp_agent_state_cb.grid(row=0, column=0, padx=10, pady=10)

        self.snmp_settings_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.snmp_settings_container.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
        self.snmp_settings_container.grid_columnconfigure(0, weight=1)

        general_settings_frame = ctk.CTkFrame(self.snmp_settings_container)
        general_settings_frame.grid(row=0, column=0, pady=5, sticky="ew")
        general_settings_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(general_settings_frame, text="Traps Enable:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.traps_enable_state_cb = ctk.CTkCheckBox(general_settings_frame, text="")
        self.traps_enable_state_cb.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(general_settings_frame, text="TPU SNMP Port:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.tpu_snmp_port_entry = ctk.CTkEntry(general_settings_frame)
        self.tpu_snmp_port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        v1_v2_frame = ctk.CTkFrame(self.snmp_settings_container)
        v1_v2_frame.grid(row=1, column=0, pady=5, sticky="ew")
        self.snmp_v1_v2_enable_cb = ctk.CTkCheckBox(v1_v2_frame, text="Enable SNMP v1/v2", command=self._toggle_snmp_config_visibility)
        self.snmp_v1_v2_enable_cb.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        self.snmp_v1_v2_settings_frame = ctk.CTkFrame(v1_v2_frame, fg_color="transparent")
        self.snmp_v1_v2_settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20)
        self.snmp_v1_v2_settings_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.snmp_v1_v2_settings_frame, text="Read Community:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.snmp_v1_v2_read_entry = ctk.CTkEntry(self.snmp_v1_v2_settings_frame)
        self.snmp_v1_v2_read_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.snmp_v1_v2_settings_frame, text="Write Community:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.snmp_v1_v2_set_entry = ctk.CTkEntry(self.snmp_v1_v2_settings_frame)
        self.snmp_v1_v2_set_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        v3_frame = ctk.CTkFrame(self.snmp_settings_container)
        v3_frame.grid(row=2, column=0, pady=5, sticky="ew")
        self.snmp_v3_enable_cb = ctk.CTkCheckBox(v3_frame, text="Enable SNMP v3", command=self._toggle_snmp_config_visibility)
        self.snmp_v3_enable_cb.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        self.snmp_v3_settings_frame = ctk.CTkFrame(v3_frame, fg_color="transparent")
        self.snmp_v3_settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20)
        self.snmp_v3_settings_frame.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(self.snmp_v3_settings_frame, text="Read User:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.snmp_v3_read_user_entry = ctk.CTkEntry(self.snmp_v3_settings_frame)
        self.snmp_v3_read_user_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.snmp_v3_settings_frame, text="Password:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.snmp_v3_read_pass_entry = ctk.CTkEntry(self.snmp_v3_settings_frame, show="*")
        self.snmp_v3_read_pass_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.snmp_v3_settings_frame, text="Auth Protocol:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.snmp_v3_read_auth_entry = ctk.CTkEntry(self.snmp_v3_settings_frame)
        self.snmp_v3_read_auth_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.snmp_v3_settings_frame, text="Write User:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.snmp_v3_write_user_entry = ctk.CTkEntry(self.snmp_v3_settings_frame)
        self.snmp_v3_write_user_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.snmp_v3_settings_frame, text="Password:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.snmp_v3_write_pass_entry = ctk.CTkEntry(self.snmp_v3_settings_frame, show="*")
        self.snmp_v3_write_pass_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.snmp_v3_settings_frame, text="Auth Protocol:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.snmp_v3_write_auth_entry = ctk.CTkEntry(self.snmp_v3_settings_frame)
        self.snmp_v3_write_auth_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        hosts_main_frame = ctk.CTkFrame(self.snmp_settings_container)
        hosts_main_frame.grid(row=3, column=0, pady=10, sticky="ew")
        hosts_main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hosts_main_frame, text="Notification Handling", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(5,10), sticky="w")

        hosts_grid_frame = ctk.CTkFrame(hosts_main_frame, fg_color="transparent")
        hosts_grid_frame.grid(row=1, column=0, sticky="ew", padx=5)
        hosts_grid_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(hosts_grid_frame, text="Host", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(hosts_grid_frame, text="Enable", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(hosts_grid_frame, text="IP Addr.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(hosts_grid_frame, text="Port", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(hosts_grid_frame, text="Trap Mode", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5)

        self.host_widgets.clear()
        for i in range(5):
            ctk.CTkLabel(hosts_grid_frame, text=str(i+1)).grid(row=i+1, column=0)
            
            enable_cb = ctk.CTkCheckBox(hosts_grid_frame, text="")
            enable_cb.grid(row=i+1, column=1, padx=5)
            
            ip_entry = ctk.CTkEntry(hosts_grid_frame, placeholder_text="0.0.0.0")
            ip_entry.grid(row=i+1, column=2, padx=5, sticky="ew")
            
            port_entry = ctk.CTkEntry(hosts_grid_frame, width=60)
            port_entry.grid(row=i+1, column=3, padx=5)
            
            trap_mode_cb = ctk.CTkComboBox(hosts_grid_frame, values=list(self.trap_mode_map.keys()), width=140)
            trap_mode_cb.grid(row=i+1, column=4, padx=5)
            
            self.host_widgets.append({'enable': enable_cb, 'ip': ip_entry, 'port': port_entry, 'mode': trap_mode_cb})

        buttons_frame = ctk.CTkFrame(tab_frame)
        buttons_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        buttons_frame.grid_columnconfigure((0,1), weight=1)

        self.query_snmp_config_button = ctk.CTkButton(buttons_frame, text="Consultar Configuración SNMP", command=self._run_retrieve_snmp_config_thread)
        self.query_snmp_config_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.program_snmp_config_button = ctk.CTkButton(buttons_frame, text="Programar Configuración SNMP", command=self._run_execute_snmp_config_thread)
        self.program_snmp_config_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        log_button = ctk.CTkButton(tab_frame, text="📂 Open Last Report (log.html)", state="disabled", command=self._open_log_file)
        log_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.log_buttons.append(log_button)

        self._toggle_snmp_config_visibility()
        
    def _populate_input_activation_tab(self, tab_frame):
        """Populates the Input Activation tab with its widgets."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)

        consult_frame = ctk.CTkFrame(tab_frame)
        consult_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        consult_frame.grid_columnconfigure(1, weight=1)

        self.retrieve_inputs_button = ctk.CTkButton(consult_frame, text="Consultar Estado de Entradas", command=self._run_retrieve_inputs_state_thread)
        self.retrieve_inputs_button.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        self.input_activation_status_label = ctk.CTkLabel(consult_frame, text="Estado: Desconocido", font=ctk.CTkFont(weight="bold"))
        self.input_activation_status_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.inputs_scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Entradas Disponibles")
        self.inputs_scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.inputs_scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        program_main_frame = ctk.CTkFrame(tab_frame)
        program_main_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        program_main_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(program_main_frame, text="Programar Activación/Desactivación", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(5,10), sticky="w")

        program_controls_frame = ctk.CTkFrame(program_main_frame, fg_color="transparent")
        program_controls_frame.grid(row=1, column=0, sticky="ew")
        program_controls_frame.grid_columnconfigure(2, weight=1)

        self.activation_mode_var = ctk.StringVar(value="activate")
        activate_radio = ctk.CTkRadioButton(program_controls_frame, text="Activar", variable=self.activation_mode_var, value="activate")
        activate_radio.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        deactivate_radio = ctk.CTkRadioButton(program_controls_frame, text="Desactivar", variable=self.activation_mode_var, value="deactivate")
        deactivate_radio.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(program_controls_frame, text="Duración:").grid(row=0, column=1, padx=(20, 5), pady=10, sticky="e")
        self.duration_combobox = ctk.CTkComboBox(program_controls_frame, values=list(self.duration_map.keys()))
        self.duration_combobox.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="ew")
        self.duration_combobox.set("Permanente")

        self.program_inputs_button = ctk.CTkButton(program_controls_frame, text="Programar Entradas", command=self._run_program_inputs_activation_thread)
        self.program_inputs_button.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        
        log_button = ctk.CTkButton(tab_frame, text="📂 Open Last Report (log.html)", state="disabled", command=self._open_log_file)
        log_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="s")
        self.log_buttons.append(log_button)

    def _populate_chrono_register_tab(self, tab_frame):
        """Populates the Chronological Register tab."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(2, weight=1)

        controls_frame = ctk.CTkFrame(tab_frame)
        controls_frame.grid(row=0, column=0, padx=20, pady=(10,0), sticky="ew")
        controls_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(controls_frame, text="Número de Entradas:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.num_entries_entry = ctk.CTkEntry(controls_frame, placeholder_text="Ej: 10")
        self.num_entries_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(controls_frame, text="Filtro de Evento/Alarma:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.event_filter_entry = ctk.CTkEntry(controls_frame, placeholder_text="Opcional")
        self.event_filter_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(controls_frame, text="Orden:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.chrono_order_combobox = ctk.CTkComboBox(controls_frame, values=["Ascendente", "Descendente"])
        self.chrono_order_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.chrono_order_combobox.set("Ascendente")

        action_buttons_frame = ctk.CTkFrame(tab_frame)
        action_buttons_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        action_buttons_frame.grid_columnconfigure((0,1), weight=1)

        self.capture_last_entries_button = ctk.CTkButton(action_buttons_frame, text="Capturar Entradas", command=self._run_capture_last_entries_thread)
        self.capture_last_entries_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.clear_chrono_button = ctk.CTkButton(action_buttons_frame, text="Limpiar Registro", command=self._run_clear_chrono_log_thread)
        self.clear_chrono_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.chrono_log_display = ctk.CTkTextbox(tab_frame, state="disabled", wrap="none")
        self.chrono_log_display.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
    def _populate_debug_log_tab(self, tab_frame):
        """Populates the Debug Log tab."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        
        self.debug_log_display = ctk.CTkTextbox(tab_frame, state="disabled", wrap="none")
        self.debug_log_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def _populate_loops_blocking_tab(self, tab_frame):
        """Populates the Loops and Blocking tab with its widgets."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)

        control_frame = ctk.CTkFrame(tab_frame)
        control_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.refresh_alignment_button = ctk.CTkButton(control_frame, text="Consultar Estados Actuales de Bucles y Bloqueos", command=self._run_refresh_alignment_states_thread)
        self.refresh_alignment_button.pack(pady=10, padx=10, fill="x")

        container = ctk.CTkScrollableFrame(tab_frame, label_text="Control de Bucles y Bloqueos")
        container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        loops_frame = ctk.CTkFrame(container)
        loops_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        loops_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(loops_frame, text="LOOPS", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 10))
        
        self.loop1_widgets = self._create_alignment_control_row(loops_frame, "TELEPROTECTION -1-", 1, is_loop=True)
        self.loop2_widgets = self._create_alignment_control_row(loops_frame, "TELEPROTECTION -2-", 2, is_loop=True)

        blocking_frame = ctk.CTkFrame(container)
        blocking_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        blocking_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(blocking_frame, text="BLOCKING", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 10))

        self.blocking1_widgets = self._create_alignment_control_row(blocking_frame, "TELEPROTECTION -1-", 1, is_loop=False)
        self.blocking2_widgets = self._create_alignment_control_row(blocking_frame, "TELEPROTECTION -2-", 2, is_loop=False)
        
        log_button = ctk.CTkButton(tab_frame, text="📂 Open Last Report (log.html)", state="disabled", command=self._open_log_file)
        log_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="s")
        self.log_buttons.append(log_button)

    def _create_alignment_control_row(self, parent, title, tp_number, is_loop):
        """Helper function to create a control row for loops or blocking."""
        widgets = {}
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", expand=True, padx=10, pady=5)

        row_frame.grid_columnconfigure(2, weight=1)
        row_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(row_frame, text=title, width=130).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        status_module_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        status_module_frame.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        widgets['status_label'] = ctk.CTkLabel(status_module_frame, text="Estado: Desconocido", width=120)
        widgets['status_label'].pack(anchor="w")
        widgets['module_label'] = ctk.CTkLabel(status_module_frame, text="Módulo: -", text_color="gray")
        widgets['module_label'].pack(anchor="w")
        widgets['timer_label'] = ctk.CTkLabel(status_module_frame, text="", text_color="cyan")
        widgets['timer_label'].pack(anchor="w")
        widgets['timer_label'].pack_forget()

        if is_loop:
            ctk.CTkLabel(row_frame, text="Type:").grid(row=0, column=2, padx=(10, 5), pady=10, sticky="e")
            widgets['type_combo'] = ctk.CTkComboBox(row_frame, values=list(self.loop_type_map.keys()), width=120)
            widgets['type_combo'].grid(row=0, column=3, padx=(0, 10), pady=10, sticky="w")
            widgets['type_combo'].set("NONE")
        
        ctk.CTkLabel(row_frame, text="Duration:").grid(row=0, column=4, padx=(10, 5), pady=10, sticky="e")
        widgets['duration_combo'] = ctk.CTkComboBox(row_frame, values=list(self.duration_map.keys()), width=140)
        widgets['duration_combo'].grid(row=0, column=5, padx=(0, 10), pady=10, sticky="w")
        widgets['duration_combo'].set("Permanente")

        button_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        button_frame.grid(row=0, column=6, padx=10, pady=10)

        if is_loop:
            command_activate = lambda: self._run_program_loop_thread(tp_number, activate=True)
            command_deactivate = lambda: self._run_program_loop_thread(tp_number, activate=False)
        else:
            command_activate = lambda: self._run_program_blocking_thread(tp_number, activate=True)
            command_deactivate = lambda: self._run_program_blocking_thread(tp_number, activate=False)

        widgets['activate_button'] = ctk.CTkButton(button_frame, text="Activar", width=80, command=command_activate)
        widgets['activate_button'].pack(side="left", padx=(0, 5))
        widgets['deactivate_button'] = ctk.CTkButton(button_frame, text="Desactivar", width=80, command=command_deactivate)
        widgets['deactivate_button'].pack(side="left")

        return widgets

    def _toggle_snmp_config_visibility(self):
        """Shows or hides sections based on the state of the master checkboxes."""
        if self.snmp_agent_state_cb.get() == 1:
            self.snmp_settings_container.grid()
        else:
            self.snmp_settings_container.grid_remove()
            return

        if self.snmp_v1_v2_enable_cb.get() == 1:
            self.snmp_v1_v2_settings_frame.grid()
        else:
            self.snmp_v1_v2_settings_frame.grid_remove()

        if self.snmp_v3_enable_cb.get() == 1:
            self.snmp_v3_settings_frame.grid()
        else:
            self.snmp_v3_settings_frame.grid_remove()

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

    def process_gui_queue(self):
        """
        Process messages from the thread-safe queue to update the GUI.
        """
        try:
            while not self.gui_queue.empty(): # Mientras haya mensajes en la cola
                message = self.gui_queue.get_nowait()
                msg_type = message[0]
                
                if msg_type == 'main_status':
                    self._update_status(message[1], message[2])
                elif msg_type == 'session_status':
                    self._update_session_status(message[1], message[2])
                elif msg_type == 'snmp_listener_status':
                    self._update_snmp_listener_status(message[1], message[2])
                elif msg_type == 'enable_buttons':
                    self.run_button_state(is_running=False)
                elif msg_type == 'modules_display':
                    self._update_modules_display(message[1])
                elif msg_type == 'assigned_modules_display':
                    self._update_assigned_modules_display(message[1], message[2])
                elif msg_type == 'command_assignment_grids':
                    self._update_command_assignment_grids(message[1], message[2], message[3])
                elif msg_type == 'full_snmp_config_display':
                    self._update_full_snmp_config_display(message[1])
                elif msg_type == 'update_input_activation_display':
                    self._update_input_activation_display(message[1], message[2])
                elif msg_type == 'program_inputs_success':
                    self._handle_program_inputs_success(message[1], message[2], message[3])
                elif msg_type == 'update_chrono_log_display':
                    self._update_chrono_log_display(message[1])
                elif msg_type == 'debug_log':
                    self._update_debug_log(message[1])
                elif msg_type == 'update_alignment_states':
                    self._update_alignment_states(message[1])
                elif msg_type == 'program_alignment_success':
                    self._handle_program_alignment_success(*message[1:])
                elif msg_type == 'update_ibtu_full_config':
                    self._update_ibtu_full_config_display(message[1])
                elif msg_type == 'scheduler_log':
                    self._update_scheduler_log(message[1], message[2])
                    
        except queue.Empty:
            pass    # Si no hay mensajes no hacemos nada
        finally:
            self.after(100, self.process_gui_queue) # Comprobamos nuevos mensajes en la cola cada 100ms

    def _update_debug_log(self, text):
        """Appends text to the debug log display."""
        self.debug_log_display.configure(state="normal")
        self.debug_log_display.insert("end", text + "\n")
        self.debug_log_display.configure(state="disabled")
        self.debug_log_display.see("end")

    # --- ROBOT FRAMEWORK LOGIC ---
    def _read_test_names(self, robot_file_path):
        try:
            suite = TestSuiteBuilder().build(robot_file_path)
            return [test.name for test in suite.tests]
        except Exception as e:
            print(f"Error reading {robot_file_path}: {e}")
            return []

    def _discover_and_load_tests(self, directory):
        if not os.path.isdir(directory):
            os.makedirs(directory)
            with open(os.path.join(directory, "example_tests.robot"), "w") as f:
                f.write("*** Settings ***\nLibrary    OperatingSystem\n\n*** Test Cases ***\nExample Test\n    Log To Console    Hello from example test\n")
        search_pattern = os.path.join(directory, '*.robot')
        robot_files = glob.glob(search_pattern)
        return {file: self._read_test_names(file) for file in robot_files}

    def _find_test_file(self, test_name, preferred_filename=None):
        """Finds the .robot file that contains a specific test case, optionally in a preferred file."""
        if preferred_filename:
            full_path = os.path.join(TEST_DIRECTORY, preferred_filename)
            tests_to_check = test_name if isinstance(test_name, list) else [test_name]
            if full_path in self.tests_data and all(t in self.tests_data[full_path] for t in tests_to_check):
                return full_path
        
        tests_to_check = test_name if isinstance(test_name, list) else [test_name]
        for file_path, test_list in self.tests_data.items():
            if all(t in test_list for t in tests_to_check):
                return file_path
        return None

    def _update_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)
        
    def _update_session_status(self, message, color):
        self.session_status_label.configure(text=f"Estado: {message}", text_color=color)

    def _update_snmp_listener_status(self, text, color):
        self.snmp_listener_status_label.configure(text=text, text_color=color)

    def _update_modules_display(self, module_list):
        for widget in self.modules_result_frame.winfo_children():
            widget.destroy()
        if not module_list:
            ctk.CTkLabel(self.modules_result_frame, text="Awaiting module list...").grid(row=0, column=0, padx=10, pady=10)
            return
        self.modules_result_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(self.modules_result_frame, text="Slot", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")
        ctk.CTkLabel(self.modules_result_frame, text="Módulo", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=(5, 10), sticky="w")
        for i, module_name in enumerate(module_list):
            text_color = "gray60" if module_name == "None" else ctk.ThemeManager.theme["CTkLabel"]["text_color"]
            ctk.CTkLabel(self.modules_result_frame, text=f"#{i}", text_color=text_color).grid(row=i + 1, column=0, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.modules_result_frame, text=module_name, anchor="w", text_color=text_color).grid(row=i + 1, column=1, padx=10, pady=2, sticky="ew")

    def _update_assigned_modules_display(self, tp1_info, tp2_info):
        """Thread-safe function to update the assigned modules display."""
        def set_entry_value(entry, value):
            entry.delete(0, "end")
            entry.insert(0, value)

        if tp1_info and isinstance(tp1_info, list) and len(tp1_info) == 2:
            self.tp1_module_label.configure(text=tp1_info[0])
            set_entry_value(self.tp1_tx_entry, tp1_info[1][0])
            set_entry_value(self.tp1_rx_entry, tp1_info[1][1])
        else:
            self.tp1_module_label.configure(text="-")
            set_entry_value(self.tp1_tx_entry, "")
            set_entry_value(self.tp1_rx_entry, "")

        if tp2_info and isinstance(tp2_info, list) and len(tp2_info) == 2:
            self.tp2_module_label.configure(text=tp2_info[0])
            set_entry_value(self.tp2_tx_entry, tp2_info[1][0])
            set_entry_value(self.tp2_rx_entry, tp2_info[1][1])
        else:
            self.tp2_module_label.configure(text="-")
            set_entry_value(self.tp2_tx_entry, "")
            set_entry_value(self.tp2_rx_entry, "")
            
    def _update_trap_display(self, trap_list):
        """Thread-safe function to update the trap display from a list of trap dicts."""
        self.trap_display.configure(state="normal")
        self.trap_display.delete("1.0", "end")
        if not trap_list:
            self.trap_display.insert("1.0", "No hay traps para mostrar.")
        else:
            formatted_text = ""
            for i, trap in enumerate(trap_list):
                formatted_text += f"--- Trap #{i+1} ---\n"
                for key, value in trap.items():
                    if key == 'varbinds_dict':
                        formatted_text += f"  {key}:\n"
                        for vk, vv in value.items():
                            formatted_text += f"    {vk}: {vv}\n"
                    else:
                        formatted_text += f"  {key}: {value}\n"
                formatted_text += "\n"
            self.trap_display.insert("1.0", formatted_text)
        self.trap_display.configure(state="disabled")
    
    def _update_full_snmp_config_display(self, listener):
        """Updates the entire SNMP configuration tab with data from the listener object."""
        
        def set_entry(entry, value):
            if value is not None:
                entry.delete(0, "end")
                entry.insert(0, str(value))

        def set_checkbox(cb, value):
            if value is not None:
                if value in [True, 'True', 'true', '1', 1]:
                    cb.select()
                else:
                    cb.deselect()
        
        set_checkbox(self.snmp_agent_state_cb, listener.snmp_agent_state)
        set_checkbox(self.traps_enable_state_cb, listener.traps_enable_state)
        set_entry(self.tpu_snmp_port_entry, listener.tpu_snmp_port)
        set_checkbox(self.snmp_v1_v2_enable_cb, listener.snmp_v1_v2_enable)
        set_entry(self.snmp_v1_v2_read_entry, listener.snmp_v1_v2_read)
        set_entry(self.snmp_v1_v2_set_entry, listener.snmp_v1_v2_set)
        set_checkbox(self.snmp_v3_enable_cb, listener.snmp_v3_enable)
        set_entry(self.snmp_v3_read_user_entry, listener.snmp_v3_read_user)
        set_entry(self.snmp_v3_read_pass_entry, listener.snmp_v3_read_pass)
        set_entry(self.snmp_v3_read_auth_entry, listener.snmp_v3_read_auth)
        set_entry(self.snmp_v3_write_user_entry, listener.snmp_v3_write_user)
        set_entry(self.snmp_v3_write_pass_entry, listener.snmp_v3_write_pass)
        set_entry(self.snmp_v3_write_auth_entry, listener.snmp_v3_write_auth)

        if listener.hosts_config and isinstance(listener.hosts_config, list):
            for i, host_data in enumerate(listener.hosts_config):
                if i < len(self.host_widgets):
                    widgets = self.host_widgets[i]
                    if len(host_data) == 4:
                        set_checkbox(widgets['enable'], host_data[0] == '1')
                        set_entry(widgets['ip'], host_data[1])
                        set_entry(widgets['port'], host_data[2])
                        mode_str = self.trap_mode_map_rev.get(str(host_data[3]), "V.2c Trap")
                        widgets['mode'].set(mode_str)
        
        self._toggle_snmp_config_visibility()


    def _update_command_assignment_grids(self, command_ranges, num_inputs, num_outputs):
        """Dynamically builds the checkbox grids for command assignment, including logic controls."""
        for widget in self.tx_grid_frame.winfo_children(): widget.destroy()
        for widget in self.rx_grid_frame.winfo_children(): widget.destroy()
        self.tx_checkboxes.clear()
        self.rx_checkboxes.clear()
        self.tx_logic_checkboxes.clear()
        self.rx_logic_checkboxes.clear()

        if not command_ranges or len(command_ranges) < 10:
            ctk.CTkLabel(self.tx_grid_frame, text="Consulte la configuración para ver la tabla.").pack()
            ctk.CTkLabel(self.rx_grid_frame, text="Consulte la configuración para ver la tabla.").pack()
            self.tx_tp1_header_label.configure(text="Teleprotection (1): ...")
            self.tx_tp2_header_label.configure(text="Teleprotection (2): ...")
            self.rx_tp1_header_label.configure(text="Teleprotection (1): ...")
            self.rx_tp2_header_label.configure(text="Teleprotection (2): ...")
            return
        
        tp1_name, tp2_name, tp1_min_in, tp1_max_in, tp1_min_out, tp1_max_out, tp2_min_in, tp2_max_in, tp2_min_out, tp2_max_out = command_ranges
        self.tx_tp1_header_label.configure(text=f"Teleprotection (1)    {tp1_name}    Commands TX    {tp1_min_in} - {tp1_max_in}")
        self.tx_tp2_header_label.configure(text=f"Teleprotection (2)    {tp2_name}    Commands TX    {tp2_min_in} - {tp2_max_in}")
        self.rx_tp1_header_label.configure(text=f"Teleprotection (1)    {tp1_name}    Commands RX    {tp1_min_out} - {tp1_max_out}")
        self.rx_tp2_header_label.configure(text=f"Teleprotection (2)    {tp2_name}    Commands RX    {tp2_min_out} - {tp2_max_out}")
        
        max_cmd_tx = max(int(tp1_max_in), int(tp2_max_in))
        max_cmd_rx = max(int(tp1_max_out), int(tp2_max_out))
        
        self._build_grid(self.tx_grid_frame, "Inp", num_inputs, max_cmd_tx, self.tx_checkboxes)
        
        logic_label_tx = ctk.CTkLabel(self.tx_grid_frame, text="OR=On; AND=Off", font=ctk.CTkFont(size=11))
        logic_label_tx.grid(row=num_inputs + 1, column=0, padx=(5, 10), pady=5, sticky="e")
        for c in range(max_cmd_tx):
            checkbox = ctk.CTkCheckBox(self.tx_grid_frame, text="", width=16)
            checkbox.grid(row=num_inputs + 1, column=c + 1, padx=2, pady=5)
            self.tx_logic_checkboxes.append(checkbox)
            
        self._build_grid(self.rx_grid_frame, "Out", num_outputs, max_cmd_rx, self.rx_checkboxes)
        
        logic_label_rx = ctk.CTkLabel(self.rx_grid_frame, text="OR = On\nAND = Off", font=ctk.CTkFont(weight="bold", size=10))
        logic_label_rx.grid(row=0, column=max_cmd_rx + 1, padx=15, pady=2)
        for r in range(num_outputs):
            checkbox = ctk.CTkCheckBox(self.rx_grid_frame, text="", width=16)
            checkbox.grid(row=r + 1, column=max_cmd_rx + 1, padx=15, pady=1)
            self.rx_logic_checkboxes.append(checkbox)

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
            
    def _update_input_activation_display(self, state, input_list):
        """Dynamically builds the checkboxes for input activation."""
        if self.activation_timer:
            self.after_cancel(self.activation_timer)
            self.activation_timer = None
            
        for widget in self.inputs_scroll_frame.winfo_children():
            widget.destroy()
        self.input_activation_checkboxes.clear()

        self.inputs_are_active = state in [True, 'True', '1', 1]

        if self.inputs_are_active:
            self.input_activation_status_label.configure(text="Estado: Activo", text_color="green")
        else:
            self.input_activation_status_label.configure(text="Estado: Inactivo", text_color="orange")

        if not input_list:
            ctk.CTkLabel(self.inputs_scroll_frame, text="No se encontraron entradas o están inactivas.").pack(pady=10)
            return
        
        self.inputs_scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for i, input_state in enumerate(input_list):
            is_checked = (input_state == '1' or input_state == 1)
            cb = ctk.CTkCheckBox(self.inputs_scroll_frame, text=f"Entrada {i+1}")
            if is_checked:
                cb.select()
            cb.grid(row=i // 4, column=i % 4, padx=10, pady=5, sticky="w")
            self.input_activation_checkboxes.append(cb)
            
    def _start_activation_timer(self, duration_seconds):
        """Starts a countdown timer that updates the status label."""
        if self.activation_timer:
            self.after_cancel(self.activation_timer)
        
        self._update_countdown(duration_seconds)

    def _update_countdown(self, remaining_seconds):
        """Updates the countdown label each second."""
        if remaining_seconds > 0:
            self.input_activation_status_label.configure(text=f"Estado: Activo (finaliza en {remaining_seconds}s)", text_color="green")
            self.activation_timer = self.after(1000, self._update_countdown, remaining_seconds - 1)
        else:
            self.input_activation_status_label.configure(text="Estado: Inactivo", text_color="orange")
            self.inputs_are_active = False
            self.activation_timer = None
            for cb in self.input_activation_checkboxes:
                cb.deselect()
                
    def _handle_program_inputs_success(self, activate_deactivate, duration, inputs_list):
        """Handles the GUI update after a successful input activation/deactivation."""
        is_activating = (activate_deactivate == "1")
        self.inputs_are_active = is_activating

        if is_activating:
            for i, cb in enumerate(self.input_activation_checkboxes):
                if i < len(inputs_list):
                    if inputs_list[i] == 1:
                        cb.select()
                    else:
                        cb.deselect()
            
            if duration != "0":
                self._start_activation_timer(int(duration))
            else:
                self.input_activation_status_label.configure(text="Estado: Activo", text_color="green")
        else:
            self.input_activation_status_label.configure(text="Estado: Inactivo", text_color="orange")
            if self.activation_timer:
                self.after_cancel(self.activation_timer)
                self.activation_timer = None
            for cb in self.input_activation_checkboxes:
                cb.deselect()
                
    def _update_chrono_log_display(self, log_content):
        """Updates the chronological register display."""
        self.chrono_log_display.configure(state="normal")
        self.chrono_log_display.delete("1.0", "end")

        if isinstance(log_content, list) and log_content:
            formatted_lines = []
            for entry in log_content:
                ts = entry.get('timestamp', 'N/A')
                event = entry.get('alarm_event', 'N/A')
                formatted_lines.append(f"Timestamp: {ts} | Evento: {event}")
            log_text = "\n".join(formatted_lines)
            self.chrono_log_display.insert("1.0", log_text)
        elif isinstance(log_content, str) and log_content:
            self.chrono_log_display.insert("1.0", log_content)
        else:
            self.chrono_log_display.insert("1.0", "No se recuperaron entradas del registro o está vacío.")

        self.chrono_log_display.configure(state="disabled")

    def _update_alignment_states(self, listener):
        """Updates the status labels, module names, and types in the Alignment tab."""
        if listener.loop_state_1 is not None:
            self._update_alignment_row_ui(self.loop1_widgets, listener.loop_state_1 in ['1', 1, 'True', True], is_loop=True)
        if listener.loop_module_name_1 is not None:
            self.loop1_widgets['module_label'].configure(text=f"Módulo: {listener.loop_module_name_1}")
        if listener.loop_type_1 is not None:
            type_str = self.loop_type_map_rev.get(str(listener.loop_type_1), "NONE")
            self.loop1_widgets['type_combo'].set(type_str)

        if listener.loop_state_2 is not None:
            self._update_alignment_row_ui(self.loop2_widgets, listener.loop_state_2 in ['1', 1, 'True', True], is_loop=True)
        if listener.loop_module_name_2 is not None:
            self.loop2_widgets['module_label'].configure(text=f"Módulo: {listener.loop_module_name_2}")
        if listener.loop_type_2 is not None:
            type_str = self.loop_type_map_rev.get(str(listener.loop_type_2), "NONE")
            self.loop2_widgets['type_combo'].set(type_str)

        if listener.blocking_state_1 is not None:
            self._update_alignment_row_ui(self.blocking1_widgets, listener.blocking_state_1 in ['1', 1, 'True', True], is_loop=False)
        if listener.blocking_module_name_1 is not None:
            self.blocking1_widgets['module_label'].configure(text=f"Módulo: {listener.blocking_module_name_1}")

        if listener.blocking_state_2 is not None:
            self._update_alignment_row_ui(self.blocking2_widgets, listener.blocking_state_2 in ['1', 1, 'True', True], is_loop=False)
        if listener.blocking_module_name_2 is not None:
            self.blocking2_widgets['module_label'].configure(text=f"Módulo: {listener.blocking_module_name_2}")
    
    def _update_ibtu_full_config_display(self, listener):
        """Updates the entire IBTU ByTones tab with data from the listener object."""
        self._update_ibtu_tones_table(self.ibtu_tx_tone_widgets, listener.ibtu_tx_tones, is_tx=True)
        self._update_ibtu_tones_table(self.ibtu_rx_tone_widgets, listener.ibtu_rx_tones, is_tx=False)

        if listener.ibtu_tx_scheme is not None:
            scheme_text = self.ibtu_scheme_map_rev.get(str(listener.ibtu_tx_scheme), "2+2 (1)")
            self.ibtu_tx_tone_widgets['scheme_combo'].set(scheme_text)
        
        if self.ibtu_tx_table_widgets:
            first_tone_app_type = self.ibtu_tx_table_widgets[0]['app_type'].get()
            self._update_guard_tone_options(first_tone_app_type, self.ibtu_tx_tone_widgets['guard_combo'])

        if listener.ibtu_tx_guard_freq:
            self.ibtu_tx_tone_widgets['guard_combo'].set(listener.ibtu_tx_guard_freq)

        if listener.ibtu_rx_scheme is not None:
            scheme_text = self.ibtu_scheme_map_rev.get(str(listener.ibtu_rx_scheme), "2+2 (1)")
            self.ibtu_rx_tone_widgets['scheme_combo'].set(scheme_text)

        if self.ibtu_rx_table_widgets:
            first_tone_app_type = self.ibtu_rx_table_widgets[0]['app_type'].get()
            self._update_guard_tone_options(first_tone_app_type, self.ibtu_rx_tone_widgets['guard_combo'])

        if listener.ibtu_rx_guard_freq:
            self.ibtu_rx_tone_widgets['guard_combo'].set(listener.ibtu_rx_guard_freq)

    # --- Test Execution Threads ---
    def _run_list_modules_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_list_modules_test, daemon=True).start()

    def _run_view_assigned_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_view_assigned_test, daemon=True).start()

    def _run_assign_modules_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_assign_modules_test, daemon=True).start()

    def _run_program_commands_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_commands_test, daemon=True).start()

    def _run_configure_timezone_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_configure_timezone_test, daemon=True).start()

    def _run_log_command_info_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_log_command_info_test, daemon=True).start()

    def _run_program_assignments_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_assignments_test, daemon=True).start()
        
    def _run_retrieve_snmp_config_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_snmp_config, daemon=True).start()

    def _run_execute_snmp_config_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_execute_snmp_config, daemon=True).start()
        
    def _run_retrieve_inputs_state_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_inputs_state, daemon=True).start()

    def _run_program_inputs_activation_thread(self):
        """Validates the requested action and then starts the thread to run the test."""
        self.run_button_state(is_running=True)

        if self.inputs_are_active is None:
            self.gui_queue.put(('main_status', "Error: Consulte primero el estado de las entradas.", "red"))
            self.run_button_state(is_running=False)
            return

        action_to_perform = self.activation_mode_var.get()

        if action_to_perform == "activate" and self.inputs_are_active:
            self.gui_queue.put(('main_status', "Aviso: Las entradas ya se encuentran activas.", "orange"))
            self.run_button_state(is_running=False)
            return

        if action_to_perform == "deactivate" and not self.inputs_are_active:
            self.gui_queue.put(('main_status', "Aviso: Las entradas ya se encuentran inactivas.", "orange"))
            self.run_button_state(is_running=False)
            return
        
        threading.Thread(target=self._execute_program_inputs_activation, daemon=True).start()
        
    def _run_retrieve_chrono_log_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_chrono_log, daemon=True).start()

    def _run_clear_chrono_log_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_clear_chrono_log, daemon=True).start()

    def _run_capture_last_entries_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_capture_last_entries, daemon=True).start()

    def _run_refresh_alignment_states_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_refresh_alignment_states, daemon=True).start()

    def _run_program_loop_thread(self, tp_number, activate):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_loop, args=(tp_number, activate), daemon=True).start()

    def _run_program_blocking_thread(self, tp_number, activate):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_blocking, args=(tp_number, activate), daemon=True).start()
        
    def _start_snmp_listener_thread(self):
        self.run_button_state(is_running=True)
        self.snmp_listener_thread = threading.Thread(target=self._execute_start_listener, daemon=True)
        self.snmp_listener_thread.start()

    def _stop_snmp_listener_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_stop_listener, daemon=True).start()

    def _run_retrieve_ibtu_config_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_ibtu_config, daemon=True).start()

    def _run_program_ibtu_s1_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_ibtu_s1, daemon=True).start()

    def _run_program_ibtu_s2_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_ibtu_s2, daemon=True).start()

    def _run_program_ibtu_s3_thread(self):
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_ibtu_s3, daemon=True).start()

    def run_button_state(self, is_running):
        session_active = self.browser_process is not None
  
        # Main Logic:
        # Button States: Enabled if there's session connected and there's nothing running
        action_state = "normal" if session_active and not is_running else "disabled"
        
            # --- LÓGICA CENTRALIZADA DE ESTADOS ---
        # Estado para botones que deben estar ACTIVOS cuando NO se está ejecutando nada (idle).
        idle_state = "normal" if session_active and not is_running else "disabled"
        # Estado para botones que deben estar ACTIVOS SÓLO MIENTRAS se está ejecutando algo (running).
        running_state = "normal" if session_active and is_running else "disabled"
        
        
        
        
        if is_running:
            self.gui_queue.put(('main_status', "Status: Running...", "orange"))

        # Enable/Disable Session Buttons
        self.connect_button.configure(state="disabled" if session_active else "normal") # Bloqueamos boton conectar si ya hay sesión, sino normal
        self.disconnect_button.configure(state="normal" if session_active else "disabled") # Habilitamos boton desconectar si hay sesión, sino bloqueado

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
        if hasattr(self, 'capture_last_entries_button'): self.capture_last_entries_button.configure(state=idle_state)
        if hasattr(self, 'clear_chrono_button'): self.clear_chrono_button.configure(state=idle_state)
        if hasattr(self, 'query_snmp_config_button'): self.query_snmp_config_button.configure(state=idle_state)
        if hasattr(self, 'program_snmp_config_button'): self.program_snmp_config_button.configure(state=idle_state)
        if hasattr(self, 'refresh_alignment_button'): self.refresh_alignment_button.configure(state=idle_state)
        
    # Scheduler Buttons
        if hasattr(self, 'run_sequence_button'):
            self.run_sequence_button.configure(state=idle_state) # El botón de ejecutar usa 'idle_state'. Solo podremos darle al boton cuando no haya nada corriendo.
        if hasattr(self, 'stop_sequence_button'):
            self.stop_sequence_button.configure(state=running_state) # El botón de detener usa 'running_state'. Solo podemos darle al boton cuando haya algo corriendo (por ejemplo los tests del mismo planificador).
        
    # SNMP listener Buttons
        # Listener States: They have to be disabled if theres something running
        if hasattr(self, 'start_listener_button'): self.start_listener_button.configure(state=idle_state)
        if hasattr(self, 'stop_listener_button'): self.stop_listener_button.configure(state=idle_state)
        
        # Traps Visualizer State: They only need an active session
        viewer_state = "normal" if session_active else "disabled"   # Lo hacemos ya que tenemos que poder ver traps aunque haya algo corriendo
        if hasattr(self, 'show_all_traps_button'): self.show_all_traps_button.configure(state=viewer_state)
        if hasattr(self, 'filter_traps_button'): self.filter_traps_button.configure(state=viewer_state)
        if hasattr(self, 'reset_traps_button'): self.reset_traps_button.configure(state=viewer_state)

        for btn in self.log_buttons:    # Para los botones de log, solo necesitan que no haya algo corriendo. No es necesario sesion activa
            btn.configure(state="normal" if not is_running else "disabled")

    # Widgets Logic for Alignment Tab (Activate Inputs...)
        if is_running: # Para evitar que intentemos hacer cambios mientras algo está corriendo, bloqueamos todo
            for widgets in [self.loop1_widgets, self.loop2_widgets, self.blocking1_widgets, self.blocking2_widgets]:
                if widgets:
                    widgets['activate_button'].configure(state="disabled")
                    widgets['deactivate_button'].configure(state="disabled")
                    widgets['duration_combo'].configure(state="disabled")
                    if 'type_combo' in widgets:
                        widgets['type_combo'].configure(state="disabled")
        elif session_active:
                 for widgets_dict, is_loop_flag in [(self.loop1_widgets, True), (self.loop2_widgets, True), 
                                                     (self.blocking1_widgets, False), (self.blocking2_widgets, False)]:
                    if widgets_dict:
                        is_active = "Activo" in widgets_dict['status_label'].cget("text")
                        self._update_alignment_row_ui(widgets_dict, is_active, is_loop_flag)
        else:
                 for widgets in [self.loop1_widgets, self.loop2_widgets, self.blocking1_widgets, self.blocking2_widgets]:
                    if widgets:
                        widgets['activate_button'].configure(state="disabled")
                        widgets['deactivate_button'].configure(state="disabled")
                        widgets['duration_combo'].configure(state="disabled")
                        if 'type_combo' in widgets:
                            widgets['type_combo'].configure(state="disabled")

    
    # --- Test Execution Logic ---
    def _execute_list_modules_test(self):
        self._run_robot_test(
            test_name="List Detected Modules",
            on_success=lambda listener: self.gui_queue.put(('modules_display', listener.modules if listener.modules is not None else [])),
            on_pass_message="Modules listed successfully!",
            on_fail_message="Failed to list modules!"
        )

    def _execute_view_assigned_test(self):
        self._run_robot_test(
            test_name="List assigned Modules and Commands assigned",
            on_success=lambda listener: self.gui_queue.put(('assigned_modules_display', listener.tp1_info, listener.tp2_info)),
            on_pass_message="Assigned modules info retrieved!",
            on_fail_message="Failed to retrieve assigned modules!"
        )
    
    def _execute_log_command_info_test(self):
        self._run_robot_test(
            test_name="Log and Save Teleprotection Commands and Inputs/Outputs",
            preferred_filename="Test2_CommandAssign.robot",
            on_success=lambda listener: self.gui_queue.put(('command_assignment_grids', listener.command_ranges, listener.num_inputs, listener.num_outputs)),
            on_pass_message="Configuration data retrieved!",
            on_fail_message="Failed to retrieve configuration data!"
        )

    def _execute_assign_modules_test(self):
        tp1 = self.entry_tp1.get()
        tp2 = self.entry_tp2.get()
        if not tp1 or not tp2:
            self.gui_queue.put(('main_status', "Error: Please provide values for TP1 and TP2.", "red"))
            self.run_button_state(is_running=False)
            return
        
        self._run_robot_test(
            test_name="Assign Prioritized Detected Modules",
            variables=[f"TP1:{tp1}", f"TP2:{tp2}"],
            on_pass_message="Modules assigned successfully!",
            on_fail_message="Failed to assign modules!"
        )
    
    def _execute_program_commands_test(self):
        """Executes the 'Command Number Assignments' test."""
        tp1_tx = self.tp1_tx_entry.get()
        tp1_rx = self.tp1_rx_entry.get()
        tp2_tx = self.tp2_tx_entry.get()
        tp2_rx = self.tp2_rx_entry.get()

        if not all(v.isdigit() for v in [tp1_tx, tp1_rx, tp2_tx, tp2_rx]):
            self.gui_queue.put(('main_status', "Error: Todos los campos de órdenes deben ser numéricos.", "red"))
            self.run_button_state(is_running=False)
            return

        self._run_robot_test(
            test_name="Command Number Assignments",
            variables=[
                f"TP1_TX_Command_Number_NUM_COMMANDS:{tp1_tx}",
                f"TP1_RX_Command_Number_NUM_COMMANDS:{tp1_rx}",
                f"TP2_TX_Command_Number_NUM_COMMANDS:{tp2_tx}",
                f"TP2_RX_Command_Number_NUM_COMMANDS:{tp2_rx}"
            ],
            on_pass_message="Número de órdenes programado correctamente!",
            on_fail_message="Fallo al programar el número de órdenes!"
        )

    def _execute_configure_timezone_test(self):
        """Executes the 'Configure Display Time Zone' test."""
        selected_tz_name = self.timezone_selector.get()
        tz_value = self.timezone_map.get(selected_tz_name)

        self._run_robot_test(
            test_name="Open_BasicConfiguration+Configure Display Time Zone",
            variables=[f"Time_zone:{tz_value}"],
            on_pass_message=f"Zona horaria configurada a {selected_tz_name}!",
            on_fail_message="Fallo al configurar la zona horaria!"
        )
        
    def _execute_retrieve_snmp_config(self):
        """Runs the test to get current SNMP configuration."""
        self._run_robot_test(
            test_name="Retrieve Full SNMP Configuration",
            preferred_filename="Test3_SNMP.robot",
            on_success=lambda listener: self.gui_queue.put(('full_snmp_config_display', listener)),
            on_pass_message="Configuración SNMP consultada con éxito!",
            on_fail_message="Fallo al consultar la configuración SNMP!"
        )

    def _execute_execute_snmp_config(self):
        """Reads the GUI fields and runs the test to program SNMP settings."""
        
        hosts_config_list = []
        for host in self.host_widgets:
            host_enable = '1' if host['enable'].get() == 1 else '0'
            ip_address = host['ip'].get()
            port = host['port'].get()
            trap_mode_str = host['mode'].get()
            trap_mode = self.trap_mode_map.get(trap_mode_str, '1')
            hosts_config_list.append([host_enable, ip_address, port, trap_mode])

        hosts_config_str = json.dumps(hosts_config_list)

        variables = [
            f"SNMP_AGENT_STATE:{self.snmp_agent_state_cb.get()}",
            f"TRAPS_ENABLE_STATE:{self.traps_enable_state_cb.get()}",
            f"TPU_SNMP_PORT:{self.tpu_snmp_port_entry.get()}",
            f"SNMP_V1_V2_ENABLE:{self.snmp_v1_v2_enable_cb.get()}",
            f"SNMP_V1_V2_READ:{self.snmp_v1_v2_read_entry.get()}",
            f"SNMP_V1_V2_SET:{self.snmp_v1_v2_set_entry.get()}",
            f"SNMP_V3_ENABLE:{self.snmp_v3_enable_cb.get()}",
            f"SNMP_V3_READ_USER:{self.snmp_v3_read_user_entry.get()}",
            f"SNMP_V3_READ_PASS:{self.snmp_v3_read_pass_entry.get()}",
            f"SNMP_V3_READ_AUTH:{self.snmp_v3_read_auth_entry.get()}",
            f"SNMP_V3_WRITE_USER:{self.snmp_v3_write_user_entry.get()}",
            f"SNMP_V3_WRITE_PASS:{self.snmp_v3_write_pass_entry.get()}",
            f"SNMP_V3_WRITE_AUTH:{self.snmp_v3_write_auth_entry.get()}",
            f"HOSTS_CONFIG_STR:{hosts_config_str}"
        ]

        self._run_robot_test(
            test_name="Execute Full SNMP Configuration",
            preferred_filename="Test3_SNMP.robot",
            variables=variables,
            on_pass_message="Configuración SNMP programada con éxito!",
            on_fail_message="Fallo al programar la configuración SNMP!"
        )

    def _execute_program_assignments_test(self):
        """Reads the checkbox grids and runs the assignment test."""
        if not self.tx_checkboxes and not self.rx_checkboxes:
            self.gui_queue.put(('main_status', "Error: Primero consulta la configuración para generar las tablas.", "red"))
            self.run_button_state(is_running=False)
            return
        tx_matrix = [[cb.get() for cb in row] for row in self.tx_checkboxes]
        rx_matrix = [[cb.get() for cb in row] for row in self.rx_checkboxes]
        tx_logic_list = [cb.get() for cb in self.tx_logic_checkboxes]
        rx_logic_list = [cb.get() for cb in self.rx_logic_checkboxes]
        
        self._run_robot_test(
            test_name="Program Command Assignments",
            preferred_filename="Test2_CommandAssign.robot",
            variables=[
                f"tx_matrix_str:{str(tx_matrix)}",
                f"rx_matrix_str:{str(rx_matrix)}",
                f"tx_list_str:{str(tx_logic_list)}",
                f"rx_list_str:{str(rx_logic_list)}"
            ],
            on_pass_message="Asignaciones programadas correctamente!",
            on_fail_message="Fallo al programar las asignaciones!"
        )
        
    def _execute_retrieve_inputs_state(self):
        """Runs the test to get the current state of the inputs."""
        self._run_robot_test(
            test_name="Retrieve Inputs Activation State",
            preferred_filename="Test4_Alignment.robot",
            on_success=lambda listener: self.gui_queue.put(('update_input_activation_display', listener.input_activation_state, listener.input_info)),
            on_pass_message="Estado de entradas consultado con éxito!",
            on_fail_message="Fallo al consultar el estado de las entradas."
        )

    def _execute_program_inputs_activation(self):
        """Gathers data from the GUI and runs the input activation test. Assumes validation has passed."""
        activate_deactivate = "1" if self.activation_mode_var.get() == "activate" else "0"
        duration_str = self.duration_combobox.get()
        duration = self.duration_map.get(duration_str, "0")
        
        inputs_list = [1 if cb.get() == 1 else 0 for cb in self.input_activation_checkboxes]
        inputs_list_str = json.dumps(inputs_list)

        variables = [
            f"ACTIVATE_DEACTIVATE:{activate_deactivate}",
            f"DURATION:{duration}",
            f"INPUTS_LIST:{inputs_list_str}"
        ]

        def on_success_callback(listener):
            self.gui_queue.put(('program_inputs_success', activate_deactivate, duration, inputs_list))

        self._run_robot_test(
            test_name="Input Activation",
            preferred_filename="Test4_Alignment.robot",
            variables=variables,
            on_success=on_success_callback,
            on_pass_message="Operación de activación de entradas completada.",
            on_fail_message="Fallo en la operación de activación de entradas."
        )
        
    def _execute_retrieve_chrono_log(self):
        """Runs the test to get the full chronological register."""
        self._run_robot_test(
            test_name="Retrieve Chronological Register",
            preferred_filename="Chronological_Register.robot",
            on_success=lambda listener: self.gui_queue.put(('update_chrono_log_display', listener.chronological_log)),
            on_pass_message="Registro cronológico consultado.",
            on_fail_message="Fallo al consultar el registro cronológico."
        )

    def _execute_clear_chrono_log(self):
        """Runs the test to clear the chronological register."""
        def on_success_callback(listener):
            self.gui_queue.put(('update_chrono_log_display', "Registro cronológico borrado."))

        self._run_robot_test(
            test_name="Delete Chronological Register",
            preferred_filename="Chronological_Register.robot",
            on_success=on_success_callback,
            on_pass_message="Registro cronológico borrado con éxito.",
            on_fail_message="Fallo al borrar el registro cronológico."
        )

    def _execute_capture_last_entries(self):
        """Runs the test to capture the last N entries from the log."""
        num_entries = self.num_entries_entry.get()
        event_filter = self.event_filter_entry.get()
        order = self.chrono_order_combobox.get()
        order_bool = "True" if order == "Ascendente" else "False"

        if not num_entries.isdigit() or int(num_entries) <= 0:
            self.gui_queue.put(('main_status', "Error: 'Número de Entradas' debe ser un número positivo.", "red"))
            self.run_button_state(is_running=False)
            return

        variables = [
            f"EXPECTED_NUM_ENTRIES:{num_entries}",
            f"EVENT_ALARM_FILTER:{event_filter}",
            f"CHRONO_ORDER:{order_bool}"
        ]

        self._run_robot_test(
            test_name="Capture Last Chronological Log Entries",
            preferred_filename="Chronological_Register.robot",
            variables=variables,
            on_success=lambda listener: self.gui_queue.put(('update_chrono_log_display', listener.chronological_log)),
            on_pass_message=f"Capturadas las últimas {num_entries} entradas.",
            on_fail_message="Fallo al capturar las últimas entradas."
        )

    def _execute_refresh_alignment_states(self):
        """Runs a single test to get all loop and blocking states."""
        self._run_robot_test(
            test_name="Current Loop and Blocking State",
            preferred_filename="Test4_Alignment.robot",
            on_success=lambda listener: self.gui_queue.put(('update_alignment_states', listener)),
            on_pass_message="Estados de alineación consultados.",
            on_fail_message="Fallo al consultar estados de alineación."
        )

    def _execute_program_loop(self, tp_number, activate):
        """Gathers data and runs the Program Teleprotection Loop test."""
        activate_deactivate = '1' if activate else '0'
        
        widgets = self._get_alignment_widgets(tp_number, is_loop=True)
        
        is_currently_active = "Activo" in widgets['status_label'].cget("text")
        if (activate and is_currently_active) or (not activate and not is_currently_active):
            status = "activo" if is_currently_active else "inactivo"
            self.gui_queue.put(('main_status', f"Aviso: El bucle TP{tp_number} ya está {status}.", "orange"))
            self.gui_queue.put(('enable_buttons', None))
            return

        loop_type_str = widgets['type_combo'].get()
        duration_str = widgets['duration_combo'].get()
        
        loop_type = self.loop_type_map.get(loop_type_str, '0')
        duration = self.duration_map.get(duration_str, '0')

        variables = [
            f"LOOP_TELEPROTECTION_NUMBER:{tp_number}",
            f"ACTIVATE_DEACTIVATE_LOOP:{activate_deactivate}",
            f"LOOP_TYPE:{loop_type}",
            f"LOOP_DURATION:{duration}"
        ]

        def on_success_callback(listener):
            self.gui_queue.put(('program_alignment_success', tp_number, True, activate, duration))

        self._run_robot_test(
            test_name="Program Teleprotection Loop",
            preferred_filename="Test4_Alignment.robot",
            variables=variables,
            on_success=on_success_callback,
            on_pass_message=f"Bucle TP{tp_number} programado con éxito.",
            on_fail_message=f"Fallo al programar bucle TP{tp_number}."
        )

    def _execute_program_blocking(self, tp_number, activate):
        """Gathers data and runs the Program Teleprotection Blocking test."""
        activate_deactivate = '1' if activate else '0'

        widgets = self._get_alignment_widgets(tp_number, is_loop=False)

        is_currently_active = "Activo" in widgets['status_label'].cget("text")
        if (activate and is_currently_active) or (not activate and not is_currently_active):
            status = "activo" if is_currently_active else "inactivo"
            self.gui_queue.put(('main_status', f"Aviso: El bloqueo TP{tp_number} ya está {status}.", "orange"))
            self.gui_queue.put(('enable_buttons', None))
            return

        duration_str = widgets['duration_combo'].get()
        duration = self.duration_map.get(duration_str, '0')

        variables = [
            f"BLOCKING_TELEPROTECTION_NUMBER:{tp_number}",
            f"ACTIVATE_DEACTIVATE_BLOCKING:{activate_deactivate}",
            f"BLOCKING_DURATION:{duration}"
        ]
        
        def on_success_callback(listener):
            self.gui_queue.put(('program_alignment_success', tp_number, False, activate, duration))

        self._run_robot_test(
            test_name="Program Teleprotection Blocking",
            preferred_filename="Test4_Alignment.robot",
            variables=variables,
            on_success=on_success_callback,
            on_pass_message=f"Bloqueo TP{tp_number} programado con éxito.",
            on_fail_message=f"Fallo al programar bloqueo TP{tp_number}."
        )

    def _execute_start_listener(self):
        """Starts the SNMP trap listener using the Python library directly."""
        try:
            import asyncio
            asyncio.set_event_loop(asyncio.new_event_loop())
            
            ip = self.snmp_ip_entry.get()
            port = int(self.snmp_port_entry.get())
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            mib_dir = os.path.join(script_dir, "compiled_mibs")
            mib_uri = Path(mib_dir).as_uri()
            
            if not os.path.isdir(mib_dir):
                error_msg = f"Error: Directorio MIBs no encontrado en {mib_dir}"
                self.gui_queue.put(('main_status', error_msg, "red"))
                self.gui_queue.put(('enable_buttons', None))
                return
            
            self.trap_receiver.start_trap_listener(listen_ip=ip, listen_port=port, mib_dirs_string=mib_uri)
            
            try:
                self.trap_receiver.load_mibs("DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB")
                self.gui_queue.put(('snmp_listener_status', "Listener: Ejecutando", "green"))
                self.gui_queue.put(('main_status', f"Listener SNMP iniciado en {ip}:{port}", "#2ECC71"))
            except Exception as e_mibs:
                error_msg = f"ADVERTENCIA: Error cargando MIBs: {repr(e_mibs)}"
                self.gui_queue.put(('main_status', error_msg, "orange"))

        except Exception as e_start:
            error_msg = f"Error al iniciar listener: {repr(e_start)}"
            print(f"!!! GUI ERROR (Start): {error_msg}")
            self.gui_queue.put(('main_status', error_msg, "red"))
            self.gui_queue.put(('snmp_listener_status', 'Listener: Error', 'red'))
        finally:
            self.gui_queue.put(('enable_buttons', None))

    def _execute_stop_listener(self):
        """Stops the SNMP trap listener."""
        try:
            self.trap_receiver.stop_trap_listener()
            self.gui_queue.put(('snmp_listener_status', 'Listener: Detenido', 'red'))
            self.gui_queue.put(('main_status', "Listener SNMP detenido.", "orange"))
        except Exception as e:
            self.gui_queue.put(('main_status', f"Error al detener listener: {e}", "red"))
        finally:
            self.gui_queue.put(('enable_buttons', None))

    def _show_all_traps(self):
        traps = self.trap_receiver.get_all_raw_received_traps()
        self._update_trap_display(traps)
        self._update_status("Traps actualizados.", "white")

    def _filter_traps(self):
        filter_text = self.snmp_filter_entry.get()
        traps = self.trap_receiver.get_filtered_traps_by_text(filter_text)
        self._update_trap_display(traps)
        self._update_status(f"Mostrando traps filtrados por '{filter_text}'.", "white")

    def _reset_traps(self):
        self.trap_receiver.clear_all_received_traps()
        self._update_trap_display([])
        self._update_status("Traps borrados.", "white")

    def _execute_retrieve_ibtu_config(self):
        """Runs the test to get current IBTU ByTones configuration."""
        self._run_robot_test(
            test_name="Retrieve IBTU ByTones Full Configuration",
            preferred_filename="Module_IBTU_ByTones.robot",
            on_success=lambda listener: self.gui_queue.put(('update_ibtu_full_config', listener)),
            on_pass_message="Configuración IBTU consultada con éxito!",
            on_fail_message="Fallo al consultar la configuración IBTU."
        )

    def _execute_program_ibtu_s1(self):
        """Gathers data from the General section and runs the corresponding test."""
        try:
            rx_op_mode_str = self.ibtu_rx_op_mode.get()
            rx_op_mode = self.ibtu_rx_op_mode_map.get(rx_op_mode_str, "0")
            
            local_p = self.ibtu_local_periodicity.get()
            remote_p = self.ibtu_remote_periodicity.get()
            snr_act = self.ibtu_snr_activation.get()
            snr_deact = self.ibtu_snr_deactivation.get()

            if not all(v.isdigit() for v in [local_p, remote_p, snr_act, snr_deact]):
                self.gui_queue.put(('main_status', "Error: Todos los campos de la sección General deben ser numéricos.", "red"))
                self.run_button_state(is_running=False)
                return

            variables = [
                f"RX_OPERATION_MODE:{rx_op_mode}",
                f"LOCAL_PERIODICITY:{local_p}",
                f"REMOTE_PERIODICITY:{remote_p}",
                f"SNR_THRESHOLD_ACTIVATION:{snr_act}",
                f"SNR_THRESHOLD_DEACTIVATION:{snr_deact}"
            ]

            self._run_robot_test(
                test_name="Program IBTU ByTones S1 General",
                preferred_filename="Module_IBTU_ByTones.robot",
                variables=variables,
                on_pass_message="Sección General de IBTU programada con éxito.",
                on_fail_message="Fallo al programar la Sección General de IBTU."
            )
        except Exception as e:
            self.gui_queue.put(('main_status', f"Error preparando test IBTU S1: {e}", "red"))
            self.run_button_state(is_running=False)


    def _execute_program_ibtu_s2(self):
        """Gathers data from the Frequencies section and runs the corresponding test."""
        try:
            def process_tone_table(widgets_list, tone_widgets):
                if not widgets_list: return None, None, None, None
                
                scheme_text = tone_widgets['scheme_combo'].get()
                scheme_value = self.ibtu_scheme_map.get(scheme_text, "0")
                guard = tone_widgets['guard_combo'].get()
                
                app_type_list = []
                freq_list = []
                for row_widgets in widgets_list:
                    app_type_str = row_widgets['app_type'].get()
                    app_type = self.ibtu_app_type_map.get(app_type_str, "0")
                    app_type_list.append(app_type)
                    freq = row_widgets['freq'].get()
                    if not freq.isdigit():
                            raise ValueError(f"Frecuencia '{freq}' no es un valor numérico válido.")
                    freq_list.append(freq)
                    
                return scheme_value, guard, app_type_list, freq_list

            tx_scheme_val, tx_guard, tx_app_types, tx_freqs = process_tone_table(self.ibtu_tx_table_widgets, self.ibtu_tx_tone_widgets)
            if tx_app_types is None:
                self.gui_queue.put(('main_status', "Error: No hay datos en la tabla TX. Consulte primero.", "red"))
                self.run_button_state(is_running=False)
                return

            rx_scheme_val, rx_guard, rx_app_types, rx_freqs = process_tone_table(self.ibtu_rx_table_widgets, self.ibtu_rx_tone_widgets)
            if rx_app_types is None:
                self.gui_queue.put(('main_status', "Error: No hay datos en la tabla RX. Consulte primero.", "red"))
                self.run_button_state(is_running=False)
                return

            variables = [
                f"TX_SCHEME:{tx_scheme_val}",
                f"TX_GUARD_FREQUENCY:{tx_guard}",
                f"TX_APPLICATION_TYPE_LIST_STR:{json.dumps(tx_app_types)}",
                f"TX_FREQUENCY_LIST_STR:{json.dumps(tx_freqs)}",
                f"RX_SCHEME:{rx_scheme_val}",
                f"RX_GUARD_FREQUENCY:{rx_guard}",
                f"RX_APPLICATION_TYPE_LIST_STR:{json.dumps(rx_app_types)}",
                f"RX_FREQUENCY_LIST_STR:{json.dumps(rx_freqs)}"
            ]

            self._run_robot_test(
                test_name="Program IBTU ByTones S2 Frequencies",
                preferred_filename="Module_IBTU_ByTones.robot",
                variables=variables,
                on_pass_message="Frecuencias de IBTU programadas con éxito.",
                on_fail_message="Fallo al programar las Frecuencias de IBTU."
            )

        except ValueError as ve:
            self.gui_queue.put(('main_status', f"Error de validación: {ve}", "red"))
            self.run_button_state(is_running=False)
        except Exception as e:
            self.gui_queue.put(('main_status', f"Error preparando test IBTU S2: {e}", "red"))
            self.run_button_state(is_running=False)


    def _execute_program_ibtu_s3(self):
        """Gathers data from the Levels section and runs the corresponding test."""
        try:
            input_level = self.ibtu_input_level.get()
            power_boost = self.ibtu_power_boosting.get()
            output_level = self.ibtu_output_level.get()

            if not input_level or not power_boost or not output_level:
                self.gui_queue.put(('main_status', "Error: Todos los campos de Niveles son obligatorios.", "red"))
                self.run_button_state(is_running=False)
                return

            try:
                float(input_level)
                float(power_boost)
                float(output_level)
            except ValueError:
                self.gui_queue.put(('main_status', "Error: Los campos de Niveles deben ser numéricos.", "red"))
                self.run_button_state(is_running=False)
                return

            variables = [
                f"BY_TONES_INPUT_LEVEL:{input_level}",
                f"BY_TONES_POWER_BOOSTING:{power_boost}",
                f"BY_TONES_OUTPUT_LEVEL:{output_level}"
            ]

            self._run_robot_test(
                test_name="Program IBTU ByTones S3 Levels",
                preferred_filename="Module_IBTU_ByTones.robot",
                variables=variables,
                on_pass_message="Niveles de IBTU programados con éxito.",
                on_fail_message="Fallo al programar los Niveles de IBTU."
            )
        except Exception as e:
            self.gui_queue.put(('main_status', f"Error preparando test IBTU S3: {e}", "red"))
            self.run_button_state(is_running=False)

    def _run_robot_test(self, test_name, variables=None, on_success=None, on_pass_message="Test Passed!", on_fail_message="Test Failed!", preferred_filename=None, output_filename=None, suppress_gui_updates=False):
        """Generic function to run a robot test."""
        session_file_path = os.path.abspath("session.json")
        if not self.browser_process or not os.path.exists(session_file_path):
            self.gui_queue.put(('main_status', "Error: No hay una sesión activa. Por favor, conéctese primero.", "red"))
            self.gui_queue.put(('enable_buttons', None))
            return

        robot_script_path = self._find_test_file(test_name, preferred_filename=preferred_filename)
        if not robot_script_path:
            self.gui_queue.put(('main_status', f"Error: Test case '{test_name}' not found.", "red"))
            self.run_button_state(is_running=False)
            return

        ip = self.entry_ip.get()
        all_variables = [f"IP_ADDRESS:{ip}"]
        if variables:
            all_variables.extend(variables)


        output_file = output_filename if output_filename else "output.xml" # Para usar el nombre único
        result_code = -1 # Valor por defecto en caso de error

        listener = self.TestOutputListener(self)
        try:
            result_code = robot.run(
                robot_script_path,
                test=test_name,
                variable=all_variables,
                outputdir="test_results",
                output=output_file,
                log="log.html", report="report.html", 
                listener=listener,
                stdout=None, stderr=None
            )
            # Si el test pasó Y se proporcionó un callback 'on_success', lo ejecutamos. No lo ponemos dentro del siguiente if (como estaba antes) ya que queremos ejecutar las funciones de callback siempre, dentro del if not suppress_gui_updates: dejaríamos de ejecutar estas funciones cuando hacemos tests en el planificador)
            if result_code == 0 and on_success:
                on_success(listener)

            if not suppress_gui_updates: # Solo actualiza la GUI si no es una ejecución del planificador. 
                if result_code == 0:
                    self.gui_queue.put(('main_status', f"Status: {on_pass_message} (PASS)", "#2ECC71"))
                else:
                    self.gui_queue.put(('main_status', f"Status: {on_fail_message} (FAIL)", "#E74C3C"))
                
                
        except Exception as e:
            if not suppress_gui_updates:
                self.gui_queue.put(('main_status', f"Critical Error: {e}", "#E74C3C"))
                
        if not suppress_gui_updates:    
            self.gui_queue.put(('enable_buttons', None))
            
        return result_code
    
    def _start_browser_process_thread(self):
        """Starts the browser process in a separate thread."""
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_start_browser, daemon=True).start()

    def _execute_start_browser(self):
        """Executes start_browser.robot to open and maintain the browser session."""
        if self.browser_process:
            self.gui_queue.put(('main_status', "Aviso: Ya hay una sesión activa.", "orange"))
            self.gui_queue.put(('enable_buttons', None))
            return
        
        self.gui_queue.put(('session_status', "Conectando...", "orange"))
        
        session_file_path = os.path.abspath("session.json")
        if os.path.exists(session_file_path):
            os.remove(session_file_path)

        ip = self.entry_ip.get()
        command = [
            sys.executable, '-m', 'robot',
            '--outputdir', 'test_results',
            '--log', 'None', '--report', 'None',
            '--variable', f'IP_ADDRESS:{ip}',
            '--variable', f'SESSION_FILE_PATH:{session_file_path}',
            os.path.join(TEST_DIRECTORY, 'start_browser.robot')
        ]
        
        self.browser_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        session_file_found = False
        timeout = 50 # segundos
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(session_file_path):
                session_file_found = True
                break
            if self.browser_process.poll() is not None:
                break 
            time.sleep(0.5)

        if session_file_found:
            self.gui_queue.put(('session_status', "Conectado", "green"))
            self.gui_queue.put(('main_status', "Sesión iniciada. Listo para ejecutar acciones.", "white"))
        else:
            self.gui_queue.put(('session_status', "Error", "red"))
            self.gui_queue.put(('main_status', "Error: No se pudo iniciar la sesión. Revise la consola.", "red"))
            stdout, stderr = self.browser_process.communicate()
            print("--- STDOUT del proceso del navegador ---")
            print(stdout)
            print("--- STDERR del proceso del navegador ---")
            print(stderr)
            # Si el tiempo se agota, nos aseguramos de terminar el proceso para que no quede huérfano.
            if self.browser_process.poll() is None: # Si el proceso todavía está corriendo
                self.browser_process.terminate()
            self.browser_process = None

        self.gui_queue.put(('enable_buttons', None))

    def _stop_browser_process_thread(self):
        """Stops the browser process in a separate thread."""
        self.run_button_state(is_running=True)
        threading.Thread(target=self._execute_stop_browser, daemon=True).start()
        
    def _execute_stop_browser(self):
        """Terminates the browser process."""
        if self.browser_process:
            self.browser_process.terminate()
            self.browser_process = None
            session_file_path = os.path.abspath("session.json")
            if os.path.exists(session_file_path):
                os.remove(session_file_path)
            self.gui_queue.put(('session_status', "Desconectado", "orange"))
            self.gui_queue.put(('main_status', "Sesión del navegador cerrada.", "white"))
        else:
            self.gui_queue.put(('main_status', "Aviso: No hay ninguna sesión activa para cerrar.", "orange"))
        
        self.gui_queue.put(('enable_buttons', None))

    def on_closing(self):
        """Handles the window closing event to ensure cleanup."""
        if self.browser_process:
            self._execute_stop_browser()
        self.destroy()

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

    def _get_alignment_widgets(self, tp_number, is_loop):
        """Returns the widget dictionary for a given alignment row."""
        if is_loop:
            return self.loop1_widgets if tp_number == 1 else self.loop2_widgets
        else:
            return self.blocking1_widgets if tp_number == 1 else self.blocking2_widgets

    def _update_alignment_row_ui(self, widgets, is_active, is_loop):
        """Central function to update a single row's UI based on its active state."""
        if not widgets: return

        widgets['status_label'].configure(text="Estado: Activo" if is_active else "Estado: Inactivo",
                                          text_color="green" if is_active else "orange")
        if not is_active:
            widgets['timer_label'].pack_forget()

        controls_state = "disabled" if is_active else "normal"
        widgets['activate_button'].configure(state="disabled" if is_active else "normal")
        widgets['deactivate_button'].configure(state="normal" if is_active else "disabled")
        widgets['duration_combo'].configure(state=controls_state)
        if is_loop and 'type_combo' in widgets:
            widgets['type_combo'].configure(state=controls_state)

    def _handle_program_alignment_success(self, tp_number, is_loop, is_activating, duration):
        """Updates the UI after a loop/blocking is programmed and manages timers."""
        timer_key = f"{'loop' if is_loop else 'block'}_{tp_number}"
        widgets = self._get_alignment_widgets(tp_number, is_loop)

        if timer_key in self.alignment_timers:
            self.after_cancel(self.alignment_timers[timer_key])
            del self.alignment_timers[timer_key]

        self._update_alignment_row_ui(widgets, is_activating, is_loop)

        if is_activating and duration != "0":
            duration_sec = int(duration)
            widgets['timer_label'].pack(anchor="w")
            self._alignment_countdown(duration_sec, timer_key)

    def _alignment_countdown(self, remaining_seconds, timer_key):
        """Handles the countdown for a temporary loop/block."""
        tp_number = int(timer_key.split('_')[1])
        is_loop = 'loop' in timer_key
        widgets = self._get_alignment_widgets(tp_number, is_loop)

        if remaining_seconds > 0:
            widgets['timer_label'].configure(text=f"Finaliza en {remaining_seconds}s")
            timer_id = self.after(1000, self._alignment_countdown, remaining_seconds - 1, timer_key)
            self.alignment_timers[timer_key] = timer_id
        else:
            widgets['timer_label'].pack_forget()
            self._update_alignment_row_ui(widgets, is_active=False, is_loop=is_loop)
            if timer_key in self.alignment_timers:
                del self.alignment_timers[timer_key]
  
  
            # ----------- TASK SCHEDULER -----------                
    def _run_task_sequence_thread(self):
        """Inicia la ejecución de la secuencia de tareas en un hilo separado."""
        # Preparamos el evento para poder detener la secuencia
        self.stop_sequence_event = threading.Event()
        
        # Deshabilitamos botones para no interferir pasando el estado "is_running"
        self.run_button_state(is_running=True) 

        threading.Thread(target=self._execute_task_sequence, daemon=True).start()
        
    def _stop_task_sequence(self):
        """Establece la señal para detener la ejecución de la secuencia."""
        if hasattr(self, 'stop_sequence_event'):
            self.gui_queue.put(('scheduler_log', "Señal de detención enviada... Finalizando tarea actual.\n", "orange"))
            self.stop_sequence_event.set()
            # self.stop_sequence_button.configure(state="disabled")


    def _execute_task_sequence(self):
        """
        Motor de ejecución de la secuencia de tareas.
        NOTA: Este método se ejecuta en un hilo secundario.
        """
        sequence_failed = False
        xml_files = []
 
        try:
            if not hasattr(self, 'task_sequence') or not self.task_sequence:
                self.gui_queue.put(('main_status', "Error: No hay tareas en la secuencia.", "red"))
                return

            self.gui_queue.put(('scheduler_log', "--- Iniciando secuencia de tareas ---\n", "white"))

            timestamp_before_task = datetime.now(timezone.utc).isoformat() # Timestamp inicial

            for i, task in enumerate(self.task_sequence):
                # Comprobar si se ha solicitado detener la secuencia
                if self.stop_sequence_event.is_set():
                    self.gui_queue.put(('scheduler_log', "Secuencia detenida por el usuario.\n", "orange"))
                    break

                task_name = task.get('name', f"Tarea {i+1}")
                self.gui_queue.put(('scheduler_log', f"▶ Ejecutando Tarea [{i+1}/{len(self.task_sequence)}]: {task_name}\n", "cyan"))
                
                task_result = 0 # 0 = PASS, otro valor = FAIL
                
                # ----------- PROCESAR TIPO DE TAREA -----------
                if task['type'] == 'robot_test':
                    output_file = f"output_task_{i}.xml"
                    output_file_path = os.path.join("test_results", output_file) # Guardamos el path del fichero xml correspondiente a este test para poder especificarlo mas tarde en codigo error (en caso de que el test falle)
                    timestamp_before_task = datetime.now(timezone.utc).isoformat()
                    # ***************************************************************************************************************************
                    # MODIFICACIÓN: AHORA USAREMOS EL MAPA DEFINIFO EN INIT QUE RELACIONA EL NOMBRE DEL TEST CON EL MENSAJE DE LA COLA Y LOS ATRIBUTOS DEL LISTENER -> MAS ABAJO ->
                    # # **IMPORTANTE**: _run_robot_test debe devolver el código de resultado (lo guardamos en task_result) para dar fallo despues del inicio de cualquier tarea en caso de ser != 0
                    # #Ejecutamos el test correspondiente al que pone en la tarea
                    # task_result = self._run_robot_test(
                    #     test_name=task['test_name'],
                    #     variables=task.get('variables', []),
                    #     preferred_filename=task.get('filename'),
                    #     output_filename=output_file,
                    #     suppress_gui_updates=True # Para evitar mensajes de status duplicados
                    # )
                    # ***************************************************************************************************************************
                    # -> ->
                    # 1. Comprobar si este test tiene una acción de GUI asociada
                    gui_update_info = self.test_gui_update_map.get(task['test_name'])  # Recordemos que "task" era un diccionario que tenía la clave "test_name"
                    success_callback = None # Por defecto, no hay callback

                    if gui_update_info:
                        message_type, attr_names = gui_update_info
                        # ************************************************************************************************************
                        # 2. Crear una función de callback dinámicamente
                        def create_callback(msg_type, attrs):
                            def callback(listener):
                                # Recopila los valores de los atributos necesarios del objeto listener
                                params = [getattr(listener, attr, None) for attr in attrs]
                                self.gui_queue.put(tuple([msg_type] + params))  # EL OBJETIVO DE ESTA FUNCION!
                            return callback
                        # ************************************************************************************************************

                        success_callback = create_callback(message_type, attr_names)

                    # 3. Pasar el callback (o None si no hay) a la función de ejecución
                    task_result = self._run_robot_test(
                        test_name=task['test_name'],
                        variables=task.get('variables', []),
                        preferred_filename=task.get('filename'),
                        output_filename=output_file,
                        suppress_gui_updates=True,
                        on_success=success_callback  # <--  Si no se crea ningún callback especial para este test, el valor de success_callback será None y no se ejecutará nada extra.
                    )
                    
                    if os.path.exists(output_file_path):
                        xml_files.append(output_file_path)  # Guardamos el XML para el informe consolidado si se generó el archivo en el path guardado
                    else:
                        self.gui_queue.put(('scheduler_log', f"⚠️  No se generó archivo de salida para '{task['name']}'.\n", "orange"))

                elif task['type'] == 'delay':
                    delay_seconds = int(task.get('duration', 5))
                    self.gui_queue.put(('scheduler_log', f"  Pausando durante {delay_seconds} segundos...\n", "gray"))
                    
                    # Hacemos una pausa interrumpible
                    for _ in range(delay_seconds):
                        if self.stop_sequence_event.is_set():
                            break
                        time.sleep(1)

                elif task['type'] == 'check_snmp_traps':
                    self.gui_queue.put(('scheduler_log', "  Buscando nuevos traps SNMP...\n", "gray"))
                    new_traps = self.trap_receiver.get_traps_since(timestamp_before_task)
                    
                    if new_traps:
                        self.gui_queue.put(('scheduler_log', f"  ✔ Encontrados {len(new_traps)} traps nuevos.\n", "green"))
                        self.save_traps_to_db(new_traps)
                    else:
                        self.gui_queue.put(('scheduler_log', "  - No se encontraron traps nuevos.\n", "gray"))
                    
                    # Actualizamos el timestamp para la siguiente tarea
                    timestamp_before_task = datetime.now(timezone.utc).isoformat()

                # ----------- MANEJAR RESULTADO DE LA TAREA -----------
                if task_result != 0:
                    self.gui_queue.put(('scheduler_log', f"❌ Tarea '{task_name}' ha fallado.\n", "red"))
                    sequence_failed = True
                    if task.get('on_fail') == 'stop':
                        self.gui_queue.put(('scheduler_log', "Política 'on_fail: stop'. Deteniendo la secuencia.\n", "red"))
                        break
                else:
                    self.gui_queue.put(('scheduler_log', f"✔ Tarea '{task_name}' completada.\n", "green"))
                    
            # ----------- FINAL DE LA SECUENCIA -----------
        finally:
            self.gui_queue.put(('scheduler_log', "--- Secuencia de tareas finalizada ---\n", "white"))

            # Generar informe consolidado si se ejecutaron tests
            if xml_files:
                self.gui_queue.put(('scheduler_log', "Generando informe consolidado...\n", "gray"))
                try:
                # ***************************************************************************************************************************
                #  CORRECCIÓN: YA NO HAREMOS USO DE ESTO, SINO DE SUBPROCESS para llamar a rebot --- EN UN PROCESO A PARTE DEL DE LA GUI
                #     rebot_cli(['--name', 'Informe de Secuencia', 
                #             '--outputdir', 'test_results',
                #             '--log', 'log_consolidado.html',
                #             '--report', 'report_consolidado.html'] + xml_files)
                #     self.gui_queue.put(('scheduler_log', "✔ Informe consolidado 'report_consolidado.html' creado.\n", "green"))
                # except Exception as e:
                #     self.gui_queue.put(('scheduler_log', f"❌ Error al generar informe consolidado: {e}\n", "red"))
                # ***************************************************************************************************************************

            # Construir el comando para ejecutar rebot. Lo hacemos creando un proceso completamente separado para generar el informe. De esta forma si rebot falla no afecta a la app principal (GUI). Tambien podemos determinal un Timeout, asi la GUI no se puede quedar congelada.
                    command = [
                        sys.executable,  # Usa el mismo python que ejecuta la app
                        "-m", "robot.rebot",
                        "--name", "Informe de Secuencia",
                        "--outputdir", "test_results",
                        "--log", "log_consolidado.html",
                        "--report", "report_consolidado.html"
                    ] + xml_files

                    # Ejecutar el comando como un subproceso con un tiempo de espera
                    result = subprocess.run(
                        command, 
                        capture_output=True, 
                        text=True, 
                        timeout=30  # Espera un máximo de 30 segundos
                    )

                    if result.returncode == 0:
                        self.gui_queue.put(('scheduler_log', "✔ Informe consolidado creado.\n", "green"))
                    else:
                        # Si rebot falla, muestra el error
                        error_output = result.stderr or result.stdout
                        self.gui_queue.put(('scheduler_log', f"❌ Error al generar informe: {error_output}\n", "red"))

                except subprocess.TimeoutExpired:
                    self.gui_queue.put(('scheduler_log', "❌ Error: La generación del informe tardó demasiado (timeout).\n", "red"))

                except Exception as e:
                    self.gui_queue.put(('scheduler_log', f"❌ Error inesperado al generar informe: {e}\n", "red"))

            # Restaurar GUI
            final_message = "Secuencia completada con errores." if sequence_failed else "Secuencia completada con éxito."
            final_color = "red" if sequence_failed else "green"
            self.gui_queue.put(('main_status', final_message, final_color))
            
            self.gui_queue.put(('enable_buttons', None)) # Rehabilitamos botones
        
            
    def _get_test_case_arguments(self, test_name):
        """
        Consulta el diccionario de mapeo para obtener los argumentos de un test.
        """
        # .get() es una forma segura de acceder a un diccionario.
        # Si no encuentra el test_name, devuelve una lista vacía por defecto [].
        return self.test_variable_map.get(test_name, [])
    
    
    # --- GUI ---
    def _populate_scheduler_tab(self, tab_frame):
        """Crea y organiza todos los widgets para la pestaña del Planificador de Tareas."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(2, weight=1)

        # --- 1. FRAME DE CREACIÓN DE TAREAS ---
        creator_frame = ctk.CTkFrame(tab_frame)
        creator_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        creator_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(creator_frame, text="1. Crear Tarea", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        ctk.CTkLabel(creator_frame, text="Tipo de Tarea:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.task_type_combo = ctk.CTkComboBox(creator_frame, values=["Ejecutar Test", "Pausa (segundos)", "Verificar Traps SNMP Nuevos"], command=self._on_task_type_change)
        self.task_type_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")


        # Widget para seleccionar el test (inicialmente oculto)
        self.task_test_label = ctk.CTkLabel(creator_frame, text="Test a Ejecutar:")
        # test_names = [test for tests in self.tests_data.values() for test in tests] # Dejamos de usar esta linea para clasificar todos los tests en las siguietnes lineas de codigo
        # Crear la lista organizada con cabeceras de archivo
        organized_test_list = []
        if self.tests_data:
            for file_path, test_list in self.tests_data.items():    # FOR que recorre dos variables: file_path y test_list dentro de items() de self.tests_data
                # Añadimos el nombre del archivo como cabecera
                filename = os.path.basename(file_path)
                organized_test_list.append(f"--- {filename} ---")
                # Añadimos los tests de ese archivo, indentados
                for test in test_list: # Recorremos todos los tests que hay dentro del archivo de test que esta recorriendo el primer FOR
                    organized_test_list.append(f"  {test}")
        else:
            organized_test_list = ["No se encontraron tests"]
        self.task_test_combo = ctk.CTkComboBox(creator_frame, values=organized_test_list, command=self._on_test_selection_change)
        
        
        # Widget para las variables del test (inicialmente oculto)
        self.task_vars_label = ctk.CTkLabel(creator_frame, text="Variables:")
        self.task_vars_entry = ctk.CTkEntry(creator_frame, placeholder_text="VAR1:valor1 VAR2:valor2")
        
        
        # Widget para el parámetro de duración (inicialmente oculto)
        self.task_param_label = ctk.CTkLabel(creator_frame, text="Duración (s):")
        self.task_param_entry = ctk.CTkEntry(creator_frame, placeholder_text="Ej: 10")
        
        # Widget para mostrar los argumentos esperados
        self.task_args_display_label = ctk.CTkLabel(creator_frame, text="", text_color="gray", font=ctk.CTkFont(size=11))
        
        
        ctk.CTkLabel(creator_frame, text="Si Falla:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.task_on_fail_combo = ctk.CTkComboBox(creator_frame, values=["Detener secuencia", "Continuar"])
        self.task_on_fail_combo.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        add_task_button = ctk.CTkButton(creator_frame, text="Añadir Tarea a la Secuencia", command=self._add_task_to_sequence)
        add_task_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        
        self._on_task_type_change(self.task_type_combo.get()) # Llamada inicial para configurar la visibilidad

        # --- 2. FRAME DE LA SECUENCIA DE TAREAS ---
        sequence_frame = ctk.CTkFrame(tab_frame)
        sequence_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        sequence_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(sequence_frame, text="2. Secuencia de Tareas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.task_sequence_frame = ctk.CTkScrollableFrame(sequence_frame, height=200)
        self.task_sequence_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        sequence_controls_frame = ctk.CTkFrame(sequence_frame, fg_color="transparent")
        sequence_controls_frame.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ns")
        move_up_button = ctk.CTkButton(sequence_controls_frame, text="▲ Subir", width=80, command=lambda: self._move_task(-1))
        move_up_button.pack(pady=5)
        move_down_button = ctk.CTkButton(sequence_controls_frame, text="▼ Bajar", width=80, command=lambda: self._move_task(1))
        move_down_button.pack(pady=5)
        remove_button = ctk.CTkButton(sequence_controls_frame, text="❌ Eliminar", width=80, fg_color="#D32F2F", hover_color="#B71C1C", command=self._remove_selected_task)
        remove_button.pack(pady=5)

        # --- 3. FRAME DE EJECUCIÓN Y REGISTRO ---
        execution_frame = ctk.CTkFrame(tab_frame)
        execution_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        execution_frame.grid_columnconfigure(0, weight=1)
        execution_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(execution_frame, text="3. Ejecución y Registro", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        execution_buttons = ctk.CTkFrame(execution_frame, fg_color="transparent")
        execution_buttons.grid(row=1, column=0, sticky="ew")
        execution_buttons.grid_columnconfigure((0,1), weight=1)
        self.run_sequence_button = ctk.CTkButton(execution_buttons, text="▶️ Ejecutar Secuencia", command=self._run_task_sequence_thread)
        self.run_sequence_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.stop_sequence_button = ctk.CTkButton(execution_buttons, text="⏹️ Detener Secuencia", command=self._stop_task_sequence, state="disabled")
        self.stop_sequence_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.scheduler_log_textbox = ctk.CTkTextbox(execution_frame, state="disabled")
        self.scheduler_log_textbox.grid(row=2, column=0, padx=10, pady=(5,10), sticky="nsew")


    def _populate_db_viewer_tab(self, tab_frame):
        """Crea los widgets para el visor de la base de datos de traps."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)

        controls_frame = ctk.CTkFrame(tab_frame)
        controls_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        refresh_button = ctk.CTkButton(controls_frame, text="Refrescar Datos de la Base de Datos", command=self._load_traps_from_db)
        refresh_button.pack(pady=10, padx=10, fill="x")

        self.db_display_textbox = ctk.CTkTextbox(tab_frame, state="disabled", wrap="none")
        self.db_display_textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")


    def _on_task_type_change(self, selected_type):
        """Muestra u oculta los widgets de creación de tareas según el tipo seleccionado."""
        # Lo hacemos para mostrar la info relevante en cada momento.
        # Por defecto, cuando el "formulario" se reinicia se ocultan todos estos campos
        
        # Ocultar todos los widgets opcionales primero ("Test a ejecutar", "Duracion" y "Variables")
        # Test a ejecutar
        self.task_test_label.grid_forget()
        self.task_test_combo.grid_forget()
        # Duracion
        self.task_param_label.grid_forget()
        self.task_param_entry.grid_forget()
        # Variables entrada
        self.task_vars_label.grid_forget() 
        self.task_vars_entry.grid_forget()
        # Variables esperadas
        self.task_args_display_label.grid_forget()
        
        # Mostrar los widgets necesarios para el tipo de tarea seleccionado. Solo para estos tipos de tareas los mostraremos.
        if selected_type == "Ejecutar Test":
            self.task_test_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.task_test_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
            
            self.task_vars_label.grid(row=3, column=0, padx=10, pady=5, sticky="w") 
            self.task_vars_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
            
            self.task_args_display_label.grid(row=4, column=1, padx=10, pady=(0,5), sticky="w")
            self._on_test_selection_change(self.task_test_combo.get()) # Llamada inicial al metodo que nos permite añadir la fila con los argumentos de ese testcase
            
        elif selected_type == "Pausa (segundos)":
            self.task_param_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.task_param_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def _add_task_to_sequence(self):
        """Recopila la información de la tarea y la añade a la secuencia."""
        task_type = self.task_type_combo.get()
        on_fail = "stop" if self.task_on_fail_combo.get() == "Detener secuencia" else "continue"
        task = {'on_fail': on_fail}

        if task_type == "Ejecutar Test":
            selected_item = self.task_test_combo.get()
            
            # Validamos que no sea una cabecera (---) o que la lista de testcase se encuentre vacia porque en ese archivo no hayan
            if selected_item.strip().startswith("---") or selected_item == "No se encontraron tests":
                self._update_status("Error: Por favor, seleccione un test válido.", "red")
                return
            
            test_name = selected_item.strip()
        
            # Adquirimos las variables
            variables_str = self.task_vars_entry.get()
            # Dividimos el string por espacios para tener una lista de "CLAVE:VALOR"
            variables_list = variables_str.split() if variables_str else []
            
            task['type'] = 'robot_test'
            task['name'] = f"TEST: {test_name}"
            task['test_name'] = test_name
            task['filename'] = self._find_test_file(test_name).split(os.sep)[-1]
            task['variables'] = variables_list 

            self.task_vars_entry.delete(0, 'end') # Limpiamos el campo de variables para la próxima tarea

        elif task_type == "Pausa (segundos)":
            duration = self.task_param_entry.get()
            if not duration.isdigit() or int(duration) <= 0:
                self._update_status("Error: La duración de la pausa debe ser un número positivo.", "red")
                return
            task['type'] = 'delay'
            task['name'] = f"PAUSA: {duration} segundos"
            task['duration'] = duration

        elif task_type == "Verificar Traps SNMP Nuevos":
            task['type'] = 'check_snmp_traps'
            task['name'] = "VERIFICAR: Traps SNMP Nuevos"

        self.task_sequence.append(task)
        self._update_task_sequence_display()

    def _update_task_sequence_display(self):
        """Redibuja la lista visual de tareas en la secuencia."""
        for widget in self.task_widgets:
            widget.destroy()
        self.task_widgets.clear()
        self.selected_task_index = -1

        for i, task in enumerate(self.task_sequence):
            task_frame = ctk.CTkFrame(self.task_sequence_frame, fg_color="transparent")
            task_frame.pack(fill="x", padx=5, pady=2)
            
            task_label = ctk.CTkLabel(task_frame, text=f"{i+1}. {task['name']}", anchor="w")
            task_label.pack(fill="x")
            
            # Hacemos que el frame y la etiqueta sean clickables para seleccionar la fila
            task_frame.bind("<Button-1>", lambda event, index=i: self._select_task_in_sequence(index))
            task_label.bind("<Button-1>", lambda event, index=i: self._select_task_in_sequence(index))
            
            self.task_widgets.append(task_frame)

    def _select_task_in_sequence(self, index):
        """Gestiona la selección de una tarea en la lista."""
        self.selected_task_index = index
        for i, frame in enumerate(self.task_widgets):
            if i == index:
                frame.configure(fg_color=("gray80", "gray25")) # Color de resaltado
            else:
                frame.configure(fg_color="transparent")

    def _move_task(self, direction):
        """Mueve la tarea seleccionada hacia arriba (-1) o hacia abajo (1)."""
        if self.selected_task_index == -1: return # Es para evitar mover nada u obtener error en caso de querer mover sin seleccionar nada.

        # Partimos de la lista de tareas que está en la memoria (self.task_sequence)
        new_index = self.selected_task_index + direction # Calculamos la nueva posición del objeto seleccionado que queremos mover.
        if 0 <= new_index < len(self.task_sequence): # Nos aseguramos que la nueva pos se encuentre dentro de los indices posibles de la lista.
            # Intercambiar elementos en la lista de datos
            item = self.task_sequence.pop(self.selected_task_index) # Nos lo saca de la lista, guardandolo temporalmente
            self.task_sequence.insert(new_index, item)
            
            # Redibujar y pre-seleccionar el elemento movido
            self._update_task_sequence_display() # Una vez actualizada "task_sequence", podemos actualizar la lista en pantalla
            self._select_task_in_sequence(new_index) # Hemos redibujado la lista de tareas actualizada, pero queremos conservar el elemento que habíamos movido como seleccionado.

    def _remove_selected_task(self):
        """Elimina la tarea seleccionada de la secuencia."""
        if self.selected_task_index == -1: return # Es para evitar mover nada u obtener error en caso de querer mover sin seleccionar nada.
        
        self.task_sequence.pop(self.selected_task_index) # Lo sacamos de la lista SIN GUARDARLO
        self._update_task_sequence_display()

    def _update_scheduler_log(self, message, color):
        """Añade un mensaje al cuadro de texto de registro del planificador."""
        self.scheduler_log_textbox.configure(state="normal")
        self.scheduler_log_textbox.insert("end", message, (color,))
        self.scheduler_log_textbox.configure(state="disabled")
        self.scheduler_log_textbox.see("end") # Auto-scroll hacia el final

    def _on_test_selection_change(self, selected_test):
        """Se activa al seleccionar un test y muestra sus argumentos requeridos."""

            # Si el usuario selecciona una cabecera (---), no hacemos nada.
        if selected_test.strip().startswith("---"):
            self.task_args_display_label.configure(text="") # Limpiamos la etiqueta
            return

        actual_test_name = selected_test.strip()
        args = self._get_test_case_arguments(actual_test_name)
        if args:
            self.task_args_display_label.configure(text=f"Argumentos: {', '.join(args)}")
        else:
            self.task_args_display_label.configure(text="Este test no requiere argumentos.")
            
            
            
    def _load_traps_from_db(self):
        """Carga los traps desde el archivo SQLite y los muestra en el textbox."""
        try:
            conn = sqlite3.connect(self.db_path) # Crea una conexion nueva para este hilo (el de la GUI)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp_received, event_type, source_address, varbinds_json FROM traps ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close() # Cierra la conexión en cuanto tengamos los datos
            
            self.db_display_textbox.configure(state="normal")
            self.db_display_textbox.delete("1.0", "end")

            if not rows:
                self.db_display_textbox.insert("1.0", "La base de datos está vacía.")
            else:
                for row in rows:
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
            self._update_status("Historial de traps cargado.", "white")

        except Exception as e:
            self._update_status(f"Error al leer la base de datos: {e}", "red")
            
            
if __name__ == "__main__":
    if not os.path.exists("test_results"):
        os.makedirs("test_results")
    app = ModernTestRunnerApp()
    app.mainloop()
