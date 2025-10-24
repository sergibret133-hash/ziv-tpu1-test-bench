
import customtkinter as ctk
import tkinter as tk

# ************************** EQUIPMENT TAB **************************
def create_equipment_tab(app_ref):
    """Crea y devuelve el CTkTabView completo para la sección 'EQUIPMENT'."""
    
    # 1. Crear el contenedor de pestañas
    tab_view = ctk.CTkTabview(app_ref, corner_radius=8)
    tab_view.add("Basic Configuration")
    tab_view.add("Command Assignment")
    tab_view.add("Module Configuration")
    
    # 2. Delegar el rellenado de cada sub-pestaña a su función correspondiente
    _populate_basic_config_tab(app_ref, tab_view.tab("Basic Configuration"))
    _populate_command_assignment_tab(app_ref, tab_view.tab("Command Assignment"))
    _populate_module_config_tab(app_ref, tab_view.tab("Module Configuration"))
    
    # 3. Devolver el TabView ya construido y rellenado
    return tab_view


# ************************** BASIC CONFIG TAB **************************
def _populate_basic_config_tab(app_ref, tab_frame):
    """Populates the 'Basic Configuration' tab with its widgets."""
    tab_frame.grid_columnconfigure(0, weight=1)

    main_scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Funcionalidades de Configuración Básica")
    main_scroll_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
    main_scroll_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(0, weight=1)

    list_modules_frame = ctk.CTkFrame(main_scroll_frame)
    list_modules_frame.grid(row=0, column=0, pady=10, sticky="ew")
    ctk.CTkLabel(list_modules_frame, text="1. Listar Módulos en el Equipo", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    app_ref.list_modules_button = ctk.CTkButton(list_modules_frame, text="Listar Módulos Instalados", command=app_ref.equipment_controller._run_list_modules_thread)
    app_ref.list_modules_button.pack(pady=10)
    app_ref.modules_result_frame = ctk.CTkScrollableFrame(list_modules_frame, label_text="Módulos Detectados", height=150)
    app_ref.modules_result_frame.pack(pady=10, padx=10, fill="both", expand=True)
    _update_modules_display(app_ref, [])

    assign_modules_frame = ctk.CTkFrame(main_scroll_frame)
    assign_modules_frame.grid(row=1, column=0, pady=10, sticky="ew")
    ctk.CTkLabel(assign_modules_frame, text="2. Asignar Módulos Priorizados", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    
    tp1_frame = ctk.CTkFrame(assign_modules_frame, fg_color="transparent")
    tp1_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(tp1_frame, text="Módulo Prioridad 1 (TP1):", width=180).pack(side="left")
    app_ref.entry_tp1 = ctk.CTkEntry(tp1_frame, placeholder_text="Nombre del módulo, ej: IDTU (1)")
    app_ref.entry_tp1.pack(side="left", expand=True, fill="x")

    tp2_frame = ctk.CTkFrame(assign_modules_frame, fg_color="transparent")
    tp2_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(tp2_frame, text="Módulo Prioridad 2 (TP2):", width=180).pack(side="left")
    app_ref.entry_tp2 = ctk.CTkEntry(tp2_frame, placeholder_text="Nombre del módulo, ej: IPTU (1)")
    app_ref.entry_tp2.pack(side="left", expand=True, fill="x")
    
    app_ref.assign_modules_button = ctk.CTkButton(assign_modules_frame, text="Asignar Módulos Priorizados", command=app_ref.equipment_controller._run_assign_modules_thread)
    app_ref.assign_modules_button.pack(pady=15)

    view_assigned_frame = ctk.CTkFrame(main_scroll_frame)
    view_assigned_frame.grid(row=2, column=0, pady=10, sticky="ew")
    ctk.CTkLabel(view_assigned_frame, text="3. Consultar y Programar Órdenes", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    app_ref.view_assigned_button = ctk.CTkButton(view_assigned_frame, text="Consultar Configuración Actual", command=app_ref.equipment_controller._run_view_assigned_thread)
    app_ref.view_assigned_button.pack(pady=10)
    
    assigned_display_container = ctk.CTkFrame(view_assigned_frame, fg_color="transparent")
    assigned_display_container.pack(fill="x", expand=True, padx=10)
    assigned_display_container.grid_columnconfigure((0, 1), weight=1)
    
    tp1_display_frame = ctk.CTkFrame(assigned_display_container)
    tp1_display_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
    ctk.CTkLabel(tp1_display_frame, text="Teleprotección 1", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    app_ref.tp1_module_label = app_ref._create_info_row(tp1_display_frame, "Módulo:")
    app_ref.tp1_tx_entry = app_ref._create_info_entry_row(tp1_display_frame, "Órdenes TX:")
    app_ref.tp1_rx_entry = app_ref._create_info_entry_row(tp1_display_frame, "Órdenes RX:")

    tp2_display_frame = ctk.CTkFrame(assigned_display_container)
    tp2_display_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
    ctk.CTkLabel(tp2_display_frame, text="Teleprotección 2", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    app_ref.tp2_module_label = app_ref._create_info_row(tp2_display_frame, "Módulo:")
    app_ref.tp2_tx_entry = app_ref._create_info_entry_row(tp2_display_frame, "Órdenes TX:")
    app_ref.tp2_rx_entry = app_ref._create_info_entry_row(tp2_display_frame, "Órdenes RX:")
    
    app_ref.program_commands_button = ctk.CTkButton(view_assigned_frame, text="Programar Nuevas Órdenes", command=app_ref.equipment_controller._run_program_commands_thread)
    app_ref.program_commands_button.pack(pady=(15,10))
    
    timezone_frame = ctk.CTkFrame(main_scroll_frame)
    timezone_frame.grid(row=4, column=0, pady=10, sticky="ew")
    ctk.CTkLabel(timezone_frame, text="4. Configurar Zona Horaria", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    
    tz_selector_frame = ctk.CTkFrame(timezone_frame, fg_color="transparent")
    tz_selector_frame.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(tz_selector_frame, text="Zona Horaria:", width=180).pack(side="left")
    app_ref.timezone_selector = ctk.CTkComboBox(tz_selector_frame, values=list(app_ref.timezone_map.keys()))
    app_ref.timezone_selector.pack(side="left", expand=True, fill="x")
    app_ref.timezone_selector.set("(UTC+2)Madrid")

    app_ref.program_timezone_button = ctk.CTkButton(timezone_frame, text="Programar Zona Horaria", command=app_ref.equipment_controller._run_configure_timezone_thread)
    app_ref.program_timezone_button.pack(pady=15)

    status_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
    status_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
    app_ref.status_label = ctk.CTkLabel(status_frame, text="Status: Ready", font=ctk.CTkFont(weight="bold"))
    app_ref.status_label.pack(pady=5)
    log_button = ctk.CTkButton(status_frame, text="📂 Open Last Report (log.html)", state="disabled", command=app_ref._open_log_file)
    log_button.pack(pady=5)
    app_ref.log_buttons.append(log_button)
    
def _populate_module_config_tab(app_ref, tab_frame):
    """Populates the 'Module Configuration' tab with sub-tabs for each module."""
    module_names = ["IBTU_ByTones", "IBTU_DualTone", "IBTU_FFT", "IBTU_FSK", "ICPT", "IDTU", "IOCS", "IOCT", "IOTU"]
    
    module_tab_view = app_ref._create_tab_view(tab_frame, module_names)
    module_tab_view.pack(fill="both", expand=True, padx=10, pady=10)

    for module_name in module_names:
        sub_tab = module_tab_view.tab(module_name)
        sub_tab.grid_columnconfigure(0, weight=1)
        sub_tab.grid_rowconfigure(0, weight=1)

        if module_name == "IBTU_ByTones":
            _populate_ibtu_bytones_tab(app_ref, sub_tab)
        elif module_name == "IBTU_FFT":
            _populate_ibtu_fft_tab(app_ref, sub_tab)
        else:
            placeholder_frame = ctk.CTkFrame(sub_tab, fg_color="transparent")
            placeholder_frame.grid(row=0, column=0, sticky="nsew")
            ctk.CTkLabel(placeholder_frame, text=f"Configuración para {module_name}\n(En desarrollo)", 
                            font=ctk.CTkFont(size=16)).pack(expand=True)

        log_button = ctk.CTkButton(sub_tab, text="📂 Open Last Report (log.html)", state="disabled", command=app_ref._open_log_file)
        log_button.grid(row=1, column=0, padx=20, pady=20, sticky="s")
        app_ref.log_buttons.append(log_button)    
    
    

def _update_modules_display(app_ref, module_list):
    for widget in app_ref.modules_result_frame.winfo_children():
        widget.destroy()
    if not module_list:
        ctk.CTkLabel(app_ref.modules_result_frame, text="Awaiting module list...").grid(row=0, column=0, padx=10, pady=10)
        return
    app_ref.modules_result_frame.grid_columnconfigure((0, 1), weight=1)
    ctk.CTkLabel(app_ref.modules_result_frame, text="Slot", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")
    ctk.CTkLabel(app_ref.modules_result_frame, text="Módulo", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=(5, 10), sticky="w")
    for i, module_name in enumerate(module_list):
        text_color = "gray60" if module_name == "None" else ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        ctk.CTkLabel(app_ref.modules_result_frame, text=f"#{i}", text_color=text_color).grid(row=i + 1, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(app_ref.modules_result_frame, text=module_name, anchor="w", text_color=text_color).grid(row=i + 1, column=1, padx=10, pady=2, sticky="ew")
    
def _update_assigned_modules_display(app_ref, tp1_info, tp2_info):
    """Thread-safe function to update the assigned modules display."""
    def set_entry_value(entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)

    if tp1_info and isinstance(tp1_info, list) and len(tp1_info) == 2:
        app_ref.tp1_module_label.configure(text=tp1_info[0])
        set_entry_value(app_ref.tp1_tx_entry, tp1_info[1][0])
        set_entry_value(app_ref.tp1_rx_entry, tp1_info[1][1])
    else:
        app_ref.tp1_module_label.configure(text="-")
        set_entry_value(app_ref.tp1_tx_entry, "")
        set_entry_value(app_ref.tp1_rx_entry, "")

    if tp2_info and isinstance(tp2_info, list) and len(tp2_info) == 2:
        app_ref.tp2_module_label.configure(text=tp2_info[0])
        set_entry_value(app_ref.tp2_tx_entry, tp2_info[1][0])
        set_entry_value(app_ref.tp2_rx_entry, tp2_info[1][1])
    else:
        app_ref.tp2_module_label.configure(text="-")
        set_entry_value(app_ref.tp2_tx_entry, "")
        set_entry_value(app_ref.tp2_rx_entry, "")    
    # ************************** COMMAND ASSIGNMENT TAB ************************** 
    
    
def _populate_command_assignment_tab(app_ref, tab_frame):
    """Populates the 'Command Assignment' tab with its widgets."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(1, weight=1)
    
    control_frame = ctk.CTkFrame(tab_frame)
    control_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
    app_ref.refresh_assignments_button = ctk.CTkButton(control_frame, text="Consultar Configuración de Entradas/Salidas y Comandos", command=app_ref.equipment_controller._run_log_command_info_thread)
    app_ref.refresh_assignments_button.pack(pady=10)

    container = ctk.CTkScrollableFrame(tab_frame, label_text="Asignación de Comandos")
    container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
    container.grid_columnconfigure(0, weight=1)

    tx_section_frame = ctk.CTkFrame(container)
    tx_section_frame.grid(row=0, column=0, sticky="nsew", pady=(0,20))
    ctk.CTkLabel(tx_section_frame, text="ASSIGNMENT OF INPUTS TO COMMANDS (TX)", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    
    app_ref.tx_header_frame = ctk.CTkFrame(tx_section_frame, fg_color=("gray85", "gray15"))
    app_ref.tx_header_frame.pack(fill="x", padx=10, pady=(5,0))
    app_ref.tx_tp1_header_label = app_ref._create_command_header_row(app_ref.tx_header_frame, "Teleprotection (1)")
    app_ref.tx_tp2_header_label = app_ref._create_command_header_row(app_ref.tx_header_frame, "Teleprotection (2)")
    
    app_ref.tx_grid_frame = ctk.CTkFrame(tx_section_frame)
    app_ref.tx_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)

    rx_section_frame = ctk.CTkFrame(container)
    rx_section_frame.grid(row=1, column=0, sticky="nsew", pady=(10,0))
    ctk.CTkLabel(rx_section_frame, text="ASSIGNMENT OF COMMANDS(RX) TO OUTPUTS", font=ctk.CTkFont(weight="bold")).pack(pady=5)

    app_ref.rx_header_frame = ctk.CTkFrame(rx_section_frame, fg_color=("gray85", "gray15"))
    app_ref.rx_header_frame.pack(fill="x", padx=10, pady=(5,0))
    app_ref.rx_tp1_header_label = app_ref._create_command_header_row(app_ref.rx_header_frame, "Teleprotection (1)")
    app_ref.rx_tp2_header_label = app_ref._create_command_header_row(app_ref.rx_header_frame, "Teleprotection (2)")

    app_ref.rx_grid_frame = ctk.CTkFrame(rx_section_frame)
    app_ref.rx_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    app_ref.program_assignments_button = ctk.CTkButton(tab_frame, text="Programar Asignaciones", command=app_ref.equipment_controller._run_program_assignments_thread)
    app_ref.program_assignments_button.grid(row=2, column=0, padx=20, pady=(10,20))

    log_button = ctk.CTkButton(tab_frame, text="📂 Open Last Report (log.html)", state="disabled", command=app_ref._open_log_file)
    log_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="s")
    app_ref.log_buttons.append(log_button)

    _update_command_assignment_grids(app_ref, None, 0, 0)
    
def _update_command_assignment_grids(app_ref, command_ranges, num_inputs, num_outputs):
    """Dynamically builds the checkbox grids for command assignment, including logic controls."""
    for widget in app_ref.tx_grid_frame.winfo_children(): widget.destroy()
    for widget in app_ref.rx_grid_frame.winfo_children(): widget.destroy()
    app_ref.tx_checkboxes.clear()
    app_ref.rx_checkboxes.clear()
    app_ref.tx_logic_checkboxes.clear()
    app_ref.rx_logic_checkboxes.clear()

    if not command_ranges or len(command_ranges) < 10:
        ctk.CTkLabel(app_ref.tx_grid_frame, text="Consulte la configuración para ver la tabla.").pack()
        ctk.CTkLabel(app_ref.rx_grid_frame, text="Consulte la configuración para ver la tabla.").pack()
        app_ref.tx_tp1_header_label.configure(text="Teleprotection (1): ...")
        app_ref.tx_tp2_header_label.configure(text="Teleprotection (2): ...")
        app_ref.rx_tp1_header_label.configure(text="Teleprotection (1): ...")
        app_ref.rx_tp2_header_label.configure(text="Teleprotection (2): ...")
        return
    
    tp1_name, tp2_name, tp1_min_in, tp1_max_in, tp1_min_out, tp1_max_out, tp2_min_in, tp2_max_in, tp2_min_out, tp2_max_out = command_ranges
    app_ref.tx_tp1_header_label.configure(text=f"Teleprotection (1)    {tp1_name}    Commands TX    {tp1_min_in} - {tp1_max_in}")
    app_ref.tx_tp2_header_label.configure(text=f"Teleprotection (2)    {tp2_name}    Commands TX    {tp2_min_in} - {tp2_max_in}")
    app_ref.rx_tp1_header_label.configure(text=f"Teleprotection (1)    {tp1_name}    Commands RX    {tp1_min_out} - {tp1_max_out}")
    app_ref.rx_tp2_header_label.configure(text=f"Teleprotection (2)    {tp2_name}    Commands RX    {tp2_min_out} - {tp2_max_out}")
    
    max_cmd_tx = max(int(tp1_max_in), int(tp2_max_in))
    max_cmd_rx = max(int(tp1_max_out), int(tp2_max_out))
    
    app_ref._build_grid(app_ref.tx_grid_frame, "Inp", num_inputs, max_cmd_tx, app_ref.tx_checkboxes)
    
    logic_label_tx = ctk.CTkLabel(app_ref.tx_grid_frame, text="OR=On; AND=Off", font=ctk.CTkFont(size=11))
    logic_label_tx.grid(row=num_inputs + 1, column=0, padx=(5, 10), pady=5, sticky="e")
    for c in range(max_cmd_tx):
        checkbox = ctk.CTkCheckBox(app_ref.tx_grid_frame, text="", width=16)
        checkbox.grid(row=num_inputs + 1, column=c + 1, padx=2, pady=5)
        app_ref.tx_logic_checkboxes.append(checkbox)
        
    app_ref._build_grid(app_ref.rx_grid_frame, "Out", num_outputs, max_cmd_rx, app_ref.rx_checkboxes)
    
    logic_label_rx = ctk.CTkLabel(app_ref.rx_grid_frame, text="OR = On\nAND = Off", font=ctk.CTkFont(weight="bold", size=10))
    logic_label_rx.grid(row=0, column=max_cmd_rx + 1, padx=15, pady=2)
    for r in range(num_outputs):
        checkbox = ctk.CTkCheckBox(app_ref.rx_grid_frame, text="", width=16)
        checkbox.grid(row=r + 1, column=max_cmd_rx + 1, padx=15, pady=1)
        app_ref.rx_logic_checkboxes.append(checkbox)

        
        
    














# ************************** MODULE CONFIGS TAB **************************
# ibtu_bytones_subtab
def _populate_ibtu_bytones_tab(app_ref, tab_frame):
    """Populates the IBTU_ByTones configuration tab."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(0, weight=1) 

    scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Configuración de IBTU por Tonos")
    scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    scroll_frame.grid_columnconfigure(0, weight=1)
    
    general_frame = ctk.CTkFrame(scroll_frame)
    general_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    general_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(general_frame, text="General", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5,10), sticky="w")
    
    ctk.CTkLabel(general_frame, text="Reception operation mode:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    app_ref.ibtu_rx_op_mode = ctk.CTkComboBox(general_frame, values=list(app_ref.ibtu_rx_op_mode_map.keys()))
    app_ref.ibtu_rx_op_mode.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(general_frame, text="LOCAL Automatic Link Test Periodicity (h):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    app_ref.ibtu_local_periodicity = ctk.CTkEntry(general_frame, placeholder_text="0-24")
    app_ref.ibtu_local_periodicity.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
    ctk.CTkLabel(general_frame, text="REMOTE Automatic Link Test Periodicity (h):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    app_ref.ibtu_remote_periodicity = ctk.CTkEntry(general_frame, placeholder_text="0-24")
    app_ref.ibtu_remote_periodicity.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(general_frame, text="Activation Threshold for low Snr Ratio Alarm (dB):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    app_ref.ibtu_snr_activation = ctk.CTkEntry(general_frame, placeholder_text="0-18")
    app_ref.ibtu_snr_activation.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(general_frame, text="Deactivation Threshold for low Snr Ratio Alarm (dB):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    app_ref.ibtu_snr_deactivation = ctk.CTkEntry(general_frame, placeholder_text="2-20")
    app_ref.ibtu_snr_deactivation.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

    program_s1_button = ctk.CTkButton(general_frame, text="Programar Sección General", command=app_ref.equipment_controller._run_program_ibtu_s1_thread)
    program_s1_button.grid(row=6, column=0, columnspan=2, pady=10, padx=10)

    freq_frame = ctk.CTkFrame(scroll_frame)
    freq_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    freq_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(freq_frame, text="Frequencies", font=ctk.CTkFont(weight="bold")).pack(pady=(5,10))
    
    top_control_frame = ctk.CTkFrame(freq_frame)
    top_control_frame.pack(fill="x", padx=10, pady=10)
    retrieve_button = ctk.CTkButton(top_control_frame, text="Consultar Configuración IBTU", command=app_ref.equipment_controller._run_retrieve_ibtu_config_thread)
    retrieve_button.pack(pady=10, padx=10, fill="x")

    tx_rx_container = ctk.CTkFrame(freq_frame, fg_color="transparent")
    tx_rx_container.pack(fill="x", expand=True)
    tx_rx_container.grid_columnconfigure((0,1), weight=1)

    tx_frame = ctk.CTkFrame(tx_rx_container)
    tx_frame.grid(row=0, column=0, padx=(0,5), sticky="nsew")
    ctk.CTkLabel(tx_frame, text="TRANSMISSION", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    app_ref.ibtu_tx_tone_widgets = _create_tone_section(app_ref,tx_frame, is_tx=True)

    rx_frame = ctk.CTkFrame(tx_rx_container)
    rx_frame.grid(row=0, column=1, padx=(5,0), sticky="nsew")
    ctk.CTkLabel(rx_frame, text="RECEPTION", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    app_ref.ibtu_rx_tone_widgets = _create_tone_section(app_ref, rx_frame, is_tx=False)

    program_s2_button = ctk.CTkButton(freq_frame, text="Programar Frecuencias", command=app_ref.equipment_controller._run_program_ibtu_s2_thread)
    program_s2_button.pack(pady=10, padx=10)

    levels_frame = ctk.CTkFrame(scroll_frame)
    levels_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
    levels_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(levels_frame, text="Levels", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5,10), sticky="w")
    
    ctk.CTkLabel(levels_frame, text="Input Level (dBm):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    app_ref.ibtu_input_level = ctk.CTkEntry(levels_frame, placeholder_text="-40 a 0")
    app_ref.ibtu_input_level.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    
    ctk.CTkLabel(levels_frame, text="Power Boosting (dB):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    app_ref.ibtu_power_boosting = ctk.CTkEntry(levels_frame, placeholder_text="0 a 6")
    app_ref.ibtu_power_boosting.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(levels_frame, text="Output Level (dBm):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    app_ref.ibtu_output_level = ctk.CTkEntry(levels_frame, placeholder_text="-30 a 0")
    app_ref.ibtu_output_level.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    program_s3_button = ctk.CTkButton(levels_frame, text="Programar Niveles", command=app_ref.equipment_controller._run_program_ibtu_s3_thread)
    program_s3_button.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

def _create_tone_section(app_ref, parent, is_tx):
    """Helper to create the UI for TX or RX tone configuration with both scrollbars."""
    widgets = {}
    
    controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
    controls_frame.pack(fill="x", padx=5, pady=5)
    controls_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(controls_frame, text="Scheme:").grid(row=0, column=0, padx=(5,0), pady=5, sticky="w")
    widgets['scheme_combo'] = ctk.CTkComboBox(controls_frame, values=list(app_ref.ibtu_scheme_map.keys()))
    widgets['scheme_combo'].grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    ctk.CTkLabel(controls_frame, text="Guard Tone:").grid(row=1, column=0, padx=(5,0), pady=5, sticky="w")
    widgets['guard_combo'] = ctk.CTkComboBox(controls_frame, values=app_ref.all_ibtu_frequencies)
    widgets['guard_combo'].grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    button_frame = ctk.CTkFrame(parent, fg_color="transparent")
    button_frame.pack(fill="x", padx=5, pady=5)
    widgets['copy_button'] = ctk.CTkButton(button_frame, text="Copy")
    widgets['copy_button'].pack(side="left", padx=5)
    widgets['reset_button'] = ctk.CTkButton(button_frame, text="Reset")
    widgets['reset_button'].pack(side="left", padx=5)
    
    table_container = ctk.CTkFrame(parent)
    table_container.pack(fill="both", expand=True, padx=5, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=1)

    bg_color = table_container.cget("fg_color")
    if isinstance(bg_color, (list, tuple)):
        bg_color = bg_color[1] if ctk.get_appearance_mode() == "Dark" else bg_color[0]

    canvas = tk.Canvas(table_container, bg=bg_color, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    v_scrollbar = ctk.CTkScrollbar(table_container, orientation="vertical", command=canvas.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    
    h_scrollbar = ctk.CTkScrollbar(table_container, orientation="horizontal", command=canvas.xview)
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    table_frame = ctk.CTkFrame(canvas, fg_color="transparent")
    canvas.create_window((0, 0), window=table_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    table_frame.bind("<Configure>", on_frame_configure)
    
    widgets['table_frame'] = table_frame

    headers = ["Tone", "Command activated", "Command transmitted", "Application Type", "Frequency (Hz)"]
    for i, header in enumerate(headers):
        header_label = ctk.CTkLabel(table_frame, text=header, font=ctk.CTkFont(weight="bold"))
        header_label.grid(row=0, column=i, padx=10, pady=5)
        table_frame.grid_columnconfigure(i, minsize=140)

    return widgets


def _update_ibtu_tones_table(app_ref, tone_widgets, tone_data, is_tx):
    """Populates the tones table with data and stores the interactive widgets."""
    table_frame = tone_widgets['table_frame']
    
    for widget in table_frame.winfo_children():
        if widget.grid_info()['row'] > 0:
            widget.destroy()
    
    table_widgets_list = app_ref.ibtu_tx_table_widgets if is_tx else app_ref.ibtu_rx_table_widgets
    command_groups = app_ref.tx_command_groups if is_tx else app_ref.rx_command_groups
    table_widgets_list.clear()
    command_groups.clear()

    if not tone_data:
        ctk.CTkLabel(table_frame, text="No data retrieved.").grid(row=1, column=0, columnspan=5, pady=10)
        return

    for i, row_data in enumerate(tone_data):
        row = i + 1
        row_widgets = {}
        
        command_transmitted = str(row_data[2])
        row_widgets['command'] = command_transmitted
        
        ctk.CTkLabel(table_frame, text=row_data[0]).grid(row=row, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text=row_data[1]).grid(row=row, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text=command_transmitted).grid(row=row, column=2, padx=5, pady=2)
        
        app_type_combo = ctk.CTkComboBox(table_frame, values=list(app_ref.ibtu_app_type_map.keys()))
        app_type_combo.grid(row=row, column=3, padx=5, pady=2)
        row_widgets['app_type'] = app_type_combo
        
        freq_combo = ctk.CTkComboBox(table_frame, values=["..."])
        freq_combo.grid(row=row, column=4, padx=5, pady=2)
        row_widgets['freq'] = freq_combo

        table_widgets_list.append(row_widgets)

        if command_transmitted not in command_groups:
            command_groups[command_transmitted] = []
        command_groups[command_transmitted].append(row_widgets)

    for i, row_widgets in enumerate(table_widgets_list):
        app_type_combo = row_widgets['app_type']
        freq_combo = row_widgets['freq']
        
        app_type_combo.configure(command=lambda v, idx=i, tx=is_tx: _on_tone_setting_change(app_ref, v, idx, 'app_type', tx))
        freq_combo.configure(command=lambda v, idx=i, tx=is_tx: _on_tone_setting_change(app_ref, v, idx, 'freq', tx))

        row_data = tone_data[i]
        if len(row_data) >= 5:
            app_type_val = str(row_data[3])
            app_type_str = app_ref.ibtu_app_type_map_rev.get(app_type_val, "Blocking")
            app_type_combo.set(app_type_str)
            app_ref._update_frequency_options(app_type_str, freq_combo)
            freq_val = str(row_data[4])
            freq_combo.set(freq_val)
            
def _on_tone_setting_change(app_ref, new_value, row_index, widget_type, is_tx):
    """Callback to handle changes in app_type or frequency and synchronize linked rows."""
    table_widgets = app_ref.ibtu_tx_table_widgets if is_tx else app_ref.ibtu_rx_table_widgets
    command_groups = app_ref.tx_command_groups if is_tx else app_ref.rx_command_groups
    
    if row_index >= len(table_widgets):
        return

    source_row_widgets = table_widgets[row_index]
    command_key = source_row_widgets['command']
    linked_widgets = command_groups.get(command_key, [])

    for row in linked_widgets:
        if widget_type == 'app_type':
            row['app_type'].set(new_value)
            app_ref._update_frequency_options(new_value, row['freq'])
        elif widget_type == 'freq':
            row['freq'].set(new_value)
    
    if row_index == 0 and widget_type == 'app_type':
        guard_combo = app_ref.ibtu_tx_tone_widgets['guard_combo'] if is_tx else app_ref.ibtu_rx_tone_widgets['guard_combo']
        app_ref._update_guard_tone_options(new_value, guard_combo)
        
def _update_frequency_options(app_ref, selected_app_type, freq_combo):
    """Callback to update the frequency combobox based on the application type."""
    freq_list = app_ref.ibtu_freq_map.get(selected_app_type, [])
    current_freq = freq_combo.get()
    freq_combo.configure(values=freq_list)
    if current_freq not in freq_list:
        freq_combo.set(freq_list[0] if freq_list else "")
        
def _update_guard_tone_options(app_ref, selected_app_type, guard_combo):
    """Callback to update the guard tone combobox based on the first tone's application type."""
    freq_list = app_ref.ibtu_freq_map.get(selected_app_type, [])
    current_guard_freq = guard_combo.get()
    guard_combo.configure(values=freq_list)
    if current_guard_freq not in freq_list:
        guard_combo.set(freq_list[0] if freq_list else "")

    
# def _update_options_for_first_tone(app_ref, selected_app_type, guard_combo, freq_combo):
#     """A special callback for the first tone's app_type, updating both its own freq and the guard tone."""
#     _update_guard_tone_options(app_ref, selected_app_type, guard_combo)
#     _update_frequency_options(app_ref, selected_app_type, freq_combo)


def _update_ibtu_full_config_display(app_ref, listener):
    """Updates the entire IBTU ByTones tab with data from the listener object."""
    _update_ibtu_tones_table(app_ref, app_ref.ibtu_tx_tone_widgets, listener.ibtu_tx_tones, is_tx=True)
    _update_ibtu_tones_table(app_ref, app_ref.ibtu_rx_tone_widgets, listener.ibtu_rx_tones, is_tx=False)

    if listener.ibtu_tx_scheme is not None:
        scheme_text = app_ref.ibtu_scheme_map_rev.get(str(listener.ibtu_tx_scheme), "2+2 (1)")
        app_ref.ibtu_tx_tone_widgets['scheme_combo'].set(scheme_text)
    
    if app_ref.ibtu_tx_table_widgets:
        first_tone_app_type = app_ref.ibtu_tx_table_widgets[0]['app_type'].get()
        app_ref._update_guard_tone_options(first_tone_app_type, app_ref.ibtu_tx_tone_widgets['guard_combo'])

    if listener.ibtu_tx_guard_freq:
        app_ref.ibtu_tx_tone_widgets['guard_combo'].set(listener.ibtu_tx_guard_freq)

    if listener.ibtu_rx_scheme is not None:
        scheme_text = app_ref.ibtu_scheme_map_rev.get(str(listener.ibtu_rx_scheme), "2+2 (1)")
        app_ref.ibtu_rx_tone_widgets['scheme_combo'].set(scheme_text)

    if app_ref.ibtu_rx_table_widgets:
        first_tone_app_type = app_ref.ibtu_rx_table_widgets[0]['app_type'].get()
        app_ref._update_guard_tone_options(first_tone_app_type, app_ref.ibtu_rx_tone_widgets['guard_combo'])

    if listener.ibtu_rx_guard_freq:
        app_ref.ibtu_rx_tone_widgets['guard_combo'].set(listener.ibtu_rx_guard_freq)




# **************************** IBTU_FFT  *************************************
def _populate_ibtu_fft_tab(app_ref, tab_frame):
    """Populates the IBTU FFT configuration tab."""

    # Configurar grid para el tab_frame
    tab_frame.grid_columnconfigure(0, weight=1) # Columna 0 ocupa todo el ancho
    tab_frame.grid_rowconfigure(0, weight=1)    # Fila 0 (scroll_frame) ocupa casi todo el alto

    # *** Frame principal con scroll ***
    scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Configuración IBTU FFT")
    scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    scroll_frame.grid_columnconfigure(0, weight=1) # Para que el contenido dentro use el ancho

    # *** Creamos Sub-Frames para cada sección ***

    # Sección General
    general_frame = ctk.CTkFrame(scroll_frame)
    general_frame.pack(fill="x", padx=10, pady=10)
    general_frame.grid_columnconfigure(1, weight=1) # Columna de widgets ocupa espacio

    ctk.CTkLabel(general_frame, text="General Settings", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")

    # Periodicidades y Umbrales SNR (Ejemplos Estáticos)
    ctk.CTkLabel(general_frame, text="Local Periodicity (h):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    app_ref.fft_local_periodicity_entry = ctk.CTkEntry(general_frame, placeholder_text="0-24")
    app_ref.fft_local_periodicity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(general_frame, text="Remote Periodicity (h):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    app_ref.fft_remote_periodicity_entry = ctk.CTkEntry(general_frame, placeholder_text="0-24")
    app_ref.fft_remote_periodicity_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(general_frame, text="SNR Activation Thresh. (dB):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    app_ref.fft_snr_activation_entry = ctk.CTkEntry(general_frame, placeholder_text="0-17")
    app_ref.fft_snr_activation_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(general_frame, text="SNR Deactivation Thresh. (dB):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    app_ref.fft_snr_deactivation_entry = ctk.CTkEntry(general_frame, placeholder_text="3-20")
    app_ref.fft_snr_deactivation_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
    
    # ********************** OPERATION MODE ****************
    # Frame para Modos de Operación RX (Dinámico)
    app_ref.fft_rx_op_mode_frame = ctk.CTkFrame(general_frame, fg_color="transparent")
    app_ref.fft_rx_op_mode_frame.grid(row=5, column=0, columnspan=2, pady=(10, 5), sticky="ew")
    app_ref.fft_rx_op_mode_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(app_ref.fft_rx_op_mode_frame, text="Reception Operation Mode:").pack(anchor="w", padx=10)

    # Añadimos los Comboboxes y labels dinamicamente 
    app_ref.fft_rx_op_mode_combos.clear() # Limpiar lista por si se repopula. fft_rx_op_mode_combos será a traves de lo que accederemos para cambiar el contenido dinamicamente desde app.py
    MAX_COMMANDS = 8 # Asumir un máximo por ahora
    for i in range(MAX_COMMANDS):
        # Frame de la fila donde colocaremos el label el combo de cada comando que iteramos con el FOR 
        row_frame = ctk.CTkFrame(app_ref.fft_rx_op_mode_frame, fg_color="transparent")
        # Empaquetamos en lugar de usar grid aquí para que aparezcan uno debajo del otro
        row_frame.pack(fill="x", padx=10, pady=2)
        row_frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(row_frame, text=f"  Command {i+1}:", width=100)
        label.grid(row=0, column=0, sticky="w")
        combo = ctk.CTkComboBox(row_frame, values=list(app_ref.fft_rx_op_mode_map.keys())) # Los valores disponibles para seleccionar para operation mode los cogemos de la inicialización del mapeo de estas variables.
        combo.grid(row=0, column=1, sticky="ew")
        app_ref.fft_rx_op_mode_combos.append({"frame": row_frame, "label": label, "combo": combo}) #fft_rx_op_mode_combos será a traves de lo que accederemos para cambiar el contenido dinamicamente desde app.py
        row_frame.pack_forget() # Ocultar inicialmente
    
    
    
    # ****************** Sección Frequencies -> COLUMNAS TX Y RX ************
    frequencies_frame = ctk.CTkFrame(scroll_frame)
    frequencies_frame.pack(fill="x", padx=10, pady=10)
    frequencies_frame.grid_columnconfigure((0, 2), weight=1) # Columnas TX y RX (por eso ponemos (0,¡2!)
    frequencies_frame.grid_columnconfigure(1, weight=0)      # Columna botones Copy

    ctk.CTkLabel(frequencies_frame, text="Frequencies & Application Modes", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=(5, 10), sticky="w")


        # ********************** TX ****************
        # Sub-frame TX
    tx_freq_frame = ctk.CTkFrame(frequencies_frame)
    tx_freq_frame.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="nsew")
    tx_freq_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(tx_freq_frame, text="Transmission (TX)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="w")
    
        # WIDGETS TX

    ctk.CTkLabel(tx_freq_frame, text="Bandwidth:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    app_ref.fft_tx_bw_combo = ctk.CTkComboBox(tx_freq_frame, values=list(app_ref.fft_bw_map.keys()))    # 1kHz, 2kHz,4kHz. # Los valores disponibles para seleccionar los cogemos de la inicialización del mapeo de estas variables.
    app_ref.fft_tx_bw_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    ctk.CTkLabel(tx_freq_frame, text="Guard Freq (Hz):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    app_ref.fft_tx_guard_freq_entry = ctk.CTkEntry(tx_freq_frame, placeholder_text="e.g., 1100")
    app_ref.fft_tx_guard_freq_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    # TODO: Añadir botón para seleccionar frecuencia

    app_ref.fft_tx_app_mode_frame = ctk.CTkFrame(tx_freq_frame, fg_color="transparent")
    app_ref.fft_tx_app_mode_frame.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky="ew")
    ctk.CTkLabel(app_ref.fft_tx_app_mode_frame, text="Application Mode:").pack(anchor="w", padx=5)

        # *** Añadimos Comboboxes y Labels Dinámicos TX para el Modo de Aplicación ***
    app_ref.fft_tx_app_mode_combos.clear()
    for i in range(MAX_COMMANDS):
        row_frame = ctk.CTkFrame(app_ref.fft_tx_app_mode_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=5, pady=2)
        row_frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(row_frame, text=f"  Command {i+1}:", width=100)
        label.grid(row=0, column=0, sticky="w")
        combo = ctk.CTkComboBox(row_frame, values=list(app_ref.fft_app_mode_map.keys()))    # Los valores disponibles para seleccionar para application mode los cogemos de la inicialización del mapeo de estas variables.
        combo.grid(row=0, column=1, sticky="ew")
        
        app_ref.fft_tx_app_mode_combos.append({"frame": row_frame, "label": label, "combo": combo}) #fft_tx_app_mode_combos será a traves de lo que accederemos para cambiar el contenido dinamicamente desde app.py
        row_frame.pack_forget() # Ocultar inicialmente

    # **********************************************************************************************

    # Botones Copy
    copy_buttons_frame = ctk.CTkFrame(frequencies_frame, fg_color="transparent")
    copy_buttons_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ns")   # column=1 para que esté en medio
    # TODO: Añadir comandos a los botones Copy
    copy_rx_to_tx_button = ctk.CTkButton(copy_buttons_frame, text="RX -> TX", width=60) # command=...
    copy_rx_to_tx_button.pack(pady=10)
    copy_tx_to_rx_button = ctk.CTkButton(copy_buttons_frame, text="TX -> RX", width=60) # command=...
    copy_tx_to_rx_button.pack(pady=10)

    # **********************************************************************************************

        # ********************** RX ****************
        # Sub-frame RX
    rx_freq_frame = ctk.CTkFrame(frequencies_frame)
    rx_freq_frame.grid(row=1, column=2, padx=(5, 0), pady=5, sticky="nsew")
    rx_freq_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(rx_freq_frame, text="Reception (RX)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="w")

        # Widgets RX
    ctk.CTkLabel(rx_freq_frame, text="Bandwidth:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    app_ref.fft_rx_bw_combo = ctk.CTkComboBox(rx_freq_frame, values=list(app_ref.fft_bw_map.keys()))# Los valores disponibles para seleccionar el BW los cogemos de la inicialización del mapeo de esta variable.
    app_ref.fft_rx_bw_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    ctk.CTkLabel(rx_freq_frame, text="Guard Freq (Hz):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    app_ref.fft_rx_guard_freq_entry = ctk.CTkEntry(rx_freq_frame, placeholder_text="e.g., 1100")
    app_ref.fft_rx_guard_freq_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    # TODO: Añadir botón para seleccionar frecuencia

    app_ref.fft_rx_app_mode_frame = ctk.CTkFrame(rx_freq_frame, fg_color="transparent")
    app_ref.fft_rx_app_mode_frame.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky="ew")
    ctk.CTkLabel(app_ref.fft_rx_app_mode_frame, text="Application Mode:").pack(anchor="w", padx=5)

        # *** Añadimos Comboboxes y Labels Dinámicos RX para el Modo de Aplicación ***
    app_ref.fft_rx_app_mode_combos.clear()
    for i in range(MAX_COMMANDS):
        row_frame = ctk.CTkFrame(app_ref.fft_rx_app_mode_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=5, pady=2)
        row_frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(row_frame, text=f"  Command {i+1}:", width=100)
        label.grid(row=0, column=0, sticky="w")
        combo = ctk.CTkComboBox(row_frame, values=list(app_ref.fft_app_mode_map.keys()))      # Los valores disponibles para seleccionar para application mode los cogemos de la inicialización del mapeo de estas variables.      
        combo.grid(row=0, column=1, sticky="ew")
        
        app_ref.fft_rx_app_mode_combos.append({"frame": row_frame, "label": label, "combo": combo})    #fft_rx_app_mode_combos será a traves de lo que accederemos para cambiar el contenido dinamicamente desde app.py        
        row_frame.pack_forget() # Ocultar inicialmente
        
        
        
    # --- Sección Levels ---
    levels_frame = ctk.CTkFrame(scroll_frame)
    levels_frame.pack(fill="x", padx=10, pady=10)
    levels_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(levels_frame, text="Levels", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")

    # Input Level, Power Boosting, Output Level (Ejemplos Estáticos)
    ctk.CTkLabel(levels_frame, text="Input Level (dBm):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    app_ref.fft_input_level_entry = ctk.CTkEntry(levels_frame, placeholder_text="-40 a 0")
    app_ref.fft_input_level_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(levels_frame, text="Power Boosting (dB):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    app_ref.fft_power_boosting_entry = ctk.CTkEntry(levels_frame, placeholder_text="0 a 6")
    app_ref.fft_power_boosting_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(levels_frame, text="Output Level (dBm):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    app_ref.fft_output_level_entry = ctk.CTkEntry(levels_frame, placeholder_text="-30 a 0")
    app_ref.fft_output_level_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")


    # --- 3. Frame para botones (al final, fuera del scroll) ---
    buttons_frame = ctk.CTkFrame(tab_frame)
    buttons_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
    buttons_frame.grid_columnconfigure((0, 1), weight=1)

    app_ref.query_ibtu_fft_button = ctk.CTkButton(buttons_frame, text="Consultar Configuración IBTU FFT", command=app_ref.equipment_controller._run_retrieve_ibtu_fft_config_thread)
    app_ref.query_ibtu_fft_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    app_ref.program_ibtu_fft_button = ctk.CTkButton(buttons_frame, text="Programar Configuración IBTU FFT", command=app_ref.equipment_controller._run_program_ibtu_fft_thread) 
    app_ref.program_ibtu_fft_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    app_ref.query_ibtu_fft_button.configure(state="disabled")
    app_ref.program_ibtu_fft_button.configure(state="disabled")


def _update_ibtu_fft_config_display(app_ref, fft_config_data):  # fft_config_data espera un diccionairio .json
    """Updates the IBTU FFT configuration tab with data from the listener dictionary."""

    # --- Funciones auxiliares (helper) ---
    def set_entry(entry_widget, value): # Antes de actualizar los widgets, comprueba que existan y que el valor pasado no sea None
        if entry_widget and value is not None:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, str(value))

    def set_combobox(combo_widget, value_map_rev, value):   # Recordemos que a traves del mapeo de variables ..._rev podiamos convertir los numeros que nos pasa el listener a texto para ser leido desde la GUI.
        if combo_widget and value is not None:
            # Busca el texto correspondiente al valor numérico en el diccionario de variables _rev
            display_text = value_map_rev.get(str(value))
            if display_text:
                combo_widget.set(display_text)  # Si ha sido posible obtener texto del mapeo a traves del diccionario de variables _rev, actualizamos el widget.
            else:
                # Si no se encuentra, muestra el valor crudo (o un placeholder)
                combo_widget.set(str(value)) # O podrías poner combo_widget.set("")

    # *** Actualizar Sección General *** Pasamos el widget en el que queremos escribir y los datos que nos pasan por argumento "fft_config_data" -> Recordemos que es un diccionario, y lo que nos interesa el valor de cada una de las claves que pasamos a traves del .get 
    set_entry(app_ref.fft_local_periodicity_entry, fft_config_data.get('local_periodicity'))    # Para poder actualizar las entradas, usamos set_entry. 1er param: le pasamos la entrada existente en la GUI que queremos actualizar con el 2o param, que es un diccionario con todos los datos.
    set_entry(app_ref.fft_remote_periodicity_entry, fft_config_data.get('remote_periodicity'))
    set_entry(app_ref.fft_snr_activation_entry, fft_config_data.get('snr_activation'))
    set_entry(app_ref.fft_snr_deactivation_entry, fft_config_data.get('snr_deactivation'))

    # Actualizar Modos Operación RX (Dinámico)
    rx_op_mode_list = fft_config_data.get('rx_op_mode_list', [])    # Esto es lo que nos llega del listener. Nos quedamos con la lista de config de los modos de operacion
    num_rx_commands = len(rx_op_mode_list)
    for i, widget_dict in enumerate(app_ref.fft_rx_op_mode_combos): # CUIDADO! Aqui recorremos los combos y frames QUE YA HAY DISPUESTOS EN LA GUI (Y QUE QUEREMOS ACTUALIZAR CON LOS QUE NOS HAN PASADO Y TENEMOS GUARDADOS EN rx_op_mode_list
        frame = widget_dict['frame']     
        combo = widget_dict['combo']
        if i < num_rx_commands:
            set_combobox(combo, app_ref.fft_rx_op_mode_map_rev, rx_op_mode_list[i]) # 1er param: el combo que queremos actualizar y que estamos recorriendo. 2o param:la función set_combobox necesita del diccionario de mapeo para actualizar los combobox. 3er param: El valor que estemos iterando de la lista de valores que nos ha llegado del listener.
            # El frame para este comando debe ser visible
            frame.pack(fill="x", padx=10, pady=2) 
        else:
            # Ocultamos los frames de comandos que no existen
            frame.pack_forget()

    # *** Actualizar Sección Frequencies ***
    # TX
    set_combobox(app_ref.fft_tx_bw_combo, app_ref.fft_bw_map_rev, fft_config_data.get('tx_bw'))
    set_entry(app_ref.fft_tx_guard_freq_entry, fft_config_data.get('tx_guard_freq'))

        # Modos de aplicación para TX
    tx_app_mode_list = fft_config_data.get('tx_app_mode_list', [])
    num_tx_commands = len(tx_app_mode_list) # Usar longitud real de datos TX
    for i, widget_dict in enumerate(app_ref.fft_tx_app_mode_combos):
        frame = widget_dict['frame']
        combo = widget_dict['combo']
        if i < num_tx_commands:
            set_combobox(combo, app_ref.fft_app_mode_map_rev, tx_app_mode_list[i])
            frame.pack(fill="x", padx=5, pady=2) 
        else:
            frame.pack_forget()

    # RX
    set_combobox(app_ref.fft_rx_bw_combo, app_ref.fft_bw_map_rev, fft_config_data.get('rx_bw'))
    set_entry(app_ref.fft_rx_guard_freq_entry, fft_config_data.get('rx_guard_freq'))

    rx_app_mode_list = fft_config_data.get('rx_app_mode_list', [])
    
        # Modos de aplicación para TX
    # Reutilizamos num_rx_commands calculado antes
    for i, widget_dict in enumerate(app_ref.fft_rx_app_mode_combos):
        frame = widget_dict['frame']
        combo = widget_dict['combo']
        if i < num_rx_commands: # Basado en el número de comandos RX
            set_combobox(combo, app_ref.fft_app_mode_map_rev, rx_app_mode_list[i])
            frame.pack(fill="x", padx=5, pady=2) 
        else:
            frame.pack_forget()

    # --- 3. Actualizar Sección Levels ---
    set_entry(app_ref.fft_input_level_entry, fft_config_data.get('input_level'))
    set_entry(app_ref.fft_power_boosting_entry, fft_config_data.get('power_boosting'))
    set_entry(app_ref.fft_output_level_entry, fft_config_data.get('output_level'))