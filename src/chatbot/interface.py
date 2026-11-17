import gradio as gr
from src.chatbot.bot import chatbot
from pathlib import Path



def demo_func():

    chat = gr.Chatbot(
        height=500,
        placeholder="Hola. Pregúntame algo sobre los contratos menores.",
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

