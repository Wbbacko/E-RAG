import json
import gradio as gr
import pickle as pkl
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from tqdm import tqdm

class EntityDatabase():
    def __init__(self, database_path='./data/kb_refs_clean.json'):
        self.database_path = database_path
        try:
            self.raw_data = json.load(open(self.database_path, 'r', encoding='utf-8'))
        except Exception as e:
            raise gr.Error(str(e))
        
    def init(self, openai_helper):
        if not os.path.exists('./data/kb_refs_clean_embedding.pkl'):
            print("there is no embedding file, start generate ...")
            keys = [list(v.keys()) for v in self.raw_data.values()]
            keys = [item for sublist in keys for item in sublist]
            keys = list(set(keys))
            self.embedding_data = {}
            try:
                for key in tqdm(keys):
                    emb = openai_helper.get_embedding(key)
                    self.embedding_data[key] = emb
            except Exception as e:
                raise gr.Error(str(e))
            if len(self.embedding_data) > 0:
                pkl.dump(self.embedding_data, open('./data/kb_refs_clean_embedding.pkl', 'wb'))
        else:
            self.embedding_data = pkl.load(open('./data/kb_refs_clean_embedding.pkl', 'rb'))        

    def get_all_entities(self):
        return list(self.raw_data.keys())
    
    def get_info_by_entity(self, entity):
        results = {}
        for ent in entity:
            if ent in self.raw_data:
                results[ent] = self.raw_data[ent]
        return results
    
    def similarity(self, retrieval_json, query_emb):
        cos_similarity = {}
        for ent in retrieval_json:
            keys = list(retrieval_json[ent].keys())
            keys_array = np.array([self.embedding_data[key] for key in keys])
            query_array = np.array([query_emb])
            cos_sim = cosine_similarity(keys_array, query_array).reshape(-1)
            cos_similarity[ent] = cos_sim
            
        return cos_similarity
