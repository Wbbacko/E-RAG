# -*- coding: utf-8 -*-
from entity_based_rag.modules.openai_helper import OpenAIHelper
from entity_based_rag.modules.database import EntityDatabase
import gradio as gr
from entity_based_rag.prompts import query_parser_system_prompt, generator_system_prompt
import json

class QueryParser():
    def __init__(self, config=None):
        self.config = config
        self.history = []
        self.chatbot = []
        self.last_entities = []
        self.top_k = 5

        self.openai_helper = OpenAIHelper(**self.config)
        
        # database
        try:
            self.entity_database = EntityDatabase()
            self.entity_database.init(self.openai_helper)
        except Exception as e:
            raise gr.Error(str(e))
    
    def talk(self, query_text):
        query = query_text.replace("\n", " ")
        self.history.append({'role': 'user', 'content': query})
        try:
            response_json = self.parse_entity()
            if len(response_json['entities']) == 0:
                self.chatbot.append([query_text, response_json['reason'] if response_json['reason'] != "" else 'I am unable to answer this question.'])
                return self.chatbot, response_json, None, None

            retrieval_json = self.retrieval_entity(response_json['entities'])

            cos_similarity = self.rank(
                retrieval_json, query)

            top_k_rank_json = {}
            for ent in cos_similarity:
                scores = cos_similarity[ent]
                idx = scores.argsort()[-self.top_k:][::-1].tolist()
                keys = list(retrieval_json[ent].keys())
                top_k_rank_json[ent] = {
                    keys[key_id]: retrieval_json[ent][keys[key_id]] for key_id in idx}

            for ent in top_k_rank_json:
                if self.entity_database.raw_data[ent].get('introduce') is not None:
                    top_k_rank_json[ent]['introduce'] = self.entity_database.raw_data[ent]['introduce']

            response_text = self.generate_answer(top_k_rank_json)

            self.chatbot.append([query_text, response_text])
            self.last_entities = response_json['entities']
            self.history.append(
                {'role': 'assistant', 'content': response_text})
            return self.chatbot, response_json, top_k_rank_json, None
        except Exception as e:
            self.history.pop()
            raise gr.Error(str(e))

    def parse_entity(self):
        system_prompt = query_parser_system_prompt.replace('{input_entities_str}', ', '.join(
            self.last_entities)).replace('{entities_str}', ', '.join(self.entity_database.get_all_entities()))
        try:
            response = self.openai_helper.talk(
                messages=self.history, system_prompt=system_prompt, response_format={'type': 'json_object'})
            json_data = json.loads(response)
            return json_data
        except Exception as e:
            raise gr.Error(str(e))

    def retrieval_entity(self, entities):
        try:
            retrieval_json = self.entity_database.get_info_by_entity(entities)
            return retrieval_json
        except Exception as e:
            raise gr.Error(str(e))

    def generate_answer(self, top_k_rank_json):
        system_prompt = generator_system_prompt.replace(
            '{information}', json.dumps(top_k_rank_json, ensure_ascii=False))
        try:
            response_text = self.openai_helper.talk(
                messages=[self.history[-1]], system_prompt=system_prompt)
            return response_text
        except Exception as e:
            raise gr.Error(str(e))

    def rank(self, retrieval_json, query):
        try:
            query_emb = self.openai_helper.get_embedding(query)
            rank_json = self.entity_database.similarity(retrieval_json, query_emb)
            return rank_json
        except Exception as e:
            raise gr.Error(str(e))

    def clear(self):
        self.history = []
        self.chatbot = []
        self.last_entities = []
        return None, None, None, None