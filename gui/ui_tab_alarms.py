import customtkinter as ctk

def create_alarms_tab(app_ref):
    """Crea y devuelve el frame para la sección de Alarmas."""
    main_frame = ctk.CTkFrame(app_ref, corner_radius=0, fg_color="transparent")
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)

    # --- Controles ---
    controls_frame = ctk.CTkFrame(main_frame)
    controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    controls_frame.grid_columnconfigure((0, 1), weight=1)

    start_button = ctk.CTkButton(controls_frame, text="▶️ Iniciar Monitorización", command=app_ref.alarms_controller.start_monitoring)
    start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    stop_button = ctk.CTkButton(controls_frame, text="⏹️ Detener Monitorización", command=app_ref.alarms_controller.stop_monitoring)
    stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # --- Paneles de Alarmas ---
    alarms_container = ctk.CTkFrame(main_frame)
    alarms_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    alarms_container.grid_columnconfigure((0, 1, 2), weight=1)
    alarms_container.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(alarms_container, text="System Alarms", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0)
    app_ref.system_alarms_textbox = ctk.CTkTextbox(alarms_container, state="disabled", wrap="word")
    app_ref.system_alarms_textbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    ctk.CTkLabel(alarms_container, text="Alarms Tp(1)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
    app_ref.tp1_alarms_textbox = ctk.CTkTextbox(alarms_container, state="disabled", wrap="word")
    app_ref.tp1_alarms_textbox.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    ctk.CTkLabel(alarms_container, text="Alarms Tp(2)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2)
    app_ref.tp2_alarms_textbox = ctk.CTkTextbox(alarms_container, state="disabled", wrap="word")
    app_ref.tp2_alarms_textbox.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
    
    return main_frame

def update_alarms_display(app_ref, alarms_data):
    """Actualiza las cajas de texto con la nueva información de alarmas."""
    if not alarms_data:
        print("ADVERTENCIA: update_alarms_display recibió datos vacíos.")
        return
    def update_textbox(textbox, content):
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", content if content else "Sin alarmas activas.")
        textbox.configure(state="disabled")

    if 'system' in alarms_data:
        update_textbox(app_ref.system_alarms_textbox, alarms_data['system'])
    if 'tp1' in alarms_data:
        update_textbox(app_ref.tp1_alarms_textbox, alarms_data['tp1'])
    if 'tp2' in alarms_data:
        update_textbox(app_ref.tp2_alarms_textbox, alarms_data['tp2'])
    
