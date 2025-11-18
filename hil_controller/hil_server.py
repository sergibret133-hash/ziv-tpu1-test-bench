"""
Fecha: 31/10/2025 (Refactorizado 11/11/2025 para lgpio en Debian 13)
Servidor HIL para tests del equipo de teleprotecciones TPU-1.
TFG: Design and Development of an Automated Test Bench for Robustness Testing of Teleprotection Equipment

Librería GPIO: lgpio (para compatibilidad con Debian 13 / libgpiod)

Este .py se ejecuta en la Raspberry Pi 4b (Debian 13).
Funciones:
1. Inicializa los pines GPIO que controlan un módulo de 8 relés.
2. Inicializa los pines GPIO para leer las SALIDAS de orden (T0/T5) mediante callbacks.
3. Abre un servidor de Sockets TCP.
4. Espera comandos desde un cliente (GUI de Robot Framework).
5. Convierte esos comandos en acciones físicas (activar/desactivar relés o leer entradas).

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

import socket
import sys
import time
import threading
import json
import os

try:
    import gpiod
    from gpiod.line import Direction, Value, Bias, Edge
    print("GPIOD VERSION:", gpiod.__version__)
except Exception as e:
    print("ERROR: No se pudo importar 'gpiod'. Instala python3-libgpiod (libgpiod v2).")
    print(f"Detalle import error: {e}")
    sys.exit(1)

from datetime import timedelta

# *** INICIALIZACION ***
#  *** Variables globales ***
t0_logs = []  # Lista para almacenar los logs de T0
t5_logs = []  # Lista para almacenar los logs de T5
logging_active = False  # Indicador de si el logging está activo (para los callbacks)

current_log_channels = []  # Canales que estamos registrando actualmente
current_log_mode = "ALL"
# Hilos para los eventos (lo necesita lgpio)

t0_monitor_threads = []
t5_monitor_threads = []

# Handle global para el chip GPIO
GPIO_CHIP_NAME = "/dev/gpiochip0"
CHIP = None
# Para lgpio
# GPIO_CHIP = 0
# CHIP_HANDLE = None

RELAY_REQUESTS = {}      # Diccionario para {pin_id: request_obj}
T0_REQUESTS = {}                 
T5_REQUESTS = {}                 

# Guarda el estado de todos los relés. Becesario para el comando 'STATE'
pin_states = {}


# Lógica de los Relés
# -----------------------------------
# Teniendo en cuenta que los relés son Activos a Nivvel bajo ->
#   - Poner el pin GPIO en 0 (0V) -> CIERRA el relé (ON)
#   - Poner el pin GPIO en 1 (3.3V) -> ABRE el relé (OFF)
RELAY_ON_STATE = Value.INACTIVE
RELAY_OFF_STATE = Value.ACTIVE

# Mapeo de pines GPIO
# comando : pin_GPIO 
PIN_MAP = {
    '1': 17,  # Pin 11 Físico
    '2': 27,  # Pin 13 Físico
    '3': 22,  # Pin 15 Físico
    '4': 5,  # Pin 29 Físico
    '5': 6,   # Pin 31 Físico
    '6': 13,  # Pin 33 Físico
}

# Pines de FEEDBACK T0 (Entradas físicas desde optoacoplador en paralelo a la entrada TPU)
T0_PIN_MAP = {
    '1': 4,   # Físico 7
    '2': 18,  # Físico 12
    '3': 23,  # Físico 16
    '4': 24,  # Físico 18
    '5': 25,  # Físico 22
    '6': 8,   # Físico 24 (SPI)
}

# Pines de Recepción de Orden Salida T5 (Entradas físicas RPI conectadas a Relés SSR de salida de la IPTU)
T5_PIN_MAP = {
    '1': 26,  # Físico 37
    '2': 19,   # Físico 35
    '3': 16,  # Físico 36
    '4': 20,  # Físico 38
    '5': 21,  # Físico 40
    '6': 12,  # Físico 32
}



def t0_callback_handler(channel, timestamp):
    "Se ejecuta automáticamente al detectar flanco en el pin de Feedback T0"
    if logging_active:
        t0_logs.append(timestamp)
        
def t5_callback_handler(channel, timestamp):
    "Se ejecuta automáticamente al detectar flanco en el pin de Feedback T5"
    if logging_active:
        t5_logs.append(timestamp)

# HILO DE SONDEO (para gpiod_v2) ---
def _alert_poll_loop(channel_id, request_obj, callback):
    """
    Hilo dedicado a sondear un 'request' gpiod v2 para eventos de flanco.
    """
    global logging_active
    # Tratamos de obtener el pin para el log
    try:
        # Obtenemos el pin BCM desde el objeto request
        pin_bcm = request_obj.offsets[0]
        print(f"Evento Hilo del canal {channel_id} y pin GPIO{pin_bcm} Iniciado. Esperando logging_active para seguir")
    except Exception:
        pin_bcm = "N/A"
        print(f"Evento Hilo del canal {channel_id} Iniciado pero sin haber recuperado pin_bcm del objeto request. Esperando logging_active para seguir")

    while not logging_active:
        time.sleep(0.05)

    print(f"Evento Hilo del canal {channel_id} del pin GPIO{pin_bcm} Logging activado. Comenzamos el sondeo :).")
    try:
        while logging_active:
            # Esperamos un evento con timeout de 100ms
            if request_obj.wait_edge_events(timeout=timedelta(milliseconds=100)):
                # Leemos los eventos
                events = request_obj.read_edge_events() # Timeout pequeño para leer
                for event in events:
                    # Pasamos el timestamp (en ns) y el pin_id al callback
                    callback(channel_id, event.timestamp_ns)    # event.timestamp_ns: no ponemos () al final porque no es un metodo!
    
    except Exception as e:
        if logging_active:
            print(f"ERROR en Hilo de Evento en canal {channel_id}: {e}")
    finally:
        print(f"Evento Hilo {channel_id}. Hilo detenido.")
        

# *** FUNCIONES DE GPIO ***
def setup_gpio():
    """Configura gpiod. Reclama los pines de salida."""
    global CHIP, RELAY_REQUESTS, pin_states
    print("Configurando pines GPIO...")
    
    try:
        # Abrimos el chip GPIO
        CHIP = gpiod.Chip(GPIO_CHIP_NAME)
        # Preparamos la config base para todos los relés
        # Configuramos los pines de salida y su estado por defecto con la configuración anterior (output y valor de RELAY_OFF_STATE)
        for pin_id, pin_bcm in PIN_MAP.items():    # Iteramos sobre todos los pines de salida. 
            # Creamos la configuración para ESTE pin específico
            # Direction.OUTPUT -> Salida
            # output_value=RELAY_OFF_STATE -> Empieza en HIGH (Relé apagado)
            settings = gpiod.LineSettings(
                direction=Direction.OUTPUT, 
                output_value=RELAY_OFF_STATE
            )
            
            # Solicitamos CADA línea individualmente
            req = CHIP.request_lines(
                consumer=f"HIL_Relay_{pin_id}",
                config={pin_bcm: settings}
            )
            RELAY_REQUESTS[pin_id] = req # Guardamos el objeto request
            pin_states[pin_id] = 0       # Guardamos el estado lógico
            
        print(f"Salidas físicas activación inputs GPIO listas. {len(RELAY_REQUESTS)} relés configurados.")
        
    except Exception as e:
        print(f"ERROR FATAL: No se pudo inicializar gpiod.")
        print(f"Detalle: {e}")
        if CHIP:
            CHIP.close()    
        sys.exit(1)
        
def cleanup_gpio():
    """Limpia y libera los pines GPIO al cerrar el script."""
    global CHIP, RELAY_REQUESTS, logging_active
    print("\nCerrando servidor y limpiando pines gpio")
    
    _release_log_pins()
    
    if CHIP:
        # Liberamos todos los pines guardados
        for req in RELAY_REQUESTS.values():
            req.release()
            
        CHIP.close()
        CHIP = None
        print("Lineas gpiod liberadas y chip cerrado.")


def set_pin_state(pin_id, state):
    """Establece el estado de un pin GPIO específico de los de salida (RELÉS)"""
    if pin_id in RELAY_REQUESTS:
        req = RELAY_REQUESTS[pin_id]
        pin_bcm = PIN_MAP[pin_id]
        
        if state == 1:
            req.set_value(pin_bcm, RELAY_ON_STATE)
            pin_states[pin_id] = 1
            print(f"Pin {pin_id} GPIO {pin_bcm} activado (ON)")
        else:
            req.set_value(pin_bcm, RELAY_OFF_STATE)
            pin_states[pin_id] = 0
            print(f"Pin {pin_id} GPIO {pin_bcm} desactivado (OFF)")
        return "ACK"    # Una vez asignado el pin GPIO de salidam confirmamos con ACK
    else:
        return "ERROR: Pin ID no válido."


def _release_log_pins():
    "Detiene los hilos y libera los pines de log T0 & T5"
    global logging_active, T0_REQUESTS, T5_REQUESTS
    global t0_monitor_threads, t5_monitor_threads
    
    # Detenemos los hilos
    if logging_active:
        logging_active = False
        print(f"INFO, Deteniendo hilos de log configurados en CONFIG_LOG")
        for thread in t0_monitor_threads + t5_monitor_threads:
            thread.join(timeout=0.2)
            
    if not T0_REQUESTS and not T5_REQUESTS:
        return
    
    print(f"INFo, Lberando pines de log..")
    
    for req in T0_REQUESTS.values():
        req.release()
    for req in T5_REQUESTS.values():
        req.release()

    T0_REQUESTS.clear()
    T5_REQUESTS.clear()
    
    t0_monitor_threads.clear()
    t5_monitor_threads.clear()
    
    current_log_channels.clear()
    print("INFO, Pines de log liberados")
    
# *** FUNCIONES DE PULSO ***
def pulse_pin(pin_id, duration):
    """Genera un pulso en un pin GPIO específico durante una duración dada."""
    if pin_id in PIN_MAP:
        response_on = set_pin_state(pin_id, 1)  # Activamos el pin y comprobamos respuesta
        if response_on != "ACK":
            return response_on      # Si falla la activación de la salida, devolvemos el codigo de error que nos retorna set_pin_state
        
        time.sleep(duration)         

        response_off = set_pin_state(pin_id, 0)  # Desactivamos el pin y comprobamos respuesta
        if response_off != "ACK":
            return response_off     # Si falla la activación de la salida, devolvemos el codigo de error que nos retorna set_pin_state
        return "ACK"
    else:
        return "ERROR,Pin ID no válido."
    
def execute_burst(pin_id, num_pulses, duration, delay):
    """Genera una ráfaga de pulsos en un pin GPIO específico."""
    if pin_id not in PIN_MAP:
        return "ERROR, Pin ID no válido."
    print(f"INICIO RÁFAGA: {num_pulses} pulsos de {duration}s en pin {pin_id}")    
    
    for i in range(num_pulses):
        # Pulso ON
        set_pin_state(pin_id, 1)
        time.sleep(duration)
        
        # Pulso OFF
        set_pin_state(pin_id, 0)
        
        if i < num_pulses - 1:  # mientras que no sea el último pulso
            time.sleep(delay)
            
    print(f"FIN RÁFAGA en pin {pin_id}")
    return "ACK, RÁFAGA COMPLETADA"

# *** FUNCIONES SERVIDOR ***
           
def parse_and_execute(command):
    """ Toma el comando de texto, lo interpreta y ejecuta la acción GPIO correspondiente """
    global CHIP, logging_active
    global current_log_channels, current_log_mode
    global T0_REQUESTS, T5_REQUESTS
    global t0_monitor_threads, t5_monitor_threads
    
    command = command.strip()
    
    try:
        if command == 'PING':
            response = "PONG"

        elif command.startswith("CONFIG_LOG,"):
            try:
                _release_log_pins()
                
                time.sleep(0.1)
                
                parts = command.split(',')
                
                # DETERMINAMOS EL MODO en el que funcionará nuestro sistema y los canales de log
                log_mode = "ALL"
                if parts[1] in ["T0", "T5", "All"]:
                    log_mode = parts[1]
                    channel_ids = parts[2:]
                    print(f"Modo log detectado a: {log_mode}")
                else:
                    channel_ids = parts[1:]     # Si no nos pasaran el tipo de modo de log, asumimos que nos pasan los canales directamente para hacer un log completo (es por eso que hemos declarado log_mode = "ALL")
                
                current_log_mode = log_mode
                
                # print(f"abans clear") 
                # current_log_channels.clear()
                # print(f"abans for")
                
                
                # Config de T0: Rising -Edge, PULL-DOWN
                settings_t0 = gpiod.LineSettings(
                direction=Direction.INPUT,
                edge_detection=Edge.RISING,
                bias=Bias.PULL_DOWN
                )
                
                
                # Config de T5: FALLING-Edge, PULL-UP
                settings_t5 = gpiod.LineSettings(   
                direction=Direction.INPUT,
                edge_detection=Edge.FALLING,
                bias=Bias.PULL_UP
                )
                
                current_log_channels.clear()
                
                # Reclamamos los elementos gpiod en función del modo que hayamos escogido funcionar nuestro sistema (current_log_mode: ALL, T0 o T5):
                for channel_id in channel_ids:
                    channel_id = channel_id.strip()
                    if channel_id not in T0_PIN_MAP or channel_id not in T5_PIN_MAP:
                        return f"ERROR, Canal '{channel_id}' no valido"
                
                    # Reclamamos los pines para alertas de flanco de '0' a '1' condicionalmente en funcion del tipo de log pasado
                    if current_log_mode == "ALL" or current_log_mode == "T0":
                        pin_bcm = T0_PIN_MAP[channel_id]
                        req = CHIP.request_lines(
                            consumer=f"HIL_T0_{channel_id}",
                            config={pin_bcm: settings_t0}
                        )                        
                        T0_REQUESTS[channel_id] = req   # Guardamos el request del canal que estammos iterando en la lista de request de T0
                        print(f"Canal {channel_id}: T0 (GPIO {pin_bcm}) reclamado.")
                        
                    if current_log_mode == "ALL" or current_log_mode == "T5":
                        pin_bcm = T5_PIN_MAP[channel_id]
                        req = CHIP.request_lines(
                            consumer=f"HIL_T5_{channel_id}",
                            config={pin_bcm: settings_t5}
                        )                        
                        T5_REQUESTS[channel_id] = req   # Guardamos el request del canal que estammos iterando en la lista de request de T5
                        print(f"Canal {channel_id}: T5 (GPIO {pin_bcm}) reclamado.")
                        
                    current_log_channels.append(channel_id)     # current_log_channel nos servirá para saber en el momento que queramos iniciar el log, SI ANTES HA SIDO CONFIGURADO CON CONFIG_LOG!
  
                return f"ACK, Canales '{','.join(current_log_channels)}' configurados para modo de logging {current_log_mode}"
            
            except Exception as e:
                print(f"Error en CONFIG_LOG: {e}")
                return f"ERROR, No se pudo configurar el canal para logging: {e}"
            
        elif command == "START_LOG":    
            # Iniciamos registro de logs
            if not current_log_channels:
                return "ERROR, No se han configurado canales. HAY QUE HACERLO ANTES CON EL COMANDO 'CONFIG_LOG,<ch_id>,<ch_id>..' !"
            
            t0_logs.clear()     # Limpiamos logs anteriores
            t5_logs.clear()    # Limpiamos logs anteriores
            # t0_monitor_threads.clear()
            # t5_monitor_threads.clear()  
            
            logging_active = True   # Activamso el flag conforme el log se ha iniciado
            
            # Iniciamos los hilos de T0 (si no hay, no iteraremos ninguno)
            for channel_id, req_obj in T0_REQUESTS.items():
                thread = threading.Thread(target=_alert_poll_loop, args=(channel_id, req_obj, t0_callback_handler), daemon=True)
                t0_monitor_threads.append(thread)
                thread.start()
            
            # Iniciamos los hilos de T5 (si no hay, no iteraremos ninguno)
            for channel_id, req_obj in T5_REQUESTS.items():
                thread = threading.Thread(target=_alert_poll_loop, args=(channel_id, req_obj, t5_callback_handler), daemon=True)
                t5_monitor_threads.append(thread)
                thread.start()                
                                
            return f"ACK, Logging iniciado para {len(current_log_channels)} canales"
        
        elif command == "STOP_LOG":
            if not logging_active:
                 return "ERROR, No hay logging activo."
            _release_log_pins()
            return f"ACK, Logging detenido. Registros T0: {len(t0_logs)}, Registros T5: {len(t5_logs)}"
            
        elif command == "GET_LOGS":
            # Devolvemos los logs en formato JSON
            logs_data = {
                "channels": ",".join(current_log_channels),
                "t0_ns": t0_logs,
                "t5_ns": t5_logs
            }
            # Para que el host interprete que le ha llegado los logs, los enviamos con prefijo JSON,
            return "JSON," + json.dumps(logs_data)
            
        elif command.startswith("ON,"):
            pin_id = command.split(',')[1]
            return set_pin_state(pin_id, 1)

        elif command.startswith("OFF,"):
            pin_id = command.split(',')[1]
            return set_pin_state(pin_id, 0)

        elif command.startswith("PULSE,"):
            parts = command.split(',')
            if len(parts) == 3:
                pin_id = parts[1]
                duration_s = float(parts[2])
                return pulse_pin(pin_id, duration_s)
            else:
                return "ERROR, Comando PULSE inválido. Formato correcto: PULSE,<pin_id>,<duration_s>"

        elif command.startswith("PULSE_BATCH,"):
            parts = command.split(',')
            if len(parts) >= 3:
                duration_s = float(parts[1])
                pin_ids = parts[2:]

                # Iniciaremos cada pulso en hilo separado para cada pin para que sean SIMULTANEOS
                threads = []
                for pin_id in pin_ids:
                    if pin_id in PIN_MAP:
                        thread = threading.Thread(target=pulse_pin, args=(pin_id, duration_s))
                        threads.append(thread)
                        thread.start()
                    else:
                        print(f"WARNING, Pin ID '{pin_id}' no existe en PIN_MAP. Ignorando.")
                
                # Esperamos a que todos los hilos terminen
                for thread in threads:
                    thread.join()
                
                return "ACK,PULSE_BATCH COMPLETED"
            else:
                return "ERROR, comando PULSE_BATCH inválido. Formato correcto: PULSE_BATCH,<duration_s>,<pin_id1>,<pin_id2>,..."
            
        elif command.startswith("BURST,"):
            try:
                parts = command.split(',')
                pin_id = parts[1]
                num_pulses = int(parts[2])
                duration_s = float(parts[3])
                delay = float(parts[4])
                return execute_burst(pin_id, num_pulses, duration_s, delay)
            
            except (IndexError, ValueError):
                return "ERROR,Comando BURST inválido. Formato correcto: BURST,<pin_id>,<num_pulses>,<duration_s>,<delay>"

        elif command.startswith("BURST_BATCH,"):
            try:
                parts = command.split(',')
                num_pulses = int(parts[1])
                duration_s = float(parts[2])
                delay = float(parts[3])
                pin_ids = parts[4:]
                
                if not pin_ids:
                    return "ERROR, BURST_BATCH necesita al menos un pin_id"
                
                threads = []
                
                for pin_id in pin_ids:
                    if pin_id in PIN_MAP:
                        thread = threading.Thread(target=execute_burst, args=(pin_id, num_pulses, duration_s, delay))
                        threads.append(thread)
                        thread.start()
                    else:
                        print(f"WARNING, pin_id '{pin_id}' no se encuentra en PIN_MAP")
                
                # Esperamos a que los hilos de las rafagas finalicen..
                for thread in threads:
                    thread.join()
                
                return "ACK, BURST_BARCH se ha realizado con exito! :)"

            except (IndexError, ValueError):
                return "ERROR, Comando BURST_BATCH invalido. El formato debe ser: BURST_BATCH,<num_pulses>,<duration_s>,<delay>,<pin1>,<pin2>,..."
            
        elif command.startswith("GET_OUTPUT,"):
            parts = command.split(',')
            if len(parts) == 2:
                pin_id = parts[1]
                if pin_id not in T5_PIN_MAP:
                    return f"ERROR, Pin ID '{pin_id}' no existe en T5_PIN_MAP."
                
                pin_bcm = T5_PIN_MAP[pin_id]

                # Describimos la nueva confiuración del pin que vamos a reclamar
                settings_read = gpiod.LineSettings(
                direction=Direction.INPUT,
                bias=Bias.PULL_UP
                )
                
                req = None
                try:    # Reclamamos el pin
                    req = CHIP.request_lines(
                        consumer="HIL_GET_OUTPUT",
                        config={pin_bcm: settings_read}
                    )                    
                    state = req.get_value(pin_bcm)
                    # Como los reles de la generacion de salidas de la IPTU funciona ACTIVO-ALTO 
                    if state == Value.INACTIVE:  
                        return "STATE,HIGH"
                    else:
                        return "STATE,LOW"
                finally:
                    if req:
                        req.release()  # Liberamos la linea
            else:
                return "ERROR,Comando GET_OUTPUT inválido. Formato correcto: GET_OUTPUT,<pin_id>"

        elif command.startswith("STATE,"):
            pin_id = command.split(',')[1]
            if pin_id in pin_states:
                state = pin_states[pin_id]
                return f"STATE,{state}"
            else:
                return f"ERROR,Pin ID '{pin_id}' no existe en pin_states."

            
            
        elif command == 'RESET':
            for pin_id in PIN_MAP.keys():
                set_pin_state(pin_id, 0)
                pin_states[pin_id] = 0
            return f"ACK,({len(PIN_MAP)}) relés -> OFF"
        else:
            return "ERROR,Comando no reconocido."

    except Exception as e:
        print(f"Error procesando comando '{command}': {e}")
        return f"ERROR,{str(e)}"

# *** BUCLE DEL SERVIDOR ***
def handle_client(conn, addr):
    """Maneja la comunicación con un cliente conectado."""
    try:
        print(f"\nCliente conectado desde: {addr[0]}:{addr[1]}")
        
        while True:     # Bucle de recepción de comandos del cliente
            data = conn.recv(1024)      # Decidimos recibir hasta 1024 bytes de datos
            
            if not data:
                # Si data está vacío -> el cliente ha cerrado la conexión
                print(f"Cliente {addr[0]} desconectado.")
                break
            
            # Decodificamos los bytes a string
            command = data.decode('utf-8').strip()
            if not command:
                continue # Ignorar envíos vacíos
            
            print(f"Comando recibido: '{command}'")
            
            # Procesamos el comando y obtenemos respuesta
            response = parse_and_execute(command)

            # Enviar respuesta de vuelta al cliente
            conn.sendall(response.encode('utf-8') + b'\n')
            
    except ConnectionResetError:
        print(f"Cliente {addr[0]} cerró la conexión.")
    except Exception as e:
        print(f"Error con el cliente {addr[0]}: {e}")
    finally:
        conn.close()

def main():
    HOST = '0.0.0.0'    # Para escuchar en todas las tarjetas de red disponibles
    PORT = 65432   
    server_socket = None
    
    try:
        setup_gpio()    # Inicializa lgpio y CHIP_HANDLE
        
        # Creamos el socket
        # AF_INET= IPv4, SOCK_STREAM= TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Permite volver a ejecutar el servidor después de cerrarlo
        
        # Vinculamos el socket al HOST y PUERTO
        server_socket.bind((HOST, PORT))
        
        # Ponemos el socket a escuchar
        server_socket.listen()
        print(f"\nServidor HIL iniciado. Escuchando en {HOST}:{PORT}...")
        print("Esperando conexiones del cliente GUI")

        while True:
            # Aceptamos una nueva conexión
            conn, addr = server_socket.accept()     # NOs quedamos aqui hasta que el cliente se conecte
            
            # Manejamos al cliente en un hilo separado
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True  # Hilo demonio para que se cierre al cerrar el programa principal
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nCerrando servidor.")
    except Exception as e:
        print(f"\nERROR EN EL SERVIDOR :( : {e}")
    finally:
        # Haya error o hayamos salido del servidor, limpiamos todo, cerrando el servidor y hacinedo limpieza de los pines GPIO
        if server_socket:
            server_socket.close()
        cleanup_gpio()  # Cerramos el HANDLE lgpio
        print("Servidor detenido.")

if __name__ == "__main__":
    main()