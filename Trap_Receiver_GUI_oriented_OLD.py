# Trap_Receiver_GUI_oriented.py
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from pysnmp.smi import builder, view, compiler, rfc1902
from datetime import datetime, timezone, timedelta
from dateutil import parser

import threading
import time
import logging
import collections
import re
import pprint # Used for pretty printing dictionaries
import asyncio # Import asyncio

# Configuración de logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Usar un logger específico para la librería

class Trap_Receiver_GUI_oriented:
    
    # Definimos los OIDs fijos que queremos guardar
    _specific_desired_oids = {
        'DIMAT-TPU1C-MIB::tpu1cNotifyState',
        'DIMAT-TPU1C-MIB::tpu1cNotifyInputCurrentState',
        'DIMAT-TPU1C-MIB::tpu1cNotifyOutputCurrentState',
        'DIMAT-TPU1C-MIB::tpu1cNotifyCmdNum',
        'DIMAT-TPU1C-MIB::tpu1cNotifyCmdCurrentState',
        'DIMAT-TPU1C-MIB::tpu1cNotifyCounterValue'
    }
    _secs_oid_name = 'DIMAT-TPU1C-MIB::tpu1cNotifyTimeSecsUtc'
    _millis_oid_name = 'DIMAT-TPU1C-MIB::tpu1cNotifyTimeMillisecs'
    _calculated_timestamp_name = 'DIMAT-TPU1C-MIB::tpu1cNotifyCalculatedTimestampUtc'
    
    def __init__(self):
        self._transport_dispatcher = None
        self._mib_builder = None
        self._mib_view_controller = None
        self._received_traps = collections.deque() # Cola general de todos los traps recibidos
        self._classified_traps = {}   # Diccionario para almacenar traps por tipo de evento

        self._trap_filters = []
        self._listener_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock() # Protege _received_traps, _classified_traps, _trap_filters
        
        self._classification_oid_key_numeric = "1.3.6.1.6.3.1.1.4.1.0" # OID estándar
        self._classification_oid_key_named = "SNMPv2-MIB::snmpTrapOID.0" # Nombre simbólico

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
                logger.error(f"Error configurando fuentes del compilador MIB con directorios {mib_dirs}: {e}.")
        else:
            logger.info("No se proporcionaron directorios MIB, usando configuración por defecto del compilador MIB.")

    def load_mibs(self, *mib_modules):
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
                
                reqPDU = pMod.apiMessage.get_pdu(reqMsg)
                varBinds = pMod.apiPDU.get_varbinds(reqPDU)

                processed_var_binds = []
                temp_raw_value_store = {}
                
                for oid, val in varBinds:
                    try:
                        resolved_oid = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid), val).resolve_with_mib(self._mib_view_controller)
                        oid_name_str = str(resolved_oid[0].prettyPrint())
                        value_str = str(resolved_oid[1].prettyPrint())
                        processed_var_binds.append({'oid': oid_name_str, 'value': value_str, 'raw_oid': str(oid)})
                        temp_raw_value_store[oid_name_str] = value_str
                    except Exception as e:
                        logging.warning(f"Error resolviendo varbind {oid}={val}: {e}. Manteniendo valores raw.")
                        processed_var_binds.append({'oid': str(oid), 'value': str(val), 'raw_oid': str(oid)})
                        temp_raw_value_store[str(oid)] = str(val)
                
                calculated_timestamp_iso = None
                secs_str = temp_raw_value_store.get(self._secs_oid_name)
                millis_str = temp_raw_value_store.get(self._millis_oid_name)

                if secs_str is not None:
                    try:
                        secs_int = int(secs_str)
                        dt_object = datetime.fromtimestamp(secs_int, tz=timezone.utc)
                        if millis_str is not None:
                            try:
                                millis_int = int(millis_str)
                                if 0 <= millis_int <= 999:
                                    dt_object += timedelta(milliseconds=millis_int)
                            except (ValueError, TypeError):
                                pass
                        calculated_timestamp_iso = dt_object.isoformat()
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error al procesar timestamp: {e}")
                
                varbinds_dict_content = {
                    item['oid']: item['value'] 
                    for item in processed_var_binds 
                    if 'oid' in item and item['oid'] in self._specific_desired_oids and 'value' in item
                }
                
                if calculated_timestamp_iso:
                    varbinds_dict_content[self._calculated_timestamp_name] = calculated_timestamp_iso
                
                classification_key = "UNKNOWN_TRAP_TYPE"
                trap_oid_found = False
                for vb in processed_var_binds:
                    if vb['oid'] == self._classification_oid_key_named:
                        classification_key = vb['value'] 
                        trap_oid_found = True
                        break
                
                safe_event_key = self._sanitize_event_key(classification_key)
                
                trap_details_to_store = {
                    'timestamp_received_utc': datetime.now(timezone.utc).isoformat(),
                    'source_address': str(transportAddress[0]),
                    'event_type': safe_event_key,
                    'varbinds_dict': varbinds_dict_content
                }

                with self._lock:
                    self._received_traps.append(trap_details_to_store) 
                    if safe_event_key not in self._classified_traps:
                        self._classified_traps[safe_event_key] = collections.deque()
                    self._classified_traps[safe_event_key].append(trap_details_to_store)
                
                logging.info(f"Trap procesado y almacenado. Total en general: {len(self._received_traps)}")

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
            self._mib_builder.load_modules('SNMPv2-MIB', 'SNMP-FRAMEWORK-MIB')
        except Exception as e:
            logger.warning(f"Error cargando MIBs esenciales: {e}")

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
        # This is the method that runs in the background thread.
        # We need to create and set an event loop for this specific thread.
        asyncio.set_event_loop(asyncio.new_event_loop())

        if not self._transport_dispatcher:
            return
        self._transport_dispatcher.job_started(1)
        try:
            self._transport_dispatcher.run_dispatcher() 
        except Exception as e:
            if not self._stop_event.is_set():
                logger.error(f"Excepción en el bucle del dispatcher: {e}", exc_info=True)
        finally:
            self._transport_dispatcher.job_finished(1) 
            logger.info("Bucle del dispatcher finalizado.")

    def stop_trap_listener(self):
        if not self._listener_thread or not self._listener_thread.is_alive():
            if not self._stop_event.is_set(): 
                logger.info("El listener no está en ejecución o ya fue detenido.")
            self._stop_event.set() 
            return

        logger.info("Deteniendo el listener de traps...")
        self._stop_event.set() 
        
        if self._transport_dispatcher:
            self._transport_dispatcher.close_dispatcher()
        
        if self._listener_thread.is_alive():
            self._listener_thread.join(timeout=2.0)

        if self._listener_thread.is_alive():
            logger.warning("El hilo del listener no terminó correctamente.")
        else:
            logger.info("Listener de traps detenido y hilo terminado.")
        
        self._listener_thread = None
        self._transport_dispatcher = None 
        logger.info("Recursos del listener liberados.")

    def clear_all_received_traps(self):
        with self._lock:
            self._received_traps.clear()
            self._classified_traps.clear()
        logger.info("Todas las colas de traps limpiadas.")

    def get_all_raw_received_traps(self):
        with self._lock:
            return list(self._received_traps) 
            
    def get_filtered_traps_by_text(self, filter_text):
        """
        Returns a list of traps where the string representation contains the filter_text.
        """
        if not filter_text:
            return self.get_all_raw_received_traps()
            
        filtered_list = []
        filter_text_lower = filter_text.lower()
        with self._lock:
            for trap in self._received_traps:
                # Convert the whole trap dictionary to a string for searching
                trap_as_string = pprint.pformat(trap).lower()
                if filter_text_lower in trap_as_string:
                    filtered_list.append(trap)
        return filtered_list
    
    
    def get_traps_since(self, timestamp_iso_string):
        """
        Returns a list of traps received after the provided timestamp.
        """
        start_time = parser.isoparse(timestamp_iso_string)
        new_traps = []
        with self._lock:
            for trap in self._received_traps:
                trap_time = parser.isoparse(trap['timestamp_received_utc'])
                if trap_time > start_time:
                    new_traps.append(trap)
        return new_traps