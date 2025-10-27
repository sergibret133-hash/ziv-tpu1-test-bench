import threading
import logic.robot_executor as robot_executor # Necesitará llamar al ejecutor
import json

class EquipmentController:
    def __init__(self, app_ref):
        self.app_ref = app_ref
        
        # ***** BASIC CONFIGURATION *****
    def _run_list_modules_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_list_modules_test, daemon=True).start()

    def _execute_list_modules_test(self):
        test_name="List Detected Modules"
        active_id = self.app_ref.active_session_id
        # Activamos semaforo
        self.app_ref.is_main_task_running = True
        
        try:
            # Buscamos la info de actualizacion de la GUI en nuestro mapa inicializado en init (el mismo que usa el planificador cuando ejecuta los tests)
            gui_update_info = self.app_ref.test_gui_update_map.get(test_name)
            success_callback = None
            
            if gui_update_info: #si se encuentra, CREAMOS EL CALLBACK DINAMICO (de esta forma evitamos repetir codigo y amortizamos el mapeo que hacemos con el diccionario de tests)
                message_type, attr_names = gui_update_info

            #*********************************************************************************************************
                # Utilizamos el método de creación de  callback dinamico
                success_callback = self.app_ref._create_gui_update_callback(active_id, message_type, attr_names)
            #*********************************************************************************************************
                
            robot_executor._run_robot_test(
                self.app_ref,
                test_name=test_name,
                session_id=active_id,
                on_success=success_callback,
                on_pass_message="Estado de entradas consultado con éxito!",
                on_fail_message="Fallo al consultar el estado de las entradas."
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red"))
        finally:
        # Liberamos el semaforo
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _run_view_assigned_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_view_assigned_test, daemon=True).start()

    def _execute_view_assigned_test(self):
        test_name="List assigned Modules and Commands assigned"
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        
        try:
            # Buscamos la info de actualizacion de la GUI en nuestro mapa inicializado en init (el mismo que usa el planificador cuando ejecuta los tests)
            gui_update_info = self.app_ref.test_gui_update_map.get(test_name)
            success_callback = None
            
            if gui_update_info: #si se encuentra, CREAMOS EL CALLBACK DINAMICO (de esta forma evitamos repetir codigo y amortizamos el mapeo que hacemos con el diccionario de tests)
                message_type, attr_names = gui_update_info

            #*********************************************************************************************************
                # Utilizamos el método de creación de  callback dinamico
                success_callback = self.app_ref._create_gui_update_callback(active_id, message_type, attr_names)
            #*********************************************************************************************************
            
            robot_executor._run_robot_test(
                self.app_ref,
                test_name=test_name,
                session_id=active_id,
                on_success=success_callback,
                on_pass_message="Assigned modules info retrieved!",
                on_fail_message="Failed to retrieve assigned modules!"
            )
        except Exception as e:
                self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
                
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))

    def _run_assign_modules_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_assign_modules_test, daemon=True).start()

    def _execute_assign_modules_test(self):
        self.app_ref.is_main_task_running = True
        active_id = self.app_ref.active_session_id
        try:
            tp1 = self.app_ref.entry_tp1.get()
            tp2 = self.app_ref.entry_tp2.get()
            if not tp1 or not tp2:
                self.app_ref.gui_queue.put(('main_status', "Error: Please provide values for TP1 and TP2.", "red"))
                self.app_ref.run_button_state(is_running=False)
                return

            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Assign Prioritized Detected Modules",
                session_id=active_id,
                variables=[f"TP1:{tp1}", f"TP2:{tp2}"],
                on_pass_message="Modules assigned successfully!",
                on_fail_message="Failed to assign modules!"
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _run_program_commands_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_commands_test, daemon=True).start()

    def _execute_program_commands_test(self):
        """Executes the 'Command Number Assignments' test."""
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        try:
            tp1_tx = self.app_ref.tp1_tx_entry.get()
            tp1_rx = self.app_ref.tp1_rx_entry.get()
            tp2_tx = self.app_ref.tp2_tx_entry.get()
            tp2_rx = self.app_ref.tp2_rx_entry.get()

            if not all(v.isdigit() for v in [tp1_tx, tp1_rx, tp2_tx, tp2_rx]):
                self.app_ref.gui_queue.put(('main_status', "Error: Todos los campos de órdenes deben ser numéricos.", "red"))
                self.app_ref.run_button_state(is_running=False)
                return

            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Command Number Assignments",
                session_id=active_id,
                variables=[
                    f"TP1_TX_Command_Number_NUM_COMMANDS:{tp1_tx}",
                    f"TP1_RX_Command_Number_NUM_COMMANDS:{tp1_rx}",
                    f"TP2_TX_Command_Number_NUM_COMMANDS:{tp2_tx}",
                    f"TP2_RX_Command_Number_NUM_COMMANDS:{tp2_rx}"
                ],
                on_pass_message="Número de órdenes programado correctamente!",
                on_fail_message="Fallo al programar el número de órdenes!"
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
                
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
    
    def _run_configure_timezone_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_configure_timezone_test, daemon=True).start()

    def _execute_configure_timezone_test(self):
        """Executes the 'Configure Display Time Zone' test."""
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        
        try:
            selected_tz_name = self.app_ref.timezone_selector.get()
            tz_value = self.app_ref.timezone_map.get(selected_tz_name)

            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Open_BasicConfiguration+Configure Display Time Zone",
                session_id=active_id,
                variables=[f"Time_zone:{tz_value}"],
                on_pass_message=f"Zona horaria configurada a {selected_tz_name}!",
                on_fail_message="Fallo al configurar la zona horaria!"
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
# ************ COMMAND ASSIGNMENTS ************
    def _run_program_assignments_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_assignments_test, daemon=True).start()

    def _execute_program_assignments_test(self):
        """Reads the checkbox grids and runs the assignment test."""
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        
        try:
            if not self.app_ref.tx_checkboxes and not self.app_ref.rx_checkboxes:
                self.app_ref.gui_queue.put(('main_status', "Error: Primero consulta la configuración para generar las tablas.", "red"))
                self.app_ref.run_button_state(is_running=False)
                return
            tx_matrix = [[cb.get() for cb in row] for row in self.app_ref.tx_checkboxes]
            rx_matrix = [[cb.get() for cb in row] for row in self.app_ref.rx_checkboxes]
            tx_logic_list = [cb.get() for cb in self.app_ref.tx_logic_checkboxes]
            rx_logic_list = [cb.get() for cb in self.app_ref.rx_logic_checkboxes]
            
            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Program Command Assignments",
                session_id=active_id,
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
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
    def _run_log_command_info_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_log_command_info_test, daemon=True).start()

    
    def _execute_log_command_info_test(self):
        test_name="Log and Save Teleprotection Commands and Inputs/Outputs"
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        
        try:
            # Buscamos la info de actualizacion de la GUI en nuestro mapa inicializado en init (el mismo que usa el planificador cuando ejecuta los tests)
            gui_update_info = self.app_ref.test_gui_update_map.get(test_name)
            success_callback = None
            
            if gui_update_info: #si se encuentra, CREAMOS EL CALLBACK DINAMICO (de esta forma evitamos repetir codigo y amortizamos el mapeo que hacemos con el diccionario de tests)
                message_type, attr_names = gui_update_info

            #*********************************************************************************************************
                # Utilizamos el método de creación de  callback dinamico
                success_callback = self.app_ref._create_gui_update_callback(active_id, message_type, attr_names)
            #*********************************************************************************************************
            
            robot_executor._run_robot_test(
                self.app_ref,
                test_name=test_name,
                session_id=active_id,
                preferred_filename="Test2_CommandAssign.robot",
                on_success=success_callback,
                on_pass_message="Configuration data retrieved!",
                on_fail_message="Failed to retrieve configuration data!"
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))

