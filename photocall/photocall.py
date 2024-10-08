import streamlit as st
import os
import json
from PIL import Image
from PIL import ExifTags
import zipfile

def corregir_orientacion(imagen):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(imagen._getexif().items())

        if exif[orientation] == 3:
            imagen = imagen.rotate(180, expand=True)
        elif exif[orientation] == 6:
            imagen = imagen.rotate(270, expand=True)
        elif exif[orientation] == 8:
            imagen = imagen.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # La imagen no tiene información EXIF
        pass

    return imagen
# Añadir un sistema de registro simple
usuarios_registrados = {}
def registrar_usuario(user_id):
    if user_id not in usuarios_registrados:
        usuarios_registrados[user_id] = True
        return True
    return False

# Configuración de la página para dispositivos móviles
st.set_page_config(
    page_title="CONCURSO DE FOTOS",
    page_icon="📸",
    layout="wide"  # Usar diseño amplio para mejor visualización en móviles
)

# Carpeta donde se guardarán las fotos 📁
IMG_DIR = "./fotos"

# Archivo para guardar la info de las fotos 📄
IMAGE_INFO_FILE = "./info_fotos.json"

# Cargamos la info de las fotos desde el archivo 🔄
if os.path.exists(IMAGE_INFO_FILE):
    with open(IMAGE_INFO_FILE, 'r') as f:
        info_fotos = json.load(f)
else:
    info_fotos = {}

# Creamos la carpeta si no existe 📂
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

st.title('📸 Sube y vota las mejores fotos!')

# Usar columnas para organizar mejor el contenido
col1, col2 = st.columns(2)

with col1:
    user_id = st.text_input('Nombre de Instagram sin @, para que todos puedan ver la foto que has subido:').strip().lower()
    if st.button('Registrar', key='registrar'):
        if registrar_usuario(user_id):
            st.success('Usuario registrado con éxito! 🎉')
        else:
            st.warning('Este Nombre de Instagram ya está registrado.')

with col2:
    opcion = st.selectbox("Elige una opción", ["Subir foto 📤", "Ver fotos 📸", "📁"])





if opcion == "Subir foto 📤":
    # Comprobamos si ya has subido una foto 🔄
    if user_id in [info['uploader'] for info in info_fotos.values()]:
        st.write('Ya has subido la foto. 📸')
    else:
        # Sube tu foto 📥
        foto_subida = st.file_uploader("Elige una foto", type=['png', 'jpg', 'jpeg'])
        nombre_foto = st.text_input('Añade la descripcion:')

        if foto_subida is not None and nombre_foto and user_id:
            foto = Image.open(foto_subida)
            foto = corregir_orientacion(foto)
            foto.save(os.path.join(IMG_DIR, nombre_foto + '.png'))

            # Guardamos la info de la foto 📝
            info_fotos[nombre_foto] = {'uploader': user_id, 'likes': []}
            st.success('¡Foto guardada con éxito! 🎉')

            # Guardamos la info de las fotos en el archivo 📋
            with open(IMAGE_INFO_FILE, 'w') as f:
                json.dump(info_fotos, f)
            st.experimental_rerun()

elif opcion == "Ver fotos 📸":
    # Ordenamos las fotos por likes ❤️
    fotos_ordenadas = sorted(info_fotos.items(), key=lambda item: len(item[1]['likes']), reverse=True)
    # Mostramos las fotos 📸
    for nombre_foto, info in fotos_ordenadas:
        foto = Image.open(os.path.join(IMG_DIR, nombre_foto + '.png'))
        likes = len(info['likes'])
        descripcion = nombre_foto  # Aquí puedes reemplazar 'nombre_foto' con la descripción de la foto
        st.image(foto, use_column_width=True)
        st.write(f'@{info["uploader"]} ➡️ {descripcion} ({likes}❤️)')
        if user_id:
            if st.button('❤️', key=nombre_foto, help='Vota por esta foto'):
                info['likes'].append(user_id)
                st.success('¡Has votado por esta foto! ❤️')
                # Actualizamos el archivo de info de las fotos cada vez que se da like 👍
                with open(IMAGE_INFO_FILE, 'w') as f:
                    json.dump(info_fotos, f)
            elif user_id in info['likes']:
                st.write('Ya has votado por esta foto! ❤️')

elif opcion == "📁":
    # Añade una opción para introducir una contraseña
    password = st.text_input("Introduce la contraseña", type='password')

    # Si la contraseña es correcta, muestra el botón de descarga y la opción de borrar fotos
    if password == "Admin1":
        # Crea un archivo zip
        with zipfile.ZipFile('fotos.zip', 'w') as zip_f:
            for nombre_foto in info_fotos.keys():
                # Añade cada foto al archivo zip
                zip_f.write(os.path.join(IMG_DIR, nombre_foto + '.png'), arcname=nombre_foto + '.png')

        # Lee el contenido del archivo zip
        with open('fotos.zip', 'rb') as f:
            bytes = f.read()

        # Proporciona un botón de descarga para el archivo zip
        st.download_button(
            label="Descargar fotos.zip",
            data=bytes,
            file_name='fotos.zip',
            mime='application/zip',
        )

        # Opción para borrar fotos
        st.subheader("Borrar fotos")
        foto_a_borrar = st.selectbox("Selecciona la foto a borrar", list(info_fotos.keys()))

        if st.button('Borrar foto', key='borrar_foto'):
            # Borrar la foto del sistema de archivos
            try:
                os.remove(os.path.join(IMG_DIR, foto_a_borrar + '.png'))
                # Borrar la información de la foto
                del info_fotos[foto_a_borrar]
                # Actualizar el archivo de info de las fotos
                with open(IMAGE_INFO_FILE, 'w') as f:
                    json.dump(info_fotos, f)
                st.success('¡Foto borrada con éxito! 🗑️')
            except Exception as e:
                st.error(f'Error al borrar la foto: {e}')