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
import sounddevice as sd
import numpy as np
from collections import defaultdict
from datetime import timedelta

try:
    import gpiod
    from gpiod.line import Direction, Value, Bias, Edge
    print("GPIOD VERSION:", gpiod.__version__)
except Exception as e:
    print("ERROR: No se pudo importar 'gpiod'. Instala python3-libgpiod (libgpiod v2).")
    print(f"Detalle import error: {e}")
    sys.exit(1)


# ********************************************************************************************
# GENERADOR DE RUIDO ANALÓGICO INYECTADO (DSP)
# ********************************************************************************************
class WhiteNoiseGenerator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.stream = None
        self.amplitude = 0.0  # Amplitud del ruido
        self.is_running = False
        self.lock = threading.Lock()
        
    def _audio_callback(self, outdata, frames, time_info, status):
        """Genera ruido blanco y lo escribe en el buffer de salida."""
        if status:
            print(f"AUDIO_WARN {status}")

        # Generación matematica de la distrubución normal de ruido blanco
        noise = np.random.normal(0, 1, frames)
        
        # Aplicamos ganancia
        with self.lock:
            current_amplitude = self.amplitude
        
        noise = noise * current_amplitude
        
        # Aseguramos que los datos están en el rango -1.0, 1.0
        noise = np.clip(noise, -1.0, 1.0)
        
        # Volcamos los datos al buffer de salida
        outdata[:, 0] = noise.astype(np.float32)  # Canal mono!
        
    def start(self):
        if not self.is_running:
            try:
                self.stream = sd.OutputStream(
                    channels=1,
                    samplerate=self.fs,
                    callback=self._audio_callback
                )
                self.stream.start()
                self.is_running = True
                print("DSP Generador de ruido blanco iniciado.")
            except Exception as e:
                print(f"ERROR al iniciar el generador de ruido blanco: {e}")
    
    def stop(self):
        if self.is_running:
            self.stream.stop()
            self.stream.close()
            self.is_running = False
            print("DSP Generador de ruido blanco detenido.")
    
    def set_amplitude(self, amplitude):
        level = max(0.0 , min(float(amplitude), 1.0))
        with self.lock:
            self.amplitude = level
        print(f"DSP Amplitud de ruido blanco ajustada a: {level}")
        
noise_generator = WhiteNoiseGenerator()
                
        
        
# *** INICIALIZACION ***
#  *** Variables globales ***
# t0_logs = []  # Lista para almacenar los logs de T0
# t5_logs = []  # Lista para almacenar los logs de T5
# PASAMOS A TRABAJAR CON DICCIONARIOS QUE CONTIENEN LISTAS: { '1': [], '2': []}
t0_logs = defaultdict(list)
t5_logs = defaultdict(list)


logging_active = False  # Indicador de si el logging está activo (para los callbacks)
logging_lock = threading.Lock()     # Lo utilizaremos por seguridad para leer de los diccionarios compartidos

# current_log_channels = []  # Canales que estamos registrando actualmente
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
# Teniendo en cuenta que configuramos los relés como Activos Nivel Bajo para utilizar los optoacopladores que funcionan por activos nivel bajo también EN LA SALIDA DE LOS MISMOS ->
#   - Ponemos el pin GPIO en 1 (3.3V) -> ACTIVA OPTO (PRODUCE '0' EN LA SALIDA DEL OPTO) -> CIERRA el relé (ON)
#   - Ponemos el pin GPIO en 0 (0V) -> DESACTIVA OPTO (PRODUCE '1' EN LA SALIDA DEL OPTO) -> ABRE el relé (OFF)
RELAY_ON_STATE = Value.ACTIVE
RELAY_OFF_STATE = Value.INACTIVE

# Mapeo de pines GPIO
# comando : pin_GPIO 
PIN_MAP = {
    '1': 17,  # Fila 1 (IO17)
    '2': 18,  # Fila 1 (IO18)
    '3': 24,  # Fila 2 (IO24)
    '4': 25,  # Fila 2 (IO25)
    '5': 5,   # Fila 2 (IO5)
    '6': 6,   # Fila 2 (IO6)
}

# Pines de FEEDBACK T0 (Entradas físicas desde optoacoplador en paralelo a la entrada TPU)
T0_PIN_MAP = {
    '1': 23,  # Fila 3 (IO23)
    '2': 22,  # Fila 3 (IO22)
    '3': 12,  # Fila 3 (IO12)
    '4': 20,  # Fila 3 (IO20)
    '5': 19,  # Fila 3 (IO19)
    '6': 16,  # Fila 2 (IO16 - Extremo derecho
}

