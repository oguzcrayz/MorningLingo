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
            key_dict = dict(st.secrets['gcp_service_account'])
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
            users_ws.append_row([username, password, name, 0])
            return True
        except: return False
    return False

# --- 3. XP VE PUAN SİSTEMİ ---
def get_user_xp(username):
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            records = users_ws.get_all_records()
            for user in records:
                if str(user['username']) == username:
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
                headers = users_ws.row_values(1)
                if 'xp' not in headers:
                    col_idx = len(headers) + 1
                    users_ws.update_cell(1, col_idx, 'xp')
                else:
                    col_idx = headers.index('xp') + 1

                cur_val = users_ws.cell(cell.row, col_idx).value
                current_xp = int(cur_val) if cur_val and str(cur_val).isdigit() else 0
                users_ws.update_cell(cell.row, col_idx, current_xp + amount)
        except: pass

# --- 4. LİDERLİK TABLOSU ---
def get_leaderboard(limit=50):
    """Top kullanıcıları XP'ye göre sıralı getir"""
    sheet = get_db_connection()
    if sheet:
        try:
            users_ws = sheet.worksheet('users')
            records = users_ws.get_all_records()
            # XP'ye göre sırala (büyükten küçüğe)
            sorted_users = sorted(records, key=lambda x: int(x.get('xp') or 0), reverse=True)
            # İlk 50'yi al (veya daha az varsa hepsini)
            return sorted_users[:min(limit, len(sorted_users))]
        except: return []
    return []

# --- 5. KELİME İŞLEMLERİ ---
def add_word(username, word, meaning, example="-", synonyms="-", forms="-", priority="Çok"):
    """Kelime ekle - varsayılan öncelik: Çok"""
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # username, word, meaning, example, synonyms, forms, date, priority
            vocab_ws.append_row([username, word, meaning, example, synonyms, forms, date, priority])
            return True
        except: return False
    return False

def get_user_words(username):
    """Kullanıcının tüm kelimelerini getir"""
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            all_data = vocab_ws.get_all_records()
            return [row for row in all_data if row['username'] == username]
        except: return []
    return []

def delete_word(word_text, username):
    """Kelime sil"""
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            cell = vocab_ws.find(word_text)
            if cell:
                row_val = vocab_ws.row_values(cell.row)
                if row_val[0] == username:
                    vocab_ws.delete_rows(cell.row)
                    return True
        except: pass
    return False

def get_random_words(username, limit=5):
    """Rastgele kelimeler getir"""
    words = get_user_words(username)
    if not words: return []
    if len(words) >= limit: return [w['word'] for w in random.sample(words, limit)]
    return [w['word'] for w in words]

# --- 6. ÖNCELİK SİSTEMİ (KART ALGORİTMASI) ---
def update_priority(username, word, new_priority):
    """Kelime önceliğini güncelle: Çok, Orta, Az"""
    sheet = get_db_connection()
    if sheet:
        try:
            vocab_ws = sheet.worksheet('vocab')
            all_data = vocab_ws.get_all_records()

            # Kelimeyi bul
            for idx, row in enumerate(all_data, start=2):  # 2'den başla (1. satır başlık)
                if row['username'] == username and row['word'] == word:
                    headers = vocab_ws.row_values(1)
                    # priority veya difficulty sütununu bul
                    if 'priority' in headers:
                        col_idx = headers.index('priority') + 1
                    elif 'difficulty' in headers:
                        col_idx = headers.index('difficulty') + 1
                    else:
                        # Yeni sütun ekle
                        col_idx = len(headers) + 1
                        vocab_ws.update_cell(1, col_idx, 'priority')

                    vocab_ws.update_cell(idx, col_idx, new_priority)
                    return True
        except Exception as e:
            pass
    return False

def increase_priority(username, word):
    """Bilmedi - önceliği artır (Az -> Orta -> Çok)"""
    words = get_user_words(username)
    for w in words:
        if w['word'] == word:
            current = w.get('priority') or w.get('difficulty') or 'Çok'
            if current == 'Az':
                new_priority = 'Orta'
            elif current == 'Orta':
                new_priority = 'Çok'
            else:
                new_priority = 'Çok'  # Zaten en yüksek
            return update_priority(username, word, new_priority)
    return False

