# NavMap – Indoor Navigation System
## Stack: HTML + CSS + JS (separate files) + Python Flask + MongoDB

---

## 📁 Project Structure
```
navmap/
├── frontend/
│   ├── index.html              ← Landing page
│   ├── css/
│   │   └── main.css            ← Shared styles
│   ├── js/
│   │   └── utils.js            ← Shared JS (API calls, auth helpers)
│   └── pages/
│       ├── login.html          ← Admin login
│       ├── register.html       ← Admin register
│       ├── dashboard.html      ← Admin dashboard
│       ├── editor.html         ← Floor plan pin editor
│       └── nav.html            ← USER navigation page (QR scan target)
│
└── backend/
    ├── app.py                  ← Main Flask app (run this)
    ├── routes/
    │   ├── auth.py             ← Register / Login / JWT
    │   ├── floorplans.py       ← Upload floor plan images
    │   ├── markers.py          ← Add / edit / delete pins
    │   ├── qr.py               ← Real QR PNG generation
    │   ├── analytics.py        ← Real scan analytics
    │   └── navigate.py         ← Public navigation API
    ├── models/
    │   └── db.py               ← MongoDB connection
    ├── uploads/                ← Floor plan images stored here (auto-created)
    ├── requirements.txt
    └── .env.example
```

---

## 🚀 Setup & Run

### Step 1: Install dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### Step 2: Configure .env
```bash
copy .env.example .env
```
Edit `.env` with your MongoDB Atlas URI:
```
MONGO_URI=mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/navmap?retryWrites=true&w=majority
DB_NAME=navmap
JWT_SECRET=any_long_random_string_here
FRONTEND_URL=http://localhost:5000
```

### Step 3: Run
```bash
python app.py
```
Open: **http://localhost:5000**

---

## 🔄 How It Works

### Admin Flow
1. Go to http://localhost:5000 → Register your organization
2. Login → redirected to Dashboard → Floor Plans tab
3. Click **"Upload Floor Plan"** → upload image for each floor
4. Click **"Edit Pins"** → click on map image to place room pins
5. Go to **QR Codes** tab → click **"⬇ PNG"** to download each QR
6. Print QR codes → stick on walls/pillars in the building

### User Flow (No Login Required)
1. User sees QR sticker on a pillar
2. Scans QR with phone camera
3. Opens: `http://localhost:5000/nav?org=<org_id>&room=<marker_id>`
4. Page shows: **"I am at [scanned room]"** — pre-filled automatically
5. User selects destination from dropdown
6. Clicks **"Show Route →"**
7. Sees route line on map + step-by-step directions

---

## ⚠️ Important: MongoDB Password Fix
If your password has special characters (@, #, $, etc), encode it:
```python
from urllib.parse import quote_plus
print(quote_plus("your@password"))  # Use this encoded version in .env
```

---

## 🔑 No API Keys Needed
| Feature | Library | Cost |
|---------|---------|------|
| QR generation | qrcode (Python) | Free |
| Maps | Uploaded images + CSS | Free |
| Auth | PyJWT + bcrypt | Free |
| Database | MongoDB Atlas | Free (512MB) |
| Routing | Custom JS | Free |

---

## 📡 API Reference
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/auth/register | ❌ | Register org + admin |
| POST | /api/auth/login | ❌ | Login → get JWT token |
| GET | /api/floorplans/ | ✅ | List floor plans |
| POST | /api/floorplans/ | ✅ | Upload floor plan image |
| DELETE | /api/floorplans/\<id\> | ✅ | Delete floor plan |
| GET | /api/markers/floor/\<fp_id\> | ❌ | Markers for a floor |
| GET | /api/markers/org/\<org_id\> | ❌ | All markers for org |
| POST | /api/markers/ | ✅ | Add marker/pin |
| PUT | /api/markers/\<id\> | ✅ | Update marker |
| DELETE | /api/markers/\<id\> | ✅ | Delete marker |
| GET | /api/qr/marker/\<id\> | ✅ | QR as base64 JSON |
| GET | /api/qr/marker/\<id\>/download | ❌ | Download QR as PNG |
| GET | /api/qr/all | ✅ | All QRs for org |
| POST | /api/analytics/scan | ❌ | Log a QR scan (auto) |
| GET | /api/analytics/ | ✅ | Real analytics data |
| GET | /api/navigate/org/\<id\> | ❌ | All nav data for org |
| GET | /api/navigate/room/\<id\> | ❌ | Single room nav data |

---

## 🌐 Deploy to Render.com (Free)
1. Push to GitHub
2. Go to render.com → New Web Service
3. Set Start Command: `cd backend && python app.py`
4. Add environment variables from .env
5. Done — your app is live!
