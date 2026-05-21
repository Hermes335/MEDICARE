# MEDIBoT - Backend Integration Progress
**Last updated: 2026-05-21**

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
- Logout button in Sidebar (shows user email) and MobileTopBar

### 2. Backend Server Setup (DONE)
- Express.js + TypeScript server
- Dependencies: express, better-sqlite3, jsonwebtoken, bcryptjs, cors, tsx, undici
- SQLite database (`mediguide.db`) with tables: users, history_entries, saved_meds
- JWT auth middleware (7-day token expiry)
- Vite proxy configured (`/api` → `localhost:3001`)

### 3. Auth Routes (DONE & TESTED)
- `POST /api/auth/register` — returns token + user
- `POST /api/auth/login` — returns token + user
- Password hashing with bcryptjs

### 4. Chat Placeholder Endpoint (DONE & TESTED)
- `POST /api/chat` — returns hardcoded MedicineCard responses
- String matching on symptom keywords (headache, fever, cough, stomach, allerg)
- 800ms simulated delay
- Ready to swap in real AI model when training completes

### 5. History & Saved Meds Routes (DONE & TESTED)
- `GET/POST/DELETE /api/history` — JWT-protected, per-user
- `GET/POST/DELETE /api/saved-meds` — JWT-protected, per-user

### 6. Frontend Integration (DONE)
- `src/lib/api.ts` — fetch wrapper with auth token, covers all 10 API endpoints
- `src/lib/auth.tsx` — AuthProvider + useAuth hook, localStorage persistence
- `src/app/components/LoginScreen.tsx` — login/register form with validation
- `App.tsx` — AuthProvider wraps app, LoginScreen shown if not authenticated
- `ChatScreen.tsx` — calls `POST /api/chat`, persists history via `api.history.add()`, persists saved meds via `api.savedMeds.add()`
- `PharmacyScreen.tsx` — fetches from `/api/pharmacy/nearby` with geolocation, real Leaflet map
- `HistoryScreen.tsx` — fetches from `/api/history` and `/api/saved-meds`
- Voice input (Mic icon) removed from ChatScreen

### 7. Pharmacy Endpoint (DONE & TESTED)
- `GET /api/pharmacy/nearby` — queries Nominatim OpenStreetMap API
- Uses `undici.fetch` + `child_process` fallback for network isolation issue
- Calculates distances with haversine formula, returns sorted results

### 8. Interactive Map (DONE)
- Real Leaflet map with OpenStreetMap tiles (no API key needed)
- User location marker + pharmacy markers with popups
- Auto-fits bounds to show all results
- Installed: `leaflet` (plain, no react-leaflet wrapper — avoids React 18/19 peer dep conflict)

### 9. End-to-End Testing (DONE)
- Full flow verified via curl: register → login → chat → history → saved-meds → pharmacy
- All endpoints return correct data

---

## How to Run

```bash
# Terminal 1 — API server
npm run server        # or: npx tsx server/index.ts

# Terminal 2 — Vite dev server
npm run dev           # http://localhost:5173
```

Server runs on `http://localhost:3001`, Vite proxies `/api` requests to it.

**Note:** After modifying server code, fully restart the server to clear tsx cache.

---

## File Structure
```
server/
  index.ts              # Express entry point
  db.ts                 # SQLite setup + schema
  standalone-pharmacy.cjs  # Child_process fallback for pharmacy fetch
  routes/
    auth.ts             # Register + login
    chat.ts             # Placeholder AI chat
    pharmacy.ts         # Nominatim pharmacy lookup
    history.ts          # History CRUD (protected)
    saved-meds.ts       # Saved meds CRUD (protected)
  middleware/
    auth.ts             # JWT verification

src/lib/
  api.ts                # Frontend fetch wrapper (all endpoints)
  auth.tsx              # Auth context + hook

src/app/components/
  LoginScreen.tsx       # Login/register form
  NavBar.tsx            # Sidebar + BottomNav + MobileTopBar (with logout)
  ChatScreen.tsx        # Chat with placeholder AI + save/history persistence
  PharmacyScreen.tsx    # Real Leaflet map + Nominatim pharmacy data
  HistoryScreen.tsx     # History + saved meds from API
```

---

## Remaining / Nice-to-Have

1. **Swap in real AI model** — replace placeholder chat endpoint when model training completes
2. **Error handling polish** — better error messages in UI for network failures
3. **Stale token handling** — auto-logout when JWT expires (currently stays "logged in" with stale token)
4. **ChatScreen MOCK_RESPONSES cleanup** — remove dead code once real model is integrated
