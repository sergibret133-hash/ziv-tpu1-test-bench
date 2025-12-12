import time
from vncdotool import api as vnc_api


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
    
    
    def load_profile(self, profile_number):
        """ Carga los perfiles 01_CLEAN.cfg o 02_NOISE .cfg en Netstorm via VNC """
        p_num = int(profile_number)
        
        if p_num == 1:
            filename = "01_CLEAN"
        elif p_num == 2:
            filename = "02_NOISE"
        elif p_num == 3:
            filename = "03_STORM"
        # Archivos .cfg para escenario B, Test Loss Breakpoint Analysis
        # elif p_num == 4:
        #     filename = ""
        # elif p_num == 5:
        #     filename = ""
        # elif p_num == 6:
        #     filename = ""
        # elif p_num == 7:
        #     filename = ""
            
        else:
            filename = ""    
            
        filename = "01_CLEAN" if p_num == 1 else "02_NOISE"
        print(f"VNC: Cargando perfil {filename}.cfg en Netstorm...")
        
        self.client.keyPress('home')   # Nos aseguramos de situarnos en la pantalla de inicio
        time.sleep(0.2)
        
        
        for i in range(8):
            self.client.keyPress('left') # Nos movemos al primer icono de la pantalla de Home
            time.sleep(0.2)
        
        for i in range(3):
            self.client.keyPress('right')
            time.sleep(0.2)  # Navegamos hasta el icono de Files
        
        self.client.keyPress('enter') # Entramos en Files
        time.sleep(0.2)
        
        for i in range(5):
            self.client.keyPress('esc') # Nos movemos al primer icono de la pantalla de Home
            time.sleep(0.2)

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
        
        # Seleccionamos el perfil a cargar
        if p_num == 1:
            self.client.keyPress('up')    # Nos aseguramos de estar arriba
        elif p_num == 2:
            self.client.keyPress('down')  # Bajamos al perfil 02_NOISE
            
        elif p_num == 3:
            self.client.keyPress('down')
            time.sleep(0.2)
            self.client.keyPress('down')  # Bajamos dos veces para escoger el perfil 03_STORM
        
        # Perfiles para escenario B, Test Loss Breakpoint Analysis
        # elif p_num == 4:
        #     
        # elif p_num == 5:
        #   
        # elif p_num == 6:
        #     
        # elif p_num == 7:
        #     
        
        self.client.keyPress('enter') # Seleccionamos el perfil
        time.sleep(0.5)
        
        # Apretamos Load para cargar el perfil
        # self.client.keyPress('f1')
        self.make_click(130, 268)  # Coordenadas del botón Load
        time.sleep(0.3)
        
        # Confirmamos el Load
        self.client.keyPress('left')
        time.sleep(0.3)
        self.client.keyPress('enter')
        time.sleep(1.0)
        
        self.client.keyPress('home')   # Volvemos a Home
        print(f"VNC: Perfil {filename}.cfg cargado.")
        
        time.sleep(0.5)
        
    def toggle_injection(self):
        """ Activa o desactiva la inyección de ruido en Netstorm via el atajo que dispone presionando Ctrl + e"""
        print("VNC: Activando inyección de ruido..")
        self.client.keyPress('ctrl-e')
        time.sleep(0.8)
            
_vnc_netstorm = None

# Keywords para Robot

def connect_to_netstorm(netstorm_ip: str, vnc_password: str):
    """ Conecta al Netstorm via VNC """
    global _vnc_netstorm
    _vnc_netstorm = NetstormController(netstorm_ip, vnc_password)

def disconnect_from_netstorm():
    """ Desconecta la sesión VNC del Netstorm """
    global _vnc_netstorm    # Variable global que mantiene la sesión VNC
    if _vnc_netstorm:
        _vnc_netstorm.disconnect()
        _vnc_netstorm = None

def set_network_profile(profile_name):
    """ Mapea nombres a números de perfil """
    if profile_name == "CLEAN":
        _vnc_netstorm.load_profile(1)
    elif profile_name == "NOISE":
        _vnc_netstorm.load_profile(2)
    elif profile_name == "STORM":
        _vnc_netstorm.load_profile(3)
    # Mapeo de perfiles escenario B, Test Loss Breakpoint Analysis
    # elif
    else:
        print(f"No se reconoce el perfil pasado como argumento: {profile_name}")
        
def toggle_noise():
    """ Inicia la inyección de ruido en Netstorm """
    _vnc_netstorm.toggle_injection()

        