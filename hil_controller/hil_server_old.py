"""
Fecha: 31/10/2025
Servidor HIL para tests del equipo de teleprotecciones TPU-1.
TFG: Design and Development of an Automated Test Bench for Robustness Testing of Teleprotection Equipment

Este .py se ejecuta en la Raspberry Pi 4b.
Funciones:
1. Inicializa los pines GPIO que controlan un módulo de 8 relés de estado solido. Éstos, daran paso a pulsos que el modulo IPTU procesara y hará envío de inputs a traves de la interfaz de linea asignada. 
2. Inicializa los pines GPIO para leer las SALIDAS de orden de la IPTU.
3. Abre un servidor de Sockets TCP.
4. Espera comandos desde un cliente, que en nuestro caso será nuestra GUI.
5. Convierte esos comandos en acciones físicas (activar/desactivar relés o leer entradas).

COMANDOS
ON,<pin_id>        -> Activa el relé (ej: 'ON 1')
OFF,<pin_id>       -> Desactiva el relé (ej: 'OFF 1')
PULSE,<pin_id>,<t> -> Activa el relé, espera 't' segundos, lo desactiva (ej: 'PULSE 1 0.5')
PULSE_BATCH,<t>,<pin_id1>,<pin_id2>,... -> Activa el relé, espera 't' segundos, lo desactiva (ej: 'PULSE 1 0.5')
STATE,<pin_id>     -> Devuelve el estado actual del pin de salida físico (1=ON, 0=OFF)
GET_OUTPUT,<pin_id>  -> Devuelve el estado actual del pin de entrada física (1=ON, 0=OFF)
RESET              -> Apaga todos los relés.
PING               -> Devuelve 'PONG' (para comprobar conexión)
"""

import socket
import sys
import time
import RPi.GPIO as GPIO
import threading
import json

# *** INICIALIZACION ***
#  *** Variables globales ***
t0_logs = []  # Lista para almacenar los logs de T0
t5_logs = []  # Lista para almacenar los logs de T5
logging_active = False  # Indicador de si el logging está activo (para los callbacks)
current_log_channel = None  # Canal que estamos registrando actualmente

# Lógica de los Relés
# -----------------------------------
# Teniendo en cuenta que los relés son Activos a Nivvel bajo ->
#   - Poner el pin GPIO en LOW (0V) -> CIERRA el relé (ON)
#   - Poner el pin GPIO en HIGH (3.3V) -> ABRE el relé (OFF)
RELAY_ON_STATE = GPIO.LOW
RELAY_OFF_STATE = GPIO.HIGH



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
    '1': 27,  # Físico 8 (Nos aseguramos que el serial esté desactivado)
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

# *** FUNCIONES DE GPIO ***
def setup_gpio():
    """Configura los pines GPIO al iniciar el script."""
    print("Configurando pines GPIO...")
    GPIO.setmode(GPIO.BCM)  # numeración de pines BCM
    
    try:
        GPIO.cleanup()
    except:
        pass
    
    GPIO.setwarnings(False) # Desactivar advertencias de "pin en uso"
    
    for pin in PIN_MAP.values():    # Iteramos sobre todos los pines
        GPIO.setup(pin, GPIO.OUT)       # Configuramos como pin de SALIDA
        GPIO.output(pin, RELAY_OFF_STATE) # Aseguramos que todos los relés empiecen APAGADOS
        
    print(f"Salidas físicas activación inputs GPIO listas. {len(PIN_MAP)} relés configurados en modo Activo-Bajo.")
    print(f"Estado inicial salidas físicas activación inputs: OFF (GPIO.{'HIGH' if RELAY_OFF_STATE == GPIO.HIGH else 'LOW'})")

    for pin in T0_PIN_MAP.values():    # Iteramos sobre todos los pines
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)       # Configuramos como pin de ENTRADA con resistencia PULL-DOWN y haya voltaje cuando se active el relé de la IPTU.
        
    print(f"Entradas físicas lectura outputs GPIO listas. {len(T0_PIN_MAP)} entradas configuradas con PULL-DOWN.")


    for pin in T5_PIN_MAP.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Configuramos como pin de ENTRADA con resistencia PULL-DOWN y haya voltaje cuando se active el relé de la IPTU.
    
    print(f"Entradas físicas lectura outputs GPIO listas. {len(T5_PIN_MAP)} entradas configuradas con PULL-DOWN.")
    

def cleanup_gpio():
    """Limpia y resetea los pines GPIO al cerrar el script."""
    print("\nCerrando servidor y limpiando pines GPIO")
    GPIO.cleanup()

