import gradio as gr
from src.chatbot.bot import chatbot

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
        'Consulta los datos de Snowflake en lenguaje ntarual.'
        'Por ejemplo, pregunta por contratos, adjudicatarios o años.'
    ),
    examples=[
        'Cuántos contratos hay',
        '¿Cuántos contratos hubo por año?',
        'Cual es el precio medio por año',
        'Que tipos de contratos hay?'
    ],
)

css = """
.gradio-container {
    font-family: "Segoe UI", sans-serif;
}

.gradio-container h1 {
    font-size: 32px;
    color: #174A67;
}

.gradio-container p {
    font-size: 16px;
}
"""

demo.launch(
    theme=gr.themes.Soft(),
    css=css,
)