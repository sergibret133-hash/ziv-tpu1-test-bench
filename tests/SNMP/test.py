# trap_listener_library.py

import asyncio
import threading
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp # udp6 si también lo necesitas
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from pysnmp.smi import builder, view, compiler, rfc1902
from datetime import datetime, timezone
import time

class TrapListenerLibrary:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, mib_dirs=None, listen_ip="0.0.0.0", listen_port=162):
        """
        Inicializa el listener de traps.
        :param mib_dirs: Lista de directorios donde buscar MIBs compiladas,
                         ej: ["file:///C:/Users/sergio.bret/Documents/SNMP/compiled_mibs"]
                         o una cadena con una sola ruta.
        :param listen_ip: IP en la que escuchar. "0.0.0.0" para todas las interfaces.
        :param listen_port: Puerto en el que escuchar.
        """
        self._listen_ip = listen_ip
        self._listen_port = int(listen_port)
        self._received_traps = []
        self._lock = threading.Lock()  # Para proteger el acceso a _received_traps
        self._dispatcher_thread = None
        self._stop_event = threading.Event() # Para señalar al hilo del dispatcher que se detenga
        self._loop = None # Event loop para asyncio

        # Configuración de MIBs
        self.mib_builder = builder.MibBuilder()
        self.mib_view_controller = view.MibViewController(self.mib_builder)
        
        if mib_dirs:
            if isinstance(mib_dirs, str):
                mib_dirs = [mib_dirs]
            compiler.add_mib_compiler(self.mib_builder, sources=mib_dirs)
        
        # Pre-cargar MIBs (puedes hacer esto configurable o añadir un keyword)
        try:
            self.mib_builder.load_modules("DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB")
            print("MIBs DIMAT-BASE-MIB y DIMAT-TPU1C-MIB cargadas.")
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar las MIBs DIMAT: {e}")
            print("Asegúrate de que las MIBs compiladas estén en las rutas especificadas y sean accesibles.")


    def _process_varbinds(self, var_binds_list):
        processed_varbinds = []
        resolved_var_binds = [
            rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolve_with_mib(self.mib_view_controller)
            for x in var_binds_list
        ]

        for oid, val in resolved_var_binds:
            oid_str = oid.prettyPrint()
            val_str = val.prettyPrint()
            translated_value = val_str # Por defecto

            if "tpu1cNotifyTimeSecsUtc" in oid_str:
                try:
                    # Asumiendo que val es un entero representando timestamp Unix
                    dt_object = datetime.fromtimestamp(int(str(val)), tz=timezone.utc)
                    translated_value = dt_object.isoformat()
                except ValueError:
                    print(f"Advertencia: No se pudo convertir el timestamp para {oid_str}: {val_str}")
                    translated_value = f"Error de formato: {val_str}"
                
            elif "1.3.6.1.4.1.6346.1.8" in oid_str: # Verifica el OID, no el valor
                # El valor de este OID es en sí mismo otro OID que indica el tipo de notificación
                try:
                    # val es un ObjectIdentity, ej: ObjectIdentity('1.3.6.1.4.1.6346.1.8.1.1.1')
                    notification_type_location = self.mib_view_controller.get_node_name(val.getOid())
                    # get_node_name devuelve una tupla, ej: ('dimatTpu1cNotifications', 'trapA')
                    # Queremos el nombre del nodo, ej: 'trapA'
                    translated_value = f"Notification Type: {notification_type_location[-1]}"
                except Exception as e:
                    print(f"Advertencia: No se pudo resolver el tipo de notificación para {oid_str} con valor {val_str}: {e}")
                    translated_value = f"Error de resolución MIB: {val_str}"

            processed_varbinds.append({
                "oid": oid_str,
                "raw_value": val_str,
                "value": translated_value
            })
        return processed_varbinds

    def _trap_callback(self, transport_dispatcher, transport_domain, transport_address, whole_msg):
        # Este callback se ejecuta en el hilo del event loop de asyncio
        print(f"Trap recibido de {transport_address[0]}:{transport_address[1]} en hilo {threading.get_ident()}")
        
        while whole_msg:
            msg_ver = int(api.decodeMessageVersion(whole_msg))
            if msg_ver not in api.PROTOCOL_MODULES:
                print(f"Unsupported SNMP version {msg_ver}")
                return

            p_mod = api.PROTOCOL_MODULES[msg_ver]
            req_msg, whole_msg = decoder.decode(whole_msg, asn1Spec=p_mod.Message())
            
            trap_data = {
                "received_at": datetime.now(timezone.utc).isoformat(),
                "source_ip": transport_address[0],
                "source_port": transport_address[1],
                "version": msg_ver,
                "varbinds": []
            }

            req_pdu = p_mod.apiMessage.get_pdu(req_msg)
            if req_pdu.isSameTypeWith(p_mod.TrapPDU()):
                if msg_ver == api.SNMP_VERSION_1:
                    trap_data["enterprise"] = p_mod.apiTrapPDU.get_enterprise(req_pdu).prettyPrint()
                    trap_data["agent_address"] = p_mod.apiTrapPDU.get_agent_address(req_pdu).prettyPrint()
                    trap_data["generic_trap"] = p_mod.apiTrapPDU.get_generic_trap(req_pdu).prettyPrint()
                    trap_data["specific_trap"] = p_mod.apiTrapPDU.get_specific_trap(req_pdu).prettyPrint()
                    trap_data["uptime"] = p_mod.apiTrapPDU.get_timestamp(req_pdu).prettyPrint()
                    var_binds_list = p_mod.apiTrapPDU.get_varbinds(req_pdu)
                else: # SNMP_VERSION_2c o SNMP_VERSION_3
                    var_binds_list = p_mod.apiPDU.get_varbinds(req_pdu)
                
                trap_data["varbinds"] = self._process_varbinds(var_binds_list)

                with self._lock:
                    self._received_traps.append(trap_data)
                print(f"Trap procesado y almacenado: {trap_data}")

            else:
                print(f"Mensaje no es un Trap PDU: {req_pdu.prettyPrint()}")
        return whole_msg # Importante para que pysnmp pueda procesar mensajes concatenados si los hubiera


    def _run_dispatcher_loop(self):
        # Esta función se ejecuta en un hilo separado
        print(f"Iniciando dispatcher de asyncio en hilo {threading.get_ident()}...")
        # self._loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(self._loop)
        
        self.transport_dispatcher = AsyncioDispatcher()
        self.transport_dispatcher.register_recv_callback(self._trap_callback)

        # UDP/IPv4
        try:
            self.transport_dispatcher.register_transport(
                udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_server_mode("10.212.42.4", 162)
            )
            # udp6 si lo necesitas:
            # self.transport_dispatcher.register_transport(
            # udp6.DOMAIN_NAME, udp6.Udp6AsyncioTransport(loop=self._loop).open_server_mode(('::1', self._listen_port))
            # )
            print(f"Escuchando traps en {self._listen_ip}:{self._listen_port}")
        except Exception as e:
            print(f"ERROR AL REGISTRAR TRANSPORTE: {e}. ¿El script se ejecuta con suficientes privilegios para el puerto {self._listen_port}?")
            self._stop_event.set() # Indica que no se pudo iniciar
            return


        self.transport_dispatcher.job_started(1) # Indica que hay un trabajo activo

        self.transport_dispatcher.run_dispatcher() 
        # try:
        #     # Bucle principal del dispatcher
        #     while not self._stop_event.is_set():
        #         # El timeout es importante para que runDispatcher() no bloquee indefinidamente
        #         # y podamos verificar self._stop_event periódicamente.
        #         self.transport_dispatcher.run_dispatcher(timeout=0.1) 
        # except Exception as e:
        #     print(f"Error en el dispatcher loop: {e}")
        # finally:
        #     print("Cerrando dispatcher de asyncio...")
        #     self.transport_dispatcher.job_finished(1) # Indica que el trabajo ha terminado
        #     self.transport_dispatcher.close_dispatcher()
        #     self._loop.call_soon_threadsafe(self._loop.stop) # Detiene el event loop de forma segura
        #     # No cerramos el loop aquí, run_forever o run_until_complete lo hará
        #     print("Dispatcher de asyncio cerrado.")


    # --- Keywords para Robot Framework ---

    def start_trap_listener(self):
        """
        Inicia el listener de traps SNMP en un hilo separado.
        Este programa puede necesitar ejecutarse como root/administrador para monitorizar el puerto 162.
        """
        print("Listener activado.")

        if self._dispatcher_thread and self._dispatcher_thread.is_alive():
            print("El listener de traps ya está activo.")
            return
        


        self._stop_event.clear()
        with self._lock:
            self._received_traps = [] # Limpiar traps de sesiones anteriores


        self.transport_dispatcher = AsyncioDispatcher()
        self.transport_dispatcher.register_recv_callback(self._trap_callback)

        # UDP/IPv4
        try:
            self.transport_dispatcher.register_transport(
                udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_server_mode("10.212.42.4", 162)
            )
            # udp6 si lo necesitas:
            # self.transport_dispatcher.register_transport(
            # udp6.DOMAIN_NAME, udp6.Udp6AsyncioTransport(loop=self._loop).open_server_mode(('::1', self._listen_port))
            # )
            print(f"Escuchando traps en {self._listen_ip}:{self._listen_port}")
        except Exception as e:
            print(f"ERROR AL REGISTRAR TRANSPORTE: {e}. ¿El script se ejecuta con suficientes privilegios para el puerto {self._listen_port}?")
            self._stop_event.set() # Indica que no se pudo iniciar
            return


        self.transport_dispatcher.job_started(1) # Indica que hay un trabajo activo

        
        
        self._dispatcher_thread = threading.Thread(target=self.transport_dispatcher.run_dispatcher , daemon=True)
        self._dispatcher_thread.start()
        
        # Pequeña espera para asegurar que el hilo y el dispatcher inicien
        time.sleep(1) 
        if self._stop_event.is_set(): # Si _run_dispatcher_loop falló al iniciar (e.g. error de puerto)
             raise RuntimeError("El listener de traps no pudo iniciarse. Revisa los logs para más detalles..")
        print("Listener de traps SNMP iniciado.")

    def stop_trap_listener(self):
        """
        Detiene el listener de traps SNMP.
        """
        if self._dispatcher_thread and self._dispatcher_thread.is_alive():
            print("Deteniendo listener de traps SNMP...")
            self._stop_event.set()
            self._dispatcher_thread.join(timeout=5) # Espera a que el hilo termine
            if self._dispatcher_thread.is_alive():
                print("Advertencia: El hilo del listener no terminó limpiamente.")
            self._dispatcher_thread = None
            print("Listener de traps SNMP detenido.")
        else:
            print("El listener de traps no estaba activo.")

    def get_received_traps(self):
        """
        Devuelve una copia de la lista de todos los traps recibidos y procesados
        desde que se inició el listener o desde la última limpieza.
        Cada trap es un diccionario con su información.
        """
        with self._lock:
            return list(self._received_traps) # Devuelve una copia

    def clear_received_traps(self):
        """
        Limpia la lista de traps recibidos almacenados.
        """
        with self._lock:
            self._received_traps = []
        print("Lista de traps recibidos limpiada.")

    def wait_for_trap(self, timeout_seconds=30, expected_oid=None, expected_value_in_varbind=None):
        """
        Espera hasta que se reciba un trap que cumpla con los criterios o se alcance el timeout.

        :param timeout_seconds: Tiempo máximo de espera en segundos.
        :param expected_oid: (Opcional) Un OID que debe estar presente en los varbinds del trap.
        :param expected_value_in_varbind: (Opcional) Un texto que debe estar contenido
                                          en el valor (procesado/traducido) de algún varbind del trap.
        :return: El primer trap que coincida con los criterios, o None si se alcanza el timeout.
        """
        end_time = time.time() + float(timeout_seconds)
        print(f"Esperando trap por {timeout_seconds}s (OID: {expected_oid}, Valor: {expected_value_in_varbind})...")
        
        while time.time() < end_time:
            with self._lock:
                # Iterar sobre una copia para evitar problemas si la lista se modifica
                traps_to_check = list(self._received_traps) 
            
            for trap in traps_to_check:
                match_oid = not expected_oid # Si no se espera OID, es un match por defecto
                match_value = not expected_value_in_varbind # Si no se espera valor, es un match por defecto

                if expected_oid: #En caso de que se haya especificado un OID
                    for vb in trap.get("varbinds", []):
                        if vb.get("oid") == expected_oid:
                            match_oid = True
                            break
                
                if expected_value_in_varbind: #En caso de que se haya especificado un varbind
                    for vb in trap.get("varbinds", []):
                        # Busca en el campo 'value' que contiene el valor ya procesado/traducido
                        if expected_value_in_varbind in str(vb.get("value", "")):
                            match_value = True
                            break
                
                if match_oid and match_value:
                    print(f"Trap encontrado que cumple criterios: {trap}")
                    return trap
            
            time.sleep(0.5) # Pausa para no consumir CPU excesivamente

        print(f"Timeout: No se recibió el trap esperado después de {timeout_seconds}s.")
        return None

