import customtkinter as ctk

def create_alignment_tab(app_ref):
    """Crea y devuelve el CTkTabView completo para la sección 'EQUIPMENT'."""
    
    tab_view = ctk.CTkTabview(app_ref, corner_radius=8)
    tab_view.add("Loops Blocking")
    tab_view.add("Input Activation")

    
    # Cada función se encarga rellenar su propia pestaña.
    _populate_loops_blocking_tab(app_ref, tab_view.tab("Loops Blocking"))
    _populate_input_activation_tab(app_ref, tab_view.tab("Input Activation"))
    
    # Devolvemos el TabView ya construido y rellenado
    return tab_view

def _update_alignment_states(app_ref, listener):
    """Updates the status labels, module names, and types in the Alignment tab."""
    if listener is None:
        print("DEBUG ALIGNMENT: listener es None. Limpiando o ignorando actualización.")
        # Opcional: podrías limpiar la UI si quieres:
        for widgets in [app_ref.loop1_widgets, app_ref.loop2_widgets, app_ref.blocking1_widgets, app_ref.blocking2_widgets]:
            if widgets:
                widgets['status_label'].configure(text="Estado: Desconocido", text_color="gray")
                widgets['module_label'].configure(text="Módulo: -", text_color="gray")
                if 'type_combo' in widgets:
                    widgets['type_combo'].set("NONE")
        return
    
    
    
    if listener.loop_state_1 is not None:
        _update_alignment_row_ui(app_ref.loop1_widgets, listener.loop_state_1 in ['1', 1, 'True', True], is_loop=True)
    if listener.loop_module_name_1 is not None:
        app_ref.loop1_widgets['module_label'].configure(text=f"Módulo: {listener.loop_module_name_1}")
    if listener.loop_type_1 is not None:
        type_str = app_ref.loop_type_map_rev.get(str(listener.loop_type_1), "NONE")
        app_ref.loop1_widgets['type_combo'].set(type_str)

    if listener.loop_state_2 is not None:
        _update_alignment_row_ui(app_ref.loop2_widgets, listener.loop_state_2 in ['1', 1, 'True', True], is_loop=True)
    if listener.loop_module_name_2 is not None:
        app_ref.loop2_widgets['module_label'].configure(text=f"Módulo: {listener.loop_module_name_2}")
    if listener.loop_type_2 is not None:
        type_str = app_ref.loop_type_map_rev.get(str(listener.loop_type_2), "NONE")
        app_ref.loop2_widgets['type_combo'].set(type_str)

    if listener.blocking_state_1 is not None:
        _update_alignment_row_ui(app_ref.blocking1_widgets, listener.blocking_state_1 in ['1', 1, 'True', True], is_loop=False)
    if listener.blocking_module_name_1 is not None:
        app_ref.blocking1_widgets['module_label'].configure(text=f"Módulo: {listener.blocking_module_name_1}")

    if listener.blocking_state_2 is not None:
        _update_alignment_row_ui(app_ref.blocking2_widgets, listener.blocking_state_2 in ['1', 1, 'True', True], is_loop=False)
    if listener.blocking_module_name_2 is not None:
        app_ref.blocking2_widgets['module_label'].configure(text=f"Módulo: {listener.blocking_module_name_2}")

def _update_alignment_row_ui(widgets, is_active, is_loop):
    """Central function to update a single row's UI based on its active state."""
    if not widgets: return

    widgets['status_label'].configure(text="Estado: Activo" if is_active else "Estado: Inactivo",
                                        text_color="green" if is_active else "orange")
    if not is_active:
        widgets['timer_label'].pack_forget()

    controls_state = "disabled" if is_active else "normal"
    widgets['activate_button'].configure(state="disabled" if is_active else "normal")
    widgets['deactivate_button'].configure(state="normal" if is_active else "disabled")
    widgets['duration_combo'].configure(state=controls_state)
    if is_loop and 'type_combo' in widgets:
        widgets['type_combo'].configure(state=controls_state)
        
        
def _get_alignment_widgets(app_ref, tp_number, is_loop):
    """Returns the widget dictionary for a given alignment row."""
    if is_loop:
        return app_ref.loop1_widgets if tp_number == 1 else app_ref.loop2_widgets
    else:
        return app_ref.blocking1_widgets if tp_number == 1 else app_ref.blocking2_widgets
        
        
