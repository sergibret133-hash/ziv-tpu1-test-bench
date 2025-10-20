# snmp_trap_listener.py
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp #, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from pysnmp.smi import builder, view, compiler, rfc1902
from datetime import datetime, timezone

import threading
import time
import logging
import collections
import re # Para la condición regex y para sanitizar nombres de claves

# Configuración de logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Usar un logger específico para la librería

class trapReceiver_Robot_3:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    def __init__(self):
        self._transport_dispatcher = None
        self._mib_builder = None
        self._mib_view_controller = None
        self._received_traps = collections.deque() # Cola general de todos los traps recibidos
        self._classified_traps = {}   # Diccionario para almacenar traps por tipo de evento
                                      # Ejemplo: {'IF-MIB::linkDown': deque([...]), 'MY-CUSTOM-MIB::myEvent': deque([...])}
        self._trap_filters = []
        self._listener_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock() # Protege _received_traps, _classified_traps, _trap_filters
        
        # OID estándar que identifica el tipo de notificación en SNMPv2c y posterior
        # Su valor es otro OID que, resuelto, da el nombre de la notificación.
        # SNMPv2-MIB::snmpTrapOID.0 is 1.3.6.1.6.3.1.1.4.1.0
        self._classification_oid_key_numeric = "1.3.6.1.6.3.1.1.4.1.0" 
        self._classification_oid_key_named = "SNMPv2-MIB::snmpTrapOID.0" # Default symbolic name

    def _initialize_mib_controller(self, mib_dirs_string):
        logger.debug("Inicializando controladores MIB...")
        self._mib_builder = builder.MibBuilder()
        self._mib_view_controller = view.MibViewController(self._mib_builder)
        
        if mib_dirs_string:
            mib_dirs = [d.strip() for d in mib_dirs_string.split(',')]
            try:
                compiler.add_mib_compiler(self._mib_builder, sources=mib_dirs)
                logger.info(f"Compilador MIB configurado para buscar MIBs de texto en: {mib_dirs}")
            except Exception as e:
                logger.error(f"Error configurando fuentes del compilador MIB con directorios {mib_dirs}: {e}. Asegúrate que son directorios de MIBs de texto.")
        else:
            logger.info("No se proporcionaron directorios MIB, usando configuración por defecto del compilador MIB.")

    def load_mibs(self, *mib_modules):
        """
        Carga los módulos MIB especificados. Las MIBs deben estar pre-compiladas (.py)
        y accesibles por el MIB builder (e.g., en directorios configurados o PYTHONPATH).
        | Load Mibs | SNMPv2-MIB | IF-MIB | MY-CUSTOM-MIB |
        """
        if not self._mib_builder:
            raise RuntimeError("El controlador MIB no ha sido inicializado. Llama a 'Start Trap Listener' primero.")
        if not mib_modules:
            logger.warning("No se especificaron módulos MIB para cargar.")
            return
        try:
            self._mib_builder.load_modules(*mib_modules)
            logger.info(f"MIBs cargadas: {', '.join(mib_modules)}")
        except Exception as e:
            logger.error(f"Error al cargar MIBs {mib_modules}: {e}")
            raise

    def _sanitize_event_key(self, key_string):
        """
        Limpia una cadena para que sea una clave de diccionario/nombre de lista seguro.
        Reemplaza caracteres no alfanuméricos (excepto '::', '-', '_', '.') por '_'.
        """
        if not isinstance(key_string, str):
            key_string = str(key_string)
        return re.sub(r'[^\w:\-\.]', '_', key_string)

    def _callback(self, transportDispatcher, transportDomain, transportAddress, wholeMsg):
        try:
            while wholeMsg:
                msgVer = int(api.decodeMessageVersion(wholeMsg))
                if msgVer in api.PROTOCOL_MODULES:
                    pMod = api.PROTOCOL_MODULES[msgVer]
                else:
                    logging.warning(f"Unsupported SNMP version {msgVer} from {transportAddress}")
                    return

                reqMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
                
                community_name = "N/A"
                if hasattr(pMod, 'apiMessage') and hasattr(pMod.apiMessage, 'get_community'):
                    try:
                        community_name = pMod.apiMessage.get_community(reqMsg).prettyPrint()
                    except Exception:
                        community_name = "ErrorDecodingCommunity"
                
                reqPDU = pMod.apiMessage.get_pdu(reqMsg)
                varBinds = pMod.apiPDU.get_varbinds(reqPDU)

                processed_var_binds = []
                for oid, val in varBinds:
                    try:
                        resolved_oid = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid), val).resolve_with_mib(self._mib_view_controller)
                        oid_name_str = str(resolved_oid[0].prettyPrint())
                        value_str = str(resolved_oid[1].prettyPrint())
                        processed_var_binds.append({
                            'oid': oid_name_str,
                            'value': value_str,
                            'raw_oid': str(oid),
                            'raw_value': str(val),
                            'value_type': type(resolved_oid[1]).__name__
                        })
                    except Exception as e:
                        logging.warning(f"Error resolviendo varbind {oid}={val}: {e}. Manteniendo valores raw.")
                        processed_var_binds.append({
                            'oid': str(oid),
                            'value': str(val),
                            'raw_oid': str(oid),
                            'raw_value': str(val),
                            'value_type': type(val).__name__
                        })
                
                varbinds_dict_content = {
                    item['oid']: item['value'] for item in processed_var_binds 
                    if 'oid' in item and 'value' in item and isinstance(item['oid'], str)
                }
                
                pdu_type_name = reqPDU.__class__.__name__
                classification_key = "UNKNOWN_TRAP_TYPE" 

                # SNMPv1 Trap specific processing
                if msgVer == api.SNMP_VERSION_1 and reqPDU.getTagSet() == pMod.TrapPDU.tagSet:
                    enterprise = pMod.apiTrapPDU.get_enterprise(reqPDU).prettyPrint()
                    generic_trap = int(pMod.apiTrapPDU.get_generic_trap(reqPDU))
                    specific_trap = int(pMod.apiTrapPDU.get_specific_trap(reqPDU))
                    # agent_addr = pMod.apiTrapPDU.get_agent_addr(reqPDU).prettyPrint() # Available if needed
                    # snmp_uptime_v1 = pMod.apiTrapPDU.get_timestamp(reqPDU).prettyPrint() # Available if needed

                    if generic_trap == 0: classification_key = f"{enterprise}::coldStart"
                    elif generic_trap == 1: classification_key = f"{enterprise}::warmStart"
                    elif generic_trap == 2: classification_key = f"{enterprise}::linkDown"
                    elif generic_trap == 3: classification_key = f"{enterprise}::linkUp"
                    elif generic_trap == 4: classification_key = f"{enterprise}::authenticationFailure"
                    elif generic_trap == 5: classification_key = f"{enterprise}::egpNeighborLoss"
                    elif generic_trap == 6: classification_key = f"{enterprise}::enterpriseSpecific.{specific_trap}"
                    else: classification_key = f"{enterprise}::genericTrap.{generic_trap}"
                
                # SNMPv2c / SNMPv3 Trap/Inform specific processing
                elif msgVer >= api.SNMP_VERSION_2C and \
                     (reqPDU.getTagSet() == pMod.SNMPv2TrapPDU.tagSet or reqPDU.getTagSet() == pMod.InformRequestPDU.tagSet):
                    trap_oid_found = False
                    for vb in processed_var_binds: # Use the already processed varbinds list
                        if vb['raw_oid'] == self._classification_oid_key_numeric or \
                           vb['oid'] == self._classification_oid_key_named:
                            classification_key = vb['value'] 
                            trap_oid_found = True
                            break
                    if not trap_oid_found:
                        logging.warning(f"SNMPv{msgVer+1} PDU ({pdu_type_name}) de {transportAddress} no contiene {self._classification_oid_key_named} ({self._classification_oid_key_numeric}).")
                        classification_key = f"SNMPv{msgVer+1}_{pdu_type_name}_NO_TRAP_OID"
                else:
                    classification_key = f"NON_TRAP_PDU_{pdu_type_name}"

                safe_event_key = self._sanitize_event_key(classification_key)
                
                # --- Construcción de datos mínimos para almacenar ---
                trap_details_to_store = {
                    'timestamp_received_utc': datetime.now(timezone.utc).isoformat(),
                    'source_address': str(transportAddress[0]), # IP Origen
                    'event_type': safe_event_key,
                    'original_event_type': classification_key,
                    'varbinds_dict': varbinds_dict_content
                }

                # --- Visualización en terminal de varbinds_dict ---
                logger.info(f"--- Trap Recibido de: {transportAddress[0]}:{transportAddress[1]} (Comunidad: '{community_name}') ---")
                logger.info(f"    Tipo Original: '{classification_key}' -> Clasificado como: '{safe_event_key}'")
                logger.info(f"    Varbinds (OID: Valor):")
                if varbinds_dict_content:
                    for oid_key, value in varbinds_dict_content.items():
                        logger.info(f"        {oid_key}: {value}")
                else:
                    logger.info("        (No hay varbinds en el diccionario)")
                logger.info("------------------------------------------------------------------------------------")


                with self._lock:
                    self._received_traps.append(trap_details_to_store) 
                    if safe_event_key not in self._classified_traps:
                        self._classified_traps[safe_event_key] = collections.deque()
                    self._classified_traps[safe_event_key].append(trap_details_to_store)
                
                logging.debug(f"Trap procesado y almacenado (mínimo). Total en general: {len(self._received_traps)}, Total para '{safe_event_key}': {len(self._classified_traps[safe_event_key])}")

        except Exception as e:
            logging.error(f"Error fatal procesando mensaje/trap de {transportAddress}: {e}", exc_info=True)
        
        return wholeMsg

    def start_trap_listener(self, listen_ip="0.0.0.0", listen_port=162, mib_dirs_string=""):
        if self._listener_thread and self._listener_thread.is_alive():
            logger.info("El listener ya está en ejecución.")
            return

        self._stop_event.clear()
        with self._lock:
            self._received_traps.clear()
            self._classified_traps.clear() 
            self._trap_filters.clear()

        self._initialize_mib_controller(mib_dirs_string)
        try:
            logger.info("Cargando MIBs esenciales: SNMPv2-MIB, SNMPv2-SMI, SNMP-FRAMEWORK-MIB, SNMP-TARGET-MIB, SNMP-NOTIFICATION-MIB")
            self._mib_builder.load_modules(
                'SNMPv2-MIB', 'SNMPv2-SMI', 'SNMP-FRAMEWORK-MIB', 
                'SNMP-TARGET-MIB', 'SNMP-NOTIFICATION-MIB'
            )
        except Exception as e:
            logger.warning(f"Error cargando MIBs esenciales. La resolución de OID podría ser limitada: {e}")

        self._transport_dispatcher = AsyncioDispatcher()
        self._transport_dispatcher.register_recv_callback(self._callback)

        try:
            self._transport_dispatcher.register_transport(
                udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_server_mode((listen_ip, int(listen_port)))
            )
            logger.info(f"Listener de traps SNMP (IPv4) iniciado en {listen_ip}:{int(listen_port)}")
        except Exception as e:
            logger.error(f"Error al registrar transporte UDP/IPv4 en {listen_ip}:{int(listen_port)}: {e}")
            if self._transport_dispatcher: self._transport_dispatcher.close_dispatcher()
            self._transport_dispatcher = None
            raise RuntimeError(f"Fallo al iniciar listener IPv4: {e}")
    
        self._listener_thread = threading.Thread(target=self._run_dispatcher_loop, daemon=True)
        self._listener_thread.start()
        
        time.sleep(0.1) 
        if not self._listener_thread.is_alive():
            if self._transport_dispatcher:
                self._transport_dispatcher.close_dispatcher()
                self._transport_dispatcher = None
            raise RuntimeError("El hilo del listener no pudo iniciarse.")
        logger.info("Hilo del dispatcher del listener iniciado.")

    def _run_dispatcher_loop(self):
        if not self._transport_dispatcher:
            logger.error("Transport dispatcher no inicializado en _run_dispatcher_loop.")
            return
            
        self._transport_dispatcher.job_started(1)
        try:
            logger.debug("Iniciando self._transport_dispatcher.run_dispatcher()...")
            self._transport_dispatcher.run_dispatcher() 
        except Exception as e:
            if not self._stop_event.is_set():
                logger.error(f"Excepción en el bucle del dispatcher (run_dispatcher): {e}", exc_info=True)
        finally:
            self._transport_dispatcher.job_finished(1) 
            logger.info("Bucle del dispatcher (run_dispatcher) finalizado.")

    def stop_trap_listener(self):
        if not self._listener_thread or not self._listener_thread.is_alive():
            if not self._stop_event.is_set(): 
                logger.info("El listener no está en ejecución o ya fue detenido.")
            self._stop_event.set() 
            return

        logger.info("Deteniendo el listener de traps...")
        self._stop_event.set() 
        
        if self._transport_dispatcher:
            try:
                # Unregister all transports for the domain before closing dispatcher
                # This might not be strictly necessary if close_dispatcher handles it, but can be safer.
                # self._transport_dispatcher.unregister_transport(udp.DOMAIN_NAME) # This might error if not registered
                # Instead, just close.
                pass
            except Exception as e:
                logger.warning(f"Error durante unregister_transport (ignorado): {e}")
            
            self._transport_dispatcher.close_dispatcher()
        
        if self._listener_thread.is_alive():
            logger.debug("Esperando que el hilo del listener termine (join)...")
            self._listener_thread.join(timeout=5.0)

        if self._listener_thread.is_alive():
            logger.warning("El hilo del listener no terminó correctamente después del timeout.")
        else:
            logger.info("Listener de traps detenido y hilo terminado.")
        
        self._listener_thread = None
        self._transport_dispatcher = None 
        logger.info("Recursos del listener liberados.")

    def add_trap_filter(self, oid, value=None, condition='equals'):
        with self._lock:
            self._trap_filters.append({'oid': oid, 'value': value, 'condition': condition.lower()})
        logger.info(f"Filtro añadido: OID='{oid}', Value='{value}', Condition='{condition}'")

    def clear_trap_filters(self):
        with self._lock:
            self._trap_filters.clear()
        logger.info("Todos los filtros de traps han sido eliminados.")

    def clear_all_received_traps(self):
        with self._lock:
            self._received_traps.clear()
            self._classified_traps.clear()
        logger.info("Todas las colas de traps (general y clasificadas) limpiadas.")

    def _check_condition(self, actual_value, expected_value, condition):
        if actual_value is None and expected_value is not None: 
             return False
        if expected_value is None: 
            return True 
            
        actual_value_str = str(actual_value)
        expected_value_str = str(expected_value)

        if condition == 'equals': return actual_value_str == expected_value_str
        elif condition == 'contains': return expected_value_str in actual_value_str
        elif condition == 'startswith': return actual_value_str.startswith(expected_value_str)
        elif condition == 'endswith': return actual_value_str.endswith(expected_value_str)
        elif condition == 'regex':
            try:
                return bool(re.search(expected_value_str, actual_value_str))
            except re.error as e:
                logger.warning(f"Expresión Regex inválida '{expected_value_str}': {e}")
                return False
        else:
            logger.warning(f"Condición de filtro desconocida: {condition}")
            return False

    def _trap_matches_filters(self, trap_data):
        if not self._trap_filters: 
            return True

        for f_filter in self._trap_filters:
            oid_to_find = f_filter['oid']
            expected_value = f_filter['value']
            condition = f_filter['condition']
            
            actual_value = trap_data['varbinds_dict'].get(oid_to_find)

            if actual_value is None: 
                return False 
            if not self._check_condition(actual_value, expected_value, condition):
                return False 
        
        return True

    def wait_for_trap(self, timeout=30, consume_trap=True):
        end_time = time.monotonic() + float(timeout)
        logger.info(f"Esperando trap (en cola general) con filtros (timeout={timeout}s): {self._trap_filters if self._trap_filters else 'Ninguno'}")
        
        while time.monotonic() < end_time:
            if self._stop_event.is_set():
                logger.info("Espera de trap interrumpida por evento de parada.")
                break

            trap_to_return = None
            with self._lock:
                found_trap_index = -1
                for i, trap_data_item in enumerate(self._received_traps):
                    if self._trap_matches_filters(trap_data_item):
                        trap_to_return = trap_data_item 
                        found_trap_index = i
                        break 

                if trap_to_return:
                    # Note: 'source_address' is now used instead of 'source_ip'
                    logger.info(f"Trap coincidente encontrado (cola general): Origen={trap_to_return.get('source_address', 'N/A')}, TipoEvento='{trap_to_return.get('event_type', 'N/A')}'")
                    if consume_trap:
                        if found_trap_index == 0:
                             self._received_traps.popleft()
                        else:
                            temp_list = list(self._received_traps)
                            del temp_list[found_trap_index]
                            self._received_traps = collections.deque(temp_list)

                        event_type_key = trap_to_return.get('event_type') 
                        if event_type_key and event_type_key in self._classified_traps:
                            try:
                                self._classified_traps[event_type_key].remove(trap_to_return) 
                                if not self._classified_traps[event_type_key]: 
                                    del self._classified_traps[event_type_key]
                                logger.debug(f"Trap consumido de la cola clasificada '{event_type_key}'.")
                            except ValueError:
                                logger.warning(f"Trap no encontrado en cola clasificada '{event_type_key}' al consumir.")
                        logger.debug(f"Trap consumido de la cola general. Restantes: {len(self._received_traps)}")
                    return trap_to_return 
            
            time.sleep(0.1)

        logger.info(f"Timeout esperando trap (cola general). No se encontró trap coincidente con filtros.")
        return None

    def set_classification_oid(self, oid_string='SNMPv2-MIB::snmpTrapOID.0'):
        logger.warning("set_classification_oid es principalmente para depuración interna. La clasificación estándar de v2c usa snmpTrapOID.0.")
        if not oid_string:
            logger.error("El OID de clasificación no puede ser vacío. Manteniendo el actual.")
            raise ValueError("El OID de clasificación no puede ser vacío.")
        
        if "::" in oid_string : 
            self._classification_oid_key_named = oid_string
        else: 
            self._classification_oid_key_numeric = oid_string
            if self._mib_view_controller:
                try:
                    identity_node = rfc1902.ObjectIdentity(oid_string).resolve_with_mib(self._mib_view_controller)
                    self._classification_oid_key_named = identity_node.get_label() 
                    logger.info(f"OID numérico {oid_string} resuelto a {self._classification_oid_key_named} para clasificación.")
                except Exception as e:
                    logger.warning(f"No se pudo resolver el OID numérico {oid_string} a un nombre: {e}. Se usará el numérico.")
                    self._classification_oid_key_named = oid_string 
            else:
                 self._classification_oid_key_named = oid_string 

        logger.info(f"OID de clasificación (nombre preferido) establecido a: {self._classification_oid_key_named}")
        logger.info(f"OID de clasificación (numérico) establecido a: {self._classification_oid_key_numeric}")

    def get_event_types(self):
        with self._lock:
            return list(self._classified_traps.keys())

    def get_traps_by_event_type(self, event_type, consume_traps=True, limit=0):
        logger.debug(f"Solicitando traps para tipo de evento: '{event_type}', consumir: {consume_traps}, límite: {limit}")
        traps_to_return = []
        with self._lock:
            if event_type not in self._classified_traps:
                logger.info(f"No se encontraron traps para el tipo de evento: '{event_type}'.")
                return []

            event_deque = self._classified_traps[event_type]
            num_to_fetch = len(event_deque)
            if limit > 0 and limit < num_to_fetch:
                num_to_fetch = limit

            if consume_traps:
                for _ in range(num_to_fetch):
                    if not event_deque: break 
                    trap = event_deque.popleft() 
                    traps_to_return.append(trap)
                    try:
                        self._received_traps.remove(trap) 
                    except ValueError:
                        logger.warning(f"Trap no encontrado en _received_traps al consumir de lista clasificada '{event_type}'.")
                if not event_deque: 
                    del self._classified_traps[event_type]
                    logger.info(f"Tipo de evento '{event_type}' ahora vacío y eliminado de listas clasificadas.")
            else: 
                for i in range(num_to_fetch):
                    traps_to_return.append(event_deque[i]) 
            
            count = len(traps_to_return)
        logger.info(f"Devueltos {count} traps para tipo de evento '{event_type}'. Consumidos: {consume_traps}")
        return traps_to_return

    def clear_traps_by_event_type(self, event_type):
        logger.info(f"Limpiando traps para tipo de evento: '{event_type}'")
        with self._lock:
            if event_type in self._classified_traps:
                traps_being_removed = list(self._classified_traps[event_type]) 
                del self._classified_traps[event_type] 
                
                if traps_being_removed:
                    ids_to_remove = {id(t) for t in traps_being_removed}
                    new_received_traps = collections.deque(
                        t for t in self._received_traps if id(t) not in ids_to_remove
                    )
                    removed_count = len(self._received_traps) - len(new_received_traps)
                    self._received_traps = new_received_traps
                    logger.info(f"Eliminados {removed_count} traps del tipo '{event_type}' de todas las colas.")
                else:
                    logger.info(f"No había traps en la lista clasificada '{event_type}'.")
            else:
                logger.info(f"No se encontraron traps o tipo de evento '{event_type}' para limpiar.")

    def get_all_raw_received_traps(self, consume_traps=False):
        with self._lock:
            traps_copy = list(self._received_traps) 
            if consume_traps:
                logger.warning("Consumiendo TODOS los traps recibidos de todas las colas.")
                self._received_traps.clear()
                self._classified_traps.clear()
            return traps_copy

    def count_traps_by_event_type(self, event_type):
        with self._lock:
            if event_type in self._classified_traps:
                return len(self._classified_traps[event_type])
            return 0
            
    def count_all_raw_received_traps(self):
        with self._lock:
            return len(self._received_traps)
        
        
    