# Pines de Recepción de Orden Salida T5 (Entradas físicas RPI conectadas a Relés SSR de salida de la IPTU)
T5_PIN_MAP = {
    '1': 4,   # Fila 4 (IO4)
    '2': 27,  # Fila 4 (IO27)
    '3': 21,  # Fila 4 (IO21)
    '4': 13,  # Fila 4 (IO13)
    '5': 26,  # Fila 4 (IO26)
    '6': 2,   # Fila 4 (SDA - GPIO 2) *Ver nota abajo
}



# def t0_callback_handler(channel, timestamp):
#     "Se ejecuta automaticamente al detectar flanco en el pin de feedback T0"
#     if logging_active:
#         t0_logs.append(time.time_ns())
        
# def t5_callback_handler(channel, timestamp):
#     "Se ejecuta automaticamente al detectar flanco en el pin de feedback T5"
#     if logging_active:
#         t5_logs.append(time.time_ns())

# YA NO NECESITAMOS CALLBACKS GLOBALES! -> IMPLEMENTAMOS FUNCIÓN QUE RECIBE EL CANAL
def append_log(channel_id, timestamp, is_t5=False):
    """Agrega el timestamp al diccionario del canal correspondiente de forma segura."""
    with logging_lock:
        if is_t5:
            t5_logs[channel_id].append(timestamp)
        else:
            t0_logs[channel_id].append(timestamp)




# HILO DE SONDEO (para gpiod_v2) ---
def _alert_poll_loop(channel_id, request_obj, is_t5):
    """
    Hilo dedicado a sondear un pin especifico.
    """
    global logging_active
    
    while not logging_active:
        time.sleep(0.01)

    print(f"Hilo Polling iniciado para Canal {channel_id} ({'T5' if is_t5 else 'T0'}). Comenzamos el sondeo :).")
    
    try:
        while logging_active:
            # Esperamos un evento con timeout de 100ms
            if request_obj.wait_edge_events(timeout=timedelta(milliseconds=50)):# Timeout pequeño para leer
                # Leemos los eventos
                events = request_obj.read_edge_events() 
                for event in events:
                    # Pasamos el timestamp (en ns) y el pin_id al callback
                    # callback(channel_id, event.timestamp_ns)    # event.timestamp_ns: no ponemos () al final porque no es un metodo!
                    append_log(channel_id, time.time_ns(), is_t5)   # Utilizamos la nueva función a la que podemos pasar el canal del que queremos hacer log

    except Exception as e:
        if logging_active:
            print(f"ERROR en hilo canal {channel_id}: {e}")
        

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
        print(f"FATAL GPIO ERROR: {e}")
        sys.exit(1)
        
def cleanup_gpio():
    """Limpia y libera los pines GPIO al cerrar el script."""
    # global CHIP, RELAY_REQUESTS, logging_active
    print("\nCerrando servidor y limpiando pines gpio")
    _release_log_pins()
    for req in RELAY_REQUESTS.values(): req.release()
    if CHIP: CHIP.close()
    print("Lineas gpiod liberadas y chip cerrado.")


def _release_log_pins():
    "Detiene los hilos y libera los pines de log T0 & T5"
    global logging_active
    # global T0_REQUESTS, T5_REQUESTS
    # global t0_monitor_threads, t5_monitor_threads
    
    # Detenemos los hilos
    logging_active = False
    print(f"INFO, Deteniendo hilos de log configurados en CONFIG_LOG")
    for thread in t0_monitor_threads + t5_monitor_threads:
        thread.join(timeout=0.2)
        
    # if not T0_REQUESTS and not T5_REQUESTS:
    #     return
    
    print(f"INFo, Lberando pines de log..")
    
    for req in T0_REQUESTS.values():
        req.release()
    for req in T5_REQUESTS.values():
        req.release()

    T0_REQUESTS.clear()
    T5_REQUESTS.clear()
    
    t0_monitor_threads.clear()
    t5_monitor_threads.clear()
    
    # current_log_channels.clear()
    print("INFO, Pines de log liberados")




