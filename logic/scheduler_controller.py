
import json
import customtkinter as ctk
import os
from tkinter import filedialog
import threading
import  subprocess
from datetime import datetime, timezone
from logic import db_handler
import time
import sys

import logic.robot_executor as robot_executor

class SchedulerController:
    def __init__(self, app_ref):
        self.app_ref = app_ref  # Reference to the main application
        
        self.current_task_index = -1
        self.stop_sequence_flag = threading.Event()
        self.task_output_files = [] # Para guardar los output.xml
        
        
        
    def _on_task_type_change(self, selected_type):
        """Muestra u oculta los widgets de creación de tareas según el tipo seleccionado."""
        # Lo hacemos para mostrar la info relevante en cada momento.
        # Por defecto, cuando el "formulario" se reinicia, se ocultan todos estos campos
        
        # Ocultar todos los widgets opcionales primero ("Test a ejecutar", "Duracion" y "Variables"). AL OCULTARLOS CON FORGET PASARAN A OCUPAR UN ESPACIO DE 0PX, POR LO QUE P.EJ. ELEMENTOS DE LA 6A FILA ("Si Falla") APARECERAN JUNTO A LA 1A Y 2A QUE SON PERMANENTES!
        # Test a ejecutar
        self.app_ref.task_test_label.grid_forget()
        self.app_ref.task_test_combo.grid_forget()
        # Duracion
        self.app_ref.task_param_label.grid_forget()
        self.app_ref.task_param_entry.grid_forget()
        # Variables entrada
        self.app_ref.task_vars_label.grid_forget()
        self.app_ref.task_vars_entry.grid_forget()

        # Advertencia SNMP
        self.app_ref.snmp_warning_label.grid_forget()

        # Variables esperadas
        # self.app_ref.task_args_display_label.grid_forget()    # Finalmente ocultaremos el frame intermedio completo, ya que hemos añadido el boton de copiar ->
        # ->
        if hasattr(self.app_ref, 'args_frame') and self.app_ref.args_frame is not None:
            self.app_ref.args_frame.grid_forget()
        
        # Selector de Sesión
        if hasattr(self.app_ref, 'task_session_selector') and self.app_ref.task_session_selector:
            self.app_ref.task_session_selector.grid_forget() # Ocultar selector de sesión
        
        # Mostrar los widgets necesarios para el tipo de tarea seleccionado. Solo para estos tipos de tareas los mostraremos.
        if selected_type == "Ejecutar Test":
            self.app_ref.task_test_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_test_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

            self.app_ref.task_vars_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_vars_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

            self.app_ref.args_frame.grid(row=4, column=1, padx=10, pady=(0,5), sticky="w")
            
            if hasattr(self.app_ref, 'task_session_selector') and self.app_ref.task_session_selector:
                self.app_ref.task_session_selector.grid(row=5, column=1, padx=10, pady=5, sticky="ew") # Mostrar selector de sesión
            
            self._on_test_selection_change(self.app_ref.task_test_combo.get()) # Llamada inicial al metodo que nos permite añadir la fila con los argumentos de ese testcase

        elif selected_type == "Pausa (segundos)":
            self.app_ref.task_param_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_param_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        elif selected_type == "Verificar Traps SNMP Nuevos":
            self.app_ref.snmp_warning_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")


        

    def _select_task_in_sequence(self, index):
        """Gestiona la selección de una tarea en la lista."""
        self.app_ref.selected_task_index = index
        for i, frame in enumerate(self.app_ref.task_widgets):
            if i == index:
                frame.configure(fg_color=("gray80", "gray25")) # Color de resaltado
            else:
                frame.configure(fg_color="transparent")
                
    def _move_task(self, direction):
        """Mueve la tarea seleccionada hacia arriba (-1) o hacia abajo (1)."""
        if self.app_ref.selected_task_index == -1: return # Es para evitar mover nada u obtener error en caso de querer mover sin seleccionar nada.

        # Partimos de la lista de tareas que está en la memoria (self.app_ref.task_sequence)
        new_index = self.app_ref.selected_task_index + direction # Calculamos la nueva posición del objeto seleccionado que queremos mover.
        if 0 <= new_index < len(self.app_ref.task_sequence): # Nos aseguramos que la nueva pos se encuentre dentro de los indices posibles de la lista.
            # Intercambiar elementos en la lista de datos
            item = self.app_ref.task_sequence.pop(self.app_ref.selected_task_index) # Nos lo saca de la lista, guardandolo temporalmente
            self.app_ref.task_sequence.insert(new_index, item)
            
            # Redibujar y pre-seleccionar el elemento movido
            self.app_ref.update_task_sequence_display() # Una vez actualizada "task_sequence", podemos actualizar la lista en pantalla
            self.app_ref._select_task_in_sequence(new_index) # Hemos redibujado la lista de tareas actualizada, pero queremos conservar el elemento que habíamos movido como seleccionado.
            
    def _remove_selected_task(self):
        """Elimina la tarea seleccionada de la secuencia."""
        if self.app_ref.selected_task_index == -1: return # Es para evitar mover nada u obtener error en caso de querer mover sin seleccionar nada.
        
        self.app_ref.task_sequence.pop(self.app_ref.selected_task_index) # Lo sacamos de la lista SIN GUARDARLO
        self.app_ref.update_task_sequence_display()
        
        
    def _on_test_selection_change(self, selected_test):
        """Se activa al seleccionar un test y muestra sus argumentos requeridos."""

            # Si el usuario selecciona una cabecera (---), no hacemos nada.
        if not selected_test or selected_test.strip().startswith("---"):
            self.app_ref.task_args_display_label.configure(text="") # Limpiamos la etiqueta
            return

        actual_test_name = selected_test.strip()
        args = self.app_ref._get_test_case_arguments(actual_test_name)
        if args:
            self.app_ref.task_args_display_label.configure(text=f"Argumentos: {', '.join(args)}")
        else:
            self.app_ref.task_args_display_label.configure(text="Este test no requiere argumentos.")
            
    def _add_task_to_sequence(self):
        """Recopila la información de la tarea y la añade a la secuencia"""
        task_type = self.app_ref.task_type_combo.get()
        on_fail_action = self.app_ref.task_on_fail_combo.get()  # Puede ser "Detener secuencia", "Continuar"
        
        task_details = {    # Diccionario de valores que iremos rellenando. ESTE SERÁ EL ELEMENTO QUE AÑADIREMOS AL FINAL A LA LISTA DE SECUENCIA DE TAREAS!
            'type': task_type,
            'name': '', # Lo gaurdaremos mas abajo
            'on_fail': on_fail_action,
            'session_id': None, #Por defecto
            'file': '', #Por defecto
            'vars': '', #Por defecto
            'param': '' # Para Pausa o Traps
        }

        if task_type == "Ejecutar Test":
            test_full_name = self.app_ref.task_test_combo.get().strip()
            
            # **************** Lógica de Sesión (Solo para Tests ****************
            selected_session_str = self.app_ref.task_session_selector.get() # nuevo -> para poder escoger la sesion en la que se ejecuta el test
            # Como (al igual que nos ha pasado en alguna otra ocasion) nosotros necesitamos el ID ('A' o 'B') y no todo el texto Sesión A o Sesión B ->
            session_map = {"Sesión A": "A", "Sesión B": "B"}   # -> Hacemos un mapeo
            session_id = session_map.get(selected_session_str, 'A') # Definimos 'A' como valor por defecto
            task_details['session_id'] = session_id # <-- Se guarda el ID de la sesión
            # *****************************************
            
            test_name = test_full_name.lstrip(" -")     # Limpiamos el nombre del test si viene con formato '  Test Name'
            

            robot_file_path = robot_executor._find_test_file(self.app_ref, test_name)      # Buscamos el archivo .robot correspondiente
            if not robot_file_path:
                self.app_ref.gui_queue.put(('scheduler_log', f" Error: No se pudo encontrar el archivo .robot para el test '{test_name}'.\n", "red"))
                return
        
            # Adquirimos las variables que se pasarán al test
            variables = self.app_ref.task_vars_entry.get()
            
            # Usamos el nombre limpio para la lógica, aunque usaremos el completo para mostrar
            display_name = test_full_name if test_full_name.startswith("---") else test_name
            
            task_details['name'] = f"{display_name} (Sesión: {session_id})" # <-- Nombre actualizado
            task_details['file'] = os.path.basename(robot_file_path) # Guardamos solo el nombre del archivo
            task_details['vars'] = variables
            

            self.app_ref.task_vars_entry.delete(0, 'end') # Limpiamos el campo de variables para la próxima tarea

        elif task_type == "Pausa (segundos)":
            duration_str = self.app_ref.task_param_entry.get()
            try:
                duration = int(duration_str)
                if duration <= 0:
                    raise ValueError
            except ValueError:
                self.app_ref.gui_queue.put(('scheduler_log', f"Error: La duración de la pausa debe ser un número positivo.\n", "red"))
                return
            task_details['name'] = f"PAUSA: {duration} segundos" 
            task_details['param'] = duration
            


        elif task_type == "Verificar Traps SNMP Nuevos":
            task_details['param'] = None
            task_details['name'] = "Capturar Traps SNMP De la Secuencia"

        self.app_ref.task_sequence.append(task_details)
        self.app_ref.update_task_sequence_display()
        
        
        # Limpiamos los campos después de añadir
        self.app_ref.task_vars_entry.delete(0, 'end')
        self.app_ref.task_param_entry.delete(0, 'end')
        self.app_ref.task_test_combo.set("")
        self.app_ref.task_args_display_label.configure(text="")
        
        
    def _copy_suggested_args(self):
        """
        Copia los argumentos sugeridos de la etiqueta de ayuda al portapapeles.
        """
        # Obtener el texto completo de la etiqueta de ayuda
        full_text = self.app_ref.task_args_display_label.cget("text")
        
        # Limpiar el texto para quedarnos solo con las variables
        #    (eliminamos el prefijo "Argumentos: ")
        if "Argumentos: " in full_text:
            args_to_copy = full_text.replace("Argumentos: ", "")
            
            # Llamar a la función de copiado que ya tienes
            if args_to_copy:
                self.app_ref.copy_to_clipboard(args_to_copy)
            else:
                self.app_ref._update_status("No hay argumentos que copiar.", "orange")
        else:
            self.app_ref._update_status("No hay argumentos que copiar.", "orange")

    # ************ FUNCIONES DE CARGA Y GUARDADO DE PERFILES DE SECUENCIAS **********
            
    def _save_sequence_profile(self):
        """Guarda la secuencia de tareas actual en un archivo JSON."""
        # Comprobamos si hay algo que guardar
        if not self.app_ref.task_sequence:
            self.app_ref._update_status("No hay ninguna secuencia de tareas para guardar.", "orange")
            return

        # Creamos la carpeta de perfiles si no existe
        profiles_dir = "scheduler_profiles"
        os.makedirs(profiles_dir, exist_ok=True)

        # Abrimos el diálogo "Guardar como.."
        filepath = filedialog.asksaveasfilename(
            title="Guardar Perfil de la Secuencia",
            initialdir=profiles_dir,
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )

        # Si el usuario cancela, no hacemos nada
        if not filepath:
            return

        # Escribimos la secuencia en el archivo
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # json.dumps convierte la lista de Python a un string en formato JSON
                # indent=4 hace que el archivo sea legible para los humanos
                json.dump(self.app_ref.task_sequence, f, indent=4)
            
            self.app_ref.gui_queue.put(('main_status', f"Perfil '{os.path.basename(filepath)}' guardado con éxito.", "green"))
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error al guardar el perfil: {e}", "red"))
            
    def _load_sequence_profile(self):
        """Carga una secuencia de tareas desde un archivo JSON."""
        
        profiles_dir = "scheduler_profiles" # Carpeta donde guardamos los perfiles
        os.makedirs(profiles_dir, exist_ok=True)

        # Abrimos el diálogo "Abrir..."
        filepath = filedialog.askopenfilename(
            title="Cargar Perfil de la Secuencia",
            initialdir=profiles_dir,
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )

        # Si el usuario cancela, no hacemos nada
        if not filepath:
            return

        # Leemos y cargamos la secuencia desde el archivo
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # json.load convierte el string JSON de nuevo a una lista de Python!
                loaded_sequence = json.load(f)
            
            # Actualizamos la secuencia actual y refrescamos la GUI
            self.app_ref.task_sequence = loaded_sequence
            self.app_ref.update_task_sequence_display()
            
            self.app_ref.gui_queue.put(('main_status', f"Perfil '{os.path.basename(filepath)}' cargado con éxito.", "green"))

        except json.JSONDecodeError:
            self.app_ref.gui_queue.put(('main_status', "Error: El archivo seleccionado no es un perfil JSON válido.", "red"))
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error al cargar el perfil: {e}", "red"))        

    def _run_task_sequence_thread(self):
        """Inicia la ejecución de la secuencia de tareas en un hilo separado."""
        if self.app_ref.is_main_task_running:
            self.app_ref.gui_queue.put(('scheduler_log', "Error: Ya hay una tarea principal en ejecución.\n", "red"))
            return
        if not self.app_ref.task_sequence:
            self.app_ref.gui_queue.put(('scheduler_log', "No hay tareas en la secuencia para ejecutar.\n", "gray"))
            return
        
        required_sessions = set(task['session_id'] for task in self.app_ref.task_sequence if task['type'] == 'Ejecutar Test')
        for session_id in required_sessions:
            if not self.app_ref.sessions[session_id]['process']:
                msg = f"Error: La Sesión {session_id} no está conectada.\n"
                self.app_ref.gui_queue.put(('scheduler_log', msg, "red"))
                return
        # Preparamos antes de la ejecución
        self.app_ref.is_main_task_running = True
        self.stop_sequence_flag.clear()
        self.task_output_files = [] # Limpiar lista de outputs.xml
        self.current_task_index = -1
        # Deshabilitamos botones para no interferir pasando el estado "is_running"
        # self.app_ref.run_button_state(is_running=True)    # Mejor pasarlo a la cola y no llamar a una función de app_ref desde un controlador... ->
        # ->
        self.app_ref.gui_queue.put(('enable_buttons', None)) # Actualiza estado de botones
        self.app_ref.gui_queue.put(('scheduler_log', "▶️ Iniciando secuencia...\n", "cyan"))
        
        # Ejecutamos el hilo 
        threading.Thread(target=self._execute_next_task, daemon=True).start()
        
    def _stop_task_sequence(self):
        """Establece la señal para detener la ejecución de la secuencia."""
        if self.app_ref.is_main_task_running:
            self.app_ref.stop_sequence_event.set()
            self.app_ref.gui_queue.put(('scheduler_log', "Señal de detención enviada... Finalizando tarea actual.\n", "orange"))
            
            
    def _execute_next_task(self, sequence_failed=False):
        """
        Función recursiva/iterativa que se ejecuta en el hilo.
        Ejecuta una tarea y luego se llama a sí misma para la siguiente.
        """
        
        # *** CONDICIONES DE PARADA (depende de lo que se asignó y lo que pasó en el bucle anterior) ***
        # 1. Si la secuencia falló y la tarea anterior debía detenerla
        if sequence_failed:
            self.app_ref.gui_queue.put(('scheduler_log', "Secuencia detenida debido a un error.\n", "red"))
            self._consolidate_reports(sequence_failed=True)
            return # Termina el hilo

        # 2. Si se presionó el botón de Stop
        if self.stop_sequence_flag.is_set():
            self.app_ref.gui_queue.put(('scheduler_log', "⏹️ Secuencia detenida por el usuario.\n", "orange"))
            self._consolidate_reports(sequence_failed=True) # Consideramos 'fallida' si se detiene
            return # Termina el hilo

        # 3. Si hemos completado todas las tareas :)
        self.current_task_index += 1    # Recordemos que el indice estaba inicializado a -1! 
        if self.current_task_index >= len(self.app_ref.task_sequence):
            self.app_ref.gui_queue.put(('scheduler_log', "✅ Secuencia completada.\n", "green"))
            self._consolidate_reports(sequence_failed=False)
            return # Salimos del bucle y el hilo termina. Ya no seguimos con el resto del bucle.

        # *** OBTENER Y EJECUTAR TAREA ACTUAL ***
        task = self.app_ref.task_sequence[self.current_task_index]
        task_num = self.current_task_index + 1
        total_tasks = len(self.app_ref.task_sequence)
        
        # Modificamos el nombre para el log, quitando el prefijo de guiones si existe
        log_name = task['name'].lstrip(" -")
        log_msg = f"--- (Tarea {task_num}/{total_tasks}) {log_name} ---\n"
        self.app_ref.gui_queue.put(('scheduler_log', log_msg, "white"))

        # *** LOGIC***
        # Inicializamos las variables antes de comenzar a ejecutar la tarea
        task_failed = False
        result_code = 0 # (PASS)        
        try:
            if task['type'] == "Ejecutar Test":
                # CUidado! Ya no usamos self.app_ref.active_session_id!
                session_to_run = task['session_id']
                # *******************************************
                
                if not session_to_run or not self.app_ref.sessions[session_to_run]['process']:  # SI la tarea no tiene asignada una sesión o la sesión que esta asignada a la tarea no está activa.
                    raise RuntimeError(f"Sesión {session_to_run} (requerida por la tarea) no está conectada.")

                output_file = f"output_task_{self.current_task_index}.xml"
                self.task_output_files.append(os.path.join("test_results", output_file))
                
                # Nombre limpio del test para buscar en el mapa
                clean_test_name = task['name'].split(" (Sesión:")[0].lstrip(" -")   # Solo queremos quedarnos con el nombre del test!

                # Creamos el callback para esta sesión específica. Esto lo hacemos para poder actualizar las secciones de la GUI correspondientes a la hora de ejecutar tests.
                on_success_callback = self.app_ref._create_gui_update_callback(
                    session_to_run,
                    *self.app_ref.test_gui_update_map.get(clean_test_name, (None, []))  # Buscamos el nombre del test de la tarea en el mapa. Si lo encuentra, nos devuelve una tupla! -> ('modules_display', ['modules']). 
                                                                                        # SI no lo encontrara en el mapa (porque sea un test que no actualiza la GUI), nos daría el valor por defecto de la tupla vacía: (None, [])                                         
                                                                                        #  Para separar la tupla, separamos en elemenetos con el *
                )

                result_code = robot_executor._run_robot_test(
                    app_ref=self.app_ref,
                    test_name=clean_test_name,
                    session_id=session_to_run, 
                    variables=task['vars'].split(),
                    on_success=on_success_callback,
                    preferred_filename=task['file'],
                    output_filename=output_file,
                    log_file=f"log_task_{self.current_task_index}.html",
                    report_file=f"report_task_{self.current_task_index}.html",
                    suppress_gui_updates=True, # No queremos status "PASS/FAIL" por cada test, ya que al final obtendremos el informe
                    block=True
                )
                if result_code != 0:
                    task_failed = True  # Despues de ejecutar el test (al final de este método/hilo), en caso de que haya fallado, se valorará en funcion de lo que esta tarea tenga asignado en task['on_fail'] si detener toda la secuencia


            elif task['type'] == "Pausa (segundos)":
                duration = task['param']
                self.app_ref.gui_queue.put(('scheduler_log', f" Iniciando pausa de {duration}s...\n", "gray"))
                # Hacemos la pausa en incrementos de 1s para poder cancelarla
                for _ in range(duration):
                    if self.stop_sequence_flag.is_set():
                        break # tenemos que permitir salir de la pausa en caso de que se quiera detener la secuencia
                    time.sleep(1)   # Para no sobrecargar la cpu
                
                if not self.stop_sequence_flag.is_set():
                    self.app_ref.gui_queue.put(('scheduler_log', f" Pausa finalizada.\n", "gray"))
            
            elif task['type'] == "Verificar Traps SNMP Nuevos":
                if not self.app_ref.trap_listener_controller.is_listener_running():
                     raise RuntimeError("El Listener SNMP no está iniciado.")
                     
                new_traps_found = self.app_ref.trap_listener_controller.check_and_clear_new_traps()
                
                if not new_traps_found:
                    self.app_ref.gui_queue.put(('scheduler_log', "❌ FALLÓ: No se recibieron nuevos traps SNMP.\n", "red"))
                    task_failed = True
                else:
                     self.app_ref.gui_queue.put(('scheduler_log', "✅ ÉXITO: Se recibieron nuevos traps SNMP.\n", "green"))

        except Exception as e:
            self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error fatal en la tarea: {e}\n", "red"))
            task_failed = True

        
        # *** Decidir si continuar ***
        should_stop = task_failed and (task['on_fail'] == "Detener secuencia")  # Solo pararemos la secuencia en el caso de que el test que haya fallado tenga asignado en el on_fail que así sea
        
        # Llamada recursiva para la siguiente tarea
        self._execute_next_task(sequence_failed=should_stop)           
        
        
         
    # def _execute_task_sequence(self):
    #     """
    #     Ejecución de la secuencia de tareas.
    #     Este método se ejecuta en un hilo secundario.
    #     """
    #     try:
    #         active_id = self.app_ref.active_session_id
    #         if not self.app_ref.sessions[active_id]['process']:
    #             raise Exception(f"Sesión {active_id} no está conectada.")
    #     except Exception as e:
    #         self.app_ref.gui_queue.put(('scheduler_log', f"Error: {e}", "red"))
    #         self.app_ref.gui_queue.put(('enable_buttons', None))
    #         return
        
        
    #     self.app_ref.is_main_task_running = True
        
    #     sequence_failed = False
    #     xml_files = []

    #     try:
    #         # 1. Crear el directorio para los historiales si no existe
    #         history_dir = "trap_history"
    #         os.makedirs(history_dir, exist_ok=True)
            
    #         # 2. Obtener el nombre del archivo desde la GUI
    #         history_name = self.app_ref.scheduler_history_name_entry.get()
    #         if not history_name:
    #             # Si está vacío, generar un nombre por defecto con fecha y hora
    #             history_name = f"traps_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
    #         # 3. Construir la ruta completa y crear la BD para esta sesión
    #         current_db_path = os.path.join(history_dir, f"{history_name}.db")
    #         db_handler.initialize_database(current_db_path) # Inicializamos la nueva BD
                
    #         if not hasattr(self.app_ref, 'task_sequence') or not self.app_ref.task_sequence:
    #             self.app_ref.gui_queue.put(('main_status', "Error: No hay tareas en la secuencia.", "red"))
    #             return

    #         self.app_ref.gui_queue.put(('scheduler_log', f"--- Iniciando secuencia de tareas. Traps se guardarán en: {current_db_path} ---\n", "white"))

    #         timestamp_before_task = datetime.now(timezone.utc).isoformat() # Timestamp inicial

    #         for i, task in enumerate(self.app_ref.task_sequence):
    #             # Comprobar si se ha solicitado detener la secuencia
    #             if self.app_ref.stop_sequence_event.is_set():
    #                 self.app_ref.gui_queue.put(('scheduler_log', "Secuencia detenida por el usuario.\n", "orange"))
    #                 break

    #             task_name = task.get('name', f"Tarea {i+1}")
    #             self.app_ref.gui_queue.put(('scheduler_log', f"▶ Ejecutando Tarea [{i+1}/{len(self.app_ref.task_sequence)}]: {task_name}\n", "cyan"))
                
    #             task_result = 0 # 0 = PASS, otro valor = FAIL
                
    #             # ----------- PROCESAR TIPO DE TAREA -----------
    #             if task['type'] == 'robot_test':
    #                 output_file = f"output_task_{i}.xml"
    #                 output_file_path = os.path.join("test_results", output_file) # Guardamos el path del fichero xml correspondiente a este test para poder especificarlo mas tarde en codigo error (en caso de que el test falle)
    #                 timestamp_before_task = datetime.now(timezone.utc).isoformat()
    #                 # ***************************************************************************************************************************

    #                 # Comprobamos si este test tiene una acción de GUI asociada
    #                 gui_update_info = self.app_ref.test_gui_update_map.get(task['test_name'])  # Recordemos que "task" era un diccionario que tenía la clave "test_name"
    #                 success_callback = None # Por defecto, no hay callback

    #                 if gui_update_info:
    #                     message_type, attr_names = gui_update_info
    #                     # ************************************************************************************************************
    #                     # Llamamos directamente al método reutilizable que ya existe en la clase
    #                     success_callback = self.app_ref._create_gui_update_callback(active_id, message_type, attr_names)
    #                     # ************************************************************************************************************

    #                 # 2. Pasar el callback (o None si no hay) a la función de ejecución
    #                 task_result = robot_executor._run_robot_test(
    #                     self.app_ref,
    #                     test_name=task['test_name'],
    #                     session_id=active_id,
    #                     variables=task.get('variables', []),
    #                     preferred_filename=task.get('filename'),
    #                     output_filename=output_file,
    #                     suppress_gui_updates=True,
    #                     on_success=success_callback  # <--  Si no se crea ningún callback especial para este test, el valor de success_callback será None y no se ejecutará nada extra.
    #                 )
                    
    #                 if os.path.exists(output_file_path):
    #                     xml_files.append(output_file_path)  # Guardamos el XML para el informe consolidado si se generó el archivo en el path guardado
    #                 else:
    #                     self.app_ref.gui_queue.put(('scheduler_log', f"⚠️  No se generó archivo de salida para '{task['name']}'.\n", "orange"))

    #             elif task['type'] == 'delay':
    #                 delay_seconds = int(task.get('duration', 5))
    #                 self.app_ref.gui_queue.put(('scheduler_log', f"  Pausando durante {delay_seconds} segundos...\n", "gray"))
                    
    #                 # Hacemos una pausa interrumpible
    #                 for _ in range(delay_seconds):
    #                     if self.app_ref.stop_sequence_event.is_set():
    #                         break
    #                     time.sleep(1)

    #             elif task['type'] == 'check_snmp_traps':
    #                 self.app_ref.gui_queue.put(('scheduler_log', "  Buscando nuevos traps SNMP...\n", "gray"))
    #                 new_traps = self.app_ref.trap_receiver.get_traps_since(timestamp_before_task)
                    
    #                 if new_traps:
    #                     self.app_ref.gui_queue.put(('scheduler_log', f"  ✔ Encontrados {len(new_traps)} traps nuevos.\n", "green"))
    #                     db_handler.save_traps_to_db(self.app_ref, new_traps, current_db_path)
    #                 else:
    #                     self.app_ref.gui_queue.put(('scheduler_log', "  - No se encontraron traps nuevos.\n", "gray"))
                    
    #                 # Actualizamos el timestamp para la siguiente tarea
    #                 timestamp_before_task = datetime.now(timezone.utc).isoformat()

    #             # ----------- MANEJAR RESULTADO DE LA TAREA -----------
    #             if task_result != 0:
    #                 self.app_ref.gui_queue.put(('scheduler_log', f"❌ Tarea '{task_name}' ha fallado.\n", "red"))
    #                 sequence_failed = True
    #                 if task.get('on_fail') == 'stop':
    #                     self.app_ref.gui_queue.put(('scheduler_log', "Política 'on_fail: stop'. Deteniendo la secuencia.\n", "red"))
    #                     break
    #             else:
    #                 self.app_ref.gui_queue.put(('scheduler_log', f"✔ Tarea '{task_name}' completada.\n", "green"))
                    
    #         # ----------- FINAL DE LA SECUENCIA -----------
    #     finally:
    #         self.app_ref.gui_queue.put(('scheduler_log', "--- Secuencia de tareas finalizada ---\n", "white"))

    #         # Generar informe consolidado si se ejecutaron tests
    #         if xml_files:
    #             self.app_ref.gui_queue.put(('scheduler_log', "Generando informe consolidado...\n", "gray"))
    #             try:
    #             # ***************************************************************************************************************************
    #             #  CORRECCIÓN: YA NO HAREMOS USO DE ESTO, SINO DE SUBPROCESS para llamar a rebot --- EN UN PROCESO A PARTE DEL DE LA GUI
    #             #     rebot_cli(['--name', 'Informe de Secuencia', 
    #             #             '--outputdir', 'test_results',
    #             #             '--log', 'log_consolidado.html',
    #             #             '--report', 'report_consolidado.html'] + xml_files)
    #             #     app_ref.gui_queue.put(('scheduler_log', "✔ Informe consolidado 'report_consolidado.html' creado.\n", "green"))
    #             # except Exception as e:
    #             #     app_ref.gui_queue.put(('scheduler_log', f"❌ Error al generar informe consolidado: {e}\n", "red"))
    #             # ***************************************************************************************************************************

    #         # Construir el comando para ejecutar rebot. Lo hacemos creando un proceso completamente separado para generar el informe. De esta forma si rebot falla no afecta a la app principal (GUI). Tambien podemos determinal un Timeout, asi la GUI no se puede quedar congelada.
    #                 command = [
    #                     sys.executable,  # Usa el mismo python que ejecuta la app
    #                     "-m", "robot.rebot",
    #                     "--name", "Informe de Secuencia",
    #                     "--outputdir", "test_results",
    #                     "--log", "log_consolidado.html",
    #                     "--report", "report_consolidado.html"
    #                 ] + xml_files

    #                 # Ejecutar el comando como un subproceso con un tiempo de espera
    #                 result = subprocess.run(
    #                     command, 
    #                     capture_output=True, 
    #                     text=True, 
    #                     timeout=30  # Espera un máximo de 30 segundos
    #                 )

    #                 if result.returncode == 0:
    #                     self.app_ref.gui_queue.put(('scheduler_log', "✔ Informe consolidado creado.\n", "green"))
    #                 else:
    #                     # Si rebot falla, muestra el error
    #                     error_output = result.stderr or result.stdout
    #                     self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error al generar informe: {error_output}\n", "red"))

    #             except subprocess.TimeoutExpired:
    #                 self.app_ref.gui_queue.put(('scheduler_log', "❌ Error: La generación del informe tardó demasiado (timeout).\n", "red"))

    #             except Exception as e:
    #                 self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error inesperado al generar informe: {e}\n", "red"))

    #         # Restaurar GUI
    #         final_message = "Secuencia completada con errores." if sequence_failed else "Secuencia completada con éxito."
    #         final_color = "red" if sequence_failed else "green"
    #         self.app_ref.gui_queue.put(('main_status', final_message, final_color))
            
    #         self.app_ref.gui_queue.put(('enable_buttons', None)) # Rehabilitamos botones
            

    #         self.app_ref.is_main_task_running = False
    #         self.app_ref.gui_queue.put(('enable_buttons', None))
                
    

    def _consolidate_reports(self, sequence_failed):
        """
        Se llama al final de la secuencia (éxito, fallo o stop).
        Genera un informe consolidado. Es el paso final en la ejecución de una secuencia (independientmente de que falle o se ejecute con exito)
        """
        try:
            if not self.task_output_files:
                self.app_ref.gui_queue.put(('scheduler_log', "No se generaron informes de tests para consolidar.\n", "gray"))   # Seria raro encontrarnos con este caso. Significaría que tendriamos que valorar alguna condicion mas de error en el bucle recurrente del metodo _execute_next_task
            else:
                self.app_ref.gui_queue.put(('scheduler_log', " Generando informe consolidado...\n", "cyan"))
                
                # Limpiamos informes antiguos
                if os.path.exists("test_results/report_consolidado.html"):
                    os.remove("test_results/report_consolidado.html")
                if os.path.exists("test_results/log_consolidado.html"):
                    os.remove("test_results/log_consolidado.html")

                # Construimos el comando para 'rebot'
                command = [
                    sys.executable, '-m', 'robot.rebot',
                    '--outputdir', 'test_results',
                    '--output', 'output_consolidado.xml',
                    '--log', 'log_consolidado.html',
                    '--report', 'report_consolidado.html',
                    '--name', 'Secuencia de Pruebas'
                ] + self.task_output_files # Añadimos todos los output.xml

                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    timeout=30,
                    encoding='utf-8' # Asegurar encoding
                )

                if result.returncode == 0:
                    self.app_ref.gui_queue.put(('scheduler_log', "✔ Informe consolidado creado.\n", "green"))
                else:
                    error_output = result.stderr or result.stdout
                    self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error al generar informe: {error_output}\n", "red"))

        except subprocess.TimeoutExpired:   # Debido al timeout del suboprocess de result
            self.app_ref.gui_queue.put(('scheduler_log', "❌ Error: La generación del informe tardó demasiado.\n", "red"))
        except Exception as e:  # Cualquier otro error que no sea de timeout
            self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error inesperado al generar informe: {e}\n", "red"))

        # *** Restaurar GUI (SIEMPRE se ejecuta) ***
        final_message = "Secuencia completada con errores." if sequence_failed else "Secuencia completada con éxito."
        final_color = "red" if sequence_failed else "green"
        self.app_ref.gui_queue.put(('main_status', final_message, final_color))
        
        self.app_ref.gui_queue.put(('enable_buttons', None)) # Rehabilitamos botones
        self.app_ref.is_main_task_running = False
        self.stop_sequence_flag.clear()
        self.current_task_index = -1    # Volvemos a inicializar la variable indice de las tareas
        self.task_output_files = []


