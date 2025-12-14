import streamlit as st
# Sayfa ayarını EN BAŞTA yapmalıyız
st.set_page_config(page_title="MorningLingo", page_icon="☕", layout="wide")

from ai_logic import AITutor
import database as db
import pandas as pd
from gtts import gTTS
import io
import random
import time

# --- MOBİL UYUMLULUK ---
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#FF4B4B">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 20px; background-color: #f0f2f6; padding: 0 20px; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B; color: white; }
    .flashcard { background: linear-gradient(145deg, #ffffff, #f9f9f9); border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .flashcard-word { font-size: 38px; font-weight: 600; color: #2c3e50; margin: 15px 0; }
    .flashcard-meaning { font-size: 24px; color: #e74c3c; margin-top: 10px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

def celebrate_xp(amount):
    st.toast(f"🎉 +{amount} XP Kazandın!", icon="⭐")
    time.sleep(0.5)

# --- GİRİŞ KONTROLÜ ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ''
if 'real_name' not in st.session_state: st.session_state['real_name'] = ''

if not st.session_state['logged_in']:
    st.title("☕ MorningLingo")
    tab_login, tab_signup = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_login:
        with st.form("login_form"):
            user = st.text_input("Kullanıcı Adı")
            pwd = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş Yap", use_container_width=True):
                name = db.login_user(user, pwd)
                if name:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.session_state['real_name'] = name
                    st.success("Giriş başarılı!"); st.rerun()
                else: st.error("Hatalı giriş.")
                
    with tab_signup:
        with st.form("signup_form"):
            new_user = st.text_input("Kullanıcı Adı Seç")
            new_pwd = st.text_input("Şifre Seç", type="password")
            new_name = st.text_input("Adın Nedir?")
            if st.form_submit_button("Kayıt Ol", use_container_width=True):
                if db.register_user(new_user, new_pwd, new_name): 
                    st.success("Kayıt başarılı! Giriş yapabilirsin.")
                else: st.error("Kullanıcı adı alınmış.")
    st.stop()

# --- SIDEBAR (YAN MENÜ) ---
with st.sidebar:
    st.write(f"👋 Merhaba, **{st.session_state['real_name']}**")
    
    # XP GÖSTERGESİ
    current_xp = db.get_user_xp(st.session_state['username'])
    level = int(current_xp / 100) + 1
    progress = (current_xp % 100) / 100.0
    st.progress(progress, text=f"Seviye {level} ({current_xp} XP)")
    
    if st.button("🚪 Çıkış"):
        st.session_state['logged_in'] = False; st.rerun()

    st.divider()
    
    # API KEY YÖNETİMİ (Otomatik)
    if 'api_key' in st.secrets:
        st.session_state['api_key'] = st.secrets['api_key']
    
    if 'api_key' not in st.session_state or not st.session_state['api_key']:
        st.warning("⚠️ API Key Eksik!")
        st.stop()

    # AYARLAR
    lang_level = st.selectbox("Seviye", ["A1", "A2", "B1", "B2", "C1"])
    word_limit = st.slider("Soru Limiti", 3, 20, 5)

# --- ANA UYGULAMA ---
try:
    tutor = AITutor(st.session_state['api_key'])
except Exception as e:
    st.error(f"Yapay Zeka Bağlantı Hatası: {e}")
    st.stop()

user_words = db.get_user_words(st.session_state['username'])

tabs = st.tabs(["💬 Chat", "📚 Kelimeler", "🃏 Kartlar", "📖 Okuma", "🧩 Hikaye", "🧠 Sınav", "⚡ Hızlı"])

with tabs[0]: # CHAT
    st.header("Teacher Lingo")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "model", "parts": ["Hello! Ready to chat?"]}]
    
    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["role"]=="user" else "assistant"):
            st.write(msg["parts"][0])
            
    if prompt := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "parts": [prompt]})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Düşünüyor..."):
                response = tutor.get_chat_response(prompt, st.session_state.messages)
                st.write(response)
        st.session_state.messages.append({"role": "model", "parts": [response]})
        db.add_xp(st.session_state['username'], 5)

