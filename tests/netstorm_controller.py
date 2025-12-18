import time
from vncdotool import api as vnc_api
import threading
from twisted.internet import reactor

NETSTORM_SESSION = None

class NetstormController:
    """ Controlador para el simulador de acciones por VNC del equipo Netstorm (de Albedo) para inyección de ruido."""
    
    def __init__(self, ip, password):
        self.server = f"{ip}::5900"
        
        # Si la pass es None o cadena vacía, se conecta sin pass
        if not password or password == "None" or password == "":
            self.password = None
        else:
            self.password = password
        
        
        self.client = vnc_api.connect(self.server, password=self.password)

        if not reactor.running:
            self._reactor_thread = threading.Thread(
                target=reactor.run,
                kwargs={"installSignalHandlers": False},
                daemon=True
            )
            self._reactor_thread.start()

        time.sleep(0.5)

        self.keepalive()
        
    def keepalive(self):
        """
        Mantiene viva la sesión VNC enviando la tecla shift
        """
        try:
            self.client.keyPress('shift')
            time.sleep(0.05)
        except:
            pass

    
    def disconnect(self):
        """ Desconecta la sesión VNC """
        if self.client:
            print("VNC: Desconectando de Netstorm...")
            try:
                self.client.disconnect()
                
            except Exception as e:
                print(f"VNC: Error al desconectar: {e}")
            self.client = None      # Marcamos la sesión como desconectada
        
    
    def make_click(self, x, y):
        """ Realiza un click en las coordenadas x e y """
        self.client.mouseMove(x, y)
        time.sleep(0.2)
        
        self.client.mousePress(1)
        time.sleep(0.2)

    
    def _send_sequence(self, keys):
        """ Envía una secuencia de teclas al VNC """
        for key in keys:
            self.client.keyPress(key)
            time.sleep(0.5)
    
    def reset_to_home(self):
        self.client.keyPress('home')   # Nos aseguramos de situarnos en la pantalla de inicio
        time.sleep(0.2)
        
        
        for i in range(8):
            self.client.keyPress('left') # Nos movemos al primer icono de la pantalla de Home
            time.sleep(0.1)
            
    def access_to_internal_memory_files(self):
        for i in range(3):
            self.client.keyPress('right')
            time.sleep(0.1)  # Navegamos hasta el icono de Files
        
        self.client.keyPress('enter') # Entramos en Files
        time.sleep(0.2)
        
        for i in range(5):
            self.client.keyPress('esc') # Nos movemos al primer icono de la pantalla de Home
            time.sleep(0.1)

        # Navegamos hasta el subdirectorio de seleccion de perfiles
        self.client.keyPress('enter') # Entrar en Files
        time.sleep(0.2)
        self.client.keyPress('up') # Aseguramos que estamos arriba en Configuration files
        time.sleep(0.2)
        self.client.keyPress('enter') # Entrar en Configuration files
        time.sleep(0.2)
        self.client.keyPress('up') # Aseguramos que estamos arriba en Internal Memory
        time.sleep(0.2)
        self.client.keyPress('enter') # Entrar en Internal Memory
        time.sleep(0.4)
        
        
    def set_numeric_value(self, value):
        """ 
        Maneja el teclado numerico
        Borra el valor actual y escribe el nuevo.
        """
        val_str = str(value)
        print(f"VNC: Escrbiendo el valor numerico pasado como arg: {val_str}")

        # Borramos el valor actual
        # self.client.keyPress('f2') 
        for i in range(15):
            self.client.keyPress('f3') 
            time.sleep(0.05)
        time.sleep(0.2)
    
        # escribimos lo que nos pasan
        for charr in val_str:
            if charr == '.':
                self.client.keyPress('.')
            else:
                self.client.keyPress(charr)
            time.sleep(0.1)
            
        # Confirmamos
        time.sleep(0.2)
        self.client.keyPress('f4')
        time.sleep(0.5)
        
    def set_text_value(self, text):
        """
        Maneja el teclado alfanumérico
        """
        str_text = str(text)
        print(f"VNC: Escribiendo texto: {str_text}")
        
        # Borramos texto actual
        # self.client.keyPress('f2') 
        for i in range(30):
            self.client.keyPress('f3') 
            time.sleep(0.05)
        time.sleep(0.2)
        
        # Escribimos
        for char in str_text:
            # Primero evaluamos si se trata de un caracter especial
            if char == '_':
                self.client.keyPress('_') 
            elif char == '-':
                self.client.keyPress('-')
            elif char == '.':
                self.client.keyPress('.')
            elif char.isupper():
                self.client.keyPress(char)
            else:   # Para letras y nums estándar
                self.client.keyPress(char)
            time.sleep(0.1)
            
        # Confirmamos
        self.client.keyPress('f4')
        time.sleep(0.5)
        
    def load_profile(self, profile_number):
        """ Carga los perfiles 01_CLEAN.cfg o 02_NOISE .cfg en Netstorm via VNC """
        p_num = int(profile_number)
        
        print(f"VNC: Cargando perfil  en Netstorm...")
        
        self.reset_to_home()
    
        self.access_to_internal_memory_files()
        
        # reset arriba
        for i in range(10):
            self.client.keyPress('up')
        
        # Seleccionamos el perfil a cargar
        for a in range (profile_number - 1):
            self.client.keyPress('down')  # Bajamos al perfil 02_NOISE
            time.sleep(0.1)
        
        self.client.keyPress('enter') # Seleccionamos el perfil
        time.sleep(0.5)
        
        # Apretamos Load para cargar el perfil
        # self.client.keyPress('f1')
        self.make_click(130, 268)  # Coordenadas del botón Load
        time.sleep(0.2)
        
        # Confirmamos el Load
        self.client.keyPress('left')
        time.sleep(0.3)
        self.client.keyPress('enter')
        time.sleep(0.5)
        
        self.client.keyPress('home')   # Volvemos a Home
        print(f"VNC: Perfil cargado.")
        
        time.sleep(0.5)
        
    def toggle_injection(self):
        """ Activa o desactiva la inyección de ruido en Netstorm via el atajo que dispone presionando Ctrl + e"""
        print("VNC: Activando inyección de ruido..")
        self.client.keyPress('ctrl-e')
        time.sleep(0.8)
    
    
    def _navigate_and_set(self, value, is_numeric=True):
        """
        Función auxiliar:
        Baja una posicion en el menú
        Si "value" no es IGNORE, entra, escribe y sale
        Si "value" es IGNORE, no hace nada
        """
        self.client.keyPress('down') # Bajamos al siguiente parámetro
        time.sleep(0.2)
        if value != "IGNORE" and value is not None:
            # Solo entramos a editar si el usuario nos lo pide
            self.client.keyPress('enter') 
            time.sleep(0.2)
            
            if is_numeric:
                self.set_numeric_value(value)
            else:
                self.set_text_value(value)
        
    
    # Para acceder a Config Ruido Default
    def test_section_access(self, port, noise_config):
        """ 
        Accede a la configuración de ruido correspondiente al puerto y el tipo de ruido pasado como argumento.
        Tipos de ruido: 
        1. Loss
        2. Delay & Jitter
        3. Bandwidth
        4. Duplication
        5. Bit Errors
        """
    
        self.reset_to_home()
        
        self.client.keyPress('enter') # Entramos en Test
        time.sleep(0.2)
        
        for i in range(6):
            self.client.keyPress('esc') # Nos movemos al primer icono de la pantalla de Home
            time.sleep(0.1)

        # Navegamos hasta el subdirectorio de Configuración Default de Ruido
        self.client.keyPress('enter')   # Entrar en Tests
        time.sleep(0.2)
        
        for i in range(3):
            self.client.keyPress('up')  # Nos movemos al primer elemento del 1er menú de tests
            time.sleep(0.1)
        
        self.client.keyPress('enter')   # Damos clic en action
        time.sleep(0.2)
        
        self.client.keyPress('up')   # Aseguramos que estamos arriba en la Selección de Puertos 
        if port == 'A':
            pass
        elif port == 'B':
            self.client.keyPress('down')  #Bajamos al puerto B
            time.sleep(0.2)
        self.client.keyPress('enter') # Entrar en Puerto A  
        time.sleep(0.2)
        
        for i in range(15):
            self.client.keyPress('up')  # Nos movemos al primer elemento del 3er menú de tests
            time.sleep(0.1)
        # Entramos en Default
        self.client.keyPress('enter')
        
        
        # Accedemos al tipo de configuracion de ruido pasado como argumento
        # Nos aseguramos que estemos arriba del todo
        for i in range(4):
            self.client.keyPress('up')
            time.sleep(0.1)
        # Accedemos al tipo de ruido que queremos configurar
        if noise_config == "Loss":
            pass
        elif noise_config == "Delay & Jitter":
            self.client.keyPress('down')
            
        elif noise_config == "Bandwidth":
            for i in range(2):
                self.client.keyPress('down')
        elif noise_config == "Duplication":
            for i in range(3):
                self.client.keyPress('down')
        elif noise_config == "Bit errors":
            for i in range(4):
                self.client.keyPress('down')
        else:
            print(f"Configuración de ruido {noise_config} pasada como argumento no reconocido. \n Opciones disponibles: Loss, Delay & Jitter, Bandwidth, Duplication, Bit errors")
        self.client.keyPress('enter')
        
    def loss_config(self, loss_mode, loss_probability, burst_length, burst_separation, alternative_loss_prob, mean_length, mean_alternative_length):
        """
        Configuración LOSS basada en tu calibración visual (9 ítems):
        1. Mode
        2. Burst length (ms)  -> Saltamos (asumimos uso de frames)
        3. Burst length (fr)  -> EDITAMOS
        4. Burst Separation (ms) -> Saltamos
        5. Burst Separation (fr) -> EDITAMOS
        6. Loss Probability   -> EDITAMOS
        7. Alternative loss probability -> Saltamos (o configuras si quieres)
        8. Mean Length        -> Saltamos
        9. Mean alternative length -> Saltamos
        """
        if loss_mode == "IGNORE" and (loss_probability != "IGNORE" or burst_length != "IGNORE" or burst_separation != "IGNORE" or alternative_loss_prob != "IGNORE" or mean_length != "IGNORE" or mean_alternative_length != "IGNORE"):
            print("ERROR VNC: No se puede configurar parámetros de Loss sin especificar el Modo (la navegación depende de ello).")
            return
        
        # CONFIGURAMOS MODO
        if loss_mode != "IGNORE":
            print("Mode Seleccionado")
            time.sleep(0.4)
            for i in range(8): 
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
            print("# Reset arriba completado. -> Siguiente: Seleccionamos Mode y nos desplazamos hasta el modo correspondiente")
            time.sleep(0.4)
            self.client.keyPress('enter')   # Seleccionamos Mode
            
            # Definimos cuantas veces hay que bajar para cada modo
            mode_steps = {
                "none": 0,
                "single": 1,
                "timed_burst": 2,
                "frame_burst": 3,
                "timed_periodic_burst": 4,
                "frame_periodic_burst": 5,
                "random": 6,
                "two_state_random": 7
            }    
            
            steps = mode_steps.get(loss_mode.lower(), 0)    #Localizamos el # de pasos que tenemos que hacer para seleccionar el modo 

            for i in range(8): # Reset Arriba
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
                
            print(f"VNC: Se ha seleccionado el modo:'{loss_mode}' -> ({steps} saltos)")
            
            # Realizamos los saltos
            for a in range(steps):
                self.client.keyPress('down')
                time.sleep(0.4)
                
            self.client.keyPress('enter')

            time.sleep(0.5)
            
            # si el usuario selecciona None, salimos de la función ya que no necesitams modificar ningun paranetro mas!
            if loss_mode.lower() == "none":
                print("VNC: Modo Loss desactivado (None). Saliendo de configuración.")
                return

        if loss_mode != "IGNORE":
            if loss_mode == "timed_burst":          
                self._navigate_and_set(burst_length)    # Burst length (fr) -> Bajamos y Editamos
                
            elif loss_mode == "frame_burst":
                self.client.keyPress('down')
                self._navigate_and_set(burst_length)
                
            elif loss_mode == "timed_periodic_burst":
                self._navigate_and_set(burst_length)
                self.client.keyPress('down')
                self._navigate_and_set(burst_separation)
                
            elif loss_mode == "frame_periodic_burst":
                self.client.keyPress('down')
                self._navigate_and_set(burst_length)
                self.client.keyPress('down')
                self._navigate_and_set(burst_separation)
            
            elif loss_mode == "random":
                for i in range(4):
                    self.client.keyPress('down')
                self._navigate_and_set(loss_probability)
            
            elif loss_mode == "two_state_random":
                for i in range(4):
                    self.client.keyPress('down')
                self._navigate_and_set(loss_probability)
                self._navigate_and_set(alternative_loss_prob)
                self._navigate_and_set(mean_length)
                self._navigate_and_set(mean_alternative_length)
            
            else:
                print(f"No se reconoce el tipo de modo {loss_mode}")
                

    def delay_jitter_config(self, delay_mode, fixed_delay, min_delay, max_delay, avg_delay, reordening):
        if delay_mode == "IGNORE" and (fixed_delay != "IGNORE" or min_delay != "IGNORE" or max_delay != "IGNORE" or avg_delay != "IGNORE" or reordening != "IGNORE"):
            print("ERROR VNC: No se puede configurar parámetros de Loss sin especificar el Modo (la navegación depende de ello).")
            return
        
        # CONFIGURAMOS MODO
        if delay_mode != "IGNORE":
            print("Mode Seleccionado")
            time.sleep(0.4)
            for i in range(8): 
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
            print("# Reset arriba completado. -> Siguiente: Seleccionamos Mode y nos desplazamos hasta el modo correspondiente")
            time.sleep(0.4)
            self.client.keyPress('enter')   # Seleccionamos Mode

            mode_steps = {
                "none": 0,
                "deterministic": 1,
                "random_uniform": 2, 
                "random_exponential": 3
            }
            
            steps = mode_steps.get(delay_mode.lower(), 0)
            
            for i in range(8): # Reset Arriba
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
                
            print(f"VNC: Se ha seleccionado el modo:'{delay_mode}' -> ({steps} saltos)")
        
            for a in range(steps):
                self.client.keyPress('down')
                time.sleep(0.4)
                
            self.client.keyPress('enter')
            time.sleep(0.5)
            # Modo seleccionado!
            if delay_mode.lower() == "none":
                print("VNC: Modo jitter desactivado (None). Saliendo.")
                return

        #  RESTO DE PARAMETROS   
        if delay_mode != "IGNORE":
            if delay_mode == "deterministic":          
                self._navigate_and_set(fixed_delay)

            elif delay_mode == "random_uniform":
                self.client.keyPress('down')
                time.sleep(0.2)
                self._navigate_and_set(min_delay)
                self._navigate_and_set(max_delay)
                self.client.keyPress('down')
                time.sleep(0.2)
                # Allow Reordering
                self.client.keyPress('down')
                time.sleep(0.2)
                if reordening != "IGNORE":
                    self.client.keyPress('enter')
                    time.sleep(0.2)
                    self.client.keyPress('up')      # Nos aseguramos que estemos arriba (en "No")
                    time.sleep(0.2)
                    if str(reordening).lower() in ['1', 'yes', 'true']:   # En caso de que queramos activarlo
                        self.client.keyPress('down')
                    self.client.keyPress('enter')
                    time.sleep(0.2)
                
            elif delay_mode == "random_exponential":
                self.client.keyPress('down')
                time.sleep(0.2)
                self._navigate_and_set(min_delay)
                self.client.keyPress('down')
                time.sleep(0.2)
                self._navigate_and_set(avg_delay)
                # Allow Reordering
                self.client.keyPress('down')
                time.sleep(0.2)
                if reordening != "IGNORE":
                    self.client.keyPress('enter')
                    time.sleep(0.2)
                    self.client.keyPress('up')      # Nos aseguramos que estemos arriba (en "No")
                    time.sleep(0.2)
                    if str(reordening).lower() in ['1', 'yes', 'true']:   # En caso de que queramos activarlo
                        self.client.keyPress('down')
                    self.client.keyPress('enter')
                    time.sleep(0.2)
                
            else:
                print(f"No se reconoce el tipo de modo {delay_mode}")
    
                
    def bandwidth_config(self, bandwidth_mode, frame_rate, max_burst_size, bit_rate):
        if bandwidth_mode == "IGNORE" and (frame_rate != "IGNORE" or max_burst_size != "IGNORE" or bit_rate != "IGNORE"):
            print("ERROR VNC: No se puede configurar parámetros de Loss sin especificar el Modo (la navegación depende de ello).")
            return
        
    # CONFIGURAMOS MODO
        if bandwidth_mode != "IGNORE":
            print("Mode Seleccionado")
            time.sleep(0.4)
            for i in range(8): 
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
            print("# Reset arriba completado. -> Siguiente: Seleccionamos Mode y nos desplazamos hasta el modo correspondiente")
            time.sleep(0.4)
            self.client.keyPress('enter')   # Seleccionamos Mode
            
            mode_steps = {
                "none": 0,
                "policing_fr_s": 1,
                "policing_bits_s": 2,
                "shaping_fr_s": 3,
                "shaping_bits_s": 4
            }
            
            steps = mode_steps.get(bandwidth_mode.lower(), 0)
   
            for i in range(8): # Reset Arriba
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
                
            print(f"VNC: Se ha seleccionado el modo:'{bandwidth_mode}' -> ({steps} saltos)")
            
            for a in range(steps):
                self.client.keyPress('down')
                time.sleep(0.4)
                
            self.client.keyPress('enter')
            time.sleep(0.5)
            # Modo seleccionado!
            if bandwidth_mode.lower() == "none":
                print("VNC: Modo Bandwidth desactivado (None). Saliendo.")
                return

        #  RESTO DE PARAMETROS
        if bandwidth_mode != "IGNORE":
            if bandwidth_mode == "policing_fr_s":          
                self._navigate_and_set(frame_rate)
                self._navigate_and_set(max_burst_size)
                
            elif bandwidth_mode == "policing_bits_s":
                self.client.keyPress('down')
                self.client.keyPress('down')
                self._navigate_and_set(bit_rate)
                self._navigate_and_set(max_burst_size)

                
            elif bandwidth_mode == "shaping_fr_s":
                self._navigate_and_set(frame_rate)
                self._navigate_and_set(max_burst_size)
                
        
            elif bandwidth_mode == "shaping_bits_s":
                self.client.keyPress('down')
                self.client.keyPress('down')
                self._navigate_and_set(bit_rate)
                self._navigate_and_set(max_burst_size)

            else:
                print(f"No se reconoce el tipo de modo {bandwidth_mode}")
        
        
        
        
        # Frame Rate
        self._navigate_and_set(frame_rate)
        
        # Max Burst Size Fr
        self._navigate_and_set(max_burst_size)
        
            
    def duplication_config(self, duplication_mode, duplication_probability):
        if duplication_mode == "IGNORE" and (duplication_probability != "IGNORE"):
            print("ERROR VNC: No se puede configurar parámetros de Loss sin especificar el Modo (la navegación depende de ello).")
            return
        
    # CONFIGURAMOS MODO
        if duplication_mode != "IGNORE":
            print("Mode Seleccionado")
            time.sleep(0.4)
            for i in range(8): 
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
            print("# Reset arriba completado. -> Siguiente: Seleccionamos Mode y nos desplazamos hasta el modo correspondiente")
            time.sleep(0.4)
            self.client.keyPress('enter')   # Seleccionamos Mode
            
            mode_steps = {
                "none": 0,
                "single": 1,
                "random": 2,
            }
            
            steps = mode_steps.get(duplication_mode.lower(), 0)
        
            for i in range(8): # Reset Arriba
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
                
            print(f"VNC: Se ha seleccionado el modo:'{duplication_mode}' -> ({steps} saltos)")
            
            # Realizamos los saltos
            for a in range(steps):
                self.client.keyPress('down')
                time.sleep(0.4)
                
            self.client.keyPress('enter')
            time.sleep(0.5)
            # Modo seleccionado!
            if duplication_mode.lower() == "none":
                print("VNC: Modo duplication desactivado (None). Saliendo.")
                return

        #  RESTO DE PARAMETROS   
        # Frame Rate
        if duplication_mode != "IGNORE":
            if duplication_mode == "random":          
                self._navigate_and_set(duplication_probability)
    
    
    def bit_errors_config(self, error_mode, error_probability):
        if error_mode == "IGNORE" and (error_probability != "IGNORE"):
            print("ERROR VNC: No se puede configurar parámetros de Loss sin especificar el Modo (la navegación depende de ello).")
            return
        
    # CONFIGURAMOS MODO
        if error_mode != "IGNORE":
            print("Mode Seleccionado")
            time.sleep(0.4)
            for i in range(8): 
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
            print("# Reset arriba completado. -> Siguiente: Seleccionamos Mode y nos desplazamos hasta el modo correspondiente")
            time.sleep(0.4)
            self.client.keyPress('enter')   # Seleccionamos Mode
            
            mode_steps = {
                "none": 0,
                "single": 1,
                "random": 2,
            }
            
            steps = mode_steps.get(error_mode.lower(), 0)
            
            for i in range(8): # Reset Arriba
                self.client.keyPress('up') # Reset arriba
                time.sleep(0.05)
            print(f"VNC: Se ha seleccionado el modo:'{error_mode}' -> ({steps} saltos)")
            
            # Realizamos los saltos
            for a in range(steps):
                self.client.keyPress('down')
                time.sleep(0.4)
                
            self.client.keyPress('enter')
            time.sleep(0.5)
            # Modo seleccionado!
            if error_mode.lower() == "none":
                print("VNC: Modo bit_errors desactivado (None). Saliendo.")
                return

        #  RESTO DE PARAMETROS   
        # Frame Rate
        if error_mode != "IGNORE":
            if error_mode == "random":     
                self._navigate_and_set(error_probability)
                
    def save_profile(self, profile_name):
        self.reset_to_home()
        self.access_to_internal_memory_files()
        self.client.keyPress('f2')
        self.set_text_value(profile_name)
        print(f"Perfil {profile_name} guardado.")
        self.client.keyPress('home')
        
        
        
_vnc_netstorm = None

# Keywords para Robot

def connect_to_netstorm(netstorm_ip: str, vnc_password: str):
    """ Conecta al Netstorm via VNC """
    global _vnc_netstorm
    if _vnc_netstorm:
        print("VNC: Sesión previa detectada. Cerramos y esperamos..")
        try:
            _vnc_netstorm.disconnect()
        except:
            pass
        time.sleep(2) # Par evitar bloqueo
        _vnc_netstorm = None
    
    _vnc_netstorm = NetstormController(netstorm_ip, vnc_password)

def disconnect_from_netstorm():
    """ Desconecta la sesión VNC del Netstorm """
    global _vnc_netstorm    # Variable global que mantiene la sesión VNC
    if _vnc_netstorm:
        _vnc_netstorm.disconnect()
        _vnc_netstorm = None
        return True

def set_network_profile(profile_name):
    """ Mapea nombres a números de perfil """
    if profile_name == "CLEAN":
        _vnc_netstorm.load_profile(1)
    elif profile_name == "NOISE":
        _vnc_netstorm.load_profile(2)
        
    elif profile_name == "WP3_Jitter":
        _vnc_netstorm.load_profile(3)
    elif profile_name == "WP3_Loss_High":
        _vnc_netstorm.load_profile(4)
    elif profile_name == "LOSS_10":
        _vnc_netstorm.load_profile(5)
    elif profile_name == "LOSS_20":
        _vnc_netstorm.load_profile(6)
    elif profile_name == "LOSS_40":
        _vnc_netstorm.load_profile(7)
    elif profile_name == "LOSS_60":
        _vnc_netstorm.load_profile(8)        
    elif profile_name == "LOSS_80":
        _vnc_netstorm.load_profile(9)            
    elif profile_name == "STORM":
        _vnc_netstorm.load_profile(10)
    # Mapeo de perfiles escenario B, Test Loss Breakpoint Analysis
    # elif
    else:
        print(f"No se reconoce el perfil pasado como argumento: {profile_name}")
        
def toggle_noise():
    """ Inicia la inyección de ruido en Netstorm """
    _vnc_netstorm.toggle_injection()
    
    
# Configuración de Sección Tests
def apply_config_loss(noise_port, loss_mode, loss_probability, burst_length, burst_separation, alternative_loss_prob, mean_length, mean_alternative_length):
    _vnc_netstorm.test_section_access(noise_port, "Loss")
    _vnc_netstorm.loss_config(loss_mode, loss_probability, burst_length, burst_separation, alternative_loss_prob, mean_length, mean_alternative_length)
    _vnc_netstorm.reset_to_home()

    
def apply_config_delay_jitter(noise_port, delay_mode, fixed_delay, min_delay, max_delay, avg_delay, reordening):
    _vnc_netstorm.test_section_access(noise_port, "Delay & Jitter")
    _vnc_netstorm.delay_jitter_config(delay_mode, fixed_delay, min_delay, max_delay, avg_delay, reordening)
    _vnc_netstorm.reset_to_home()

    
def apply_config_bandwidth(noise_port, bandwidth_mode, frame_rate, max_burst_size_fr, bit_rate):
    _vnc_netstorm.test_section_access(noise_port, "Bandwidth")
    _vnc_netstorm.bandwidth_config(bandwidth_mode, frame_rate, max_burst_size_fr, bit_rate)
    _vnc_netstorm.reset_to_home()

    
def apply_config_duplication(noise_port, duplication_mode, duplication_probability):
    _vnc_netstorm.test_section_access(noise_port, "Duplication")
    _vnc_netstorm.duplication_config(duplication_mode, duplication_probability)
    _vnc_netstorm.reset_to_home()

    
def apply_config_corruption(noise_port, error_mode, error_probability):
    _vnc_netstorm.test_section_access(noise_port, "Bit errors")
    _vnc_netstorm.bit_errors_config(error_mode, error_probability)
    _vnc_netstorm.reset_to_home()


def save_config(profile_name):
    _vnc_netstorm.save_profile(profile_name)