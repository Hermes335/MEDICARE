# MEDIBoT - Backend Integration Progress
**Date: 2026-05-21**

---

## Completed Work

### 1. Navbar Redesign (DONE)
- Rewrote `NavBar.tsx` into 3 components:
  - `Sidebar` — Desktop sidebar (w-64, collapsible to icon-only)
  - `MobileTopBar` — Mobile top bar with logo + dark mode + logout
  - `BottomNav` — Mobile bottom tab bar (4 tabs, 44px touch targets)
- Updated `App.tsx` with new flex layout (sidebar + main content column)
- Sidebar is collapsible with `PanelLeftClose`/`PanelLeftOpen` toggle
- Pure Tailwind CSS, lucide-react icons, dark mode support
- Logout button added to Sidebar (shows user email) and MobileTopBar

### 2. Backend Server Setup (DONE)
- Created `server/` directory with Express.js + TypeScript
- Installed dependencies: express, better-sqlite3, jsonwebtoken, bcryptjs, cors, tsx
- SQLite database (`mediguide.db`) with tables: users, history_entries, saved_meds
- JWT auth middleware
- Vite proxy configured (`/api` → `localhost:3001`)

### 3. Auth Routes (DONE & TESTED)
- `POST /api/auth/register` — works, returns token + user
- `POST /api/auth/login` — works, returns token + user
- Password hashing with bcryptjs, JWT tokens (7-day expiry)

### 4. Chat Placeholder Endpoint (DONE & TESTED)
- `POST /api/chat` — works, returns hardcoded MedicineCard responses
- String matching on symptom keywords (headache, fever, cough, stomach, allerg)
- 800ms simulated delay
- Same response structure as old mock, ready to swap in real AI model

### 5. History & Saved Meds Routes (DONE & TESTED)
- `GET/POST/DELETE /api/history` — protected, per-user
- `GET/POST/DELETE /api/saved-meds` — protected, per-user
- All CRUD operations work with SQLite

### 6. Frontend Integration (DONE)
- `src/lib/api.ts` — fetch wrapper with auth token handling
- `src/lib/auth.tsx` — React context (AuthProvider, useAuth hook)
- `src/app/components/LoginScreen.tsx` — login/register form with tab switcher
- `App.tsx` — wraps with AuthProvider, shows LoginScreen if not authenticated
- `ChatScreen.tsx` — updated to call `POST /api/chat` instead of mock
- `HistoryScreen.tsx` — updated to fetch from `/api/history` and `/api/saved-meds`
- Voice input (Mic icon) removed from ChatScreen
- Logout button added to Sidebar and MobileTopBar

### 7. Pharmacy Screen (DONE)
- `PharmacyScreen.tsx` — fetches from `/api/pharmacy/nearby` with geolocation
- Falls back to showing error message if geolocation unavailable
- Added loading spinner
- Removed hardcoded fallback data (API now works)

### 8. Pharmacy Endpoint (DONE)
- `GET /api/pharmacy/nearby` — uses `undici.fetch` + `child_process` fallback
- Queries Nominatim OpenStreetMap API for real pharmacy data
- Calculates distances with haversine formula
- Returns sorted results within radius

---

## How to Run

```bash
# Terminal 1 — API server
npm run server        # or: npx tsx server/index.ts

# Terminal 2 — Vite dev server
npm run dev           # http://localhost:5173
```

Server runs on `http://localhost:3001`, Vite proxies `/api` requests to it.

---

## File Structure
```
server/
  index.ts              # Express entry point
  db.ts                 # SQLite setup + schema
  routes/
    auth.ts             # Register + login
    chat.ts             # Placeholder AI chat
    pharmacy.ts         # Nominatim pharmacy lookup
    history.ts          # History CRUD (protected)
    saved-meds.ts       # Saved meds CRUD (protected)
  middleware/
    auth.ts             # JWT verification

src/lib/
  api.ts                # Frontend fetch wrapper
  auth.tsx              # Auth context + hook

src/app/components/
  LoginScreen.tsx       # Login/register form
  NavBar.tsx            # Sidebar + BottomNav + MobileTopBar (with logout)
  ChatScreen.tsx        # Uses /api/chat
  PharmacyScreen.tsx    # Uses /api/pharmacy/nearby
  HistoryScreen.tsx     # Uses /api/history and /api/saved-meds
```

---

## Remaining / Nice-to-Have

1. **End-to-end testing** — full flow: register → login → chat → pharmacy → history
2. **Error handling polish** — better error messages in UI for network failures
3. **Standalone pharmacy script** — `server/standalone-pharmacy.cjs` for child_process fallback
