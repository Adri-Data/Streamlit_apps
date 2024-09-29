import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(
    page_title="XVI Grand Prix Peñero 2024",
    page_icon="🏆",
    layout="centered",  # Cambiado de "wide" a "centered"
    initial_sidebar_state="collapsed",  # Cambiado de "expanded" a "collapsed"
    menu_items=None
)

# Constantes
ADMIN_PASSWORD = "Admin1"
PUNTUACIONES_FILE = "puntuaciones.csv"
PRUEBAS = ['Columnas Locas', 'Atrapa el banderín', 'Cuerda y coraje', 'Encesta y Escapa', 'La Muerte']

# Funciones auxiliares
def borrar_datos():
    if os.path.exists(PUNTUACIONES_FILE):
        os.remove(PUNTUACIONES_FILE)
    if 'df_puntuaciones' in st.session_state:
        del st.session_state.df_puntuaciones

def cargar_puntuaciones():
    if os.path.exists(PUNTUACIONES_FILE):
        try:
            df = pd.read_csv(PUNTUACIONES_FILE)
            if not all(col in df.columns for col in ['Peñes'] + PRUEBAS + ['Total']):
                raise KeyError
            df['Total'] = df[PRUEBAS].sum(axis=1)
        except (KeyError, pd.errors.EmptyDataError):
            df = crear_df_vacio()
            st.warning("Se ha detectado un cambio en las pruebas o un archivo corrupto. Se ha creado una nueva tabla de puntuaciones.")
    else:
        df = crear_df_vacio()
    df = df.sort_values('Total', ascending=False).reset_index(drop=True)
    df.index = df.index + 1  # Añadir esta línea para que el índice empiece en 1
    return df

def crear_df_vacio():
    return pd.DataFrame(columns=['Peñes'] + PRUEBAS + ['Total'])

def guardar_puntuaciones(df):
    df.to_csv(PUNTUACIONES_FILE, index=False)

def actualizar_puntuaciones(df):
    df['Total'] = df[PRUEBAS].sum(axis=1)
    df = df.sort_values('Total', ascending=False).reset_index(drop=True)
    df.index = df.index + 1  # Añadir esta línea para que el índice empiece en 1
    return df

def highlight_max(s):
    is_max = s == s.max()
    return ['background-color: #F2A71B' if v else '' for v in is_max]

def highlight_first_team(df):
    return ['background-color: #F2A71B' if i == 0 else '' for i in range(len(df))]

def get_styled_df(df):
    return df.style\
        .apply(highlight_max, subset=PRUEBAS + ['Total'])\
        .apply(highlight_first_team, subset=['Peñes'])

# Cargar puntuaciones al inicio
if 'df_puntuaciones' not in st.session_state:
    st.session_state.df_puntuaciones = cargar_puntuaciones()

# Título principal
st.markdown("<h1 style='text-align: center; font-size: 24px;'>🏆🐂 XVI Grand Prix Peñero 2024 🐂🏆</h1>", unsafe_allow_html=True)

# Mostrar el dataframe principal
st.markdown("<h2 style='text-align: center; font-size: 20px;'>Puntuaciones</h2>", unsafe_allow_html=True)

# Eliminamos las columnas y mostramos el dataframe a ancho completo
st.dataframe(get_styled_df(st.session_state.df_puntuaciones), use_container_width=True)

# Sección de administrador (disimulada)
with st.expander("Opciones avanzadas"):
    password = st.text_input("Contraseña", type="password")

    if password == ADMIN_PASSWORD:
        df = st.session_state.df_puntuaciones.copy()  # Trabajar con una copia
        
        # Seleccionar la prueba a modificar
        prueba_seleccionada = st.selectbox("Seleccionar prueba", PRUEBAS)
        st.markdown(f"### Resultados para {prueba_seleccionada}")
        
        for peña in df['Peñes']:
            puntuacion = st.number_input(f"Puntuación para {peña}", value=df.loc[df['Peñes'] == peña, prueba_seleccionada].values[0], key=f"{peña}_{prueba_seleccionada}_{df.index[df['Peñes'] == peña][0]}")
            df.loc[df['Peñes'] == peña, prueba_seleccionada] = puntuacion  # Actualizar puntuación directamente

        if st.button("Actualizar puntuaciones"):
            df = actualizar_puntuaciones(df)
            st.success("Puntuaciones actualizadas")
            guardar_puntuaciones(df)
            st.session_state.df_puntuaciones = df  # Actualizar el estado

        nueva_peña = st.text_input("Añadir nueva peña")
        if st.button("Añadir peña") and nueva_peña and nueva_peña not in df['Peñes'].tolist():
            nueva_fila = pd.DataFrame({'Peñes': [nueva_peña], **{prueba: [0] for prueba in PRUEBAS}, 'Total': [0]})
            df = pd.concat([df, nueva_fila], ignore_index=True)
            df = actualizar_puntuaciones(df)
            st.success(f"Peña {nueva_peña} añadida")
            guardar_puntuaciones(df)
            st.session_state.df_puntuaciones = df  # Actualizar el estado

        peña = st.selectbox("Seleccionar Peña para editar/eliminar", options=df['Peñes'].tolist())
        
        if peña:
            puntuaciones = {}
            for prueba in PRUEBAS:
                puntuaciones[prueba] = st.number_input(prueba, value=df.loc[df['Peñes'] == peña, prueba].values[0], key=f"{peña}_{prueba}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar"):
                    df.loc[df['Peñes'] == peña, PRUEBAS] = list(puntuaciones.values())
                    df = actualizar_puntuaciones(df)
                    st.success(f"Puntuaciones actualizadas para la peña {peña}")
                    guardar_puntuaciones(df)
                    st.session_state.df_puntuaciones = df  # Actualizar el estado
            
            with col2:
                if st.button("Eliminar"):
                    df = df[df['Peñes'] != peña]
                    df = actualizar_puntuaciones(df)
                    st.success(f"Peña {peña} eliminada")
                    guardar_puntuaciones(df)
                    st.session_state.df_puntuaciones = df  # Actualizar el estado

        st.markdown("---")
        st.markdown("### Borrar todos los datos")
        st.warning("¡Cuidado! Esta acción borrará todos los datos y no se puede deshacer.")
        
        confirmacion = st.checkbox("Estoy seguro de que quiero borrar todos los datos")
        
        if st.button("Borrar todos los datos", disabled=not confirmacion):
            borrar_datos()
            st.success("Todos los datos han sido borrados")
            st.experimental_rerun()

# Sección de fotos (reducida)
with st.expander("Galería de fotos"):
    st.write("Aquí puedes subir y ver fotos del Gran Prix")
    # Aquí iría el código para subir y ver fotos (no implementado en este ejemplo)

# Pie de página
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 14px;'>¡Disfruteu del Gran Prix Peñeros! 🎉🏆</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>🥳Fet per Adrián Navarro de No Parem Mai🥳</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'><a href='https://www.linkedin.com/in/adrian-ai-datascience/' target='_blank'>Adrián Navarro</a> <img src='https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg' width='15' height='15'></p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>@adri.frg.02 <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/1200px-Instagram_logo_2016.svg.png' width='15' height='15'></p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>@adri.frg.02 <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/1200px-Instagram_logo_2016.svg.png' width='20' height='20'></p>", unsafe_allow_html=True)