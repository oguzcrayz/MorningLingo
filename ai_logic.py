import google.generativeai as genai
import json

class AITutor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_reading_text(self, level, length):
        prompt = f"Write an engaging reading text approximately {length} words long, suitable for {level} English level learners. Do not include translation. Just the English text."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except: return "Hata oluştu. API Key kontrol et."

    def generate_translation_challenge(self, level):
        prompt = f"Give me one simple Turkish sentence to translate into English, suitable for {level} level. Just the sentence."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except: return "Hata."

    def check_translation(self, source_text, user_translation):
        prompt = f"Source Turkish: '{source_text}'. User translation: '{user_translation}'. Rate this 1-10. Correct mistakes. Be encouraging."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except: return "Hata."

    def analyze_word(self, word):
        prompt = f"""
        Analyze the English word '{word}'. 
        Return strictly JSON format: 
        {{
            'meaning': 'Turkish meaning', 
            'example': 'Simple English example sentence', 
            'synonyms': '2-3 synonyms',
            'forms': 'List related forms (Noun, Verb, Adj, Adv). e.g. Decide (v) -> Decision (n)'
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', ''))
            return data['meaning'], data['example'], data['synonyms'], data.get('forms', '-')
        except: return "Bulunamadı", "-", "-", "-"

    # --- YENİ EKLENEN: AKILLI BAŞLANGIÇ PAKETİ ---
    def generate_starter_pack(self, level, count):
        """
        Belirtilen seviye ve sayıda kelime üretir.
        """
        prompt = f"""
        Generate exactly {count} useful English words for {level} level learners.
        For EACH word, provide meaning, example, synonyms, and forms.
        Return strictly a JSON List of objects:
        [
          {{
            "word": "...",
            "meaning": "...",
            "example": "...",
            "synonyms": "...",
            "forms": "..."
          }},
          ...
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', ''))
            return data # Bu bir liste dönecek
        except: return []

    def generate_story_with_words(self, words):
        w_list = ", ".join(words)
        prompt = f"Write a very short, funny story (max 100 words) using these words: {w_list}. Highlight the words in **bold**."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except: return "Hikaye oluşturulamadı."

    def generate_quiz(self, words):
        w_list = ", ".join(words)
        prompt = f"""Create a multiple choice quiz for these words: {w_list}. 
        Return strictly JSON format: [{{'question': '...', 'options': ['A', 'B', 'C'], 'answer': '...'}}]"""
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text.replace('```json', '').replace('```', ''))
        except: return []

    def generate_tr_en_quiz(self, level):
        prompt = f"Give me a Turkish word ({level} level) and its English equivalent. JSON format: {{'tr': '...', 'en': '...'}}"
        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', ''))
            return data['tr'], data['en']
        except: return "Hata", "Error"

    def get_chat_response(self, user_message, chat_history):
        system_instruction = "You are 'LingoBot', a friendly English teacher. Reply in English. Correct grammar mistakes gently."
        chat = self.model.start_chat(history=chat_history)
        full_prompt = f"{system_instruction}\n\nUser: {user_message}"
        try:
            response = chat.send_message(full_prompt)
            return response.text
        except: return "Hata."

    def check_pronunciation(self, audio_bytes, target_word):
        prompt = f"Listen to this audio. The user is trying to pronounce: '{target_word}'. Rate 1-10 and give advice."
        try:
            response = self.model.generate_content([prompt, {"mime_type": "audio/wav", "data": audio_bytes}])
            return response.text
        except Exception as e: return f"Ses analiz edilemedi: {e}"