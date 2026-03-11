from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from database import connect_db, close_db, get_db
from routes import auth, crimes, notes

app = FastAPI(title="CrimeEye API", version="1.0.0")

# CORS – allow Vite dev server during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


# Register API routes
app.include_router(auth.router)
app.include_router(crimes.router)
app.include_router(notes.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "CrimeEye"}


# ─── Serve Vue SPA ────────────────────────────────────────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.isdir(STATIC_DIR):
    # Mount assets folder so hashed JS/CSS bundles are served correctly
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Let API routes take priority; this only fires for non-/api paths
        index = os.path.join(STATIC_DIR, "index.html")
        return FileResponse(index)
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "message": "CrimeEye API is running. Build the Vue frontend and place it in backend/static/.",
            "docs": "/docs",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
