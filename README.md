# Buzdolabı Şefi (Smart Fridge Chef)

Buzdolabınızdaki malzemelere göre yapay zeka destekli tarif öneren web uygulaması. Kullanıcı hesapları, beğeni/atlama takibi, tüketim kaydı ve haftalık tekrar analizi destekler.

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
# Frontend
npm install

# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ortam değişkenleri

**Backend** (`backend/.env`):

```env
GEMINI_API_KEY=your_gemini_api_key
SESSION_SECRET=rastgele-guvenli-bir-string   # Örn: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
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
uvicorn app.main:app --reload --port 3001
```

**Terminal 2 – Frontend:**
```bash
npm run dev
```

Tarayıcıda: http://localhost:3000

## Testler

```bash
# Backend testleri (pytest)
npm run test:backend
# veya: cd backend && source venv/bin/activate && python -m pytest tests/ -v

# Frontend testleri (vitest)
npm run test
```

## Proje Yapısı

```
smart-fridge-chef/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/          # Pydantic modelleri
│   │   ├── routes/          # API endpoint'leri (auth, recipes, feedback)
│   │   ├── services/        # İş mantığı (auth, DB, RAG, FAISS)
│   │   └── middleware/      # Oturum doğrulama
│   ├── data/                # recipes.json, FAISS indeks, SQLite DB
│   ├── scripts/             # build_faiss_index.py
│   └── tests/               # Pytest testleri
├── pages/                   # React sayfaları
├── store/                   # AuthContext, FridgeContext
├── utils/                   # API istemcisi, yardımcılar
└── tests/                   # Vitest testleri
```

## Canlıya Alma Öncesi Kontrol Listesi

- [ ] `SESSION_SECRET` güçlü ve benzersiz
- [ ] `GEMINI_API_KEY` ayarlı
- [ ] `NODE_ENV=production` (backend)
- [ ] CORS `allow_origins` canlı frontend URL'i içeriyor
- [ ] SMTP ayarları (magic link e-posta gönderimi için; `backend/.env.example` örneğe bakın)
- [ ] SQLite veritabanı yedekleme stratejisi

## API Dokümantasyonu

Backend çalışırken: http://localhost:3001/docs

## Lisans

MIT
