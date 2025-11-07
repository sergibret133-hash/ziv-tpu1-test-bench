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

# *** HIL CONTROL KEYWORDS ***
def send_hil_command(raspberry_pi_ip: str, command: str, port: int = 65432):
    """
    Se conecta al servidor HIL de la Raspberry Pi y envía un comando.
    Devuelve la respuesta del servidor.
    
    COMANDOS
    ON,<pin_id>          -> Activa el relé (ej: 'ON 1')
    OFF,<pin_id>         -> Desactiva el relé (ej: 'OFF 1')
    PULSE,<pin_id>,<t>   -> Activa el relé, espera 't' segundos, lo desactiva (ej: 'PULSE 1 0.5')
    PULSE_BATCH,<t>,<pin_id1>,<pin_id2>,... -> Activa el relé, espera 't' segundos, lo desactiva (ej: 'PULSE 1 0.5')
    STATE,<pin_id>       -> Devuelve el estado actual del pin de salida físico (1=ON, 0=OFF)
    GET_OUTPUT,<pin_id>  -> Devuelve el estado actual del pin de entrada física (1=ON, 0=OFF)
    RESET                -> Apaga todos los relés.
    PING                 -> Devuelve 'PONG' (para comprobar conexión)
    CONFIG_LOG,<pin_id>  -> Configura el pin para logging de tiempos (T0 o T5)
    START_LOG            -> Inicia el logging de tiempos.
    STOP_LOG             -> Detiene el logging de tiempos.
    GET_LOGS             -> Devuelve los logs en formato JSON.
    """
    
    print(f"HIL CMD: Conectando a {raspberry_pi_ip}:{port}...")
    try:
        # Crea el socket con un timeout de 5s
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect((raspberry_pi_ip, port))
            
            # Enviamos el comando
            s.sendall(command.encode('utf-8'))
            
            # Esperamos la respuesta (con maximo 1024 bytes)
            response = ""
            while True:
                part = s.recv(4096).decode('utf-8')
                response += part
                if '\n' in part or not part:    # Final de respuesta o conexión cerrada -> Salimos del bucle en el que esperamos respuesta
                    break
            
            response = response.strip() # Limpiamos espacios y saltos de línea
            print(f"HIL CMD: Comando '{command}' enviado. Respuesta: {response[:150]}...")  # logeamos solo los primeros 150 caracteres para no saturar
            
            
            # Comprobamos la respuesta, realizando las siguientes verifiaciones
            valid_responses = ["ACK", "PONG", "STATE", "JSON"]
            if not response.startswith(valid_responses):
                raise Exception(f"response no coincide con lo que esperabamos (ACK.., PONG, STATE, JSON.. : {response}")
            
            return response

    except socket.timeout:
        print(f"HIL ERROR: Timeout al conectar en la IP: {raspberry_pi_ip}", file=sys.stderr)
        raise Exception(f"Timeout al conectar en la IP: {raspberry_pi_ip}")
    except ConnectionRefusedError:
        print(f"HIL ERROR: Conexión rechazada.", file=sys.stderr)
        raise Exception(f"Conexión rechazada")
    except Exception as e:
        print(f"HIL ERROR: {e}", file=sys.stderr)
        raise Exception(f"Error al enviar comando HIL: {e}")
    
    
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

# *** KEYWORD DE GENERACIÓN DE INFORME ***
def generate_performance_report(rpi_logs, traps_A_list, traps_B_list):
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