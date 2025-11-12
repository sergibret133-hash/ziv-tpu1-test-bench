from selenium.webdriver import ChromeOptions
import socket
import sys
import json
import re
from datetime import datetime
import time
import os
import csv

ACTIVE_APP_REF = None   # Referencia a la aplicación activa
HIL_SOCKET = None       # Aqui guardaremos nuestra conexion

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


def _ensure_hil_connection(ip: str, port: int):
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
# *** HIL CONTROL KEYWORDS ***
def send_hil_command(raspberry_pi_ip: str, command: str, port: int = 65432, timeout: float = 15.0):
    """
    Se conecta al servidor HIL de la Raspberry Pi y envía un comando.
    Devuelve la respuesta del servidor.
    
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
    global HIL_SOCKET
    # Nos aseguramos que haya conexión (persistenete), usando el timeout por defecto (15s) en caso de tener que reconectar
    _ensure_hil_connection(raspberry_pi_ip, port)
    
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
        print(f"HIL ERROR: {e}. Intentando reconectar...")
        HIL_SOCKET = None
        # Faltaría establecer la reconexión...
        raise Exception(f"Error HIL durante comando: {e}")
    except Exception as e:
        print(f"HIL ERROR Inesperado: {e}")
        raise e
    
    finally:
        # Al final, independientemente de lo que haya pasado, restauramos el timeout original (de esta forma aseguramos pings rapidos!)
        if HIL_SOCKET:
            HIL_SOCKET.settimeout(original_timeout)
        print(f"HIL: Timeout del socket restaurado a {original_timeout}s.")
        
def hil_start_performance_log(ip: str, channel: str, port: int = 65432):
    """
    Configura y comienza el logging de tiempos en la Raspberry Pi HIL.
    channel: 'T0' o 'T5'
    """
    response = send_hil_command(ip, f"CONFIG_LOG,{channel}", port)
    if not response.startswith("ACK"):
        raise Exception(f"Error al configurar logging en canal {channel}: {response}")
    
    response = send_hil_command(ip, "START_LOG", port)
    if not response.startswith("ACK"):
        raise Exception(f"Error al iniciar logging en canal {channel}: {response}")
    
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
    Analiza un trap y devuelve su tipo (T1, T2, T3, T4) y su timestamp interno TPU.
    Devuelve (tipo, timestamp_str) o (None, None) si no es relevante.
    """
    # Convertimos a string para búsqueda rápida (aunque sea menos elegante, es robusto)
    trap_str = json.dumps(trap_data)
    
    trap_type = None
    if "tpu1cNotifyInputCircuits" in trap_str: trap_type = "T1"
    elif "tpu1cNotifyCommandTx" in trap_str: trap_type = "T2"
    elif "tpu1cNotifyCommandRx" in trap_str: trap_type = "T3"
    elif "tpu1cNotifyOutputCircuits" in trap_str: trap_type = "T4"
    
    if not trap_type:
        return None, None

    # Extraemos el timestamp TPU (usando la función que ya tenías o una regex mejorada)
    # Asumo que tu función _extract_tpu_timestamp existente funciona bien.
    timestamp = _extract_tpu_timestamp(trap_data)
    
    return trap_type, timestamp



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


def generate_burst_performance_report(rpi_logs, all_traps_a, all_traps_b):
    """
    Genera un informe correlacionando listas de traps con logs de RPi.
    """
    # Preparamos un diccionario para clasificar los traps SNMP en función del tiempo al que pertenezcan
    traps_by_type = {"T1": [], "T2": [], "T3": [], "T4": []}
    
    # Clasificamos todos los traps de la Sesión A (T1 y T2)
    for trap in all_traps_a:
        t_type, t_time = _extract_trap_type_and_time(trap)
        if t_type in ["T1", "T2"]:
            traps_by_type[t_type].append(t_time)

    # Clasificamos todos los traps de la Sesión B (T3 y T4)
    for trap in all_traps_b:
        t_type, t_time = _extract_trap_type_and_time(trap)
        if t_type in ["T3", "T4"]:
            traps_by_type[t_type].append(t_time)
            
    # Asumimos que los traps llegan ordenados. Aunque lo ideal sería ordenar las listas..
    
    # Generamos el informe CSV
    filename = f"test_results/burst_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs("test_results", exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Cabecera
        writer.writerow(["Ciclo", "T0 (Físico IN)", "T1 (Trap IN)", "T2 (Trap TX)", "T3 (Trap RX)", "T4 (Trap OUT)", "T5 (Físico OUT)", "Delta Total (ms)"])    
        
        
        num_cycles = len(rpi_logs.get('t0_ns', [])) # Utilizamos get() por si no llegaran logs, haríamos len de un vector vacio, y nos daría como resultado 0 en lugar de error
        
        for i in range(num_cycles):
            # Obtenemos T0 y T5
            t0 = rpi_logs['t0_ns'][i] if i < len(rpi_logs['t0_ns']) else "MISSING"
            t5 = rpi_logs['t5_ns'][i] if i < len(rpi_logs['t5_ns']) else "MISSING"
            
            # Obtenemos T1-T4
            # Si llegamos a perder un trap en la red UDP, hay peliogro de que perdamos la correlación (tipico en SNMP)
            t1 = traps_by_type["T1"][i] if i < len(traps_by_type["T1"]) else "MISSING_TRAP"
            t2 = traps_by_type["T2"][i] if i < len(traps_by_type["T2"]) else "MISSING_TRAP"
            t3 = traps_by_type["T3"][i] if i < len(traps_by_type["T3"]) else "MISSING_TRAP"
            t4 = traps_by_type["T4"][i] if i < len(traps_by_type["T4"]) else "MISSING_TRAP"
            
            # Calculamos la latencia total
            delta = "N/A"
            if isinstance(t0, int) and isinstance(t5, int):     # Comprobamos en primer lugar que los logs existan
                delta = round((t5 - t0) / 1_000_000.0, 3) # ns a ms con redondeo

            writer.writerow([i+1, t0, t1, t2, t3, t4, t5, delta])
            
    print(f"BURST REPORT generado: {filename}")
    return filename

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