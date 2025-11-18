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
import lgpio
import threading
import json
import os

# *** INICIALIZACION ***
#  *** Variables globales ***
t0_logs = []  # Lista para almacenar los logs de T0
t5_logs = []  # Lista para almacenar los logs de T5
logging_active = False  # Indicador de si el logging está activo (para los callbacks)
current_log_channel = None  # Canal que estamos registrando actualmente

# Hilos para los eventos (lo necesita lgpio)
t0_monitor_thread = None
t5_monitor_thread = None

# Handle global para el chip GPIO
GPIO_CHIP = 0
CHIP_HANDLE = None

# Lógica de los Relés
# -----------------------------------
# Teniendo en cuenta que los relés son Activos a Nivvel bajo ->
#   - Poner el pin GPIO en 0 (0V) -> CIERRA el relé (ON)
#   - Poner el pin GPIO en 1 (3.3V) -> ABRE el relé (OFF)
RELAY_ON_STATE = 0  # Equivalente a GPIO.LOW
RELAY_OFF_STATE = 1 # Equivalente a GPIO.HIGH

# Mapeo de pines GPIO
# comando : pin_GPIO 
PIN_MAP = {
    '1': 17,  # Pin 11 Físico
    # '2': 27,  # Pin 13 Físico
    # '3': 22,  # Pin 15 Físico
    # '4': 5,  # Pin 16 Físico
    # '5': 6,   # Pin 18 Físico
    # '6': 13,  # Pin 22 Físico
    # '7': 19,   # Pin 29 Físico
    # '8': 26,   # Pin 31 Físico
}

# 2. Pines de FEEDBACK T0 (Entradas físicas desde optoacoplador en paralelo a la entrada TPU)
T0_PIN_MAP = {
    # '1': 3,   # Físico 5
    # '2': 7,   # Físico 26
    # '3': 8,   # Físico 24
    # '4': 9,   # Físico 21
    # '5': 10,  # Físico 19
    # '6': 11,  # Físico 23
    '1': 27,  # Físico 13
    # '8': 15,  # Físico 10 (Nos aseguramos que el serial esté desactivado)
}


T5_PIN_MAP = {
    '1': 23,
    # '2': 23,
    # '3': 24,
    # '4': 25,
    # '5': 12,
    # '6': 16,
    # '7': 20,
    # '8': 21,
}

# Guarda el estado de todos los relés. Becesario para el comando 'STATE'
pin_states = {pin_id: 0 for pin_id in PIN_MAP.keys()}

def t0_callback_handler(channel):
    "Se ejecuta automáticamente al detectar flanco en el pin de Feedback T0"
    if logging_active:
        t0_logs.append(time.monotonic_ns())
        
def t5_callback_handler(channel):
    "Se ejecuta automáticamente al detectar flanco en el pin de Feedback T5"
    if logging_active:
        t5_logs.append(time.monotonic_ns())

# HILO DE SONDEO (para lgpio) ---
def _alert_poll_loop(pin, callback):
    """
    Hilo dedicado a sondear un pin para eventos de flanco. Cada 100ms. lgpio no crea hilos de callback automáticamente como RPi.GPIO.
    """
    global logging_active, CHIP_HANDLE
    print(f"[Evento Hilo-{pin}] Iniciado. Esperando 'logging_active'...")
    
    while not logging_active:
        if CHIP_HANDLE is None: # SI el servidor se cerrara el handle no sería valido
            print(f"[Evento Hilo-{pin}] Handle de chip no válido. Abortando.")
            return
        time.sleep(0.1) #100ms de polling

    # Una vez salimos del bucle y se solicita hacer logging (activando logging_active)
    print(f"[Evento Hilo-{pin}] Logging activado. Comenzando sondeo en GPIO {pin}.")
    try:
        while logging_active:
            # Esperamos un evento con un timeout de 100ms, ya que sino saturaríamos mucho
            n, data = lgpio.alert_read_multiple(CHIP_HANDLE, pin, 100, 0.1)
            if n > 0:
                # n es el numero de eventos recibidos
                for i in range(n):
                    callback(pin) # Si recibimos algun evento, iteramos sobre cada uno de estos y se lo pasamos al callback. RECORDEMOS QUE EL CALLBACK UNICAMENTE AÑADE EL TIMESTAMP A LA LISTA DE LOGS t0_logs Y t5_logs!
    except Exception as e:
        if logging_active: # mponemos esta condicion para que no nos aparezca el error de excepción cuando cerremos
            print(f"ERROR en Hilo de Evento (GPIO {pin}): {e}")
    finally:
        print(f"[Evento Hilo-{pin}] Hilo detenido.")

