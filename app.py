import os
import streamlit as st
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# ====== Configuración de la app ======
st.set_page_config(page_title='Tablero Inteligente con Estilos')
st.title('🎨 Tablero Inteligente con Estilos (DALL·E 2)')

with st.sidebar:
    st.subheader("ℹ️ Acerca de:")
    st.write("Esta aplicación permite dibujar un boceto y generar una ilustración en distintos estilos usando IA (DALL·E 2).")
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
st.subheader("✏️ Dibuja tu boceto (opcional)")
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

# ====== Proceso de generación ======
if client and generate_button:
    with st.spinner("Generando imagen con IA..."):
        try:
            # Prompt: tomamos el estilo y añadimos instrucción
            prompt_text = f"Una ilustración en estilo {style.lower()} de un boceto simple."

            # Si el usuario dibujó algo en el canvas, lo tomamos como referencia textual
            if canvas_result.image_data is not None:
                prompt_text += " El boceto representa un dibujo hecho a mano que debe ser reinterpretado en ese estilo."

            # Generar imagen con DALL·E 2
            result = client.images.generate(
                model="dall-e-2",     
                prompt=prompt_text,
                size="1024x1024"   # valores válidos: 256x256, 512x512, 1024x1024
            )

            # DALL·E devuelve una URL
            image_url = result.data[0].url

            # Mostrar en la app
            st.image(image_url, caption=f"Imagen generada en estilo {style}", use_column_width=True)
            st.write("🔗 [Abrir imagen en otra pestaña](" + image_url + ")")

        except Exception as e:
            st.error(f"Ocurrió un error al generar la imagen: {e}")
else:
    if not ke:
        st.warning("⚠️ Por favor ingresa tu API Key de OpenAI.")
