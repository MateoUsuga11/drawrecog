import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# ====== Configuración de la app ======
st.set_page_config(page_title='Tablero Inteligente')
st.title('🎨 Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
    st.write("---")

    # ====== Personalización ======
    st.subheader("🎛 Personalización del Canvas")
    canvas_width = st.number_input("Ancho del Canvas (px)", min_value=200, max_value=1200, value=400, step=50)
    canvas_height = st.number_input("Alto del Canvas (px)", min_value=200, max_value=800, value=300, step=50)
    
    stroke_width = st.slider("Ancho de línea", 1, 30, 5)
    stroke_color = st.color_picker("Color del pincel", "#000000")
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")

st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarlo")

# ====== Opciones de dibujo ======
drawing_mode = st.selectbox(
    "Herramienta de Dibujo:",
    ("freedraw","line","rect","circle","transform", "polygon", "point"),
)

# ====== Crear canvas ======
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode=drawing_mode,
    key="canvas",
)

# ====== API Key ======
ke = st.text_input('🔑 Ingresa tu API Key de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# ====== Botón analizar ======
analyze_button = st.button("🔍 Analiza la imagen", type="secondary")

# ====== Análisis ======
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        # Guardar imagen
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
        base64_image = encode_image_to_base64("img.png")
        prompt_text = "Describe en español brevemente la imagen"

        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            if response.choices[0].message.content is not None:
                full_response = response.choices[0].message.content
                message_placeholder.markdown(full_response)
                if Expert == profile_imgenh:
                    st.session_state.mi_respuesta = response.choices[0].message.content
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API key.")