# *** FUNCIONES DE GPIO ***
def setup_gpio():
    """Configura los pines GPIO al iniciar el script."""
    global CHIP_HANDLE
    print("Configurando pines GPIO...")
    
    try:
        # Abrimos el chip GPIO
        CHIP_HANDLE = lgpio.gpiochip_open(GPIO_CHIP)
        
        # GPIO.setmode(GPIO.BCM)  # numeración de pines BCM
        
        # Limpieza previa
        all_pins = set(list(PIN_MAP.values()) + list(T0_PIN_MAP.values()) + list(T5_PIN_MAP.values()))  # Se combinan todos los valores de todos los mapas y con set se acaban juntando todas las listas y se eliminan aquellos valores que se encuentren duplicados.
        for pin in all_pins:
            try:
                lgpio.gpio_free(CHIP_HANDLE, pin)
            except lgpio.error:
                pass # Lo que esperaríamos -> Que no esté en uso..
        
        # Configuramos los pines de salida y su estado por defecto
        for pin in PIN_MAP.values():    # Iteramos sobre todos los pines de salida
            lgpio.gpio_claim_output(CHIP_HANDLE, pin)
            lgpio.gpio_write(CHIP_HANDLE, pin, RELAY_OFF_STATE) # Aseguramos que todos los relés empiecen APAGADOS

        
        print(f"Salidas físicas activación inputs GPIO listas. {len(PIN_MAP)} relés configurados en modo Activo-Bajo.")
        print(f"Estado inicial salidas físicas activación inputs: OFF (GPIO.{'HIGH' if RELAY_OFF_STATE == 1 else 'LOW'})")


        # Configuramos los pines de entrada T0 y T5
        
        for pin in T0_PIN_MAP.values():    # Iteramos sobre todos los pines
            lgpio.gpio_claim_input(CHIP_HANDLE, pin, lgpio.SET_PULL_DOWN)       # Configuramos como pin de ENTRADA con resistencia PULL-DOWN y haya voltaje cuando se active el relé de la IPTU. El modo PULL-DOWN lo configuraremos propiamente en el codigo para la condicion de recibir el comando CONFIG_LOG


        for pin in T5_PIN_MAP.values():
            lgpio.gpio_claim_input(CHIP_HANDLE, pin, lgpio.SET_PULL_DOWN)  # Configuramos como pin de ENTRADA con resistencia PULL-DOWN y haya voltaje cuando se active el relé de la IPTU. El modo PULL-DOWN lo configuraremos propiamente en el codigo para la condicion de recibir el comando CONFIG_LOG
        
        print(f"Entradas físicas T0 y T5 de lectura outputs-IPTU listas. {len(T5_PIN_MAP) + len(T5_PIN_MAP)} entradas configuradas.")
    
    except Exception as e:
        print(f"ERROR FATAL: No se pudo inicializar lgpio.")
        print(f"Detalle: {e}")
        sys.exit(1)
        
def cleanup_gpio():
    """Limpia y resetea los pines GPIO al cerrar el script."""
    global CHIP_HANDLE, logging_active
    print("\nCerrando servidor y limpiando pines GPIO")
    
    logging_active = False # Señal para que los hilos de sondeo terminen
    time.sleep(0.2) # Pequeña espera para que los hilos terminen
    
    if CHIP_HANDLE is not None:     # MIentras haya CHIP_HANDLE y el servidor no se haya cerrado ya de forma inesperada..
        # Liberamos todos los pines asignados en los mapeos
        all_pins = set(list(PIN_MAP.values()) + list(T0_PIN_MAP.values()) + list(T5_PIN_MAP.values()))      # Al usar set() juntamos todos los valores de las listas y eliminamos los que estén duplicados
        for pin in all_pins:
            try:
                lgpio.gpio_free(CHIP_HANDLE, pin)   # Liberamos cada pin
            except lgpio.error:
                pass # No se había usado, por lo que esta libre 
                
        # Cerramos el handle del chip
        lgpio.gpiochip_close(CHIP_HANDLE)
        CHIP_HANDLE = None
        print("Lgpio liberados.")


