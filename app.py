import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title("🛠️ Hata Tespit Ekranı")
st.write("Aşağıdaki maddelere bakarak sorunun nerede olduğunu anlayacağız.")

# --- KONTROL 1: YAPAY ZEKA (GEMINI) ---
st.header("1. Yapay Zeka (Gemini) Kontrolü")
if 'api_key' in st.secrets:
    key_ilk_5 = st.secrets['api_key'][:5]
    st.success(f"✅ 'api_key' Secrets içinde bulundu. (Başlangıç: {key_ilk_5}...)")
    
    # Test edelim
    try:
        genai.configure(api_key=st.secrets['api_key'])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Merhaba, çalışıyor musun?")
        st.success(f"✅ BAŞARILI! Yapay zeka cevap verdi: {response.text}")
    except Exception as e:
        st.error(f"❌ API Key var ama çalışmıyor! Hata Detayı: {e}")
        st.info("İPUCU: Google Cloud Console'dan 'Generative Language API' servisini ENABLE (Etkinleştir) yapmamış olabilirsin.")
else:
    st.error("❌ 'api_key' Secrets dosyasında BULUNAMADI. En tepeye eklediğinden emin misin?")

st.divider()

# --- KONTROL 2: VERİTABANI (GOOGLE SHEETS) ---
st.header("2. Veritabanı Kontrolü")
if 'gcp_service_account' in st.secrets:
    st.success("✅ '[gcp_service_account]' başlığı bulundu.")
    
    # Detaylı Anahtar Kontrolü
    keys = st.secrets['gcp_service_account']
    if 'private_key' in keys:
        st.success("✅ 'private_key' (Uzun şifre) bulundu.")
    else:
        st.error("❌ 'private_key' EKSİK!")

    if 'private_key_id' in keys:
        st.success("✅ 'private_key_id' (Kısa ID) bulundu.")
    else:
        st.error("❌ 'private_key_id' EKSİK!")

    # Bağlantı Testi
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key_dict = dict(st.secrets['gcp_service_account'])
        
        # Satır sonu düzeltmesi
        if 'private_key' in key_dict:
            key_dict['private_key'] = key_dict['private_key'].replace('\\n', '\n')
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open('MorningLingoDB')
        st.success("✅ BAŞARILI! Veritabanına bağlandım.")
    except Exception as e:
        st.error(f"❌ Bağlantı Hatası: {e}")
else:
    st.error("❌ '[gcp_service_account]' bölümü Secrets içinde yok.")
