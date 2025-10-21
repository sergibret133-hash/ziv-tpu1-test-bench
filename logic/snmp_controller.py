import threading
import logic.robot_executor as robot_executor # Necesitará llamar al ejecutor
import json

class SNMPController:
    def __init__(self, app_ref):
        self.app_ref = app_ref
        
        
    def _run_retrieve_snmp_config_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_snmp_config, daemon=True).start()
        
    def _execute_retrieve_snmp_config(self):
        """Runs the test to get current SNMP configuration."""
        test_name="Retrieve Full SNMP Configuration"
        
        self.app_ref.is_main_task_running = True 
        
        try:
            # Buscamos la info de actualizacion de la GUI en nuestro mapa inicializado en init (el mismo que usa el planificador cuando ejecuta los tests)
            gui_update_info = self.app_ref.test_gui_update_map.get(test_name)
            success_callback = None
            
            if gui_update_info: #si se encuentra, CREAMOS EL CALLBACK DINAMICO (de esta forma evitamos repetir codigo y amortizamos el mapeo que hacemos con el diccionario de tests)
                message_type, attr_names = gui_update_info

            #*********************************************************************************************************
                # Utilizamos el método de creación de  callback dinamico
                success_callback = self.app_ref._create_gui_update_callback(message_type, attr_names)
            #*********************************************************************************************************
            robot_executor._run_robot_test(
                self.app_ref,
                test_name=test_name,
                preferred_filename="Test3_SNMP.robot",
                on_success=success_callback,
                on_pass_message="Configuración SNMP consultada con éxito!",
                on_fail_message="Fallo al consultar la configuración SNMP!"
            )
            
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _run_execute_snmp_config_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_execute_snmp_config, daemon=True).start()
        
    def _execute_execute_snmp_config(self):
        """Reads the GUI fields and runs the test to program SNMP settings."""
        self.app_ref.is_main_task_running = True
        
        try:
            hosts_config_list = []
            for host in self.app_ref.host_widgets:
                host_enable = '1' if host['enable'].get() == 1 else '0'
                ip_address = host['ip'].get()
                port = host['port'].get()
                trap_mode_str = host['mode'].get()
                trap_mode = self.app_ref.trap_mode_map.get(trap_mode_str, '1')
                hosts_config_list.append([host_enable, ip_address, port, trap_mode])

            hosts_config_str = json.dumps(hosts_config_list)

            variables = [
                f"SNMP_AGENT_STATE:{self.app_ref.snmp_agent_state_cb.get()}",
                f"TRAPS_ENABLE_STATE:{self.app_ref.traps_enable_state_cb.get()}",
                f"TPU_SNMP_PORT:{self.app_ref.tpu_snmp_port_entry.get()}",
                f"SNMP_V1_V2_ENABLE:{self.app_ref.snmp_v1_v2_enable_cb.get()}",
                f"SNMP_V1_V2_READ:{self.app_ref.snmp_v1_v2_read_entry.get()}",
                f"SNMP_V1_V2_SET:{self.app_ref.snmp_v1_v2_set_entry.get()}",
                f"SNMP_V3_ENABLE:{self.app_ref.snmp_v3_enable_cb.get()}",
                f"SNMP_V3_READ_USER:{self.app_ref.snmp_v3_read_user_entry.get()}",
                f"SNMP_V3_READ_PASS:{self.app_ref.snmp_v3_read_pass_entry.get()}",
                f"SNMP_V3_READ_AUTH:{self.app_ref.snmp_v3_read_auth_entry.get()}",
                f"SNMP_V3_WRITE_USER:{self.app_ref.snmp_v3_write_user_entry.get()}",
                f"SNMP_V3_WRITE_PASS:{self.app_ref.snmp_v3_write_pass_entry.get()}",
                f"SNMP_V3_WRITE_AUTH:{self.app_ref.snmp_v3_write_auth_entry.get()}",
                f"HOSTS_CONFIG_STR:{hosts_config_str}"
            ]

            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Execute Full SNMP Configuration",
                preferred_filename="Test3_SNMP.robot",
                variables=variables,
                on_pass_message="Configuración SNMP programada con éxito!",
                on_fail_message="Fallo al programar la configuración SNMP!"
            )
            
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))