def decrease_priority(username, word):
    """Bildi - önceliği azalt (Çok -> Orta -> Az)"""
    words = get_user_words(username)
    for w in words:
        if w['word'] == word:
            current = w.get('priority') or w.get('difficulty') or 'Çok'
            if current == 'Çok':
                new_priority = 'Orta'
            elif current == 'Orta':
                new_priority = 'Az'
            else:
                new_priority = 'Az'  # Zaten en düşük
            return update_priority(username, word, new_priority)
    return False

def get_priority_value(priority):
    """Öncelik değeri: Çok=4, Orta=2, Az=1"""
    priority_map = {'Çok': 4, 'Orta': 2, 'Az': 1, 'Hard': 4, 'Normal': 2, 'Medium': 1}
    return priority_map.get(priority, 4)

def get_words_by_priority(username, count=5, used_words=None):
    """Önceliğe göre ağırlıklı kelime seçimi"""
    if used_words is None:
        used_words = set()

    words = get_user_words(username)
    if not words: return []

    # Daha önce kullanılmamış kelimeleri filtrele
    available_words = [w for w in words if w['word'] not in used_words]

    # Eğer yeterli kullanılmamış kelime yoksa, kullanılmışlardan da al
    if len(available_words) < count:
        available_words = words

    if not available_words: return []

    # Ağırlıklı seçim için liste oluştur
    weighted_words = []
    for w in available_words:
        priority = w.get('priority') or w.get('difficulty') or 'Çok'
        weight = get_priority_value(priority)
        # Her kelimenin ağırlığı kadar tekrar ekle
        weighted_words.extend([w] * weight)

    # Rastgele seç (ağırlıklı)
    selected = []
    selected_set = set()

    while len(selected) < min(count, len(available_words)) and weighted_words:
        choice = random.choice(weighted_words)
        if choice['word'] not in selected_set:
            selected.append(choice)
            selected_set.add(choice['word'])
            # Seçileni listeden çıkar
            weighted_words = [w for w in weighted_words if w['word'] != choice['word']]

    return selected

def get_smart_quiz_words(username, limit=5):
    """Sınav için akıllı kelime seçimi (önceliğe göre)"""
    words = get_user_words(username)
    if not words: return []

    # Önceliğe göre sırala (Çok önce)
    priority_order = {'Çok': 0, 'Hard': 0, 'Orta': 1, 'Normal': 1, 'Az': 2, 'Medium': 2}
    sorted_words = sorted(words, key=lambda x: priority_order.get(x.get('priority') or x.get('difficulty') or 'Çok', 0))

    # İlk limit kadar al
    return [w['word'] for w in sorted_words[:min(limit, len(sorted_words))]]

# --- 7. METİN OLUŞTURMA İÇİN KULLANILAN KELİMELERİ TAKİP ---
def get_used_words_for_text(username):
    """Metin oluşturmada kullanılan kelimeleri getir (session'dan)"""
    # Bu fonksiyon session_state ile çalışacak, DB'ye kaydetmeye gerek yok
    return st.session_state.get('used_text_words', set())

def mark_words_as_used(words):
    """Kelimeleri kullanılmış olarak işaretle"""
    if 'used_text_words' not in st.session_state:
        st.session_state['used_text_words'] = set()
    st.session_state['used_text_words'].update(words)

def reset_used_words():
    """Kullanılmış kelimeleri sıfırla"""
    st.session_state['used_text_words'] = set()

# --- 8. ESKİ FONKSİYONLAR (GERİYE UYUMLULUK) ---
def update_difficulty(username, word, status):
    """Eski fonksiyon - geriye uyumluluk için"""
    # Eski status'ları yeni sisteme çevir
    status_map = {'Hard': 'Çok', 'Normal': 'Orta', 'Medium': 'Az'}
    new_priority = status_map.get(status, status)
    return update_priority(username, word, new_priority)