# --- Sección para probar la librería directamente (opcional) ---
if __name__ == '__main__':
    print("Probando TrapListenerLibrary localmente...")
    # Asegúrate de que la ruta a tus MIBs es correcta si las necesitas para la prueba.
    # Ejemplo: mib_path = "file:///C:/Users/tu_usuario/ruta/a/mibs_compiladas"
    mib_path = "file:///C:/Users/sergio.bret/Documents/SNMP/compiled_mibs" # Ajusta esta ruta
    
    # Crea una instancia de la librería, especificando la ruta a las MIBs
    # listener = TrapListenerLibrary(mib_dirs=[mib_path], listen_ip="10.212.42.4", listen_port=162)

    try:
        
        transport_dispatcher = AsyncioDispatcher()
        transport_dispatcher.register_recv_callback(TrapListenerLibrary._trap_callback)

        # UDP/IPv4
        try:
            transport_dispatcher.register_transport(
                udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_server_mode("10.212.42.4", 162)
            )
            # udp6 si lo necesitas:
            # self.transport_dispatcher.register_transport(
            # udp6.DOMAIN_NAME, udp6.Udp6AsyncioTransport(loop=self._loop).open_server_mode(('::1', self._listen_port))
            # )
            
        except Exception as e:
            print(f"ERROR AL REGISTRAR TRANSPORTE: {e}. ¿El script se ejecuta con suficientes privilegios para el puerto 162?")
            raise RuntimeError("No se pudo iniciar el listener de traps. Revisa los logs para más detalles.")


        transport_dispatcher.job_started(1) # Indica que hay un trabajo activo

        
        
        dispatcher_thread = threading.Thread(target=transport_dispatcher.run_dispatcher , daemon=True)
        dispatcher_thread.start()
        # print("Listener iniciado. Envía un trap a 127.0.0.1:162 para probar.")
        # print("Por ejemplo, desde otra terminal:")
        # print("| snmptrap -v2c -c public 127.0.0.1 '' 1.3.6.1.4.1.6346.1.8.1.1.1 tpu1cNotificationDataText.0 s \"Test de Alarma\"")
        # print("| snmptrap -v2c -c public 127.0.0.1 '' 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.5.0 s \"Test Genérico\"")

        while True:
            time.sleep(1) # Mantén el script principal vivo para que el listener siga corriendo
        # Esperar un trap en alguno de sus varbinds traducidos
        print("\nEsperando un trap  (timeout 20s)...")
        trap = listener.wait_for_trap(timeout_seconds=20)
        if trap:
            print(f"Trap recibido por wait_for_trap: {trap}")
        else:
            print("No se recibió el trap en el tiempo esperado.")

        # Esperar un trap que contenga un OID específico
        # print("\nEsperando un trap con OID '1.3.6.1.2.1.1.5.0' (timeout 20s)...")
        # trap_oid_especifico = listener.wait_for_trap(timeout_seconds=20, expected_oid="1.3.6.1.2.1.1.5.0")
        # if trap_oid_especifico:
        #     print(f"Trap con OID específico recibido: {trap_oid_especifico}")
        # else:
        #     print("No se recibió el trap con OID específico en el tiempo esperado.")

        print("\nPresiona Ctrl+C para detener la prueba...")
        while True: # Mantén el script principal vivo para que el listener siga corriendo
            time.sleep(1)
            # Podrías imprimir los traps recibidos periódicamente
            current_traps = listener.get_received_traps()
            if current_traps:
                print(f"Traps actuales: {current_traps}")
                listener.clear_received_traps()

    except KeyboardInterrupt:
        print("\nInterrupción por teclado recibida.")
    except RuntimeError as e:
        print(f"Error en la ejecución de la prueba: {e}")
    finally:
        print("Deteniendo listener para finalizar prueba...")
        print("Prueba finalizada.")