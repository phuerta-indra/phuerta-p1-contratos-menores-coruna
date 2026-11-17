import gradio as gr
from src.chatbot.bot import chatbot
import base64
from pathlib import Path

def imagen_a_texto(ruta):
    datos = base64.b64encode(Path(ruta).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{datos}"

def demo_func():

    logo = imagen_a_texto(Path(__file__).parent.parent.parent / "img" / "logo.png")
    logo_placeholder = f'<div class="logo-chat"><img src="{logo}" alt="Logo"></div>'


    chat = gr.Chatbot(
        height=700,
        placeholder=logo_placeholder,
    )


    textbox = gr.Textbox(
        placeholder='Escribe aquí tu pregunta',
        lines=1
    )


    demo = gr.ChatInterface(
        fn=chatbot,
        chatbot=chat,
        textbox=textbox,
        title='Asistente para consultar datos sobre contratos menores en A Coruña',
        description=(
            'Consulta los datos de Snowflake en lenguaje natural. '
            'Por ejemplo, pregunta por contratos, adjudicatarios o años.'
        ),
        examples=[
            '¿Cuántos contratos hay?',
            '¿Cuántos contratos hubo por año?',
            '¿Cuál es el precio medio por año?',
            '¿Qué tipos de contratos hay?'
        ],
    )

    return demo

