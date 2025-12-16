import google.generativeai as genai
import json
import random

class AITutor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    # --- 1. CHAT FONKSİYONU ---
    def get_chat_response(self, user_input, history):
        """İngilizce öğretmen chat yanıtı"""
        prompt = f"""You are a helpful, friendly English tutor named "Teacher Lingo".
        The user is learning English and speaks Turkish.
        User says: {user_input}

        Instructions:
        - Keep your answer short, encouraging and helpful
        - If the user makes grammar mistakes, correct them politely
        - If user writes in Turkish, respond in Turkish but include English examples
        - Be supportive and motivating
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Bağlantı hatası. Lütfen tekrar dene."

    # --- 2. KELİME ANALİZİ (GELİŞTİRİLMİŞ) ---
    def analyze_word(self, word):
        """Kelimeyi analiz et: düzelt, anlam, örnek, eş anlamlı, tüm formlar"""
        prompt = f"""Analyze the English word '{word}' (correct it if misspelled).

        Output ONLY a valid JSON object like this (no extra text):
        {{
            "corrected_word": "the correct spelling of the word",
            "meaning": "Turkish meaning (Türkçe anlam)",
            "example": "A simple example sentence using the word",
            "synonyms": "2-3 synonyms separated by comma",
            "forms": "All word forms: noun form, verb form, adjective form, adverb form (whichever exist). Example: 'beauty (n), beautify (v), beautiful (adj), beautifully (adv)'"
        }}

        Important:
        - If the word is misspelled, provide the correct spelling in corrected_word
        - Include ALL grammatical forms that exist for this word family
        - Meaning MUST be in Turkish
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_text)
            corrected = data.get("corrected_word", word)
            return corrected, data.get("meaning", "-"), data.get("example", "-"), data.get("synonyms", "-"), data.get("forms", "-")
        except:
            return word, "Bulunamadı", "-", "-", "-"

    # --- 3. METİN OLUŞTURMA (SEVİYE, TÜR, UZUNLUK) ---
    def generate_text(self, level, text_type, word_count):
        """Belirli seviye, tür ve uzunlukta metin oluştur"""
        type_prompts = {
            "Bilgilendirici": "informative and educational (facts, explanations)",
            "Felsefi": "philosophical and thought-provoking (deep questions, existence, meaning)",
            "Sanatsal": "artistic and creative (describing art, beauty, aesthetics)",
            "Edebi": "literary (storytelling, narrative, descriptive prose)",
            "İkna Edici": "persuasive (convincing, argumentative, opinion-based)",
            "Hukuki": "legal style (formal, contracts, rights, regulations)",
            "Dini": "spiritual/religious (faith, morality, values)"
        }

        type_desc = type_prompts.get(text_type, "general")

        prompt = f"""Write an English text with these specifications:
        - Language Level: {level} (CEFR scale)
        - Text Type: {type_desc}
        - Word Count: approximately {word_count} words

        Rules for {level} level:
        - A1: Very simple sentences, basic vocabulary, present tense mostly
        - A2: Simple sentences, common vocabulary, past and future tense
        - B1: Moderate complexity, wider vocabulary, various tenses
        - B2: Complex sentences, advanced vocabulary, all tenses, idioms
        - C1: Sophisticated language, nuanced vocabulary, complex structures
        - C2: Near-native complexity, rare vocabulary, literary devices

        Write ONLY the text, no explanations or headers.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Metin oluşturulamadı. Lütfen tekrar dene."

    # --- 4. KELİME LİSTESİNDEN METİN OLUŞTURMA ---
    def generate_text_from_words(self, words, level, highlight=True):
        """Verilen kelimelerden metin oluştur"""
        word_list = ", ".join([w['word'] if isinstance(w, dict) else w for w in words])

        prompt = f"""Write a coherent English text using ALL of these words: {word_list}

        Requirements:
        - Language Level: {level}
        - You MUST use ALL the given words naturally in the text
        - The text should make sense and flow well
        - Length: approximately 100-150 words

        {"Mark each of the given words by surrounding them with **double asterisks** for highlighting." if highlight else ""}

        Write ONLY the text, no explanations.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Metin oluşturulamadı."

    # --- 5. RASTGELE KELİME ÜRETİMİ (SEVİYEYE GÖRE) ---
    def generate_random_words(self, level, count):
        """Belirli seviyede rastgele kelimeler üret"""
        prompt = f"""Generate {count} random English vocabulary words for {level} level learners.

        Output ONLY a valid JSON array (no extra text):
        [
            {{
                "word": "the English word",
                "meaning": "Turkish meaning (Türkçe anlam)",
                "example": "A simple example sentence",
                "synonyms": "2-3 synonyms",
                "forms": "All forms: noun (n), verb (v), adjective (adj), adverb (adv) - whichever exist"
            }},
            ...
        ]

        Rules for {level}:
        - A1: Most basic, everyday words (colors, numbers, family, food)
        - A2: Common words (weather, hobbies, travel basics)
        - B1: Intermediate vocabulary (work, education, opinions)
        - B2: Upper intermediate (abstract concepts, business, media)
        - C1: Advanced vocabulary (academic, professional, nuanced)
        - C2: Sophisticated, rare words (literary, technical, idiomatic)

        Make sure words are useful and commonly needed at this level.
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_text)
        except:
            return []

    # --- 6. HİKAYE OLUŞTURMA ---
    def generate_story_with_words(self, words):
        """Verilen kelimelerle kısa hikaye oluştur"""
        if not words: return "Önce kelime eklemelisin!"
        word_list = ", ".join(words)
        prompt = f"""Write a very short story (50-70 words) using these words: {word_list}

        Mark each of these words with **double asterisks** for highlighting.
        Make the story interesting and coherent.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Hikaye oluşturulamadı."

    # --- 7. QUIZ OLUŞTURMA ---
    def generate_quiz(self, words):
        """Çoktan seçmeli sınav oluştur"""
        if not words: return []
        word_list = ", ".join(words)
        prompt = f"""Create a multiple choice quiz for these English words: {word_list}

        Output ONLY a valid JSON array:
        [
            {{
                "question": "What is the meaning of 'WORD'?",
                "options": ["Correct Turkish meaning", "Wrong option 1", "Wrong option 2", "Wrong option 3"],
                "answer": "Correct Turkish meaning"
            }},
            ...
        ]

        Rules:
        - Questions should ask for Turkish meanings
        - Include 4 options per question
        - Wrong options should be plausible but incorrect
        - Shuffle the correct answer position
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_text)
        except:
            return []

    # --- 8. OKUMA METNİ ---
    def generate_reading_text(self, level, length):
        """Seviyeye uygun okuma metni oluştur"""
        prompt = f"""Write a reading text for {level} level English learners.

        Requirements:
        - Length: approximately {length} words
        - Topic: Choose an interesting, educational topic
        - Vocabulary and grammar must match {level} level
        - Include varied sentence structures appropriate for the level

        Write ONLY the text, no title or explanations.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Metin oluşturulamadı."

    # --- 9. ÇEVİRİ CHALLENGE ---
    def generate_translation_challenge(self, level):
        """Çeviri alıştırması için Türkçe cümle üret"""
        prompt = f"""Give me one Turkish sentence for {level} level English translation practice.
        The sentence should be appropriate for {level} learners to translate.
        Output ONLY the Turkish sentence, nothing else."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Cümle oluşturulamadı."

    def check_translation(self, turkish, user_english):
        """Kullanıcının çevirisini kontrol et"""
        prompt = f"""Turkish sentence: {turkish}
        User's English translation: {user_english}

        Evaluate this translation:
        1. Is it correct? (Yes/Partially/No)
        2. If wrong, provide the correct translation
        3. Give a score out of 10
        4. Brief feedback in Turkish

        Keep response concise."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "Kontrol edilemedi."

    # --- 10. BAŞLANGIÇ PAKETİ ---
    def generate_starter_pack(self, level, count):
        """Yeni kullanıcılar için başlangıç kelime paketi"""
        prompt = f"""Generate {count} essential English words for {level} level beginners.

        Output ONLY a valid JSON array:
        [
            {{
                "word": "English word",
                "meaning": "Turkish meaning",
                "example": "Simple example sentence",
                "synonyms": "1-2 synonyms",
                "forms": "word forms if applicable"
            }},
            ...
        ]

        Choose the most useful, everyday words for this level.
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_text)
        except:
            return []

    # --- 11. TÜRKÇE-İNGİLİZCE HIZLI TEST ---
    def generate_tr_en_quiz(self, level):
        """Hızlı Türkçe-İngilizce kelime testi"""
        prompt = f"""Give me a random Turkish word and its English equivalent for {level} level.
        Output ONLY valid JSON: {{"tr": "Turkish word", "en": "English word"}}"""
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_text)
            return data.get('tr'), data.get('en')
        except:
            return "Hata", "Error"

    # --- 12. TELAFFUZ KONTROLÜ (PLACEHOLDER) ---
    def check_pronunciation(self, audio_bytes, target_text):
        """Telaffuz kontrolü - gelecekte ses tanıma ile"""
        return f"'{target_text}' kelimesini güzel söyledin! Pratik yapmaya devam et."
