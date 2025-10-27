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
            
            
    def _run_program_inputs_activation_thread(self):
        """Validates the requested action and then starts the thread to run the test."""
        self.app_ref.run_button_state(is_running=True)

        if self.app_ref.inputs_are_active is None:
            self.app_ref.gui_queue.put(('main_status', "Error: Consulte primero el estado de las entradas.", "red"))
            self.app_ref.run_button_state(is_running=False)
            return

        action_to_perform = self.app_ref.activation_mode_var.get()

        if action_to_perform == "activate" and self.app_ref.inputs_are_active:
            self.app_ref.gui_queue.put(('main_status', "Aviso: Las entradas ya se encuentran activas.", "orange"))
            self.app_ref.run_button_state(is_running=False)
            return

        if action_to_perform == "deactivate" and not self.app_ref.inputs_are_active:
            self.app_ref.gui_queue.put(('main_status', "Aviso: Las entradas ya se encuentran inactivas.", "orange"))
            self.app_ref.run_button_state(is_running=False)
            return

        threading.Thread(target=self._execute_program_inputs_activation, daemon=True).start()


    def _execute_program_inputs_activation(self):
        """Gathers data from the GUI and runs the input activation test. Assumes validation has passed."""
        self.app_ref.is_main_task_running = True
        active_id = self.app_ref.active_session_id
        try:
            activate_deactivate = "1" if self.app_ref.activation_mode_var.get() == "activate" else "0"
            duration_str = self.app_ref.duration_combobox.get()
            duration = self.app_ref.duration_map.get(duration_str, "0")

            inputs_list = [1 if cb.get() == 1 else 0 for cb in self.app_ref.input_activation_checkboxes]
            inputs_list_str = json.dumps(inputs_list)

            variables = [
                f"ACTIVATE_DEACTIVATE:{activate_deactivate}",
                f"DURATION:{duration}",
                f"INPUTS_LIST:{inputs_list_str}"
            ]

            def on_success_callback(listener):
                self.app_ref.gui_queue.put(('program_inputs_success', activate_deactivate, duration, inputs_list))

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