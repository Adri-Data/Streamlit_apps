import streamlit as st
from admin import admin_interface
import json
import os
import pandas as pd

# Función para cargar datos desde un archivo JSON
def cargar_datos():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            return json.load(f)
    return {"nombres": [], "emparejamientos": {}}

def user_interface():
    st.title("Consulta de Amigo Invisible 🎁")
    st.subheader("Consulta quién te toca regalar")
    
    if 'emparejamientos_numerados' not in st.session_state:
        st.warning("No se han generado emparejamientos aún.")
        return
    emparejamientos = st.session_state.emparejamientos

    numero = st.number_input("Ingrese su número (por ejemplo, 1, 2, ...)", min_value=1, max_value=100)

    if st.button("Consultar"):

        if str(numero) in emparejamientos.keys():
            nombre, amigo = emparejamientos[str(numero)]
            st.write(f"{nombre}, tienes que hacerle el regalo a {amigo}.")
        else:
            st.warning("Número no válido o no asignado.")

# Lógica principal
if __name__ == "__main__":
    st.set_page_config(page_title="Amigo Invisible ❄️", layout="centered", page_icon="❄️", initial_sidebar_state="collapsed")  # Configuración de la página
    st.title("Asignador de Amigo Invisible 🎄")
    
    # Cargar datos existentes
    datos = cargar_datos()
    st.session_state.nombres = datos["nombres"]
    st.session_state.emparejamientos = datos["emparejamientos"]
    st.session_state.emparejamientos_numerados = datos.get("emparejamientos_numerados", {})  # Inicializar si no hay datos

    # Navegación
    st.sidebar.title("Navegación")
    page = st.sidebar.radio("Selecciona una página:", ("Consulta", "Administración"))

    if page == "Administración":
        admin_interface()  # Llamar a la interfaz de administración
    else:
        user_interface()  # Llamar a la interfaz de consulta

    # Decoración navideña
    st.markdown("""
        <style>
            .stApp {
                background-image: url('https://www.transparentpng.com/thumb/snowflake/snowflake-png-transparent-image-1.png');
                background-size: cover;
            }
        </style>
    """, unsafe_allow_html=True)
