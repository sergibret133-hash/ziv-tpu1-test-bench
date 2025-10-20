import threading
import os
from pathlib import Path
import asyncio


class TrapListenerController:
    def __init__(self, app_ref):
        self.app_ref = app_ref


    def _start_snmp_listener_thread(self):
        self.app_ref.run_button_state(is_running=True)
        self.app_ref.snmp_listener_thread = threading.Thread(target=self._execute_start_listener, daemon=True)
        self.app_ref.snmp_listener_thread.start()

    def _execute_start_listener(self):
        """Starts the SNMP trap listener using the Python library directly."""
        try:
            print("--- 1. Entrando en _execute_start_listener ---")
            # asyncio.set_event_loop(asyncio.new_event_loop())

            ip = self.app_ref.snmp_ip_entry.get()
            port = int(self.app_ref.snmp_port_entry.get())
            print(f"--- 2. IP y Puerto obtenidos: {ip}:{port} ---")

            script_dir = os.path.dirname(os.path.abspath(__file__))
            mib_dir = os.path.join(script_dir, "compiled_mibs")
            mib_uri = Path(mib_dir).as_uri()
            
            if not os.path.isdir(mib_dir):
                error_msg = f"Error: Directorio MIBs no encontrado en {mib_dir}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
                self.app_ref.gui_queue.put(('enable_buttons', None))
                print("--- ERROR: Directorio MIB no encontrado ---")
                return
            
            print("--- 3. Llamando a trap_receiver.start_trap_listener... ---") 
            
            self.app_ref.trap_receiver.start_trap_listener(listen_ip=ip, listen_port=port, mib_dirs_string=mib_uri)
            print("--- 4. start_trap_listener HA TERMINADO. Cargando MIBs... ---")  
            try:
                self.app_ref.trap_receiver.load_mibs("DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB")
                self.app_ref.gui_queue.put(('snmp_listener_status', "Listener: Ejecutando", "green"))
                self.app_ref.gui_queue.put(('main_status', f"Listener SNMP iniciado en {ip}:{port}", "#2ECC71"))
            except Exception as e_mibs:
                error_msg = f"ADVERTENCIA: Error cargando MIBs: {repr(e_mibs)}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "orange"))

        except Exception as e_start:
            error_msg = f"Error al iniciar listener: {repr(e_start)}"
            print(f"!!! GUI ERROR (Start): {error_msg}")
            self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
            self.app_ref.gui_queue.put(('snmp_listener_status', 'Listener: Error', 'red'))
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
            self.app_ref.gui_queue.put(('main_status', f"Error al detener listener: {e}", "red"))
        finally:
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
        
    