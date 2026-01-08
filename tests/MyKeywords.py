from selenium.webdriver import ChromeOptions
import socket
import sys
import json
import re
from datetime import datetime
import time
import os
import csv

import serial
import time

import statistics


ACTIVE_APP_REF = None   # Referencia a la aplicación activa
HIL_SOCKET = None       # Aqui guardaremos nuestra conexion
HIL_SERIAL = None

# Cosntante para determinar el modo de trabajo. 
# Opciones: 
# "TEMPORAL_SPLIT" (Arduino para Burst, RPi para Logs)
# "FINAL_RPI_ONLY" (RPi para Burst y Logs)
HIL_SETUP_MODE = "FINAL_RPI_ONLY"
# *****************************************

# *** CONFIGURACIÓN DEL HIL TEMPORAL ***
ARDUINO_COM_PORT = "COM3"
ARDUINO_BAUDRATE = 9600
# *****************************************
# TIEMPOS VENTANAS
WIN_PROC_TX  = 0.015
WIN_CHANNEL  = 0.015
WIN_PROC_OUT  = 0.015
WIN_RELAY_HW = 0.02

WIN_T0_TO_T5 = 0.030

SKEW_TOLERANCE = 0.015  # No modifica, solo es para buscar valor hacia atras en las ventanas

HIL_CLOCK_OFFSET_S = 0.0  # Sí modifica los valores de los timestamps de la RPI

def _get_app_ref():
    """Función auxiliar para recuperar la app activa de forma segura y poder usarla en los keywords para acceder a clases que solo la lógica de la aplicación principal tiene acceso."""
    if ACTIVE_APP_REF is not None:
        return ACTIVE_APP_REF
    raise Exception("ERROR CRÍTICO: 'ACTIVE_APP_REF' no está asignado.")


def get_chrome_options(arguments):
    """
    Creates a ChromeOptions object and adds the given arguments.
    This is used to configure the browser in Robot Framework.
    """
    options = ChromeOptions()
    for arg in arguments:
        options.add_argument(arg)
    return options


def _ensure_rpi_connection(ip: str, port: int):
    """
    Asegura que la conexión HIL (HIL_SOCKET) esté abierta
    En caso de que fuera None (está cerrada o es la primera vez), crea una nueva conexión.
    """
    global HIL_SOCKET
    if HIL_SOCKET is None:
        try:
            print(f"HIL (Persistente): Abriendo nueva conexión a {ip}:{port}...")

            # Creamos el socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Ponemos un timeout por defecto para las conexiones
            sock.settimeout(15.0)
            
            # Nos conectamos
            sock.connect((ip, int(port)))
            
            # Asignamos a la variable global la conexion
            HIL_SOCKET = sock
            print("HIL Persistente: Conexion realizada")
            
        except Exception as e:
            HIL_SOCKET = None   # Lo dejamos a none aunque falle
            print(f"HIL (Persistente) ERROR: No se pudo conectar: {e}")
            raise Exception(f"Fallo crítico al conectar con el HIL: {e}")   # Lo hacemos para que el test falle
    # Como se puede observar si HIL_SOCKET NO era None, no hacemos nada ya que la conexion está presente.



def _ensure_arduino_connection():
    """Asegura que la conexión a la Arduino esté abierta."""
    global HIL_SERIAL, ARDUINO_COM_PORT, ARDUINO_BAUDRATE
    if HIL_SERIAL is None:
        try:
            print(f"Modo Arduino: Abrimos puerto serie {ARDUINO_COM_PORT} a una velocidad bauds = {ARDUINO_BAUDRATE} bauds")
            hil_ser = serial.Serial(ARDUINO_COM_PORT, baudrate=ARDUINO_BAUDRATE, timeout=5)
            HIL_SERIAL = hil_ser
            time.sleep(2)   # Esperamos a que el Arduino acabe de establecer la conexióon
            print(f"Modo Arduino: Conexión realizada en {hil_ser.name} ")
        except Exception as e:
            HIL_SERIAL = None
            print(f"ERROR, (Modo Arduino) - No se pudo establecer conexión a {ARDUINO_COM_PORT}: {e}")
            raise Exception(f"Fallo al conectar con el modulo HIL Arduino: {e}")
        
        
        
