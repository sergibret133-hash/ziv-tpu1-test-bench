import threading
import os
from pathlib import Path
import asyncio
import json

class TrapListenerController:
    def __init__(self, app_ref):
        self.app_ref = app_ref

    def is_listener_running(self):
        """
        Comprueba si el listener de traps está activo.
        Lee la variable de estado de app_ref.
        """
        if hasattr(self.app_ref, 'is_snmp_listener_running'):
            return self.app_ref.is_snmp_listener_running
        return False
    
    def check_and_clear_new_traps(self, oid_to_check=None):
        """
        Verifica los traps recibidos desde la última comprobación y los limpia.
        
        Args:
            oid_to_check (str, optional): Si nos lo dan, buscamos este OID específico en los traps recibidos. 

        Returns:
            bool: True si la condición se cumple (traps recibidos genéricos, o trap específico encontrado), False en caso contrario.
        """
        
        if not hasattr(self.app_ref, 'trap_receiver'):
            print("ERROR: trap_receiver no encontrado en app_ref.")
            return (False,[],[])

        # Obtenemos todos los traps actuales
        try:
            received_traps = self.app_ref.trap_receiver.get_all_raw_received_traps()
        except Exception as e:
            print(f"Error al obtener traps: {e}")
            return (False,[],[])
            
        # Limpiamos la lista interna del listener INMEDIATAMENTE
        try:
            self.app_ref.trap_receiver.clear_all_received_traps()
        except Exception as e:
            print(f"Error al limpiar traps: {e}")
            # Continuamos para procesar lo que ya obtuvimos
            
        # Comprobamos si hemos recibido algo
        if not received_traps:
            return (False,[],[]) # No hemos recibido nada

        # Si la tarea era solo para verificar si hubo algo..
        if oid_to_check is None:
            return (True,received_traps,received_traps) # Sí, se recibieron traps (devolvemos todos)

        # Si la tarea buscaba un OID específico
        found_matching_traps = []

        for trap_obj in received_traps:
            # Convertir el trap a string para una búsqueda simple en caso de que nos llegue el trap como diccionario
            trap_message_str = ""
            if isinstance(trap_obj, dict):
                trap_message_str = json.dumps(trap_obj)
            # Si nos llega como str, lo dejamos tal cual
            elif isinstance(trap_obj, str):
                trap_message_str = trap_obj

            if oid_to_check in trap_message_str:    # Comprobamos si el OID coincide..
                found_matching_traps.append(trap_obj) # Guardamos el objeto original
        
        
        if found_matching_traps:
            return (True, found_matching_traps, received_traps) # ¡Encontrado! Devolvemos solo los que coinciden
        else:
            return (False, [], received_traps) # No encontramos el OID específico
        
        
    def _start_snmp_listener_thread(self):
        self.app_ref.run_button_state(is_running=True)
        self.app_ref.snmp_listener_thread = threading.Thread(target=self._execute_start_listener, daemon=True)
        self.app_ref.snmp_listener_thread.start()

    def _execute_start_listener(self):
        """Starts the SNMP trap listener using the Python library directly."""
        try:
            print("*** Entrando en _execute_start_listener ***")
            # asyncio.set_event_loop(asyncio.new_event_loop())

            ip = self.app_ref.snmp_ip_entry.get()
            port = int(self.app_ref.snmp_port_entry.get())
            print(f"*** IP y Puerto obtenidos: {ip}:{port} ***")

            script_dir = os.path.dirname(os.path.abspath(__file__))
            mib_dir = os.path.join(script_dir, "compiled_mibs")
            mib_uri = Path(mib_dir).as_uri()
            
            if not os.path.isdir(mib_dir):
                error_msg = f"Error: Directorio MIBs no encontrado en {mib_dir}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
                self.app_ref.gui_queue.put(('enable_buttons', None))
                print("*** ERROR: Directorio MIB no encontrado ***")
                self.app_ref.is_snmp_listener_running = False
                return
            
            print("*** Llamando a trap_receiver.start_trap_listener... ***") 
            
            self.app_ref.trap_receiver.start_trap_listener(listen_ip=ip, listen_port=port, mib_dirs_string=mib_uri)
            print("*** start_trap_listener HA TERMINADO. Cargando MIBs... ***")  
            try:
                self.app_ref.trap_receiver.load_mibs("DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB")
                self.app_ref.is_snmp_listener_running = True
                self.app_ref.gui_queue.put(('snmp_listener_status', "Listener: Ejecutando", "green"))
                self.app_ref.gui_queue.put(('main_status', f"Listener SNMP iniciado en {ip}:{port}", "#2ECC71"))
                self.app_ref.is_snmp_listener_running = True
            except Exception as e_mibs:
                error_msg = f"ADVERTENCIA: Error cargando MIBs: {repr(e_mibs)}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "orange"))
                self.app_ref.is_snmp_listener_running = True

        except Exception as e_start:
            self.app_ref.is_snmp_listener_running = False
            error_msg = f"Error al iniciar listener: {repr(e_start)}"
            print(f"!!! GUI ERROR (Start): {error_msg}")
            self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
            self.app_ref.gui_queue.put(('snmp_listener_status', 'Listener: Error', 'red'))
            self.app_ref.is_snmp_listener_running = False
        finally:
            self.app_ref.gui_queue.put(('enable_buttons', None))

    def _stop_snmp_listener_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_stop_listener, daemon=True).start()

    def _execute_stop_listener(self):
        """Stops the SNMP trap listener."""
        try:
            self.app_ref.trap_receiver.stop_trap_listener()
            self.app_ref.gui_queue.put(('snmp_listener_status', 'Listener: Detenido', 'red'))
            self.app_ref.gui_queue.put(('main_status', "Listener SNMP detenido.", "orange"))
        except Exception as e:
            self.app_ref.is_snmp_listener_running = False
            self.app_ref.gui_queue.put(('main_status', f"Error al detener listener: {e}", "red"))
        finally:
            self.app_ref.is_snmp_listener_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))

    def _show_all_traps(self):
        traps = self.app_ref.trap_receiver.get_all_raw_received_traps()
        self.app_ref.update_trap_display(traps)
        self.app_ref._update_status("Traps en vivo actualizados.", "white")

    def _filter_traps(self):
        filter_text = self.app_ref.snmp_filter_entry.get()
        traps = self.app_ref.trap_receiver.get_filtered_traps_by_text(filter_text)
        self.app_ref.update_trap_display(traps)
        self.app_ref._update_status(f"Mostrando traps filtrados por '{filter_text}'.", "white")

    def _reset_traps(self):
        self.app_ref.trap_receiver.clear_all_received_traps()
        self.app_ref.update_trap_display([])
        self.app_ref._update_status("Traps en vivo borrados.", "white")
    
    # Para poder captar los traps y compararlos en la Correlacion de Eventos de traps SNMP con eventos del Registro Cronológico, NECESITAMOS REALIZAR UNA FUNCION NUEVA QUE OBTENGA LOS DATOS QUE DESDE LA GUI, 
    # Y NO DIRECTAMENTE DESDE  _show_all_traps (YA QUE PUEDE INTERFERIR CON EL FUNCIONAMIENTO DE LA GUI)
    def get_raw_traps_for_correlation(self):
            """Obtiene los traps crudos recibidos sin actualizar la GUI."""
            if self.app_ref.trap_receiver:
                # Llama al método que realmente tiene los datos en Trap_Receiver_GUI_oriented
                return self.app_ref.trap_receiver.get_all_raw_received_traps()
            return []
    