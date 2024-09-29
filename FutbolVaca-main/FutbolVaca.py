import streamlit as st
import json
import os

# Configuración de la página
st.set_page_config(
    page_title="XVI Grand Prix Peñero 2024",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Constantes
ADMIN_PASSWORD = "Admin1"
TORNEO_FILE = "torneo.json"
RONDAS = ['Octavos', 'Cuartos', 'Semifinal', 'Final']

# Funciones auxiliares
def cargar_torneo():
    if os.path.exists(TORNEO_FILE):
        with open(TORNEO_FILE, 'r') as f:
            return json.load(f)
    return []

def guardar_torneo(torneo):
    with open(TORNEO_FILE, 'w') as f:
        json.dump(torneo, f)

def inicializar_equipo(nombre):
    return {
        "nombre": nombre,
        "rondas": {ronda: {"cruces": []} for ronda in RONDAS}
    }

def crear_partido(torneo, ronda, equipo1, equipo2):
    # Verificar si los equipos ya están en el cruce
    for equipo in torneo:
        if equipo["nombre"] == equipo1 or equipo["nombre"] == equipo2:
            equipo["rondas"][ronda]["cruces"].append({"equipo1": equipo1, "equipo2": equipo2, "goles": [0, 0]})
    return torneo

def añadir_resultado(torneo, ronda, equipo1, equipo2, resultado):
    for equipo in torneo:
        for cruce in equipo["rondas"][ronda]["cruces"]:
            if cruce["equipo1"] == equipo1 and cruce["equipo2"] == equipo2:
                cruce["goles"] = [int(resultado.split('-')[0]), int(resultado.split('-')[1])]
    return torneo

def obtener_ganador(cruce):
    goles1 = cruce["goles"][0]
    goles2 = cruce["goles"][1]
    if goles1 > goles2:
        return cruce["equipo1"]
    elif goles2 > goles1:
        return cruce["equipo2"]
    return None  # Empate

def generar_siguientes_rondas(torneo):
    for i, ronda in enumerate(RONDAS[:-1]):
        siguiente_ronda = RONDAS[i + 1]
        ganadores = []
        for cruce in [cruce for equipo in torneo for cruce in equipo["rondas"][ronda]["cruces"]]:
            if cruce["goles"] != [0, 0]:  # Solo considerar cruces con resultados
                ganador = obtener_ganador(cruce)
                if ganador:
                    ganadores.append(ganador)

        # Crear cruces para la siguiente ronda
        for j in range(0, len(ganadores), 2):
            if j + 1 < len(ganadores):  # Asegurarse de que haya un par
                torneo = crear_partido(torneo, siguiente_ronda, ganadores[j], ganadores[j + 1])
    return torneo

# Cargar torneo al inicio
if 'torneo' not in st.session_state:
    st.session_state.torneo = cargar_torneo()

# Título principal
st.markdown("<h1 style='text-align: center;'>🏆🐂 XVI Grand Prix Peñero 2024 🐂🏆</h1>", unsafe_allow_html=True)

# Mostrar las eliminatorias
for ronda in RONDAS:
    st.markdown(f"<h3 style='text-align: center;'>{ronda}</h3>", unsafe_allow_html=True)
    for equipo in st.session_state.torneo:
        for cruce in equipo["rondas"][ronda]["cruces"]:
            if cruce:
                ganador = obtener_ganador(cruce)
                color_equipo1 = 'green' if ganador == cruce['equipo1'] else 'red' if ganador == cruce['equipo2'] else 'black'
                color_equipo2 = 'green' if ganador == cruce['equipo2'] else 'red' if ganador == cruce['equipo1'] else 'black'
                st.markdown(f"<div style='border: 1px solid #ccc; padding: 10px; border-radius: 5px; text-align: center;'>"
                             f"<h4 style='color: {color_equipo1};'>{cruce['equipo1']} {cruce['goles'][0]} - {cruce['goles'][1]} {cruce['equipo2']}</h4>"
                             f"</div>", unsafe_allow_html=True)
                st.markdown("---")

# Sección de administrador
with st.expander("Opciones avanzadas"):
    password = st.text_input("Contraseña", type="password")
    if password == ADMIN_PASSWORD:
        nuevo_equipo = st.text_input("Añadir nuevo equipo")
        if st.button("Añadir equipo") and nuevo_equipo:
            # Verificar si el equipo ya existe
            if any(equipo["nombre"] == nuevo_equipo for equipo in st.session_state.torneo):
                st.warning("El equipo ya existe.")
            else:
                st.session_state.torneo.append(inicializar_equipo(nuevo_equipo))
                guardar_torneo(st.session_state.torneo)
                st.success(f"Equipo {nuevo_equipo} añadido")

        # Crear partidos
        ronda = st.selectbox("Seleccionar ronda para crear partido", options=RONDAS)
        equipo1 = st.selectbox("Equipo 1", options=[e["nombre"] for e in st.session_state.torneo])
        equipo2 = st.selectbox("Equipo 2", options=[e["nombre"] for e in st.session_state.torneo if e["nombre"] != equipo1])

        if st.button("Crear partido"):
            if equipo1 != equipo2:  # Asegurarse de que los equipos sean diferentes
                st.session_state.torneo = crear_partido(st.session_state.torneo, ronda, equipo1, equipo2)
                guardar_torneo(st.session_state.torneo)
                st.success("Partido creado")
            else:
                st.warning("Por favor, selecciona dos equipos diferentes.")

        # Actualizar resultados
        st.subheader("Actualizar resultados")
        ronda_resultado = st.selectbox("Seleccionar ronda para actualizar resultado", options=RONDAS)
        partidos_en_ronda = []

        # Crear una lista de partidos en el formato deseado
        for e in st.session_state.torneo:
            for cruce in e["rondas"][ronda_resultado]["cruces"]:
                partidos_en_ronda.append(f"{cruce['equipo1']} vs {cruce['equipo2']}")

        partido_seleccionado = st.selectbox("Seleccionar partido", options=partidos_en_ronda)

        if partido_seleccionado:
            equipo1, equipo2 = partido_seleccionado.split(" vs ")
            resultado = st.text_input("Resultado (formato: X-Y)")

            if st.button("Actualizar resultado"):
                if resultado and '-' in resultado:
                    st.session_state.torneo = añadir_resultado(st.session_state.torneo, ronda_resultado, equipo1, equipo2, resultado)
                    st.session_state.torneo = generar_siguientes_rondas(st.session_state.torneo)
                    guardar_torneo(st.session_state.torneo)
                    st.success("Resultado actualizado y siguientes rondas generadas")
                else:
                    st.warning("Por favor, ingresa un resultado válido en el formato X-Y.")

# Pie de página
st.markdown("---")
st.markdown("<p style='text-align: center;'>¡Disfruteu del Gran Prix Peñeros! 🎉🏆</p>", unsafe_allow_html=True)