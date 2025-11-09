import streamlit as st
from utils import cargar_datos

def user_interface():
    st.title("Consulta de Amigo Invisible 🎁")
    st.subheader("Ingresa tu número secreto para ver a quién regalar")
    
    # Cargar datos de la fuente de verdad (JSON)
    datos = cargar_datos()
    emparejamientos_numerados = datos["emparejamientos"]

    if not emparejamientos_numerados:
        st.warning("⚠️ El Administrador aún no ha generado el Amigo Invisible. Inténtalo más tarde.")
        return

    # Usar un input de texto para el número, evitando que se vea como un contador
    numero_str = st.text_input("Ingrese su Número Secreto (por ejemplo, 12)", max_chars=2, key="user_number_input")

    if st.button("Consultar Mi Amigo Invisible"):
        if not numero_str.isdigit():
            st.warning("Por favor, ingresa un número válido.")
            return
            
        # El JSON guarda los números como claves de string
        if numero_str in emparejamientos_numerados:
            # Formato: [nombre_regalador, nombre_receptor]
            nombre_regalador, nombre_receptor = emparejamientos_numerados[numero_str]
            st.snow()
            st.balloons() # Pequeña celebración visual
            #st.success(f"🎉 ¡Felicidades, **{nombre_regalador}**! 🎉")
            st.success(f"🎉 ¡Felicidades, tienes que hacerle el regalo a: **{nombre_receptor}**.")
            st.markdown("---")
            st.markdown("🤫 ¡Guarda el secreto!")
            
        else:
            st.error("Número Secreto no válido o no asignado. Vuelve a intentarlo.")