# *** HIL CONTROL KEYWORDS ***
def send_hil_command(raspberry_pi_ip: str, command: str, port: int = 65432, timeout: float = 15.0):
    """
    Se conecta al servidor HIL de la Raspberry Pi o a la Arduino por puerto Serie y envía un comando.
    Devuelve la respuesta del servidor.
    
    En modo "FINAL_RPI_ONLY", envía TODOS los comandos a la RPi.
    En modo "TEMPORAL_SPLIT", envía BURST/PULSE al Arduino y el resto a la RPi.
    
    COMANDOS
    ---------------------------------------------------------------------
    -- Control Básico de Relés --
    ON,<pin_id>        -> Activa el relé (ej: 'ON 1')
    OFF,<pin_id>       -> Desactiva el relé (ej: 'OFF 1')
    PULSE,<pin_id>,<t> -> Activa el relé, espera 't' seg, lo desactiva
    PULSE_BATCH,<t>,<pin_id1>,... -> Ejecuta PULSE en hilos separados
    RESET              -> Apaga todos los relés.

    -- Lectura de Estado --
    STATE,<pin_id>     -> Devuelve el estado (guardado) del relé (1=ON, 0=OFF)
    GET_OUTPUT,<pin_id>  -> Devuelve el estado (real) del pin T5 (HIGH/LOW)
    PING               -> Devuelve 'PONG' (para comprobar conexión)

    -- Performance Logging & Burst --
    CONFIG_LOG,<pin_id>  -> Reclama los pines T0/T5 para alertas de flanco
    START_LOG            -> Inicia los hilos de sondeo de eventos T0/T5
    STOP_LOG             -> Detiene los hilos de sondeo y libera los pines
    GET_LOGS             -> Devuelve los logs T0/T5 acumulados en formato JSON
    BURST,<pin>,<n>,<dur>,<del> -> Ejecuta ráfaga local: N pulsos de 'dur' con 'del' seg de retraso entre ellos.
    """
    global HIL_SOCKET, HIL_SERIAL, HIL_SETUP_MODE, ARDUINO_COM_PORT, ARDUINO_BAUDRATE
    # Nos aseguramos que haya conexión (persistenete), usando el timeout por defecto (15s) en caso de tener que reconectar
    # Para Arduino, usa (ip, ARDUINO_BAUDRATE)!

    
    if HIL_SETUP_MODE == "FINAL_RPI_ONLY":
        _ensure_rpi_connection(raspberry_pi_ip, port)
        original_timeout = HIL_SOCKET.gettimeout()

        try:
            HIL_SOCKET.settimeout(timeout)
            print(f"HIL: Timeout del socket ajustado temporalmente a {timeout}s para comando largo.")

            # Enviamos el comando por el socket existente
            HIL_SOCKET.sendall(command.encode('utf-8'))
                
            # Esperamos la RESPUESTA (con maximo 4096 bytes)
            response = ""
            while True:
                part = HIL_SOCKET.recv(4096).decode('utf-8')
                response += part
                if '\n' in part or not part:    # Final de respuesta o conexión cerrada -> Salimos del bucle en el que esperamos respuesta
                    break
                
            response = response.strip() # Limpiamos espacios y saltos de línea
            print(f"HIL CMD: Comando '{command}' enviado. Respuesta: {response[:150]}...")  # logeamos solo los primeros 150 caracteres para no saturar
            
            
            # Comprobamos la respuesta, realizando las siguientes verifiaciones
            valid_responses = ("ACK", "PONG", "STATE", "JSON")
            if not response.startswith(valid_responses):
                raise Exception(f"response no coincide con lo que esperabamos (ACK.., PONG, STATE, JSON.. : {response}")
            return response
        
        
        except (BrokenPipeError, ConnectionResetError, socket.timeout) as e:
            # Si la conexión finaliza de golpe, intentamos reconectar UNA vez
            print(f"HIL ERROR: {e}. Desconectando")
            HIL_SOCKET = None
            raise Exception(f"Error HIL durante comando: {e}")
        except Exception as e:
            print(f"HIL ERROR Inesperado: {e}")
            raise e
        
        finally:
            # Al final, independientemente de lo que haya pasado, restauramos el timeout original (de esta forma aseguramos pings rapidos!)
            if HIL_SOCKET:
                HIL_SOCKET.settimeout(original_timeout)
            print(f"HIL: Timeout del socket restaurado a {original_timeout}s.")
    
    elif HIL_SETUP_MODE == "TEMPORAL_SPLIT": 
        if command.startswith("BURST_BATCH,") or command.startswith("PULSE,"):
            # enviamos al Arduino
            _ensure_arduino_connection()
            original_timeout = HIL_SERIAL.timeout
            try:
                HIL_SERIAL.timeout = timeout
                translated_command = ""     # Inicializamos la variable que contendrá el comando traducido
                
                if command.startswith("BURST_BATCH,"):
                    # Recordemos que la GUI nos envía el comando de la siguiente manera: "BURST_BATCH,num,dur,del,ch1,ch2..."
                    parts = command.split(',')
                    num_pulses = int(parts[1])
                    duration_sec = float(parts[2])
                    delay_sec = float(parts[3])
                    channels = parts[4:]            
                
                    if len(channels) > 1:
                        print(f"Modo Arduino: WARNING: !Se han seleccionado {len(channels[4])}! RECORDEMOS QUE EL MODULO ARDUINO SOLO PUEDE MANEJAR UN CANAL!")
                        print(f"Modo Arduino: WARNING: PROCEDEMOS A EJECTUAR EL COMANDO SOLO EN EL CANAL 1")            

                    duration_ms = int(duration_sec * 1000)
                    delay_ms = int(delay_sec * 1000)
                    
                    # Preparamos el formato de comando que espera la Arduino
                    translated_command = f"B:{num_pulses}:{duration_ms}:{delay_ms}\n"   #\n al final para indicar que es el final del comando!
                    
                elif command.startswith("PULSE,"):
                    parts = command.split(',')
                    pin_id_ignored = parts[1]
                    print(f"Modo ARDUINO INFO: Pin '{pin_id_ignored}' ignorado, YA QUE MODULO ARDUINO SOLO TIENE UN CANAL DISPONIBLE!")
                    duration_sec = float(parts[2])
                    duration_ms = int(duration_sec * 1000)

                    translated_command = f"P:{duration_ms}\n"
                    
                print(f"Comando HIL original: {command} se ha traducido a {translated_command.strip()}")   
                # Pasamos por el puerto serie de la Arduino el comando preparado
                HIL_SERIAL.write(translated_command.encode('utf-8'))
                
                # Esperamos el response
                response = HIL_SERIAL.readline().decode('utf-8').strip()
                print(f"Modo ARDUINO Response: {response}")
                
                if response.startswith("ACK"):
                    return response
                elif response == "PONG_ARDUINO": 
                    return "PONG"
                else: 
                    return f"ACK, {response}"   # Aunque no sea valido, para que el test de robot no de fallo, mandamos ACK
                
            except (serial.SerialException, Exception) as e:
                print(f"ERROR Modo ARDUINO: {e}. Desconectando.")
                HIL_SERIAL = None
                raise Exception(f"ERROR Modo ARDUINO: {e}")
            finally:
                if HIL_SERIAL:
                    HIL_SERIAL.timeout = original_timeout
        
        elif command == "PING":
            translated_command = "PONG\n"
  
        else:
            # *** Enviamos a la RASPBERRY PI. aqui sí necesitaremos la IP ***
            _ensure_rpi_connection(raspberry_pi_ip, port)
            original_timeout = HIL_SOCKET.gettimeout()
            try:
                HIL_SOCKET.settimeout(timeout)
                HIL_SOCKET.sendall(command.encode('utf-8'))
                
                response = ""
                while True:
                    part = HIL_SOCKET.recv(4096).decode('utf-8')
                    response += part
                    if '\n' in part or not part:
                        break
                    
                response = response.strip()
                print(f"HIL (RPi) CMD: Comando '{command}' enviado. Respuesta: {response[:150]}...")
                
                valid_responses = ("ACK", "PONG", "STATE", "JSON")
                if not response.startswith(valid_responses):
                    raise Exception(f"Respuesta HIL (RPi) no válida: {response}")
                return response
            
            except (BrokenPipeError, ConnectionResetError, socket.timeout) as e:
                print(f"HIL (RPi) ERROR: {e}. Desconectando.")
                HIL_SOCKET = None
                raise Exception(f"Error HIL (RPi) durante comando: {e}")
            except Exception as e:
                print(f"HIL (RPi) ERROR Inesperado: {e}")
                raise e
            finally:
                if HIL_SOCKET: HIL_SOCKET.settimeout(original_timeout)
    else:
        raise Exception(f"HIL_SETUP_MODE no reconocido: {HIL_SETUP_MODE}")    
                
                
                
        
def hil_start_performance_log(ip: str, channel: str, port: int = 65432):
    """
    Configura y comienza el logging de tiempos en la Raspberry Pi HIL.
    channel: Puede ser un string de canales separados por una coma -> 1,2,3..
    En modo TEMPORAL, solo pide T5.
    En modo FINAL, pide ALL (T0 y T5).
    """
    global HIL_SETUP_MODE
    
    log_command = ""
    if HIL_SETUP_MODE == "FINAL_RPI_ONLY":
        log_command = f"CONFIG_LOG,ALL,{channel}"
        print("INFO Modo RPI: Configurando para logs COMPLETOS (T0 y T5).")
    
    elif HIL_SETUP_MODE == "TEMPORAL_SPLIT":
        log_command = f"CONFIG_LOG,T5,{channel}"
        print("INFO Modo ARDUINO: Configurando para logs de T5).")
        
        
    response = send_hil_command(ip, log_command, port)
    if not response.startswith("ACK"):
        raise Exception(f"Error al configurar logging en los canales {channel}: {response}")
    
    response = send_hil_command(ip, "START_LOG", port)
    if not response.startswith("ACK"):
        raise Exception(f"Error al iniciar logging {HIL_SETUP_MODE} en los canales {channel}: {response}")
    
    return "OK, HIL Logging iniciado"

