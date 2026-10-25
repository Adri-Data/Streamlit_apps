import streamlit as st

from utils import cargar_datos


def _query_params():
    """Read Streamlit query parameters across supported Streamlit versions."""
    try:
        return dict(st.query_params)
    except Exception:
        legacy = st.experimental_get_query_params()
        return {key: values[-1] if isinstance(values, list) else values for key, values in legacy.items()}


def user_interface():
    st.title("Consulta de Amigo Invisible 🎁")
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

        st.snow()
        st.balloons()
        st.success(f"🎉 **{nombre_receptor}** es la persona a quien tienes que hacer el regalo.")
        st.markdown("🤫 ¡Guarda el secreto!")
