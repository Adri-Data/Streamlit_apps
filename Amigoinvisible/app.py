import streamlit as st
from admin import admin_interface
from user_interface import user_interface
from utils import cargar_datos

# --- Lógica principal ---
if __name__ == "__main__":
    
    # 1. Configuración de la Página
    st.set_page_config(
        page_title="Amigo Invisible 25 ❄️", 
        layout="centered", 
        page_icon="🎁", 
        initial_sidebar_state="auto"
    )
    st.title("Asignador de Amigo Invisible 🎄")
    
    # 2. Cargar datos persistentes
    datos = cargar_datos()
    
    # Inicializar el estado de la sesión con los datos persistentes
    st.session_state.nombres = datos["nombres"]
    st.session_state.emparejamientos_numerados = datos["emparejamientos"]

    # 3. Navegación
    st.sidebar.title("Navegación")
    page = st.sidebar.radio(
        "Selecciona una página:", 
        ("Consulta (Usuario)", "Administración (Sorteo)")
    )

    st.markdown("---")

    # 4. Enrutamiento
    if page == "Administración (Sorteo)":
        admin_interface() 
    else:
        user_interface() 

    # 5. Decoración (Mejor uso de emojis y estilos Streamlit)
    st.sidebar.markdown("""
        ---
        ### ☃️ ¡Felices Fiestas! 🎅
        Crea tu sorteo de Amigo Invisible.
    """)