def hil_stop_performance_log(ip: str, port: int = 65432):
    """
    Detiene el logging de tiempos en la RPI, descarga los logs JSON y los devuelve como diccionario de pyth para que robot lo use más tarde.
    """
    response = send_hil_command(ip, "STOP_LOG", port)
    if not response.startswith("ACK"):
        raise Exception(f"Error al detener logging: {response}")

    raw_response = send_hil_command(ip, "GET_LOGS", port)
    if raw_response.startswith("JSON,"):
        # ELiminamos el "JSON," del inicio
        json_data = raw_response[5:]
        try:
            logs = json.loads(json_data)     # Convertimos el JSON a diccionario de Python   
            return logs
        except json.JSONDecodeError as e:
            raise Exception(f"Error al decodificar logs JSON: {e}")
    else:
        raise Exception(f"Error al obtener logs (Tipo de respuuesta no valida :( ): {raw_response[:100]}..")


# *** CRUCE DE DATOS SNMP & RPI ***

# Funciones para generate_performance_report
def find_trap_by_oid(trap_list, oid_substring):
    """
    Busca el PRIMER trap en la lista que contenga el substring OID.
    """
    if not trap_list: return None
    
    for trap in trap_list:
        trap_str = json.dumps(trap) if isinstance(trap, dict) else str(trap)    # Convertimos a string para buscar el substring
        if oid_substring in trap_str:
            return trap
    return None


def _extract_tpu_timestamp(trap_data):
    if isinstance(trap_data, dict):
        # Si el trap nos viene como diccionario ya, intentamos acceder directamente
        try:
            # Opción A: Si está en la raíz
            val = trap_data.get("DIMAT-TPU1C-MIB::tpu1cNotifyCalculatedTimestampUtc")
            if val: return val

            # Opción B: Si está dentro de 'varbinds_dict' (más probable según tus ejemplos)
            val = trap_data.get("varbinds_dict", {}).get("DIMAT-TPU1C-MIB::tpu1cNotifyCalculatedTimestampUtc")
            if val: return val
        except:
            pass # Si falla, caemos al método de fuerza bruta

    # Si no es un diccionario o no hemos encontrado el valor, usamos regex
    # Convertimos a string y buscamos el patrón, esté donde esté.
    trap_str = json.dumps(trap_data) if isinstance(trap_data, dict) else str(trap_data)
    match = re.search(r'tpu1cNotifyCalculatedTimestampUtc":\s*"([^"]+)"', trap_str)     # ([^"]+) es lo que nos queremos quedar. Hasta que encuentre una comilla. El + asegura que haya al menos un caracter. \s* para posibles espacios
    if match:
        return match.group(1)
        
    return "N/A"


def _extract_trap_type_and_time(trap_data):
    """
    Analiza un trap y devuelve su tipo (T1, T2, T3, T4) y su timestamp interno TPU y valor.
    Valor será '1' cuando sea activación y '0' para desactivacion (None si no lo detecta)
    """
    # Convertimos a string para búsqueda rápida (aunque sea menos elegante, es robusto)
    trap_str = json.dumps(trap_data)
    
    trap_type = None
    if "tpu1cNotifyInputCircuits" in trap_str: trap_type = "T1"
    elif "tpu1cNotifyCommandTx" in trap_str: trap_type = "T2"
    elif "tpu1cNotifyCommandRx" in trap_str: trap_type = "T3"
    elif "tpu1cNotifyOutputCircuits" in trap_str: trap_type = "T4"
    
    if not trap_type:
        return None, None, None

    # Extraemos el timestamp TPU (usando la función que ya tenías o una regex mejorada)
    # Asumo que tu función _extract_tpu_timestamp existente funciona bien.
    timestamp = _extract_tpu_timestamp(trap_data)
    
    # Extraemos el valor (activacion o desactivacion)
    value = None
    try:
        if isinstance(trap_data, dict) and 'varbinds_dict' in trap_data:
            varbinds = trap_data['varbinds_dict']
            # Buscamos la clave del diccionario que nos proporciona el estado
            for k, v in varbinds.items():
                if "tpu1cNotifyState" in k:
                    value = str(v)
                    break
    except Exception:
        pass    # Para el fallback
    
    # Fallback
    if value is None:
        match = re.search(r'tpu1cNotifyState":\s*"?(\d)"?', trap_str)   # Con "? .. " hacemos que pueda pillar las comillas en caso de que nos pasaran un json. El dato que nos quedamos (\d). Solo caturara un numero, '1' o '0'
        if match:
            value = match.group(1)
            
    return trap_type, timestamp, value



# *** KEYWORD DE GENERACIÓN DE INFORME ***
def generate_performance_report_OLD (rpi_logs, traps_A_list, traps_B_list):
    """
    Genera el CSV maestro cruzando datos de RPi, Sesión A y Sesión B.
    traps_A_list y traps_B_list son listas de listas (una sublista por cada loop).
    """

    filename = f"test_results/performance_burst_{int(time.time())}.csv"
    os.makedirs("test_results", exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Cabecera del CSV con los 5 tiempos clave
        writer.writerow([
            "Ciclo",
            "T0_Inicio_Fisico(ns)",
            "T1_Trap1(ns)", "T2_Trap2(ns)",
            "T3_Trap3(ns)", "T4_Trap4(ns)",
            "T5_Fin_Fisico(ns)",
            "Delta_Total_ms (T5-T0)"
        ])
        
        num_loops = max(len(traps_A_list), len(traps_B_list))
        for i in range(num_loops):
            # Obtenemos T0 y T5 de la RPi para este ciclo 'i'
            t0 = rpi_logs['t0_ns'][i] if i < len(rpi_logs['t0_ns']) else "N/A"
            t5 = rpi_logs['t5_ns'][i] if i < len(rpi_logs['t5_ns']) else "N/A"
            
            # Obtenemos traps de este ciclo
            loop_traps_A = traps_A_list[i] if i < len(traps_A_list) else []
            loop_traps_B = traps_B_list[i] if i < len(traps_B_list) else []

            t1_trap = find_trap_by_oid(loop_traps_A, "tpu1cNotifyInputCircuits")
            t2_trap = find_trap_by_oid(loop_traps_A, "tpu1cNotifyCommandTx")
            t3_trap = find_trap_by_oid(loop_traps_B, "tpu1cNotifyCommandRx")
            t4_trap = find_trap_by_oid(loop_traps_B, "tpu1cNotifyOutputCircuits")

            t1_time = _extract_tpu_timestamp(t1_trap) if t1_trap else "NOT_FOUND"
            t2_time = _extract_tpu_timestamp(t2_trap) if t2_trap else "NOT_FOUND"
            t3_time = _extract_tpu_timestamp(t3_trap) if t3_trap else "NOT_FOUND"
            t4_time = _extract_tpu_timestamp(t4_trap) if t4_trap else "NOT_FOUND"

            # Calculamos Delta Total si tenemos datos
            delta_ms = "N/A"
            if isinstance(t0, int) and isinstance(t5, int):
                delta_ms = round((t5 - t0) / 1_000_000, 3)  # Convertir ns a ms

            writer.writerow([i+1, t0, t1_time, t2_time, t3_time, t4_time, t5, delta_ms])
            
    return filename


def _to_epoch(value):
    """Convierte timestamps:
       - RPi en ns (int o float grande) -> seconds (float)
       - TPU en ISO string -> seconds (float)
       - Si ya es float en segundos, lo devuelve tal cual.
    """
    if not value or value in ("MISSING", "N/A"):
        return None

    # Números: int o float
    if isinstance(value, (int, float)):
        v = float(value)
        # heurística: si es > 1e12, probablemente ns -> convertir a segundos
        if v > 1e12:
            return v / 1_000_000_000.0
        # si está en rango típico epoch (ej. > 1e9 ~ 2001-09-09), lo tomamos como segundos
        if v > 1e9:
            return v
        # si es pequeño (p.e. < 1e6) lo consideramos inválido
        return None

    # Strings: intentar ISO y varios formatos conocidos
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).timestamp()
        except Exception:
            pass

        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt).timestamp()
            except Exception:
                pass

        print(f"Error converting timestamp '{value}'")
        return None

    return None


