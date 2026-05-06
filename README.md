# 🛒 Termiz Bozor Narxlari

Termiz shahridagi **5 ta yirik bozorda** sotiladigan oziq-ovqat va kundalik mahsulotlar narxlarini bir joyda solishtirish va eng arzon bozorni topish uchun zamonaviy web ilova.

## ✨ Asosiy imkoniyatlar

- 🏪 **5 ta bozor** — Termiz shahar Markaziy, Yashil Dunyo, Surxon Savdo Majmuasi, Eski Termiz va Universal bozorlari
- 🛒 **70+ mahsulot** — sabzavotlar, mevalar, go'sht, sut, don, ziravorlar va boshqalar
- 💰 **Aqlli savatcha** — bir nechta mahsulot tanlab, qaysi bozorda jami arzon ekanini bilish
- 📈 **Narxlar tarixi** — Chart.js bilan vizual grafiklar (oxirgi 30 kun)
- 📍 **Interaktiv xarita** — Leaflet + OpenStreetMap (bepul, API kerak emas)
- 🧮 **Tejash kalkulyatori** — har bir mahsulot uchun
- 📱 **Mobil-friendly** — telefon, planshet, kompyuterda mukammal
- 🎨 **Zamonaviy dizayn** — Tailwind CSS, Alpine.js
- 👥 **Foydalanuvchi paneli** — ro'yxatdan o'tish, login, profil
- ⚙️ **Admin panel** — narxlarni tezkor yangilash uchun

## 🚀 O'rnatish (Step-by-step)

### 1-qadam: Loyihani yuklab oling

```bash
# zip faylni ochib chiqaring
cd termiz_bozor
```

### 2-qadam: Virtual muhit yarating

```bash
python -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3-qadam: Kutubxonalarni o'rnating

```bash
pip install -r requirements.txt
```

### 4-qadam: Bazani yarating

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5-qadam: Boshlang'ich ma'lumotlarni yuklang

```bash
python manage.py seed_data --days 30
```

Bu buyruq quyidagilarni avtomatik yaratadi:
- 5 ta bozor (haqiqiy Termiz manzillari bilan)
- 8 ta kategoriya
- 75+ ta mahsulot
- 30 kunlik narx tarixi (har bir mahsulot uchun har bir bozorda)

### 6-qadam: Admin foydalanuvchini yarating

```bash
python manage.py createsuperuser
```

Username, email va parolni kiriting.

### 7-qadam: Saytni ishga tushiring

```bash
python manage.py runserver
```

Brauzeringizda oching: **http://127.0.0.1:8000**

Admin panel: **http://127.0.0.1:8000/admin/**

## 📁 Loyiha tuzilishi

```
termiz_bozor/
├── config/                  # Django sozlamalari
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/            # Foydalanuvchilar
│   ├── markets/             # Bozorlar
│   ├── products/            # Mahsulotlar va kategoriyalar
│   ├── prices/              # Narxlar va aqlli savatcha
│   └── core/                # Bosh sahifa, qidiruv API
├── templates/               # HTML shabnonlar
│   ├── base.html
│   ├── core/
│   ├── products/
│   ├── markets/
│   ├── prices/
│   ├── accounts/
│   └── partials/
├── static/                  # Statik fayllar
├── media/                   # Yuklangan rasmlar
├── manage.py
├── requirements.txt
└── README.md
```

## 🎨 Texnik stack

**Backend:**
- Python 3.11+
- Django 5.0
- Django REST Framework
- SQLite (production uchun PostgreSQL'ga osonlik bilan o'tish mumkin)

**Frontend:**
- Django Templates
- Tailwind CSS (CDN orqali, build kerak emas)
- Alpine.js (interaktivlik uchun)
- Chart.js (grafiklar)
- Leaflet + OpenStreetMap (xaritalar)

**Boshqa:**
- Pillow (rasmlar uchun)
- WhiteNoise (production statik fayllar)
- Hech qanday tashqi API ishlatilmaydi! ✅

## 📊 Asosiy sahifalar

| URL | Tavsif |
|-----|--------|
| `/` | Bosh sahifa — bozorlar, eng arzon mahsulotlar, mashhur mahsulotlar |
| `/mahsulotlar/` | Barcha mahsulotlar ro'yxati (filterlar bilan) |
| `/mahsulotlar/<slug>/` | **Mahsulot solishtirish** — 5 ta bozor, narx tarixi, kalkulyator |
| `/bozorlar/` | Barcha bozorlar |
| `/bozorlar/<slug>/` | Bozor sahifasi — barcha mahsulotlar narxi |
| `/bozorlar/xarita/` | Interaktiv xarita |
| `/narxlar/eng-arzon/` | **Aqlli savatcha** — eng arzon bozorni topish |
| `/narxlar/tarix/` | Narxlar tarixi grafigi |
| `/admin/` | Admin panel (narxlarni boshqarish) |

## ⚙️ Admin panel

Admin panel orqali siz quyidagilarni boshqarishingiz mumkin:

1. **Bozorlar** — qo'shish, tahrirlash, manzil, ish vaqti
2. **Kategoriyalar** — qo'shish, tartibni o'zgartirish
3. **Mahsulotlar** — qo'shish, rasm yuklash, mashhurlik belgisi
4. **Narxlar** — kunlik narxlarni tezkor kiritish
5. **Foydalanuvchilar** — rollar, sozlamalar

### Tezkor narx yangilash buyrug'i

Har kuni avtomatik narx yangilash uchun:

```bash
python manage.py update_prices_daily
```

Buni cron'ga qo'shish (Linux):
```bash
# har kuni soat 8:00 da
0 8 * * * cd /yo'l/termiz_bozor && python manage.py update_prices_daily
```

## 🔧 Sozlash

`.env` fayl yarating (`.env.example` asosida):

```env
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here
```

## 💡 Foydali buyruqlar

```bash
# Eski ma'lumotlarni o'chirib, yangidan yuklash
python manage.py seed_data --clear --days 30

# Faqat 7 kunlik narx tarixi
python manage.py seed_data --days 7

# Kunlik narx yangilash
python manage.py update_prices_daily

# Production uchun statik fayllarni yig'ish
python manage.py collectstatic
```

## 🌐 Production'ga deploy

1. `DEBUG=False` qiling `settings.py`'da
2. `ALLOWED_HOSTS`'ga domain qo'shing
3. PostgreSQL'ga o'ting (ixtiyoriy)
4. `python manage.py collectstatic` ishga tushiring
5. Gunicorn + Nginx bilan deploy qiling

## 🤝 Hissa qo'shish

Loyihani yaxshilash uchun pull request yuboring yoki issue oching.

## 📝 Litsenziya

MIT License — erkin foydalaning va o'zgartiring.

## 👨‍💻 Muallif

Termiz shahri uchun ❤️ bilan yaratilgan.

---

**Savollaringiz bormi?** Admin panelda ma'lumotlarni o'zgartirib, o'zingizga moslang!
"# termizbozor" 
