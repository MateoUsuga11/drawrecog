import os
import io
import base64
import streamlit as st
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# ====== Función para codificar imagen (opcional si quieres debug) ======
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# ====== Configuración de la app ======
st.set_page_config(page_title='Tablero Inteligente con Estilo')
st.title('🎨 Tablero Inteligente con Estilos de IA')

with st.sidebar:
    st.subheader("ℹ️ Acerca de:")
    st.write("Esta aplicación permite dibujar un boceto y transformarlo en una ilustración con distintos estilos usando IA.")
    st.write("---")

    # Personalización del canvas
    st.subheader("🎛 Opciones del Canvas")
    canvas_width = st.number_input("Ancho del Canvas (px)", min_value=200, max_value=1200, value=400, step=50)
    canvas_height = st.number_input("Alto del Canvas (px)", min_value=200, max_value=800, value=300, step=50)
    
    stroke_width = st.slider("Ancho de línea", 1, 30, 5)
    stroke_color = st.color_picker("Color del pincel", "#000000")
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")

# Selección de estilo
st.subheader("🎨 Elige el estilo de la imagen generada")
style = st.selectbox("Estilo:", ["Anime", "Realista", "Pixel Art", "Acuarela", "Cómic", "Minimalista"])

# ====== Canvas ======
st.subheader("✏️ Dibuja tu boceto")
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode="freedraw",
    key="canvas",
)

# ====== API Key ======
ke = st.text_input('🔑 Ingresa tu API Key de OpenAI', type="password")
if ke:
    os.environ['OPENAI_API_KEY'] = ke
    client = OpenAI(api_key=ke)
else:
    client = None

# ====== Botón para generar ======
generate_button = st.button("✨ Generar imagen con estilo")

# ====== Proceso de análisis ======
if canvas_result.image_data is not None and client and generate_button:
    with st.spinner("Generando imagen con IA..."):
        try:
            # Guardar boceto como PNG
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
            input_image.save('boceto.png')

            # Prompt con el estilo elegido
            prompt_text = f"Convierte este boceto en una ilustración con estilo {style.lower()}."

            with open("boceto.png", "rb") as boceto_file:
                # Usamos la API de edición de imágenes
                result = client.images.generate(
                    model="dall-e-2",    # o "dall-e-3" si tu cuenta lo soporta
                    prompt=prompt_text,
                    size="1024x1024"     # valores válidos: "256x256", "512x512", "1024x1024"
                )

            # Decodificar resultado
            image_b64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_b64)
            output_image = Image.open(io.BytesIO(image_bytes))

            # Mostrar resultado
            st.image(output_image, caption=f"Imagen generada en estilo {style}", use_column_width=True)

            # Botón de descarga
            st.download_button(
                label="⬇️ Descargar imagen",
                data=image_bytes,
                file_name=f"boceto_{style.lower()}.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"Ocurrió un error al generar la imagen: {e}")
else:
    if not ke:
        st.warning("⚠️ Por favor ingresa tu API Key de OpenAI.")
