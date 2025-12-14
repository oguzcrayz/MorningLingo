import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import streamlit as st
import os
import json
import random

# --- 1. BAĞLANTI AYARLARI ---
def get_db_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    try:
        # YÖNTEM 1: Streamlit Cloud (Secrets - TOML Formatı)
        if 'gcp_service_account' in st.secrets:
            # Secrets objesini sözlüğe çeviriyoruz
            key_dict = dict(st.secrets['gcp_service_account'])
            
            # Private Key içindeki \n karakterlerini düzelt (Çok Önemli!)
            if 'private_key' in key_dict:
                key_dict['private_key'] = key_dict['private_key'].replace('\\n', '\n')
            
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)

        # YÖNTEM 2: Bilgisayarında (secrets.json)
        elif os.path.exists('secrets.json'):
            creds = ServiceAccountCredentials.from_json_keyfile_name('secrets.json', scope)
            
        else:
            return None

        client = gspread.authorize(creds)
        sheet = client.open('MorningLingoDB')
        return sheet

    except Exception as e:
        st.error(f"Veritabanı Bağlantı Hatası: {e}")
        return None

# --- 2. KULLANICI İŞLEMLERİ ---
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
            # Varsayılan XP 0 olarak ekleniyor
            users_ws.append_row([username, password, name, 0])
            return True
        except: return False
    return False

# --- 3. XP VE PUAN SİSTEMİ (Hata veren yer burasıydı, düzelttik) ---
def get_user_xp(username):
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            records = users_ws.get_all_records()
            for user in records:
                if str(user['username']) == username:
                    # XP değeri boşsa veya yoksa 0 döndür
                    return int(user.get('xp') or 0)
        except: return 0
    return 0

def add_xp(username, amount):
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            cell = users_ws.find(username)
            if cell:
                # Başlıkları kontrol et
                headers = users_ws.row_values(1)
                if 'xp' not in headers:
                    col_idx = len(headers) + 1
                    users_ws.update_cell(1, col_idx, 'xp')
                else:
                    col_idx = headers.index('xp') + 1
                
                # Mevcut puanı al
                cur_val = users_ws.cell(cell.row, col_idx).value
                # Eğer hücre boşsa 0 kabul et
                current_xp = int(cur_val) if cur_val and str(cur_val).isdigit() else 0
                
                users_ws.update_cell(cell.row, col_idx, current_xp + amount)
        except: pass

# --- 4. KELİME İŞLEMLERİ ---
def add_word(username, word, meaning, example="-", synonyms="-", forms="-"):
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            vocab_ws.append_row([username, word, meaning, example, synonyms, forms, date, "Hard"])
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
    words = get_user_words(username)
    if not words: return []
    if len(words) >= limit: return [w['word'] for w in random.sample(words, limit)]
    return [w['word'] for w in words]

def update_difficulty(username, word, status):
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            cell = vocab_ws.find(word)
            if cell:
                headers = vocab_ws.row_values(1)
                if 'difficulty' in headers:
                    col_idx = headers.index('difficulty') + 1
                    vocab_ws.update_cell(cell.row, col_idx, status)
        except: pass

def get_smart_quiz_words(username, limit=5):
    words = get_user_words(username)
    if not words: return []
    hard_words = [w for w in words if w.get('difficulty') == 'Hard']
    if len(hard_words) < limit:
        return [w['word'] for w in words[:limit]] # Yeterince yoksa normal getir
    return [w['word'] for w in random.sample(hard_words, limit)]