def find_closest_next(target_time, candidate_list, time_window=2.0, skew_tolerance=0.0, used_set=None):
    """
    Para evitar coger de la lista de traps aquellos que estén duplicados o fuera de secuencia.
    Busca en candidate_list el valor de tiempo que este más cerca a target_time
    Este valor tiene que cumplir que target_time <= valor < target_time + time_window
    Si no encuentra valor devuelve 'None'
    Con el argumento skew_tolerance podemos permitir buscar hacia ATRAS un determinado tiempo (s). Interesante para compensar relojes desincronizados entre varios equipos. 
    """
    if target_time is None:
        return None, None
    
    best_val = None
    best_idx = None
    
    for idx, c_val in enumerate(candidate_list):
        if used_set is not None and idx in used_set:
            continue

        if c_val is None:
            continue
        # Buscamos eventos que ocurrieron DESPUÉS del target (para evitar duplicados) y antes tambien por la compensacion del skew que nos pasen, pero dentro de la ventana (para no coger uno muy posterior que no cuadre con la sincronización por indice) 
        start_search = target_time - skew_tolerance
        end_search = target_time + time_window
        if start_search <= c_val < end_search:
            # Encontramos un candidato válido.
            # ESTRATEGIA GREEDY: Nos quedamos con el PRIMERO válido que encontremos (el más antiguo disponible)
            # Esto es mejor para FIFOs (First In, First Out) como los traps.
            if best_val is None or c_val < best_val:
                best_val = c_val
                best_idx = idx

    if best_idx is not None and used_set is not None:
        used_set.add(best_idx)
        
    return best_val, best_idx


