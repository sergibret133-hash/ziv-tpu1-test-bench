import customtkinter as ctk
import json
import os

def create_monitoring_tab(app_ref):
    """Crea y devuelve el CTkTabView completo para la sección 'MONITORING'."""
    
    # 1. Crear el contenedor de pestañas
    tab_view = ctk.CTkTabview(app_ref, corner_radius=8)
    tab_view.add("SNMP")
    tab_view.add("Chronological Register")
    tab_view.add("Historial de Traps (BD)")
    tab_view.add("Correlación de Eventos")
    tab_view.add("Informe Verificación")
    
    # 2. Delegar el rellenado de cada sub-pestaña a su función correspondiente
    _populate_snmp_tab(app_ref, tab_view.tab("SNMP"))
    _populate_chrono_register_tab(app_ref, tab_view.tab("Chronological Register"))
    _populate_db_viewer_tab(app_ref, tab_view.tab("Historial de Traps (BD)"))
    _populate_event_correlation_tab(app_ref, tab_view.tab("Correlación de Eventos"))
    _populate_verification_report_tab(app_ref, tab_view.tab("Informe Verificación"))
    
    # 3. Devolver el TabView ya construido y rellenado
    return tab_view

# ****** SNMP TAB ******
def _populate_snmp_tab(app_ref, tab_frame):
    """Populates the SNMP tab with its sub-tabs."""
    snmp_tab_view = app_ref._create_tab_view(tab_frame, ["Receptor de Traps", "Diccionario de Traps", "Configuración SNMP"])
    snmp_tab_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    _populate_snmp_receiver_tab(app_ref, snmp_tab_view.tab("Receptor de Traps"))
    _populate_snmp_dictionary_tab(app_ref, snmp_tab_view.tab("Diccionario de Traps"))
    _populate_snmp_config_tab(app_ref, snmp_tab_view.tab("Configuración SNMP"))
    

    



