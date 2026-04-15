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
| **Semantic Search (AI)**    | Gemini 2.5 Flash interprets natural language queries (e.g., "I need something for mobile testing" → returns phones/tablets) |
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
| **401 auto-redirect** | Added after production testing revealed expired tokens left users on broken pages | Already implemented in `useApi.ts` — listed here as a post-MVP hardening step |

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

## 🎨 UI Design Decisions (vs. Wireframes)

The provided wireframes were used as a **functional reference**, not a visual template. Key deliberate deviations:

| Wireframe | This Implementation | Justification |
|-----------|--------------------|--------------| 
| Basic table layout, no color system | Dark-accented cards, status color badges | Internal tools are used 8h/day — color-coded status (green/red/blue) enables instant scanning without reading text |
| Single-column form for admin actions | Split Admin view: Hardware panel + Users panel | Admins manage both resources simultaneously — side-by-side reduces context switching |
| Generic action buttons always visible | Contextual buttons (Rent only when Available, Return only when In Use) | Hides impossible actions rather than disabling them — cleaner UX, prevents user confusion |
| No AI panel in wireframe | Collapsible AI Assistant panel in the dashboard | AI is a first-class feature of this spec — it needed dedicated, accessible UI, not buried in a menu |

---

## 🤖 AI Development Log

### Tooling

| Tool | Usage |
|------|-------|
| **Gemini (Antigravity)** | Primary AI pair programmer — architecture design, API contract analysis, implementation, test generation, deployment debugging |
| **Gemini 2.5 Flash API** | Runtime AI layer integrated into the app — semantic search and inventory auditing |
| **VS Code** | IDE with Pylance, Vue Language Features, and ESLint extensions |

### How AI Was Used (vs. Where I Overrode It)

The goal was to use AI to move fast — not to blindly accept every suggestion. Here's the breakdown:

| Decision | AI suggestion | My override | Why |
|----------|--------------|-------------|-----|
| **Database choice** | PostgreSQL | Kept SQLite | Portability for reviewer — no DB server required to run locally |
| **Test isolation** | `:memory:` SQLite | `tempfile.NamedTemporaryFile` | `:memory:` fails with multi-connection SQLite — AI missed this |
| **JWT library** | `python-jose` | `PyJWT` | Simpler, actively maintained, no known CVEs at time of writing |
| **Gemini model** | `gemini-2.0-flash` | `gemini-2.5-flash` | Free tier quota exhausted during dev — diagnosed from 429 error logs |
| **Keyword fallback** | ~8 term mappings | 40+ mappings | Initial coverage too narrow — "communicate", "small", "compact" returned empty results |
| **Business logic guards** | Frontend-only validation | Enforced in backend too | Frontend guards are UX — backend guards are security. Both required |
| **CORS policy** | `*` wildcard | Specific domains + Vercel regex | Wildcard is insecure even for internal tools |

### Prompt Trail

Key prompts that shaped the architecture (paraphrased from the actual Antigravity/Gemini session):

**Phase 1 — Database Schema (Manual, before AI)**

I wrote `sqlite_db.py` myself first — defining the relational schema, foreign key constraints, status enums, triggers, and connection management before any AI was involved. This gave me full control over the data model as the foundation.

---

**Phase 2 — Frontend Analysis & API Contract Mapping**
> *"Analyze this Vue 3 frontend codebase. Map every API call in useApi.ts, every store action, and every component. Tell me exactly what backend contract needs to exist to make this frontend work without changing a single line of frontend code."*

Outcome: AI produced a complete API contract map — 14 endpoints with exact paths, HTTP methods, request bodies, and expected response shapes. This became the implementation spec for the backend.

---

**Phase 3 — Backend Implementation**
> *"Build a FastAPI backend that exactly matches this API contract. Use the existing sqlite_db.py schema. Add bcrypt password hashing, JWT auth, rental business logic guards, and seed from this JSON."*

Outcome: Full `main.py` in one session (~350 lines). I reviewed every endpoint against `useApi.ts` manually and found 2 field name mismatches — corrected before moving on.

**Key decision made during this phase:** Business logic guards (cannot rent Repair/In Use/Unknown) were placed **in the backend**, not just the frontend. AI initially suggested frontend-only checks — I pushed back and required server-side enforcement so API consumers cannot bypass them with direct HTTP calls.