# --- Fin Nuevas Keywords ---
if __name__ == '__main__':
    print("Iniciando listener de traps SNMP para prueba (con clasificación)...")
    
    mib_path_precompiled = None 
    # listener._mib_builder.addMibSources(builder.DirMibSource("ruta/a/tus/mibs_py"))
    # Asegúrate que tus MIBs compiladas (.py) están en PYTHONPATH o añadidas como arriba.

    listener = trapReceiver_Robot_3()
    
    # logging.getLogger().setLevel(logging.DEBUG) # Para depuración detallada
    # logging.getLogger('pysnmp').setLevel(logging.WARNING) # Para reducir verbosidad de pysnmp

    test_listen_ip = "10.212.42.4" 
    test_listen_port = 162 

    try:
        listener.start_trap_listener(listen_ip=test_listen_ip, listen_port=test_listen_port)
        
        try:
            logger.info("Cargando MIBs personalizadas: DIMAT-BASE-MIB, DIMAT-TPU1C-MIB (asegúrate que están compiladas y en PYTHONPATH)")
            listener.load_mibs("DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB") 
        except Exception as e:
            print(f"ADVERTENCIA: Error cargando MIBs personalizadas: {e}. Los OIDs podrían no resolverse a nombres.")

        print(f"Listener iniciado. Esperando traps en {test_listen_ip}:{test_listen_port}...")
        print(f"Clasificando por OID (nombre preferido): {listener._classification_oid_key_named}")
        print(f"Clasificando por OID (numérico): {listener._classification_oid_key_numeric}")

        print("\nEsperando 60 segundos para recibir traps...")
        start_wait_time = time.monotonic()
        while time.monotonic() - start_wait_time < 120:
            if listener._stop_event.is_set(): 
                print("Listener detenido durante la espera.")
                break
            # Imprime un punto cada 5 segundos para indicar que sigue esperando
            if int(time.monotonic() - start_wait_time) % 5 == 0:
                print(".", end="", flush=True)
                time.sleep(1) 
            else:  # Espera un poco para no saturar la CPU
                time.sleep(0.2)
        print("\nFin del periodo de espera.")

        print("\n--- Resumen de Traps Almacenados (Estructura Mínima) ---")
        event_types = listener.get_event_types()
        if not event_types:
            print("No se recibieron traps clasificados.")
        else:
            print(f"Tipos de evento (sanitizados) recibidos: {event_types}")
            for etype in event_types:
                count = listener.count_traps_by_event_type(etype)
                print(f"  - Tipo: '{etype}', Cantidad: {count}")
                
                # traps_of_type = listener.get_traps_by_event_type(etype, consume_traps=False, limit=1)
                # if traps_of_type:
                #     print(f"    Ejemplo de trap almacenado para '{etype}':")
                #     import json
                #     print(json.dumps(traps_of_type[0], indent=2, default=str)) 
        

        # --- Ejemplo de visualización específica de traps tpu1cNotifyCommandTx ---
        print("\n--- Visualización específica de traps 'DIMAT-TPU1C-MIB::tpu1cNotifyCommandTx' (si existen) ---")
        specific_event_key = "DIMAT-TPU1C-MIB::tpu1cNotifyCommandTx" 
        
        if specific_event_key in listener.get_event_types():
            print(f"Obteniendo traps para el tipo de evento: '{specific_event_key}'")
            tpu1c_traps = listener.get_traps_by_event_type(specific_event_key, consume_traps=False) 
            
            if tpu1c_traps:
                print(f"Se encontraron {len(tpu1c_traps)} traps del tipo '{specific_event_key}'. Su contenido almacenado es:")
                import json
                for i, trap_stored_data in enumerate(tpu1c_traps):
                    print(f"\nTrap Almacenado #{i+1} ({specific_event_key}):")
                    print(json.dumps(trap_stored_data, indent=2, default=str))
                    # Si quisieras ver solo el varbinds_dict de este trap específico:
                    # print(f"  Varbinds Dict: {json.dumps(trap_stored_data.get('varbinds_dict', {}), indent=2, default=str)}")
            else:
                print(f"No se encontraron traps para '{specific_event_key}' en este momento (aunque el tipo existe).")
        else:
            print(f"El tipo de evento '{specific_event_key}' no se encuentra entre los tipos recibidos.")
            print(f"Tipos disponibles: {listener.get_event_types()}")

    # Para ver todos los traps recibidos en la cola general (sin consumir):
        all_traps_raw = listener.get_all_raw_received_traps() # No consume por defecto
        print(f"\nTotal de traps en la cola general (_received_traps): {len(all_traps_raw)}")
        if all_traps_raw:
            import json
            for i, trap_stored_data in enumerate(all_traps_raw):
                print(f"\nTrap Almacenado #{i+1}:")
                print(json.dumps(trap_stored_data, indent=2, default=str))
                # Si quisieras ver solo el varbinds_dict de este trap específico:
                # print(f"  Varbinds Dict: {json.dumps(trap_stored_data.get('varbinds_dict', {}), indent=2, default=str)}")
        else:
            print(f"No se encontraron traps para '{specific_event_key}' en este momento (aunque el tipo existe).")


    except KeyboardInterrupt:
        print("\nInterrupción por teclado recibida.")
    except RuntimeError as e:
        print(f"Error de ejecución: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}", exc_info=True)
    finally:
        print("\nDeteniendo listener...")
        listener.stop_trap_listener()
        print("Listener detenido.")