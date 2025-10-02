import os
import streamlit as st
import base64
import openai
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# ====== Función para codificar imagen ======
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# ====== Configuración de la app ======
st.set_page_config(page_title='Tablero Inteligente')
st.title('🎨 Tablero Inteligente con Estilo')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Esta app convierte tu boceto en una imagen con el estilo que elijas usando IA.")
    st.write("---")

    # Personalización del canvas
    st.subheader("🎛 Opciones de Canvas")
    canvas_width = st.number_input("Ancho del Canvas (px)", min_value=200, max_value=1200, value=400, step=50)
    canvas_height = st.number_input("Alto del Canvas (px)", min_value=200, max_value=800, value=300, step=50)
    
    stroke_width = st.slider("Ancho de línea", 1, 30, 5)
    stroke_color = st.color_picker("Color del pincel", "#000000")
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")

# Selección de estilo
st.subheader("Elige el estilo de la imagen generada")
style = st.selectbox("🎨 Estilo:", ["Anime", "Realista", "Pixel Art", "Acuarela", "Cómic", "Minimalista"])

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
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# ====== Botón para generar ======
generate_button = st.button("✨ Generar imagen con estilo")

if canvas_result.image_data is not None and api_key and generate_button:
    with st.spinner("Generando imagen con IA..."):
        # Guardar boceto
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('boceto.png')
        
        base64_image = encode_image_to_base64("boceto.png")

        # Crear prompt con estilo elegido
        prompt_text = f"Convierte este boceto en una ilustración con estilo {style.lower()}."

        try:
            response = openai.images.generate(
                model="gpt-image-1",
                prompt=prompt_text,
                size="512x512",
                image=[{"b64_json": base64_image}],
            )

            # Decodificar y mostrar imagen
            image_base64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            output_image = Image.open(io.BytesIO(image_bytes))

            st.image(output_image, caption=f"Imagen generada en estilo {style}", use_column_width=True)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API key.")
