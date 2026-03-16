# Buzdolabı Şefi 

Buzdolabınızdaki malzemelere göre yapay zeka destekli tarif öneren web uygulaması. Kullanıcı hesapları, beğeni/atlama takibi, tüketim kaydı ve haftalık tekrar analizi destekler. Türk yemeklerine ve Türkçe özelinde geliştirilmiştir. -Belen

## Özellikler

- **Tarif Önerisi:** Buzdolabı malzemelerine göre FAISS vektör araması ile tarif önerisi
- **RAG Pipeline:** FAISS → Reranker → Gemini LLM ile açıklamalı öneriler
- **Kullanıcı Hesapları:** E-posta ile magic link girişi (şifresiz)
- **Geri Bildirim:** Beğeni/atlama, tüketim saati, porsiyon, haftalık tekrar takibi
- **Tercihler:** Vegan, vejetaryen, glutensiz, süt ürünü yok, kuruyemiş alerjisi filtreleri
- **İkame Önerileri:** Eksik malzemeler için LLM tabanlı ikame önerileri

## Gereksinimler

- **Node.js** 18+
- **Python** 3.10+
- **Gemini API anahtarı** (LLM özellikleri için)

## Kurulum

### 1. Bağımlılıkları yükle

```bash
npm install

cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ortam değişkenleri

**Backend** (`backend/.env`):

```env
GEMINI_API_KEY=your_gemini_api_key
SESSION_SECRET=rastgele-guvenli-bir-string
```

**Magic Link E-posta (SMTP)** – Giriş bağlantısı e-posta ile gönderilsin istiyorsanız:

```env
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
FRONTEND_URL=http://localhost:3000
```

Gmail için "Uygulama şifresi" (App Password) kullanın; normal şifre çalışmaz.

**Frontend** (opsiyonel, `.env.local`):

```env
VITE_API_URL=http://localhost:3001/api
```

### 3. FAISS indeksini oluştur (ilk kurulumda)

```bash
cd backend
python scripts/build_faiss_index.py
```

## Çalıştırma

**Terminal 1 – Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 3001 --reload-exclude 'venv/*'
```
veya `npm run dev:backend`

**Terminal 2 – Frontend:**
```bash
npm run dev
```

Tarayıcıda: http://127.0.0.1:3000

> **Not:** `--reload-exclude 'venv/*'` venv klasöründeki değişikliklerin uvicorn'u sürekli yeniden başlatmasını önler.

## Testler

```bash
npm run test:backend

npm run test
```

## Proje Yapısı

```
smart-fridge-chef/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── middleware/
│   ├── data/
│   ├── scripts/
│   └── tests/
├── components/
├── pages/
├── store/
├── utils/
└── tests/
```

## Canlıya Almadan Önce Bunlara Bakın

- [ ] **Oturum güvenliği:** `SESSION_SECRET` için rastgele, güçlü bir değer kullanın (varsayılan değeri değiştirin)
- [ ] **AI özellikleri:** `GEMINI_API_KEY` tanımlı olsun; aksi halde tarif açıklamaları ve ikame önerileri çalışmaz
- [ ] **Production modu:** Backend'i `NODE_ENV=production` ile çalıştırın
- [ ] **CORS:** `FRONTEND_URL` veya `allow_origins` içinde canlı frontend adresiniz (örn. `https://uygulama.com`) tanımlı olsun
- [ ] **E-posta girişi:** Magic link göndermek istiyorsanız SMTP ayarlarını yapın (`backend/.env.example` referans alınabilir)
- [ ] **Veri güvenliği:** SQLite veritabanınızı düzenli yedekleyin

## API Dokümantasyonu

Backend çalışırken: http://localhost:3001/docs

## Lisans

MIT
