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

class trapReceiver_Robot_2:
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
            # pysnmp's add_mib_compiler expects sources to be URLs or MIB module names,
            # not local directory paths directly for compilation.
            # It's better to use mib_builder.addMibSources for pre-compiled .py files
            # or ensure mib_dirs are in Python's path if they contain .py MIBs.
            # For compiled MIBs (.py files), they need to be in a directory listed in sys.path
            # or loaded explicitly if the MIB compiler setup is more complex.
            # The original code used add_mib_compiler, which is for compiling MIB text files.
            # If mib_dirs point to directories with .py files, those directories should be
            # added to where PySNMP looks for MIBs.
            # A common way is `self._mib_builder.addMibSources(builder.DirMibSource('path/to/compiled/mibs'))`
            # For simplicity, assuming `compiler.add_mib_compiler` was intended for setting up search paths
            # or that the MIBs are found via Python's import mechanism.
            # If these are directories of MIB text files to be compiled on the fly:
            try:
                compiler.add_mib_compiler(self._mib_builder, sources=mib_dirs)
                logger.info(f"Compilador MIB configurado para buscar MIBs de texto en: {mib_dirs}")
            except Exception as e:
                logger.error(f"Error configurando fuentes del compilador MIB con directorios {mib_dirs}: {e}. Asegúrate que son directorios de MIBs de texto.")

            # If mib_dirs are paths to *pre-compiled* MIBs (.py files)
            # you might need to add them differently, e.g., by ensuring they are in sys.path
            # or using mib_builder.addMibSources for PySNMP to find them.
            # Example for pre-compiled MIBs:
            # for m_dir in mib_dirs:
            #    self._mib_builder.addMibSources(builder.DirMibSource(m_dir.replace("file://", ""))) # Remove file:// if present
            # logger.info(f"Fuentes de MIBs (pre-compiladas) añadidas: {mib_dirs}")

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
        Reemplaza caracteres no alfanuméricos (excepto '::', '-', '_') por '_'.
        """
        if not isinstance(key_string, str):
            key_string = str(key_string)
        # Permitir MIB::name, guiones y guiones bajos. Reemplazar otros no alfanuméricos.
        return re.sub(r'[^\w:\-\.]', '_', key_string) # Added dot for OIDs like .0

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
                
                # Check if it's a community-based message (v1, v2c) and log community string
                community_name = "N/A"
                if hasattr(pMod, 'apiMessage') and hasattr(pMod.apiMessage, 'get_community'):
                    try:
                        community_name = pMod.apiMessage.get_community(reqMsg).prettyPrint()
                    except Exception:
                        community_name = "ErrorDecodingCommunity"
                
                logging.debug(f"Mensaje SNMPv{msgVer+1} (raw version {msgVer}) recibido de {transportAddress}. Comunidad: '{community_name}'")


                reqPDU = pMod.apiMessage.get_pdu(reqMsg)
                varBinds = pMod.apiPDU.get_varbinds(reqPDU)

                processed_var_binds = []
                for oid, val in varBinds:
                    try:
                        resolved_oid = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid), val).resolve_with_mib(self._mib_view_controller)
                        oid_name_str = str(resolved_oid[0].prettyPrint())
                        value_str = str(resolved_oid[1].prettyPrint()) # This could be an OID name if val is an OID
                        
                        # If the value itself is an OID (common for snmpTrapOID.0),
                        # its prettyPrint might be the name we want.
                        # For other types, it's the direct value.
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
                
                trap_data = {
                    'timestamp_received_utc': datetime.now(timezone.utc).isoformat(),
                    'transport_domain': str(transportDomain),
                    'transport_address': str(transportAddress),
                    'snmp_version': msgVer + 1, # User-friendly version (1, 2, 3)
                    'community_string': community_name,
                    'varbinds': processed_var_binds,
                    'varbinds_dict': {item['oid']: item['value'] for item in processed_var_binds if 'oid' in item and 'value' in item and isinstance(item['oid'], str)},
                    'pdu_type': reqPDU.__class__.__name__ # e.g., TrapPDU, SNMPv2TrapPDU
                }

                classification_key = "UNKNOWN_TRAP_TYPE" 

                # SNMPv1 Trap specific processing (PDU type is TrapPDU)
                if msgVer == api.SNMP_VERSION_1 and reqPDU.getTagSet() == pMod.TrapPDU.tagSet:
                    enterprise = pMod.apiTrapPDU.get_enterprise(reqPDU).prettyPrint()
                    generic_trap = int(pMod.apiTrapPDU.get_generic_trap(reqPDU))
                    specific_trap = int(pMod.apiTrapPDU.get_specific_trap(reqPDU))
                    
                    trap_data['enterprise'] = enterprise
                    trap_data['generic_trap'] = generic_trap
                    trap_data['specific_trap'] = specific_trap
                    trap_data['snmp_uptime'] = pMod.apiTrapPDU.get_timestamp(reqPDU).prettyPrint() # agent_addr also available

                    if generic_trap == 0: classification_key = f"{enterprise}::coldStart"
                    elif generic_trap == 1: classification_key = f"{enterprise}::warmStart"
                    elif generic_trap == 2: classification_key = f"{enterprise}::linkDown" # Often includes ifIndex in varbinds
                    elif generic_trap == 3: classification_key = f"{enterprise}::linkUp"   # Often includes ifIndex in varbinds
                    elif generic_trap == 4: classification_key = f"{enterprise}::authenticationFailure"
                    elif generic_trap == 5: classification_key = f"{enterprise}::egpNeighborLoss"
                    elif generic_trap == 6: # enterpriseSpecific
                        # Try to resolve specific trap using MIB, if possible, otherwise use number
                        # This part might need more sophisticated MIB handling for v1 specific traps
                        classification_key = f"{enterprise}::enterpriseSpecific.{specific_trap}"
                    else: classification_key = f"{enterprise}::genericTrap.{generic_trap}"
                
                # SNMPv2c / SNMPv3 Trap/Inform specific processing
                elif msgVer >= api.SNMP_VERSION_2C and \
                     (reqPDU.getTagSet() == pMod.SNMPv2TrapPDU.tagSet or reqPDU.getTagSet() == pMod.InformRequestPDU.tagSet):
                    
                    trap_oid_found = False
                    # The first varbind is often sysUpTime.0, the second is snmpTrapOID.0
                    # We search for snmpTrapOID.0 by its known OID or resolved name.
                    for vb in processed_var_binds:
                        # Check against both numeric and potentially resolved name of classification OID key
                        if vb['raw_oid'] == self._classification_oid_key_numeric or \
                           vb['oid'] == self._classification_oid_key_named:
                            # The 'value' of snmpTrapOID.0 is the actual notification OID
                            # This value should have been resolved to a name if MIBs are loaded.
                            classification_key = vb['value'] # This is already str(resolved_oid[1].prettyPrint()) from above
                            trap_oid_found = True
                            logging.debug(f"snmpTrapOID.0 ({vb['oid']}) encontrado, valor (tipo de trap): {classification_key}")
                            break
                    
                    if not trap_oid_found:
                        # If snmpTrapOID.0 is not found, this is unusual for a v2c/v3 trap.
                        # It might be a generic trap that doesn't follow the convention, or MIBs are missing.
                        # We can try to find a NotificationType object in the varbinds as a fallback.
                        # For now, we'll mark it.
                        logging.warning(f"SNMPv{msgVer+1} Trap/Inform de {transportAddress} no contiene {self._classification_oid_key_named} ({self._classification_oid_key_numeric}). Varbinds: {processed_var_binds}")
                        classification_key = f"SNMPv{msgVer+1}_TRAP_NO_TRAP_OID"
                else:
                    # Not a v1 trap, and not a v2c/v3 Trap/Inform PDU.
                    # Could be GetResponse, Report, etc., if listener receives them.
                    classification_key = f"NON_TRAP_PDU_{trap_data['pdu_type']}"

                safe_event_key = self._sanitize_event_key(classification_key)
                trap_data['event_type'] = safe_event_key 
                trap_data['original_event_type'] = classification_key

                logging.info(f"Trap recibido de {transportAddress[0]}:{transportAddress[1]} (Comunidad: '{community_name}') -> Tipo Original: '{classification_key}', Tipo Sanitizado/Almacenado: '{safe_event_key}'")
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    import json
                    logging.debug(f"Detalles del trap: {json.dumps(trap_data, indent=2)}")


                with self._lock:
                    self._received_traps.append(trap_data) # Add to general queue

                    if safe_event_key not in self._classified_traps:
                        self._classified_traps[safe_event_key] = collections.deque()
                    self._classified_traps[safe_event_key].append(trap_data)
                
                logging.debug(f"Trap procesado y almacenado bajo llave: {safe_event_key}. Total en general: {len(self._received_traps)}, Total para este tipo: {len(self._classified_traps[safe_event_key])}")

        except Exception as e:
            logging.error(f"Error fatal procesando mensaje/trap de {transportAddress}: {e}", exc_info=True)
        
        return wholeMsg # Important for pysnmp dispatcher

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
        # MIBs should be loaded via `Load Mibs` keyword after starting.
        # However, loading SNMPv2-MIB here can be beneficial for snmpTrapOID.0 resolution.
        try:
            logger.info("Cargando MIBs esenciales: SNMPv2-MIB, SNMPv2-SMI, SNMP-FRAMEWORK-MIB, SNMP-TARGET-MIB, SNMP-NOTIFICATION-MIB")
            self._mib_builder.load_modules(
                'SNMPv2-MIB', 
                'SNMPv2-SMI', # For ObjectIdentity, MibIdentifier etc.
                'SNMP-FRAMEWORK-MIB', # For security related OIDs if v3 is ever used
                'SNMP-TARGET-MIB',    # For notification target OIDs
                'SNMP-NOTIFICATION-MIB' # For snmpNotifyType etc.
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
            self._transport_dispatcher.close_dispatcher() # Clean up dispatcher if transport fails
            self._transport_dispatcher = None
            raise RuntimeError(f"Fallo al iniciar listener IPv4: {e}")
    
        self._listener_thread = threading.Thread(target=self._run_dispatcher_loop, daemon=True)
        self._listener_thread.start()
        
        time.sleep(0.1) # Give thread a moment to start
        if not self._listener_thread.is_alive():
            # Attempt to clean up dispatcher if thread didn't start
            if self._transport_dispatcher:
                self._transport_dispatcher.close_dispatcher()
                self._transport_dispatcher = None
            raise RuntimeError("El hilo del listener no pudo iniciarse.")
        logger.info("Hilo del dispatcher del listener iniciado.")

    def _run_dispatcher_loop(self):
        if not self._transport_dispatcher:
            logger.error("Transport dispatcher no inicializado en _run_dispatcher_loop.")
            return
            
        self._transport_dispatcher.job_started(1) # Must be paired with job_finished
        try:
            logger.debug("Iniciando self._transport_dispatcher.run_dispatcher()...")
            self._transport_dispatcher.run_dispatcher() 
        except Exception as e:
            if not self._stop_event.is_set(): # Log only if not an intentional stop
                logger.error(f"Excepción en el bucle del dispatcher (run_dispatcher): {e}", exc_info=True)
        finally:
            self._transport_dispatcher.job_finished(1) # Signal job completion
            logger.info("Bucle del dispatcher (run_dispatcher) finalizado.")

    def stop_trap_listener(self):
        if not self._listener_thread or not self._listener_thread.is_alive():
            if not self._stop_event.is_set(): 
                logger.info("El listener no está en ejecución o ya fue detenido.")
            self._stop_event.set() # Ensure stop event is set even if no thread
            return

        logger.info("Deteniendo el listener de traps...")
        self._stop_event.set() 
        
        if self._transport_dispatcher:
            # Unregister transports and close dispatcher
            # This should cause run_dispatcher() to return.
            try:
                self._transport_dispatcher.unregister_transport(udp.DOMAIN_NAME) # Important for clean shutdown
            except Exception as e:
                logger.warning(f"Error durante unregister_transport: {e}")
            
            self._transport_dispatcher.close_dispatcher()
            # No need for time.sleep here, join will wait.
        
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
        """
        Añade un filtro para `wait_for_trap`.
        - oid: El nombre del OID resuelto (ej: "IF-MIB::ifIndex.1") o el OID numérico.
        - value: El valor esperado para el OID. Si es None, solo se comprueba la presencia del OID.
        - condition: 'equals', 'contains', 'startswith', 'endswith', 'regex'.
        """
        with self._lock:
            self._trap_filters.append({'oid': oid, 'value': value, 'condition': condition.lower()})
        logger.info(f"Filtro añadido: OID='{oid}', Value='{value}', Condition='{condition}'")

    def clear_trap_filters(self):
        with self._lock:
            self._trap_filters.clear()
        logger.info("Todos los filtros de traps han sido eliminados.")

    def clear_all_received_traps(self):
        """Limpia todas las colas de traps: la general y todas las clasificadas."""
        with self._lock:
            self._received_traps.clear()
            self._classified_traps.clear()
        logger.info("Todas las colas de traps (general y clasificadas) limpiadas.")

    def _check_condition(self, actual_value, expected_value, condition):
        # This function is called by _trap_matches_filters
        # actual_value comes from trap_data['varbinds_dict'][oid_to_find]
        if actual_value is None and expected_value is not None: # OID present but value is None (should not happen if varbind has value)
             return False # or handle as per logic, maybe OID exists is enough if expected_value is None
        if expected_value is None: # If no value is expected, presence of OID is enough (handled in _trap_matches_filters)
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
        # This function assumes trap_data['varbinds_dict'] exists and maps OID names to values.
        if not self._trap_filters: # No filters, so all traps match
            return True

        for f_filter in self._trap_filters:
            oid_to_find = f_filter['oid']
            expected_value = f_filter['value']
            condition = f_filter['condition']
            
            # Check if OID exists in the trap's varbinds_dict
            # trap_data['varbinds_dict'] uses resolved OID names as keys.
            # The filter's 'oid' should also be a resolved name or a raw OID if that's what's in varbinds_dict keys
            # when resolution fails. For robustness, one might check both resolved and raw OID if filter can provide both.
            
            actual_value = trap_data['varbinds_dict'].get(oid_to_find)

            if actual_value is None: # OID not found in this trap
                # If expected_value is None, filter might mean "OID must NOT exist". This is not handled.
                # Current logic: if OID not found, this filter fails unless expected_value is also None (presence check).
                # Let's refine: if OID is not found, the filter does not match.
                return False 

            # OID was found, now check its value against the condition
            if not self._check_condition(actual_value, expected_value, condition):
                return False # This specific filter condition was not met for the OID.
        
        return True # All filters were successfully matched.

    def wait_for_trap(self, timeout=30, consume_trap=True):
        """
        Espera un trap que coincida con los filtros definidos en la cola GENERAL.
        Devuelve el primer trap coincidente o None.
        Los filtros se aplican usando `varbinds_dict` del trap.
        """
        end_time = time.monotonic() + float(timeout)
        logger.info(f"Esperando trap (en cola general) con filtros (timeout={timeout}s): {self._trap_filters if self._trap_filters else 'Ninguno'}")
        
        while time.monotonic() < end_time:
            if self._stop_event.is_set():
                logger.info("Espera de trap interrumpida por evento de parada.")
                break

            trap_to_return = None
            with self._lock:
                # Iterate carefully if consuming, as deque modification can be tricky.
                # A common pattern for consume: iterate, find, then remove outside iteration or by index.
                # For deque, removing from middle is inefficient (O(N)). Popping from ends is O(1).
                # If frequent consumption from middle is needed, consider alternative structures or marking.
                
                found_trap_index = -1
                for i, trap_data_item in enumerate(self._received_traps):
                    if self._trap_matches_filters(trap_data_item):
                        trap_to_return = trap_data_item # Found a match
                        found_trap_index = i
                        break # Process this trap

                if trap_to_return:
                    logger.info(f"Trap coincidente encontrado (cola general): Origen={trap_to_return['transport_address'][0]}, TipoEvento='{trap_to_return.get('event_type', 'N/A')}'")
                    if consume_trap:
                        # Efficiently remove if index is known (though list conversion for deque removal is still O(N))
                        # For deque, if we only ever consume the first match:
                        if found_trap_index == 0:
                             self._received_traps.popleft()
                        else:
                            # Rebuild deque without the item (if not too large) or use list conversion
                            temp_list = list(self._received_traps)
                            del temp_list[found_trap_index]
                            self._received_traps = collections.deque(temp_list)

                        # Also remove from classified list
                        event_type_key = trap_to_return.get('event_type') # This is the sanitized key
                        if event_type_key and event_type_key in self._classified_traps:
                            try:
                                self._classified_traps[event_type_key].remove(trap_to_return) # remove() on deque is O(N)
                                if not self._classified_traps[event_type_key]: # If deque becomes empty
                                    del self._classified_traps[event_type_key]
                                logger.debug(f"Trap consumido de la cola clasificada '{event_type_key}'.")
                            except ValueError:
                                logger.warning(f"Trap no encontrado en cola clasificada '{event_type_key}' al consumir, ¿ya fue consumido o inconsistencia?")
                        logger.debug(f"Trap consumido de la cola general. Restantes: {len(self._received_traps)}")
                    return trap_to_return 
            
            time.sleep(0.1) # Short sleep to avoid busy-waiting

        logger.info(f"Timeout esperando trap (cola general). No se encontró trap coincidente con filtros.")
        return None

    # --- Nuevas Keywords para Robot Framework ---

    def set_classification_oid(self, oid_string='SNMPv2-MIB::snmpTrapOID.0'):
        """
        DEPRECATED / INTERNAL DETAIL. La clasificación usa SNMPv2-MIB::snmpTrapOID.0 por defecto.
        Esta keyword se mantiene por si se necesita lógica de clasificación muy específica,
        pero la implementación actual se basa en el estándar snmpTrapOID.0.
        """
        logger.warning("set_classification_oid es principalmente para depuración interna. La clasificación estándar de v2c usa snmpTrapOID.0.")
        if not oid_string:
            logger.error("El OID de clasificación no puede ser vacío. Manteniendo el actual.")
            raise ValueError("El OID de clasificación no puede ser vacío.")
        
        # Attempt to resolve it to see if it's a valid OID format or MIB object
        # This is tricky as MIBs might not be loaded yet.
        # For now, just store it. The callback logic will use it.
        # It's better if this refers to the *name* of the OID in varbinds, e.g. 'SNMPv2-MIB::snmpTrapOID.0'
        # or its numeric equivalent.
        if "::" in oid_string : # Likely a named OID
            self._classification_oid_key_named = oid_string
            # We don't have a MIB view here to resolve it to numeric easily.
            # The callback will check both named and a default numeric.
        else: # Assume numeric
            self._classification_oid_key_numeric = oid_string
            # Try to find its name if MIBs are loaded (best effort)
            if self._mib_view_controller:
                try:
                    # This is a bit of a hack to resolve a plain OID string to a name
                    identity_node = rfc1902.ObjectIdentity(oid_string).resolve_with_mib(self._mib_view_controller)
                    self._classification_oid_key_named = identity_node.get_label() # or prettyPrint()
                    logger.info(f"OID numérico {oid_string} resuelto a {self._classification_oid_key_named} para clasificación.")
                except Exception as e:
                    logger.warning(f"No se pudo resolver el OID numérico {oid_string} a un nombre: {e}. Se usará el numérico.")
                    self._classification_oid_key_named = oid_string # Fallback to using numeric as named too
            else:
                 self._classification_oid_key_named = oid_string # No MIB view, use numeric as named

        logger.info(f"OID de clasificación (nombre preferido) establecido a: {self._classification_oid_key_named}")
        logger.info(f"OID de clasificación (numérico) establecido a: {self._classification_oid_key_numeric}")


    def get_event_types(self):
        """
        Devuelve una lista de todos los tipos de evento (claves de clasificación sanitizadas)
        para los cuales se han recibido traps.
        """
        with self._lock:
            return list(self._classified_traps.keys())

    def get_traps_by_event_type(self, event_type, consume_traps=True, limit=0):
        """
        Devuelve una lista de traps para el 'event_type' especificado (clave sanitizada).
        - event_type: La clave de clasificación sanitizada (ej: 'IF-MIB::linkDown', 'MY-MIB::myEvent_specific').
        - consume_traps: Si es True (defecto), los traps devueltos se eliminan de esta lista clasificada
                         y de la cola general _received_traps.
        - limit: Número máximo de traps a devolver. 0 (defecto) significa todos los disponibles.
        Devuelve una lista vacía si el tipo de evento no existe o no tiene traps.
        """
        # event_type aquí DEBE ser la clave sanitizada que se usó para almacenar.
        # No es necesario sanitizar de nuevo si el usuario provee la clave correcta.
        # Si el usuario provee la "original_event_type", entonces sí necesitaría sanitización aquí.
        # Para consistencia, la keyword debería esperar la misma forma de clave que get_event_types() devuelve.
        # event_type_sanitized = self._sanitize_event_key(event_type) # No, event_type should already be sanitized
        
        logger.debug(f"Solicitando traps para tipo de evento: '{event_type}', consumir: {consume_traps}, límite: {limit}")
        
        traps_to_return = []
        with self._lock:
            if event_type not in self._classified_traps:
                logger.info(f"No se encontraron traps para el tipo de evento: '{event_type}' (puede que necesite ser la versión sanitizada).")
                return []

            event_deque = self._classified_traps[event_type]
            
            count = 0
            # Determine how many to fetch
            num_to_fetch = len(event_deque)
            if limit > 0 and limit < num_to_fetch:
                num_to_fetch = limit

            if consume_traps:
                for _ in range(num_to_fetch):
                    if not event_deque: break # Should not happen if num_to_fetch is based on len(event_deque)
                    trap = event_deque.popleft() 
                    traps_to_return.append(trap)
                    try:
                        self._received_traps.remove(trap) # O(N) on deque, also O(N) on list if _received_traps is list
                    except ValueError:
                        logger.warning(f"Trap no encontrado en _received_traps al consumir de lista clasificada '{event_type}'. Pudo ser consumido antes o inconsistencia.")
                    count += 1
                if not event_deque: 
                    del self._classified_traps[event_type]
                    logger.info(f"Tipo de evento '{event_type}' ahora vacío y eliminado de listas clasificadas.")
            else: # No consumir, solo devolver copia
                # Iterate up to num_to_fetch and copy
                for i in range(num_to_fetch):
                    traps_to_return.append(event_deque[i]) # Access by index for deque
                count = len(traps_to_return)


        logger.info(f"Devueltos {count} traps para tipo de evento '{event_type}'. Consumidos: {consume_traps}")
        return traps_to_return

    def clear_traps_by_event_type(self, event_type):
        """
        Limpia todos los traps para un 'event_type' específico (clave sanitizada).
        Los traps también se eliminan de la cola general _received_traps.
        """
        logger.info(f"Limpiando traps para tipo de evento: '{event_type}'")
        # event_type_sanitized = self._sanitize_event_key(event_type) # Assume event_type is already sanitized
        with self._lock:
            if event_type in self._classified_traps:
                traps_being_removed = list(self._classified_traps[event_type]) # Get all traps for this type
                del self._classified_traps[event_type] # Delete the classified deque
                
                # Efficiently remove from _received_traps if it's large
                # Creating a new deque might be faster if many items are removed.
                if traps_being_removed:
                    # Create a set of IDs for fast lookup if traps are hashable (dicts are not directly)
                    # Or rely on object identity if they are the same objects.
                    # For dicts, using id() might work if they are not copied.
                    ids_to_remove = {id(t) for t in traps_being_removed}
                    new_received_traps = collections.deque(
                        t for t in self._received_traps if id(t) not in ids_to_remove
                    )
                    removed_count = len(self._received_traps) - len(new_received_traps)
                    self._received_traps = new_received_traps
                    logger.info(f"Eliminados {removed_count} traps del tipo '{event_type}' de todas las colas.")
                else:
                    logger.info(f"No había traps en la lista clasificada '{event_type}' para eliminar de la cola general.")
            else:
                logger.info(f"No se encontraron traps o tipo de evento '{event_type}' para limpiar.")

    def get_all_raw_received_traps(self, consume_traps=False):
        """
        Devuelve una COPIA de la lista de TODOS los traps recibidos en la cola general,
        sin importar su clasificación o filtros.
        Si consume_traps es True, la cola general _received_traps y las colas clasificadas
        serán vaciadas. ¡Usar con precaución!
        """
        with self._lock:
            traps_copy = list(self._received_traps) # Return a copy
            if consume_traps:
                logger.warning("Consumiendo TODOS los traps recibidos de todas las colas.")
                self._received_traps.clear()
                self._classified_traps.clear()
            return traps_copy


    def count_traps_by_event_type(self, event_type):
        """
        Devuelve el número de traps actualmente almacenados para el 'event_type' especificado (clave sanitizada).
        """
        # event_type_sanitized = self._sanitize_event_key(event_type) # Assume event_type is already sanitized
        with self._lock:
            if event_type in self._classified_traps:
                return len(self._classified_traps[event_type])
            return 0
            
    def count_all_raw_received_traps(self):
        """Devuelve el número total de traps en la cola general _received_traps."""
        with self._lock:
            return len(self._received_traps)

# --- Fin Nuevas Keywords ---
if __name__ == '__main__':
    print("Iniciando listener de traps SNMP para prueba (con clasificación)...")
    
    # Ejemplo de ruta MIBs (ajusta a tu entorno)
    # Para Windows: "file:///C:/Users/user/Documents/SNMP/compiled_mibs"
    # Para Linux/Mac: "file:///home/user/snmp/compiled_mibs" or "/usr/share/snmp/mibs"
    # Estas rutas son para add_mib_compiler si son MIBs de TEXTO.
    # Si son .py compiladas, deben estar en PYTHONPATH o cargadas con DirMibSource.
    # Para este ejemplo, asumimos que las MIBs .py están en una carpeta y la añadimos como DirMibSource.
    # Comenta o ajusta `mib_path_precompiled` según tu configuración.
    # mib_path_precompiled = "C:/Users/sergio.bret/Documents/SNMP/compiled_mibs" # Directorio con .py
    mib_path_precompiled = None # Descomentar y ajustar si tienes MIBs .py en una ruta específica.

    listener = trapReceiver_Robot_2()
    
    # Configurar el nivel de logging para ver más detalles si es necesario
    # logging.getLogger().setLevel(logging.DEBUG) # Para depuración detallada
    # logging.getLogger('pysnmp').setLevel(logging.ERROR) # Para silenciar logs de pysnmp si son muy verbosos

    test_listen_ip = "10.212.42.4" 
    test_listen_port = 162 

    try:
        # Inicializa el listener. MIBs se cargan después.
        # Si mib_path_precompiled está definido, se usará para añadir DirMibSource.
        # De lo contrario, se asume que las MIBs están en PYTHONPATH o son estándar.
        if mib_path_precompiled:
            # Esto es una forma de añadir directorios de MIBs .py, necesita hacerse ANTES de load_mibs
            # y preferiblemente dentro de _initialize_mib_controller o similar.
            # Por ahora, lo hacemos explícito antes de start_trap_listener para que _initialize_mib_controller las vea.
            # Esto es una simplificación; una mejor integración sería pasar la ruta a _initialize_mib_controller.
            # listener._mib_builder.addMibSources(builder.DirMibSource(mib_path_precompiled))
            # logger.info(f"Añadida fuente de MIBs precompiladas: {mib_path_precompiled}")
            # El mib_dirs_string en start_trap_listener es para MIBs de TEXTO.
            listener.start_trap_listener(listen_ip=test_listen_ip, listen_port=test_listen_port, mib_dirs_string="")
        else:
            listener.start_trap_listener(listen_ip=test_listen_ip, listen_port=test_listen_port)
        
        
        # Cargar MIBs necesarias. SNMPv2-MIB es crucial para snmpTrapOID.0.
        # Las MIBs personalizadas (DIMAT-BASE-MIB, DIMAT-TPU1C-MIB) deben estar compiladas a .py
        # y encontradas por PySNMP (e.g., en PYTHONPATH, o en un dir añadido con addMibSources).
        try:
            # Si tus MIBs .py están en una carpeta específica y no en PYTHONPATH,
            # necesitarías añadir esa carpeta a las fuentes del mib_builder ANTES de load_mibs.
            # Ejemplo: listener._mib_builder.addMibSources(builder.DirMibSource('ruta/a/tus/mibs_py'))
            # Esto se haría idealmente dentro de _initialize_mib_controller o antes de llamar a load_mibs.
            # Por ahora, la carga de MIBs esenciales ya se hace en start_trap_listener.
            
            logger.info("Cargando MIBs personalizadas: DIMAT-BASE-MIB, DIMAT-TPU1C-MIB")
            listener.load_mibs("DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB") 
        except Exception as e:
            print(f"ADVERTENCIA: Error cargando MIBs personalizadas: {e}. Los OIDs podrían no resolverse a nombres.")

        print(f"Listener iniciado. Esperando traps en {test_listen_ip}:{test_listen_port}...")
        print(f"Clasificando por OID (nombre): {listener._classification_oid_key_named}")
        print(f"Clasificando por OID (numérico): {listener._classification_oid_key_numeric}")


        # Simulación de espera de traps
        print("\nEsperando 60 segundos para recibir traps...")
        start_wait_time = time.monotonic()
        while time.monotonic() - start_wait_time < 60:
            if listener._stop_event.is_set(): # Check if listener was stopped externally
                print("Listener detenido durante la espera.")
                break
            # Imprimir un punto cada 5 segundos para mostrar actividad
            if int(time.monotonic() - start_wait_time) % 5 == 0:
                print(".", end="", flush=True)
                time.sleep(1) # Evitar imprimir múltiples puntos en el mismo segundo
            else:
                time.sleep(0.2)
        print("\nFin del periodo de espera.")

 
        # print("\n--- Resumen de Traps ---")   #Nos lista los tipos de evento que han llegado de los traps capturados y muestra el primer trap de cada tipo. 
        # event_types = listener.get_event_types()
        # if not event_types:
        #     print("No se recibieron traps clasificados.")
        # else:
        #     print(f"Tipos de evento (sanitizados) recibidos: {event_types}")
        #     for etype in event_types:
        #         count = listener.count_traps_by_event_type(etype)
        #         print(f"  - Tipo: '{etype}', Cantidad: {count}")
                
        #         # Obtener y mostrar (sin consumir) el primer trap de este tipo como ejemplo
        #         traps_of_type = listener.get_traps_by_event_type(etype, consume_traps=False, limit=1)
        #         if traps_of_type:
        #             print(f"    Ejemplo de trap para '{etype}':")
        #             import json
        #             # Usar json.dumps con un default para manejar tipos no serializables si los hubiera
        #             print(json.dumps(traps_of_type[0], indent=2, default=str)) 
        
 # --- INICIO: Bloque para visualizar traps tpu1cNotifyCommandTx ---
        print("\n--- Visualización específica de traps 'DIMAT-TPU1C-MIB::tpu1cNotifyCommandTx' ---")
        specific_event_key = "DIMAT-TPU1C-MIB::tpu1cNotifyCommandTx" # Esta es la clave esperada
        
        # Verificar si este tipo de evento fue recibido
        if specific_event_key in listener.get_event_types():
            print(f"Intentando obtener traps para el tipo de evento: '{specific_event_key}'")
            # Obtener todos los traps de este tipo, sin consumirlos
            tpu1c_traps = listener.get_traps_by_event_type(specific_event_key, consume_traps=False) 
            
            if tpu1c_traps:
                print(f"Se encontraron {len(tpu1c_traps)} traps del tipo '{specific_event_key}':")
                import json
                for i, trap in enumerate(tpu1c_traps):
                    print(f"\nTrap #{i+1} ({specific_event_key}):")
                    print(json.dumps(trap, indent=2, default=str))
            else:
                print(f"No se encontraron traps para '{specific_event_key}' en este momento (aunque el tipo existe).")
        else:
            print(f"El tipo de evento '{specific_event_key}' no se encuentra entre los tipos recibidos.")
            print(f"Tipos disponibles: {listener.get_event_types()}")
        # --- FIN: Bloque para visualizar traps tpu1cNotifyCommandTx ---

    # Para ver todos los traps recibidos en la cola general (sin consumir):
        # all_traps_raw = listener.get_all_raw_received_traps() # No consume por defecto
        # print(f"\nTotal de traps en la cola general (_received_traps): {len(all_traps_raw)}")
        # if all_traps_raw:
        #     print("Primer trap de la cola general (raw):")
        #     import json
        #     print(json.dumps(all_traps_raw[0], indent=2, default=str))

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

