from fastapi import FastAPI
from pydantic import BaseModel
import psycopg

app = FastAPI()

def get_connection():
    return psycopg.connect(
        "postgresql://neondb_owner:npg_3c7EqXelrUYC@ep-holy-salad-ah1ma8af-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require",
        connect_timeout=10
    )

class Settings(BaseModel):
    hospital_name: str
    registration_number: str
    gst_number: str
    address: str
    city: str
    state: str
    pincode: str
    phone: str
    email: str
    website: str
    established_year: int

@app.on_event("startup")
def startup():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            hospital_name VARCHAR(255),
            registration_number VARCHAR(100),
            gst_number VARCHAR(100),
            address TEXT,
            city VARCHAR(100),
            state VARCHAR(100),
            pincode VARCHAR(20),
            phone VARCHAR(20),
            email VARCHAR(100),
            website VARCHAR(100),
            established_year INT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.post("/settings")
def add_settings(data: Settings):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (
            hospital_name,
            registration_number,
            gst_number,
            address,
            city,
            state,
            pincode,
            phone,
            email,
            website,
            established_year
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data.hospital_name,
        data.registration_number,
        data.gst_number,
        data.address,
        data.city,
        data.state,
        data.pincode,
        data.phone,
        data.email,
        data.website,
        data.established_year
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Settings Added Successfully"}

@app.get("/settings")
def get_settings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows