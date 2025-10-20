import customtkinter as ctk
import os



# Función principal que se llamará desde app.py
def create_scheduler_tab(app_ref):
    scheduler_frame = ctk.CTkFrame(app_ref, corner_radius=0)
    
    scheduler_frame.grid_columnconfigure(0, weight=1)
    scheduler_frame.grid_rowconfigure(2, weight=1)

    # --- 1. FRAME DE CREACIÓN DE TAREAS ---
    creator_frame = ctk.CTkFrame(scheduler_frame)
    creator_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
    creator_frame.grid_columnconfigure(1, weight=1)
    
    ctk.CTkLabel(creator_frame, text="1. Crear Tarea", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

    # --- PASO 1: CREACIÓN DE TODOS LOS WIDGETS (PERMANENTES Y DINÁMICOS) ---

    # Widget permanente: Tipo de Tarea
    ctk.CTkLabel(creator_frame, text="Tipo de Tarea:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    app_ref.task_type_combo = ctk.CTkComboBox(creator_frame, values=["Ejecutar Test", "Pausa (segundos)", "Verificar Traps SNMP Nuevos"], command=app_ref.scheduler_controller._on_task_type_change)
    app_ref.task_type_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    # Widget dinámico: Test a Ejecutar
    app_ref.task_test_label = ctk.CTkLabel(creator_frame, text="Test a Ejecutar:")
    organized_test_list = []
    if app_ref.tests_data:
        for file_path, test_list in app_ref.tests_data.items():
            filename = os.path.basename(file_path)
            organized_test_list.append(f"--- {filename} ---")
            for test in test_list:
                organized_test_list.append(f"  {test}")
    else:
        organized_test_list = ["No se encontraron tests"]
    app_ref.task_test_combo = ctk.CTkComboBox(creator_frame, values=organized_test_list, command=app_ref.scheduler_controller._on_test_selection_change)
    
    # Widget dinámico: Variables del test
    app_ref.task_vars_label = ctk.CTkLabel(creator_frame, text="Variables:")
    app_ref.task_vars_entry = ctk.CTkEntry(creator_frame, placeholder_text="VAR1:valor1 VAR2:valor2")
    
    # Widget dinámico: Frame de Argumentos y Botón Copiar
    app_ref.args_frame = ctk.CTkFrame(creator_frame, fg_color="transparent")
    app_ref.task_args_display_label = ctk.CTkLabel(app_ref.args_frame, text="", text_color="gray", 
                                               font=ctk.CTkFont(size=11), 
                                               wraplength=750,  # <-- Límite de ancho en píxeles
                                               justify="left")   # <-- Alineación del texto
    app_ref.task_args_display_label.pack(side="left", padx=(0, 10))
    copy_args_button = ctk.CTkButton(app_ref.args_frame, text="Copiar", width=60, command=app_ref.scheduler_controller._copy_suggested_args)
    copy_args_button.pack(side="left")
    
    # Widget dinámico: Parámetro de duración
    app_ref.task_param_label = ctk.CTkLabel(creator_frame, text="Duración (s):")
    app_ref.task_param_entry = ctk.CTkEntry(creator_frame, placeholder_text="Ej: 10")
    
    # Widget dinámico: Advertencia SNMP
    app_ref.snmp_warning_label = ctk.CTkLabel(creator_frame, text="⚠️ Recuerda iniciar el Listener desde MONITORING > SNMP.", text_color=("#D35400", "#F39C12"), font=ctk.CTkFont(weight="bold"))
    
    # Widget permanente: Si Falla
    ctk.CTkLabel(creator_frame, text="Si Falla:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    app_ref.task_on_fail_combo = ctk.CTkComboBox(creator_frame, values=["Detener secuencia", "Continuar"])
    app_ref.task_on_fail_combo.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

    # Widget permanente: Botón Añadir
    add_task_button = ctk.CTkButton(creator_frame, text="Añadir Tarea a la Secuencia", command=app_ref.scheduler_controller._add_task_to_sequence)
    add_task_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

# --- 2. FRAME DE LA SECUENCIA DE TAREAS ---
    sequence_frame = ctk.CTkFrame(scheduler_frame)
    sequence_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    sequence_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(sequence_frame, text="2. Secuencia de Tareas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    app_ref.task_sequence_frame = ctk.CTkScrollableFrame(sequence_frame, height=200)
    app_ref.task_sequence_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    
    # Frame para los botones de Cargar/Guardar Perfil
    profile_actions_frame = ctk.CTkFrame(sequence_frame, fg_color="transparent")
    profile_actions_frame.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="n")

    load_profile_button = ctk.CTkButton(profile_actions_frame, text="Cargar Perfil...", width=100, command=app_ref.scheduler_controller._load_sequence_profile)
    load_profile_button.pack(pady=(0, 5))

    save_profile_button = ctk.CTkButton(profile_actions_frame, text="Guardar Perfil...", width=100, command=app_ref.scheduler_controller._save_sequence_profile)
    save_profile_button.pack(pady=5)


    sequence_controls_frame = ctk.CTkFrame(sequence_frame, fg_color="transparent")
    sequence_controls_frame.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ns")

    move_up_button = ctk.CTkButton(sequence_controls_frame, text="▲ Subir", width=80, command=lambda: app_ref.scheduler_controller._move_task(-1))
    move_up_button.pack(pady=5)

    move_down_button = ctk.CTkButton(sequence_controls_frame, text="▼ Bajar", width=80, command=lambda: app_ref.scheduler_controller._move_task(1))
    move_down_button.pack(pady=5)

    remove_button = ctk.CTkButton(sequence_controls_frame, text="❌ Eliminar", width=80, fg_color="#D32F2F", hover_color="#B71C1C", command=app_ref.scheduler_controller._remove_selected_task)
    remove_button.pack(pady=5)

    # --- 3. FRAME DE EJECUCIÓN Y REGISTRO ---
    execution_frame = ctk.CTkFrame(scheduler_frame)
    execution_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
    execution_frame.grid_columnconfigure(0, weight=1)
    execution_frame.grid_rowconfigure(3, weight=1)

    ctk.CTkLabel(execution_frame, text="3. Ejecución y Registro", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    # Campo para introducir el nombre del archivo donde se guardaran los traps atrapados en la BD
    history_name_frame = ctk.CTkFrame(execution_frame, fg_color="transparent")
    history_name_frame.grid(row=1, column=0, padx=10, pady=(5,0), sticky="ew")

    ctk.CTkLabel(history_name_frame, text="Nombre de la Sesión de Traps:").pack(side="left", padx=(0, 5))
    app_ref.scheduler_history_name_entry = ctk.CTkEntry(history_name_frame, placeholder_text="ej: prueba_activacion_inputs_1")
    app_ref.scheduler_history_name_entry.pack(side="left", fill="x", expand=True)
    ctk.CTkLabel(history_name_frame, text=".db").pack(side="left", padx=(5, 0))

    # Botones de ejecución
    execution_buttons = ctk.CTkFrame(execution_frame, fg_color="transparent")
    execution_buttons.grid(row=2, column=0, sticky="ew")
    execution_buttons.grid_columnconfigure((0,1), weight=1)
    app_ref.run_sequence_button = ctk.CTkButton(execution_buttons, text="▶️ Ejecutar Secuencia", command=app_ref.scheduler_controller._run_task_sequence_thread)
    app_ref.run_sequence_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    app_ref.stop_sequence_button = ctk.CTkButton(execution_buttons, text="⏹️ Detener Secuencia", command=app_ref.scheduler_controller._stop_task_sequence, state="disabled")
    app_ref.stop_sequence_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    
    # Campo de texto para el log de ejecución
    app_ref.scheduler_log_textbox = ctk.CTkTextbox(execution_frame, state="disabled")
    app_ref.scheduler_log_textbox.grid(row=3, column=0, padx=10, pady=(5,10), sticky="nsew")

    app_ref.scheduler_controller._on_task_type_change(app_ref.task_type_combo.get()) # Llamada inicial para configurar la visibilidad    

    return scheduler_frame
        
def _update_scheduler_log(app_ref, message, color):
    """Añade un mensaje al cuadro de texto de registro del planificador."""
    app_ref.scheduler_log_textbox.configure(state="normal")
    app_ref.scheduler_log_textbox.insert("end", message, (color,))
    app_ref.scheduler_log_textbox.configure(state="disabled")
    app_ref.scheduler_log_textbox.see("end") # Autoscroll hacia el final
    
def _update_task_sequence_display(app_ref):
    """Redibuja la lista visual de tareas en la secuencia."""
    for widget in app_ref.task_widgets:
        widget.destroy()
    app_ref.task_widgets.clear()
    app_ref.selected_task_index = -1

    for i, task in enumerate(app_ref.task_sequence):
        task_frame = ctk.CTkFrame(app_ref.task_sequence_frame, fg_color="transparent")
        task_frame.pack(fill="x", padx=5, pady=2)
        
        task_label = ctk.CTkLabel(task_frame, text=f"{i+1}. {task['name']}", anchor="w")
        task_label.pack(fill="x")
        
        # Hacemos que el frame y la etiqueta sean clickables para seleccionar la fila
        task_frame.bind("<Button-1>", lambda event, index=i: app_ref.scheduler_controller._select_task_in_sequence(index))
        task_label.bind("<Button-1>", lambda event, index=i: app_ref.scheduler_controller._select_task_in_sequence(index))

        app_ref.task_widgets.append(task_frame)