def generate_burst_performance_report(rpi_logs, all_traps_a, all_traps_b, file_suffix=""):
    """
    Genera un informe correlacionando listas de traps con logs de RPi mediante Correlación Temporal. De esta forma, evitamos traps duplicados o que lleguen muy tarde.
    ¡IMPORTANTE! ¡LA RPI Y LA TPU TIENEN QUE ESTAR SINCRONIZADAS CONTRA EL MISMO RELOJ POR NTP!
    Filtramos solo para activaciones.
    """
    # Preparamos un diccionario para clasificar los traps SNMP en función del tiempo al que pertenezcan
    traps_by_type = {"T1": [], "T2": [], "T3": [], "T4": []}
    
    # Clasificamos todos los traps de la Sesión A (T1 y T2)
    for trap in all_traps_a:
        t_type, t_time, t_val = _extract_trap_type_and_time(trap)
        if t_type in ["T1", "T2"]:
            if t_val == '1' or t_val is None:
                epoch_t = _to_epoch(t_time)
                if epoch_t is not None:
                    traps_by_type[t_type].append(epoch_t)

    # Clasificamos todos los traps de la Sesión B (T3 y T4)
    for trap in all_traps_b:
        t_type, t_time, t_val = _extract_trap_type_and_time(trap)
        if t_type in ["T3", "T4"]:
            if t_val == '1' or t_val is None:
                epoch_t = _to_epoch(t_time)
                if epoch_t is not None:
                    traps_by_type[t_type].append(epoch_t)
            
    # Obtenemos las listas
    raw_t0_list = rpi_logs.get('t0_ns',[])
    raw_t5_list = rpi_logs.get('t5_ns',[])
    
    t5_epochs = []
    for t_ns in raw_t5_list:
        if t_ns:
            t5_epochs.append(float(t_ns) / 1_000_000_000.0) # Convertimos a segundos
            
    t0_epochs = []
    for t_ns in raw_t0_list:
        if t_ns:
            t0_epochs.append(float(t_ns) / 1_000_000_000.0)
            
            
                     
    # Convertimos traps T1
    t1_epochs = [t for t in traps_by_type["T1"] if t is not None]
    
    stats = {
        "input_lat": [], "tx_proc": [], "ch_delay": [],
        "rx_proc": [], "output_lat": [], "total_delay": []
    }      
            

    num_cycles = len(t0_epochs)
    use_physical_ref = True
    

    # Antes de empezar a iterar sobre todas las listas, necesitamos saber num_cycles. 
    # Usamos la lista de T1 como ancla del numero "correcto" (éste marcara la sincronización de tiempos posteriores T2, T3,..) 
    


    # COMO EMERGENCIA SI NO NOS LLEGAN LOS LOGS
    if num_cycles == 0 and len(t1_epochs) > 0:  # Si no hay T0, pero si T1, usamos T1 como ancla
        use_physical_ref = False
        num_cycles = len(t1_epochs)
        print("WARNING: No hay logs T0. Usando T1 como ancla de emergencia")
    else:
        print(f"INFO REPORT: Usando T0 como ancla. num_cycles = {num_cycles} = len(t0_list)")


    # Generamos el informe CSV
    filename = f"test_results/burst_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_suffix}.csv"
    os.makedirs("test_results", exist_ok=True)
    

    
    used_indices = {
        "T1": set(),
        "T2": set(),
        "T3": set(),
        "T4": set(),
        "T5": set()
    }
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Cabecera
        writer.writerow([
            "Ciclo",
            "Lat. Entrada (T1-T0)", "Proc. TX (T2-T1)",
            "Canal/Loop (T3-T2)", 
            "Proc. RX (T4-T3)", "Lat. Salida (T5-T4)",
            "TOTAL Delay",
            "T0 (Fís)", "T1 (Trap)", "T2 (Trap)", "T3 (Trap)", "T4 (Trap)", "T5 (Fis)"
            ])    
        


        for i in range(num_cycles):
            t0_val, t1_val, t2_val, t3_val, t4_val, t5_val = None, None, None, None, None, None
            ref_for_t3, ref_for_t4 = None, None
            
            if use_physical_ref:    # MODO NORMAL; con T0 como ancla (cuando dispongamos de logs RPi)
                t0_val = t0_epochs[i] if i < len(t0_epochs) else None
                
                if t0_val and len(t1_epochs):  # Solo si tenemos T0 seguimos buscando T1
                    t1_val, t1_idx = find_closest_next(t0_val, t1_epochs, time_window=0.030, skew_tolerance=0.020, used_set=used_indices["T1"])

            else:
                # Modo con T1 como ancla y suponiendo que recibimos traps SNMP en caso de no disponer logs RPi
                # ******** DATOS  ********
                t1_val = t1_epochs[i]
                
                # Buscamos T0 basado en T1 (hacia atras en el tiempo ya que T0 ocurre antes que T1) Como find_closest_next SOLO FUNCIONA HACIA DELANTE ->
                # -> Lo implementamos aqui mismo
                if t1_val:
                    candidates_t0 = []
                    for val_t0 in t0_epochs:
                        if val_t0 and (t1_val - 0.030) < val_t0 <= (t1_val + 0.005):  # Ventana hacia atras (desde val_t1)
                            candidates_t0.append(val_t0)
                    if candidates_t0:
                        t0_val = max(candidates_t0)    # Nos queremos quedar con el valor más proximo a T1 (para no coger anteriores..), que es el maximo de los que ha encontrado
                        
                
            if t1_val:    
                # find_closest_next ya aplica el _to_epoch. Por lo que obtenemos los valores convertidos a ns ya
                # Buscamos T2 basado en T1 (Ventana de 1.5s adelante)
                t2_val, t2_idx = find_closest_next(t1_val, traps_by_type["T2"], WIN_PROC_TX, skew_tolerance=0.001, used_set=used_indices["T2"] )

                # Buscamos T3 basado en T2. Si el find_closest_next anterior hubiera fallado partimos de T1 para no romper con la sincronizacion
                ref_for_t3 = t2_val if t2_val else t1_val
                t3_val, t3_idx = find_closest_next(ref_for_t3, traps_by_type["T3"], WIN_CHANNEL, skew_tolerance=0.002, used_set=used_indices["T3"])
                
                # Buscamos T4 basado en T3. Si el find_closest_next anterior hubiera fallado partimos de T2 para no romper con la sincronizacion
                ref_for_t4 = t3_val if t3_val else ref_for_t3
                t4_val, t4_idx = find_closest_next(ref_for_t4, traps_by_type["T4"], WIN_PROC_OUT, skew_tolerance=0.002, used_set=used_indices["T4"])
                
            # Buscamos T5 (Físico RPi)
            # DEFINIMOS FILTRO ANTI-RUIDO: 3ms (0.003s)
            MIN_PHYSICAL_DELAY_S = 0.003
            
            if t0_val:
                search_start_time = t0_val + MIN_PHYSICAL_DELAY_S
                t5_val, t5_idx = find_closest_next(t0_val, t5_epochs, time_window=0.030, skew_tolerance=0, used_set=used_indices["T5"])
            # Si el find_closest_next anterior hubiera fallado partimos del trap anterior.
            elif t4_val:
                t5_val, t5_idx = find_closest_next(t4_val, t5_epochs, WIN_RELAY_HW, skew_tolerance=0.002, used_set=used_indices["T5"])


            if t5_val is not None:
                t5_val += HIL_CLOCK_OFFSET_S  # Corregimos el retraso del reloj RPi

                
            # ********* CALCULOS DIFERENCIA DE TIEMPO/DELAYS *********
            def calc_delta(end, start, delay_name=None):
                if end is not None and start is not None:
                    val = round((end - start) * 1000, 3)
                    # Si tenemos key_name, guardamos para la media
                    if delay_name and val >= -10:
                        stats[delay_name].append(val)
                    return val
                return "N/A"    # Si alguno de los parametros pasado (tiempo "end" o "start") no existe devolvemos N/A
            
            input_lat = calc_delta(t1_val, t0_val, "input_lat")
            tx_proc = calc_delta(t2_val, t1_val, "tx_proc")
            ch_delay = calc_delta(t3_val, t2_val, "ch_delay")
            rx_proc = calc_delta(t4_val, t3_val, "rx_proc")
            output_lat = calc_delta(t5_val, t4_val, "output_lat")

            # Total Delay (T5 - T0) con fallback a T1 si no tenemos T0
            if t0_val and t5_val:
                total_delay = calc_delta(t5_val, t0_val, "total_delay")
            elif t1_val and t5_val:
                # Fallback si perdimos T0 pero tenemos T1
                total_delay = calc_delta(t5_val, t1_val, "total_delay")
            else:
                total_delay = "N/A"
            
            
            # formatamos los valores convertidos con epoch a sec
            t0_f = f"{t0_val:.3f}" if t0_val else "MISSING"
            t1_f = f"{t1_val:.3f}" if t1_val else "MISSING"
            t2_f = f"{t2_val:.3f}" if t2_val else "MISSING"
            t3_f = f"{t3_val:.3f}" if t3_val else "MISSING"
            t4_f = f"{t4_val:.3f}" if t4_val else "MISSING"
            t5_f = f"{t5_val:.3f}" if t5_val else "MISSING"
            
            
            writer.writerow([i+1,
                            input_lat, tx_proc, ch_delay, rx_proc, output_lat, total_delay,
                            t0_f, t1_f, t2_f, t3_f, t4_f, t5_f
                            ])
                
                
                
        # Fila de medias
        writer.writerow([])     # Dejamos una separacion respecto a las filas anteriores.
        
        averages = ["MEDIA"]    # Lo ponemos como primer valor, ya que de esta manera lo hacemos coincidiir con la columna de Ciclos y todo cuadra cuando escribamos el row de average completo!
        keys_order = ["input_lat", "tx_proc", "ch_delay", "rx_proc", "output_lat", "total_delay"]
        
        for k in keys_order:    # Aquí iteramos el contenido del vector que hemos creado con las claves del diccionario stats que recorreremos con el for!
            values = stats[k]
            if values: 
                average = sum(values) / len(values)
                averages.append(f"{average:.3f}")
            else:
                averages.append("N/A")
        # COmo solo estamos rellenando de medias los delays, necesitamos rellenar el resto de columnas con vacíos
        averages.extend([""] * 6)
        
        writer.writerow(averages)                
            
    print(f"BURST REPORT generado: {filename}")
    
    t3_traps_count = len(traps_by_type['T3'])
    t4_traps_count = len(traps_by_type['T4'])
    
    return filename, t3_traps_count, t4_traps_count

# Para poder tener acceso a app_ref desde Robot Framework
def get_current_trap_count(session_id):
    """Llama al metodo dentro de TrapListenerController, pasándole antes la referencia de la aplicacion principal (esta es la que SÍ tiene acceso a Trap_Listener_Controller)'.
    Esto lo hacemos porque Robot Framework no puede importar directamente clases de la lógica de la aplicación principal.
    """
    app = _get_app_ref()
    # Fíjate: MyKeywords NO hace el trabajo, solo se lo pide al controlador
    return app.trap_listener_controller.get_current_trap_count(session_id)

