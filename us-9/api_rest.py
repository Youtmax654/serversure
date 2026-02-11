"""
FastAPI Application for IoT Surveillance Project
Monitors Server Room (Temperature, Humidity, Luminosity) and detects intrusions
Provides REST API to query measurements and alerts from SQLite database
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


# ==================== Pydantic Models ====================

class MeasurementResponse(BaseModel):
    """Response model for a single measurement"""
    timestamp: str
    temperature: float
    humidity: float
    luminosity: int

    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2026-02-11 15:30:45",
                "temperature": 22.5,
                "humidity": 65.0,
                "luminosity": 450
            }
        }


class MeasurementHistoryResponse(BaseModel):
    """Response model for measurement history"""
    count: int
    measurements: List[MeasurementResponse]

    class Config:
        schema_extra = {
            "example": {
                "count": 3,
                "measurements": [
                    {
                        "timestamp": "2026-02-11 15:30:45",
                        "temperature": 22.5,
                        "humidity": 65.0,
                        "luminosity": 450
                    }
                ]
            }
        }


class AlertResponse(BaseModel):
    """Response model for an alert"""
    timestamp: str
    alert_type: str
    value: str

    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2026-02-11 14:22:10",
                "alert_type": "motion_detected",
                "value": "intrusion_detected"
            }
        }


class AlertHistoryResponse(BaseModel):
    """Response model for alert history"""
    count: int
    alerts: List[AlertResponse]

    class Config:
        schema_extra = {
            "example": {
                "count": 2,
                "alerts": [
                    {
                        "timestamp": "2026-02-11 14:22:10",
                        "alert_type": "motion_detected",
                        "value": "intrusion_detected"
                    }
                ]
            }
        }


# ==================== FastAPI Application ====================

app = FastAPI(
    title="IoT Surveillance API",
    description="REST API for monitoring server room conditions and intrusion detection",
    version="1.0.0",
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving photos
PHOTOS_DIR = Path("/home/admin/surveillance_photos")
if PHOTOS_DIR.exists():
    app.mount("/photos", StaticFiles(directory=str(PHOTOS_DIR)), name="photos")
else:
    print(f"Warning: Photos directory not found at {PHOTOS_DIR}")

# Database path
DB_PATH = "../surveillance.db"


# ==================== Database Utilities ====================

def get_db_connection():
    """Create a database connection with dict-like row access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row: sqlite3.Row) -> dict:
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(row)


# ==================== API Endpoints ====================

@app.get(
    "/api/sensors/last",
    response_model=MeasurementResponse,
    summary="Get Latest Sensor Measurement",
    description="Returns the most recent temperature, humidity, and luminosity measurement from the database."
)
def get_latest_measurement():
    """
    Fetch the latest sensor measurement from the measurements table.
    
    Returns:
        MeasurementResponse: The most recent measurement or 404 if no data exists
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT timestamp, temperature, humidity, luminosity FROM measurements ORDER BY timestamp DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            raise HTTPException(
                status_code=404,
                detail="No measurements found in database"
            )
        
        measurement = dict_from_row(row)
        return MeasurementResponse(**measurement)
    
    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


@app.get(
    "/api/sensors/history",
    response_model=MeasurementHistoryResponse,
    summary="Get Sensor Measurement History",
    description="Returns the last N sensor measurements from the measurements table."
)
def get_measurement_history(
    limit: int = Query(20, ge=1, le=1000, description="Number of recent measurements to retrieve (1-1000)")
):
    """
    Fetch sensor measurement history from the measurements table.
    
    Args:
        limit: Number of recent measurements to return (default: 20, max: 1000)
    
    Returns:
        MeasurementHistoryResponse: List of measurements and count
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT timestamp, temperature, humidity, luminosity FROM measurements ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return MeasurementHistoryResponse(count=0, measurements=[])
        
        measurements = [
            MeasurementResponse(**dict_from_row(row))
            for row in rows
        ]
        
        return MeasurementHistoryResponse(count=len(measurements), measurements=measurements)
    
    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


@app.get(
    "/api/alerts",
    response_model=AlertHistoryResponse,
    summary="Get System Alerts",
    description="Returns the last N system alerts (motion detection, intrusions, etc.)"
)
def get_alerts(
    limit: int = Query(10, ge=1, le=1000, description="Number of recent alerts to retrieve (1-1000)")
):
    """
    Fetch system alerts from the alerts table.
    
    Args:
        limit: Number of recent alerts to return (default: 10, max: 1000)
    
    Returns:
        AlertHistoryResponse: List of alerts and count
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT timestamp, alert_status, value FROM alerts ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return AlertHistoryResponse(count=0, alerts=[])
        
        alerts = [
            AlertResponse(**dict_from_row(row))
            for row in rows
        ]
        
        return AlertHistoryResponse(count=len(alerts), alerts=alerts)
    
    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


@app.get(
    "/health",
    summary="Health Check",
    description="Returns health status of the API and database connectivity."
)
def health_check():
    """
    Health check endpoint to verify API and database are operational.
    
    Returns:
        dict: Status information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )


@app.get(
    "/",
    summary="API Info",
    description="Returns basic information about the IoT Surveillance API."
)
def root():
    """
    Root endpoint providing basic API information.
    
    Returns:
        dict: API information and available endpoints
    """
    return {
        "name": "IoT Surveillance API",
        "version": "1.0.0",
        "description": "REST API for monitoring server room conditions and intrusion detection",
        "documentation": "/docs",
        "endpoints": {
            "latest_measurement": "/api/sensors/last",
            "measurement_history": "/api/sensors/history",
            "alerts": "/api/alerts",
            "photos": "/photos/{filename}",
            "health": "/health"
        }
    }


# ==================== Main ====================

if __name__ == "__main__":
    # Run the server programmatically
    uvicorn.run(
        app,
        host="localhost",          # Accessible on the local network
        port=8000,               # Default FastAPI port
        reload=False,            # Set to True for development with auto-reload
        log_level="info"         # Log level (debug, info, warning, error, critical)
    )
