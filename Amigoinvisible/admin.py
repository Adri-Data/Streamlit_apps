import os
import random
import secrets
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

from utils import ADMIN_PASSWORD, cargar_datos, guardar_datos


def generar_amigo_invisible(nombres, restricciones):
    """Find a complete randomized assignment, respecting every restriction."""
    if len(nombres) < 2 or len(set(nombres)) != len(nombres):
        return None, "Introduce al menos dos nombres únicos."
    if len(nombres) > 100:
        return None, "El máximo de esta interfaz es de 100 participantes por la matriz de restricciones."

    # Randomized augmenting-path matching finds a complete assignment in polynomial time.
    receptores_a_regalador = {}
    regaladores = nombres.copy()
    random.shuffle(regaladores)

    def buscar_receptor(regalador, visitados):
        opciones = [
            receptor for receptor in nombres
            if receptor != regalador and receptor not in restricciones.get(regalador, set())
        ]
        random.shuffle(opciones)
        for receptor in opciones:
            if receptor in visitados:
                continue
            visitados.add(receptor)
            anterior = receptores_a_regalador.get(receptor)
            if anterior is None or buscar_receptor(anterior, visitados):
                receptores_a_regalador[receptor] = regalador
                return True
        return False

    if not all(buscar_receptor(regalador, set()) for regalador in regaladores):
        return None, "No existe una asignación válida con esas restricciones."

    asignaciones = {regalador: receptor for receptor, regalador in receptores_a_regalador.items()}
    numeros = set()
    while len(numeros) < len(nombres):
        numeros.add(str(secrets.randbelow(900_000) + 100_000))
    emparejamientos_numerados = {
        numero: [regalador, asignaciones[regalador]]
        for numero, regalador in zip(numeros, nombres)
    }
    return emparejamientos_numerados, None


def _share_links(base_url, emparejamientos):
    base_url = base_url.strip().rstrip("/")
    if not base_url:
        return {}
    return {
        regalador: f"{base_url}/?{urlencode({'app_name': 'AmigoInvisible', 'user_name': regalador, 'number': numero})}"
        for numero, (regalador, _receptor) in emparejamientos.items()
    }


def admin_interface():
    st.subheader("⚙️ Administración del sorteo")
    password = st.text_input("Contraseña de administrador", type="password", key="admin_password_input")
    if password != ADMIN_PASSWORD:
        st.info("Introduce la contraseña para administrar el sorteo.")
        return
    st.success("Acceso de administración concedido.")

    datos = cargar_datos()
    if "nombres_input" not in st.session_state:
        st.session_state.nombres_input = ", ".join(datos["nombres"])

    nombres_input = st.text_area(
        "Participantes (separados por comas)", value=st.session_state.nombres_input,
        key="nombres_text_area",
    )
    st.session_state.nombres_input = nombres_input
    nombres = [nombre.strip() for nombre in nombres_input.split(",") if nombre.strip()]

    if len(nombres) != len(set(nombres)):
        st.error("Hay nombres repetidos. Cada participante debe tener un nombre único.")
        return

    st.markdown("### Restricciones")
    st.caption("Marca las combinaciones que no se permiten. Nadie puede regalarse a sí mismo.")
    restricciones = {nombre: set() for nombre in nombres}
    if nombres:
        header = st.columns([1] + [1] * len(nombres))
        header[0].write("Regalador ↓")
        for index, receptor in enumerate(nombres):
            header[index + 1].write(receptor)
        for regalador in nombres:
            cols = st.columns([1] + [1] * len(nombres))
            cols[0].write(regalador)
            for index, receptor in enumerate(nombres):
                key = f"restrict_{regalador}_{receptor}"
                if regalador == receptor:
                    restricciones[regalador].add(receptor)
                bloqueado = cols[index + 1].checkbox(
                    f"{regalador} no regala a {receptor}", key=key,
                    disabled=regalador == receptor,
                    value=True if regalador == receptor else st.session_state.get(key, False),
                    label_visibility="collapsed",
                )
                if bloqueado:
                    restricciones[regalador].add(receptor)

    base_url = st.text_input(
        "URL pública de la app (para crear enlaces completos)",
        value=os.environ.get("APP_BASE_URL", datos.get("base_url", "")),
        placeholder="https://tu-app.streamlit.app",
        help="Pega aquí la URL publicada de Streamlit. Se guardará para los próximos sorteos.",
    ).strip()

    if datos["emparejamientos"] and st.button("Guardar URL sin cambiar el sorteo"):
        guardar_datos(datos["nombres"], datos["emparejamientos"], base_url)
        st.success("URL guardada; el sorteo actual no ha cambiado.")

    if st.button("🎲 Generar y guardar sorteo", type="primary", use_container_width=True):
        emparejamientos, error = generar_amigo_invisible(nombres, restricciones)
        if error:
            st.error(error)
        else:
            guardar_datos(nombres, emparejamientos, base_url)
            st.success(f"Sorteo creado: {len(emparejamientos)} participantes y {len(emparejamientos)} receptores únicos.")
            links = _share_links(base_url, emparejamientos)
            if links:
                st.markdown("### Enlaces personales")
                st.caption("Envía a cada persona solo su enlace. Al abrirlo, deberá pulsar el botón para revelar su asignación.")
                st.dataframe(
                    pd.DataFrame([{"Participante": nombre, "Enlace privado": link} for nombre, link in links.items()]),
                    hide_index=True, use_container_width=True,
                    column_config={"Enlace privado": st.column_config.LinkColumn("Enlace privado", display_text="Abrir enlace")},
                )
            else:
                st.warning("El sorteo está guardado. Añade la URL pública de la app y vuelve a generar para obtener enlaces completos.")

    st.markdown("---")
    actual = cargar_datos()
    emparejamientos = actual["emparejamientos"]
    if emparejamientos:
        st.markdown("### Sorteo guardado")
        st.success(f"{len(actual['nombres'])} participantes; {len(emparejamientos)} asignaciones.")
        st.caption("Cada participante aparece exactamente una vez como regalador y una vez como receptor.")
        links = _share_links(base_url or actual.get("base_url", ""), emparejamientos)
        if links:
            st.dataframe(
                pd.DataFrame([{"Participante": nombre, "Enlace privado": link} for nombre, link in links.items()]),
                hide_index=True, use_container_width=True,
                column_config={"Enlace privado": st.column_config.LinkColumn("Enlace privado", display_text="Abrir enlace")},
            )
    else:
        st.info("Todavía no hay ningún sorteo guardado.")
