
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
        
        
        
    def _on_task_type_change(self, selected_type):
        """Muestra u oculta los widgets de creación de tareas según el tipo seleccionado."""
        # Lo hacemos para mostrar la info relevante en cada momento.
        # Por defecto, cuando el "formulario" se reinicia se ocultan todos estos campos
        
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
        
        # Mostrar los widgets necesarios para el tipo de tarea seleccionado. Solo para estos tipos de tareas los mostraremos.
        if selected_type == "Ejecutar Test":
            self.app_ref.task_test_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_test_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

            self.app_ref.task_vars_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_vars_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

            self.app_ref.args_frame.grid(row=4, column=1, padx=10, pady=(0,5), sticky="w")
            self._on_test_selection_change(self.app_ref.task_test_combo.get()) # Llamada inicial al metodo que nos permite añadir la fila con los argumentos de ese testcase

        elif selected_type == "Pausa (segundos)":
            self.app_ref.task_param_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_param_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        elif selected_type == "Verificar Traps SNMP Nuevos":
            self.app_ref.snmp_warning_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    def _add_task_to_sequence(self):
        """Recopila la información de la tarea y la añade a la secuencia."""
        task_type = self.app_ref.task_type_combo.get()
        on_fail = "stop" if self.app_ref.task_on_fail_combo.get() == "Detener secuencia" else "continue"
        task = {'on_fail': on_fail}

        if task_type == "Ejecutar Test":
            selected_item = self.app_ref.task_test_combo.get()
            
            # Validamos que no sea una cabecera (---) o que la lista de testcase se encuentre vacia porque en ese archivo no hayan
            if selected_item.strip().startswith("---") or selected_item == "No se encontraron tests":
                self.app_ref._update_status("Error: Por favor, seleccione un test válido.", "red")
                return
            
            test_name = selected_item.strip()
        
            # Adquirimos las variables
            variables_str = self.app_ref.task_vars_entry.get()
            # Dividimos el string por espacios para tener una lista de "CLAVE:VALOR"
            variables_list = variables_str.split() if variables_str else []
            
            task['type'] = 'robot_test'
            task['name'] = f"TEST: {test_name}"
            task['test_name'] = test_name
            task['filename'] = robot_executor._find_test_file(self.app_ref, test_name).split(os.sep)[-1]
            task['variables'] = variables_list

            self.app_ref.task_vars_entry.delete(0, 'end') # Limpiamos el campo de variables para la próxima tarea

        elif task_type == "Pausa (segundos)":
            duration = self.app_ref.task_param_entry.get()
            if not duration.isdigit() or int(duration) <= 0:
                self.app_ref._update_status("Error: La duración de la pausa debe ser un número positivo.", "red")
                return
            task['type'] = 'delay'
            task['name'] = f"PAUSA: {duration} segundos"
            task['duration'] = duration

        elif task_type == "Verificar Traps SNMP Nuevos":
            task['type'] = 'check_snmp_traps'
            task['name'] = "VERIFICAR: Traps SNMP Nuevos"

        self.app_ref.task_sequence.append(task)
        self.app_ref.update_task_sequence_display()
        

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
        if selected_test.strip().startswith("---"):
            self.app_ref.task_args_display_label.configure(text="") # Limpiamos la etiqueta
            return

        actual_test_name = selected_test.strip()
        args = self.app_ref._get_test_case_arguments(actual_test_name)
        if args:
            self.app_ref.task_args_display_label.configure(text=f"Argumentos: {', '.join(args)}")
        else:
            self.app_ref.task_args_display_label.configure(text="Este test no requiere argumentos.")
            
            
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
        # Deshabilitamos botones para no interferir pasando el estado "is_running"
        self.app_ref.run_button_state(is_running=True)
        # Preparamos el evento para poder detener la secuencia
        self.app_ref.stop_sequence_event = threading.Event()
        threading.Thread(target=self._execute_task_sequence, daemon=True).start()


    def _stop_task_sequence(self):
        """Establece la señal para detener la ejecución de la secuencia."""
        if hasattr(self.app_ref, 'stop_sequence_event'):
            self.app_ref.gui_queue.put(('scheduler_log', "Señal de detención enviada... Finalizando tarea actual.\n", "orange"))
            self.app_ref.stop_sequence_event.set()

    def _execute_task_sequence(self):
        """
        Motor de ejecución de la secuencia de tareas.
        NOTA: Este método se ejecuta en un hilo secundario.
        """
        self.app_ref.is_main_task_running = True
        
        sequence_failed = False
        xml_files = []

        try:
            # 1. Crear el directorio para los historiales si no existe
            history_dir = "trap_history"
            os.makedirs(history_dir, exist_ok=True)
            
            # 2. Obtener el nombre del archivo desde la GUI
            history_name = self.app_ref.scheduler_history_name_entry.get()
            if not history_name:
                # Si está vacío, generar un nombre por defecto con fecha y hora
                history_name = f"traps_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
            # 3. Construir la ruta completa y crear la BD para esta sesión
            current_db_path = os.path.join(history_dir, f"{history_name}.db")
            db_handler.initialize_database(current_db_path) # Inicializamos la nueva BD
                
            if not hasattr(self.app_ref, 'task_sequence') or not self.app_ref.task_sequence:
                self.app_ref.gui_queue.put(('main_status', "Error: No hay tareas en la secuencia.", "red"))
                return

            self.app_ref.gui_queue.put(('scheduler_log', f"--- Iniciando secuencia de tareas. Traps se guardarán en: {current_db_path} ---\n", "white"))

            timestamp_before_task = datetime.now(timezone.utc).isoformat() # Timestamp inicial

            for i, task in enumerate(self.app_ref.task_sequence):
                # Comprobar si se ha solicitado detener la secuencia
                if self.app_ref.stop_sequence_event.is_set():
                    self.app_ref.gui_queue.put(('scheduler_log', "Secuencia detenida por el usuario.\n", "orange"))
                    break

                task_name = task.get('name', f"Tarea {i+1}")
                self.app_ref.gui_queue.put(('scheduler_log', f"▶ Ejecutando Tarea [{i+1}/{len(self.app_ref.task_sequence)}]: {task_name}\n", "cyan"))
                
                task_result = 0 # 0 = PASS, otro valor = FAIL
                
                # ----------- PROCESAR TIPO DE TAREA -----------
                if task['type'] == 'robot_test':
                    output_file = f"output_task_{i}.xml"
                    output_file_path = os.path.join("test_results", output_file) # Guardamos el path del fichero xml correspondiente a este test para poder especificarlo mas tarde en codigo error (en caso de que el test falle)
                    timestamp_before_task = datetime.now(timezone.utc).isoformat()
                    # ***************************************************************************************************************************
                    # MODIFICACIÓN: AHORA USAREMOS EL MAPA DEFINIFO EN INIT QUE RELACIONA EL NOMBRE DEL TEST CON EL MENSAJE DE LA COLA Y LOS ATRIBUTOS DEL LISTENER -> MAS ABAJO ->
                    # # **IMPORTANTE**: _run_robot_test debe devolver el código de resultado (lo guardamos en task_result) para dar fallo despues del inicio de cualquier tarea en caso de ser != 0
                    # #Ejecutamos el test correspondiente al que pone en la tarea
                    # task_result = app_ref._run_robot_test(
                    #     test_name=task['test_name'],
                    #     variables=task.get('variables', []),
                    #     preferred_filename=task.get('filename'),
                    #     output_filename=output_file,
                    #     suppress_gui_updates=True # Para evitar mensajes de status duplicados
                    # )
                    # ***************************************************************************************************************************
                    # -> ->
                    # 1. Comprobar si este test tiene una acción de GUI asociada
                    gui_update_info = self.app_ref.test_gui_update_map.get(task['test_name'])  # Recordemos que "task" era un diccionario que tenía la clave "test_name"
                    success_callback = None # Por defecto, no hay callback

                    if gui_update_info:
                        message_type, attr_names = gui_update_info
                        # ************************************************************************************************************
                        # Llamamos directamente al método reutilizable que ya existe en la clase
                        success_callback = self.app_ref._create_gui_update_callback(message_type, attr_names)
                        # ************************************************************************************************************

                    # 2. Pasar el callback (o None si no hay) a la función de ejecución
                    task_result = robot_executor._run_robot_test(
                        self.app_ref,
                        test_name=task['test_name'],
                        variables=task.get('variables', []),
                        preferred_filename=task.get('filename'),
                        output_filename=output_file,
                        suppress_gui_updates=True,
                        on_success=success_callback  # <--  Si no se crea ningún callback especial para este test, el valor de success_callback será None y no se ejecutará nada extra.
                    )
                    
                    if os.path.exists(output_file_path):
                        xml_files.append(output_file_path)  # Guardamos el XML para el informe consolidado si se generó el archivo en el path guardado
                    else:
                        self.app_ref.gui_queue.put(('scheduler_log', f"⚠️  No se generó archivo de salida para '{task['name']}'.\n", "orange"))

                elif task['type'] == 'delay':
                    delay_seconds = int(task.get('duration', 5))
                    self.app_ref.gui_queue.put(('scheduler_log', f"  Pausando durante {delay_seconds} segundos...\n", "gray"))
                    
                    # Hacemos una pausa interrumpible
                    for _ in range(delay_seconds):
                        if self.app_ref.stop_sequence_event.is_set():
                            break
                        time.sleep(1)

                elif task['type'] == 'check_snmp_traps':
                    self.app_ref.gui_queue.put(('scheduler_log', "  Buscando nuevos traps SNMP...\n", "gray"))
                    new_traps = self.app_ref.trap_receiver.get_traps_since(timestamp_before_task)
                    
                    if new_traps:
                        self.app_ref.gui_queue.put(('scheduler_log', f"  ✔ Encontrados {len(new_traps)} traps nuevos.\n", "green"))
                        db_handler.save_traps_to_db(self.app_ref, new_traps, current_db_path)
                    else:
                        self.app_ref.gui_queue.put(('scheduler_log', "  - No se encontraron traps nuevos.\n", "gray"))
                    
                    # Actualizamos el timestamp para la siguiente tarea
                    timestamp_before_task = datetime.now(timezone.utc).isoformat()

                # ----------- MANEJAR RESULTADO DE LA TAREA -----------
                if task_result != 0:
                    self.app_ref.gui_queue.put(('scheduler_log', f"❌ Tarea '{task_name}' ha fallado.\n", "red"))
                    sequence_failed = True
                    if task.get('on_fail') == 'stop':
                        self.app_ref.gui_queue.put(('scheduler_log', "Política 'on_fail: stop'. Deteniendo la secuencia.\n", "red"))
                        break
                else:
                    self.app_ref.gui_queue.put(('scheduler_log', f"✔ Tarea '{task_name}' completada.\n", "green"))
                    
            # ----------- FINAL DE LA SECUENCIA -----------
        finally:
            self.app_ref.gui_queue.put(('scheduler_log', "--- Secuencia de tareas finalizada ---\n", "white"))

            # Generar informe consolidado si se ejecutaron tests
            if xml_files:
                self.app_ref.gui_queue.put(('scheduler_log', "Generando informe consolidado...\n", "gray"))
                try:
                # ***************************************************************************************************************************
                #  CORRECCIÓN: YA NO HAREMOS USO DE ESTO, SINO DE SUBPROCESS para llamar a rebot --- EN UN PROCESO A PARTE DEL DE LA GUI
                #     rebot_cli(['--name', 'Informe de Secuencia', 
                #             '--outputdir', 'test_results',
                #             '--log', 'log_consolidado.html',
                #             '--report', 'report_consolidado.html'] + xml_files)
                #     app_ref.gui_queue.put(('scheduler_log', "✔ Informe consolidado 'report_consolidado.html' creado.\n", "green"))
                # except Exception as e:
                #     app_ref.gui_queue.put(('scheduler_log', f"❌ Error al generar informe consolidado: {e}\n", "red"))
                # ***************************************************************************************************************************

            # Construir el comando para ejecutar rebot. Lo hacemos creando un proceso completamente separado para generar el informe. De esta forma si rebot falla no afecta a la app principal (GUI). Tambien podemos determinal un Timeout, asi la GUI no se puede quedar congelada.
                    command = [
                        sys.executable,  # Usa el mismo python que ejecuta la app
                        "-m", "robot.rebot",
                        "--name", "Informe de Secuencia",
                        "--outputdir", "test_results",
                        "--log", "log_consolidado.html",
                        "--report", "report_consolidado.html"
                    ] + xml_files

                    # Ejecutar el comando como un subproceso con un tiempo de espera
                    result = subprocess.run(
                        command, 
                        capture_output=True, 
                        text=True, 
                        timeout=30  # Espera un máximo de 30 segundos
                    )

                    if result.returncode == 0:
                        self.app_ref.gui_queue.put(('scheduler_log', "✔ Informe consolidado creado.\n", "green"))
                    else:
                        # Si rebot falla, muestra el error
                        error_output = result.stderr or result.stdout
                        self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error al generar informe: {error_output}\n", "red"))

                except subprocess.TimeoutExpired:
                    self.app_ref.gui_queue.put(('scheduler_log', "❌ Error: La generación del informe tardó demasiado (timeout).\n", "red"))

                except Exception as e:
                    self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error inesperado al generar informe: {e}\n", "red"))

            # Restaurar GUI
            final_message = "Secuencia completada con errores." if sequence_failed else "Secuencia completada con éxito."
            final_color = "red" if sequence_failed else "green"
            self.app_ref.gui_queue.put(('main_status', final_message, final_color))
            
            self.app_ref.gui_queue.put(('enable_buttons', None)) # Rehabilitamos botones
            

            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
                
    