def _populate_snmp_receiver_tab(app_ref, tab_frame):
    """Populates the SNMP Receiver sub-tab with its widgets."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(1, weight=1)

    config_frame = ctk.CTkFrame(tab_frame)
    config_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
    config_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(config_frame, text="Dirección IP del Listener:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    ip_line_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
    ip_line_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    ip_line_frame.grid_columnconfigure(0, weight=1)
    
    app_ref.snmp_ip_entry = ctk.CTkEntry(ip_line_frame, placeholder_text="0.0.0.0")
    app_ref.snmp_ip_entry.grid(row=0, column=0, sticky="ew")
    
    app_ref.copy_ip_button = ctk.CTkButton(ip_line_frame, text="Usar IP Local", command=app_ref._set_local_ip, width=100)
    app_ref.copy_ip_button.grid(row=0, column=1, padx=(10, 0))

    ctk.CTkLabel(config_frame, text="Puerto del Listener:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    app_ref.snmp_port_entry = ctk.CTkEntry(config_frame, placeholder_text="171")
    app_ref.snmp_port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    app_ref.snmp_port_entry.insert(0, "171")
    
    app_ref.start_listener_button = ctk.CTkButton(config_frame, text="Iniciar Listener", command=app_ref.trap_listener_controller._start_snmp_listener_thread)
    app_ref.start_listener_button.grid(row=3, column=0, pady=10, padx=5, sticky="ew")

    app_ref.stop_listener_button = ctk.CTkButton(config_frame, text="Detener Listener", command=app_ref.trap_listener_controller._stop_snmp_listener_thread)
    app_ref.stop_listener_button.grid(row=3, column=1, pady=10, padx=5, sticky="ew")

    app_ref.snmp_listener_status_label = ctk.CTkLabel(config_frame, text="Listener: Detenido", text_color="red")
    app_ref.snmp_listener_status_label.grid(row=4, column=0, columnspan=2, pady=(0, 5))

    app_ref.trap_display = ctk.CTkTextbox(tab_frame, state="disabled")
    app_ref.trap_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    controls_frame = ctk.CTkFrame(tab_frame)
    controls_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
    controls_frame.grid_columnconfigure((0,1,2), weight=1)

    app_ref.show_all_traps_button = ctk.CTkButton(controls_frame, text="Refrescar Traps", command=app_ref.trap_listener_controller._show_all_traps)
    app_ref.show_all_traps_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
    filter_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    filter_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    app_ref.snmp_filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="Filtrar por texto...")
    app_ref.snmp_filter_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
    app_ref.filter_traps_button = ctk.CTkButton(filter_frame, text="Filtrar", width=60, command=app_ref.trap_listener_controller._filter_traps)
    app_ref.filter_traps_button.pack(side="left")

    app_ref.reset_traps_button = ctk.CTkButton(controls_frame, text="Borrar Traps Almacenados", command=app_ref.trap_listener_controller._reset_traps)
    app_ref.reset_traps_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
    
def _update_trap_display(app_ref, trap_list):
    """Thread-safe function to update the trap display from a list of trap dicts."""
    app_ref.trap_display.configure(state="normal")
    app_ref.trap_display.delete("1.0", "end")
    if not trap_list:
        app_ref.trap_display.insert("1.0", "No hay traps para mostrar.")
    else:
        formatted_text = ""
        for i, trap in enumerate(trap_list):
            formatted_text += f"--- Trap #{i+1} ---\n"
            for key, value in trap.items():
                if key == 'varbinds_dict':
                    formatted_text += f"  {key}:\n"
                    for vk, vv in value.items():
                        formatted_text += f"    {vk}: {vv}\n"
                else:
                    formatted_text += f"  {key}: {value}\n"
            formatted_text += "\n"
        app_ref.trap_display.insert("1.0", formatted_text)
    app_ref.trap_display.configure(state="disabled")
       
    
# ****** DICCIONARIO DE TRAPS ******
def _populate_snmp_dictionary_tab(app_ref, tab_frame):
    """Populates the SNMP Trap Dictionary sub-tab."""
    label = ctk.CTkLabel(tab_frame, text="Diccionario de Traps SNMP", font=ctk.CTkFont(size=16, weight="bold"))
    label.pack(pady=10)

    scroll_frame = ctk.CTkScrollableFrame(tab_frame)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    trap_dictionary = {
        "tpu1cNotifyConfigModification": "Notificación de modificación de configuración.",
        "tpu1cNotifyModuleError": "Notificación de error en un módulo.",
        "tpu1cNotifyReceiverBlocked": "Notificación de bloqueo del receptor.",
        "tpu1cNotifySyncLoss": "Notificación de pérdida de sincronismo.",
        "tpu1cNotifyIPLinkFault": "Notificación de fallo en el enlace IP.",
        "tpu1NotifyIpSyncLoss": "Notificación de pérdida de sincronismo IP.",
        "tpu1cNotifyIpTxTrans": "Notificación de transición en la transmisión IP.",
        "tpu1cNotifyMeanTranferDelay": "Notificación de retardo medio de transferencia.",
        "tpu1cNotifyFrameDelayVariation": "Notificación de variación en el retardo de trama (Jitter).",
        "tpu1cNotifyFrameLossRatio": "Notificación de ratio de pérdida de tramas.",
        "tpu1cNotifyGenRemAlarm": "Notificación de alarma remota general.",
        "tpu1cNotifyOutputCircuits": "Notificación de cambio de estado en los circuitos de salida.",
        "tpu1cNotifyInputCircuits": "Notificación de cambio de estado en los circuitos de entrada.",
        "tpu1cNotifyCommandTx": "Notificación de transmisión de un comando.",
        "tpu1cNotifyCommandRx": "Notificación de recepción de un comando."
    }
    
    for name, desc in trap_dictionary.items():
        _create_dictionary_entry(app_ref, scroll_frame, name, desc)

def _create_dictionary_entry(app_ref, parent, name, description):
    """Creates a single entry for the trap dictionary display."""
    entry_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20"))
    entry_frame.pack(fill="x", pady=4, padx=5)
    entry_frame.grid_columnconfigure(0, weight=1)
    
    name_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
    name_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5,0))
    name_frame.grid_columnconfigure(0, weight=1)

    name_label = ctk.CTkLabel(name_frame, text=name, font=ctk.CTkFont(weight="bold"))
    name_label.grid(row=0, column=0, sticky="w")
    
    copy_button = ctk.CTkButton(name_frame, text="Copiar", width=50, command=lambda n=name: app_ref.copy_to_clipboard(n))
    copy_button.grid(row=0, column=1, sticky="e", padx=(10,0))

    desc_label = ctk.CTkLabel(entry_frame, text=description, wraplength=600, justify="left", anchor="w")
    desc_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,5))



# ********** Chronological Register Tab **********
def _populate_chrono_register_tab(app_ref, tab_frame):
    """Populates the Chronological Register tab."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(2, weight=1)

    controls_frame = ctk.CTkFrame(tab_frame)
    controls_frame.grid(row=0, column=0, padx=20, pady=(10,0), sticky="ew")
    controls_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(controls_frame, text="Número de Entradas:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    app_ref.num_entries_entry = ctk.CTkEntry(controls_frame, placeholder_text="Ej: 10")
    app_ref.num_entries_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(controls_frame, text="Filtro de Evento/Alarma:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    app_ref.event_filter_entry = ctk.CTkEntry(controls_frame, placeholder_text="Opcional")
    app_ref.event_filter_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    
    ctk.CTkLabel(controls_frame, text="Orden:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    app_ref.chrono_order_combobox = ctk.CTkComboBox(controls_frame, values=["Ascendente", "Descendente"])
    app_ref.chrono_order_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    app_ref.chrono_order_combobox.set("Ascendente")

    action_buttons_frame = ctk.CTkFrame(tab_frame)
    action_buttons_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    action_buttons_frame.grid_columnconfigure((0,1), weight=1)

    app_ref.capture_last_entries_button = ctk.CTkButton(action_buttons_frame, text="Capturar Entradas", command=app_ref.monitoring_controller._run_capture_last_entries_thread)
    app_ref.capture_last_entries_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
    app_ref.clear_chrono_button = ctk.CTkButton(action_buttons_frame, text="Limpiar Registro", command=app_ref.monitoring_controller._run_clear_chrono_log_thread)
    app_ref.clear_chrono_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    app_ref.chrono_log_display = ctk.CTkTextbox(tab_frame, state="disabled", wrap="none")
    app_ref.chrono_log_display.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
    
    
    
def _update_chrono_log_display(app_ref, log_content):
    """Updates the chronological register display."""
    app_ref.chrono_log_display.configure(state="normal")
    app_ref.chrono_log_display.delete("1.0", "end")

    if isinstance(log_content, list) and log_content:
        formatted_lines = []
        for entry in log_content:
            ts = entry.get('timestamp', 'N/A')
            event = entry.get('alarm_event', 'N/A')
            formatted_lines.append(f"Timestamp: {ts} | Evento: {event}")
        log_text = "\n".join(formatted_lines)
        app_ref.chrono_log_display.insert("1.0", log_text)
    elif isinstance(log_content, str) and log_content:
        app_ref.chrono_log_display.insert("1.0", log_content)
    else:
        app_ref.chrono_log_display.insert("1.0", "No se recuperaron entradas del registro o está vacío.")

    app_ref.chrono_log_display.configure(state="disabled")

# ********** SNMP CONFIG TAB **********
def _populate_snmp_config_tab(app_ref, tab_frame):
    """Populates the new SNMP Configuration sub-tab with all its widgets."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(0, weight=1)

    scroll_frame = ctk.CTkScrollableFrame(tab_frame, label_text="Configuración General SNMP")
    scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    scroll_frame.grid_columnconfigure(0, weight=1)

    agent_frame = ctk.CTkFrame(scroll_frame)
    agent_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    app_ref.snmp_agent_state_cb = ctk.CTkCheckBox(agent_frame, text="Enable SNMP Agent", font=ctk.CTkFont(weight="bold"), command=lambda: _toggle_snmp_config_visibility(app_ref))
    app_ref.snmp_agent_state_cb.grid(row=0, column=0, padx=10, pady=10)

    app_ref.snmp_settings_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    app_ref.snmp_settings_container.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
    app_ref.snmp_settings_container.grid_columnconfigure(0, weight=1)

    general_settings_frame = ctk.CTkFrame(app_ref.snmp_settings_container)
    general_settings_frame.grid(row=0, column=0, pady=5, sticky="ew")
    general_settings_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(general_settings_frame, text="Traps Enable:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    app_ref.traps_enable_state_cb = ctk.CTkCheckBox(general_settings_frame, text="")
    app_ref.traps_enable_state_cb.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    ctk.CTkLabel(general_settings_frame, text="TPU SNMP Port:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    app_ref.tpu_snmp_port_entry = ctk.CTkEntry(general_settings_frame)
    app_ref.tpu_snmp_port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    v1_v2_frame = ctk.CTkFrame(app_ref.snmp_settings_container)
    v1_v2_frame.grid(row=1, column=0, pady=5, sticky="ew")
    app_ref.snmp_v1_v2_enable_cb = ctk.CTkCheckBox(v1_v2_frame, text="Enable SNMP v1/v2", command=lambda: _toggle_snmp_config_visibility(app_ref))
    app_ref.snmp_v1_v2_enable_cb.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
    
    app_ref.snmp_v1_v2_settings_frame = ctk.CTkFrame(v1_v2_frame, fg_color="transparent")
    app_ref.snmp_v1_v2_settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20)
    app_ref.snmp_v1_v2_settings_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(app_ref.snmp_v1_v2_settings_frame, text="Read Community:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    app_ref.snmp_v1_v2_read_entry = ctk.CTkEntry(app_ref.snmp_v1_v2_settings_frame)
    app_ref.snmp_v1_v2_read_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    ctk.CTkLabel(app_ref.snmp_v1_v2_settings_frame, text="Write Community:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    app_ref.snmp_v1_v2_set_entry = ctk.CTkEntry(app_ref.snmp_v1_v2_settings_frame)
    app_ref.snmp_v1_v2_set_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    v3_frame = ctk.CTkFrame(app_ref.snmp_settings_container)
    v3_frame.grid(row=2, column=0, pady=5, sticky="ew")
    app_ref.snmp_v3_enable_cb = ctk.CTkCheckBox(v3_frame, text="Enable SNMP v3", command=lambda: _toggle_snmp_config_visibility(app_ref))
    app_ref.snmp_v3_enable_cb.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    app_ref.snmp_v3_settings_frame = ctk.CTkFrame(v3_frame, fg_color="transparent")
    app_ref.snmp_v3_settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20)
    app_ref.snmp_v3_settings_frame.grid_columnconfigure((1, 3), weight=1)
    
    ctk.CTkLabel(app_ref.snmp_v3_settings_frame, text="Read User:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    app_ref.snmp_v3_read_user_entry = ctk.CTkEntry(app_ref.snmp_v3_settings_frame)
    app_ref.snmp_v3_read_user_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    ctk.CTkLabel(app_ref.snmp_v3_settings_frame, text="Password:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    app_ref.snmp_v3_read_pass_entry = ctk.CTkEntry(app_ref.snmp_v3_settings_frame, show="*")
    app_ref.snmp_v3_read_pass_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
    ctk.CTkLabel(app_ref.snmp_v3_settings_frame, text="Auth Protocol:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    app_ref.snmp_v3_read_auth_entry = ctk.CTkEntry(app_ref.snmp_v3_settings_frame)
    app_ref.snmp_v3_read_auth_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    
    ctk.CTkLabel(app_ref.snmp_v3_settings_frame, text="Write User:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    app_ref.snmp_v3_write_user_entry = ctk.CTkEntry(app_ref.snmp_v3_settings_frame)
    app_ref.snmp_v3_write_user_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    ctk.CTkLabel(app_ref.snmp_v3_settings_frame, text="Password:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
    app_ref.snmp_v3_write_pass_entry = ctk.CTkEntry(app_ref.snmp_v3_settings_frame, show="*")
    app_ref.snmp_v3_write_pass_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
    ctk.CTkLabel(app_ref.snmp_v3_settings_frame, text="Auth Protocol:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    app_ref.snmp_v3_write_auth_entry = ctk.CTkEntry(app_ref.snmp_v3_settings_frame)
    app_ref.snmp_v3_write_auth_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    hosts_main_frame = ctk.CTkFrame(app_ref.snmp_settings_container)
    hosts_main_frame.grid(row=3, column=0, pady=10, sticky="ew")
    hosts_main_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(hosts_main_frame, text="Notification Handling", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(5,10), sticky="w")

    hosts_grid_frame = ctk.CTkFrame(hosts_main_frame, fg_color="transparent")
    hosts_grid_frame.grid(row=1, column=0, sticky="ew", padx=5)
    hosts_grid_frame.grid_columnconfigure(2, weight=1)

    ctk.CTkLabel(hosts_grid_frame, text="Host", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
    ctk.CTkLabel(hosts_grid_frame, text="Enable", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5)
    ctk.CTkLabel(hosts_grid_frame, text="IP Addr.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5)
    ctk.CTkLabel(hosts_grid_frame, text="Port", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5)
    ctk.CTkLabel(hosts_grid_frame, text="Trap Mode", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5)

    app_ref.host_widgets.clear()
    for i in range(5):
        ctk.CTkLabel(hosts_grid_frame, text=str(i+1)).grid(row=i+1, column=0)
        
        enable_cb = ctk.CTkCheckBox(hosts_grid_frame, text="")
        enable_cb.grid(row=i+1, column=1, padx=5)
        
        ip_entry = ctk.CTkEntry(hosts_grid_frame, placeholder_text="0.0.0.0")
        ip_entry.grid(row=i+1, column=2, padx=5, sticky="ew")
        
        port_entry = ctk.CTkEntry(hosts_grid_frame, width=60)
        port_entry.grid(row=i+1, column=3, padx=5)
        
        trap_mode_cb = ctk.CTkComboBox(hosts_grid_frame, values=list(app_ref.trap_mode_map.keys()), width=140)
        trap_mode_cb.grid(row=i+1, column=4, padx=5)
        
        app_ref.host_widgets.append({'enable': enable_cb, 'ip': ip_entry, 'port': port_entry, 'mode': trap_mode_cb})

    buttons_frame = ctk.CTkFrame(tab_frame)
    buttons_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    buttons_frame.grid_columnconfigure((0,1), weight=1)

    app_ref.query_snmp_config_button = ctk.CTkButton(buttons_frame, text="Consultar Configuración SNMP", command=app_ref.snmp_controller._run_retrieve_snmp_config_thread)
    app_ref.query_snmp_config_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    app_ref.program_snmp_config_button = ctk.CTkButton(buttons_frame, text="Programar Configuración SNMP", command=app_ref.snmp_controller._run_execute_snmp_config_thread)
    app_ref.program_snmp_config_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    
    log_button = ctk.CTkButton(tab_frame, text="📂 Open Last Report (log.html)", state="disabled", command=app_ref._open_log_file)
    log_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
    app_ref.log_buttons.append(log_button)

    _toggle_snmp_config_visibility(app_ref)
    
def _update_full_snmp_config_display(app_ref, listener):
    """Updates the entire SNMP configuration tab with data from the listener object."""

    def set_entry(entry, value):
        # Nos aseguramos de que el widget existe antes de usarlo
        if not hasattr(app_ref, entry.winfo_name()): return
        entry.delete(0, "end")
        if value is not None:
            entry.insert(0, str(value))

    
    def set_checkbox(cb, value):
        if not hasattr(app_ref, cb.winfo_name()): return    # Si no existe, salimos de la función
        cb.deselect() # Deseleccionamos por defecto
        if value is not None:
            if value in [True, 'True', 'true', '1', 1]:
                cb.select()
    def set_combobox(combo, value_map_rev, value):
         # Asegurarse de que el widget existe antes de usarlo
        if not hasattr(app_ref, combo.winfo_name()): return
        combo.set("") # Valor vacío por defecto
        if value is not None:
            display_text = value_map_rev.get(str(value))
            if display_text:
                combo.set(display_text)    
                
    print(f"DEBUG SNMP: entrando a _update_full_snmp_config_display. listener es: {repr(listener)}")
    
    
    
    if listener is None:
        print("DEBUG SNMP: listener ES None. Limpiando UI...")
        set_checkbox(app_ref.snmp_agent_state_cb, None)
        set_checkbox(app_ref.traps_enable_state_cb, None)
        set_entry(app_ref.tpu_snmp_port_entry, None)
        set_checkbox(app_ref.snmp_v1_v2_enable_cb, None)
        set_entry(app_ref.snmp_v1_v2_read_entry, None)
        set_entry(app_ref.snmp_v1_v2_set_entry, None)
        set_checkbox(app_ref.snmp_v3_enable_cb, None)
        set_entry(app_ref.snmp_v3_read_user_entry, None)
        set_entry(app_ref.snmp_v3_read_pass_entry, None)
        set_entry(app_ref.snmp_v3_read_auth_entry, None)
        set_entry(app_ref.snmp_v3_write_user_entry, None)
        set_entry(app_ref.snmp_v3_write_pass_entry, None)
        set_entry(app_ref.snmp_v3_write_auth_entry, None)

        # Limpiar la tabla de hosts
        if hasattr(app_ref, 'host_widgets'):
            for widgets in app_ref.host_widgets:
                set_checkbox(widgets['enable'], None)
                set_entry(widgets['ip'], None)
                set_entry(widgets['port'], None)
                widgets['mode'].set("") # O el valor por defecto

        _toggle_snmp_config_visibility(app_ref) # Actualizar visibilidad basada en checkboxes limpios
        print("DEBUG SNMP: UI limpiada. Saliendo con return.")
        return # Salimos
    
    print(f"DEBUG SNMP: listener NO es None. Procediendo a actualizar widgets...")
                  
    set_checkbox(app_ref.snmp_agent_state_cb, listener.snmp_agent_state)
    set_checkbox(app_ref.traps_enable_state_cb, listener.traps_enable_state)
    set_entry(app_ref.tpu_snmp_port_entry, listener.tpu_snmp_port)
    set_checkbox(app_ref.snmp_v1_v2_enable_cb, listener.snmp_v1_v2_enable)
    set_entry(app_ref.snmp_v1_v2_read_entry, listener.snmp_v1_v2_read)
    set_entry(app_ref.snmp_v1_v2_set_entry, listener.snmp_v1_v2_set)
    set_checkbox(app_ref.snmp_v3_enable_cb, listener.snmp_v3_enable)
    set_entry(app_ref.snmp_v3_read_user_entry, listener.snmp_v3_read_user)
    set_entry(app_ref.snmp_v3_read_pass_entry, listener.snmp_v3_read_pass)
    set_entry(app_ref.snmp_v3_read_auth_entry, listener.snmp_v3_read_auth)
    set_entry(app_ref.snmp_v3_write_user_entry, listener.snmp_v3_write_user)
    set_entry(app_ref.snmp_v3_write_pass_entry, listener.snmp_v3_write_pass)
    set_entry(app_ref.snmp_v3_write_auth_entry, listener.snmp_v3_write_auth)

    # Actualizar tabla de hosts (con comprobación por si listener.hosts_config es None)
    if hasattr(app_ref, 'host_widgets') and listener.hosts_config and isinstance(listener.hosts_config, list):
        for i, host_data in enumerate(listener.hosts_config):
            if i < len(app_ref.host_widgets):
                widgets = app_ref.host_widgets[i]
                if len(host_data) == 4:
                    set_checkbox(widgets['enable'], host_data[0] == '1')
                    set_entry(widgets['ip'], host_data[1])
                    set_entry(widgets['port'], host_data[2])
                    set_combobox(widgets['mode'], app_ref.trap_mode_map_rev, host_data[3])
    elif hasattr(app_ref, 'host_widgets'):
         # Si listener.hosts_config es None o no es lista, limpiar tabla
         for widgets in app_ref.host_widgets:
                set_checkbox(widgets['enable'], None)
                set_entry(widgets['ip'], None)
                set_entry(widgets['port'], None)
                widgets['mode'].set("")


    _toggle_snmp_config_visibility(app_ref)

    
def _toggle_snmp_config_visibility(app_ref):
    """Shows or hides sections based on the state of the master checkboxes."""
    if app_ref.snmp_agent_state_cb.get() == 1:
        app_ref.snmp_settings_container.grid()
    else:
        app_ref.snmp_settings_container.grid_remove()
        return

    if app_ref.snmp_v1_v2_enable_cb.get() == 1:
        app_ref.snmp_v1_v2_settings_frame.grid()
    else:
        app_ref.snmp_v1_v2_settings_frame.grid_remove()

    if app_ref.snmp_v3_enable_cb.get() == 1:
        app_ref.snmp_v3_settings_frame.grid()
    else:
        app_ref.snmp_v3_settings_frame.grid_remove()

def _update_snmp_listener_status(app_ref, text, color):
    app_ref.snmp_listener_status_label.configure(text=text, text_color=color)


# ********** DB Viewer Tab **********

def _populate_db_viewer_tab(app_ref, tab_frame):
    """Crea los widgets para el visor de la base de datos de traps."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(2, weight=1)

    controls_frame = ctk.CTkFrame(tab_frame)
    controls_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

    # *********************** YA NO UTILIZAMOS BOTON DE REFRESCO. ABRIMOS ARCHIVOS DE BDs ***********************
    # refresh_button = ctk.CTkButton(controls_frame, text="Refrescar Datos de la Base de Datos", command=app_ref._load_traps_from_db)
    # refresh_button.pack(pady=10, padx=10, fill="x")
    # ***********************************************************************************************************
    
    # Botón para cargar un archivo de base de datos específico
    load_button = ctk.CTkButton(controls_frame, text="Cargar Archivo de Historial (.db)...", command=app_ref.monitoring_controller._load_traps_from_file)
    load_button.pack(pady=10, padx=10, fill="x")

    # Nueva etiqueta para mostrar el archivo actual
    app_ref.db_viewer_file_label = ctk.CTkLabel(tab_frame, text="Ningún archivo cargado.", font=ctk.CTkFont(size=12, slant="italic"))
    app_ref.db_viewer_file_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
    
    # Campo de texto para mostrar los traps cargados desde la base de datos
    app_ref.db_display_textbox = ctk.CTkTextbox(tab_frame, state="disabled", wrap="none")
    app_ref.db_display_textbox.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")


# ********** SNMPvsChrono_Correlation_Display **********

def _populate_event_correlation_tab(app_ref, tab_frame):
    """Crea los widgets para la función de análisis de correlación de datos provenientes de SNMP y el Registro Cronológico."""

    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(1, weight=1)

    controls_frame = ctk.CTkFrame(tab_frame)
    controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    # Guardamos la referencia del botón en app_ref para poder deshabilitarlo
    app_ref.correlation_button = ctk.CTkButton(
        controls_frame, 
        text="▶️ Iniciar Test de Correlación (Activar Entrada 1)", 
        command=app_ref.monitoring_controller.start_correlation_test
    )
    app_ref.correlation_button.pack(fill="x", padx=5, pady=5)

    # *** Frame de Resultados (Visores) ***
    results_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
    results_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    results_frame.grid_columnconfigure((0, 1), weight=1)
    results_frame.grid_rowconfigure(1, weight=1)

    # Columna para el Registro Cronológico
    ctk.CTkLabel(results_frame, text="Registro Cronológico", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
    app_ref.corr_chrono_textbox = ctk.CTkTextbox(results_frame, state="disabled", wrap="word")
    app_ref.corr_chrono_textbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    # Columna para los Traps SNMP
    ctk.CTkLabel(results_frame, text="Traps SNMP Recibidos", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5)
    app_ref.corr_snmp_textbox = ctk.CTkTextbox(results_frame, state="disabled", wrap="word")
    app_ref.corr_snmp_textbox.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    # *** Veredicto Final ***
    app_ref.corr_result_label = ctk.CTkLabel(results_frame, text="Resultado: PENDIENTE", font=ctk.CTkFont(size=16, weight="bold"), text_color="gray")
    app_ref.corr_result_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    
def _update_correlation_display(app_ref, chrono_report, trap_report, result, color):
    """Actualiza la GUI de Correlación de Eventos con los resultados del test."""
    
    # 1. Actualizar la etiqueta de Veredicto
    app_ref.corr_result_label.configure(text=f"Resultado: {result}", text_color=color)

    # 2. Actualizar TextBox de Cronológico
    app_ref.corr_chrono_textbox.configure(state="normal")
    app_ref.corr_chrono_textbox.delete("1.0", "end")
    app_ref.corr_chrono_textbox.insert("1.0", chrono_report)
    app_ref.corr_chrono_textbox.configure(state="disabled")

    # 3. Actualizar TextBox de SNMP
    app_ref.corr_snmp_textbox.configure(state="normal")
    app_ref.corr_snmp_textbox.delete("1.0", "end")
    app_ref.corr_snmp_textbox.insert("1.0", trap_report)
    app_ref.corr_snmp_textbox.configure(state="disabled")
    
    
    
    # ******************* Pestaña Visualizador de Reports Verificación de Traps SNMP *******************

def _populate_verification_report_tab(app_ref, tab_frame):
    """Crea los widgets para el visor del informe de verificación (CSV)."""
    tab_frame.grid_columnconfigure(0, weight=1)
    tab_frame.grid_rowconfigure(2, weight=1)

    # Botón para cargar el archivo CSV
    load_button = ctk.CTkButton(
        tab_frame, 
        text="Cargar Informe de Verificación (.csv)...", 
        command=app_ref.monitoring_controller._load_verification_report
    )
    load_button.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

    # Etiqueta para mostrar el archivo actual
    app_ref.verification_report_file_label = ctk.CTkLabel(
        tab_frame, 
        text="Ningún informe cargado.", 
        font=ctk.CTkFont(size=12, slant="italic")
    )
    app_ref.verification_report_file_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
    
    # Campo de texto para mostrar el informe formateado
    app_ref.verification_report_display = ctk.CTkTextbox(tab_frame, state="disabled", wrap="word")
    app_ref.verification_report_display.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")

def _update_verification_report_display(app_ref, formatted_text, filepath):
        """Actualiza el visor del informe de verificación."""
        
        # Actualizar la etiqueta con el nombre del archivo
        filename = os.path.basename(filepath) if filepath else "Ningún informe cargado."
        app_ref.verification_report_file_label.configure(text=f"Mostrando: {filename}")

        # Actualizar el cuadro de texto
        app_ref.verification_report_display.configure(state="normal")
        app_ref.verification_report_display.delete("1.0", "end")
        if not formatted_text:
            app_ref.verification_report_display.insert("1.0", "El informe está vacío o no se pudo cargar.")
        else:
            app_ref.verification_report_display.insert("1.0", formatted_text)
        app_ref.verification_report_display.configure(state="disabled")