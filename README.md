# CrimeEye 👁

Community-driven crime reporting platform for Bangladesh, built with **Vue 3 + FastAPI + MongoDB Atlas**.

---

## Stack

| Layer    | Tech                            |
|----------|---------------------------------|
| Frontend | Vue 3, Vite, Pinia, Leaflet     |
| Backend  | FastAPI, uvicorn                |
| Database | MongoDB Atlas (Motor async driver) |
| Auth     | JWT (python-jose + passlib/bcrypt) |

---

## One-time Setup

### 1. MongoDB Atlas

1. Create a free cluster at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create a database user and get the connection string
3. Whitelist your IP address (Network Access)

### 2. Backend `.env`

```bash
cd backend
cp .env.example .env
# Edit .env and set your MONGODB_URL and a strong SECRET_KEY
```

### 3. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Development

### Run backend (auto-reload)

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Run frontend dev server (with proxy to backend)

```bash
cd frontend
npm run dev
```

Frontend: http://localhost:5173 (proxies `/api` → `http://localhost:8000`)

---

## Production Build

```bash
# Build Vue and place output in backend/static/
cd frontend
npm run build

# Start the unified server (serves API + Vue SPA)
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login → JWT token |
| GET | `/api/auth/me` | Current user |
| GET | `/api/crimes` | List crimes (filterable) |
| POST | `/api/crimes` | Submit crime report |
| GET | `/api/crimes/heatmap` | Heatmap data points |
| GET | `/api/crimes/{id}` | Single crime report |
| POST | `/api/crimes/{id}/vote` | Upvote / downvote |
| GET | `/api/crimes/{id}/notes` | Community notes |
| POST | `/api/crimes/{id}/notes` | Add community note |

---

## Features

- 🗺 **Map View** – Leaflet map with category-colored crime pins + heatmap mode
- 📋 **Feed View** – Paginated crime cards with category filters
- ➕ **Report Form** – Map-based location picker, anonymous posting
- 💬 **Community Notes** – Add context, vote on notes
- 👍 **Voting** – Upvote/downvote for credibility scoring
- 🔐 **Auth** – JWT-based register/login, optional anonymous posting
- 📊 **Trust Score** – Computed from votes + evidence + reporter reputation
