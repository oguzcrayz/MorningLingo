import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import streamlit as st
import os
import json
import random

# --- BAĞLANTI AYARLARI ---
def get_db_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    try:
        if os.path.exists('secrets.json'):
            creds = ServiceAccountCredentials.from_json_keyfile_name('secrets.json', scope)
        elif 'GCP_JSON' in st.secrets:
            key_dict = json.loads(st.secrets['GCP_JSON'])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        else: return None
        client = gspread.authorize(creds)
        return client.open('MorningLingoDB')
    except Exception as e:
        st.error(f"DB Hatası: {e}")
        return None

# --- KULLANICI İŞLEMLERİ ---
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
            existing = users_ws.col_values(1)
            if username in existing: return False
            users_ws.append_row([username, password, name, 0])
            return True
        except: return False
    return False

# --- XP SİSTEMİ ---
def get_user_xp(username):
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            cell = users_ws.find(username)
            if cell:
                xp_val = users_ws.cell(cell.row, 4).value
                return int(xp_val) if xp_val else 0
        except: return 0
    return 0

def add_xp(username, points):
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            cell = users_ws.find(username)
            if cell:
                current_xp = users_ws.cell(cell.row, 4).value
                current_xp = int(current_xp) if current_xp else 0
                new_xp = current_xp + points
                users_ws.update_cell(cell.row, 4, new_xp)
                return new_xp
        except: pass
    return 0

# --- KELİME İŞLEMLERİ ---
def add_word(username, word, meaning, example, synonyms, forms):
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # Sıralama: user, word, meaning, example, syn, date, difficulty, FORMS
            # Varsayılan Zorluk: "Hard"
            vocab_ws.append_row([username, word, meaning, example, synonyms, date, "Hard", forms])
            add_xp(username, 10) 
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

# --- AKILLI TEKRAR MANTIĞI ---
def update_difficulty(username, word_text, status): 
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            cell = vocab_ws.find(word_text)
            if cell:
                row_val = vocab_ws.row_values(cell.row)
                if row_val[0] == username:
                    # Difficulty sütunu 7. sırada (G sütunu)
                    vocab_ws.update_cell(cell.row, 7, status)
                    return True
        except: return False
    return False

def get_smart_quiz_words(username, limit=5):
    words = get_user_words(username)
    if not words: return []
    
    # Gruplama
    hard_words = [w for w in words if w.get('difficulty', 'Hard') == 'Hard']
    medium_words = [w for w in words if w.get('difficulty', 'Hard') == 'Medium']
    normal_words = [w for w in words if w.get('difficulty', 'Hard') == 'Normal']
    
    selected_words = []
    
    # 1. ZORLAR
    random.shuffle(hard_words); selected_words.extend(hard_words[:limit])
    
    # 2. ORTALAR
    if len(selected_words) < limit:
        rem = limit - len(selected_words)
        random.shuffle(medium_words); selected_words.extend(medium_words[:rem])
        
    # 3. NORMALLER
    if len(selected_words) < limit:
        rem = limit - len(selected_words)
        random.shuffle(normal_words); selected_words.extend(normal_words[:rem])
    
    random.shuffle(selected_words)
    return [w['word'] for w in selected_words]

# --- LİDERLİK ---
def get_leaderboard(limit=5):
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            all_users = users_ws.get_all_records()
            sorted_users = sorted(all_users, key=lambda x: int(x['xp']) if x['xp'] else 0, reverse=True)
            leaderboard = []
            for u in sorted_users[:limit]:
                xp = int(u['xp']) if u['xp'] else 0
                leaderboard.append({'name': u['name'], 'count': xp})
            return leaderboard
        except: return []
    return []

# --- RASTGELE KELİME (Hikaye Modu İçin Basit Seçim) ---
def get_random_words(username, limit=5):
    import random
    words = get_user_words(username)
    if not words: return []
    if len(words) >= limit: return [w['word'] for w in random.sample(words, limit)]
    return [w['word'] for w in words]