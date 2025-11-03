from selenium.webdriver import ChromeOptions
import socket
import sys


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
    ON <pin_id>        -> Activa el relé (ej: 'ON 1')
    OFF <pin_id>       -> Desactiva el relé (ej: 'OFF 1')
    PULSE <pin_id> <t> -> Activa el relé, espera 't' segundos, lo desactiva (ej: 'PULSE 1 0.5')
    PULSE_BATCH <t> <pin_id1> <pin_id2> ... -> Activa el relé, espera 't' segundos, lo desactiva (ej: 'PULSE 1 0.5')
    STATE <pin_id>     -> Devuelve el estado actual del pin (1=ON, 0=OFF)
    RESET              -> Apaga todos los relés.
    PING               -> Devuelve 'PONG' (para comprobar conexión)
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
            response = s.recv(1024).decode('utf-8').strip()
            
            print(f"HIL CMD: Comando '{command}' enviado. Respuesta: {response}")
            
            # Comprueba la respuesta
            if not response.startswith("ACK") and not response.startswith("PONG") and not response.startswith("STATE"):
                raise Exception(f"response no coincide con lo que esperabamos (ACK.., PONG o STATE.. : {response}")
            
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