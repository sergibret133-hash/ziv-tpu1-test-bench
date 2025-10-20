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
# from collections import deque
import collections
import re # Para la condición regex y para sanitizar nombres de claves

# Configuración de logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Usar un logger específico para la librería

class trapReceiver_Robot_1:
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
        self._classification_oid_key = 'SNMPv2-MIB::snmpTrapOID.0' # 1.3.6.1.6.3.1.1.4.1.0

    def _initialize_mib_controller(self, mib_dirs_string):
        logger.debug("Inicializando controladores MIB...")
        self._mib_builder = builder.MibBuilder()
        self._mib_view_controller = view.MibViewController(self._mib_builder)
        
        if mib_dirs_string:
            mib_dirs = [d.strip() for d in mib_dirs_string.split(',')]
            compiler.add_mib_compiler(self._mib_builder, sources=mib_dirs)
            logger.info(f"Compilador MIB configurado con directorios: {mib_dirs}")
        else:
            logger.info("No se proporcionaron directorios MIB, usando configuración por defecto del compilador MIB.")

    def load_mibs(self, *mib_modules):
        """
        Carga los módulos MIB especificados. Las MIBs deben estar pre-compiladas (.py)
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
        return re.sub(r'[^\w:\-]', '_', key_string)

    def _callback(self, transportDispatcher, transportDomain, transportAddress, wholeMsg):
        try:
            while wholeMsg:
                # Existing message decoding
                msgVer = int(api.decodeMessageVersion(wholeMsg))
                if msgVer in api.PROTOCOL_MODULES:
                    pMod = api.PROTOCOL_MODULES[msgVer]
                else:
                    logging.warning("Unsupported SNMP version %s" % msgVer)
                    return

                reqMsg, wholeMsg = decoder.decode(
                    wholeMsg,
                    asn1Spec=pMod.Message(),
                )

                # Get common PDU and varbinds (for v2c/v3)
                reqPDU = pMod.apiMessage.get_pdu(reqMsg)
                varBinds = pMod.apiPDU.get_varbinds(reqPDU)

                # Convert varbinds to a more friendly format (list of dicts)
                # and resolve OIDs to names
                processed_var_binds = []
                for oid, val in varBinds:
                    try:
                        # Resolve OID to name for better readability
                        resolved_oid = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid), val).resolve_with_mib(self._mib_view_controller)
                        processed_var_binds.append({
                            'oid': str(resolved_oid[0].prettyPrint()), # OID name
                            'value': str(resolved_oid[1].prettyPrint()), # Value
                            'raw_oid': str(oid), # Keep raw OID
                            'raw_value': str(val) # Keep raw value
                        })
                    except Exception as e:
                        logging.warning(f"Error resolving varbind {oid}={val}: {e}. Keeping raw values.")
                        processed_var_binds.append({
                            'oid': str(oid),
                            'value': str(val),
                            'raw_oid': str(oid),
                            'raw_value': str(val)
                        })
                
                # Extract common information
                trap_data = {
                    'timestamp_received_utc': datetime.now(timezone.utc).isoformat(),
                    'transport_domain': str(transportDomain),
                    'transport_address': str(transportAddress),
                    'snmp_version': msgVer,
                    'varbinds': processed_var_binds
                }

                # --- DYNAMIC CLASSIFICATION LOGIC ---
                classification_key = "UNKNOWN_TRAP" # Default if nothing else matches

                if msgVer == api.SNMP_VERSION_1: # SNMPv1 Trap
                    # For SNMPv1, derive classification from enterprise, generic, specific traps
                    enterprise = pMod.apiTrapPDU.get_enterprise(reqPDU).prettyPrint()
                    generic_trap = int(pMod.apiTrapPDU.get_generic_trap(reqPDU))
                    specific_trap = int(pMod.apiTrapPDU.get_specific_trap(reqPDU))
                    
                    # Add SNMPv1 specific fields to trap_data
                    trap_data['enterprise'] = enterprise
                    trap_data['generic_trap'] = generic_trap
                    trap_data['specific_trap'] = specific_trap
                    trap_data['snmp_uptime'] = pMod.apiTrapPDU.get_timestamp(reqPDU).prettyPrint()

                    # Common SNMPv1 generic traps have well-known names
                    if generic_trap == 0:
                        classification_key = f"{enterprise}::coldStart"
                    elif generic_trap == 1:
                        classification_key = f"{enterprise}::warmStart"
                    elif generic_trap == 2:
                        classification_key = f"{enterprise}::linkDown"
                    elif generic_trap == 3:
                        classification_key = f"{enterprise}::linkUp"
                    elif generic_trap == 4:
                        classification_key = f"{enterprise}::authenticationFailure"
                    elif generic_trap == 5:
                        classification_key = f"{enterprise}::egpNeighborLoss"
                    elif generic_trap == 6: # specific_trap for generic=6 (enterpriseSpecific)
                        classification_key = f"{enterprise}::enterpriseSpecific.{specific_trap}"
                    else:
                        classification_key = f"{enterprise}::genericTrap.{generic_trap}"

                elif msgVer >= api.SNMP_VERSION_2C: # SNMPv2c/v3 Trap
                    # For SNMPv2c/v3, try to find snmpTrapOID.0
                    trap_oid_found = False
                    for oid_obj, val_obj in pMod.apiPDU.get_varbinds(reqPDU):
                        if str(oid_obj) == str(self._classification_oid_key): # Check against the configured classification OID (default snmpTrapOID.0)
                            try:
                                # Resolve the trap OID to its friendly name
                                resolved_trap_oid = rfc1902.ObjectType(oid_obj, val_obj).resolve_with_mib(self._mib_view_controller)
                                classification_key = str(resolved_trap_oid[1].prettyPrint()) # Use the resolved value of snmpTrapOID.0 as the key
                                trap_oid_found = True
                                break
                            except Exception:
                                # If resolution fails, use the raw OID value
                                classification_key = str(val_obj.prettyPrint())
                                trap_oid_found = True
                                break
                    if not trap_oid_found:
                        # Fallback if snmpTrapOID.0 isn't found in a v2c/v3 trap (unlikely for standard traps)
                        classification_key = "SNMPv2c_TRAP_NO_TRAP_OID"
                else: # Other PDU types (e.g., GetResponse, which aren't traps)
                    classification_key = "NON_TRAP_PDU"
                
                # --- Store the received trap ---
                logging.info(f"*** Callback INICIADO - Trap recibido de {transportAddress} - Tipo clasificado: {classification_key}")
                
                # Always store the raw trap for full inspection
                # This is crucial for debugging if classification fails
                self._received_traps_raw.append(trap_data) 

                # Store in classified queues
                with self._lock:
                    if classification_key not in self._received_traps_by_type:
                        self._received_traps_by_type[classification_key] = collections.deque()
                    self._received_traps_by_type[classification_key].append(trap_data)
                    
                logging.debug(f"Trap procesado y almacenado: {classification_key}")

        except Exception as e:
            logging.error(f"Error procesando trap: {e}", exc_info=True)
        
        return wholeMsg # Important for pysnmp dispatcher

    def start_trap_listener(self, listen_ip="0.0.0.0", listen_port=162, mib_dirs_string=""):
        if self._listener_thread and self._listener_thread.is_alive():
            logger.info("El listener ya está en ejecución.")
            return

        self._stop_event.clear()
        with self._lock:
            self._received_traps.clear()
            self._classified_traps.clear() # Limpiar también las listas clasificadas
            self._trap_filters.clear()

        self._initialize_mib_controller(mib_dirs_string)
        # MIBs deben cargarse con `Load Mibs` después de `Start Trap Listener`

        self._transport_dispatcher = AsyncioDispatcher()
        self._transport_dispatcher.register_recv_callback(self._callback)

        try:
            self._transport_dispatcher.register_transport(
                udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_server_mode((listen_ip, int(listen_port)))
            )
            logger.info(f"Listener de traps SNMP (IPv4) iniciado en {listen_ip}:{int(listen_port)}")
        except Exception as e:
            logger.error(f"Error al registrar transporte UDP/IPv4 en {listen_ip}:{int(listen_port)}: {e}")
            raise RuntimeError(f"Fallo al iniciar listener IPv4: {e}")
    
        self._listener_thread = threading.Thread(target=self._run_dispatcher_loop, daemon=True)
        self._listener_thread.start()
        
        time.sleep(0.1)
        if not self._listener_thread.is_alive():
             raise RuntimeError("El hilo del listener no pudo iniciarse.")
        logger.info("Hilo del dispatcher del listener iniciado.")

    def _run_dispatcher_loop(self):
        if not self._transport_dispatcher:
            logger.error("Transport dispatcher no inicializado en _run_dispatcher_loop.")
            return
            
        self._transport_dispatcher.job_started(1)
        try:
            # Bucle principal que escucha I/O
            # runDispatcher() bloqueará hasta que jobFinished() o closeDispatcher() sea llamado
            logger.debug("Iniciando run_dispatcher()...")
            self._transport_dispatcher.run_dispatcher() 
        except Exception as e:
            # Un error aquí puede ser por close_dispatcher() mientras estaba bloqueado en select()
            # o un error más serio.
            if not self._stop_event.is_set(): # Si no fue una parada intencional
                 logger.error(f"Error en el bucle del dispatcher: {e}", exc_info=True)
        finally:
            self._transport_dispatcher.job_finished(1)
            logger.info("Bucle del dispatcher finalizado.")

    def stop_trap_listener(self):
        if not self._listener_thread or not self._listener_thread.is_alive():
            if not self._stop_event.is_set(): # Evitar logging redundante si ya se intentó parar
                logger.info("El listener no está en ejecución o ya fue detenido.")
            return

        logger.info("Deteniendo el listener de traps...")
        self._stop_event.set() # Señal para cualquier lógica que dependa de esto
        
        if self._transport_dispatcher:
            # Esto debería desbloquear run_dispatcher()
            self._transport_dispatcher.close_dispatcher()
            # Damos un respiro para que close_dispatcher procese y run_dispatcher salga.
            time.sleep(0.2) 

        if self._listener_thread.is_alive():
            self._listener_thread.join(timeout=5.0)

        if self._listener_thread.is_alive():
            logger.warning("El hilo del listener no terminó correctamente después del timeout.")
        else:
            logger.info("Listener de traps detenido y hilo terminado.")
        
        self._listener_thread = None
        self._transport_dispatcher = None # Liberar para posible reinicio limpio

    def add_trap_filter(self, oid, value=None, condition='equals'):
        with self._lock:
            self._trap_filters.append({'oid': oid, 'value': value, 'condition': condition.lower()})
        logger.info(f"Filtro añadido: OID={oid}, Value={value}, Condition={condition}")

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
        if expected_value is None:
            return True
        if actual_value is None:
            return False
            
        actual_value_str = str(actual_value)
        expected_value_str = str(expected_value)

        if condition == 'equals':
            return actual_value_str == expected_value_str
        elif condition == 'contains':
            return expected_value_str in actual_value_str
        elif condition == 'startswith':
            return actual_value_str.startswith(expected_value_str)
        elif condition == 'endswith':
            return actual_value_str.endswith(expected_value_str)
        elif condition == 'regex':
            return bool(re.search(expected_value_str, actual_value_str))
        else:
            logger.warning(f"Condición de filtro desconocida: {condition}")
            return False

    def _trap_matches_filters(self, trap_data):
        if not self._trap_filters:
            return True

        for f in self._trap_filters:
            oid_to_find = f['oid']
            expected_value = f['value']
            condition = f['condition']
            
            found_oid_in_trap = False
            # Usar varbinds_dict para búsqueda rápida de OID si solo se necesita el valor por OID
            # O iterar varbinds_list si el OID puede aparecer múltiples veces o se necesita el raw_value
            if oid_to_find in trap_data['varbinds_dict']:
                found_oid_in_trap = True
                actual_value = trap_data['varbinds_dict'][oid_to_find]
                if not self._check_condition(actual_value, expected_value, condition):
                    return False # Este filtro no coincide
            
            if not found_oid_in_trap and expected_value is not None: # Si el OID no está Y se esperaba un valor, el filtro falla
                 return False
            elif not found_oid_in_trap and expected_value is None: # Si el OID no está y solo se buscaba su presencia, el filtro falla
                 return False
            # Si el OID se encontró y la condición (o la ausencia de valor esperado) se cumplió, este filtro particular pasa.

        return True # Todos los filtros coincidieron

    def wait_for_trap(self, timeout=30, consume_trap=True):
        """
        Espera un trap que coincida con los filtros definidos en la cola GENERAL.
        Devuelve el primer trap coincidente o None.
        """
        end_time = time.monotonic() + float(timeout)
        logger.info(f"Esperando trap (en cola general) con filtros (timeout={timeout}s): {self._trap_filters}")
        
        while time.monotonic() < end_time:
            with self._lock:
                # Iterar sobre una copia para poder modificar _received_traps si consume_trap es True
                traps_to_scan = list(self._received_traps)
                for i, trap_data in enumerate(traps_to_scan):
                    if self._trap_matches_filters(trap_data):
                        logger.info(f"Trap coincidente encontrado (cola general): Origen={trap_data['source_ip']}, TipoEvento='{trap_data.get('event_type', 'N/A')}'")
                        if consume_trap:
                            # Eliminar de la cola general
                            # Esto es ineficiente para deque si el elemento no está al principio/final.
                            # Si se consume frecuentemente del medio, considerar otra estructura o estrategia.
                            try:
                                # Encuentra el mismo objeto trap en la deque original y elimínalo.
                                # Esto asume que los dicts de trap son únicos en memoria si no se copian profundamente antes.
                                self._received_traps.remove(trap_data) 
                                # También eliminar de la lista clasificada correspondiente
                                event_type_key = trap_data.get('event_type')
                                if event_type_key and event_type_key in self._classified_traps:
                                    if trap_data in self._classified_traps[event_type_key]:
                                        self._classified_traps[event_type_key].remove(trap_data)
                                        if not self._classified_traps[event_type_key]: # Si la deque queda vacía
                                            del self._classified_traps[event_type_key]
                                logger.debug(f"Trap consumido de la cola general y clasificada.")

                            except ValueError:
                                logger.warning("No se pudo encontrar el trap para consumir en _received_traps o _classified_traps, ¿quizás ya fue consumido?")
                        return trap_data
            if self._stop_event.is_set():
                logger.info("Espera de trap interrumpida por evento de parada.")
                break
            time.sleep(0.2)

        logger.info(f"Timeout esperando trap (cola general). No se encontró trap coincidente con filtros.")
        return None

    # --- Nuevas Keywords para Robot Framework ---

    def set_classification_oid(self, oid_string='SNMPv2-MIB::snmpTrapOID.0'):
        """
        Establece el OID cuyo valor se usará para clasificar los traps.
        Por defecto es 'SNMPv2-MIB::snmpTrapOID.0' (1.3.6.1.6.3.1.1.4.1.0).
        Si el OID no está presente en un trap, se clasificará como 'UNCLASSIFIED'.
        Este OID debe ser el *nombre resuelto* o el *OID numérico* que aparece
        en la clave 'oid' dentro de los varbinds de un trap.
        Ejemplo:
        | Set Classification OID | MY-CUSTOM-MIB::myEventTypeOID.0 |
        | Set Classification OID | 1.3.6.1.4.1.12345.1.1.0         |
        """
        if not oid_string:
            logger.error("El OID de clasificación no puede ser vacío. Manteniendo el actual.")
            raise ValueError("El OID de clasificación no puede ser vacío.")
        self._classification_oid_key = oid_string
        logger.info(f"OID de clasificación establecido a: {self._classification_oid_key}")

    def get_event_types(self):
        """
        Devuelve una lista de todos los tipos de evento (claves de clasificación)
        para los cuales se han recibido traps.
        """
        with self._lock:
            return list(self._classified_traps.keys())

    def get_traps_by_event_type(self, event_type, consume_traps=True, limit=0):
        """
        Devuelve una lista de traps para el 'event_type' especificado.
        - event_type: La clave de clasificación (ej: 'IF-MIB::linkDown').
        - consume_traps: Si es True (defecto), los traps devueltos se eliminan de esta lista clasificada
                         y de la cola general _received_traps.
        - limit: Número máximo de traps a devolver. 0 (defecto) significa todos los disponibles.
        Devuelve una lista vacía si el tipo de evento no existe o no tiene traps.
        """
        logger.debug(f"Solicitando traps para tipo de evento: '{event_type}', consumir: {consume_traps}, límite: {limit}")
        event_type_sanitized = self._sanitize_event_key(event_type) # Asegurar consistencia
        
        traps_to_return = []
        with self._lock:
            if event_type_sanitized not in self._classified_traps:
                logger.info(f"No se encontraron traps para el tipo de evento: '{event_type_sanitized}'")
                return []

            event_deque = self._classified_traps[event_type_sanitized]
            
            count = 0
            # Si se consume, necesitamos eliminar de la deque de forma segura
            # Si no se consume, simplemente copiamos los elementos.
            if consume_traps:
                while event_deque and (limit == 0 or count < limit):
                    trap = event_deque.popleft() # Tomar el más antiguo
                    traps_to_return.append(trap)
                    # También eliminar de la cola general _received_traps
                    try:
                        self._received_traps.remove(trap)
                    except ValueError:
                        # Podría pasar si fue consumido por wait_for_trap de la cola general
                        logger.warning(f"Trap no encontrado en _received_traps al consumir de lista clasificada '{event_type_sanitized}'. Pudo ser consumido antes.")
                    count += 1
                if not event_deque: # Si la deque quedó vacía después de consumir
                    del self._classified_traps[event_type_sanitized]
                    logger.info(f"Tipo de evento '{event_type_sanitized}' ahora vacío y eliminado de listas clasificadas.")
            else: # No consumir, solo devolver copia
                temp_list = list(event_deque) # Copia para iterar
                if limit > 0:
                    traps_to_return = temp_list[:limit]
                else:
                    traps_to_return = temp_list
                count = len(traps_to_return)

        logger.info(f"Devueltos {count} traps para tipo de evento '{event_type_sanitized}'. Consumidos: {consume_traps}")
        return traps_to_return

    def clear_traps_by_event_type(self, event_type):
        """
        Limpia todos los traps para un 'event_type' específico.
        Los traps también se eliminan de la cola general _received_traps.
        """
        logger.info(f"Limpiando traps para tipo de evento: '{event_type}'")
        event_type_sanitized = self._sanitize_event_key(event_type)
        with self._lock:
            if event_type_sanitized in self._classified_traps:
                traps_to_remove = list(self._classified_traps[event_type_sanitized]) # Copia para iterar
                del self._classified_traps[event_type_sanitized]
                
                # Eliminar de la cola general _received_traps
                # Esto puede ser lento si _received_traps es muy grande.
                # Una alternativa sería marcar los traps como "borrados" o reconstruir la lista.
                new_received_traps = collections.deque()
                removed_count = 0
                for trap in self._received_traps:
                    if trap not in traps_to_remove: # Compara por identidad de objeto (dict)
                        new_received_traps.append(trap)
                    else:
                        removed_count +=1
                self._received_traps = new_received_traps
                logger.info(f"Eliminados {removed_count} traps del tipo '{event_type_sanitized}' de todas las colas.")
            else:
                logger.info(f"No se encontraron traps o tipo de evento '{event_type_sanitized}' para limpiar.")

    def get_all_raw_received_traps(self):
        """
        Devuelve una COPIA de la lista de TODOS los traps recibidos en la cola general,
        sin importar su clasificación o filtros.
        Los traps NO se consumen.
        """
        with self._lock:
            # Devuelve una copia para evitar modificaciones externas de la lista interna
            return list(self._received_traps)

    def count_traps_by_event_type(self, event_type):
        """
        Devuelve el número de traps actualmente almacenados para el 'event_type' especificado.
        """
        event_type_sanitized = self._sanitize_event_key(event_type)
        with self._lock:
            if event_type_sanitized in self._classified_traps:
                return len(self._classified_traps[event_type_sanitized])
            return 0
            
    def count_all_raw_received_traps(self):
        """Devuelve el número total de traps en la cola general _received_traps."""
        with self._lock:
            return len(self._received_traps)

# --- Fin Nuevas Keywords ---
if __name__ == '__main__':
    print("Iniciando listener de traps SNMP para prueba (con clasificación)...")
    mib_path = "file:///C:/Users/sergio.bret/Documents/SNMP/compiled_mibs" 

    listener = trapReceiver_Robot_1()
    
    test_listen_ip = "10.212.42.4" 
    test_listen_port = 162 # Puerto no estándar para evitar conflictos y no requerir root

    try:
        # Primero, inicia el listener. MIBs se cargan después.
        listener.start_trap_listener(listen_ip=test_listen_ip, listen_port=test_listen_port, mib_dirs_string=mib_path)
        
        # Es crucial cargar SNMPv2-MIB para que snmpTrapOID.0 se resuelva correctamente.
        # Añade tus MIBs personalizadas también.
        try:
            listener.load_mibs("SNMPv2-MIB", "DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB") # MIBs básicas
        except Exception as e:
            print(f"ADVERTENCIA: Error cargando MIBs: {e}. Los OIDs podrían no resolverse a nombres.")

        # Opcional: Cambiar el OID usado para clasificación si no es snmpTrapOID.0
        # listener.set_classification_oid("MY-MIB::myCustomTrapTypeIdentifier.0")

        print(f"Listener iniciado. Esperando traps en {test_listen_ip}:{test_listen_port}...")
        print(f"Clasificando por OID: {listener._classification_oid_key}")

        # Esperar un tiempo para recibir traps
        print("\nEsperando 60 segundos para recibir traps...")
        time.sleep(60) # Espera activa

        print("\n--- Resumen de Traps ---")
        event_types = listener.get_event_types()
        if not event_types:
            print("No se recibieron traps clasificados.")
        else:
            print(f"Tipos de evento recibidos: {event_types}")
            for etype in event_types:
                count = listener.count_traps_by_event_type(etype)
                print(f"  - Tipo: '{etype}', Cantidad: {count}")
                
                # Obtener y mostrar (sin consumir) el primer trap de este tipo COMO EJEMPLO (YA QUE HEMOS PUESTO LIMIT=1)
                traps_of_type = listener.get_traps_by_event_type(etype, consume_traps=False, limit=1)
                if traps_of_type:
                    print(f"    Ejemplo de trap para '{etype}':")
                    import json
                    print(json.dumps(traps_of_type[0], indent=2))   # Cogemos el primero porque no van haber más traps de este tipo ya que lo hemos limitado a 1
                    #Para hacerlo bonito le dice a Json que lo imprima con indentación
                
                # Ejemplo de consumo:
                # consumed_traps = listener.get_traps_by_event_type(etype, consume_traps=True)
                # print(f"Consumidos {len(consumed_traps)} traps del tipo '{etype}'")

        all_traps_raw = listener.get_all_raw_received_traps()
        print(f"\nTotal de traps en la cola general (_received_traps): {len(all_traps_raw)}")
        if all_traps_raw:
             print("Primer trap de la cola general (raw):")
             import json
             print(json.dumps(all_traps_raw[0], indent=2))

    except KeyboardInterrupt:
        print("\nInterrupción por teclado recibida.")
    except RuntimeError as e:
        print(f"Error de ejecución: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        print("\nDeteniendo listener...")
        listener.stop_trap_listener()
        print("Listener detenido.")