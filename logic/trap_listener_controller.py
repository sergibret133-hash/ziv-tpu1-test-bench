import threading
import os
from pathlib import Path
import asyncio
import json

class TrapListenerController:
    def __init__(self, app_ref):
        self.app_ref = app_ref

    def is_listener_running(self, session_id):
        """
        Comprueba si el listener de traps está activo para una sesion especifica.
        Lee la variable de estado de app_ref.
        """
        if hasattr(self.app_ref, 'trap_listeners') and session_id in self.app_ref.trap_listeners:
            return self.app_ref.trap_listeners[session_id].get('is_running', False)     # Si no encuentra el valor de la clave pasada, devolvemos False por defecto
        return False
    # Para la tarea de verificación de traps sin borrado previo del SchedulerController
    def check_traps_without_clearing(self, session_id, oid_to_check=None):
        """
        Verifica los traps recibidos desde la última comprobación.
        
        Args:
            session_id (str): 'A' o 'B' para identificar el listener.
            oid_to_check (str, optional): Si nos lo dan, buscamos este OID específico en los traps recibidos. 

        Returns:
            tuple: (bool: True/False, list: traps_encontrados)        
        """
        # Para hacer borrado de traps y recolección de los nuevos tenemos que asegurarnos de que existan los diccionarios de los listeners de las dos sesiones (listener_info) y que haya Listener dentro de esa sesion (trap_receiver)
        # Comprobamos que el listener exista para la sesion que nos pasan.
        listener_info = self.app_ref.trap_listeners.get(session_id)

        if not listener_info:
            print(f"ERROR: No trap listener info found for session {session_id}.")
            return (False,[])    # tuple
        
            # Comprobamos que haya asignado la clase TrapReceiver en la clave reservada para el diccionario listener_indo de la sesion que nos pasan
        trap_receiver = listener_info['trap_receiver']
        if not trap_receiver:
            print(f"ERROR: trap_receiver no encontrado en app_ref para la session {session_id}.")
            return (False,[])

        # ******** Obtenemos todos los traps para borrarlos posteriormente ********
        try:
            received_traps = trap_receiver.get_all_raw_received_traps()
        except Exception as e:
            print(f"Error al obtener traps (Sesión {session_id}): {e}")
            return (False,[])
            
        # *********** Comprobamos si hemos recibido algo ***********
        if not received_traps:
            return (False,[]) # No hemos recibido nada

        # Si la tarea era solo para verificar si hubo algo..
        if oid_to_check is None:
            return (True,received_traps) # Sí, se recibieron traps (devolvemos todos)

        # Si la tarea buscaba un OID específico
        found_matching_traps = []   # Lista donde se guardaran todos los traps que coincidan con el del OID pasado.

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
            return (True, found_matching_traps) # ¡Encontrado! Devolvemos solo los que coinciden
        else:
            return (False, []) # No encontramos el OID específico
        
    def clear_traps_buffer(self, session_id):
        """
        Obtiene todos los traps actuales, los borra del buffer y los devuelve para que puedan ser guardados en la BD.
        
        Returns:
            list: todos_los_traps_que_habia_antes_de_borrar
        """
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info:
            print(f"ERROR: No trap listener info found for session {session_id}.")
            return []
            
        trap_receiver = listener_info['trap_receiver']
        if not trap_receiver:
            print(f"ERROR: trap_receiver no encontrado en app_ref para la session {session_id}.")
            return []

        received_traps = []
        try:
            received_traps = trap_receiver.get_all_raw_received_traps()
        except Exception as e:
            print(f"Error al obtener traps (Sesión {session_id}): {e}")
            # Continuamos para intentar borrar de todas formas

        try:
            trap_receiver.clear_all_received_traps()
            print(f"Buffer de traps (Sesión {session_id}) limpiado. {len(received_traps)} traps totales recuperados.")
        except Exception as e:
            print(f"Error al limpiar traps (Sesión {session_id}): {e}")
                
        return received_traps # Devolvemos los traps que acabamos de borrar

   
    def _start_snmp_listener_thread(self, session_id):
        # Guardamos el diccionario de la info del listener de la session_id que nos pasan como argumento.
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info:
            print(f"Error: No listener info for session {session_id}")
            return
        # Actualiza el estado de los botones
        self.app_ref.gui_queue.put(('enable_buttons', None))
        
        listener_info['listener_thread']= threading.Thread(target=self._execute_start_listener, args=(session_id,), daemon=True)
        listener_info['listener_thread'].start()

    def _execute_start_listener(self, session_id):
        """Starts the SNMP trap listener for a specific session """
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info:
            print(f"Error: No listener info for session {session_id} in thread.")
            return
        
        trap_receiver = listener_info.get('trap_receiver')
        port_widget = listener_info.get('port_widget')
        
        if not trap_receiver or not port_widget:
            print(f"Error: Missing trap_receiver or port_widget for session {session_id}")
            # Asegurarse de que los botones se reactiven si falla aquí
            self.app_ref.gui_queue.put(('enable_buttons', None))
            return
        
        try:
            print("*** Entrando en _execute_start_listener ***")

            # ip = self.app_ref.snmp_ip_entry.get()
            ip = "0.0.0.0"
            port = int(port_widget.get())
            print(f"*** IP y Puerto obtenidos (Sesión {session_id}): {ip}:{port} ***")

            script_dir = os.path.dirname(os.path.abspath(__file__))
            mib_dir = os.path.join(script_dir, "compiled_mibs")
            mib_uri = Path(mib_dir).as_uri()
            
            if not os.path.isdir(mib_dir):
                error_msg = f"Error: Directorio MIBs no encontrado en {mib_dir}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
                self.app_ref.gui_queue.put(('enable_buttons', None))
                print("*** ERROR: Directorio MIB no encontrado ***")
                listener_info['is_running'] = False
                return
            
            print(f"*** (Sesión {session_id}): Llamando a trap_receiver.start_trap_listener... ***") 
            
            trap_receiver.start_trap_listener(listen_ip=ip, listen_port=port, mib_dirs_string=mib_uri)
            
            print("*** (Sesión {session_id}) start_trap_listener HA TERMINADO. Cargando MIBs... ***")  
            try:
                trap_receiver.load_mibs("DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB")
                listener_info['is_running'] = True
                # estado especifico de la sesion
                self.app_ref.gui_queue.put(('snmp_listener_status', session_id, "Listener: Ejecutando", "green"))
                self.app_ref.gui_queue.put(('main_status', f"Listener SNMP (Sesión {session_id}) iniciado en {ip}:{port}", "#2ABE68"))

            except Exception as e_mibs:
                error_msg = f"ADVERTENCIA (Sesión {session_id}): Error cargando MIBs: {repr(e_mibs)}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "orange"))
                listener_info['is_running'] = True  # De esta manera iniciamos el listeener aunque no hayamos podido adquirir las mibs.

        except Exception as e_start:
            listener_info['is_running'] = False
            error_msg = f"Error al iniciar listener (Sesión {session_id}): {repr(e_start)}"
            print(f"!!! GUI ERROR (Start, Sesión {session_id}): {error_msg}")
            self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
            self.app_ref.gui_queue.put(('snmp_listener_status', session_id, 'Listener: Error', 'red'))

        finally:
            self.app_ref.gui_queue.put(('enable_buttons', None))

    def _stop_snmp_listener_thread(self, session_id):
        self.app_ref.gui_queue.put(('enable_buttons', None))
        threading.Thread(target=self._execute_stop_listener, args=(session_id,), daemon=True).start()

    def _execute_stop_listener(self, session_id):
        """Stops the SNMP trap listener for a specific session."""
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info:
            print(f"Error: No listener info for session {session_id} in stop thread.")
            return
        
        trap_receiver = listener_info.get('trap_receiver')
        if not trap_receiver:
            print(f"Error: Missing trap_receiver for session {session_id}")
            self.app_ref.gui_queue.put(('enable_buttons', None))
            return
        
        try:
            trap_receiver.stop_trap_listener()
            self.app_ref.gui_queue.put(('snmp_listener_status', session_id,  'Listener: Detenido', 'red'))
            self.app_ref.gui_queue.put(('main_status', f"Listener SNMP (Sesión {session_id}) detenido.", "orange"))
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error al detener listener: {e}", "red"))
        finally:
            listener_info['is_running'] = False
            self.app_ref.gui_queue.put(('enable_buttons', None))

    def _show_all_traps(self, session_id):
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info:
            self.app_ref._update_status(f"Error: No se encontró listener para la sesión {session_id}", "red")
            return

        trap_receiver = listener_info.get('trap_receiver')
        if not trap_receiver:
            self.app_ref._update_status(f"Error: trap_receiver GUI corrupto para sesión {session_id}", "red")
            return
            
        traps = trap_receiver.get_all_raw_received_traps()
        self.app_ref.update_trap_display(traps, session_id)
        self.app_ref._update_status(f"Traps (Sesión {session_id}) en vivo actualizados.", "white")



    def _filter_traps(self, session_id):
        # listener_info = self.app_ref.trap_listeners.get(session_id)
        # filter_text_widget_object = listener_info.get('filter_entry_widget')
        # trap_receiver = listener_info.get('trap_receiver')
        
        # if not (listener_info and trap_receiver and filter_text_widget_object):
        #     self.app_ref._update_status(f"Error: Componentes de GUI no encontrados para sesión {session_id}", "red")
        #     return
        # COMENTAMOS LO ANTERIOR PORQUE ES PROPENSO A DAR PROBLEMAS DEBIDO A QUE HACEMOS GET DE ALGO QUE PODRÍA SER FALLO (LISTENER_INFO). DE ESA FORMA FILTER TEXT_WIDGET_OBJECT Y TRAP_RECEIVER TAMBIEN FALLARIAN Y NO LLEGARIAMOS AL IF DONDE SE COMPRUEBA DE QUE EXISTAN.. ->
        # -> ES MEJOR SI LO JACEMOS DE LA SIGUIENTE MANERA
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info:
            self.app_ref._update_status(f"Error: No se encontró listener para la sesión {session_id}", "red")
            return
        
        filter_widget = listener_info.get('filter_entry_widget')
        trap_receiver = listener_info.get('trap_receiver')
        
        if not (filter_widget and trap_receiver):
            self.app_ref._update_status(f"Error: filter_widget o trap_receiver GUI corruptos para sesión {session_id}", "red")
            return
        
        filter_text = filter_widget.get()    #CUIDADO! .get hace referencia a adquirir el texto del widget! no el objeto widget como tal
        traps = trap_receiver.get_filtered_traps_by_text(filter_text)
        
        self.app_ref.update_trap_display(traps, session_id)
        self.app_ref._update_status(f"Mostrando traps (Sesión {session_id}) filtrados por '{filter_text}'.", "white")

    def _reset_traps(self, session_id):
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info:
            self.app_ref._update_status(f"Error: No se encontró listener para la sesión {session_id}", "red")
            return
            
        
        trap_receiver = listener_info.get('trap_receiver')
        if not trap_receiver:
            self.app_ref._update_status(f"Error: trap_receiver GUI corrupto para sesión {session_id}", "red")
            return
        
        trap_receiver.clear_all_received_traps()
        self.app_ref.update_trap_display([], session_id)
        self.app_ref._update_status(f"Traps (Sesión {session_id}) en vivo borrados.", "white")
    

    # Para poder captar los traps y compararlos en la Correlacion de Eventos de traps SNMP con eventos del Registro Cronológico, NECESITAMOS REALIZAR UNA FUNCION NUEVA QUE OBTENGA LOS DATOS QUE DESDE LA GUI, 
    # Y NO DIRECTAMENTE DESDE  _show_all_traps (YA QUE PUEDE INTERFERIR CON EL FUNCIONAMIENTO DE LA GUI)
    def get_raw_traps_for_correlation(self, session_id):
        """Obtiene los traps crudos recibidos sin actualizar la GUI para la sesion pasada."""
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info:
            self.app_ref._update_status(f"Error: No se encontró listener para la sesión {session_id}", "red")
            return []
            
        trap_receiver = listener_info.get('trap_receiver')

        if not trap_receiver:
            self.app_ref._update_status(f"Error: trap_receiver GUI corrupto para sesión {session_id}", "red")
            return []
    
        return trap_receiver.get_all_raw_received_traps()
        

    # Para los informes de rendimiento HIL & SNMP
    def get_traps_since_index(self, session_id, start_index):
        """
        Devuelve solo los traps recibidos a partir de un índice concreto.
        Ideal para ráfagas: no borra nada, pero aísla los nuevos.
        """
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info: return []
            
        trap_receiver = listener_info.get('trap_receiver')
        if not trap_receiver: return []

        # Obtenemos todos los traps (sin borrar)
        all_last_traps = trap_receiver.get_all_raw_received_traps()
        
        # Devolvemos solo los traps desde el índice start_index hasta el final
        # Si start_index es mayor que la longitud, devuelve lista vacía (correcto)
        return all_last_traps[start_index:]

    def get_current_trap_count(self, session_id):
        """Devuelve cuántos traps hay en total ahora mismo."""
        listener_info = self.app_ref.trap_listeners.get(session_id)
        if not listener_info: return 0
        trap_receiver = listener_info.get('trap_receiver')
        if not trap_receiver: return 0
        all_traps = trap_receiver.get_all_raw_received_traps()
        return len(all_traps)