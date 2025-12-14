import streamlit as st
from ai_logic import AITutor
import database as db
import pandas as pd
from gtts import gTTS
import io
import random
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="MorningLingo", page_icon="☕", layout="wide")

# --- MOBİL UYUMLULUK ---
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#FF4B4B">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
""", unsafe_allow_html=True)

# --- TASARIM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .install-guide { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; margin-bottom: 20px; font-size: 13px; text-align: center; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: none; }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 20px; background-color: #f0f2f6; border: none; padding: 0 20px; font-weight: 500; color: #555; font-size: 14px; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B; color: white; box-shadow: 0 4px 6px rgba(255, 75, 75, 0.3); }
    
    .flashcard { background: linear-gradient(145deg, #ffffff, #f9f9f9); border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #eee; margin-bottom: 20px; transition: transform 0.3s ease; position: relative; }
    .flashcard-word { font-size: 38px; font-weight: 600; color: #2c3e50; margin: 15px 0; }
    .flashcard-meaning { font-size: 24px; color: #e74c3c; margin-top: 10px; font-weight: 500; }
    
    .forms-box { background-color: #e8f8f5; border-left: 4px solid #1abc9c; border-radius: 5px; padding: 8px; margin-top: 15px; font-size: 13px; color: #16a085; font-weight: 600; text-align: left; }
    
    .badge-hard { background-color: #fadbd8; color: #c0392b; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: bold; }
    .badge-medium { background-color: #fdebd0; color: #d68910; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: bold; }
    .badge-normal { background-color: #d5f5e3; color: #27ae60; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: bold; }
    
    .stButton button { border-radius: 12px; font-weight: 500; border: none; transition: all 0.2s; }
    .stButton button:hover { opacity: 0.9; transform: scale(1.02); }
    
    audio { height: 30px; margin-top: 5px; width: 100%; }
</style>
""", unsafe_allow_html=True)

def celebrate_xp(amount):
    st.toast(f"🎉 +{amount} XP Kazandın!", icon="⭐")
    time.sleep(0.5)

# --- GİRİŞ ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ''
if 'real_name' not in st.session_state: st.session_state['real_name'] = ''

