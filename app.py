import streamlit as st
from ai_logic import AITutor
import database as db
import pandas as pd
from gtts import gTTS
import io

st.set_page_config(page_title="MorningLingo", page_icon="☕", layout="wide")

# --- GİRİŞ SİSTEMİ ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ''
if 'real_name' not in st.session_state: st.session_state['real_name'] = ''

# Eğer giriş yapılmadıysa LOGIN ekranını göster
if not st.session_state['logged_in']:
    st.title("☕ MorningLingo'ya Hoşgeldin")
    
    tab_login, tab_signup = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_login:
        with st.form("login_form"):
            user = st.text_input("Kullanıcı Adı")
            pwd = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş Yap"):
                name = db.login_user(user, pwd)
                if name:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.session_state['real_name'] = name
                    st.success("Giriş başarılı! Yönlendiriliyorsun...")
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre yanlış.")

    with tab_signup:
        with st.form("signup_form"):
            new_user = st.text_input("Kullanıcı Adı Seç")
            new_pwd = st.text_input("Şifre Seç", type="password")
            new_name = st.text_input("Adın Nedir?")
            if st.form_submit_button("Kayıt Ol"):
                if new_user and new_pwd:
                    success = db.register_user(new_user, new_pwd, new_name)
                    if success:
                        st.success("Kayıt başarılı! Şimdi 'Giriş Yap' sekmesinden girebilirsin.")
                    else:
                        st.error("Bu kullanıcı adı zaten alınmış.")
    
    st.stop() # Giriş yapmadan aşağıdaki kodları çalıştırma

# --- ANA UYGULAMA (Giriş yapıldıysa burası çalışır) ---

# Sidebar
with st.sidebar:
    st.title(f"Merhaba, {st.session_state['real_name']}! 👋")
    
    if st.button("Çıkış Yap"):
        st.session_state['logged_in'] = False
        st.rerun()
        
    st.divider()
    
    # Kelime Sayacı (Buluttan çeker)
    user_words = db.get_user_words(st.session_state['username'])
    st.metric("🧠 Kelime Hazinen", len(user_words))
    
    st.divider()
    
    # API Key Ayarı
    if 'api_key' not in st.session_state: st.session_state['api_key'] = ''
    api_key_input = st.text_input("Google API Key", value=st.session_state['api_key'], type="password")
    if api_key_input: st.session_state['api_key'] = api_key_input
    
    level = st.selectbox("Seviye", ["B1", "B2", "C1"])
    word_limit = st.slider("Hikaye/Sınav Limiti", 3, 20, 5)

if not st.session_state['api_key']:
    st.warning("👈 Lütfen sol taraftan Google API Key gir.")
    st.stop()

tutor = AITutor(st.session_state['api_key'])

# Sekmeler
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📖 Okuma", "✍️ Çeviri", "📚 Kelimelerim", "🧩 Hikaye", "🧠 Sınav", "⚡ Hızlı Test"])

# --- TAB 1: OKUMA ---
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1: st.header(f"Günün {level} Okuma Metni")
    with col2:
        if st.button("🔄 Yeni Metin"):
            with st.spinner("Yazılıyor..."):
                st.session_state['current_reading'] = tutor.generate_reading_text(level)
    if 'current_reading' in st.session_state:
        st.write(st.session_state['current_reading'])
        if st.button("🔊 Dinle", key="t1_audio"):
            try:
                tts = gTTS(text=st.session_state['current_reading'], lang='en')
                ab = io.BytesIO()
                tts.write_to_fp(ab)
                st.audio(ab, format='audio/mp3')
            except: pass

# --- TAB 2: ÇEVİRİ ---
with tab2:
    st.header("Çeviri")
    if st.button("🇹🇷 Türkçe Metin"):
        st.session_state['ch_text'] = tutor.generate_translation_challenge(level)
    if 'ch_text' in st.session_state:
        st.info(st.session_state['ch_text'])
        u_in = st.text_area("Çeviri:")
        if st.button("Kontrol") and u_in:
            st.write(tutor.check_translation(st.session_state['ch_text'], u_in))

# --- TAB 3: BULUT KELİME DEFTERİ ---
with tab3:
    st.header("📚 Kelimelerim (Bulut)")
    w_add = st.text_input("Kelime Ekle", key="cloud_w")
    if st.button("✨ Otomatik Analiz"):
        if w_add:
            m, e, s = tutor.analyze_word(w_add)
            st.session_state['nm'], st.session_state['ne'], st.session_state['ns'] = m, e, s
    
    with st.form("cloud_save"):
        fm = st.text_input("Anlam", value=st.session_state.get('nm',''))
        fe = st.text_input("Örnek", value=st.session_state.get('ne',''))
        fs = st.text_input("Eş Anlam", value=st.session_state.get('ns',''))
        if st.form_submit_button("💾 Kaydet"):
            db.add_word(st.session_state['username'], w_add, fm, fs)
            st.success("Buluta Kaydedildi!")
            st.rerun()

    # Listeleme
    if user_words:
        df = pd.DataFrame(user_words)
        st.dataframe(df[['word', 'meaning', 'synonyms', 'date']], use_container_width=True)
        to_del = st.text_input("Silmek istediğin kelimeyi yaz:")
        if st.button("Sil") and to_del:
            db.delete_word(to_del, st.session_state['username'])
            st.rerun()

# --- TAB 4: HİKAYE ---
with tab4:
    st.header("🧩 Hikaye")
    if st.button("Hikaye Yarat"):
        rw = db.get_random_words(st.session_state['username'], word_limit)
        st.session_state['story'] = tutor.generate_story_with_words(rw)
    if 'story' in st.session_state:
        st.write(st.session_state['story'])
        if st.button("🔊 Dinle", key="s_aud"):
             try:
                tts = gTTS(text=st.session_state['story'].replace('**', ''), lang='en')
                ab = io.BytesIO()
                tts.write_to_fp(ab)
                st.audio(ab, format='audio/mp3')
             except: pass

# --- TAB 5 & 6 (Sınav ve Hızlı Test) ---
with tab5:
    st.header("Sınav")
    if st.button("Başlat"):
        qw = db.get_random_words(st.session_state['username'], word_limit)
        st.session_state['q_data'] = tutor.generate_quiz(qw)
    
    if 'q_data' in st.session_state:
        for i, q in enumerate(st.session_state['q_data']):
            st.markdown(f"**{i+1}. {q['question']}**")
            st.radio("Cevap", q['options'], key=f"qz_{i}")

with tab6:
    st.header("⚡ Hızlı Test")
    if st.button("Soru Getir"):
        tr, en = tutor.generate_tr_en_quiz(level)
        st.session_state['ftr'], st.session_state['fen'] = tr, en
    
    if 'ftr' in st.session_state:
        st.markdown(f"### {st.session_state['ftr']}")
        with st.expander("Cevap"):
            st.markdown(f"**{st.session_state['fen']}**")
            if st.button("➕ Ekle"):
                m, e, s = tutor.analyze_word(st.session_state['fen'])
                db.add_word(st.session_state['username'], st.session_state['fen'], m, s)
                st.success("Eklendi!")