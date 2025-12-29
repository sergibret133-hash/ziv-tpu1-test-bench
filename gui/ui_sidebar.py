import customtkinter as ctk
from PIL import Image
from logic import robot_executor
import os

def _create_session_frame(app_ref, parent_frame, session_id):
    """
    Función auxiliar para crear un marco de sesión (A o B).
    Devuelve los widgets creados para que app_ref pueda guardarlos.
    """
    frame = ctk.CTkFrame(parent_frame)
    frame.grid_columnconfigure(1, weight=1)  # Columna de la IP se expande
    
    # Indicador de sesión "A" o "B"
    ctk.CTkLabel(frame, text=f"SESIÓN {session_id}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=(5,0))
    
    # Label "IP" y Entrada para la IP
    ctk.CTkLabel(frame, text="IP:").grid(row=1, column=0, padx=(10, 2), pady=5, sticky="w")
    entry_ip = ctk.CTkEntry(frame, placeholder_text="10.212.42.231")
    entry_ip.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=5, sticky="ew")

    # Botones de Conexión
    # (Las funciones lambda pasan el session_id y la IP para que _start_browser_process_thread abra las correspondientes sesiones. Tambien para que _stop_browser_process_thread la cierre (en este caso no es necesario que le pasemos la ip).
    connect_btn = ctk.CTkButton(frame, text="Conectar", 
                                command=lambda s_id=session_id, ip_entry=entry_ip: 
                                robot_executor._start_browser_process_thread(app_ref, s_id, ip_entry.get()))
    connect_btn.grid(row=2, column=0, columnspan=2, padx=(10, 5), pady=5, sticky="ew")
    
    disconnect_btn = ctk.CTkButton(frame, text="Desconectar", 
                                   command=lambda s_id=session_id: 
                                   robot_executor._stop_browser_process_thread(app_ref, s_id), 
                                   state="disabled")
    disconnect_btn.grid(row=2, column=2, padx=(5, 10), pady=5, sticky="ew")

    # Etiqueta de Estado
    status_label = ctk.CTkLabel(frame, text="Estado: Desconectado", text_color="orange")    # Por defecto, la etiqueta de estado mostrará el texto "Desconectado". A no ser que la sesion se haya iniciado correctamente (la actualizaremos desde la funcion)
    status_label.grid(row=3, column=0, columnspan=3, pady=(0, 5))
    # Recordemos que la etiqueta SOLO SE CREA y se retorna! Luego se guarda en una variable app_ref que podrá ser accedida más tarde para actualizar el estado. ->
        # -> la fucion _start_browser_process_thread que hay en robot_executor avisará a traves de la cola de la GUI y posteriormente se ejecutará _update_session_status con el widget del status enviado.
    
    # Devuelve los widgets para guardarlos en app_ref
    return frame, entry_ip, connect_btn, disconnect_btn, status_label


def create_sidebar(app_ref):
    """Creates the side navigation panel with the main buttons."""
    # ************************************* FRAME ************************************************
    
    app_ref.sidebar_frame = ctk.CTkFrame(app_ref, width=180, corner_radius=0)
    app_ref.sidebar_frame.grid(row=0, column=0, sticky="nsw")
    app_ref.sidebar_frame.grid_rowconfigure(11, weight=1)

    app_ref.title_label = ctk.CTkLabel(app_ref.sidebar_frame, text="TPU Automation", font=ctk.CTkFont(size=20, weight="bold"))
    app_ref.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
    
    
    # ************************ *** Creación de los frames de las Sesiones A y B y guardado de variables de sesion en app_ref *********************
    # A:
    (session_frame_A, 
     app_ref.entry_ip_A, 
     app_ref.connect_button_A, 
     app_ref.disconnect_button_A, 
     app_ref.session_status_label_A)    =_create_session_frame(app_ref, app_ref.sidebar_frame, "A") # Nos devuelve el frame de la sesión A y el resto de widgets (con referencia app_ref ya que seran usado por otras funciones de otros archivos .py).
                                            # app.sidebar_frame es el frame parent, donde iran colocados todos los widgets y el frame que nos devuelve _create_session_frame.
                                            # En el ultimo argumento le pasamos la session id para la creacion del frame de esa sesion
    session_frame_A.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="ew")

    # B:
    (session_frame_B, 
     app_ref.entry_ip_B, 
     app_ref.connect_button_B, 
     app_ref.disconnect_button_B, 
     app_ref.session_status_label_B) =_create_session_frame(app_ref, app_ref.sidebar_frame, "B")
    # A parte del frame session_frame_B, necesitamos guardar tambien el resto de widgets (QUE AUN NO HAN SIDO UTILZADOS NI ACTUALIZADOS). ->
    # -> Como son variables que se guardan con app_ref, PODRAN SER ACCEDIDOS MÁS TARDE POR OTRAS FUNCIONES que enviaran, y actualizaran sus estados con otras llamadas.
    session_frame_B.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")


    # ************************************* Selector de Contexto ************************************************
    app_ref.context_selector = ctk.CTkSegmentedButton(
        app_ref.sidebar_frame, 
        values=["Equipo A", "Equipo B"], 
        command=app_ref.set_active_context  # Llama al método que creamos en app.py para actualizar la sesion que está activa cuando se pulse el boton. 
                                            # Tendremos los dos "values" declarados a escoger. Cuando pulsemos uno de ellos, será automaticamente pasado como primer argumento a la funcion set_active_context asignada en command.
    )
    app_ref.context_selector.set("Equipo A") # Al inicio, cuando aun no se haya pulsado el boton context_selector, tendremos que definir que este pulsado uno de los values por defecto.
    app_ref.context_selector.grid(row=3, column=0, padx=20, pady=10, sticky="ew")



    # ************************************* Botones de Sección ************************************************
    app_ref.section_buttons = {}
    sections = ["FILES", "UPDATING", "EQUIPMENT", "MONITORING", "ALIGNMENT", "SCHEDULER", "ALARMS"]

    for i, section_name in enumerate(sections):
        button = ctk.CTkButton(app_ref.sidebar_frame, text=section_name)
        button.configure(command=lambda b=button, n=section_name: app_ref._select_section(b, n))
        button.grid(row=i+4, column=0, padx=20, pady=10, sticky="ew")   # Empezamos en la fila 4 (después del selector de contexto sesion)
        app_ref.section_buttons[section_name] = button
        
        
    # ************************************* Logo y Versión ************************************************
    try:
        logo_image_data = Image.open("logo.png")
        logo_image = ctk.CTkImage(dark_image=logo_image_data, light_image=logo_image_data, size=(140, 140))
        logo_label = ctk.CTkLabel(app_ref.sidebar_frame, image=logo_image, text="")
        logo_label.grid(row=12, column=0, padx=20, pady=10)
    except FileNotFoundError:
        print("Logo file ('logo.png') not found. Skipping logo display.")

    app_ref.version_label = ctk.CTkLabel(app_ref.sidebar_frame, text="v5.0 - HIL + NOISE + MULTICHANNEL", anchor="w")
    app_ref.version_label.grid(row=13, column=0, padx=20, pady=(10, 20))