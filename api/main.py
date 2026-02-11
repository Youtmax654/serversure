import sqlite3
import os
import uvicorn
import glob
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# ==================== CONFIGURATION ====================

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# File Paths
DB_PATH = BASE_DIR / "surveillance.db"
STATIC_DIR = BASE_DIR / "static"

# Photo Directory Configuration
# Priority:
# 1. Environment Variable PHOTOS_DIR
# 2. Local "photos" directory (Dev)
# 3. Hardcoded RPi path (Production fallback)
ENV_PHOTOS_DIR = os.getenv("PHOTOS_DIR")
if ENV_PHOTOS_DIR:
    PHOTOS_DIR = Path(ENV_PHOTOS_DIR)
elif (BASE_DIR / "photos").exists():
    PHOTOS_DIR = BASE_DIR / "photos"
elif os.name == 'nt':
    PHOTOS_DIR = BASE_DIR / "photos_test"
else:
    # Default RPi path
    PHOTOS_DIR = Path("/home/traps/Scripts/dashboard/surveillance_photos")

# Ensure directory exists for stability, create if local dev
if not PHOTOS_DIR.exists() and "photos" in str(PHOTOS_DIR):
    try:
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"⚠️ Warning: Could not create photo directory {PHOTOS_DIR}: {e}")

# ==================== DATA MODELS ====================

class MeasurementResponse(BaseModel):
    timestamp: str
    temperature: float
    humidity: float
    luminosity: int

class MeasurementHistoryResponse(BaseModel):
    count: int
    measurements: List[MeasurementResponse]

class AlertResponse(BaseModel):
    timestamp: str
    alert_type: str
    value: float

class AlertHistoryResponse(BaseModel):
    count: int
    alerts: List[AlertResponse]

class PhotoInfo(BaseModel):
    filename: str
    url: str
    timestamp: str
    size_bytes: int

class PhotoListResponse(BaseModel):
    count: int
    photos: List[PhotoInfo]

# ==================== APP SETUP ====================

app = FastAPI(
    title="IoT Surveillance System",
    description="API for Server Room Monitoring & Intrusion Detection",
    version="1.1.0"
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Photos Directory
if PHOTOS_DIR.exists():
    app.mount("/photos", StaticFiles(directory=str(PHOTOS_DIR)), name="photos")
    print(f"✅ Serving photos from: {PHOTOS_DIR}")
else:
    print(f"⚠️ WARNING: Photos directory not found at: {PHOTOS_DIR}")

# ==================== DATABASE HELPERS ====================

def get_db_connection():
    """Establishes connection to SQLite database."""
    if not DB_PATH.exists():
        # Retrying creation or logging error
        print(f"❌ CRITICAL ERROR: Database file not found at {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def dict_from_row(row: sqlite3.Row) -> dict:
    """Helper to convert SQLite row to dictionary."""
    return dict(row) if row else None

# ==================== API ENDPOINTS ====================

@app.get("/api/sensors/last", response_model=MeasurementResponse, tags=["Sensors"])
def get_latest_measurement():
    """Returns the single most recent sensor reading."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, temperature, humidity, luminosity 
            FROM measurements 
            ORDER BY id DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": 0.0,
                "humidity": 0.0,
                "luminosity": 0
            }
        
        return dict_from_row(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@app.get("/api/sensors/history", response_model=MeasurementHistoryResponse, tags=["Sensors"])
def get_measurement_history(limit: int = Query(20, ge=1, le=1000)):
    """Returns the last N measurements."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, temperature, humidity, luminosity 
            FROM measurements 
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        data = [dict_from_row(row) for row in rows]
        return {"count": len(data), "measurements": data}
    except Exception as e:
        print(f"Error fetching history: {e}")
        return {"count": 0, "measurements": []}

@app.get("/api/alerts", response_model=AlertHistoryResponse, tags=["Alerts"])
def get_alerts(limit: int = Query(10, ge=1, le=1000)):
    """Returns the last N security alerts."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, alert_type, value 
            FROM alerts 
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        data = [dict_from_row(row) for row in rows]
        return {"count": len(data), "alerts": data}
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return {"count": 0, "alerts": []}

@app.get("/api/photos", response_model=PhotoListResponse, tags=["Photos"])
def list_photos(limit: int = Query(20, ge=1, le=100)):
    """Returns available surveillance photos sorted by date (newest first)."""
    if not PHOTOS_DIR.exists():
        return {"count": 0, "photos": []}
    
    try:
        # Supported image extensions
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp']
        files = []
        for ext in extensions:
            # Case insensitive search would be better but glob is case sensitive on Linux
            # extending patterns for upper case extensions if needed
            files.extend(PHOTOS_DIR.glob(ext))
            files.extend(PHOTOS_DIR.glob(ext.upper()))
        
        # Get stats and sort
        photo_list = []
        for f in files:
            stat = f.stat()
            # Use modification time as proxy for photo time if not in filename
            ts = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            photo_list.append({
                "filename": f.name,
                "url": f"/photos/{f.name}",
                "timestamp": ts,
                "size_bytes": stat.st_size,
                "_mtime": stat.st_mtime # for sorting
            })
        
        # Sort by mtime descending (newest first)
        photo_list.sort(key=lambda x: x["_mtime"], reverse=True)
        
        # Apply limit
        limited_list = photo_list[:limit]
        
        # Remove internal sorting key
        for p in limited_list:
            del p["_mtime"]
            
        return {"count": len(limited_list), "photos": limited_list}
        
    except Exception as e:
        print(f"Error listing photos: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing photos: {str(e)}")

@app.get("/api/status", tags=["System"])
def system_status():
    """Simple health check endpoint."""
    return {
        "status": "online", 
        "database": str(DB_PATH),
        "photos_dir": str(PHOTOS_DIR),
        "photos_mounted": PHOTOS_DIR.exists()
    }

# ==================== FRONTEND SERVING (REACT) ====================

# Only attempt to serve frontend if the 'static' folder exists
if STATIC_DIR.exists():
    
    # 1. Mount Assets (JS/CSS generated by Vite)
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # 2. Serve Index.html at Root (HIDDEN FROM DOCS)
    @app.get("/", include_in_schema=False)
    async def serve_root():
        return FileResponse(STATIC_DIR / "index.html")

    # 3. Catch-All Route (HIDDEN FROM DOCS)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Check if a physical file is requested (e.g., favicon.ico)
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Otherwise, return index.html and let React handle the routing
        return FileResponse(STATIC_DIR / "index.html")

else:
    print("⚠️ WARNING: 'static' folder not found. React Frontend will not be served.")
    print(f"   Expected path: {STATIC_DIR}")

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print(f"🚀 Starting Server on 0.0.0.0:8000")
    print(f"📂 Database: {DB_PATH}")
    print(f"📂 Frontend: {STATIC_DIR}")
    print(f"📂 Photos: {PHOTOS_DIR}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Accessible to entire network
        port=8000,
        log_level="info"
    )