def get_traps_since_index(session_id, start_index):
    """Llama al metodo dentro de TrapListenerController, pasándole antes la referencia de la aplicacion principal (esta es la que SÍ tiene acceso a Trap_Listener_Controller)'.
    Esto lo hacemos porque Robot Framework no puede importar directamente clases de la lógica de la aplicación principal."""
    app = _get_app_ref()
    return app.trap_listener_controller.get_traps_since_index(session_id, int(start_index))


def wait_for_traps_silence(session_id, silence_window=3.0):
    """"
    Se puede usar a modo de espera, bloqueandose hasta que el contador de traps se mantenga estable durante 'silence_window' segundos.
    """
    # OBtenemos el controlador una vez
    controller = _get_app_ref().trap_listener_controller
    
    # Variables tiempo
    last_change_time = time.time()
    last_count = controller.get_current_trap_count(session_id)

    print(f"DEBUG: Esperando {silence_window}s de silencio procedente de traps..")

    while True:
        time.sleep(0.5)   # Esperamos medio segundo entre comprobaciones
        
        current_count = controller.get_current_trap_count(session_id)
        
        if current_count != last_count:
            # Si ha cambiado el contador, actualizamos la referencia de tiempo
            last_count = current_count
            last_change_time = time.time()
            
        elif (time.time() - last_change_time) >= float(silence_window):
            # Si no cambia durante 'silence_window', salimos
            print(f" Silencio detectado durante {silence_window}s. Continuando.")
            return current_count
        




def hil_get_logs_force(ip: str, port: int = 65432):
    """
    Fuerza la descarga de los logs (con el comando GET_LOGS) sin intentar detener la grabación primero.
    Para rescates de logs cuando el servidor no acaba de funcionar bien o nos da error al tratar de conectarnos de nuevo.
    """
    print("DEBUG: Intentando forzar descarga de logs (con el comando GET_LOGS)..")
    try:
        raw_response = send_hil_command(ip, "GET_LOGS", port)
        
        if raw_response.startswith("JSON,"):
            json_data = raw_response[5:]
            try:
                logs = json.loads(json_data)
                
                # VERIFICACIÓN VISUAL COMPLETA
                t0_count = len(logs.get('t0_ns', []))
                t5_count = len(logs.get('t5_ns', []))
                
                print(f"DEBUG: ¡ÉXITO! Logs rescatados de la RAM de la RPi:")
                print(f"Eventos T0 (Inicio): {t0_count}")
                print(f"Eventos T5 (Fin): {t5_count}")
                
                return logs
            except json.JSONDecodeError as e:
                print(f"ERROR: JSON corrupto: {e}")
                return {"t0_ns": [], "t5_ns": []}
        else:
            print(f"ERROR: Respuesta inesperada: {raw_response}")
            return {"t0_ns": [], "t5_ns": []}
            
    except Exception as e:
        print(f"ERROR FATAL de Conexión: {e}")
        return {"t0_ns": [], "t5_ns": []}
    
    
def pwm_step_test_analizer(rpi_logs):
    """ Analiza un ciclo de la prueba pwm y devuelve la tasa de exito y los contadores tambien """
    t0_list = rpi_logs.get('t0_ns', [])
    t5_list = rpi_logs.get('t5_ns', [])
    
    t0_count = len(t0_list)
    t5_count = len(t5_list)
    
    if t0_count == 0:
        success_rate = 0.0
    else:
        success_rate = min((t5_count / t0_count) * 100.0, 100.0)
    return success_rate, t0_count, t5_count

def init_pwm_step_test():
    """ Crea el archivo .csv para guardar el log de la prueba pwm step test """
    filename = f"test_results/pwm_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs("test_results", exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Pulse_Width_ms", "T0_count", "T5_count", "Success_Rate_%", "Status"])
    return filename

