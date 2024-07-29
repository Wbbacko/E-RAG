import gradio as gr
from entity_based_rag.modules.query_parser import QueryParser
import json


config = json.load(open('config/base.json', 'r', encoding='utf-8'))
query_parser = QueryParser(config=config)

with gr.Blocks(analytics_enabled=False) as demo:
    with gr.Row():
        with gr.Column(scale=2):
            with gr.Row():
                chatbot = gr.Chatbot(label="Assistant")
                doc_info = gr.JSON(label="Doc")
            entity_info = gr.JSON(label="Entity")
            user_input = gr.Textbox(
                show_label=False, placeholder="Please input here ...", lines=1)
            with gr.Accordion(label=""):
                submitBtn = gr.Button("Submit", variant="primary")
                clearBtn = gr.Button("Clear")
    submitBtn.click(query_parser.talk, [user_input], outputs=[
                    chatbot, entity_info, doc_info, user_input], show_progress=True)
    clearBtn.click(query_parser.clear, outputs=[
                   chatbot, entity_info, doc_info, user_input], show_progress=True)

demo.launch(_frontend=False, share=False, inbrowser=True, max_threads=10)
