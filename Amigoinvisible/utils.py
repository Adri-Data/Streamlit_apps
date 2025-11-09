import json
import os
import streamlit as st

# --- Configuración Secreta ---
# NOTA: En una aplicación real, esta contraseña debería ser una variable de entorno
# o cargarse desde un archivo de configuración secreto (como st.secrets)
ADMIN_PASSWORD = "admin123" 

# --- Rutas y Nombres de Archivos ---
DATA_FILE = 'data.json'

def cargar_datos():
    """Carga los datos de emparejamientos y nombres desde el archivo JSON."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                datos = json.load(f)
                
            # Asegurar que el formato JSON cargado sea correcto para la app
            if not isinstance(datos.get("emparejamientos"), dict):
                st.error("Error en el formato del archivo data.json.")
                return {"nombres": [], "emparejamientos": {}}

            return {
                # Lista de nombres cargados
                "nombres": datos.get("nombres", []), 
                # Diccionario {numero: [regalador, receptor]}
                "emparejamientos": datos.get("emparejamientos", {}) 
            }
        except json.JSONDecodeError:
            st.error(f"Error al decodificar JSON en {DATA_FILE}. Archivo corrupto.")
            return {"nombres": [], "emparejamientos": {}}
    
    # Devuelve la estructura inicial si el archivo no existe
    return {"nombres": [], "emparejamientos": {}}

def guardar_datos(nombres: list, emparejamientos_numerados: dict):
    """Guarda los datos en el archivo JSON."""
    data_to_save = {
        "nombres": nombres, 
        "emparejamientos": emparejamientos_numerados
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data_to_save, f, indent=4)