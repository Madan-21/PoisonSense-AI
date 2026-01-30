# 🏥 PoisonSense AI

AI-powered poison identification and emergency response system for Nepal.

## ✨ Features

- 🧠 **AI-Powered Analysis**: DistilBERT-based symptom analysis for poison identification
- 🏥 **Hospital Finder**: Locate nearby hospitals with toxicology capabilities
- ☎️ **Poison Centers**: Find nearest poison control centers
- 💊 **Antidote Locator**: Find antidote availability
- 👨‍⚕️ **Doctor Verification**: Verified healthcare professionals
- 🔐 **Secure Auth**: JWT-based authentication with email OTP verification

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **npm** or **yarn**

### 1. Clone the Repository

```bash
git clone https://github.com/Madan-21/PoisonSense-AI.git
cd PoisonSense-AI
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend (database auto-initializes on first run!)
python -m uvicorn app.main:app --reload --port 8000
```

The database will **automatically create and seed** with sample data on first run!

### 3. Frontend Setup

```bash
# Open a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost:5173 |
| 🔧 Backend API | http://localhost:8000 |
| 📚 API Docs | http://localhost:8000/docs |

### Default Admin Login

```
Email: admin@poisonsense.ai
Password: admin123
```

## 📁 Project Structure

```
PoisonSense-AI/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Config, security
│   │   ├── db/             # Database setup & seeds
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── ml/             # ML models
│   └── requirements.txt
├── frontend/               # React + Vite Frontend
│   ├── src/
│   │   ├── api/           # API clients
│   │   ├── components/    # React components
│   │   ├── context/       # Auth context
│   │   └── pages/         # Page components
│   └── package.json
└── README.md
```

## 🔧 Environment Variables (Optional)

Create a `.env` file in the `backend/` folder:

```env
# Email Configuration (for OTP emails - optional)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your-api-key

# Security (change in production!)
SECRET_KEY=your-super-secret-key-min-32-characters
```

> **Note**: Without email configuration, OTPs are displayed directly in the UI (development mode).

## 🗄️ Database

- **Type**: SQLite (auto-created as `poisonsense.db`)
- **Auto-Seed**: Database automatically seeds with sample data on first run
- **Includes**: Poison centers, hospitals, poisons, admin user

To manually reset the database:
```bash
cd backend
rm poisonsense.db
python -m uvicorn app.main:app --reload --port 8000
```

## 📞 Emergency Numbers (Nepal)

| Service | Number |
|---------|--------|
| National Poison Helpline | 1102 |
| Ambulance | 102 |
| Police | 100 |
| Emergency | 112 |

## 👥 Team

- Built with ❤️ for emergency healthcare

## 📄 License

MIT License
