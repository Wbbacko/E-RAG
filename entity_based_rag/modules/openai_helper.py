from openai import AzureOpenAI
import gradio as gr
import tiktoken


class OpenAIHelper():
    def __init__(self, type, api_key, api_version, azure_endpoint, chat_model, embedding_model):
        self.type = type
        self.api_key = api_key
        self.api_version = api_version
        self.azure_endpoint = azure_endpoint
        self.chat_model = chat_model
        self.embedding_model = embedding_model

        try:
            self.client = AzureOpenAI(api_key=self.api_key, api_version=self.api_version, azure_endpoint=self.azure_endpoint)
        except Exception as e:
            raise gr.Error(str(e))

    def get_embedding(self, text, **kwargs):
        try:
            response = self.client.embeddings.create(input=text, model=self.embedding_model, **kwargs)
            return response.data[0].embedding
        except Exception as e:
            raise gr.Error(str(e))

    def talk(self, system_prompt=None, messages=None, **kwargs):
        try:
            truncated_str = self.truncate_string(messages[0]['content'])
            messages[0]['content'] = truncated_str
            if system_prompt is not None:
                messages = [{'role':'system', 'content':system_prompt}] + messages
            response = self.client.chat.completions.create(messages=messages, model=self.chat_model, **kwargs)
            content = response.choices[0].message.content
            if content is None:
                raise gr.Error('openai return None')
            return content
        except Exception as e:
            raise gr.Error(str(e))
    
    def truncate_string(self, string: str, max_tokens: int = 15000, encoding_name: str = 'cl100k_base') -> str:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(string)
        return encoding.decode(tokens[:max_tokens])
