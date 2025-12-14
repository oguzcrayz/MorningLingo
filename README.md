# ☕ MorningLingo - AI Powered English Tutor

MorningLingo, kullanıcının İngilizce seviyesine göre kişiselleştirilmiş içerikler sunan, yapay zeka destekli bir dil öğrenme asistanıdır. Google Gemini, Google Sheets ve Streamlit teknolojileri kullanılarak geliştirilmiştir.

🔗 **Canlı Demo:** [ https://morninglingo-tynczbqvgsd48yshgu9vxd.streamlit.app/ ]

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)

## 🚀 Özellikler

Bu uygulama, standart bir kelime defterinden çok daha fazlasını sunar:

### 🧠 Yapay Zeka Destekli Öğrenme
* **Akıllı Okuma Parçaları:** Seviyenize (A1-C1) ve istediğiniz kelime sayısına (50-800) göre anlık metin oluşturur.
* **Kelime Analizi:** Bir kelime girdiğinizde AI; Türkçe anlamını, İngilizce örneğini, eş anlamlısını ve **kelime türevlerini (isim, fiil, sıfat)** otomatik getirir.
* **Hikaye Modu:** Listendeki kelimelerle sana özel, komik ve kısa hikayeler yazar.

### 🔄 Aralıklı Tekrar Sistemi (SRS)
* **Akıllı Flashcardlar:** Kelimeleri "Zor", "Orta" ve "Normal" olarak sınıflandırır.
* **Algoritma:** Zorlandığınız kelimeleri daha sık, bildiklerinizi daha seyrek sorar.

### 🎙️ Konuşma ve Dinleme
* **Telaffuz Analizi:** Mikrofona konuşursunuz, AI telaffuzunuzu 10 üzerinden puanlar ve düzeltmeniz gereken sesleri söyler.
* **Seslendirme:** Okuma metinlerini ve kelime kartlarını sesli olarak dinleyebilirsiniz (Text-to-Speech).

### 📊 Veri ve İlerleme
* **Google Sheets Veritabanı:** Tüm kullanıcı verileri bulutta güvenle saklanır.
* **Excel Çıktısı:** Kelime listenizi tek tıkla Excel/CSV formatında indirebilirsiniz.
* **Oyunlaştırma:** Çalıştıkça XP kazanır ve seviye atlarsınız.
* **Mobil Uyumlu (PWA):** Telefonda uygulama gibi tam ekran çalışır.

## 🛠️ Kullanılan Teknolojiler

* **Frontend:** Streamlit (Python)
* **AI Model:** Google Gemini 1.5 Flash
* **Database:** Google Sheets API (gspread)
* **Audio:** gTTS (Google Text-to-Speech)
* **Deploy:** Streamlit Cloud

## 📸 Ekran Görüntüleri

*(Buraya uygulamanın çalışırken alınmış 1-2 ekran görüntüsünü ekleyebilirsin)*

## 📦 Kurulum (Local)

Projeyi kendi bilgisayarınızda çalıştırmak isterseniz:

1.  Repoyu klonlayın:
    ```bash
    git clone [https://github.com/KULLANICI_ADIN/MorningLingo.git](https://github.com/KULLANICI_ADIN/MorningLingo.git)
    ```
2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
3.  Google Cloud Console'dan bir Service Account oluşturun ve `secrets.json` dosyasını ana dizine ekleyin.
4.  Uygulamayı başlatın:
    ```bash
    streamlit run app.py
    ```

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir. Açık kaynaklıdır.