# ************ MODULE CONFIGURATION ************

    # **** IBTU ByTones ****
    def _run_retrieve_ibtu_config_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_ibtu_config, daemon=True).start()

    def _execute_retrieve_ibtu_config(self):
        """Runs the test to get current IBTU ByTones configuration."""
        test_name="Retrieve IBTU ByTones Full Configuration"
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        try:
            # Buscamos la info de actualizacion de la GUI en nuestro mapa inicializado en init (el mismo que usa el planificador cuando ejecuta los tests)
            gui_update_info = self.app_ref.test_gui_update_map.get(test_name)
            success_callback = None
            
            if gui_update_info: #si se encuentra, CREAMOS EL CALLBACK DINAMICO (de esta forma evitamos repetir codigo y amortizamos el mapeo que hacemos con el diccionario de tests)
                message_type, attr_names = gui_update_info

            #*********************************************************************************************************
                # Utilizamos el método de creación de  callback dinamico
                success_callback = self.app_ref._create_gui_update_callback(active_id, message_type, attr_names)
            #*********************************************************************************************************

            robot_executor._run_robot_test(
                self.app_ref,
                test_name=test_name,
                session_id=active_id,
                preferred_filename="Module_IBTU_ByTones.robot",
                on_success=success_callback,
                on_pass_message="Configuración IBTU consultada con éxito!",
                on_fail_message="Fallo al consultar la configuración IBTU."
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _run_program_ibtu_s1_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_ibtu_s1, daemon=True).start()

    def _execute_program_ibtu_s1(self):
        """Gathers data from the General section and runs the corresponding test."""
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        
        try:
            try:
                rx_op_mode_str = self.app_ref.ibtu_rx_op_mode.get()
                rx_op_mode = self.app_ref.ibtu_rx_op_mode_map.get(rx_op_mode_str, "0")

                local_p = self.app_ref.ibtu_local_periodicity.get()
                remote_p = self.app_ref.ibtu_remote_periodicity.get()
                snr_act = self.app_ref.ibtu_snr_activation.get()
                snr_deact = self.app_ref.ibtu_snr_deactivation.get()

                if not all(v.isdigit() for v in [local_p, remote_p, snr_act, snr_deact]):
                    self.app_ref.gui_queue.put(('main_status', "Error: Todos los campos de la sección General deben ser numéricos.", "red"))
                    self.app_ref.run_button_state(is_running=False)
                    return

                variables = [
                    f"RX_OPERATION_MODE:{rx_op_mode}",
                    f"LOCAL_PERIODICITY:{local_p}",
                    f"REMOTE_PERIODICITY:{remote_p}",
                    f"SNR_THRESHOLD_ACTIVATION:{snr_act}",
                    f"SNR_THRESHOLD_DEACTIVATION:{snr_deact}"
                ]

                robot_executor._run_robot_test(
                    self.app_ref,
                    test_name="Program IBTU ByTones S1 General",
                    session_id=active_id,
                    preferred_filename="Module_IBTU_ByTones.robot",
                    variables=variables,
                    on_pass_message="Sección General de IBTU programada con éxito.",
                    on_fail_message="Fallo al programar la Sección General de IBTU."
                )
            except Exception as e:
                self.app_ref.gui_queue.put(('main_status', f"Error preparando test IBTU S1: {e}", "red"))
                self.app_ref.run_button_state(is_running=False)
                
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
        
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _run_program_ibtu_s2_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_ibtu_s2, daemon=True).start()


    def _execute_program_ibtu_s2(self):
        """Gathers data from the Frequencies section and runs the corresponding test."""
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        try:
            try:
                def process_tone_table(widgets_list, tone_widgets):
                    if not widgets_list: return None, None, None, None
                    
                    scheme_text = tone_widgets['scheme_combo'].get()
                    scheme_value = self.app_ref.ibtu_scheme_map.get(scheme_text, "0")
                    guard = tone_widgets['guard_combo'].get()
                    
                    app_type_list = []
                    freq_list = []
                    for row_widgets in widgets_list:
                        app_type_str = row_widgets['app_type'].get()
                        app_type = self.app_ref.ibtu_app_type_map.get(app_type_str, "0")
                        app_type_list.append(app_type)
                        freq = row_widgets['freq'].get()
                        if not freq.isdigit():
                                raise ValueError(f"Frecuencia '{freq}' no es un valor numérico válido.")
                        freq_list.append(freq)
                        
                    return scheme_value, guard, app_type_list, freq_list

                tx_scheme_val, tx_guard, tx_app_types, tx_freqs = process_tone_table(self.app_ref.ibtu_tx_table_widgets, self.app_ref.ibtu_tx_tone_widgets)
                if tx_app_types is None:
                    self.app_ref.gui_queue.put(('main_status', "Error: No hay datos en la tabla TX. Consulte primero.", "red"))
                    self.app_ref.run_button_state(is_running=False)
                    return

                rx_scheme_val, rx_guard, rx_app_types, rx_freqs = process_tone_table(self.app_ref.ibtu_rx_table_widgets, self.app_ref.ibtu_rx_tone_widgets)
                if rx_app_types is None:
                    self.app_ref.gui_queue.put(('main_status', "Error: No hay datos en la tabla RX. Consulte primero.", "red"))
                    self.app_ref.run_button_state(is_running=False)
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

                robot_executor._run_robot_test(
                    self.app_ref,
                    test_name="Program IBTU ByTones S2 Frequencies",
                    session_id=active_id,
                    preferred_filename="Module_IBTU_ByTones.robot",
                    variables=variables,
                    on_pass_message="Frecuencias de IBTU programadas con éxito.",
                    on_fail_message="Fallo al programar las Frecuencias de IBTU."
                )

            except ValueError as ve:
                self.app_ref.gui_queue.put(('main_status', f"Error de validación: {ve}", "red"))
                self.app_ref.run_button_state(is_running=False)
            except Exception as e:
                self.app_ref.gui_queue.put(('main_status', f"Error preparando test IBTU S2: {e}", "red"))
                self.app_ref.run_button_state(is_running=False)
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))

    def _run_program_ibtu_s3_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_ibtu_s3, args=(self.app_ref,), daemon=True).start()

    def _execute_program_ibtu_s3(self):
        """Gathers data from the Levels section and runs the corresponding test."""
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        
        try:
            try:
                input_level = self.app_ref.ibtu_input_level.get()
                power_boost = self.app_ref.ibtu_power_boosting.get()
                output_level = self.app_ref.ibtu_output_level.get()

                if not input_level or not power_boost or not output_level:
                    self.app_ref.gui_queue.put(('main_status', "Error: Todos los campos de Niveles son obligatorios.", "red"))
                    self.app_ref.run_button_state(is_running=False)
                    return

                try:
                    float(input_level)
                    float(power_boost)
                    float(output_level)
                except ValueError:
                    self.app_ref.gui_queue.put(('main_status', "Error: Los campos de Niveles deben ser numéricos.", "red"))
                    self.app_ref.run_button_state(is_running=False)
                    return

                variables = [
                    f"BY_TONES_INPUT_LEVEL:{input_level}",
                    f"BY_TONES_POWER_BOOSTING:{power_boost}",
                    f"BY_TONES_OUTPUT_LEVEL:{output_level}"
                ]

                robot_executor._run_robot_test(
                    self.app_ref,
                    test_name="Program IBTU ByTones S3 Levels",
                    session_id=active_id,
                    preferred_filename="Module_IBTU_ByTones.robot",
                    variables=variables,
                    on_pass_message="Niveles de IBTU programados con éxito.",
                    on_fail_message="Fallo al programar los Niveles de IBTU."
                )
            except Exception as e:
                self.app_ref.gui_queue.put(('main_status', f"Error preparando test IBTU S3: {e}", "red"))
                self.app_ref.run_button_state(is_running=False)
                
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    # **** IBTU FFT ****
    def _run_retrieve_ibtu_fft_config_thread(self):
        """Inicia un hilo para consultar la configuración completa de IBTU FFT."""
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_ibtu_fft_config, daemon=True).start()

    def _execute_retrieve_ibtu_fft_config(self):
        """Ejecuta el test Robot para consultar la configuración de IBTU FFT."""
        test_name = "Retrieve IBTU FFT Full Configuration"
        active_id = self.app_ref.active_session_id
        active_id = self.app_ref.active_session_id
        # Crear el callback para actualizar la GUI en caso de éxito
        gui_update_info = self.app_ref.test_gui_update_map.get(test_name)   # Nos da los atributos necesarios pasandole como argumento el test mediante mapeo de la variable test_gui_update_map
        success_callback = None
        if gui_update_info:
            message_type, attr_names = gui_update_info  # Los atributos que necesitamos: 'update_ibtu_fft_config', ['ibtu_fft_data']
            # Suponiendo que modificas el listener para tener 'ibtu_fft_data'
            success_callback = self.app_ref._create_gui_update_callback(active_id, message_type, attr_names)   # Preparamos la funcion callback para ser modificada una vez ejecutado el test, PERO NO LA EJECUTAMOS AUN!

        robot_executor._run_robot_test(
            self.app_ref,
            test_name=test_name,
            session_id=active_id,
            preferred_filename="Module_IBTU_FFT.robot",
            on_success=success_callback,    # la funcion _run_robot_test EJECUTARÁ la funcion callback en caso de que el test finalice correctamente, enviando los datos de forma segura hacia la GUI mediante la cola
            on_pass_message="Configuración IBTU FFT consultada.",
            on_fail_message="Fallo al consultar configuración IBTU FFT."
        )
        
    def _run_program_ibtu_fft_thread(self):
            """Inicia un hilo para programar TODA la configuración de IBTU FFT."""
            # Nota: Podrías hacer funciones separadas para S1, S2, S3 si prefieres
            self.app_ref.run_button_state(is_running=True)
            threading.Thread(target=self._execute_program_ibtu_fft_full, daemon=True).start()

    def _execute_program_ibtu_fft_full(self):
        """Recopila datos de la GUI y ejecuta los tests Robot para programar IBTU FFT."""
        active_id = self.app_ref.active_session_id
        # --- Recopilar datos de la GUI ---
        try:
            # Sección 1
            # Recogemos cada uno de los datos que el usuario quiera programar una vez le de a program. Para posteriormente crear un diccioanrio Json y pasarselo al archivo .robot
            local_p = self.app_ref.fft_local_periodicity_entry.get()
            remote_p = self.app_ref.fft_remote_periodicity_entry.get()
            snr_act = self.app_ref.fft_snr_activation_entry.get()
            snr_deact = self.app_ref.fft_snr_deactivation_entry.get()
            rx_op_modes = [self.app_ref.fft_rx_op_mode_map.get(combo['combo'].get())    # Recogemos los valores de los comboboxes, que son strings tipo "Normal". "Permissive".. ->
                            for combo in self.app_ref.fft_rx_op_mode_combos if combo['frame'].winfo_ismapped()] # Solo visibles. -> Convertimos esos textos en variables que el archivo .robot pueda reconocer
            rx_op_mode_list_str = json.dumps(rx_op_modes) # Convertir lista a string JSON

            # Sección 2
            tx_bw = self.app_ref.fft_bw_map.get(self.app_ref.fft_tx_bw_combo.get()) # La frecuencia que pasaremos sera la que el usuario escoja mediante el combo fft_tx_bw_combo. 
            # Pero para que el archivo .robot lo entienda hay que pasarlo a formato numerico mapeando mediante fft_bw_map
            tx_guard = self.app_ref.fft_tx_guard_freq_entry.get()
            tx_app_modes = [self.app_ref.fft_app_mode_map.get(combo['combo'].get())
                            for combo in self.app_ref.fft_tx_app_mode_combos if combo['frame'].winfo_ismapped()]
            tx_app_mode_list_str = json.dumps(tx_app_modes)

            rx_bw = self.app_ref.fft_bw_map.get(self.app_ref.fft_rx_bw_combo.get())
            rx_guard = self.app_ref.fft_rx_guard_freq_entry.get()
            rx_app_modes = [self.app_ref.fft_app_mode_map.get(combo['combo'].get())
                            for combo in self.app_ref.fft_rx_app_mode_combos if combo['frame'].winfo_ismapped()]
            rx_app_mode_list_str = json.dumps(rx_app_modes)

            # Sección 3
            input_l = self.app_ref.fft_input_level_entry.get()
            power_b = self.app_ref.fft_power_boosting_entry.get()
            output_l = self.app_ref.fft_output_level_entry.get()

            # Validaciones básicas (puedes añadir más si quieres)
            if not all([local_p, remote_p, snr_act, snr_deact, tx_bw, tx_guard, rx_bw, rx_guard, input_l, power_b, output_l]):
                    raise ValueError("Faltan campos obligatorios.")
            # TODO: Añadir validaciones de rangos numéricos si es necesario

        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error recopilando datos FFT: {e}", "red"))
            self.app_ref.run_button_state(is_running=False)
            return

        # *** Ejecutar los tests Robot secuencialmente con un FOR mas adelante *** Para ello creamos un vector de tuplas, definidas por los () 
        tests_to_run = [
            ("Program IBTU FFT S1 General", [
                f"LOCAL_PERIODICITY:{local_p}", f"REMOTE_PERIODICITY:{remote_p}",
                f"SNR_THRESHOLD_ACTIVATION:{snr_act}", f"SNR_THRESHOLD_DEACTIVATION:{snr_deact}",
                f"RX_OPERATION_MODE_LIST_STR:{rx_op_mode_list_str}"
            ]),
            ("Program IBTU FFT S2 General", [
                f"TX_BW:{tx_bw}", f"TX_GUARD_FREQ:{tx_guard}", f"TX_APPLICATION_MODE_LIST_STR:{tx_app_mode_list_str}",
                f"RX_BW:{rx_bw}", f"RX_GUARD_FREQ:{rx_guard}", f"RX_APPLICATION_MODE_LIST_STR:{rx_app_mode_list_str}"
            ]),
            ("Program IBTU FFT S3 General", [
                f"INPUT_LEVEL:{input_l}", f"POWER_BOOSTING:{power_b}", f"OUTPUT_LEVEL:{output_l}"
            ])
        ]

        all_passed = True
        for test_name, variables in tests_to_run: # Las dos variables que recorremos son cada una de las tuplas de la lista de tests "tests_to_run" 
            self.app_ref.gui_queue.put(('main_status', f"Ejecutando {test_name}...", "orange"))
            # Ejecutamos el test y esperamos a que termine antes de pasar al siguiente
            # El listener interno manejará el estado final (pass/fail)
            success = robot_executor._run_robot_test(
                self.app_ref,
                test_name=test_name,
                session_id=active_id,
                preferred_filename="Module_IBTU_FFT.robot",
                variables=variables,
                # No necesitaremos on_success aquí, solo necesitamos saber si pasó o falló, ya que no necesitamos rellenar ninguna función callback.
                on_pass_message=f"{test_name} completado.",
                on_fail_message=f"Fallo en {test_name}.",
                # ¡Importante! Poner block=True para que espere
                block=True 
            )
            if not success:
                all_passed = False
                # Podríamos detener la secuencia si uno falla. Aunque preferimos que acabe de programar el resto por el momento.
                # self.app_ref.gui_queue.put(('main_status', f"Secuencia FFT detenida por fallo en {test_name}.", "red"))
                # break 

        # Mensaje final (independiente del estado de ejecución, que es manejado por el listener)
        if all_passed:
                self.app_ref.gui_queue.put(('main_status', "Programación IBTU FFT completada.", "green"))
        else:
                self.app_ref.gui_queue.put(('main_status', "Programación IBTU FFT completada con errores.", "orange"))

        # Importante: run_button_state(False) ya es llamado por el listener al final de _run_robot_test
        # Si no usas block=True, necesitarías llamarlo aquí después del último hilo.