with tabs[1]: # KELİMELER
    st.subheader("Kelime Defterim")
    
    # Hızlı Paket Ekleme
    if not user_words:
        if st.button("🚀 Bana Başlangıç Paketi Ekle (5 Kelime)"):
            with st.spinner("Hazırlanıyor..."):
                words = tutor.generate_starter_pack(lang_level, 5)
                if words:
                    for w in words:
                        db.add_word(st.session_state['username'], w.get('word','-'), w.get('meaning','-'), w.get('example','-'), w.get('synonyms','-'), w.get('forms','-'))
                    st.success("Eklendi!"); time.sleep(1); st.rerun()
                else:
                    st.error("Paket oluşturulamadı, lütfen tekrar dene.")

    # Tekil Ekleme
    c1, c2 = st.columns([3,1])
    with c1: new_w = st.text_input("Yeni Kelime")
    with c2: 
        if st.button("Analiz Et & Ekle") and new_w:
            m, e, s, f = tutor.analyze_word(new_w)
            db.add_word(st.session_state['username'], new_w, m, e, s, f)
            st.success(f"{new_w} eklendi!"); db.add_xp(st.session_state['username'], 10); time.sleep(1); st.rerun()

    if user_words:
        df = pd.DataFrame(user_words)
        st.dataframe(df, use_container_width=True)
        
        del_w = st.selectbox("Silinecek Kelime:", [w['word'] for w in user_words])
        if st.button("Sil"):
            db.delete_word(del_w, st.session_state['username'])
            st.rerun()

with tabs[2]: # KARTLAR
    if user_words:
        if 'fc_idx' not in st.session_state: st.session_state['fc_idx'] = 0
        if 'fc_flip' not in st.session_state: st.session_state['fc_flip'] = False
        
        # Döngüsel index
        w = user_words[st.session_state['fc_idx'] % len(user_words)]
        
        st.markdown(f"""
        <div class="flashcard">
            <div class="flashcard-word">{w['word']}</div>
            {f'<div class="flashcard-meaning">{w["meaning"]}</div><div style="color:#666">"{w["example"]}"</div>' if st.session_state['fc_flip'] else '<div style="margin-top:20px; color:#aaa">Cevabı Gör</div>'}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1: 
            if st.button("❌ Bilemedim"): 
                db.update_difficulty(st.session_state['username'], w['word'], 'Hard')
                st.session_state['fc_idx'] += 1; st.session_state['fc_flip'] = False; st.rerun()
        with col2: 
            if st.button("🔄 Çevir"): 
                st.session_state['fc_flip'] = not st.session_state['fc_flip']; st.rerun()
        with col3: 
            if st.button("✅ Bildim"): 
                db.update_difficulty(st.session_state['username'], w['word'], 'Normal')
                st.session_state['fc_idx'] += 1; st.session_state['fc_flip'] = False; st.rerun()
    else: st.info("Kartlar için kelime ekle.")

with tabs[3]: # OKUMA
    if st.button("Yeni Metin Oluştur"):
        st.session_state['read_text'] = tutor.generate_reading_text(lang_level, 100)
    
    if 'read_text' in st.session_state:
        st.write(st.session_state['read_text'])
        if st.button("🔊 Oku"):
            tts = gTTS(st.session_state['read_text'], lang='en'); ab=io.BytesIO(); tts.write_to_fp(ab); st.audio(ab, format='audio/mp3')

with tabs[4]: # HİKAYE
    if st.button("Hikaye Yaz"):
        rnd_words = db.get_random_words(st.session_state['username'], 5)
        if rnd_words:
            st.session_state['story'] = tutor.generate_story_with_words(rnd_words)
        else: st.warning("Kelime ekle!")
            
    if 'story' in st.session_state: st.write(st.session_state['story'])

with tabs[5]: # SINAV
    if st.button("Sınav Ol"):
        q_words = db.get_smart_quiz_words(st.session_state['username'], 5)
        if q_words:
            st.session_state['quiz'] = tutor.generate_quiz(q_words)
        else: st.warning("Kelime ekle!")
    
    if 'quiz' in st.session_state:
        for i, q in enumerate(st.session_state['quiz']):
            st.write(f"**{i+1}. {q.get('question','Soru yok')}**")
            st.radio("Seçenekler", q.get('options',[]), key=f"q{i}")
        if st.button("Bitir"):
            st.success("Tebrikler!"); db.add_xp(st.session_state['username'], 50); celebrate_xp(50)

with tabs[6]: # HIZLI TEST
    if st.button("Kelime Getir"):
        tr, en = tutor.generate_tr_en_quiz(lang_level)
        st.session_state['fast_q'] = (tr, en)
    
    if 'fast_q' in st.session_state:
        tr, en = st.session_state['fast_q']
        st.markdown(f"### {tr}")
        if st.button("Cevabı Gör"):
            st.success(en)
            if st.button("Listeme Ekle"):
                db.add_word(st.session_state['username'], en, tr)
                st.success("Eklendi!")
