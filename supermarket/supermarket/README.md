# 🛒 SuperMarket Management System — Barcode Edition

A Django web app to manage supermarket records with full **barcode support** — scan, generate, and print barcodes for all products.

---

## 🚀 Setup (Windows)

```bash
# 1. Navigate into the project folder
cd supermarket_project

# 2. Create & activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install all dependencies (Django + barcode + image libs)
pip install -r requirements.txt

# 4. Run database migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## 🔖 Barcode Features

| Feature | How it works |
|---|---|
| **Auto barcode generation** | A Code128 barcode image is created automatically when you add/save a product |
| **USB scanner support** | Plug in a USB barcode scanner → click the Barcode Number field → scan |
| **POS scanning** | Go to **POS / Scan Sale**, scan items to build a cart, then checkout |
| **Barcode lookup API** | `GET /barcode/lookup/?code=<barcode>` returns product JSON |
| **Print barcode labels** | Click the barcode icon on any product → print 1 or more labels |
| **Custom barcode numbers** | Enter any EAN-13 / Code128 number, or leave blank to use SKU |

---

## ✨ All Features

- 📦 Products with barcode generation
- 🏷️ Categories
- 🚚 Suppliers
- 🛒 POS — scan barcodes to process sales
- 🧾 Sales history with revenue tracking
- ⚠️ Low stock alerts on dashboard
- 🖨️ Print barcode labels (single or multiple copies)
- 🔐 Django Admin panel at `/admin/`

---

## 📦 Dependencies

```
Django>=4.2
python-barcode[images]   ← barcode generation
Pillow                   ← image processing
```

---

## 📝 Notes

- Barcode images are stored in `media/barcodes/`
- The POS page works with any USB HID barcode scanner (plug-and-play)
- Change `SECRET_KEY` and set `DEBUG=False` before production deployment
