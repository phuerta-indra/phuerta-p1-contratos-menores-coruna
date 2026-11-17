from src.chatbot.interface import demo_func
from pathlib import Path
import gradio as gr
 


if __name__ == '__main__':
    css_path = Path('src/chatbot/styles.css').read_text(encoding='utf-8')

    demo = demo_func()
    
    demo.launch(
        theme=gr.themes.Soft(),
        css=css_path,
    )