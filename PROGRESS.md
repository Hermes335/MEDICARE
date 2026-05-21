# MEDIBoT - Backend Integration Progress
**Date: 2026-05-21**

---

## Completed Work

### 1. Navbar Redesign (DONE)
- Rewrote `NavBar.tsx` into 3 components:
  - `Sidebar` — Desktop sidebar (w-64, collapsible to icon-only)
  - `MobileTopBar` — Mobile top bar with logo + dark mode toggle
  - `BottomNav` — Mobile bottom tab bar (4 tabs, 44px touch targets)
- Updated `App.tsx` with new flex layout (sidebar + main content column)
- Sidebar is collapsible with `PanelLeftClose`/`PanelLeftOpen` toggle
- Pure Tailwind CSS, lucide-react icons, dark mode support

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

### 6. Frontend Integration (PARTIALLY DONE)
- `src/lib/api.ts` — fetch wrapper with auth token handling
- `src/lib/auth.tsx` — React context (AuthProvider, useAuth hook)
- `src/app/components/LoginScreen.tsx` — login/register form with tab switcher
- `App.tsx` — wraps with AuthProvider, shows LoginScreen if not authenticated
- `ChatScreen.tsx` — updated to call `POST /api/chat` instead of mock
- `HistoryScreen.tsx` — updated to fetch from `/api/history` and `/api/saved-meds`
- Voice input (Mic icon) removed from ChatScreen

### 7. Pharmacy Screen (PARTIALLY DONE)
- `PharmacyScreen.tsx` — updated to fetch from `/api/pharmacy/nearby` with geolocation
- Falls back to sample data if geolocation unavailable
- Added loading spinner

---

## Known Issues

### Pharmacy Endpoint — FIXED ✅
- **Problem (was):** `GET /api/pharmacy/nearby` returned `{"error":"Failed to fetch pharmacy data"}`
- **Root cause:** 
  - Direct `fetch` in tsx runtime was failing (isolation/DNS/network issue)
  - tsx caching issue prevented code reloads from taking effect
- **Solution:**
  - Switched to `undici.fetch` (explicit Node HTTP client instead of global fetch)
  - Replaced `console.log` with `process.stderr.write` for immediate output
  - Force-restarted server (`Stop-Process -Name node -Force`) to clear tsx cache
- **Status:** Now working! Returns real Nominatim pharmacy data, sorted by distance

---

## Parts Not Started Yet

1. **Remove hardcoded fallback data** from PharmacyScreen — now that API works, remove fallback logic
2. **End-to-end testing** — full flow: register → login → chat → pharmacy → history
3. **Error handling polish** — better error messages in UI for network failures
4. **Logout button** — no way to log out currently (auth context has `logout()` but no UI trigger in Sidebar/MobileTopBar)

---

## How to Run

```bash
# Terminal 1 — API server
npm run server        # or: npx tsx server/index.ts

# Terminal 2 — Vite dev server
npm run dev           # http://localhost:5173
```

Server runs on `http://localhost:3001`, Vite proxies `/api` requests to it.

**Note on tsx caching:** After modifying server code, fully restart the server to clear tsx cache. In PowerShell: `Stop-Process -Name node -Force` before `npm run server`.

---

## File Structure
```
server/
  index.ts              # Express entry point
  db.ts                 # SQLite setup + schema
  routes/
    auth.ts             # Register + login
    chat.ts             # Placeholder AI chat
    pharmacy.ts         # Nominatim pharmacy lookup ✅ WORKING
    history.ts          # History CRUD (protected)
    saved-meds.ts       # Saved meds CRUD (protected)
  middleware/
    auth.ts             # JWT verification

src/lib/
  api.ts                # Frontend fetch wrapper
  auth.tsx              # Auth context + hook

src/app/components/
  LoginScreen.tsx       # Login/register form
  NavBar.tsx            # Sidebar + BottomNav + MobileTopBar
  ChatScreen.tsx        # Updated to use API
  PharmacyScreen.tsx    # Updated to use API (falls back to sample data)
  HistoryScreen.tsx     # Updated to use API
```