---

**Phase 4 — Test Generation**
> *"Write at least 21 pytest tests for the 3 most critical business rules: authentication, rental guards (cannot rent Repair/In Use/Unknown), and admin-only operations."*

Outcome: 21 tests generated. Initial implementation had a critical DB isolation bug — see **The Correction** below.

Follow-up prompt after the bug was discovered:
> *"All tests fail with 'no such table: users'. DB is initialized in conftest but tables don't exist when tests run. Why does this happen and how do I fix it?"*

AI correctly diagnosed the `:memory:` multi-connection issue and proposed the `tempfile` fix.

---

**Phase 5 — AI Integration**
> *"Integrate Gemini 2.5 Flash into the backend. Implement semantic_search() that interprets natural language hardware queries and returns matching hardware IDs as a JSON array. Implement inventory_audit() that analyzes the inventory and returns structured flags with severity levels. Add keyword-based and rule-based fallbacks for when the API is unavailable."*

Outcome: `ai_service.py` with lazy client initialization, structured prompts, JSON response parsing with markdown block stripping, and graceful degradation. The prompt engineering was iterative:

- **First attempt:** Gemini returned verbose text explanations instead of JSON → added `"Respond with ONLY a JSON array, no explanation"` to the prompt
- **Audit output:** Initially returned inconsistent severity strings → added explicit enum constraint: `"severity": "high" | "medium" | "low"`
- **Few-shot examples:** Added inline examples in the system prompt to anchor output format consistently

---

**Phase 6 — Deployment Fixes**
> *"Frontend on Vercel gets 'failed to fetch' for all API calls. Backend on Railway returns 502. Debug both issues step by step."*

Outcome: Identified 3 separate root causes through systematic elimination:
1. **Wrong env var** — `VITE_API_URL` vs `VITE_API_BASE_URL` in Vercel dashboard
2. **CORS rejection** — Backend had hardcoded wrong Vercel subdomain from an earlier test deploy → fixed with `*.vercel.app` regex allow-list
3. **Railway silent crash** — Start command was `uvicorn main:app` without `cd backend` first → import error → 502 → fixed in `nixpacks.toml`

---

**Phase 7 — Production Hardening (Post-Deploy)**
> *"Run a full end-to-end test against the live Railway API. Verify every endpoint returns the expected HTTP status codes. Find anything that doesn't match."*

