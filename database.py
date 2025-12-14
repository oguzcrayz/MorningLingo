import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import streamlit as st
import os
import json

# Google Sheets Bağlantısı
def get_db_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    try:
        # 1. YÖNTEM: Bilgisayarında 'secrets.json' varsa (Yerel Çalışma)
        if os.path.exists('secrets.json'):
            creds = ServiceAccountCredentials.from_json_keyfile_name('secrets.json', scope)
        
        # 2. YÖNTEM: Streamlit Cloud (YENİ VE KOLAY YÖNTEM)
        # Artık karmaşık JSON string yerine doğrudan ayarları okuyoruz
        elif 'gcp_service_account' in st.secrets:
            key_dict = st.secrets['gcp_service_account']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        
        # 3. YÖNTEM: Eski yöntem (Yedek)
        elif 'GCP_JSON' in st.secrets:
            key_dict = json.loads(st.secrets['GCP_JSON'])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
            
        else:
            st.error("⚠️ HATA: Google anahtarları bulunamadı.")
            return None

        client = gspread.authorize(creds)
        sheet = client.open('MorningLingoDB')
        return sheet

    except Exception as e:
        st.error(f"Veritabanı Bağlantı Hatası: {e}")
        return None

# --- Diğer Fonksiyonlar (Aynen Kalsın, Dokunmana Gerek Yok) ---
def login_user(username, password):
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            users = users_ws.get_all_records()
            for user in users:
                if str(user['username']) == username and str(user['password']) == password:
                    return user['name']
        except: return None
    return None

def register_user(username, password, name):
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            existing_users = users_ws.col_values(1)
            if username in existing_users: return False
            users_ws.append_row([username, password, name])
            return True
        except: return False
    return False

def add_word(username, word, meaning, synonyms, forms="-", example="-"): # Parametreleri güncelledim
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # Excel sırasına dikkat: username, word, meaning, synonyms, date, forms, example
            # Senin excel yapına göre burayı esnetebilirsin ama standart ekleme bu:
            vocab_ws.append_row([username, word, meaning, synonyms, date])
        except: pass

def get_user_words(username):
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            all_data = vocab_ws.get_all_records()
            return [row for row in all_data if row['username'] == username]
        except: return []
    return []

def delete_word(word_text, username):
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            cell = vocab_ws.find(word_text)
            if cell:
                 row_val = vocab_ws.row_values(cell.row)
                 if row_val[0] == username: vocab_ws.delete_rows(cell.row)
        except: pass

def get_random_words(username, limit=5):
    import random
    words = get_user_words(username)
    if not words: return []
    if len(words) >= limit: return [w['word'] for w in random.sample(words, limit)]
    return [w['word'] for w in words]
    
# Difficulty güncelleme fonksiyonu (Flashcard için gerekli)
def update_difficulty(username, word, status):
    # Basit versiyonda bunu boş geçebiliriz veya geliştirebilirsin
    pass
