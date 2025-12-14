import google.generativeai as genai
import json

class AITutor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_reading_text(self, level):
        prompt = (
            f"Write a short, engaging reading passage (approx. 200-300 words) "
            f"in English suitable for {level} CEFR level. "
            f"Do not include the translation, just the English text."
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Hata: {str(e)}"

    def generate_translation_challenge(self, level):
        prompt = (
            f"Write a short paragraph (3-4 sentences) in Turkish "
            f"that would correspond to a {level} level English text context. "
            f"Just give me the Turkish text."
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Hata: {str(e)}"

    def check_translation(self, turkish_text, user_translation):
        prompt = (
            f"I have this Turkish text: '{turkish_text}'\n"
            f"A student translated it to English as: '{user_translation}'\n\n"
            f"Please analyze the translation. 1. Give a score out of 10. "
            f"2. Correct the mistakes. 3. Explain why the mistakes are wrong."
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Hata: {str(e)}"

    def generate_story_with_words(self, words):
        words_str = ", ".join(words)
        prompt = (
            f"Write a short, creative story (max 200 words) in English using these specific words: {words_str}. "
            f"Important: When you use these words in the story, make them **BOLD** (like **word**) so I can see them easily."
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Hata: {str(e)}"

    def analyze_word(self, word):
        prompt = (
            f"I have an English word: '{word}'. "
            f"Please provide: "
            f"1. Its Turkish meaning (short). "
            f"2. A simple English example sentence. "
            f"3. 2 or 3 English synonyms (comma separated). "
            f"Format the output EXACTLY like this: "
            f"MEANING: [Turkish] | EXAMPLE: [English Sentence] | SYNONYMS: [synonym1, synonym2]"
        )
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            parts = text.split('|')
            meaning = parts[0].replace('MEANING:', '').strip()
            example = parts[1].replace('EXAMPLE:', '').strip() if len(parts) > 1 else ""
            synonyms = parts[2].replace('SYNONYMS:', '').strip() if len(parts) > 2 else ""
            return meaning, example, synonyms
        except Exception as e:
            return "Bulunamadı", f"Hata: {str(e)}", ""

    def generate_quiz(self, words):
        words_str = ", ".join(words)
        prompt = (
            f"Create a multiple-choice quiz for these words: {words_str}. "
            f"Return the result ONLY as a raw JSON list. "
            f"Format: [{{'question': '...', 'options': ['A) ...', 'B) ...', 'C) ...', 'D) ...'], 'answer': 'A'}}]"
        )
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except:
            return []

    # YENİ FONKSİYON: Rastgele Türkçe Kelime ve İngilizcesi
    def generate_tr_en_quiz(self, level):
        prompt = (
            f"Give me 1 random Turkish word (noun, verb or adjective) suitable for {level} English learner level. "
            f"Also provide its most common English translation. "
            f"Format exactly like this: TURKISH: [word] | ENGLISH: [word]"
        )
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            parts = text.split('|')
            tr_word = parts[0].replace('TURKISH:', '').strip()
            en_word = parts[1].replace('ENGLISH:', '').strip()
            return tr_word, en_word
        except Exception as e:
            return "Hata", "Error"