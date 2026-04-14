# 🖥️ Booksy Hardware Hub

An internal tool for Booksy employees to manage, rent, and maintain company equipment.  
Built with **FastAPI** (Python) + **Vue 3** (TypeScript) + **SQLite** + **Gemini AI**.

> **Live demo:** [https://booksy-hardware-hub.vercel.app](https://booksy-hardware-hub.vercel.app)  
> **Backend API:** [https://booksyhardwarehub-production.up.railway.app](https://booksyhardwarehub-production.up.railway.app)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (LTS)

### 1. Backend

```bash
# Create virtual environment
python -m venv venv

# Install dependencies (Windows)
venv\Scripts\python.exe -m pip install -r backend/requirements.txt

# (Linux/Mac)
# source venv/bin/activate && pip install -r backend/requirements.txt

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env → add your GEMINI_API_KEY (get one free at https://aistudio.google.com/apikey)

# Seed the database
venv\Scripts\python.exe backend/seed_db.py

# Start the server
cd backend
..\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`, backend on `http://localhost:8000`.

### 3. Default Accounts

| Username | Password      | Role  |
|----------|--------------|-------|
| `admin`  | `admin123`   | Admin |
| `j.doe`  | `password123`| User  |

### 4. Running Tests

```bash
cd backend
..\venv\Scripts\python.exe -m pytest tests/test_main.py -v
```

All **21 tests** should pass.

---

## ✅ Implementation Status

### ✅ Fully Implemented

| Feature                     | Details |
|-----------------------------|---------|
| **Admin Command Center**    | Add/delete hardware, toggle Repair status, create/delete user accounts |
| **Login System**            | JWT authentication with bcrypt password hashing |
| **Smart Dashboard**         | Hardware list with Name, Brand, Purchase Date, Status, Notes. Full sorting (4 columns) and filtering (status, brand, text search) |
| **Rent/Return Flow**        | Users can rent Available equipment and return In Use items |
| **Business Logic Guards**   | Cannot rent Repair / In Use / Unknown items. Cannot return non-rented items. Primary admin cannot be deleted |
| **Semantic Search (AI)**    | Gemini 2.0 Flash interprets natural language queries (e.g., "I need something for mobile testing" → returns phones/tablets) |
| **Inventory Auditor (AI)**  | Gemini analyzes full inventory for safety hazards, data anomalies, and operational issues |
| **AI Graceful Degradation** | Keyword-based search and rule-based audit as fallback when Gemini API is unavailable |
| **Test Suite**              | 21 critical tests: auth (4), rental guards (7), admin ops (7), AI endpoints (3) |
| **Seed Data Handling**      | Cleaned and documented all anomalies in the provided dataset |

### ⚡ Shortcuts & "Hacks"

| Shortcut | Why Acceptable | Production Refactor |
|----------|---------------|-------------------|
| **CORS `*` (all origins)** | Development/demo convenience — single-team internal tool | Restrict to specific frontend domain, add CSRF tokens |
| **SQLite file database** | Portable, zero-config, perfect for MVP review | PostgreSQL with connection pooling (Supabase/Neon) |
| **JWT without server-side blacklist** | Logout is client-side (remove token). 24h expiry limits exposure | Redis-backed token blacklist, refresh token rotation |
| **`@app.on_event("startup")`** | Works fine but deprecated in FastAPI 0.93+. Used for simplicity | Migrate to `lifespan` context manager |
| **No rate limiting** | Internal tool with limited users | Add `slowapi` rate limiter for auth and AI endpoints |

### ⚠️ Partial/Missing

| Feature | Status | Notes |
|---------|--------|-------|
| **Rental history view** | Backend schema ready (hardware_history table + triggers) | Frontend doesn't expose a dedicated history panel yet |
| **Email-based usernames** | Users have simple usernames, not emails | Would add email field + validation for production |
| **Password change** | Not implemented | Would add `/api/auth/change-password` endpoint |

### 🔮 Next Steps (24h Roadmap)

1. **Rental History Dashboard** — The `hardware_history` table already records all changes via triggers. Build a timeline UI showing who rented/returned each device and when.
2. **Role-Based Permissions** — Currently binary (admin/user). Add granular roles: IT Admin (full access), Manager (can approve rentals), Employee (can only rent).
3. **Deployment Hardening** — Move SQLite → PostgreSQL (Neon), add rate limiting, set strict CORS, implement refresh token rotation.

---

## 🤖 AI Development Log

### Tooling

| Tool | Usage |
|------|-------|
| **Gemini (Antigravity)** | Primary AI pair programmer — architecture design, API implementation, test generation, debugging |
| **Gemini 2.0 Flash API** | Integrated into the app for semantic search and inventory auditing |
| **VS Code** | IDE with Vue/Python extensions |

### Data Strategy

The provided seed dataset contained **intentional traps** to test data auditing skills. Here's how each was handled:

| Issue | Detection | Resolution |
|-------|-----------|------------|
| **Duplicate ID** (id:4 appears twice) | AI flagged during schema design | Assigned id:8 to the duplicate laptop. Added UNIQUE constraint on ID |
| **Brand typo** ("Appel" → "Apple") | AI caught during seed import | Corrected in seed.json. Documented as a data cleaning step |
| **Wrong date format** ("22-05-2023" DD-MM-YYYY) | AI identified format inconsistency | Normalized to ISO 8601: "2023-05-22" |
| **Future purchase date** (2027-10-10) | Rule-based audit flagged it | Kept as-is in DB — the AI Auditor warns about it at runtime |
| **Empty brand** (id:10) | Detected during schema validation | Set to "Unknown" — Auditor flags it for identification |
| **null purchaseDate** (id:10) | Database schema allows NULL | Handled gracefully in UI (shows "—") |
| **Safety notes** (battery swelling, liquid damage) | AI Auditor detects at runtime | Flagged as high/medium severity in audit results |

### Prompt Trail

The full development conversation is available in the repository's commit history. Key architectural decisions shaped by AI collaboration:

1. **"Analyze the recruitment task and tell me what's missing"** — AI produced a comprehensive gap analysis comparing codebase vs requirements, identifying 4 critical blockers
2. **"Write tests for the 3 most critical business rules"** — AI generated 21 tests covering auth, rental guards, admin ops. First attempt failed due to in-memory SQLite (each connection got a fresh DB) — fixed by using temp file
3. **"Connect frontend AI assistant to backend instead of mocks"** — AI refactored `AiAssistant.vue` to call `/api/ai/search` and `/api/ai/audit`, keeping mock fallback
4. **"Integrate Gemini for semantic search"** — AI created `ai_service.py` with lazy initialization, graceful degradation, and structured prompts

### The "Correction" ⚠️

**Problem:** When writing tests, AI initially used `os.environ["HARDWARE_HUB_DB_PATH"] = ":memory:"` for an in-memory SQLite database. This caused **all 21 tests to fail** with `sqlite3.OperationalError: no such table: users`.

**Root cause I identified:** SQLite's `:memory:` database creates a **separate database for each connection**. The test fixture called `initialize_database()` (which creates tables in connection #1), then tried to insert seed data (in connection #2) — which had an empty, table-less database.

**How I fixed it:** Replaced `:memory:` with a `tempfile.NamedTemporaryFile` that persists on disk during the test, ensuring all connections access the same database. Added teardown logic to delete the temp file after each test. This is a SQLite-specific gotcha that the AI missed because it assumed connection pooling behavior similar to PostgreSQL.

**Lesson:** AI tools are excellent at generating boilerplate and test structures, but understanding database connection semantics requires domain knowledge. Always verify AI-generated infrastructure code against the actual runtime behavior.

---

## 🏗️ Architecture

```
BooksyHardwareHub/
├── backend/
│   ├── main.py            # FastAPI app — auth, CRUD, rental, AI endpoints
│   ├── ai_service.py      # Gemini LLM integration (search + audit)
│   ├── sqlite_db.py       # Database schema & connection management
│   ├── seed_db.py         # Database seeding with data cleaning
│   ├── seed.json          # Cleaned initial dataset
│   ├── .env.example       # Environment template
│   ├── requirements.txt   # Python dependencies
│   └── tests/
│       ├── conftest.py    # Shared fixtures (temp DB, auth helpers)
│       └── test_main.py   # 21 critical tests
├── frontend/
│   ├── src/
│   │   ├── views/         # LoginView, DashboardView, AdminView
│   │   ├── components/    # HardwareTable, AiAssistant, modals
│   │   ├── composables/   # useApi (HTTP client), useMockData
│   │   ├── stores/        # Pinia stores (auth, hardware, users, toast)
│   │   └── types/         # TypeScript interfaces
│   └── ...
├── railway.json           # Railway deployment config
├── nixpacks.toml          # Build config for Railway
└── README.md              # This file
```

### API Endpoints

| Method   | Endpoint                  | Auth     | Description |
|----------|--------------------------|----------|-------------|
| `POST`   | `/api/auth/login`        | Public   | Login, returns JWT |
| `GET`    | `/api/auth/me`           | User     | Current user info |
| `GET`    | `/api/hardware`          | User     | List all hardware |
| `POST`   | `/api/hardware`          | Admin    | Add hardware |
| `DELETE` | `/api/hardware/:id`      | Admin    | Delete hardware |
| `PATCH`  | `/api/hardware/:id/status` | Admin  | Toggle status |
| `POST`   | `/api/hardware/:id/rent` | User     | Rent hardware |
| `POST`   | `/api/hardware/:id/return`| User    | Return hardware |
| `GET`    | `/api/users`             | Admin    | List users |
| `POST`   | `/api/users`             | Admin    | Create user |
| `DELETE` | `/api/users/:id`         | Admin    | Delete user |
| `GET`    | `/api/ai/status`         | User     | Check Gemini availability |
| `POST`   | `/api/ai/search`         | User     | Semantic search |
| `GET`    | `/api/ai/audit`          | User     | Inventory audit |

---

## 🧪 Test Coverage

```
tests/test_main.py — 21 tests, 4 categories:

TestAuthentication (4)
  ✅ test_login_valid_credentials
  ✅ test_login_invalid_credentials
  ✅ test_login_nonexistent_user
  ✅ test_protected_endpoint_without_token

TestRentalGuards (7)
  ✅ test_cannot_rent_hardware_in_repair
  ✅ test_cannot_rent_hardware_already_in_use
  ✅ test_cannot_rent_hardware_with_unknown_status
  ✅ test_successful_rent_available_hardware
  ✅ test_cannot_return_available_hardware
  ✅ test_rent_then_return_flow
  ✅ test_cannot_rent_nonexistent_hardware

TestAdminOperations (7)
  ✅ test_regular_user_cannot_create_hardware
  ✅ test_regular_user_cannot_delete_hardware
  ✅ test_regular_user_cannot_create_users
  ✅ test_admin_can_create_hardware
  ✅ test_admin_can_toggle_repair_status
  ✅ test_admin_can_create_user
  ✅ test_cannot_delete_primary_admin

TestAIEndpoints (3)
  ✅ test_semantic_search_mobile
  ✅ test_semantic_search_empty_query
  ✅ test_audit_returns_flags
```

---

## 📦 Deployment

### Backend → Railway

1. Push to GitHub
2. Connect repo at [railway.app](https://railway.app)
3. Add a **Volume** mounted at `/data` (keeps SQLite data across redeploys)
4. Add environment variables:
   - `GEMINI_API_KEY` — from [aistudio.google.com](https://aistudio.google.com/apikey)
   - `JWT_SECRET` — any random secret string
   - `HARDWARE_HUB_DB_PATH` — `/data/hardware_hub.db`
5. Railway auto-detects `nixpacks.toml` and deploys

### Frontend → Vercel

1. Connect repo at [vercel.com](https://vercel.com)
2. Set root directory: `frontend`
3. Add env variables: `VITE_API_BASE_URL=<railway-url>`, `VITE_USE_MOCK=false`
4. Deploy — Vercel auto-detects Vite

---

## 📄 License

This project was built as a recruitment task for Booksy's Early Careers Programme.
