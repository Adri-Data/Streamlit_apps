import streamlit as st
import random
import pandas as pd
# Importa tus funciones utils y ADMIN_PASSWORD aquí
from utils import cargar_datos, guardar_datos, ADMIN_PASSWORD
import json

# --- La función generar_amigo_invisible() y otras funciones de utilidad se mantienen IGUAL. ---
# Asegúrate de que las funciones cargar_datos, guardar_datos, generar_amigo_invisible y ADMIN_PASSWORD
# están definidas o importadas correctamente desde utils.py o al inicio de admin.py.
# ---
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
    
    # 2. Algoritmo de reintentos
    for _ in range(max_intentos):
        regaladores = nombres.copy()
        receptores = nombres.copy()
        random.shuffle(regaladores) 
        emparejamientos_intento = {}
        
        exito = True
        for regalador in regaladores:
            opciones = [r for r in receptores 
                        if r != regalador 
                        and r not in restricciones.get(regalador, [])]
            
            if not opciones:
                exito = False
                break
                
            elegido = random.choice(opciones)
            emparejamientos_intento[regalador] = elegido
            receptores.remove(elegido)

        if exito and not receptores:
            emparejamientos = emparejamientos_intento
            break
            
    if emparejamientos is None:
        st.error(f"⚠️ No se pudo generar una asignación válida después de {max_intentos} intentos. "
                 f"Revisa tus restricciones.")
        return None, None

    # 3. Asignación de Números Secretos
    numeros_asignados = set()
    emparejamientos_numerados = {}
    
    for nombre, amigo in emparejamientos.items():
        while True:
            numero = random.randint(00, 99) 
            if numero not in numeros_asignados:
                numeros_asignados.add(numero)
                emparejamientos_numerados[str(numero)] = [nombre, amigo] 
                break

    return emparejamientos_numerados, emparejamientos
# --- Interfaz de Administración ---

