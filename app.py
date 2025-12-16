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

# --- MOBİL UYUMLULUK VE STİLLER ---
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#FF4B4B">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 4px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { height: 40px; border-radius: 15px; background-color: #f0f2f6; padding: 0 12px; font-size: 14px; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B; color: white; }

    .flashcard {
        background: linear-gradient(145deg, #ffffff, #f9f9f9);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        min-height: 200px;
    }
    .flashcard-word { font-size: 36px; font-weight: 600; color: #2c3e50; margin: 15px 0; }
    .flashcard-meaning { font-size: 22px; color: #e74c3c; margin-top: 10px; font-weight: 500; }
    .flashcard-date { font-size: 12px; color: #999; margin-top: 10px; }
    .flashcard-priority { font-size: 14px; padding: 4px 12px; border-radius: 10px; display: inline-block; margin-top: 10px; }
    .priority-high { background-color: #ffebee; color: #c62828; }
    .priority-medium { background-color: #fff3e0; color: #ef6c00; }
    .priority-low { background-color: #e8f5e9; color: #2e7d32; }

    .word-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 4px solid #FF4B4B;
    }

    .leaderboard-item {
        background: linear-gradient(90deg, #f8f9fa 0%, #ffffff 100%);
        padding: 12px 20px;
        border-radius: 10px;
        margin: 5px 0;
        display: flex;
        align-items: center;
    }
    .leaderboard-rank { font-size: 20px; font-weight: bold; color: #FF4B4B; width: 40px; }
    .leaderboard-name { flex: 1; font-weight: 500; }
    .leaderboard-xp { color: #666; font-weight: 600; }

    .highlight-word { background-color: #fff3cd; padding: 2px 4px; border-radius: 3px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


def celebrate_xp(amount):
    st.toast(f"+{amount} XP Kazandin!", icon="⭐")
    time.sleep(0.3)


# --- GİRİŞ KONTROLÜ ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'real_name' not in st.session_state:
    st.session_state['real_name'] = ''

if not st.session_state['logged_in']:
    st.title("☕ MorningLingo")
    st.caption("Ingilizce Ogrenme Platformu")

    tab_login, tab_signup = st.tabs(["Giris Yap", "Kayit Ol"])

    with tab_login:
        with st.form("login_form"):
            user = st.text_input("Kullanici Adi")
            pwd = st.text_input("Sifre", type="password")
            if st.form_submit_button("Giris Yap", use_container_width=True):
                name = db.login_user(user, pwd)
                if name:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.session_state['real_name'] = name
                    st.success("Giris basarili!")
                    st.rerun()
                else:
                    st.error("Hatali giris.")

    with tab_signup:
        with st.form("signup_form"):
            new_user = st.text_input("Kullanici Adi Sec")
            new_pwd = st.text_input("Sifre Sec", type="password")
            new_name = st.text_input("Adin Nedir?")
            if st.form_submit_button("Kayit Ol", use_container_width=True):
                if new_user and new_pwd and new_name:
                    if db.register_user(new_user, new_pwd, new_name):
                        st.success("Kayit basarili! Giris yapabilirsin.")
                    else:
                        st.error("Kullanici adi alinmis.")
                else:
                    st.warning("Tum alanlari doldur.")
    st.stop()

# --- SIDEBAR (YAN MENÜ) ---
with st.sidebar:
    st.write(f"Merhaba, **{st.session_state['real_name']}**")

    # XP GÖSTERGESİ
    current_xp = db.get_user_xp(st.session_state['username'])
    level = int(current_xp / 100) + 1
    progress = (current_xp % 100) / 100.0
    st.progress(progress, text=f"Seviye {level} ({current_xp} XP)")

    if st.button("Cikis"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.divider()

    # API KEY YÖNETİMİ
    if 'api_key' in st.secrets:
        st.session_state['api_key'] = st.secrets['api_key']

    if 'api_key' not in st.session_state or not st.session_state['api_key']:
        st.warning("API Key Eksik!")
        st.stop()

    # GENEL AYARLAR
    st.subheader("Ayarlar")
    lang_level = st.selectbox("Dil Seviyesi", ["A1", "A2", "B1", "B2", "C1", "C2"])
    word_limit = st.slider("Kelime/Soru Limiti", 3, 20, 5)

# --- ANA UYGULAMA ---
try:
    tutor = AITutor(st.session_state['api_key'])
except Exception as e:
    st.error(f"Yapay Zeka Baglanti Hatasi: {e}")
    st.stop()

user_words = db.get_user_words(st.session_state['username'])

# --- TABS ---
tabs = st.tabs([
    "💬 Chat",
    "📚 Kelimeler",
    "🃏 Kartlar",
    "📝 Metin Olustur",
    "📖 Kelimelerden Metin",
    "🎲 Rastgele Kelime",
    "🧠 Sinav",
    "🏆 Liderlik"
])

# ==================== TAB 1: CHAT ====================
with tabs[0]:
    st.header("Teacher Lingo ile Sohbet")
    st.caption("Ingilizce sorularini sor, pratik yap!")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "model", "parts": ["Hello! I'm Teacher Lingo. How can I help you learn English today?"]}]

    # Chat geçmişi
    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.write(msg["parts"][0])

    # Yeni mesaj
    if prompt := st.chat_input("Mesajini yaz..."):
        st.session_state.messages.append({"role": "user", "parts": [prompt]})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Dusunuyor..."):
                response = tutor.get_chat_response(prompt, st.session_state.messages)
                st.write(response)
        st.session_state.messages.append({"role": "model", "parts": [response]})
        db.add_xp(st.session_state['username'], 5)
        celebrate_xp(5)

# ==================== TAB 2: KELİMELER ====================
with tabs[1]:
    st.header("Kelime Defterim")

    # Başlangıç paketi
    if not user_words:
        st.info("Henuz kelimen yok. Baslangic paketi ekleyebilir veya tek tek kelime ekleyebilirsin.")
        if st.button("Baslangic Paketi Ekle (5 Kelime)"):
            with st.spinner("Hazırlaniyor..."):
                words = tutor.generate_starter_pack(lang_level, 5)
                if words:
                    for w in words:
                        db.add_word(
                            st.session_state['username'],
                            w.get('word', '-'),
                            w.get('meaning', '-'),
                            w.get('example', '-'),
                            w.get('synonyms', '-'),
                            w.get('forms', '-')
                        )
                    st.success("5 kelime eklendi!")
                    db.add_xp(st.session_state['username'], 25)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Paket olusturulamadi, tekrar dene.")

    st.divider()

    # Tekil kelime ekleme
    st.subheader("Yeni Kelime Ekle")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_word = st.text_input("Kelime (yanlis yazsan bile duzeltilir)", placeholder="Ornek: beautful")
    with col2:
        st.write("")  # Spacing
        st.write("")
        add_btn = st.button("Analiz Et & Ekle", use_container_width=True)

    if add_btn and new_word:
        with st.spinner("Kelime analiz ediliyor..."):
            corrected, meaning, example, synonyms, forms = tutor.analyze_word(new_word)

            # Eğer kelime düzeltildiyse göster
            if corrected.lower() != new_word.lower():
                st.info(f"Kelime duzeltildi: '{new_word}' -> '{corrected}'")

            db.add_word(
                st.session_state['username'],
                corrected,
                meaning,
                example,
                synonyms,
                forms
            )
            st.success(f"'{corrected}' eklendi!")
            db.add_xp(st.session_state['username'], 10)
            celebrate_xp(10)
            time.sleep(1)
            st.rerun()

    # Kelime listesi
    if user_words:
        st.divider()
        st.subheader(f"Kelimelerim ({len(user_words)} kelime)")

        # DataFrame gösterimi
        df = pd.DataFrame(user_words)
        display_cols = ['word', 'meaning', 'example', 'synonyms', 'forms', 'date']
        available_cols = [c for c in display_cols if c in df.columns]
        if available_cols:
            st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

        # Kelime silme
        st.divider()
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            del_word = st.selectbox("Silinecek Kelime:", [w['word'] for w in user_words])
        with col_del2:
            st.write("")
            st.write("")
            if st.button("Sil", type="secondary"):
                db.delete_word(del_word, st.session_state['username'])
                st.success(f"'{del_word}' silindi!")
                time.sleep(0.5)
                st.rerun()

# ==================== TAB 3: KARTLAR ====================
with tabs[2]:
    st.header("Flashcard Calistir")
    st.caption("Oncelik sistemi: Cok > Orta > Az (Biliyorsan duser, bilmiyorsan yukselir)")

    if user_words:
        # Session state
        if 'fc_idx' not in st.session_state:
            st.session_state['fc_idx'] = 0
        if 'fc_flip' not in st.session_state:
            st.session_state['fc_flip'] = False

        # Döngüsel index
        current_idx = st.session_state['fc_idx'] % len(user_words)
        w = user_words[current_idx]

        # Öncelik bilgisi
        priority = w.get('priority') or w.get('difficulty') or 'Cok'
        priority_class = {
            'Cok': 'priority-high', 'Hard': 'priority-high',
            'Orta': 'priority-medium', 'Normal': 'priority-medium',
            'Az': 'priority-low', 'Medium': 'priority-low'
        }.get(priority, 'priority-high')

        priority_display = {'Cok': 'Cok', 'Hard': 'Cok', 'Orta': 'Orta', 'Normal': 'Orta', 'Az': 'Az', 'Medium': 'Az'}.get(priority, 'Cok')

        # Flashcard gösterimi
        st.markdown(f"""
        <div class="flashcard">
            <div class="flashcard-word">{w['word']}</div>
            {f'''
            <div class="flashcard-meaning">{w["meaning"]}</div>
            <div style="color:#666; margin-top:10px;">"{w.get("example", "-")}"</div>
            <div style="color:#888; font-size:13px; margin-top:8px;">Es anlamli: {w.get("synonyms", "-")}</div>
            <div style="color:#888; font-size:13px;">Formlar: {w.get("forms", "-")}</div>
            ''' if st.session_state['fc_flip'] else '<div style="margin-top:30px; color:#aaa; font-size:18px;">Cevabi gormek icin cevir</div>'}
            <div class="flashcard-date">Eklenme: {w.get('date', '-')}</div>
            <span class="flashcard-priority {priority_class}">Oncelik: {priority_display}</span>
        </div>
        """, unsafe_allow_html=True)

        # Kart sayacı
        st.caption(f"Kart {current_idx + 1} / {len(user_words)}")

        # Butonlar
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Hatirlamiyorum", use_container_width=True, type="secondary"):
                db.increase_priority(st.session_state['username'], w['word'])
                st.session_state['fc_idx'] += 1
                st.session_state['fc_flip'] = False
                st.rerun()
        with col2:
            if st.button("Cevir", use_container_width=True):
                st.session_state['fc_flip'] = not st.session_state['fc_flip']
                st.rerun()
        with col3:
            if st.button("Biliyorum", use_container_width=True, type="primary"):
                db.decrease_priority(st.session_state['username'], w['word'])
                st.session_state['fc_idx'] += 1
                st.session_state['fc_flip'] = False
                db.add_xp(st.session_state['username'], 2)
                st.rerun()

        # Sıfırlama
        st.divider()
        if st.button("Kartlari Bastan Basla"):
            st.session_state['fc_idx'] = 0
            st.session_state['fc_flip'] = False
            st.rerun()
    else:
        st.info("Kartlar icin once kelime ekle.")

# ==================== TAB 4: METİN OLUŞTUR ====================
with tabs[3]:
    st.header("Ingilizce Metin Olustur")
    st.caption("Seviye, tur ve uzunluk secip metin olustur")

    col1, col2, col3 = st.columns(3)
    with col1:
        text_level = st.selectbox("Seviye", ["A1", "A2", "B1", "B2", "C1", "C2"], key="text_level")
    with col2:
        text_type = st.selectbox("Metin Turu", [
            "Bilgilendirici",
            "Felsefi",
            "Sanatsal",
            "Edebi",
            "Ikna Edici",
            "Hukuki",
            "Dini"
        ])
    with col3:
        text_length = st.slider("Kelime Sayisi", 50, 800, 150, step=50)

    if st.button("Metin Olustur", use_container_width=True, type="primary"):
        with st.spinner("Metin olusturuluyor..."):
            generated_text = tutor.generate_text(text_level, text_type, text_length)
            st.session_state['generated_text'] = generated_text

    if 'generated_text' in st.session_state:
        st.divider()
        st.subheader("Olusturulan Metin")
        st.write(st.session_state['generated_text'])

        # Sesli okuma
        col_audio1, col_audio2 = st.columns([1, 3])
        with col_audio1:
            if st.button("Sesli Oku"):
                with st.spinner("Ses olusturuluyor..."):
                    tts = gTTS(st.session_state['generated_text'], lang='en')
                    audio_buffer = io.BytesIO()
                    tts.write_to_fp(audio_buffer)
                    st.audio(audio_buffer, format='audio/mp3')

# ==================== TAB 5: KELİMELERDEN METİN ====================
with tabs[4]:
    st.header("Kelime Listemden Metin Olustur")
    st.caption("Kaydettigin kelimelerden oncelik sistemine gore metin olusturur")

    if user_words:
        word_count = len(user_words)

        # En az 3 kelime gerekli
        if word_count < 3:
            st.warning(f"Bu ozellik icin en az 3 kelime gerekli. Simdilik {word_count} kelimen var.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                wl_level = st.selectbox("Seviye", ["A1", "A2", "B1", "B2", "C1", "C2"], key="wl_level")
            with col2:
                max_words = min(20, word_count)
                default_words = min(5, max_words)
                wl_count = st.slider("Kac kelime kullanilsin?", 3, max_words, default_words)

            st.info(f"Oncelik sistemine gore kelime secilecek: Cok oncelikli kelimeler 4x, Orta 2x, Az 1x olasilikla secilir.")

            # Kullanılmış kelimeleri göster
            used_words = db.get_used_words_for_text(st.session_state['username'])
            if used_words:
                st.caption(f"Daha once kullanilan kelimeler: {', '.join(used_words)}")
                if st.button("Kullanilan Kelimeleri Sifirla"):
                    db.reset_used_words()
                    st.rerun()

            if st.button("Metin Olustur", key="wl_generate", use_container_width=True, type="primary"):
                with st.spinner("Kelimeler seciliyor ve metin olusturuluyor..."):
                    # Önceliğe göre kelime seç
                    selected_words = db.get_words_by_priority(
                        st.session_state['username'],
                        wl_count,
                        used_words
                    )

                    if selected_words:
                        word_texts = [w['word'] for w in selected_words]
                        db.mark_words_as_used(word_texts)

                        # Metin oluştur
                        wl_text = tutor.generate_text_from_words(selected_words, wl_level, highlight=True)
                        st.session_state['wl_text'] = wl_text
                        st.session_state['wl_selected'] = selected_words
                    else:
                        st.warning("Yeterli kelime bulunamadi.")

            if 'wl_text' in st.session_state:
                st.divider()

                # Seçilen kelimeleri göster
                if 'wl_selected' in st.session_state:
                    selected_info = []
                    for w in st.session_state['wl_selected']:
                        p = w.get('priority') or w.get('difficulty') or 'Cok'
                        selected_info.append(f"{w['word']} ({p})")
                    st.caption(f"Secilen kelimeler: {', '.join(selected_info)}")

                st.subheader("Olusturulan Metin")
                st.markdown(st.session_state['wl_text'])

                # Sesli okuma
                if st.button("Sesli Oku", key="wl_audio"):
                    with st.spinner("Ses olusturuluyor..."):
                        # Markdown işaretlerini temizle
                        clean_text = st.session_state['wl_text'].replace("**", "")
                        tts = gTTS(clean_text, lang='en')
                        audio_buffer = io.BytesIO()
                        tts.write_to_fp(audio_buffer)
                        st.audio(audio_buffer, format='audio/mp3')
    else:
        st.info("Bu ozellik icin once kelime ekle.")

# ==================== TAB 6: RASTGELE KELİME ====================
with tabs[5]:
    st.header("Rastgele Kelime Ogren")
    st.caption("Seviyene uygun rastgele kelimeler al ve listene ekle")

    col1, col2 = st.columns(2)
    with col1:
        rw_level = st.selectbox("Seviye Sec", ["A1", "A2", "B1", "B2", "C1", "C2"], key="rw_level")
    with col2:
        rw_count = st.slider("Kac kelime?", 1, 20, 5, key="rw_count")

    if st.button("Rastgele Kelime Getir", use_container_width=True, type="primary"):
        with st.spinner(f"{rw_count} kelime getiriliyor..."):
            random_words = tutor.generate_random_words(rw_level, rw_count)
            if random_words:
                st.session_state['random_words'] = random_words
            else:
                st.error("Kelimeler getirilemedi. Tekrar dene.")

    if 'random_words' in st.session_state and st.session_state['random_words']:
        st.divider()
        st.subheader(f"Getirilen Kelimeler ({len(st.session_state['random_words'])} adet)")

        for i, word_data in enumerate(st.session_state['random_words']):
            with st.container():
                st.markdown(f"""
                <div class="word-card">
                    <div style="font-size: 20px; font-weight: bold; color: #2c3e50;">
                        {word_data.get('word', '-')}
                    </div>
                    <div style="color: #e74c3c; margin: 5px 0;">
                        {word_data.get('meaning', '-')}
                    </div>
                    <div style="color: #666; font-size: 14px;">
                        Ornek: "{word_data.get('example', '-')}"
                    </div>
                    <div style="color: #888; font-size: 13px; margin-top: 5px;">
                        Es anlamli: {word_data.get('synonyms', '-')} | Formlar: {word_data.get('forms', '-')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Ekleme butonu
                if st.button(f"➕ Listeme Ekle", key=f"add_rw_{i}"):
                    db.add_word(
                        st.session_state['username'],
                        word_data.get('word', '-'),
                        word_data.get('meaning', '-'),
                        word_data.get('example', '-'),
                        word_data.get('synonyms', '-'),
                        word_data.get('forms', '-')
                    )
                    st.success(f"'{word_data.get('word')}' listene eklendi!")
                    db.add_xp(st.session_state['username'], 10)
                    celebrate_xp(10)

        # Hepsini ekle butonu
        st.divider()
        if st.button("Tum Kelimeleri Listeme Ekle", use_container_width=True):
            for word_data in st.session_state['random_words']:
                db.add_word(
                    st.session_state['username'],
                    word_data.get('word', '-'),
                    word_data.get('meaning', '-'),
                    word_data.get('example', '-'),
                    word_data.get('synonyms', '-'),
                    word_data.get('forms', '-')
                )
            count = len(st.session_state['random_words'])
            st.success(f"{count} kelime listene eklendi!")
            db.add_xp(st.session_state['username'], count * 10)
            celebrate_xp(count * 10)
            st.session_state['random_words'] = []
            time.sleep(1)
            st.rerun()

# ==================== TAB 7: SINAV ====================
with tabs[6]:
    st.header("Kelime Sinavi")
    st.caption("Kaydettigin kelimelerden sinav ol (oncelikli kelimeler daha cok sorulur)")

    if user_words:
        quiz_count = st.slider("Kac soru?", 3, min(15, len(user_words)), min(5, len(user_words)), key="quiz_count")

        if st.button("Sinava Basla", use_container_width=True, type="primary"):
            with st.spinner("Sinav hazirlaniyor..."):
                q_words = db.get_smart_quiz_words(st.session_state['username'], quiz_count)
                if q_words:
                    quiz = tutor.generate_quiz(q_words)
                    if quiz:
                        st.session_state['quiz'] = quiz
                        st.session_state['quiz_answers'] = {}
                        st.session_state['quiz_submitted'] = False
                    else:
                        st.error("Sinav olusturulamadi. Tekrar dene.")
                else:
                    st.warning("Yeterli kelime yok.")

        if 'quiz' in st.session_state and st.session_state['quiz']:
            st.divider()

            if not st.session_state.get('quiz_submitted', False):
                for i, q in enumerate(st.session_state['quiz']):
                    st.write(f"**{i + 1}. {q.get('question', 'Soru yok')}**")
                    answer = st.radio(
                        "Secenek sec:",
                        q.get('options', []),
                        key=f"quiz_q_{i}",
                        index=None
                    )
                    st.session_state['quiz_answers'][i] = answer
                    st.divider()

                if st.button("Sinavi Bitir", use_container_width=True, type="primary"):
                    st.session_state['quiz_submitted'] = True
                    st.rerun()
            else:
                # Sonuçları göster
                correct = 0
                total = len(st.session_state['quiz'])

                for i, q in enumerate(st.session_state['quiz']):
                    user_answer = st.session_state['quiz_answers'].get(i)
                    correct_answer = q.get('answer')
                    is_correct = user_answer == correct_answer

                    if is_correct:
                        correct += 1
                        st.success(f"{i + 1}. {q.get('question')} - Dogru!")
                    else:
                        st.error(f"{i + 1}. {q.get('question')}")
                        st.write(f"   Senin cevabin: {user_answer}")
                        st.write(f"   Dogru cevap: {correct_answer}")

                # Sonuç
                score = int((correct / total) * 100)
                st.divider()
                st.subheader(f"Sonuc: {correct}/{total} ({score}%)")

                xp_earned = correct * 10 + (50 if score == 100 else 0)
                st.write(f"Kazanilan XP: +{xp_earned}")
                db.add_xp(st.session_state['username'], xp_earned)

                if st.button("Yeni Sinav"):
                    del st.session_state['quiz']
                    del st.session_state['quiz_answers']
                    del st.session_state['quiz_submitted']
                    st.rerun()
    else:
        st.info("Sinav icin once kelime ekle.")

# ==================== TAB 8: LİDERLİK ====================
with tabs[7]:
    st.header("Liderlik Tablosu")
    st.caption("En yuksek XP'ye sahip kullanicilar (Top 50)")

    # Yenile butonu
    if st.button("Tabloyu Yenile"):
        st.rerun()

    leaderboard = db.get_leaderboard(50)

    if leaderboard:
        # Mevcut kullanıcının sırası
        current_user_rank = None
        for idx, user in enumerate(leaderboard):
            if str(user.get('username')) == st.session_state['username']:
                current_user_rank = idx + 1
                break

        if current_user_rank:
            st.info(f"Senin siran: #{current_user_rank}")

        st.divider()

        # Liderlik tablosu
        for idx, user in enumerate(leaderboard):
            rank = idx + 1
            name = user.get('name', 'Anonim')
            xp = int(user.get('xp') or 0)
            level = int(xp / 100) + 1
            is_current = str(user.get('username')) == st.session_state['username']

            # Sıralama ikonları
            if rank == 1:
                rank_icon = "🥇"
            elif rank == 2:
                rank_icon = "🥈"
            elif rank == 3:
                rank_icon = "🥉"
            else:
                rank_icon = f"#{rank}"

            # Gösterim
            bg_color = "#fff3e0" if is_current else "#f8f9fa"
            st.markdown(f"""
            <div class="leaderboard-item" style="background: linear-gradient(90deg, {bg_color} 0%, #ffffff 100%);">
                <span class="leaderboard-rank">{rank_icon}</span>
                <span class="leaderboard-name">{'👤 ' if is_current else ''}{name}</span>
                <span class="leaderboard-xp">Seviye {level} • {xp} XP</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henuz liderlik tablosunda kimse yok.")
