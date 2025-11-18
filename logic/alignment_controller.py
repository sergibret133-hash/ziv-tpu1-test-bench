import threading
import logic.robot_executor as robot_executor
import json

class AlignmentController:
    def __init__(self, app_ref):
        self.app_ref = app_ref
    
    # ********

    def _run_retrieve_inputs_state_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_inputs_state, daemon=True).start()

    def _execute_retrieve_inputs_state(self):
        """Runs the test to get the current state of the inputs."""
        test_name="Retrieve Inputs Activation State"
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
                preferred_filename="Test4_Alignment.robot",
                on_success=success_callback,
                # on_success=lambda listener: app_ref.gui_queue.put(('update_input_activation_display', listener.input_activation_state, listener.input_info)),    # COMO UTILIZAMOS EL MAPA Y LA FUNCION CALLBACK, LO HACEMOS DIFERENTE
                on_pass_message="Estado de entradas consultado con éxito!",
                on_fail_message="Fallo al consultar el estado de las entradas."
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
            
    def _run_program_inputs_state_thread(self):
        """Validates the requested action and then starts the thread to run the test."""


        # Leemos las casillas de verificación
        inputs_list = []
        # 'input_activation_checkboxes' -> lista de CTkCheckBox guardada en app_ref
        for i, checkbox in enumerate(self.app_ref.input_activation_checkboxes):
            inputs_list.append(1 if checkbox.get() == 1 else 0)

        if self.app_ref.inputs_are_active is None:
            self.app_ref.gui_queue.put(('main_status', "Error: Consulte primero el estado de las entradas.", "red"))
            self.app_ref.run_button_state(is_running=False)
            return
        
        
        #   Leemos los RadioButtons "Activar" / "Desactivar"
        # 'activation_mode_var' es el StringVar que creamos en la GUI
        activation_mode = self.app_ref.activation_mode_var.get() # "activate" o "deactivate"
        activate_deactivate_flag = "1" if activation_mode == "activate" else "0"

        
        # Leemos la duración
        # 'input_activation_duration_combo' es el ComboBox de la GUI
        duration_key = self.app_ref.input_activation_duration_combo.get()
        duration_value = self.app_ref.duration_map.get(duration_key, "0") # "0", "5", "10", "30", "60"
        
        if activate_deactivate_flag == "0":
            duration_value = "0"
        
        # Convertimos la lista de inputs a un string JSON para pasarla
        inputs_list_str = json.dumps(inputs_list)
        
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(
            target=self._execute_program_inputs_activation,
            args=(activate_deactivate_flag, duration_value, inputs_list_str, inputs_list),
            daemon=True
            ).start()


    def _execute_program_inputs_activation(self, activate_deactivate_flag, duration, inputs_list_str, inputs_list_py):
        """Runs the input activation test.
        argument notation:
        inputs_list_str: JSON string representing the list of inputs
        inputs_list_py: Python list representing the list of inputs"""
        self.app_ref.is_main_task_running = True
        active_id = self.app_ref.active_session_id

        if activate_deactivate_flag == "1" and self.app_ref.inputs_are_active:
            self.app_ref.gui_queue.put(('main_status', "Aviso: Las entradas ya se encuentran activas.", "orange"))
            self.app_ref.run_button_state(is_running=False)
            return

        elif activate_deactivate_flag == "0" and not self.app_ref.inputs_are_active:
            self.app_ref.gui_queue.put(('main_status', "Aviso: Las entradas ya se encuentran inactivas.", "orange"))
            self.app_ref.run_button_state(is_running=False)
            return
        
        
        try:
            variables = [
                f"ACTIVATE_DEACTIVATE:{activate_deactivate_flag}",
                f"DURATION:{duration}",
                f"INPUTS_LIST:{inputs_list_str}"
            ]

            def on_success_callback(listener):
                self.app_ref.gui_queue.put(('program_inputs_success', active_id, activate_deactivate_flag, duration, inputs_list_py))

            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Input Activation",
                session_id=active_id,
                preferred_filename="Test4_Alignment.robot",
                variables=variables,
                on_success=on_success_callback,
                on_pass_message="Operación de activación de entradas completada.",
                on_fail_message="Fallo en la operación de activación de entradas."
            )
        
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
        
        
        # *********** LOOP / BLOCKING ************

    def _run_refresh_alignment_states_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_refresh_alignment_states, daemon=True).start()
 
    def _execute_refresh_alignment_states(self):
        """Runs a single test to get all loop and blocking states."""
        test_name = "Current Loop and Blocking State"
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
                preferred_filename="Test4_Alignment.robot",
                on_success=success_callback,
                on_pass_message="Estados de alineación consultados.",
                on_fail_message="Fallo al consultar estados de alineación."
            )
            
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))

    def _run_program_loop_thread(self, tp_number, activate):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_loop, args=(tp_number, activate), daemon=True).start()
        
    def _execute_program_loop(self, tp_number, activate):
        """Gathers data and runs the Program Teleprotection Loop test."""
        self.app_ref.is_main_task_running = True
        active_id = self.app_ref.active_session_id
        try:
            activate_deactivate = '1' if activate else '0'
            
            widgets = self.app_ref._get_alignment_widgets(tp_number, is_loop=True)
            
            is_currently_active = "Activo" in widgets['status_label'].cget("text")
            if (activate and is_currently_active) or (not activate and not is_currently_active):
                status = "activo" if is_currently_active else "inactivo"
                self.app_ref.gui_queue.put(('main_status', f"Aviso: El bucle TP{tp_number} ya está {status}.", "orange"))
                self.app_ref.gui_queue.put(('enable_buttons', None))
                return

            loop_type_str = widgets['type_combo'].get()
            duration_str = widgets['duration_combo'].get()
            
            loop_type = self.app_ref.loop_type_map.get(loop_type_str, '0')
            duration = self.app_ref.duration_map.get(duration_str, '0')

            variables = [
                f"LOOP_TELEPROTECTION_NUMBER:{tp_number}",
                f"ACTIVATE_DEACTIVATE_LOOP:{activate_deactivate}",
                f"LOOP_TYPE:{loop_type}",
                f"LOOP_DURATION:{duration}"
            ]
            def on_success_callback(listener):
                self.app_ref.gui_queue.put(('program_alignment_success', tp_number, True, activate, duration))

            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Program Teleprotection Loop",
                session_id=active_id,
                preferred_filename="Test4_Alignment.robot",
                variables=variables,
                on_success=on_success_callback,
                on_pass_message=f"Bucle TP{tp_number} programado con éxito.",
                on_fail_message=f"Fallo al programar bucle TP{tp_number}."
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _run_program_blocking_thread(self, tp_number, activate):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_program_blocking, args=(tp_number, activate), daemon=True).start()


    def _execute_program_blocking(self, tp_number, activate):
        """Gathers data and runs the Program Teleprotection Blocking test."""
        self.app_ref.is_main_task_running = True
        active_id = self.app_ref.active_session_id
        try:
            activate_deactivate = '1' if activate else '0'

            widgets = self.app_ref._get_alignment_widgets(tp_number, is_loop=False)

            is_currently_active = "Activo" in widgets['status_label'].cget("text")
            if (activate and is_currently_active) or (not activate and not is_currently_active):
                status = "activo" if is_currently_active else "inactivo"
                self.app_ref.gui_queue.put(('main_status', f"Aviso: El bloqueo TP{tp_number} ya está {status}.", "orange"))
                self.app_ref.gui_queue.put(('enable_buttons', None))
                return

            duration_str = widgets['duration_combo'].get()
            duration = self.app_ref.duration_map.get(duration_str, '0')

            variables = [
                f"BLOCKING_TELEPROTECTION_NUMBER:{tp_number}",
                f"ACTIVATE_DEACTIVATE_BLOCKING:{activate_deactivate}",
                f"BLOCKING_DURATION:{duration}"
            ]
            
            def on_success_callback(listener):
                self.app_ref.gui_queue.put(('program_alignment_success', tp_number, False, activate, duration))

            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Program Teleprotection Blocking",
                session_id=active_id,
                preferred_filename="Test4_Alignment.robot",
                variables=variables,
                on_success=on_success_callback,
                on_pass_message=f"Bloqueo TP{tp_number} programado con éxito.",
                on_fail_message=f"Fallo al programar bloqueo TP{tp_number}."
            )
            
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _handle_program_alignment_success(self, tp_number, is_loop, is_activating, duration):
        """Updates the UI after a loop/blocking is programmed and manages timers."""
        timer_key = f"{'loop' if is_loop else 'block'}_{tp_number}"
        widgets = self.app_ref._get_alignment_widgets(tp_number, is_loop)

        if timer_key in self.app_ref.alignment_timers:
            self.app_ref.after_cancel(self.app_ref.alignment_timers[timer_key])
            del self.app_ref.alignment_timers[timer_key]

        self.app_ref._update_alignment_row_ui(widgets, is_activating, is_loop)

        if is_activating and duration != "0":
            duration_sec = int(duration)
            widgets['timer_label'].pack(anchor="w")
            
            self.app_ref.start_alignment_countdown(duration_sec, timer_key)
            
            
    # HIL CONTROLLER
    # def run_hil_pulse(self):
    #     """
    #     Lee las casillas de 'Input Activation' y envía un comando PULSE_BATCH a la Raspberry Pi.
    #     """
    #     if self.app_ref.is_main_task_running:
    #         self.app_ref.gui_queue.put(('main_status', "Error: Ya hay una tarea en ejecución.", "red"))
    #         return

    #     session_id = self.app_ref.active_session_id
        
    #     try:
    #         # Obtenemos la IP de la Raspberry
    #         ip_address = self.app_ref.rpi_ip_entry.get()
    #         if not ip_address:
    #             self.app_ref.gui_queue.put(('main_status', "Error: Introduzca la IP de la Raspberry Pi.", "red"))
    #             return
                
    #         # Obtenemos la duración del pulso HIL
    #         duration_str = self.app_ref.hil_pulse_duration_entry.get()
    #         if not duration_str:
    #             self.app_ref.gui_queue.put(('main_status', "Error: Introduzca una duración para el pulso HIL.", "red"))
    #             return
            
    #         # Validamos que la duración sea un número
    #         try:
    #             duration_val = float(duration_str)
    #             if duration_val <= 0: raise ValueError
    #         except ValueError:
    #             self.app_ref.gui_queue.put(('main_status', f"Error: Duración debe ser un numero válido: '{duration_str}'. Usar ej: 0.5", "red"))
    #             return
                
    #         # Leemos las casillas de verificación
    #         # Como input_activation_checkboxes guarda una lista donde cada posicion tiene asignada el input correspondiente y lo que tenemos que pasar nosotros es una lista CON EL NUM INPUTS QUE QUEREMOS ACTIVAR
    #         # Recorremos la lista y donde haya un input que queramos activar, nos quedamos con la posición que nos situamos en el vector (+1 ya que comenzamos en 0)
    #         checked_inputs = []
    #         for i, checkbox in enumerate(self.app_ref.input_activation_checkboxes):     # En cada iteracion, enumerate() va recorriendo input_activation_checkboxes y nos devuelve las dos variables: i, checkbox
    #             if checkbox.get() == 1:     # Utilizamos get() porque es la forma de acceder a un elemento de Tkinter
    #                 checked_inputs.append(str(i + 1)) # Añadimos el ID del input

    #         if not checked_inputs:
    #             self.app_ref.gui_queue.put(('main_status', "Error: Ningún input HIL seleccionado.", "red"))
    #             return

    #         # Construimos el comando BATCH
    #         # Ej: "PULSE_BATCH 0.5 1 3 4"
    #         command_str = f"PULSE_BATCH {duration_val} {' '.join(checked_inputs)}"      #' '.join introduce unn espacio (' ') entre cada elemento de la lista 

    #     except AttributeError as e:
    #         self.app_ref.gui_queue.put(('main_status', f"Error: Faltan widgets de HIL en la GUI. {e}", "red"))
    #         return
    #     except Exception as e:
    #         self.app_ref.gui_queue.put(('main_status', f"Error preparando comando HIL: {e}", "red"))
    #         return

    #     print(f"Iniciando test HIL '{command_str}' en la IP {ip_address} para la sesión {session_id}")

    #     self.app_ref.run_button_state(is_running=True)

    #     # Iniciamos el hilo que ejecuta el test
    #     threading.Thread(
    #         target=self._execute_hil_pulse, 
    #         args=(session_id, ip_address, command_str),
    #         daemon=True
    #     ).start()
        
        
        
        
    def run_hil_burst(self):
        """
        Lee las casillas de 'Input Activation' y los parametros de rafaga para enviar un comando BURST_BATCH a la Raspberry Pi.
        """
        if self.app_ref.is_main_task_running:
            self.app_ref.gui_queue.put(('main_status', "Error: Ya hay una tarea en ejecución.", "red"))
            return

        session_id = self.app_ref.active_session_id
        
        try:
            # Obtenemos la IP de la Raspberry
            ip_address = self.app_ref.rpi_ip_entry.get()
            if not ip_address:
                self.app_ref.gui_queue.put(('main_status', "Error: Introduzca la IP de la Raspberry Pi.", "red"))
                return
                
            # Obtenemos los parametros de la rafaga HIL
            num_pulses_str = self.app_ref.hil_pulses_entry.get()                       
            duration_str = self.app_ref.hil_pulse_duration_entry.get()
            delay_str = self.app_ref.hil_pulse_delay_entry.get()
            
            if not all([num_pulses_str, duration_str, delay_str]):
                self.app_ref.gui_queue.put(('main_status', "Error: Rellene num. pulsos, duración y delay.", "red"))
                return
            
            # Validamos que los paeametros sean números
            try:
                num_pulses = str(int(num_pulses_str))
                duration_val = str(float(duration_str))
                loop_delay = str(float(delay_str))
                
                if int(num_pulses) <= 0 or float(duration_val)<= 0 or float(loop_delay)<= 0:
                    raise ValueError
            except ValueError:
                self.app_ref.gui_queue.put(('main_status', f"Error: Parámetros de ráfaga deben ser números positivos", "red"))
                return
                
            # Leemos las casillas de verificación
            # Como input_activation_checkboxes guarda una lista donde cada posicion tiene asignada el input correspondiente y lo que tenemos que pasar nosotros es una lista CON EL NUM INPUTS QUE QUEREMOS ACTIVAR
            # Recorremos la lista y donde haya un input que queramos activar, nos quedamos con la posición que nos situamos en el vector (+1 ya que comenzamos en 0)
            checked_inputs = []
            for i, checkbox in enumerate(self.app_ref.input_activation_checkboxes):     # En cada iteracion, enumerate() va recorriendo input_activation_checkboxes y nos devuelve las dos variables: i, checkbox
                if checkbox.get() == 1:     # Utilizamos get() porque es la forma de acceder a un elemento de Tkinter
                    checked_inputs.append(str(i + 1)) # Añadimos el ID del input

            if not checked_inputs:
                self.app_ref.gui_queue.put(('main_status', "Error: Ningún input HIL seleccionado.", "red"))
                return


            # Convertimos la lista de inputs a un string separado por comas
            channels_str = ",".join(checked_inputs)


        except AttributeError as e:
            self.app_ref.gui_queue.put(('main_status', f"Error: Faltan widgets de HIL en la GUI. {e}", "red"))
            return
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error preparando comando HIL: {e}", "red"))
            return

        print(f"Iniciando test HIL en la IP {ip_address} para la sesión {session_id}")

        self.app_ref.run_button_state(is_running=True)

        # Iniciamos el hilo que ejecuta el test
        threading.Thread(
            target=self._execute_hil_burst, 
            args=(session_id, ip_address, channels_str, num_pulses, duration_val, loop_delay),
            daemon=True
        ).start()
        
        
    
    # def _execute_hil_pulse(self, session_id, ip_address, command_str):
    #         """
    #         Ejecuta el test de envío de pulso HIL en un hilo separado.
    #         Args:
    #             session_id (str): ID de la sesión activa.
    #             ip_address (str): Dirección IP de la Raspberry Pi.
    #             command_str (str): Comando de pulso HIL a enviar. Disponible en formato "PULSE_BATCH duration input1 input2 ...".
    #         """
    #         self.app_ref.is_main_task_running = True
            
    #         try:
    #             print(f"Iniciando test HIL '{command_str}' en la IP {ip_address} para la sesión {session_id}")

    #             variables = [
    #                 f"RASPBERRY_PI_IP:{ip_address}",
    #                 f"COMMAND_STR:{command_str}"
    #             ]

    #             robot_executor._run_robot_test(
    #                 self.app_ref,
    #                 "Send Input Command",
    #                 session_id,
    #                 variables,
    #                 on_success=None, 
    #                 on_pass_message="Pulso(s) HIL enviado(s)",
    #                 on_fail_message="Fallo al enviar pulso(s) HIL"
    #             )
            
    #         except Exception as e:
    #             self.app_ref.gui_queue.put(('main_status', f"Error en la tarea HIL: {e}", "red")) 
                
    #         finally:
    #             self.app_ref.is_main_task_running = False
    #             self.app_ref.gui_queue.put(('enable_buttons', None))
    
    def _execute_hil_burst(self, session_id, ip_address, channels_str, num_pulses, duration_val, loop_delay):
        """
        Ejecuta el test de envío de rafaga HIL en un hilo separado.
        Args:
            session_id (str): ID de la sesión activa.
            ip_address (str): Dirección IP de la Raspberry Pi.
            parametros (str): channels_str, num_pulses, duration_val, loop_delay".
        """
        self.app_ref.is_main_task_running = True
        
        try:
            print(f"Iniciando test HIL en la IP {ip_address} para la sesión {session_id}")

            variables = [
                f"RASPBERRY_PI_IP:{ip_address}",
                f"CHANNELS_STR:{channels_str}",
                f"NUM_PULSES:{num_pulses}",
                f"PULSE_DURATION:{duration_val}",
                f"LOOP_DELAY:{loop_delay}",
            ]

            robot_executor._run_robot_test(
                self.app_ref,
                "Ejecutar Rafaga GUI",
                session_id,
                variables,
                on_success=None, 
                on_pass_message="Rafaga HIL enviada",
                on_fail_message="Fallo al enviar Rafaga HIL"
            )
        
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea HIL: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))