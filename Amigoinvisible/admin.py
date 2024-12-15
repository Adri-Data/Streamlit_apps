import streamlit as st
import random
import json
import os
import pandas as pd

# Función para cargar datos desde un archivo JSON
def cargar_datos():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            return json.load(f)
    return {"nombres": [], "emparejamientos": {}}

# Función para guardar datos en un archivo JSON
def guardar_datos(nombres, emparejamientos_numerados):
    with open('data.json', 'w') as f:
        json.dump({"nombres": nombres, "emparejamientos": emparejamientos_numerados}, f)

# Función para generar el amigo invisible
def generar_amigo_invisible(nombres, restricciones):
    emparejamientos = {}
    disponibles = nombres.copy()

    # Intentar emparejar a cada persona
    for nombre in nombres:
        opciones = [n for n in disponibles if n != nombre and n not in restricciones.get(nombre, [])]
        
        if opciones:
            elegido = random.choice(opciones)
            emparejamientos[nombre] = elegido
            disponibles.remove(elegido)
        else:
            st.warning(f"No se puede asignar un amigo invisible para {nombre}. "
                       f"Opciones disponibles: {', '.join(disponibles)}. "
                       f"Restricciones: {', '.join(restricciones.get(nombre, []))}.")
            return None

    # Verificar que no haya emparejamientos inválidos
    for nombre, amigo in emparejamientos.items():
        if amigo in restricciones.get(nombre, []):
            st.warning(f"Emparejamiento inválido: {nombre} no puede regalar a {amigo}.")
            return None

    # Asignar números aleatorios entre 1 y 100 a los emparejamientos
    numeros_asignados = set()
    emparejamientos_numerados = {}
    
    for nombre, amigo in emparejamientos.items():
        while True:
            numero = random.randint(1, 100)
            if numero not in numeros_asignados:
                numeros_asignados.add(numero)
                emparejamientos_numerados[numero] = (nombre, amigo)
                break

    return emparejamientos_numerados, emparejamientos  # Devolver también el emparejamiento original

# Función para mostrar la interfaz de administración
def admin_interface():
    st.subheader("Área de Administración")
    
    password = st.text_input("Ingrese la contraseña de administrador", type="password")
    
    if password == "admin123":  # Cambia esta contraseña por una más segura
        st.success("Contraseña correcta. ¡Bienvenido, Administrador!")
        
        # Cargar datos existentes
        datos = cargar_datos()
        nombres = datos["nombres"]
        emparejamientos = datos["emparejamientos"]

        # Mantener la información en los botones
        if 'nombres_input' not in st.session_state:
            st.session_state.nombres_input = ", ".join(nombres) if nombres else "Alice, Bob, Carl, David, Eva"
        if 'restricciones_input' not in st.session_state:
            st.session_state.restricciones_input = "Alice: [Bob], Bob: [Alice], Carl: [David]"

        nombres_input = st.text_area("Nombres (separados por comas)", st.session_state.nombres_input)
        restricciones_input = st.text_area("Restricciones (formato: nombre: [nombre1, nombre2])", st.session_state.restricciones_input)

        if st.button("Generar Amigo Invisible"):
            st.session_state.nombres_input = nombres_input  # Guardar nombres en el estado de la sesión
            st.session_state.restricciones_input = restricciones_input  # Guardar restricciones en el estado de la sesión
            
            nombres = [nombre.strip() for nombre in nombres_input.split(",")]
            restricciones = {}
            
            for line in restricciones_input.splitlines():
                if ":" in line:
                    try:
                        nombre, restriccion = line.split(":")
                        restricciones[nombre.strip()] = [n.strip() for n in restriccion.strip()[1:-1].split(",") if n.strip()]
                    except ValueError:
                        st.warning("Formato de restricciones incorrecto. Asegúrate de usar 'nombre: [nombre1, nombre2]'.")

            emparejamientos_numerados, emparejamientos = generar_amigo_invisible(nombres, restricciones)
            
            if emparejamientos_numerados:
                st.subheader("Resultados")
                for numero, (nombre, amigo) in emparejamientos_numerados.items():
                    st.write(f"{nombre} tiene que hacerle el regalo al número {numero}.")
                st.session_state.emparejamientos_numerados = emparejamientos_numerados  # Guardar emparejamientos numerados en el estado de la sesión
                st.session_state.emparejamientos = emparejamientos  # Guardar emparejamientos originales en el estado de la sesión
                
                # Guardar datos en el archivo JSON
                guardar_datos(nombres, emparejamientos_numerados)
    else:
        st.warning("Contraseña incorrecta. Inténtalo de nuevo.")