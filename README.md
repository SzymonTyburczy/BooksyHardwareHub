# BooksyHardwareHub

## 🛠 Tech Stack

- **Backend:** Python (FastAPI)
- **Database:** SQLite (built-in, file-based)
- **Frontend:** Vue.js

## Setup Instructions

### 1. Backend setup

From project root:

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

Seed the database:

```powershell
venv\Scripts\python.exe backend/seed_db.py
```

### 2. Frontend setup (Vue + Vite)

The frontend lives in `frontend/`.

Install Node.js (LTS) first, then run:

```powershell
cd frontend
npm install
npm run dev
```

### 3. Optional API configuration

Frontend tries the following endpoints automatically:

- `/api/hardware`
- `/hardware`

You can override API host by creating `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```
