from html import escape

import streamlit as st

from utils import cargar_datos


def _query_params():
    """Read Streamlit query parameters across supported Streamlit versions."""
    try:
        return dict(st.query_params)
    except Exception:
        legacy = st.experimental_get_query_params()
        return {key: values[-1] if isinstance(values, list) else values for key, values in legacy.items()}


def _assignment_identity(user_name, numero):
    user_name = str(user_name or "").strip()
    numero = str(numero or "").strip()
    if not user_name or not numero.isdigit():
        return ""
    return f"{user_name.casefold()}:{int(numero)}"


def is_reveal_screen():
    """Whether the current URL and session are showing a revealed assignment."""
    params = _query_params()
    user_name = params.get("user_name") or st.session_state.get("user_name_input", "")
    numero = params.get("number") or st.session_state.get("user_number_input", "")
    identity = _assignment_identity(user_name, numero)
    return bool(identity and identity == st.session_state.get("revealed_assignment_identity"))


def _show_reveal(nombre_receptor):
    st.markdown(
        """
        <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], footer {display: none !important;}
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(ellipse at top, #253b60 0%, #101827 58%, #090d16 100%);
        }
        [data-testid="stMain"] .block-container {
            min-height: 100vh; max-width: 100% !important; padding: 0 1.5rem !important;
            display: flex; align-items: center; justify-content: center;
        }
        .reveal-card {text-align: center; padding: clamp(2rem, 7vw, 5rem); width: min(100%, 1100px);}
        .reveal-icon {font-size: clamp(3rem, 8vw, 6rem); line-height: 1; margin-bottom: 1.5rem;}
        .reveal-kicker {color: #c8d8f1; font-size: clamp(1.2rem, 3vw, 2rem); letter-spacing: .16em;
            text-transform: uppercase; font-weight: 700; margin: 0 0 1rem;}
        .reveal-name {color: #fff; font-size: clamp(4rem, 14vw, 10rem); line-height: 1.02;
            font-weight: 900; letter-spacing: -.045em; margin: 0;
            text-shadow: 0 8px 40px rgba(108, 170, 255, .48); overflow-wrap: anywhere;}
        .reveal-secret {color: #d7e3f3; font-size: clamp(1rem, 2.5vw, 1.5rem); margin-top: 2rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="reveal-card"><div class="reveal-icon">🎁</div>'
        f'<p class="reveal-kicker">Tu regalo es para</p>'
        f'<h1 class="reveal-name">{escape(nombre_receptor)}</h1>'
        f'<p class="reveal-secret">🤫 Guarda el secreto</p></div>',
        unsafe_allow_html=True,
    )
    st.snow()
    st.balloons()


def user_interface():
    datos = cargar_datos()
    emparejamientos = datos["emparejamientos"]

    if not emparejamientos:
        st.info("El administrador aún no ha generado el sorteo.")
        return

    params = _query_params()
    app_name = params.get("app_name", "")
    user_name = params.get("user_name", "")
    numero = str(params.get("number", "")).strip()

    if app_name and app_name != "AmigoInvisible":
        st.error("Este enlace pertenece a otra aplicación.")
        return

    identity = _assignment_identity(user_name, numero)
    if not identity:
        user_name = st.session_state.get("user_name_input", user_name)
        numero = str(st.session_state.get("user_number_input", numero)).strip()
        identity = _assignment_identity(user_name, numero)

    if identity and identity == st.session_state.get("revealed_assignment_identity"):
        _show_reveal(st.session_state.revealed_recipient)
        return

    st.session_state.pop("revealed_assignment_identity", None)
    st.session_state.pop("revealed_recipient", None)

    st.title("Consulta de Amigo Invisible 🎁")
    st.subheader("Tu asignación secreta")
    if user_name and numero:
        st.write(f"Enlace preparado para **{user_name}**.")
        st.caption("Pulsa el botón para descubrir a quién tienes que hacer el regalo.")
    else:
        st.write("Introduce el nombre y el número secreto que te ha enviado el organizador.")
        user_name = st.text_input("Tu nombre", value=user_name, max_chars=100, key="user_name_input")
        numero = st.text_input("Número secreto", value=numero, max_chars=6, key="user_number_input")

    if st.button("🎁 Descubrir a quién regalo", type="primary", use_container_width=True):
        if not user_name.strip() or not numero.isdigit():
            st.warning("Comprueba el nombre y el número secreto.")
            return

        asignacion = emparejamientos.get(str(int(numero)))
        if not asignacion or len(asignacion) != 2:
            st.error("El número no es válido o no está asignado.")
            return

        nombre_regalador, nombre_receptor = asignacion
        if nombre_regalador.casefold() != user_name.strip().casefold():
            st.error("Ese enlace no coincide con el nombre asignado. Contacta con el organizador.")
            return

        st.session_state.revealed_assignment_identity = _assignment_identity(user_name, numero)
        st.session_state.revealed_recipient = nombre_receptor
        st.rerun()