# *** FUNCIONES DE LOGGING ***
def command_config_log(channels_str, mode="ALL"):
    """Configura los listeners para una lista de canales."""
    _release_log_pins()
    
    t0_logs.clear()
    t5_logs.clear()
    
    channels = channels_str.split(',')
    
    settings_in = gpiod.LineSettings(direction=Direction.INPUT, edge_detection=Edge.FALLING, bias=Bias.PULL_UP)
    
    try:
        for ch in channels:
            ch = ch.strip()
            
            # Inicializamos las variables de los logs para que aparezcan listas vacías en el json final
            t0_logs[ch] = []
            t5_logs[ch] = []


            # Configuramos T0
            if mode in ["ALL", "T0"] and ch in T0_PIN_MAP:
                pin = T0_PIN_MAP[ch]
                req = CHIP.request_lines(consumer=f"T0_{ch}", config={pin: settings_in})
                T0_REQUESTS[ch] = req   # Guardamos el request en una posicion correspondiente al canal que hemos configurado en esta iteracion del for
                
            # Configurar T5
            if mode in ["ALL", "T5"] and ch in T5_PIN_MAP:
                pin = T5_PIN_MAP[ch]
                req = CHIP.request_lines(consumer=f"T5_{ch}", config={pin: settings_in})    # Guardamos el request en una posicion correspondiente al canal que hemos configurado en esta iteracion del for
                T5_REQUESTS[ch] = req
                
        return f"ACK, Configurado log para canales: {channels}"
    
    except Exception as e:
        return f"ERROR config log: {e}"


def command_start_log():
    global logging_active

    logging_active = True
    
    # Lanzamos hilos de T0
    for ch, req in T0_REQUESTS.items():
        thread = threading.Thread(target=_alert_poll_loop, args=(ch, req, False), daemon=True)
        t0_monitor_threads.append(thread)
        thread.start()

    # Lanzamos hilos T5
    for ch, req in T5_REQUESTS.items():
        thread = threading.Thread(target=_alert_poll_loop, args=(ch, req, True), daemon=True)
        t5_monitor_threads.append(thread)
        thread.start()
        
    return "ACK, Logging Iniciado"


def command_get_logs():
    """
    Devuelve un JSON estructurado por canal.
    Estructura: 
    {
        "1": {"t0": [..], "t5": [..]},
        "2": {"t0": [..], "t5": [..]}
    }
    """
    # Identificar todos los canales que tienen datos
    all_channels = t0_logs.keys() | t5_logs.keys()
    
    response_data = {}
    for ch in all_channels:
        response_data[ch] = {
            "t0_ns": t0_logs[ch],
            "t5_ns": t5_logs[ch]
        }
    
    return "JSON," + json.dumps(response_data)

# *** FUNCIONES DE BURST Y DIPARO ***
def set_pin_state(pin_id, state):
    if pin_id in RELAY_REQUESTS:
        val = RELAY_ON_STATE if state else RELAY_OFF_STATE
        RELAY_REQUESTS[pin_id].set_value(PIN_MAP[pin_id], val)
        pin_states[pin_id] = state
        return "ACK"
    else:
        return "ERROR,Pin ID no válido."

# FUNCIONES DE PULSO
def pulse_pin(pin_id, duration):
    """Genera un pulso en un pin GPIO específico durante una duración dada."""
    if pin_id in PIN_MAP:
        if set_pin_state(pin_id, 1) != "ACK": return "ERROR_ON"
        time.sleep(duration)         
        if set_pin_state(pin_id, 0) != "ACK": return "ERROR_OFF"
        return "ACK"
    else:
        return "ERROR,Pin ID no válido."
    
