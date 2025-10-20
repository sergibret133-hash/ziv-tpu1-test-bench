

import customtkinter as ctk
from PIL import Image
from logic import robot_executor



def create_sidebar(app_ref):
    """Creates the side navigation panel with the main buttons."""
    app_ref.sidebar_frame = ctk.CTkFrame(app_ref, width=180, corner_radius=0)
    app_ref.sidebar_frame.grid(row=0, column=0, sticky="nsw")
    app_ref.sidebar_frame.grid_rowconfigure(10, weight=1)

    app_ref.title_label = ctk.CTkLabel(app_ref.sidebar_frame, text="TPU Automation", font=ctk.CTkFont(size=20, weight="bold"))
    app_ref.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

    session_frame = ctk.CTkFrame(app_ref.sidebar_frame)
    session_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    session_frame.grid_columnconfigure(0, weight=1)
    
    ctk.CTkLabel(session_frame, text="SESIÓN", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5,0))
    app_ref.connect_button = ctk.CTkButton(session_frame, text="Conectar", command=lambda: robot_executor._start_browser_process_thread(app_ref))
    app_ref.connect_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    app_ref.disconnect_button = ctk.CTkButton(session_frame, text="Desconectar", command=lambda: robot_executor._stop_browser_process_thread(app_ref), state="disabled")
    app_ref.disconnect_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    app_ref.session_status_label = ctk.CTkLabel(session_frame, text="Estado: Desconectado", text_color="orange")
    app_ref.session_status_label.grid(row=2, column=0, columnspan=2, pady=(0,5))

    app_ref.section_buttons = {}
    sections = ["FILES", "UPDATING", "EQUIPMENT", "MONITORING", "ALIGNMENT", "SCHEDULER", "ALARMS"]

    for i, section_name in enumerate(sections):
        button = ctk.CTkButton(app_ref.sidebar_frame, text=section_name)
        button.configure(command=lambda b=button, n=section_name: app_ref._select_section(b, n))
        button.grid(row=i+2, column=0, padx=20, pady=10, sticky="ew")
        app_ref.section_buttons[section_name] = button

    try:
        logo_image_data = Image.open("logo.png")
        logo_image = ctk.CTkImage(dark_image=logo_image_data, light_image=logo_image_data, size=(140, 140))
        logo_label = ctk.CTkLabel(app_ref.sidebar_frame, image=logo_image, text="")
        logo_label.grid(row=11, column=0, padx=20, pady=10)
    except FileNotFoundError:
        print("Logo file ('logo.png') not found. Skipping logo display.")

    app_ref.version_label = ctk.CTkLabel(app_ref.sidebar_frame, text="v1.4 - Desarrollo", anchor="w")
    app_ref.version_label.grid(row=12, column=0, padx=20, pady=(10, 20))