# ************************** LOOPS & BLOCKING TAB **************************
def _populate_loops_blocking_tab(app_ref, tab_frame):
    """Populates the Loops and Blocking tab with its widgets."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(1, weight=1)

    control_frame = ctk.CTkFrame(tab_frame)
    control_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
    app_ref.refresh_alignment_button = ctk.CTkButton(control_frame, text="Consultar Estados Actuales de Bucles y Bloqueos", command=app_ref.alignment_controller._run_refresh_alignment_states_thread)
    app_ref.refresh_alignment_button.pack(pady=10, padx=10, fill="x")

    container = ctk.CTkScrollableFrame(tab_frame, label_text="Control de Bucles y Bloqueos")
    container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
    container.grid_columnconfigure(0, weight=1)

    loops_frame = ctk.CTkFrame(container)
    loops_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    loops_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(loops_frame, text="LOOPS", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 10))
    
    app_ref.loop1_widgets = _create_alignment_control_row(app_ref, loops_frame, "TELEPROTECTION -1-", 1, is_loop=True)
    app_ref.loop2_widgets = _create_alignment_control_row(app_ref, loops_frame, "TELEPROTECTION -2-", 2, is_loop=True)

    blocking_frame = ctk.CTkFrame(container)
    blocking_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    blocking_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(blocking_frame, text="BLOCKING", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 10))

    app_ref.blocking1_widgets = _create_alignment_control_row(app_ref, blocking_frame, "TELEPROTECTION -1-", 1, is_loop=False)
    app_ref.blocking2_widgets = _create_alignment_control_row(app_ref, blocking_frame, "TELEPROTECTION -2-", 2, is_loop=False)

    log_button = ctk.CTkButton(tab_frame, text="📂 Open Last Report (log.html)", state="disabled", command=app_ref._open_log_file)
    log_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="s")
    app_ref.log_buttons.append(log_button)

def _create_alignment_control_row(app_ref, parent, title, tp_number, is_loop):
    """Helper function to create a control row for loops or blocking."""
    widgets = {}
    row_frame = ctk.CTkFrame(parent)
    row_frame.pack(fill="x", expand=True, padx=10, pady=5)

    row_frame.grid_columnconfigure(2, weight=1)
    row_frame.grid_columnconfigure(4, weight=1)

    ctk.CTkLabel(row_frame, text=title, width=130).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

    status_module_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
    status_module_frame.grid(row=0, column=1, padx=5, pady=10, sticky="w")
    widgets['status_label'] = ctk.CTkLabel(status_module_frame, text="Estado: Desconocido", width=120)
    widgets['status_label'].pack(anchor="w")
    widgets['module_label'] = ctk.CTkLabel(status_module_frame, text="Módulo: -", text_color="gray")
    widgets['module_label'].pack(anchor="w")
    widgets['timer_label'] = ctk.CTkLabel(status_module_frame, text="", text_color="cyan")
    widgets['timer_label'].pack(anchor="w")
    widgets['timer_label'].pack_forget()

    if is_loop:
        ctk.CTkLabel(row_frame, text="Type:").grid(row=0, column=2, padx=(10, 5), pady=10, sticky="e")
        widgets['type_combo'] = ctk.CTkComboBox(row_frame, values=list(app_ref.loop_type_map.keys()), width=120)
        widgets['type_combo'].grid(row=0, column=3, padx=(0, 10), pady=10, sticky="w")
        widgets['type_combo'].set("NONE")
    
    ctk.CTkLabel(row_frame, text="Duration:").grid(row=0, column=4, padx=(10, 5), pady=10, sticky="e")
    widgets['duration_combo'] = ctk.CTkComboBox(row_frame, values=list(app_ref.duration_map.keys()), width=140)
    widgets['duration_combo'].grid(row=0, column=5, padx=(0, 10), pady=10, sticky="w")
    widgets['duration_combo'].set("Permanente")

    button_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
    button_frame.grid(row=0, column=6, padx=10, pady=10)

    if is_loop:
        command_activate = lambda: app_ref.alignment_controller._run_program_loop_thread(tp_number, activate=True)
        command_deactivate = lambda: app_ref.alignment_controller._run_program_loop_thread(tp_number, activate=False)
    else:
        command_activate = lambda: app_ref.alignment_controller._run_program_blocking_thread(tp_number, activate=True)
        command_deactivate = lambda: app_ref.alignment_controller._run_program_blocking_thread(tp_number, activate=False)

    widgets['activate_button'] = ctk.CTkButton(button_frame, text="Activar", width=80, command=command_activate)
    widgets['activate_button'].pack(side="left", padx=(0, 5))
    widgets['deactivate_button'] = ctk.CTkButton(button_frame, text="Desactivar", width=80, command=command_deactivate)
    widgets['deactivate_button'].pack(side="left")

    return widgets

def _alignment_countdown(app_ref, remaining_seconds, timer_key):
    """Handles the countdown for a temporary loop/block."""
    tp_number = int(timer_key.split('_')[1])
    is_loop = 'loop' in timer_key
    widgets = _get_alignment_widgets(tp_number, is_loop)

    if remaining_seconds > 0:
        widgets['timer_label'].configure(text=f"Finaliza en {remaining_seconds}s")
        timer_id = app_ref.after(1000, app_ref._alignment_countdown, remaining_seconds - 1, timer_key)
        app_ref.alignment_timers[timer_key] = timer_id
    else:
        widgets['timer_label'].pack_forget()
        _update_alignment_row_ui(widgets, is_active=False, is_loop=is_loop)
        if timer_key in app_ref.alignment_timers:
            del app_ref.alignment_timers[timer_key]

# ************************** INPUT ACTIVATION TAB **************************
def _populate_input_activation_tab(app_ref, tab_frame):
    """Populates the Input Activation tab with its widgets. Includes Software/Hardware input controls."""
    # *** FRAME DE CONTROL HIL ***
    hil_frame = ctk.CTkFrame(tab_frame)
    hil_frame.pack(pady=(10, 5), padx=10, fill="x", anchor="n")
    
    hil_label = ctk.CTkLabel(hil_frame, text="Controlador HIL con Raspberry Pi", font=ctk.CTkFont(weight="bold"))
    hil_label.pack(side="left", padx=(10, 5))

    # Guardamos la entrada de IP en 'app_ref.rpi_ip_entry' para que el controlador la lea
    app_ref.rpi_ip_entry = ctk.CTkEntry(hil_frame, placeholder_text="IP de Raspberry Pi")
    app_ref.rpi_ip_entry.pack(side="left", padx=5, fill="x", expand=True)


    # *** Cabecera Activación de Entradas  ***
    input_activation_frame = ctk.CTkFrame(tab_frame)
    input_activation_frame.pack(pady=5, padx=10, fill="x", anchor="n")

    input_activation_header_frame = ctk.CTkFrame(input_activation_frame, fg_color="transparent")
    input_activation_header_frame.pack(fill="x", padx=10, pady=(5,0))

    app_ref.retrieve_inputs_button = ctk.CTkButton(input_activation_header_frame, text="Consultar Estado de Entradas", width=150, command=app_ref.alignment_controller._run_retrieve_inputs_state_thread)
    app_ref.retrieve_inputs_button.pack(side="left")

    app_ref.input_activation_status_label = ctk.CTkLabel(input_activation_header_frame, text="Estado: Desconocido", text_color="gray", font=ctk.CTkFont(weight="bold"))
    app_ref.input_activation_status_label.pack(side="left", padx=20)

    # Contenedor para la rejilla de checkboxes. _update_input_activation_display lo rellenará de forma dinámica.
    app_ref.input_checkbox_scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Entradas Disponibles")
    app_ref.input_checkbox_scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)
    
    # 4 columnas para el frame deslizable
    app_ref.input_checkbox_scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
    
    
    # *******************************************************************************************************************
    # *** FRAME DE CONTROLES DE EJECUCIÓN ***
    controls_frame = ctk.CTkFrame(tab_frame)
    controls_frame.pack(pady=5, padx=10, fill="x", anchor="s")
    
    # *** FRAMES INTERNOS PARA SOFTWARE Y HARDWARE ***
    software_controls_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    hardware_controls_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    
    # *** Cambiar de modo ***
    def on_activation_mode_change(mode):
        if mode == "Software":
            software_controls_frame.pack(fill="x", expand=True)
            hardware_controls_frame.pack_forget()
        elif mode == "Hardware":
            software_controls_frame.pack_forget()
            hardware_controls_frame.pack(fill="x", expand=True)

    # *** Selector para el modo ***
    mode_selector = ctk.CTkSegmentedButton(
        controls_frame,
        values=["Software", "Hardware"],
        command=on_activation_mode_change
    )
    mode_selector.pack(fill="x", padx=10, pady=10)
    # mode_selector.set("Software") # Estado inicial            
        
# *******************************************************************************************************************
    # *** CONTROLES SOFTWARE *** 
    software_controls_frame.grid_columnconfigure(2, weight=1)   # De esta manera la columna 2 (la de la entrada de la duración y la del botón de programar inputs) se expanderá
    
    # Radio buttons para Activar / Desactivar
    app_ref.activation_mode_var = ctk.StringVar(value="activate")
    activate_radio = ctk.CTkRadioButton(software_controls_frame, text="Activar", variable=app_ref.activation_mode_var, value="activate")
    activate_radio.grid(row=0, column=0, rowspan=2, padx=10, pady=5, sticky="w")
    deactivate_radio = ctk.CTkRadioButton(software_controls_frame, text="Desactivar", variable=app_ref.activation_mode_var, value="deactivate")
    deactivate_radio.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    
    # DURACION
    sw_label = ctk.CTkLabel(software_controls_frame, text="Duración (Software):", anchor="w")
    sw_label.grid(row=0, column=1, padx=(10,0), pady=5, sticky="w")
    
    app_ref.input_activation_duration_combo = ctk.CTkComboBox(
        software_controls_frame, 
        values=list(app_ref.duration_map.keys()),
        width=150
    )
    app_ref.input_activation_duration_combo.grid(row=1, column=1, padx=(10,5), pady=5, sticky="w")
    app_ref.input_activation_duration_combo.set("Permanente")
    
    # BOTON PROGRAMAR
    app_ref.program_inputs_button = ctk.CTkButton(
        software_controls_frame, 
        text="Programar Entradas (Software)", 
        command=app_ref.alignment_controller._run_program_inputs_state_thread
    )
    app_ref.program_inputs_button.grid(row=0, column=2, padx=10, pady=5, sticky="e")
    
# *******************************************************************************************************************
    # *** CONTROLES HARDWARE ***
    hardware_controls_frame.grid_columnconfigure(3, weight=1)
    
    # Fila 1: Canales & Pulsos
    hw_label_pulses = ctk.CTkLabel(hardware_controls_frame, text="Num Pulsos:", anchor="w")
    hw_label_pulses.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    app_ref.hil_pulses_entry = ctk.CTkEntry(hardware_controls_frame, placeholder_text="ej. 10", width=100)
    app_ref.hil_pulses_entry.insert(0, "10")
    app_ref.hil_pulses_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    # Fila 2: Entrada de duración del pulso y Delay
    # Duracion
    hw_label_duration = ctk.CTkLabel(hardware_controls_frame, text="Duración (s):", anchor="w")
    hw_label_duration.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    app_ref.hil_pulse_duration_entry = ctk.CTkEntry(hardware_controls_frame, placeholder_text="ej. 0.5", width=100)
    app_ref.hil_pulse_duration_entry.insert(0, "0.5")
    app_ref.hil_pulse_duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    
    # Delay
    hw_label_delay = ctk.CTkLabel(hardware_controls_frame, text="Delay (s):", anchor="w")
    hw_label_delay.grid(row=1, column=2, padx=10, pady=5, sticky="w")

    app_ref.hil_pulse_delay_entry = ctk.CTkEntry(hardware_controls_frame, placeholder_text="ej. 1.0", width=100)
    app_ref.hil_pulse_delay_entry.insert(0, "1.0")
    app_ref.hil_pulse_delay_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
    
    # Botón Enviar Rafaga 
    app_ref.hil_burst_button = ctk.CTkButton(hardware_controls_frame, text="Enviar Pulso(s) HIL", command=app_ref.alignment_controller.run_hil_burst)
    app_ref.hil_burst_button.grid(row=0, column=4, padx=10, pady=5, sticky="e")
    
    
    
    on_activation_mode_change("Software")   # Mostramos los controles de Software por defecto
    mode_selector.set("Software")




def _update_input_activation_display(app_ref, state, input_info):
    """Dynamically builds the checkboxes for input activation.
        state - dict with 'inputs' list VALUE STATE and 'duration' (str) or None if inactive.
        input_info - list of input NAMES (NOT states)"""
    # Cancelar temporizador previo si existe
    if app_ref.activation_timer:
        app_ref.after_cancel(app_ref.activation_timer)
        app_ref.activation_timer = None
    
    # Limpiar checkboxes previos
    for widget in app_ref.input_checkbox_scroll_frame.winfo_children():
        widget.destroy()
    app_ref.input_activation_checkboxes.clear()

    # Actualizamos la etiqueta de estado con el temporizador en caso de ser activado
    if state:
        app_ref.input_activation_status_label.configure(text="Estado: Activo", text_color="green")
        app_ref.inputs_are_active = True
        if state.get("duration", "0") != "0":   # Si la duración no es permanente, iniciar el temporizador. Adquirimos el valor de duración del diccionario 'state'
            _start_activation_timer(app_ref, int(state["duration"]))
    else:
        app_ref.input_activation_status_label.configure(text="Estado: Inactivo", text_color="orange")
        app_ref.inputs_are_active = False

    if not input_info or not isinstance(input_info, list):
        ctk.CTkLabel(app_ref.input_checkbox_scroll_frame, text="No se encontraron entradas o están inactivas.").pack(pady=10)
        return
    
    # Crear checkboxes en una rejilla de 4 columnas
    cols = 4
    # Vamos iterando todos los nombres de input_info: ['IPTU-1/Inp 1', 'IPTU-1/Inp 2', 'IPTU-1/Inp 3', ...]
    for i, input_name in enumerate(input_info):
        row = i // cols
        col = i % cols
        
        # Usamos 'app_ref.input_checkbox_scroll_frame' como padre
        checkbox = ctk.CTkCheckBox(app_ref.input_checkbox_scroll_frame, text=f"{i+1}: {input_name}")    # Creamos el checkbox
        checkbox.grid(row=row, column=col, padx=10, pady=5, sticky="w")
        
        # Marcamos la casilla si nos llega info de 'state', si no hemos llegado al final del vector de estado de inputs de 'state' y si el estado que estamos iterando esta activo ( == 1)
        if state and i < len(state.get("inputs", [])) and state.get("inputs", [])[i] == 1:
            checkbox.select()
        
        # Guardamos la referencia al checkbox
        app_ref.input_activation_checkboxes.append(checkbox)
        
def _start_activation_timer(app_ref, duration_seconds):
    """Starts a countdown timer that updates the status label."""
    if app_ref.activation_timer:
        app_ref.after_cancel(app_ref.activation_timer)

    _update_countdown(app_ref, duration_seconds)

def _update_countdown(app_ref, remaining_seconds):
    """Updates the countdown label each second."""
    if remaining_seconds > 0:
        app_ref.input_activation_status_label.configure(text=f"Estado: Activo (finaliza en {remaining_seconds}s)", text_color="green")
        app_ref.activation_timer = app_ref.after(1000, _update_countdown, app_ref, remaining_seconds - 1)
    else:
        app_ref.input_activation_status_label.configure(text="Estado: Inactivo", text_color="orange")
        app_ref.inputs_are_active = False
        app_ref.activation_timer = None
        for cb in app_ref.input_activation_checkboxes:
            cb.deselect()
            
def _handle_program_inputs_success(app_ref, activate_deactivate, duration, inputs_list):
    """Handles the GUI update after a successful input activation/deactivation."""
    is_activating = (activate_deactivate == "1")
    app_ref.inputs_are_active = is_activating

    if is_activating:
        for i, cb in enumerate(app_ref.input_activation_checkboxes):
            if i < len(inputs_list):
                if inputs_list[i] == 1:
                    cb.select()
                else:
                    cb.deselect()
        
        if duration != "0":
            _start_activation_timer(app_ref, int(duration))
        else:
            app_ref.input_activation_status_label.configure(text="Estado: Activo", text_color="green")
    else:
        app_ref.input_activation_status_label.configure(text="Estado: Inactivo", text_color="orange")
        if app_ref.activation_timer:
            app_ref.after_cancel(app_ref.activation_timer)
            app_ref.activation_timer = None
        for cb in app_ref.input_activation_checkboxes:
            cb.deselect()
            




