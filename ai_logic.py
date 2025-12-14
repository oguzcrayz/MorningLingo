import google.generativeai as genai
import json
import random

class AITutor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def get_chat_response(self, user_input, history):
        prompt = f"""You are a helpful English tutor. 
        User says: {user_input}. 
        Keep your answer short, encouraging and correct any grammar mistakes politely.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Connection error. Please check API Key."

    def analyze_word(self, word):
        prompt = f"""Analyze the English word '{word}'.
        Output ONLY a JSON string like this:
        {{"meaning": "Turkish meaning", "example": "Simple English sentence", "synonyms": "syn1, syn2", "forms": "noun/verb"}}
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_text)
            return data.get("meaning"), data.get("example"), data.get("synonyms"), data.get("forms")
        except:
            return "Bulunamadı", "-", "-", "-"

    def generate_story_with_words(self, words):
        if not words: return "Önce kelime eklemelisin!"
        word_list = ", ".join(words)
        prompt = f"Write a very short story (50 words) using these words: {word_list}. Highlight the words in bold."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except: return "Hikaye oluşturulamadı."

    def generate_quiz(self, words):
        if not words: return []
        word_list = ", ".join(words)
        prompt = f"""Create a multiple choice quiz for these words: {word_list}.
        Output ONLY a valid JSON array like:
        [
            {{"question": "What is the meaning of Apple?", "options": ["Elma", "Armut", "Muz"], "answer": "Elma"}},
            ...
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_text)
        except: return []

    def check_pronunciation(self, audio_bytes, target_text):
        return f"Harika deneme! '{target_text}' kelimesini daha net söylemeye çalış."

    def generate_reading_text(self, level, length):
        prompt = f"Write a simple reading text for {level} level English learners about a random interesting topic. Length: {length} words."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except: return "Metin oluşturulamadı."

    def generate_translation_challenge(self, level):
        prompt = f"Give me one Turkish sentence for {level} level English translation practice."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except: return "Cümle oluşturulamadı."

    def check_translation(self, turkish, user_english):
        prompt = f"Turkish: {turkish}\nUser translation: {user_english}\nRate this translation out of 10 and correct it if wrong."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except: return "Kontrol edilemedi."

    def generate_starter_pack(self, level, count):
        prompt = f"""Generate {count} common English words for {level} level.
        Output ONLY a JSON array like:
        [
            {{"word": "apple", "meaning": "elma", "example": "I eat apple", "synonyms": "fruit", "forms": "noun"}},
            ...
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_text)
        except: return []
    
    def generate_tr_en_quiz(self, level):
        prompt = f"Give me a random Turkish word and its English equivalent for {level} level. Output JSON: {{'tr': '...', 'en': '...'}}"
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_text)
            return data.get('tr'), data.get('en')
        except: return "Hata", "Error"