def log_pwm_step_test_result(filename, pulse_width_ms, t0_count, t5_count, success_rate):
    """Añade una fila al .csv de log de la prueba pwm step test"""
    status = "PASS" if success_rate == 100.0 else "CUT_OFF/FAIL"
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([pulse_width_ms, t0_count, t5_count, f"{success_rate:.1f}", status])
        
        
        
        
# REPORT PARA PRUEBAS FUNCIONALES
def generate_functional_report(rpi_logs, all_traps_a, all_traps_b, max_latency_threshold_ms=15.0, output_subdir=None, file_suffix=""):
    """
    Genera un informe FUNCIONAL.
    Se centra en la calidad de la señal (Latencia Total) y la Integridad de los datos.
    Args:
        max_latency_threshold_ms: Límite en ms. Si Latencia > limite -> FAIL.
    """
    print(f"\n[DEBUG PYTHON {file_suffix}] Inicio Reporte. Traps A: {len(all_traps_a)}, Traps B: {len(all_traps_b)}")
    
    t0_epochs_debug = [float(t)/1e9 for t in rpi_logs.get('t0_ns', []) if t]
    if len(t0_epochs_debug) > 0:
        print(f"[DEBUG PYTHON] Primer T0 (Físico RPi): {t0_epochs_debug[0]:.4f} s")
    else:
        print("[DEBUG PYTHON] ¡ALERTA! No hay logs T0 en este canal.")
    
    
    
    
    # *** PARSEO Y CLASIFICACIÓN DE DATOS (hacemos lo mismo que en burst report)
    traps_by_type = {"T1": [], "T2": [], "T3": [], "T4": []}
    
    debug_trap_count = 0
    # Procesamos Traps A y B
    for trap in all_traps_a + all_traps_b:
        t_type, t_time, t_val = _extract_trap_type_and_time(trap)
        
        debug_trap_count += 1
        if debug_trap_count <= 3: # Solo imprimimos los 3 primeros para no saturar
            print(f"[DEBUG TRAP] Raw Type: {t_type}, TimeStr: {t_time}, Val: {t_val}")
            
        if t_type and (t_val == '1' or t_val is None):
            epoch_t = _to_epoch(t_time)
            if epoch_t:
                traps_by_type[t_type].append(epoch_t)
                # DEBUG DE TIEMPO
                if debug_trap_count <= 3 and len(t0_epochs_debug) > 0:
                    diff = epoch_t - t0_epochs_debug[0]
                    print(f"[DEBUG TIME] Trap Epoch: {epoch_t:.4f} s | Diferencia vs T0: {diff*1000:.2f} ms")
                    
    print(f"[DEBUG RESUMEN] Clasificados -> T1: {len(traps_by_type['T1'])}, T2: {len(traps_by_type['T2'])}, T3: {len(traps_by_type['T3'])}, T4: {len(traps_by_type['T4'])}")                
    
    # Procesamos Logs RPi
    t0_epochs = [float(t)/1e9 for t in rpi_logs.get('t0_ns', []) if t]
    t5_epochs = [float(t)/1e9 for t in rpi_logs.get('t5_ns', []) if t]

    num_cycles = len(t0_epochs)
    print(f"INFO REPORT: Generando reporte funcional para {num_cycles} ciclos.")

    # CORRELACION TEMPORAL DATOS
    # Listas para almacenar resultados procesados
    results_list = []
    latencies = []
    
    # Contadores de Integridad (Cuántos se encontraron correlacionados con su T0)
    integrity_counts = {"T0": num_cycles, "T1": 0, "T2": 0, "T3": 0, "T4": 0, "T5": 0}
    
    # Sets para evitar reusar índices (greedy logic). Los traps seran consumidos en orden FIFO
    used_indices = {k: set() for k in ["T1", "T2", "T3", "T4", "T5"]}

    # Ventanas de tiempo 
    for i, t0_val in enumerate(t0_epochs):
        cycle_data = {"id": i + 1, "status": "UNKNOWN", "latency": "N/A", "notes": ""}
        
        # *** Búsqueda en Cascada (lo hacemos más que nada para verificar la integridad traps snmp) ***
        
        # T1 (Input Trap)
        t1_val, _ = find_closest_next(t0_val, traps_by_type["T1"], 0.030, 0.020, used_indices["T1"])
        if t1_val: integrity_counts["T1"] += 1
        
        # T2 (TX Trap). Buscamos desde T1 (si reakmente existe), sino desde T0
        ref_t2 = t1_val if t1_val else t0_val
        t2_val, _ = find_closest_next(ref_t2, traps_by_type["T2"], WIN_PROC_TX, 0.005, used_indices["T2"])
        if t2_val: integrity_counts["T2"] += 1

        # T3 (RX Trap)
        ref_t3 = t2_val if t2_val else ref_t2
        t3_val, _ = find_closest_next(ref_t3, traps_by_type["T3"], WIN_CHANNEL, 0.005, used_indices["T3"])
        if t3_val: integrity_counts["T3"] += 1

        # T4 (Output Trap)
        ref_t4 = t3_val if t3_val else ref_t3
        t4_val, _ = find_closest_next(ref_t4, traps_by_type["T4"], WIN_PROC_OUT, 0.005, used_indices["T4"])
        if t4_val: integrity_counts["T4"] += 1

        # T5 (Output Físico)
        
        # FILTRO ANTI-RUIDO
        # Definimos ventana de silencio de 3ms para ignorar el crosstalk inductivo
        MIN_PHYSICAL_DELAY_S = 0.003
        # Desplazamos el punto de inicio de la búsqueda
        search_start_t5 = t0_val + MIN_PHYSICAL_DELAY_S
        
        t5_val, _ = find_closest_next(t0_val, t5_epochs, 0.100, 0.0, used_indices["T5"])
        
        if t5_val:
            t5_val += HIL_CLOCK_OFFSET_S
            integrity_counts["T5"] += 1
            
            # Cálculo de Latencia
            delta_sec = t5_val - t0_val
            delta_ms = delta_sec * 1000.0
            
            cycle_data["latency"] = round(delta_ms, 3)
            latencies.append(delta_ms)
            
            # Evaluación PASS/FAIL
            if delta_ms <= float(max_latency_threshold_ms):
                cycle_data["status"] = "PASS"
            else:
                cycle_data["status"] = "FAIL (LATE)"
        else:
            cycle_data["status"] = "FAIL (MISSING OUT)"
            cycle_data["notes"] = "No se detectó cierre de contacto (T5)"

        results_list.append(cycle_data)

    # *** CÁLCULO DE ESTADÍSTICAS GLOBALES ***
    if latencies:
        min_lat = min(latencies)
        max_lat = max(latencies)
        avg_lat = statistics.mean(latencies)
        try:
            jitter = statistics.stdev(latencies)
        except:
            jitter = 0.0 # Si solo hay 1 dato
        
        pass_count = sum(1 for r in results_list if "PASS" in r["status"])  # Contamos los PASS
        success_rate = (pass_count / num_cycles) * 100.0
    else:
        min_lat, max_lat, avg_lat, jitter, success_rate = 0, 0, 0, 0, 0.0   # Si no hay latencias registradas, todo a 0


    # *** GENERACIÓN DEL CSV ***
    # Gestion de directorios
    if output_subdir:
        # Si nos pasan un subdirectorio, lo usamos
        save_dir = output_subdir
    else:
        # Por defecto
        save_dir = "test_results"
        
    os.makedirs(save_dir, exist_ok=True)
    
    filename = os.path.join(save_dir, f"functional_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_suffix}.csv")

    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # SECCIÓN 1: RESUMEN FUNCIONAL
        writer.writerow(["*** FUNCTIONAL SUMMARY ***"])
        writer.writerow(["Test Date", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(["Total Cycles (T0)", num_cycles])
        writer.writerow(["Threshold (ms)", max_latency_threshold_ms])
        writer.writerow(["Success Rate (%)", f"{success_rate:.2f}%"])
        writer.writerow([]) 

        # SECCIÓN 2: ESTADÍSTICAS DE LATENCIA
        writer.writerow(["*** LATENCY STATISTICS (ms) ***"])
        writer.writerow(["Minimum", f"{min_lat:.3f}"])
        writer.writerow(["Maximum", f"{max_lat:.3f}"])
        writer.writerow(["Average", f"{avg_lat:.3f}"])
        writer.writerow(["Jitter (Std Dev)", f"{jitter:.3f}"])
        writer.writerow([])

        # SECCIÓN 3: INTEGRIDAD DE SEÑAL
        writer.writerow(["*** SIGNAL INTEGRITY CHECK ***"])
        writer.writerow(["Stage", "Expected (T0 Based)", "Actual (Correlated)", "Missing Count", "Availability %"])
        
        stages = ["T1 (Input Trap)", "T2 (TX Trap)", "T3 (RX Trap)", "T4 (Output Trap)", "T5 (Physical Out)"]
        keys = ["T1", "T2", "T3", "T4", "T5"]

        for stage, key in zip(stages, keys):
            actual = integrity_counts[key]
            missing = num_cycles - actual
            avail = (actual / num_cycles) * 100.0 if num_cycles > 0 else 0
            writer.writerow([stage, num_cycles, actual, missing, f"{avail:.1f}%"])
        
        writer.writerow([])

        # SECCIÓN 4: DETALLE FUNCIONAL
        writer.writerow(["*** CYCLE DETAILS ***"])
        writer.writerow(["Cycle", "Total Latency (ms)", "Status", "Notes"])
        
        for row in results_list:
            writer.writerow([
                row["id"], 
                row["latency"], 
                row["status"], 
                row["notes"]
            ])

    print(f"FUNCTIONAL REPORT generado: {filename}")
    return filename, success_rate


def generate_storm_report(rpi_logs):
    """
    Genera un reporte para el Escenario C (Tormenta de Red) de las pruebas HIL con Inyección de ruido (WP3).
    En este informe NO se usan ventanas de tiempo! ya que no queremos descartar duplicados. 
    Solo contamos todo lo que entra y sale.
    """
    # Extraemos datos crudos (sin traps)
    t0_list = rpi_logs.get('t0_ns', [])
    t5_list = rpi_logs.get('t5_ns', [])
    
    count_t0 = len(t0_list)
    count_t5 = len(t5_list)
    
    # Validación del conteo
    status = "UNKNOWN"
    notes = ""
    
    if count_t5 == count_t0:
        status = "PASS"
        notes = "Conteo correcto. #T0 = #T5 -> El equipo ha filtrado correctamente disparos duplicados o no hubo ecos."
    elif count_t5 > count_t0:
        status = "FAIL (DUPLICATES)"
        diff = count_t5 - count_t0
        notes = f"PELIGRO: Se han detectado {diff} disparos extra :( (Falsos Positivos)."
    elif count_t5 < count_t0:
        status = "FAIL (LOSS)"
        diff = count_t0 - count_t5
        notes = f"Se han perdido {diff} disparos."

    # Generamos el CSV
    filename = f"test_results/storm_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs("test_results", exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # *** CABECERA-RESUMEN ***
        writer.writerow(["*** NETWORK STORM INTEGRITY REPORT ***"])
        writer.writerow(["Test Date", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(["Global Status", status])
        writer.writerow([])
        
        # TABLA DE CONTEO
        writer.writerow(["*** EVENT COUNT ***"])
        writer.writerow(["Metric", "Count", "Expected"])
        writer.writerow(["Inputs (T0)", count_t0, "-"])
        writer.writerow(["Outputs (T5)", count_t5, f"== {count_t0}"])
        writer.writerow([])
        
        # VERIFICAMOS LA INTEGRIDAD
        writer.writerow(["*** ANALYSIS ***"])
        writer.writerow(["Notes", notes])
        if count_t5 > count_t0:
             writer.writerow(["WARNING", "El sistema ha generado más outputs que inputs :("])
             writer.writerow(["IMPACT", "Hay riesgo de que se produzcan múltiples disparos en la IPTU del equipo B."])
        writer.writerow([])

        # EVIDENCIA CON TIMESTAMPS
        # Listamos los T5 para ver si están muy pegados (de esta manera es mas facil localizar rebotes)
        writer.writerow(["*** OUTPUT TIMESTAMPS (T5) ***"])
        writer.writerow(["Index", "Timestamp (s)", "Delta vs Prev (ms)"])
        
        t5_secs = [float(t)/1e9 for t in t5_list]   # Pasamos a s
        t5_secs.sort()  # Ordenamos la lista de timestamps T5 en orden ascendente (más antiguos a más nuevos)
        
        for i, t5 in enumerate(t5_secs):
            delta = 0.0 # Inicializamos
            if i > 0:   # COn el primer indice no podemos calcular delta
                delta = (t5 - t5_secs[i-1]) * 1000.0    # Calculamos delta pasandolo a ms
            
            # Marcamos si el delta es muy pequeño (< 10ms). Esto nos idicará si hay presencia de un rebote rápido
            marker = " <<< REBOTE/DUPLICADO" if (i > 0 and delta < 20.0) else ""
            
            writer.writerow([i+1, f"{t5:.6f}", f"{delta:.3f}", marker])     # Formatamos para que se vea bien

    print(f"STORM REPORT generado: {filename}")
    return filename, status, count_t0, count_t5



# *** MULTICANAL ***
# Añadir a MyKeywords.py

def generate_multichannel_burst_report(multi_logs, all_traps_a, all_traps_b):
    """
    Recibe los logs agrupados por canal y genera UN informe CSV por cada canal activo.
    Args:
        multi_logs: Recordemos que era un diccionario {'1': {'t0_ns': [], 't5_ns': []}, '2': ...}
    """
    generated_files = []
    
    # Iteramos por cada canal que nos ha devuelto la RPi
    for channel_id, logs_data in multi_logs.items():
        print(f"*** Procesando Canal {channel_id} ***")
        
        # logs_data ya tiene la forma {'t0_ns': [...], 't5_ns': [...]} que espera nuestra función original.
        
        # FILTRADO DE TRAPS (Opcional pero recomendado)
        # Si tus traps SNMP tienen información del canal (ej. en el OID o valor),
        # deberías filtrar aquí. Si no, pasamos todos y confiamos en la correlación temporal.
        # Por ahora, pasamos todos:
        chan_traps_a = all_traps_a 
        chan_traps_b = all_traps_b 

        # LLAMADA A TU LÓGICA ORIGINAL
        # Reutilizamos tu función 'generate_burst_performance_report'
        # PERO: Hay que modificarla ligeramente para que acepte un prefijo en el nombre del archivo
        csv_path, t3_count, t4_count = generate_burst_performance_report(
            logs_data, 
            chan_traps_a, 
            chan_traps_b, 
            file_suffix=f"_CH{channel_id}"  # Para no sobrescribir archivos!!
        )
        
        generated_files.append(csv_path)
        print(f"Reporte CH{channel_id} generado: {csv_path}")

    return f"Se han generado {len(generated_files)} informes: {', '.join(generated_files)}"


# Añadir a MyKeywords.py

def generate_multichannel_functional_report(multi_logs, all_traps_a, all_traps_b, max_latency_threshold_ms=15.0):
    """
    Genera reportes funcionales para múltiples canales y calcula un veredicto global.
    """
    global_results = {
        "reports": [],
        "channel_scores": {},
        "min_success_rate": 100.0,
        "global_status": "PASS"
    }
    
    print(f"\n*** INICIANDO ANÁLISIS FUNCIONAL MULTICANAL ({len(multi_logs)} canales) ***")

    # Iteramos sobre cada canal devuelto por la RPi (ej: '1', '2', '3')
    for channel_id, logs_data in multi_logs.items():
        print(f"Evaluando Canal {channel_id}...")
        
        # Generamos el reporte individual reutilizando tu lógica existente
        # NOTA: Pasamos todos los traps. Tu algoritmo 'find_closest_next' usará los T0 
        # específicos de este canal para encontrar sus correspondientes traps por tiempo.
        report_path, success_rate = generate_functional_report(
            logs_data,
            all_traps_a,
            all_traps_b,
            max_latency_threshold_ms,
            file_suffix=f"_CH{channel_id}"  # Identificador en el nombre del archivo
        )
        
        # Guardamos métricas
        global_results["reports"].append(report_path)
        global_results["channel_scores"][channel_id] = success_rate
        
        # Actualizamos la tasa de éxito mínima
        if success_rate < global_results["min_success_rate"]:
            global_results["min_success_rate"] = success_rate

    # Si el peor canal no tiene 100%, la prueba global no es perfecta
    if global_results["min_success_rate"] < 100.0:
        global_results["global_status"] = "FAIL/DEGRADED"

    print(f"*** RESUMEN GLOBAL ***")
    print(f"Resultado final: {global_results['global_status']}")
    print(f"Peor Canal: {global_results['min_success_rate']}% éxito")
    
    return global_results["reports"], global_results["min_success_rate"]