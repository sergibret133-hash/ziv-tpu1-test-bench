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
import time # Importado para pequeñas pausas
from pathlib import Path
from robot.api import TestSuiteBuilder
from tomlkit import key

from Trap_Receiver_GUI_oriented import Trap_Receiver_GUI_oriented

import sqlite3
from datetime import datetime, timezone
from robot.rebot import rebot_cli
# Para poder abrir archivos
from tkinter import filedialog

# *******************IMPORTS DE OTRAS PARTES DEL PROYECTO*************************
import gui.ui_sidebar as ui_sidebar
import gui.ui_tab_scheduler as ui_tab_scheduler
import gui.ui_tab_equipment as ui_tab_equipment
import gui.ui_tab_monitoring as ui_tab_monitoring
import gui.ui_tab_alignment as ui_tab_alignment
import gui.ui_tab_alarms as ui_tab_alarms

import logic.db_handler as db_handler
import logic.robot_executor as robot_executor


from logic.scheduler_controller import SchedulerController
from logic.equipment_controller import EquipmentController
from logic.monitoring_controller import MonitoringController
from logic.alignment_controller import AlignmentController
from logic.snmp_controller import SNMPController
from logic.trap_listener_controller import TrapListenerController
from logic.alarms_controller import AlarmsController
# from logic.session_controller import SessionController


# --- CONFIGURATION ---
TEST_DIRECTORY = "tests"

class ModernTestRunnerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ******* 1. INICIALIZACIÓN DE LA VENTANA PRINCIPAL *******
        self.title("Teleprotection Test Interface")
        self.geometry("1100x850") 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ************ 2. INICIALIZACIÓN DEL ESTADO Y DATOS ************
        self.browser_process = None

        self.is_main_task_running = False    # Para indicar al hilo que hace pull para comprobar alarmas si hay algun otro test ejecutandose y así no interferir.

        self.trap_receiver = Trap_Receiver_GUI_oriented()
        self.snmp_listener_thread = None
        
        self.gui_queue = queue.Queue()
        
        # MAPAS DE DATOS Y CONFIGURACIONES
        self.test_variable_map = {
            # --- Tests de Configuración Básica ---
            "List Detected Modules": [],
            "List assigned Modules and Commands assigned": [],
            "Assign Prioritized Detected Modules": ["${TP1}", "${TP2}"],
            "Command Number Assignments": [
                "${TP1_TX_Command_Number_NUM_COMMANDS}", 
                "${TP1_RX_Command_Number_NUM_COMMANDS}", 
                "${TP2_TX_Command_Number_NUM_COMMANDS}", 
                "${TP2_RX_Command_Number_NUM_COMMANDS}"
            ],
            "Open_BasicConfiguration+Configure Display Time Zone": ["${Time_zone}"],

            # --- Tests de Asignación de Comandos ---
            "Log and Save Teleprotection Commands and Inputs/Outputs": [],
            "Program Command Assignments": [
                "${tx_matrix_str}", 
                "${rx_matrix_str}", 
                "${tx_list_str}", 
                "${rx_list_str}"
            ],

            # --- Tests de SNMP ---
            "Retrieve Full SNMP Configuration": [],
            "Execute Full SNMP Configuration": [
                "${SNMP_AGENT_STATE}", "${TRAPS_ENABLE_STATE}", "${TPU_SNMP_PORT}", 
                "${SNMP_V1_V2_ENABLE}", "${SNMP_V1_V2_READ}", "${SNMP_V1_V2_SET}", 
                "${SNMP_V3_ENABLE}", "${SNMP_V3_READ_USER}", "${SNMP_V3_READ_PASS}", 
                "${SNMP_V3_READ_AUTH}", "${SNMP_V3_WRITE_USER}", "${SNMP_V3_WRITE_PASS}", 
                "${SNMP_V3_WRITE_AUTH}", "${HOSTS_CONFIG_STR}"
            ],

            # --- Tests de Alineación (Alignment) ---
            "Input Activation": ["${ACTIVATE_DEACTIVATE}", "${DURATION}", "${INPUTS_LIST}"],
            "Retrieve Inputs Activation State": [],
            "Current Loop and Blocking State": [],
            "Program Teleprotection Loop": [
                "${LOOP_TELEPROTECTION_NUMBER}", 
                "${ACTIVATE_DEACTIVATE_LOOP}", 
                "${LOOP_TYPE}", 
                "${LOOP_DURATION}"
            ],
            "Program Teleprotection Blocking": [
                "${BLOCKING_TELEPROTECTION_NUMBER}", 
                "${ACTIVATE_DEACTIVATE_BLOCKING}", 
                "${BLOCKING_DURATION}"
            ],

            # --- Tests de Registro Cronológico ---
            "Retrieve Chronological Register": [],
            "Delete Chronological Register": [],
            "Capture Last Chronological Log Entries": [
                "${EXPECTED_NUM_ENTRIES}", 
                "${EVENT_ALARM_FILTER}", 
                "${CHRONO_ORDER}"
            ],

            # --- Tests de Módulo IBTU BYTONES ---
            "Retrieve IBTU ByTones Full Configuration": [],
            "Program IBTU ByTones S1 General": [
                "${RX_OPERATION_MODE}", 
                "${LOCAL_PERIODICITY}", 
                "${REMOTE_PERIODICITY}", 
                "${SNR_THRESHOLD_ACTIVATION}", 
                "${SNR_THRESHOLD_DEACTIVATION}"
            ],
            "Program IBTU ByTones S2 Frequencies": [
                "${TX_SCHEME}", "${TX_GUARD_FREQUENCY}", "${TX_APPLICATION_TYPE_LIST_STR}", 
                "${TX_FREQUENCY_LIST_STR}", "${RX_SCHEME}", "${RX_GUARD_FREQUENCY}", 
                "${RX_APPLICATION_TYPE_LIST_STR}", "${RX_FREQUENCY_LIST_STR}"
            ],
            "Program IBTU ByTones S3 Levels": [
                "${BY_TONES_INPUT_LEVEL}", 
                "${BY_TONES_POWER_BOOSTING}", 
                "${BY_TONES_OUTPUT_LEVEL}"
            ],
            
            "Retrieve IBTU FFT Full Configuration": [],
            "Program IBTU FFT S1 General": [
                "${LOCAL_PERIODICITY}", "${REMOTE_PERIODICITY}",
                "${SNR_THRESHOLD_ACTIVATION}", "${SNR_THRESHOLD_DEACTIVATION}",
                "${RX_OPERATION_MODE_LIST_STR}"
            ],
            "Program IBTU FFT S2 General": [
                "${TX_BW}", "${TX_GUARD_FREQ}", "${TX_APPLICATION_MODE_LIST_STR}",
                "${RX_BW}", "${RX_GUARD_FREQ}", "${RX_APPLICATION_MODE_LIST_STR}"
            ],
            "Program IBTU FFT S3 General": [
                "${INPUT_LEVEL}", "${POWER_BOOSTING}", "${OUTPUT_LEVEL}"
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
        
        
    def _create_gui_update_callback(self, message_type, attr_names):
        """
        Fábrica que crea y devuelve una función de callback personalizada.
        """
        # Comprobamos si es un caso especial que requiere el listener completo
        if attr_names == ['listener']:
            def callback_special(listener):
                self.gui_queue.put((message_type, listener))    # En este caso, no envía una tupla ni tampoco ningun parametro, sino todos los objectos contenidos en el listener 
            return callback_special
        
        # Para el resto de casos con atributos SI enviamos una tupla
        # def callback(listener):
        #     # Recopila los valores de los atributos del listener
        #     params = [getattr(listener, attr, None) for attr in attr_names]
        #     # Envía el mensaje completo a la cola de la GUI
        #     self.gui_queue.put(tuple([message_type] + params))
        # return callback 
    
        def callback(listener):
            params = []
            print(f"DEBUG CALLBACK: Intentando leer atributos: {attr_names}") # <-- Añadir
            for attr in attr_names:
                value = getattr(listener, attr, 'ATTRIBUTE_NOT_FOUND') # <-- Añadir default
                print(f"DEBUG CALLBACK: Atributo '{attr}' = {value}") # <-- Añadir
                params.append(value)

            # Comprobar si se encontró algo que no sea el valor por defecto
            if 'ATTRIBUTE_NOT_FOUND' in params:
                print(f"ERROR CALLBACK: No se encontraron todos los atributos para {message_type}")
                # Decide si quieres enviar el mensaje igualmente o no
                # self.gui_queue.put(tuple([message_type] + params)) # Envía con error
                return # No envía nada si falta un atributo

            print(f"DEBUG CALLBACK: Poniendo en cola: {tuple([message_type] + params)}") # <-- Añadir
            self.gui_queue.put(tuple([message_type] + params))
        return callback
    
           
    def process_gui_queue(self):
        """
        Process messages from the thread-safe queue to update the GUI.
        """
        try:
            while not self.gui_queue.empty(): # Mientras haya mensajes en la cola
                message = self.gui_queue.get_nowait()
                
                print(f"DEBUG EN COLA: {message}") # DEBUG
                msg_type = message[0]
                
                if msg_type == 'main_status':
                    self._update_status(message[1], message[2])
                elif msg_type == 'session_status':
                    self._update_session_status(message[1], message[2])
                elif msg_type == 'snmp_listener_status':
                    ui_tab_monitoring._update_snmp_listener_status(self, message[1], message[2])
                elif msg_type == 'enable_buttons':
                    self.run_button_state(is_running=False)
                elif msg_type == 'modules_display':
                    ui_tab_equipment._update_modules_display(self, message[1])
                elif msg_type == 'assigned_modules_display':
                    ui_tab_equipment._update_assigned_modules_display(self, message[1], message[2])
                elif msg_type == 'command_assignment_grids':
                    ui_tab_equipment._update_command_assignment_grids(self, message[1], message[2], message[3])
                elif msg_type == 'full_snmp_config_display':
                    ui_tab_monitoring._update_full_snmp_config_display(self, message[1])
                elif msg_type == 'update_input_activation_display':
                    ui_tab_alignment._update_input_activation_display(self, message[1], message[2])
                elif msg_type == 'program_inputs_success':
                    ui_tab_alignment._handle_program_inputs_success(self, message[1], message[2], message[3])
                elif msg_type == 'update_chrono_log_display':
                    ui_tab_monitoring._update_chrono_log_display(self, message[1])
                elif msg_type == 'debug_log':
                    self._update_debug_log(message[1])
                elif msg_type == 'update_alignment_states':
                    ui_tab_alignment._update_alignment_states(self, message[1])
                elif msg_type == 'program_alignment_success':
                    self.alignment_controller._handle_program_alignment_success(*message[1:])
                elif msg_type == 'update_ibtu_full_config':
                    ui_tab_equipment._update_ibtu_full_config_display(self, message[1])
                elif msg_type == 'scheduler_log':
                    ui_tab_scheduler._update_scheduler_log(self, message[1], message[2])
                elif msg_type == 'update_alarms_display':
                    ui_tab_alarms.update_alarms_display(self, message[1])
                elif msg_type == 'update_correlation_display':
                    # message[1] = chrono_text_report
                    # message[2] = trap_text_report
                    # message[3] = result
                    # message[4] = color
                    ui_tab_monitoring._update_correlation_display(self, message[1], message[2], message[3], message[4])
                elif msg_type == 'update_ibtu_fft_config':
                    # message[1] contendrá el diccionario fft_config_data
                    ui_tab_equipment._update_ibtu_fft_config_display(self, message[1])

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
        """Handles the window closing event to ensure cleanup."""
        if self.browser_process:
            robot_executor._execute_stop_browser(self)
        self.destroy()      
            
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
        # self.is_task_running = is_running
        session_active = self.browser_process is not None
        
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
                            ui_tab_alignment._update_alignment_row_ui(widgets_dict, is_active, is_loop_flag)
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
        
    def _update_session_status(self, message, color):
        self.session_status_label.configure(text=f"Estado: {message}", text_color=color)


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
        # .get() es una forma segura de acceder a un diccionario.
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





    # Llamadas procedentes de controller, dirigidas a archivos de la carpeta gui
    def start_alignment_countdown(self, duration, key):
        ui_tab_alignment._alignment_countdown(self, duration, key)
        
    def update_task_sequence_display(self):
        ui_tab_scheduler._update_task_sequence_display(self)
        
    def update_trap_display(self, traps_data):
        ui_tab_monitoring._update_trap_display(self, traps_data)