def set_pin_state(pin_id, state):
    """Establece el estado de un pin GPIO específico. Esta función ya realiza el mapeo del pin_id al pin GPIO físico."""
    
    if pin_id in PIN_MAP:
        pin_gpio = PIN_MAP[pin_id]
        if state == 1:
            GPIO.output(pin_gpio, RELAY_ON_STATE)
            pin_states[pin_id] = 1
            print(f"Pin {pin_id} (GPIO {pin_gpio}) activado (ON)")
        else:
            GPIO.output(pin_gpio, RELAY_OFF_STATE)
            pin_states[pin_id] = 0
            print(f"Pin {pin_id} (GPIO {pin_gpio}) desactivado (OFF)")
        return "ACK"
    else:
        return "ERROR: Pin ID no válido."

def pulse_pin(pin_id, duration):
    """Genera un pulso en un pin GPIO específico durante una duración dada."""
    if pin_id in PIN_MAP:
        response_on = set_pin_state(pin_id, 1)  # Activamos el pin y comprobamos respuesta
        if response_on != "ACK":
            return response_on
        
        time.sleep(duration)         

        response_off = set_pin_state(pin_id, 0)  # Desactivamos el pin y comprobamos respuesta
        if response_off != "ACK":
            return response_off
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
# def _execute_pulse_batch(gpios, duration_s):
#     """Función para ser ejecutada en un hilo separado para el pulso."""
#     try:
#         # Encendemos todos los pines
#         print(f"BATCH: ON (Pines: {gpios})")
#         for pin in gpios:
#             GPIO.output(pin, RELAY_ON_STATE)
#             pin_states[pin] = 1
            
#         # Esperamos la duración del pulso que nos pasan por el argumento
#         time.sleep(duration_s)
        
#         # Apagamos todos los pines
#         print(f"BATCH: OFF (Pines: {gpios})")
#         for pin in gpios:
#             GPIO.output(pin, RELAY_OFF_STATE)
#             pin_states[pin] = 0
            
#     except Exception as e:
#         print(f"ERROR en hilo BATCH: {e}")
        
def parse_and_execute(command):
    """
    Toma el comando de texto, lo interpreta y ejecuta la acción GPIO correspondiente. Devuelve una respuesta.
    """
    command = command.strip()
    
    try:
        if command == 'PING':
            response = "PONG"

        elif command.startswith("CONFIG_LOG,"):
            try:
                parts = command.split(',')
                channel_id = parts[1].strip()
                if channel_id not in T0_PIN_MAP:
                    return f"ERROR, Canal '{channel_id}' no valido"
                
                global current_log_channel
                current_log_channel = channel_id
                
                # Obtenemos los pines físicos BCM correspondientes a cada canal.
                t0_pin = T0_PIN_MAP[channel_id]
                t5_pin = T5_PIN_MAP[channel_id]
                
                # Limpieza de logs anteriores por si acaso
                try:
                    GPIO.remove_event_detect(t0_pin)
                except RuntimeError:
                    pass
                try:
                    GPIO.remove_event_detect(t5_pin)
                except RuntimeError:
                    pass
                time.sleep(0.2)
                
                # Reconfiguramos los pines de entrada antes de añadir la deteccion
                GPIO.setup(t0_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.setup(t5_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                
                # Deteccion de flancos (de LOW a HIGH) en los pines de feedback T0 y T5
                GPIO.add_event_detect(t0_pin, GPIO.RISING, callback=t0_callback_handler)
                GPIO.add_event_detect(t5_pin, GPIO.RISING, callback=t5_callback_handler)

                return f"ACK, Canal '{channel_id}' configurado para logging. t0_pin={t0_pin}, t5_pin={t5_pin}"
            
            except Exception as e:
                return f"ERROR, No se pudo configurar el canal para logging: {e}"
            
        elif command == "START_LOG":    
            # Iniciamos registro de logs
            global logging_active
            t0_logs.clear()     # Limpiamos logs anteriores
            t5_logs.clear()    # Limpiamos logs anteriores
            logging_active = True
            return "ACK, Logging iniciado. "
        
        elif command == "STOP_LOG":
            logging_active = False
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
                return "ERROR,PULSE_BATCH inválido. Formato correcto: PULSE_BATCH,<duration_s>,<pin_id1>,<pin_id2>,..."
            
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
                state = GPIO.input(pin_gpio)
                if state == GPIO.HIGH:
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
            response = "ERROR,Comando no reconocido."
            return response

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
    
    try:
        setup_gpio()
        
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
        server_socket.close()
        cleanup_gpio()
        print("Servidor detenido.")

if __name__ == "__main__":
    main()