def set_pin_state(pin_id, state):
    """Establece el estado de un pin GPIO específico de los de salida (RELÉS)"""
    global CHIP_HANDLE
    if pin_id in PIN_MAP:
        pin_gpio = PIN_MAP[pin_id]
        if state == 1:
            lgpio.gpio_write(CHIP_HANDLE, pin_gpio, RELAY_ON_STATE)
            pin_states[pin_id] = 1
            print(f"Pin {pin_id} (GPIO {pin_gpio}) activado (ON)")
        else:
            lgpio.gpio_write(CHIP_HANDLE, pin_gpio, RELAY_OFF_STATE)
            pin_states[pin_id] = 0
            print(f"Pin {pin_id} (GPIO {pin_gpio}) desactivado (OFF)")
        return "ACK"    # Una vez asignado el pin GPIO de salidam confirmamos con ACK
    else:
        return "ERROR: Pin ID no válido."


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
    global CHIP_HANDLE, current_log_channel, logging_active
    global t0_monitor_thread, t5_monitor_thread
    
    command = command.strip()
    
    try:
        if command == 'PING':
            response = "PONG"

        elif command.startswith("CONFIG_LOG,"):
            try:
                parts = command.split(',')
                channel_id = parts[1].strip()
                if channel_id not in T0_PIN_MAP or channel_id not in T5_PIN_MAP:
                    return f"ERROR, Canal '{channel_id}' no valido"
                

                current_log_channel = channel_id    # current_log_channel nos servirá para saber en el momento que queramos iniciar el log, SI ANTES HA SIDO CONFIGURADO CON CONFIG_LOG!
                
                # Obtenemos los pines físicos BCM correspondientes a cada canal.
                t0_pin = T0_PIN_MAP[channel_id]
                t5_pin = T5_PIN_MAP[channel_id]
                
                # Liberamos por si estuvieran en modo "input" simple
                lgpio.gpio_free(CHIP_HANDLE, t0_pin)
                lgpio.gpio_free(CHIP_HANDLE, t5_pin)
                
                time.sleep(0.2)
                
                # Reclamamos los pines para alertas de flanco de '0' a '1'
                lgpio.gpio_claim_alert(CHIP_HANDLE, t0_pin, lgpio.RISING_EDGE, lgpio.SET_PULL_DOWN)
                lgpio.gpio_claim_alert(CHIP_HANDLE, t5_pin, lgpio.RISING_EDGE, lgpio.SET_PULL_DOWN) 

                return f"ACK, Canal '{channel_id}' configurado para logging. t0_pin={t0_pin}, t5_pin={t5_pin}"
            
            except Exception as e:
                return f"ERROR, No se pudo configurar el canal para logging: {e}"
            
        elif command == "START_LOG":    
            # Iniciamos registro de logs
            if not current_log_channel:
                return "ERROR, No se ha configurado canal. HAY QUE HACERLO ANTES CON EL COMANDO 'CONFIG_LOG,<ch_id>' !"
            
            t0_logs.clear()     # Limpiamos logs anteriores
            t5_logs.clear()    # Limpiamos logs anteriores
            
            # Asignamos los dos pines fisicos mapeandolos
            t0_pin = T0_PIN_MAP[current_log_channel]
            t5_pin = T5_PIN_MAP[current_log_channel]
            
            logging_active = True   # Activamso el flag conforme el log se ha iniciado
            
            # Creamos e iniciamos los hilos de sondeo. Recordemos que _alert_poll_loop en cuanto detecte que logging_active=True -> Dejará de estar en modo polling (entrará en un nuevo while que llama a callback que añade el timestamp PERO SIN ESPERAR LOS 100ms en cada iteración)
            t0_monitor_thread = threading.Thread(target=_alert_poll_loop, args=(t0_pin, t0_callback_handler), daemon=True)
            t5_monitor_thread = threading.Thread(target=_alert_poll_loop, args=(t5_pin, t5_callback_handler), daemon=True)
            t0_monitor_thread.start()
            t5_monitor_thread.start()
            
            return "ACK, Logging iniciado. "
        
        elif command == "STOP_LOG":
            if not current_log_channel:
                 return "ERROR, No hay un log activo que detener."
             
            logging_active = False
            # Esperamos a que los hilos creados para el monitoreo hayan terminado
            if t0_monitor_thread:
                t0_monitor_thread.join(timeout=0.5)
            if t5_monitor_thread:
                t5_monitor_thread.join(timeout=0.5)
            # *********************************************************************************
            # Para poder liberar los pines tenemos que mapear y quedarnos con el pin fisico antes!
            t0_pin = T0_PIN_MAP[current_log_channel]
            t5_pin = T5_PIN_MAP[current_log_channel]   
            # *********************************************************************************
            # Liberamos los pines
            lgpio.gpio_free(CHIP_HANDLE, t0_pin)
            lgpio.gpio_free(CHIP_HANDLE, t5_pin)
            
            # Para dejar listos los pines a futuro los volvemos a configurar como entradas simples
            lgpio.gpio_claim_input(CHIP_HANDLE, t0_pin, lgpio.SET_PULL_DOWN)
            lgpio.gpio_claim_input(CHIP_HANDLE, t5_pin, lgpio.SET_PULL_DOWN)
            return f"ACK, Logging detenido. Registros T0: {len(t0_logs)}, Registros T5: {len(t5_logs)}"
            
        elif command == "GET_LOGS":
            # Devolvemos los logs en formato JSON
            logs_data = {
                "channel": current_log_channel,
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


        elif command.startswith("GET_OUTPUT,"):
            parts = command.split(',')
            if len(parts) == 2:
                pin_id = parts[1]
                if pin_id not in T5_PIN_MAP:
                    return f"ERROR, Pin ID '{pin_id}' no existe en T5_PIN_MAP."
                pin_gpio = T5_PIN_MAP[pin_id]
                
                state= lgpio.gpio_read(CHIP_HANDLE, pin_gpio)   # Adquirimos el estado del pin de entrada fisico (que proviene de la generación del OUTPUT de la IPTU)
                # Como los reles de la generacion de salidas de la IPTU funciona ACTIVO-ALTO 
                if state == 1:  
                    return "STATE,HIGH"
                else:
                    return "STATE,LOW"
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