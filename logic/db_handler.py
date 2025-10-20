import sqlite3
import json
import os
from tkinter import filedialog, messagebox

def initialize_database(db_path):
    """Asegura que el archivo de BD y la tabla 'traps' existan en la ruta especificada."""
    conn = sqlite3.connect(db_path) # Crea una conexión local
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_received TEXT NOT NULL,
            source_address TEXT NOT NULL,
            event_type TEXT NOT NULL,
            varbinds_json TEXT
        )
    ''')
    conn.commit()
    conn.close()
    

def save_traps_to_db(app_ref, traps_list, db_path):
    """Guarda una lista de traps en la base de datos especificada por db_path, gestionando su propia conexión."""
    if not traps_list:
        return
    try:
        conn = sqlite3.connect(db_path)    # Crea una conexión local nueva para este hilo. De esta forma evitamos problemas de concurrencia
        cursor = conn.cursor()
        for trap in traps_list:
            varbinds_str = json.dumps(trap.get('varbinds_dict', {}))
            cursor.execute(
                "INSERT INTO traps (timestamp_received, source_address, event_type, varbinds_json) VALUES (?, ?, ?, ?)",
                (trap['timestamp_received_utc'], trap['source_address'], trap['event_type'], varbinds_str)
            )
        conn.commit()
        conn.close() # Cierra la conexión al terminar
        app_ref.gui_queue.put(('main_status', f"Guardados {len(traps_list)} traps nuevos en la BD {os.path.basename(db_path)}.", "cyan"))   # Utilizamos {os.path.basename() para no mostrar la ruta completa, solo el nombre del archivo
        
    except Exception as e:
        app_ref.gui_queue.put(('main_status', f"Error al guardar traps en {db_path}: {e}", "red"))

def fetch_traps_from_db(db_path):
    """Se conecta a una BD, extrae todos los traps y los devuelve como una lista."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp_received, event_type, source_address, varbinds_json FROM traps ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        # En lugar de actualizar la GUI, devuelve el error para que el controlador decida qué hacer
        print(f"Error al leer la base de datos: {e}")
        return None