Outcome: Discovered inventory audit 500 bug (Correction #2 below) and identified Gemini quota exhaustion on `gemini-2.0-flash`. Expanded keyword fallback coverage after testing edge-case natural language queries.





### Iterative AI Dialogue (selected micro-iterations)

Beyond the strategic phases above, the project involved dozens of smaller prompt-response-correction cycles. Five representative examples, each traceable to specific code in the repository:

---

**Micro-iteration A — Database schema: normalized history table**

Initial instinct was to store status change notes as a plain `TEXT` field on the `hardware` table. During schema design:

> *"I need to track who changed hardware status and when, for audit purposes. Is a text log field sufficient or should I normalize this?"*

AI recommended a dedicated `hardware_history` table with foreign keys to both `hardware` and `users`. Result in `sqlite_db.py` lines 38-48:

```sql
CREATE TABLE hardware_history (
  hardware_id INTEGER NOT NULL,
  old_status TEXT, new_status TEXT,
  changed_by INTEGER,
  changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (hardware_id) REFERENCES hardware(id) ON DELETE CASCADE,
  FOREIGN KEY (changed_by) REFERENCES users(id)
);
```

Added indexes on `hardware_id` and `changed_by` (lines 66-67). This is the foundation for a future rental history dashboard — data is already being captured.

---

**Micro-iteration B — Semantic search returning prose instead of JSON**

First call to `semantic_search()` returned a paragraph of text instead of a usable array:

> *"The model ignores my JSON instruction and returns a long explanation. How do I force structured output?"*

Added explicit constraints to the prompt in `ai_service.py`:
- `"Respond with ONLY a JSON array of matching item IDs, e.g. [1, 4, 9]."`
- `"If nothing matches, respond with []."`
- `"Do NOT include any explanation, just the JSON array."`

Also added markdown stripping because Gemini occasionally wraps JSON in triple-backtick code blocks.

---

**Micro-iteration C — Keyword fallback too narrow for natural language**

During quota testing, query `"give me something small to communicate"` returned `[]`.

> *"Why does keyword fallback return nothing for 'communicate'? There are phones in the inventory."*

Root cause: `KEYWORD_MAP` only had direct hardware terms. Extended with semantic clusters in `ai_service.py`:

```python
"communicate": ["iphone", "galaxy", "samsung", "sony"],
"small":       ["iphone", "galaxy", "samsung"],
"call":        ["iphone", "galaxy", "samsung"],
```

Map grew from ~8 entries to 40+ covering communication, size, use-case, and brand synonyms.

---

**Micro-iteration D — HTTP 401 vs 403 semantics**

> *"When a logged-in regular user hits an admin-only endpoint, should I return 401 or 403?"*

AI clarified: **401** = "I don't know who you are" (no/invalid token). **403** = "I know who you are, you just don't have permission." Admin-only endpoints now return 403 for authenticated non-admins, 401 for missing/invalid tokens — enforced through the `get_admin_user` dependency in `main.py`.

---

**Micro-iteration E — UNIQUE index for active rentals at database level**

> *"How do I prevent the same hardware from being rented twice at the DB level, not just application level?"*

AI suggested a **partial UNIQUE index** — unique only for rows where `return_date IS NULL`. Result in `sqlite_db.py` lines 60-62:

```sql
CREATE UNIQUE INDEX idx_rentals_active
ON rentals(hardware_id) WHERE return_date IS NULL;
```

The database itself enforces "one active rental per device", independent of application logic. Belt-and-suspenders alongside the status guard in `main.py`.

---

### AI Model Selection & Quota Management

During development, the Gemini free-tier quota for `gemini-2.0-flash` was fully exhausted from repeated testing. Diagnosed from the error response:

```
429 RESOURCE_EXHAUSTED
Quota exceeded for: generate_content_free_tier_requests
limit: 0 — model: gemini-2.0-flash
Retry after: 40s
```

**Resolution steps:**
1. Called `client.models.list()` to enumerate all available models
2. Selected `gemini-2.5-flash` — stable release, separate quota bucket, confirmed in available model list
3. Verified with a live test query before pushing to production
4. Defined a single `GEMINI_MODEL` constant so future model switches require changing exactly one line

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

### The "Correction" ⚠️

**Correction #1 — Test Database Isolation Bug**

**Problem:** When writing tests, AI initially used `os.environ["HARDWARE_HUB_DB_PATH"] = ":memory:"` for an in-memory SQLite database. This caused **all 21 tests to fail** with `sqlite3.OperationalError: no such table: users`.

**Root cause I identified:** SQLite's `:memory:` database creates a **separate database for each connection**. The test fixture called `initialize_database()` (which creates tables in connection #1), then tried to insert seed data (in connection #2) — which had an empty, table-less database.

**How I fixed it:** Replaced `:memory:` with a `tempfile.NamedTemporaryFile` that persists on disk during the test, ensuring all connections access the same database. Added teardown logic to delete the temp file after each test. This is a SQLite-specific gotcha that the AI missed because it assumed connection pooling behavior similar to PostgreSQL.

**Lesson:** AI tools are excellent at generating boilerplate and test structures, but understanding database connection semantics requires domain knowledge. Always verify AI-generated infrastructure code against the actual runtime behavior.

---

**Correction #2 — Live Production Bug: Inventory Audit 500**

**Problem:** After deployment, the `/api/ai/audit` endpoint returned `500 Internal Server Error` on production, while all 21 unit tests were passing locally.

**Root cause I identified:** During an editing session on `ai_service.py`, the line `client = _get_gemini_client()` inside `inventory_audit()` was accidentally commented out. The function then reached `if not client:` and raised `NameError: name 'client' is not defined`. The unit test for audit (`test_audit_returns_flags`) passed locally because the test environment triggered the keyword fallback path before reaching the broken line.

**How I found it:** Ran a manual end-to-end test against the live Railway API after deployment — which exposed the 500 that unit tests didn't catch because they exercise a different code path.

**How I fixed it:** Uncommented the line, re-ran all 21 tests locally (still passing), pushed, Railway redeployed, confirmed 200 from production.

**Lesson:** Unit tests verify business logic, but integration tests against the live environment catch a different category of bugs — especially subtle code editing mistakes in functions that have multiple early-exit paths.

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