def execute_burst(pin_id, num_pulses, duration, delay):
    """Genera una ráfaga de pulsos en un pin GPIO específico."""
    # if pin_id not in PIN_MAP:
    #     return "ERROR, Pin ID no válido."
    # print(f"INICIO RÁFAGA: {num_pulses} pulsos de {duration}s en pin {pin_id}")    
    
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
            
        # ******************************************************************
        # COMANDOS DE RUIDO ANALOGICCO DSP
        elif command.startswith("NOISE_START,"):
            try:
                parts = command.split(',')
                level = float(parts[1])
                noise_generator.set_amplitude(level)
                noise_generator.start()
                return f"ACK, Ruido blanco iniciado al nivel {level}"
            except Exception as e:
                return f"ERROR, No se pudo iniciar el ruido blanco: {e}"
            
        elif command == "NOISE_STOP":
            noise_generator.stop()
            return "ACK, Ruido blanco detenido"
    
        # ******************************************************************
        elif command.startswith("CONFIG_LOG,"):
            try:
                time.sleep(0.1)
                parts = command.split(',')
                
                if len(parts) > 2:
                    if parts[1] in ["T0", "T5", "ALL"]:
                        log_mode = parts[1]
                        channel_ids = parts[2:]
                    else:   # Si nos pasan directamente los canales, asumimos ALL
                        log_mode = "ALL"
                        channel_ids = parts[1:]

                    return command_config_log(",".join(channel_ids), log_mode)
                else:
                    return "ERROR, Comando CONFIG_LOG inválido. Formato correcto: CONFIG_LOG,<ch_id>,<ch_id>.. o CONFIG_LOG,<mode>,<ch_id>,<ch_id>.."
                
            except Exception as e:
                print(f"Error en CONFIG_LOG: {e}")
                return f"ERROR, No se pudo configurar el canal para logging: {e}"
            
        elif command == "START_LOG":    
            # Iniciamos registro de logs
            return command_start_log()
        
        
        elif command == "STOP_LOG":
            if not logging_active:
                 return "ERROR, No hay logging activo."
            _release_log_pins()
            return "ACK, Logging detenido."
            
        elif command == "GET_LOGS":
            return command_get_logs()
            
        elif command.startswith("ON,"):
            parts = command.split(',')
            pin_id = parts[1]
            set_pin_state(pin_id, 1)
            return f"ACK, ON {pin_id}"

        elif command.startswith("OFF,"):
            parts = command.split(',')
            pin_id = parts[1]
            set_pin_state(pin_id, 0)
            return f"ACK, OFF {pin_id}"
        
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
            
            
            
        elif command.startswith("GET_INPUT,"):
            parts = command.split(',')
            if len(parts) == 2:
                pin_id = parts[1]
                if pin_id not in T0_PIN_MAP:
                    return f"ERROR, Pin ID '{pin_id}' no existe en T0_PIN_MAP."
                
                pin_bcm = T0_PIN_MAP[pin_id]

                if pin_id in T0_REQUESTS:
                    try:
                        req = T0_REQUESTS[pin_id]
                        state = req.get_value(pin_bcm)
                        
                        # Lógica de retorno (Invertida porque Pull-Up + Active Low)
                        if state == Value.INACTIVE: 
                            return "STATE,HIGH"
                        else:
                            return "STATE,LOW"
                    except Exception as e:
                            return f"ERROR, Fallo leyendo pin ocupado: {e}"
                    
                    
                else:
                    # Describimos la nueva confiuración del pin que vamos a reclamar
                    # hacemos lectura puntual
                    settings_read = gpiod.LineSettings(
                    direction=Direction.INPUT,
                    bias=Bias.PULL_UP
                    )
                    
                    req = None
                    try:    # Reclamamos el pin
                        req = CHIP.request_lines(
                            consumer="HIL_GET_INPUT",
                            config={pin_bcm: settings_read}
                        )                    
                        state = req.get_value(pin_bcm)
                        # Como los reles de la generacion de salidas de la IPTU funciona ACTIVO-ALTO 
                        if state == Value.INACTIVE:  
                            return "STATE,HIGH"
                        else:
                            return "STATE,LOW"
                    
                    except Exception as e:
                        return f"ERROR, Excepción en GET_INPUT: {e}"
                    
                    finally:
                        if req:
                            req.release()  # Liberamos la linea
            else:
                return "ERROR,Comando GET_INPUT inválido. Formato correcto: GET_INPUT,<pin_id>"
            
            
        elif command.startswith("GET_OUTPUT,"):
            parts = command.split(',')
            if len(parts) == 2:
                pin_id = parts[1]
                if pin_id not in T5_PIN_MAP:
                    return f"ERROR, Pin ID '{pin_id}' no existe en T5_PIN_MAP."
                
                pin_bcm = T5_PIN_MAP[pin_id]

                if pin_id in T5_REQUESTS:
                    try:
                        req = T5_REQUESTS[pin_id]
                        state = req.get_value(pin_bcm)
                        
                        # Lógica de retorno (Invertida porque Pull-Up + Active Low)
                        if state == Value.INACTIVE: 
                            return "STATE,HIGH"
                        else:
                            return "STATE,LOW"
                    except Exception as e:
                            return f"ERROR, Fallo leyendo pin ocupado: {e}"
                    
                    
                else:
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
                    
                    except Exception as e:
                        return f"ERROR, Excepción en GET_OUTPUT: {e}"
                    
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
            
            print(f"[{addr[0]}] Comando: {command}")
            
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
        print(f"[-] Conexión cerrada con {addr[0]}")
        
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
        server_socket.listen(5)
        print(f"\nServidor HIL iniciado. Escuchando en {HOST}:{PORT}...")
        print("Esperando conexiones..")

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