def admin_interface():
    st.subheader("⚙️ Área de Administración (Sorteo y Configuración)")
    
    # 1. Autenticación (se mantiene igual)
    password = st.text_input("Ingrese la contraseña de administrador", type="password", key="admin_password_input")
    
    if password != ADMIN_PASSWORD:
        st.warning("Contraseña incorrecta. Inténtalo de nuevo.")
        return
        
    st.success("Contraseña correcta. ¡Bienvenido!")
    
    datos_persistentes = cargar_datos()
    
    # --- Inicialización del Estado de Sesión ---
    
    # Inicializar el estado para los nombres
    if 'nombres_input' not in st.session_state:
        st.session_state.nombres_input = ", ".join(datos_persistentes.get("nombres", [])) if datos_persistentes.get("nombres") else ""
        
    # Inicializar el estado para las restricciones con Checkboxes (NUEVO ESTADO)
    # Este estado guardará las restricciones del último sorteo para precargar los checkboxes.
    if 'restricciones_checkboxes' not in st.session_state:
        # Aquí usaremos un diccionario anidado para rastrear el estado de las restricciones
        # {Regalador: {Receptor: True/False, ...}}
        st.session_state.restricciones_checkboxes = {}


    # 2. Configuración de Nombres (se mantiene igual)
    st.markdown("---")
    st.markdown("### 1. Lista de Participantes")
    nombres_input = st.text_area(
        "Nombres (separados por comas: Juan, María, Pedro)", 
        st.session_state.nombres_input,
        key="nombres_text_area" 
    )
    st.session_state.nombres_input = nombres_input
    nombres = [n.strip() for n in nombres_input.split(",") if n.strip()]
    
    # Asegúrate de que haya nombres para el siguiente paso
    if not nombres:
        st.warning("Por favor, introduce los nombres de los participantes arriba.")
        st.markdown("---")
        # Si no hay nombres, no mostramos la sección de restricciones ni el botón de generar
        return 

    # 3. Configuración de Restricciones (¡MODIFICADO: Usamos Checkboxes!)
    st.markdown("---")
    st.markdown("### 2. Restricciones de Emparejamiento 🛑")
    st.markdown("Marca la casilla si el **Regalador** (fila) NO puede regalar al **Receptor** (columna).")
    
    # Crear un diccionario temporal para las restricciones que se enviarán al algoritmo
    restricciones_algoritmo = {nombre: [] for nombre in nombres}
    
    # 3.1 Encabezado de la Matriz (Nombres de Receptores)
    # Creamos las columnas para el diseño de matriz
    cols = st.columns([1] + [1] * len(nombres))
    
    # Primera columna (vacía) + Nombres de Receptores
    cols[0].write("**Regalador ↓**")
    for i, receptor in enumerate(nombres):
        cols[i+1].write(f"**{receptor}**")

    st.markdown("---")

    # 3.2 Cuerpo de la Matriz (Filas de Checkboxes)

    # Recorrer cada nombre como el Regalador
    for regalador in nombres:
        # Crear la fila de columnas para el Regalador actual
        row_cols = st.columns([1] + [1] * len(nombres))
        row_cols[0].write(f"**{regalador}**") # Nombre del Regalador

        # Recorrer cada nombre como el Receptor
        for i, receptor in enumerate(nombres):
            # 1. Creamos la clave única
            checkbox_key = f"restrict_{regalador}_{receptor}"
            
            # 2. **¡Solución al KeyError!** Inicializar la clave SI NO EXISTE
            # Esto asegura que si la lista de nombres cambia (y las claves también),
            # siempre habrá un valor inicial (False) antes de acceder.
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False

            # No permitir que una persona se regale a sí misma (siempre restringido)
            is_disabled = (regalador == receptor)
            
            # Creamos la etiqueta descriptiva, aunque se oculte
            unique_label = f"Restricción: {regalador} no regala a {receptor}"
            
            # 3. Crear el checkbox, usando el valor de sesión ya inicializado
            is_restricted = row_cols[i+1].checkbox(
                label=unique_label, 
                value=st.session_state[checkbox_key], # <-- ¡Ahora el valor existe siempre!
                key=checkbox_key, 
                disabled=is_disabled,
                label_visibility="collapsed" 
            )
            
            # 4. Procesar el estado del Checkbox
            if is_restricted:
                # La inicialización del diccionario ya se hizo antes del bucle
                restricciones_algoritmo[regalador].append(receptor)


    # 4. Generación y Guardado
    st.markdown("---")
    if st.button("✨ Generar y Guardar Amigo Invisible", use_container_width=True):
        
        if not nombres:
            st.error("La lista de participantes está vacía. Añade nombres primero.")
            return

        # La generación ocurre aquí...
        # ... (código de generación se mantiene igual) ...

        emparejamientos_numerados, emparejamientos_originales = generar_amigo_invisible(nombres, restricciones_algoritmo)
        
        if emparejamientos_numerados:
            st.success("¡Amigo Invisible Generado con éxito!")
            
            # GUARDAR DATOS PERSISTENTEMENTE
            guardar_datos(nombres, emparejamientos_numerados)
            
            # Actualizar el estado de la sesión para la consulta inmediata
            st.session_state.nombres = nombres
            st.session_state.emparejamientos_numerados = emparejamientos_numerados

            # Mostrar resultados para el administrador
            st.subheader("Resultados Generados (Solo Admin)")
            
            # 1. Crear el DataFrame completo
            df_resultados = pd.DataFrame([
                (n, amigo, numero) 
                for numero, (n, amigo) in emparejamientos_numerados.items()
            ], columns=["Regalador", "Receptor", "Número Secreto"]) 

            # 2. Checkbox de Debug para mostrar la columna 'Receptor' (Amigo Secreto)
            # Usamos un st.container para controlar el diseño del checkbox
            with st.container():
                mostrar_receptor = st.checkbox("Mostrar Receptor Secreto (Modo Debug)", key="debug_receptor")
            
            # 3. Aplicar filtro de columnas según el estado del checkbox
            if mostrar_receptor:
                # Mostrar todas las columnas (Modo Debug)
                df_mostrar = df_resultados
                st.warning("⚠️ MODO DEBUG ACTIVO: La columna 'Receptor' revela el Amigo Secreto.")
            else:
                # Ocultar la columna 'Receptor' (Modo Seguro para compartir)
                df_mostrar = df_resultados[["Regalador", "Número Secreto"]]
                st.info("MODO SEGURO: Solo se muestran los números para distribuir.")
            
            st.dataframe(df_mostrar, use_container_width=True)
            st.caption("Distribuye el Número Secreto a cada Regalador. Ellos lo usarán en la sección 'Consulta'.")
    # 5. Visualización del Estado Actual (se mantiene igual)
    st.markdown("---")
    st.markdown("### Estado Actual del Sorteo Guardado")
    if datos_persistentes.get("emparejamientos"):
        st.info(f"Hay **{len(datos_persistentes['nombres'])}** participantes cargados y **{len(datos_persistentes['emparejamientos'])}** emparejamientos generados.")
        st.caption("Esta información proviene del último sorteo guardado en 'data.json'.")
    else:
        st.info("Aún no se ha generado ningún sorteo.")