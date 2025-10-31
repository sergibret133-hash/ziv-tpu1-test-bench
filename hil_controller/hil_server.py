"""
Fecha: 31/10/2025
Servidor HIL para tests del equipo de teleprotecciones TPU-1.
TFG: Design and Development of an Automated Test Bench for Robustness Testing of Teleprotection Equipment

Este .py se ejecuta en la Raspberry Pi 4b.
Funciones:
1. Inicializa los pines GPIO que controlan un módulo de 8 relés de estado solido. Éstos, daran paso a pulsos que el modulo IPTU procesara y hará envío de inputs a traves de la interfaz de linea asignada. 
2. Abre un servidor de Sockets TCP.
3. Espera comandos desde un cliente, que en nuestro caso será nuestra GUI.
4. Convierte esos comandos en acciones físicas (activar/desactivar relés).

COMANDOS
ON <pin_id>        -> Activa el relé (ej: 'ON 1')
OFF <pin_id>       -> Desactiva el relé (ej: 'OFF 1')
PULSE <pin_id> <t> -> Activa el relé, espera 't' segundos, lo desactiva (ej: 'PULSE 1 0.5')
STATE <pin_id>     -> Devuelve el estado actual del pin (1=ON, 0=OFF)
RESET              -> Apaga todos los relés.
PING               -> Devuelve 'PONG' (para comprobar conexión)
"""

import socket
import sys
import time
import RPi.GPIO as GPIO

# *** INICIALIZACION ***
HOST = '0.0.0.0'    # Para escuchar en todas las tarjetas de red disponibles
PORT = 65432  

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
    '1': 17,  # Pin 11
    '2': 27,  # Pin 13
    '3': 22,  # Pin 15
    '4': 23,  # Pin 16
    '5': 24,   # Pin 18
    '6': 25,  # Pin 22
    '7': 5,   # Pin 29
    '8': 6,   # Pin 31
}

# Guarda el estado de todos los relés. Becesario para el comando 'STATE'
pin_current_state = {}  # Asignaremos el estado del pin ('1' o '0') en la posición corresponidente AL NUMERO DE PIN!

# *** FUNCIONES DE GPIO ***

def setup_gpio():
    """Configura los pines GPIO al iniciar el script."""
    print("Configurando pines GPIO...")
    GPIO.setmode(GPIO.BCM)  # numeración de pines BCM
    GPIO.setwarnings(False) # Desactivar advertencias de "pin en uso"
    
    for pin in PIN_MAP.values():    # Iteramos sobre todos los pines
        GPIO.setup(pin, GPIO.OUT)       # Configuramos como pin de SALIDA
        GPIO.output(pin, RELAY_OFF_STATE) # Aseguramos que todos los relés empiecen APAGADOS
        pin_current_state[pin] = 0      # 0 = OFF   Asignamos apagado a la lista del estado de los pines
        
    print(f"GPIO listo. {len(PIN_MAP)} relés configurados en modo Activo-Bajo.")
    print(f"Estado inicial: OFF (GPIO.{'HIGH' if RELAY_OFF_STATE == GPIO.HIGH else 'LOW'})")

def cleanup_gpio():
    """Limpia y resetea los pines GPIO al cerrar el script."""
    print("\nCerrando servidor y limpiando pines GPIO")
    GPIO.cleanup()

# *** FUNCIONES SERVIDOR ***

def parse_and_execute(command_str):
    """
    Toma el comando de texto, lo interpreta y ejecuta la
    acción GPIO correspondiente. Devuelve una respuesta.
    """
    command_str = command_str.strip().upper()
    parts = command_str.split() # Separamos por el espacio
    response = f"El comando '{command_str} no se reconoce :('" 

    if not parts:
        return "ERROR: Comando vacío."

    cmd = parts[0]
    
    try:
        if cmd == 'PING':
            response = "PONG"

        elif cmd == 'ON' and len(parts) == 2:
            pin_id = parts[1]
            pin_gpio = PIN_MAP[pin_id]  # Nos quedamos con el num pin BCM mapeado 
            GPIO.output(pin_gpio, RELAY_ON_STATE)   # Activamos el pin correspondiente
            pin_current_state[pin_gpio] = 1 # Guardamos como '1' = ON en la lista de estados de los pines
            response = f"ACK: Relé {pin_id} (GPIO {pin_gpio}) -> ON"

        elif cmd == 'OFF' and len(parts) == 2:
            pin_id = parts[1]
            pin_gpio = PIN_MAP[pin_id]
            GPIO.output(pin_gpio, RELAY_OFF_STATE)
            pin_current_state[pin_gpio] = 0 # 0 = OFF
            response = f"ACK: Relé {pin_id} (GPIO {pin_gpio}) -> OFF"

        elif cmd == 'PULSE' and len(parts) == 3:
            pin_id = parts[1]
            pin_gpio = PIN_MAP[pin_id]
            
            duration_s = float(parts[2])

            # Ejecutar pulso
            GPIO.output(pin_gpio, RELAY_ON_STATE)
            pin_current_state[pin_gpio] = 1
            time.sleep(duration_s)
            GPIO.output(pin_gpio, RELAY_OFF_STATE)
            pin_current_state[pin_gpio] = 0
            
            response = f"ACK: Relé {pin_id} (GPIO {pin_gpio}) -> PULSE {duration_s}s"
        
        elif cmd == 'STATE' and len(parts) == 2:
            pin_id = parts[1]
            pin_gpio = PIN_MAP[pin_id]
            state = pin_current_state.get(pin_gpio, 0) # Obtenemos el valor correspondiente a la posición del vector = num PIN GPIO. state = 0 por defecto en caso de no encontrarlo
            response = f"STATE: {state}"
            
        elif cmd == 'RESET':
            for pin in PIN_MAP.values():
                GPIO.output(pin, RELAY_OFF_STATE)
                pin_current_state[pin] = 0
            response = f"ACK: Todos ({len(PIN_MAP)}) los relés -> OFF"
    
    except KeyError:
        response = f"ERROR: Pin ID '{parts[1]}' no existe en PIN_MAP."
    except ValueError:
        response = f"ERROR: Duración de pulso inválida. Debe ser un número (ej: 0.5)."
    except Exception as e:
        response = f"ERROR: Excepción inesperada: {str(e)}"

    print(f"  -> {response}")
    return response


# *** BUCLE DEL SERVIDOR ***

def main():
    setup_gpio()

    # Creamos el socket
    # AF_INET= IPv4, SOCK_STREAM= TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Permite re-ejecutar el servidor inmediatamente después de cerrarlo

    try:
        # Vinculamos el socket al HOST y PUERTO
        server_socket.bind((HOST, PORT))
        
        # Ponemos el socket a escuchar
        server_socket.listen()
        print(f"\nServidor HIL iniciado. Escuchando en {HOST}:{PORT}...")
        print("Esperando conexiones del cliente GUI)")

        while True:
            # Aceptamos una nueva conexión
            conn, addr = server_socket.accept()     # NOs quedamos aqui hasta que el cliente se conecte
            
            #  Con 'with conn:' si el cliente se desconecta o apoarece un error -> la conexión se cierre sola

            with conn:
                print(f"\nCliente conectado desde: {addr[0]}:{addr[1]}")
                
                while True:     # Bucle de recepción de comandos del cliente
                    data = conn.recv(1024)      # Decidimos recibir hasta 1024 bytes de datos
                    
                    if not data:
                        # Si 'data' está vacío, el cliente ha cerrado la conexión
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