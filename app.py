import os
import io
import base64
import streamlit as st
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# ====== Configuración de la app ======
st.set_page_config(page_title='Tablero Inteligente con Estilos')
st.title('🎨 Tablero Inteligente (Imagen → Texto → Estilo)')

with st.sidebar:
    st.subheader("ℹ️ Acerca de:")
    st.write("Esta aplicación convierte tu boceto en una descripción con IA, y luego genera una ilustración en el estilo que elijas usando DALL·E 2.")
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
generate_button = st.button("✨ Convertir boceto a ilustración con estilo")

# ====== Flujo completo ======
if client and generate_button and canvas_result.image_data is not None:
    with st.spinner("Analizando boceto con IA..."):
        # Guardar boceto como PNG
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('boceto.png')

        # Convertir imagen a base64
        with open("boceto.png", "rb") as f:
            image_bytes = f.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # 1️⃣ Pedir a GPT-4o-mini que describa la imagen
        try:
            response_desc = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe en detalle esta imagen en español."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ],
                    }
                ],
                max_tokens=200
            )
            description = response_desc.choices[0].message.content
            st.success("✅ Descripción generada por IA:")
            st.write(description)

        except Exception as e:
            st.error(f"Error al describir la imagen: {e}")
            description = None

    if description:
        with st.spinner("Generando ilustración con estilo..."):
            try:
                # 2️⃣ Pasar la descripción como prompt a DALL·E 2
                prompt_text = f"{description}. Recréalo en estilo {style.lower()}."

                result = client.images.generate(
                    model="dall-e-2",
                    prompt=prompt_text,
                    size="1024x1024"
                )

                # Mostrar imagen final (URL)
                image_url = result.data[0].url
                st.image(image_url, caption=f"Imagen generada en estilo {style}", use_column_width=True)
                st.write("🔗 [Abrir imagen en otra pestaña](" + image_url + ")")

            except Exception as e:
                st.error(f"Error al generar la ilustración: {e}")
else:
    if not ke:
        st.warning("⚠️ Por favor ingresa tu API Key de OpenAI.")
