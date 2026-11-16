import gradio as gr
from src.chatbot.bot import chatbot


demo = gr.ChatInterface(
    fn=chatbot,
)
demo.launch()