if not st.session_state['logged_in']:
    col_c1, col_c2, col_c3 = st.columns([1,2,1])
    with col_c2:
        st.markdown("<h1 style='text-align: center; color: #2c3e50;'>☕ MorningLingo</h1>", unsafe_allow_html=True)
        st.markdown("""<div class="install-guide">📱 <b>Mobil Uygulama Gibi Kullan:</b><br>iOS: Paylaş ➡️ Ana Ekrana Ekle<br>Android: 3 Nokta ➡️ Uygulamayı Yükle</div>""", unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["Giriş Yap", "Kayıt Ol"])
        with tab_login:
            with st.form("login_form"):
                user = st.text_input("Kullanıcı Adı")
                pwd = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş Yap", use_container_width=True):
                    name = db.login_user(user, pwd)
                    if name:
                        st.session_state['logged_in'] = True; st.session_state['username'] = user; st.session_state['real_name'] = name; st.success("Giriş başarılı!"); st.rerun()
                    else: st.error("Hatalı giriş.")
        with tab_signup:
            with st.form("signup_form"):
                new_user = st.text_input("Kullanıcı Adı Seç")
                new_pwd = st.text_input("Şifre Seç", type="password")
                new_name = st.text_input("Adın Nedir?")
                if st.form_submit_button("Kayıt Ol", use_container_width=True):
                    if db.register_user(new_user, new_pwd, new_name): st.success("Kayıt başarılı! Giriş yapabilirsin.")
                    else: st.error("Kullanıcı adı alınmış.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👋 {st.session_state['real_name']}")
    
    current_xp = db.get_user_xp(st.session_state['username'])
    level = int(current_xp / 100) + 1
    progress = (current_xp % 100) / 100.0
    
    st.markdown(f"""
    <div style="background-color: #f0f2f6; border-radius: 10px; padding: 10px; margin-bottom: 20px;">
        <div style="display:flex; justify-content:space-between; font-weight:bold; color:#2c3e50; font-size:12px;">
            <span>Level {level}</span>
            <span>{current_xp} XP</span>
        </div>
        <div style="width:100%; background-color:#ddd; height:6px; border-radius:3px; margin-top:5px;">
            <div style="width:{progress*100}%; background-color:#FF4B4B; height:6px; border-radius:3px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Çıkış", use_container_width=True):
        st.session_state['logged_in'] = False; st.rerun()
    
    st.divider()
    user_words = db.get_user_words(st.session_state['username'])
    st.metric("🧠 Kelimelerin", len(user_words))
    
    # --- YENİ EKLENEN: EXCEL İNDİRME ---
    if user_words:
        st.markdown("---")
        df_export = pd.DataFrame(user_words)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Listemi İndir (Excel/CSV)",
            data=csv,
            file_name='morninglingo_kelimelerim.csv',
            mime='text/csv',
            use_container_width=True
        )
    # -----------------------------------

    st.divider()
    with st.popover("ℹ️ API Key Yardımı"):
        st.markdown("**1.** [Google AI Studio](https://aistudio.google.com/app/apikey)'ya git.\n**2.** 'Create API Key' de.\n**3.** Kodu kopyala ve yapıştır.")
    
    if 'api_key' not in st.session_state: st.session_state['api_key'] = ''
    api_key_input = st.text_input("Google API Key", value=st.session_state['api_key'], type="password")
    if api_key_input: st.session_state['api_key'] = api_key_input
    
    st.markdown("### Ayarlar")
    lang_level = st.selectbox("Seviye", ["B1", "B2", "C1"])
    reading_len = st.slider("Metin Uzunluğu", 50, 800, 150, 50)
    word_limit = st.slider("Soru Limiti", 3, 20, 5)

if not st.session_state['api_key']: st.warning("👈 Soldan API Key girerek başla."); st.stop()
tutor = AITutor(st.session_state['api_key'])

# --- TABS ---
tab_chat, tab1, tab2, tab3, tab_fc, tab_speak, tab4, tab5, tab6 = st.tabs(
    ["💬 Chat", "📖 Okuma", "✍️ Çeviri", "📚 Kelimeler", "🃏 Kartlar", "🎙️ Konuşma", "🧩 Hikaye", "🧠 Sınav", "⚡ Hızlı"]
)

with tab_chat:
    st.header("🎓 Teacher Lingo")
    if "messages" not in st.session_state: st.session_state.messages = [{"role": "model", "parts": ["Hello! Ready to chat?"]}]
    for i, m in enumerate(st.session_state.messages):
        with st.chat_message("user" if m["role"]=="user" else "assistant"): 
            st.write(m["parts"][0])
            if m["role"] == "assistant":
                if st.button("🔊", key=f"chat_aud_{i}"):
                    tts = gTTS(m["parts"][0], lang='en'); ab=io.BytesIO(); tts.write_to_fp(ab); st.audio(ab, format='audio/mp3')

    if p := st.chat_input("Mesaj yaz..."):
        st.session_state.messages.append({"role": "user", "parts": [p]})
        with st.chat_message("user"): st.write(p)
        db.add_xp(st.session_state['username'], 5); celebrate_xp(5)
        with st.chat_message("assistant"):
            with st.spinner("..."):
                resp = tutor.get_chat_response(p, st.session_state.messages[:-1])
                st.write(resp)
        st.session_state.messages.append({"role": "model", "parts": [resp]})
        st.rerun()

with tab1: # OKUMA
    col1, col2 = st.columns([3, 1])
    with col1: st.subheader(f"📖 {lang_level} Okuma")
    with col2:
        if st.button("🔄 Yeni", use_container_width=True): 
            st.session_state['curr_read'] = tutor.generate_reading_text(lang_level, reading_len)
            db.add_xp(st.session_state['username'], 10); celebrate_xp(10)
    if 'curr_read' in st.session_state:
        st.markdown(f"<div style='background-color:white; padding:15px; border-radius:10px; border:1px solid #eee; font-size:15px;'>{st.session_state['curr_read']}</div>", unsafe_allow_html=True)
        if st.button("🔊 Metni Dinle", key="t1a"):
            tts = gTTS(st.session_state['curr_read'], lang='en'); ab=io.BytesIO(); tts.write_to_fp(ab); st.audio(ab, format='audio/mp3')

with tab2: # ÇEVİRİ
    st.subheader("✍️ Çeviri")
    if st.button("🇹🇷 Cümle Getir"): st.session_state['ch_txt'] = tutor.generate_translation_challenge(lang_level)
    if 'ch_txt' in st.session_state:
        st.info(st.session_state['ch_txt'])
        ui = st.text_area("İngilizcesi:")
        if st.button("Kontrol") and ui: 
            st.write(tutor.check_translation(st.session_state['ch_txt'], ui))
            db.add_xp(st.session_state['username'], 15); celebrate_xp(15)

with tab3: # KELİMELERİM
    st.subheader("📚 Kelime Defteri")
    
    # --- YENİ EKLENEN: ÖZELLEŞTİRİLEBİLİR HIZLI BAŞLANGIÇ ---
    if not user_words:
        st.info("👋 Listen boş! Senin için özel bir paket hazırlayabilirim.")
        with st.form("starter_kit"):
            st.markdown("### 🚀 Hızlı Başlangıç")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                start_count = st.slider("Kaç kelime olsun?", 3, 15, 5)
            with col_s2:
                start_level = st.selectbox("Hangi seviye?", ["A1 (Başlangıç)", "A2 (Temel)", "B1 (Orta)", "B2 (İyi)", "C1 (İleri)"])
            
            if st.form_submit_button("Paketi Oluştur ve Ekle", use_container_width=True):
                with st.spinner(f"{start_level} seviyesinde {start_count} kelime hazırlanıyor..."):
                    # Level isminden sadece kodu (A1, B1 vs) al
                    clean_level = start_level.split()[0]
                    words_data = tutor.generate_starter_pack(clean_level, start_count)
                    
                    if words_data:
                        for w in words_data:
                            # Her kelimeyi veritabanına ekle
                            db.add_word(
                                st.session_state['username'], 
                                w.get('word', '-'), 
                                w.get('meaning', '-'), 
                                w.get('example', '-'), 
                                w.get('synonyms', '-'), 
                                w.get('forms', '-')
                            )
                        st.success(f"Harika! {start_count} yeni kelime eklendi."); time.sleep(1); st.rerun()
                    else:
                        st.error("Bir sorun oluştu, tekrar dene.")
    # -----------------------------------------------------------

    with st.expander("➕ Tek Tek Kelime Ekle", expanded=False):
        wa = st.text_input("Kelime", key="cw")
        if st.button("Analiz"):
            if wa: 
                m,e,s,f = tutor.analyze_word(wa)
                st.session_state.update({'nm':m, 'ne':e, 'ns':s, 'nf':f})
        with st.form("cs"):
            c1, c2 = st.columns(2)
            with c1:
                fm=st.text_input("Anlam", value=st.session_state.get('nm',''))
                fe=st.text_input("Örnek", value=st.session_state.get('ne',''))
            with c2:
                fs=st.text_input("Eş Anlam", value=st.session_state.get('ns',''))
                ff=st.text_input("Halleri", value=st.session_state.get('nf',''))
            if st.form_submit_button("Kaydet", use_container_width=True): 
                db.add_word(st.session_state['username'], wa, fm, fe, fs, ff)
                celebrate_xp(10); st.success("OK"); st.rerun()
    
    if user_words:
        df = pd.DataFrame(user_words)
        if 'forms' not in df.columns: df['forms'] = "-"
        if 'difficulty' not in df.columns: df['difficulty'] = "Hard"
        st.dataframe(df[['word', 'meaning', 'example', 'forms', 'difficulty']], use_container_width=True)
        with st.expander("Sil"):
            d = st.selectbox("Seç:", [w['word'] for w in user_words])
            if st.button("Sil"): db.delete_word(d, st.session_state['username']); st.rerun()

with tab_fc: # FLASHCARD
    st.subheader("🃏 Kartlar")
    if not user_words: st.info("Kelime ekle!")
    else:
        if 'fc_i' not in st.session_state: st.session_state['fc_i']=0
        if 'fc_f' not in st.session_state: st.session_state['fc_f']=False
        
        if st.button("🔀 Karıştır"):
             random.shuffle(user_words)
             st.session_state['fc_i']=0; st.session_state['fc_f']=False; st.rerun()
             
        cw = user_words[st.session_state['fc_i'] % len(user_words)]
        status = cw.get('difficulty', 'Hard')
        
        if status == 'Hard': badge = '<span class="badge-hard">Zor</span>'
        elif status == 'Medium': badge = '<span class="badge-medium">Tekrar</span>'
        else: badge = '<span class="badge-normal">Normal</span>'

        front_html = f"""<div style="margin-bottom:15px;">{badge}</div><div class="flashcard-word">{cw['word']}</div>"""
        
        # YENİ: SES BUTONU (Kartın hemen altına)
        if st.button("🔊", key=f"fc_sound_{cw['word']}"):
             tts = gTTS(cw['word'], lang='en'); ab=io.BytesIO(); tts.write_to_fp(ab); st.audio(ab, format='audio/mp3')

        forms_html = f'<div class="forms-box">🏗️ {cw.get("forms", "-")}</div>' if cw.get("forms") and cw.get("forms") != "-" else ""
        back_content = f"""<div class="flashcard-meaning">{cw["meaning"]}</div><div style="margin: 15px 0; color:#555; font-style:italic;">"{cw.get('example', '-')}"</div>{forms_html}"""
        
        st.markdown(f"""<div class="flashcard">{front_html}{back_content if st.session_state['fc_f'] else '<div style="margin-top:30px; color:#ccc;">❓ Çevir</div>'}</div>""", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("❌ Bilemedim", use_container_width=True):
                if status != 'Hard': db.update_difficulty(st.session_state['username'], cw['word'], 'Hard')
                st.session_state['fc_i'] += 1; st.session_state['fc_f'] = False; st.rerun()
        with c2:
            if st.button("🔄 Çevir", use_container_width=True): st.session_state['fc_f'] = not st.session_state['fc_f']; st.rerun()
        with c3:
            if st.button("✅ Biliyorum", use_container_width=True):
                new_status = 'Medium' if status == 'Hard' else 'Normal'
                if new_status != status: db.update_difficulty(st.session_state['username'], cw['word'], new_status)
                st.session_state['fc_i'] += 1; st.session_state['fc_f'] = False; st.rerun()
        st.caption(f"{st.session_state['fc_i'] % len(user_words) + 1} / {len(user_words)}")

with tab_speak:
    st.subheader("🎙️ Telaffuz")
    if user_words:
        if 'speak_word' not in st.session_state: st.session_state['speak_word'] = random.choice(user_words)['word']
        if st.button("🎲 Değiştir"): st.session_state['speak_word'] = random.choice(user_words)['word']
        target = st.session_state['speak_word']
        st.markdown(f"<h2 style='text-align:center;'>{target}</h2>", unsafe_allow_html=True)
        if st.button("🔊 Doğrusunu Dinle"):
             tts = gTTS(target, lang='en'); ab=io.BytesIO(); tts.write_to_fp(ab); st.audio(ab, format='audio/mp3')
        audio_value = st.audio_input("Sesini Kaydet")
        if audio_value:
            st.audio(audio_value)
            if st.button("📩 Puanla"):
                with st.spinner("Dinliyorum..."):
                    feedback = tutor.check_pronunciation(audio_value.read(), target)
                    st.success("Sonuç:"); st.write(feedback); db.add_xp(st.session_state['username'], 20); celebrate_xp(20)
    else: st.warning("Kelime ekle!")

with tab4:
    st.subheader("🧩 Hikaye")
    if st.button("Hikaye Yarat"): 
        st.session_state['sty'] = tutor.generate_story_with_words(db.get_random_words(st.session_state['username'], word_limit))
        db.add_xp(st.session_state['username'], 15); celebrate_xp(15)
    if 'sty' in st.session_state: st.markdown(f"<div style='background-color:white; padding:15px; border-radius:10px; border:1px solid #eee;'>{st.session_state['sty']}</div>", unsafe_allow_html=True)

with tab5:
    st.subheader("🧠 Sınav")
    if st.button("Başla"): 
        smart_words = db.get_smart_quiz_words(st.session_state['username'], word_limit)
        st.session_state['qz'] = tutor.generate_quiz(smart_words)
    if 'qz' in st.session_state:
        for i,q in enumerate(st.session_state['qz']): 
            st.markdown(f"**{i+1}. {q['question']}**")
            st.radio("Seç:", q['options'], key=f"q{i}", label_visibility="collapsed")
            st.markdown("---")
        if st.button("Bitir"): db.add_xp(st.session_state['username'], 30); celebrate_xp(30)

with tab6:
    st.subheader("⚡ Hızlı Test")
    if st.button("Soru"): tr,en = tutor.generate_tr_en_quiz(lang_level); st.session_state.update({'ft':tr, 'fe':en})
    if 'ft' in st.session_state:
        st.markdown(f"<h3 style='text-align:center;'>{st.session_state['ft']}</h3>", unsafe_allow_html=True)
        with st.expander("Cevap"): 
            st.markdown(f"**{st.session_state['fe']}**")
            if st.button("Ekle"): 
                m,e,s,f=tutor.analyze_word(st.session_state['fe'])
                db.add_word(st.session_state['username'], st.session_state['fe'], m, e if 'e' in locals() else "-", s, f)
                celebrate_xp(10); st.success("OK")