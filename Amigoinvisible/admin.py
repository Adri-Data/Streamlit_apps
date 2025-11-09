import streamlit as st
import random
import pandas as pd
from utils import cargar_datos, guardar_datos, ADMIN_PASSWORD

# --- Lógica de Generación ---

def generar_amigo_invisible(nombres: list, restricciones: dict, max_intentos=10):
    """
    Intenta generar el Amigo Invisible con restricciones.
    Retorna (emparejamientos_numerados, emparejamientos_originales) o None.
    """
    
    # 1. Validación inicial
    if len(nombres) < 2:
        st.warning("Se necesitan al menos dos nombres para generar el Amigo Invisible.")
        return None, None
    if len(set(nombres)) != len(nombres):
        st.warning("La lista de nombres contiene duplicados. Por favor, elimínelos.")
        return None, None

    emparejamientos = None
    
    # 2. Algoritmo de reintentos para evitar callejones sin salida
    for _ in range(max_intentos):
        regaladores = nombres.copy()
        receptores = nombres.copy()
        random.shuffle(regaladores) # Orden aleatorio para intentar
        emparejamientos_intento = {}
        
        exito = True
        for regalador in regaladores:
            # Filtra receptores: no puede ser él mismo, ni estar en la lista de restricciones
            opciones = [r for r in receptores 
                        if r != regalador 
                        and r not in restricciones.get(regalador, [])]
            
            if not opciones:
                # Falló la asignación, necesitamos reintentar
                exito = False
                break
                
            elegido = random.choice(opciones)
            emparejamientos_intento[regalador] = elegido
            receptores.remove(elegido)

        if exito and not receptores: # Éxito si todos fueron emparejados y la lista de receptores está vacía
            emparejamientos = emparejamientos_intento
            break
            
    if emparejamientos is None:
        st.error(f"⚠️ No se pudo generar una asignación válida después de {max_intentos} intentos. "
                 f"Revisa tus restricciones.")
        return None, None

    # 3. Asignación de Números Secretos
    numeros_asignados = set()
    emparejamientos_numerados = {}
    
    # Asignar un número único a cada regalador (clave es el número)
    for nombre, amigo in emparejamientos.items():
        while True:
            # Rango de números más amplio para mayor sensación de aleatoriedad
            numero = random.randint(00, 99)
            if numero not in numeros_asignados:
                numeros_asignados.add(numero)
                # Formato: {numero_secreto: [regalador, receptor]}
                emparejamientos_numerados[str(numero)] = [nombre, amigo] 
                break

    return emparejamientos_numerados, emparejamientos

# --- Interfaz de Administración ---

def admin_interface():
    st.subheader("⚙️ Área de Administración (Sorteo y Configuración)")
    
    # 1. Autenticación
    password = st.text_input("Ingrese la contraseña de administrador", type="password", key="admin_password_input")
    
    if password != ADMIN_PASSWORD:
        st.warning("Contraseña incorrecta. Inténtalo de nuevo.")
        return
        
    st.success("Contraseña correcta. ¡Bienvenido!")
    
    # Cargar datos para el estado inicial de los inputs
    datos = cargar_datos()
    
    # Inicializar el estado de sesión para mantener los valores en los widgets
    if 'nombres_input' not in st.session_state:
        st.session_state.nombres_input = ", ".join(datos["nombres"]) if datos["nombres"] else ""
    if 'restricciones_data' not in st.session_state:
        # Inicializar un DataFrame vacío o con datos de ejemplo
        st.session_state.restricciones_data = pd.DataFrame({
            "Regalador": ["Alice", "Bob"], 
            "No puede regalar a": ["Bob", "Alice"]
        })

    # 2. Configuración de Nombres
    st.markdown("---")
    st.markdown("### 1. Lista de Participantes")
    st.session_state.nombres_input = st.text_area(
        "Nombres (separados por comas: Juan, María, Pedro)", 
        st.session_state.nombres_input
    )
    nombres = [n.strip() for n in st.session_state.nombres_input.split(",") if n.strip()]

    # 3. Configuración de Restricciones (Usando un Data Editor para mejor UX)
    st.markdown("---")
    st.markdown("### 2. Restricciones (Quién NO puede regalar a quién)")
    st.markdown("Añade filas: **Regalador** y el **Nombre** del que NO puede ser receptor.")

    # Usar el Data Editor para una edición más estructurada
    st.session_state.restricciones_data = st.data_editor(
        st.session_state.restricciones_data,
        column_config={
            "Regalador": st.column_config.SelectboxColumn("Regalador", options=nombres),
            "No puede regalar a": st.column_config.SelectboxColumn("No puede regalar a", options=nombres)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor_restricciones"
    )

    # Procesar el DataFrame de restricciones a un diccionario
    restricciones = {}
    if not st.session_state.restricciones_data.empty:
        for index, row in st.session_state.restricciones_data.iterrows():
            regalador = row["Regalador"]
            receptor_prohibido = row["No puede regalar a"]
            if regalador and receptor_prohibido:
                if regalador in restricciones:
                    restricciones[regalador].append(receptor_prohibido)
                else:
                    restricciones[regalador] = [receptor_prohibido]


    # 4. Generación y Guardado
    st.markdown("---")
    if st.button("✨ Generar y Guardar Amigo Invisible"):
        if not nombres:
            st.warning("La lista de nombres está vacía.")
            return

        # Limpiar restricciones duplicadas y autorrestricciones
        restricciones_limpias = {}
        for r, prohibidos in restricciones.items():
             restricciones_limpias[r] = list(set([p for p in prohibidos if p != r]))

        emparejamientos_numerados, emparejamientos_originales = generar_amigo_invisible(nombres, restricciones_limpias)
        
        if emparejamientos_numerados:
            st.success("¡Amigo Invisible Generado con éxito!")
            
            # Guardar el estado
            guardar_datos(nombres, emparejamientos_numerados)
            
            # Mostrar resultados de forma segura para el administrador
            st.subheader("Resultados Generados (Solo Admin)")
            df_resultados = pd.DataFrame([
                (n, amigo, numero) 
                for numero, (n, amigo) in emparejamientos_numerados.items()
            # ], columns=["Regalador", "Receptor", "Número Secreto"])
            ], columns=["Regalador", "Número Secreto"])
            # Mostrar al Admin para que sepa los números a enviar
            st.dataframe(df_resultados)
            st.info("Distribuye el **Número Secreto** a cada Regalador. Ellos lo usarán en la sección 'Consulta'.")
            
            # Actualizar el estado global de la aplicación
            st.session_state.nombres = nombres
            st.session_state.emparejamientos_numerados = emparejamientos_numerados

    # 5. Visualización del Estado Actual
    st.markdown("---")
    st.markdown("### Estado Actual (JSON Guardado)")
    if datos["emparejamientos"]:
        st.success(f"Hay **{len(datos['nombres'])}** participantes cargados y **{len(datos['emparejamientos'])}** emparejamientos generados.")
    else:
        st.info("Aún no se ha generado ningún sorteo o el archivo está vacío.")