# 🚀 WAME Backend Setup Guide

## Prerequisites
- Python 3.8 or higher
- Git
- PowerShell (Windows) or Terminal (Mac/Linux)

## 📥 Step 1: Clone the Repository

```powershell
git clone https://github.com/SAIRAMSSSS/wame_backend.git
cd wame_backend
git checkout log-trnment-data
```

## 🐍 Step 2: Set Up Virtual Environment

```powershell
cd backend

# Create virtual environment
python -m venv .

# Activate virtual environment
# For PowerShell:
.\Scripts\Activate.ps1

# For CMD:
.\Scripts\activate.bat

# For Mac/Linux:
source Scripts/activate
```

You should see `(backend)` or similar in your terminal prompt.

## 📦 Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- Django 5.2.7
- Django REST Framework
- Django CORS Headers
- Google OAuth libraries
- Razorpay SDK
- And other dependencies

## 🔐 Step 4: Create Environment File

Create a file named `.env` in the `backend` folder with the following content:

```env
# Django Settings
SECRET_KEY=django-insecure-your-secret-key-here-change-this-in-production
DEBUG=True

# Google OAuth (Get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Razorpay Payment Gateway (Get from Razorpay Dashboard)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 🔑 How to Get API Keys:

**Google OAuth:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:3000`
   - `http://127.0.0.1:8000/api/auth/google/callback/`

**Razorpay:**
1. Sign up at [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Go to Settings → API Keys
3. Generate Test Mode keys

## 💾 Step 5: Set Up Database

The database file (`db.sqlite3`) is not included in the repository. You have two options:

### Option A: Create Fresh Database with Sample Data (Recommended)

```powershell
# Mark migrations as applied (tables will be created by populate script)
python manage.py migrate --fake

# Populate database with tournament data
python populate_data.py
```

This creates:
- ✅ 1 Tournament (Y-Ultimate Championship 2025)
- ✅ 4 Teams (Mumbai Thunderbolts, Delhi Dynamos, Bangalore Blaze, Pune Phoenix)
- ✅ 32 Players (8 per team)
- ✅ 6 Matches (3 completed with scores, 3 scheduled)
- ✅ Spirit Scores for completed matches
- ✅ 3 Fields
- ✅ Team captains and coach accounts

### Option B: Get Database from Team Member

If a team member has a database with real data:
1. Ask them to share the `db.sqlite3` file (via Slack, Drive, etc.)
2. Copy it to the `backend/` folder
3. Run: `python manage.py migrate --fake`

## 🧪 Step 6: Verify Setup

Check if everything is set up correctly:

```powershell
# Check database contents
python check_database.py

# Should show:
# - Users (coach, team captains)
# - Teams (4 teams)
# - Players (32 players)
# - Matches (6 matches)
# - Spirit Scores
```

## 🚀 Step 7: Run the Server

```powershell
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

Visit http://127.0.0.1:8000/admin/ to access the admin panel.

## 🔐 Default Login Credentials

After running `populate_data.py`, you can use:

**Coach Account:**
- Username: `coach_john_2024`
- Password: `12345`

**Team Captain Accounts:**
- Username: `captain1`, `captain2`, `captain3`, `captain4`
- Password: `password123`

**Admin Account (Create manually):**
```powershell
python manage.py createsuperuser
```

## 📱 Frontend Setup

The frontend is in a separate repository. After setting up the backend:

```powershell
# In a new terminal
cd ../..
git clone https://github.com/SAIRAMSSSS/wame_frontend.git
cd wame_frontend
git checkout tournament-safecopy-clean

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run at: http://localhost:3000/

## 🛠️ Useful Commands

### Database Management
```powershell
# Check database contents
python check_database.py

# Check specific tables
python check_tables.py

# Reset and repopulate data
rm db.sqlite3
python manage.py migrate --fake
python populate_data.py
```

### Server Management
```powershell
# Run server
python manage.py runserver

# Run on different port
python manage.py runserver 8080

# Stop server
Ctrl + C (or Ctrl + Break on Windows)
```

### Django Commands
```powershell
# Create superuser (admin)
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Make sure virtual environment is activated and dependencies installed:
```powershell
.\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Database is locked"
**Solution:** Stop any running Django servers and remove lock files:
```powershell
Stop-Process -Name python -Force
Remove-Item db.sqlite3-shm, db.sqlite3-wal -ErrorAction SilentlyContinue
```

### Issue: "Table already exists" during migration
**Solution:** Use `--fake` flag to mark migrations as applied:
```powershell
python manage.py migrate --fake
```

### Issue: "No such table: api_profile"
**Solution:** Run migrations and populate data:
```powershell
python manage.py migrate --fake
python populate_data.py
```

### Issue: Google OAuth not working
**Solution:** 
1. Check `.env` file has correct `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
2. Verify redirect URIs in Google Cloud Console
3. Make sure frontend URL matches in settings

## 📂 Project Structure

```
wame_backend/
├── backend/
│   ├── api/              # Main API app
│   │   ├── models.py     # Database models
│   │   ├── views.py      # API endpoints
│   │   ├── serializers.py # Data serializers
│   │   └── urls.py       # URL routing
│   ├── fitness_backend/  # Django settings
│   ├── manage.py         # Django management script
│   ├── requirements.txt  # Python dependencies
│   ├── populate_data.py  # Database population script
│   ├── check_database.py # Database checker
│   └── .env             # Environment variables (CREATE THIS)
└── SETUP.md             # This file
```

## 🎯 API Endpoints

Once the server is running, you can access:

- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Root:** http://127.0.0.1:8000/api/
- **Auth Endpoints:**
  - POST `/api/auth/register/` - Student registration
  - POST `/api/auth/login/` - Login
  - GET `/api/auth/google/` - Google OAuth
  - POST `/api/auth/logout/` - Logout
- **Tournament Endpoints:**
  - GET `/api/tournaments/` - List tournaments
  - GET `/api/tournaments/{id}/` - Tournament details
  - GET `/api/tournaments/{id}/leaderboard/` - Team standings
- **Profile Endpoints:**
  - GET `/api/profile/` - Current user profile
  - PUT `/api/profile/` - Update profile
- **Donate Endpoint:**
  - POST `/api/donate/` - Process donation

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Google OAuth Guide](https://developers.google.com/identity/protocols/oauth2)
- [Razorpay Integration](https://razorpay.com/docs/)

## 🤝 Getting Help

If you encounter issues:
1. Check this SETUP.md for troubleshooting
2. Review error messages in terminal
3. Check `check_database.py` output
4. Contact the team lead

## ✅ Checklist

- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with all keys
- [ ] Database set up (`python populate_data.py`)
- [ ] Server running (`python manage.py runserver`)
- [ ] Admin panel accessible
- [ ] Frontend repository cloned and running
- [ ] Can login with test accounts

---

**Happy Coding! 🎉**

For questions or issues, contact the team or check the project documentation.
