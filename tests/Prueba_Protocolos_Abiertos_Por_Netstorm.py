import socket
import subprocess

TARGET_IP = "10.212.43.85"  # IP DEL NETSTORM
def check_port(ip, port, service_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip, port))
    status = "ABIERTO (Posible API/CLI)" if result == 0 else "CERRADO"
    print(f"[{service_name}] Puerto {port}: {status}")
    sock.close()
    return result == 0

print(f"Escaneando Albedo Netstorm en {TARGET_IP}")

# Verificaciones:
check_port(TARGET_IP, 22, "SSH")
check_port(TARGET_IP, 23, "Telnet")


check_port(TARGET_IP, 80, "HTTP")
check_port(TARGET_IP, 443, "HTTPS")
check_port(TARGET_IP, 8080, "HTTP Alternativo")


check_port(TARGET_IP, 5900, "VNC")

# Verificar SNMP
# SNMP usa UDP puerto 161
# Intentamos ver si responde a ping
response = subprocess.run(["ping", "-c", "1", TARGET_IP], stdout=subprocess.DEVNULL)
if response.returncode == 0:
    print("El equipo responde a PING")
else:
    print("El equipo NO responde a PING")