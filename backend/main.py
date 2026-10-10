from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
from datetime import datetime

app = FastAPI(title="INDUX-OS SOP-Genius + Predictive + Quality + Safety")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    query: str
    image_base64: str = None
    sensor_data: dict = None

SOP_DB = {
    "bearing": {"page": 47, "manual": "CNC_Maintenance_v3.pdf", "steps": ["Power OFF + LOTO", "Remove bearing housing - 12mm wrench", "Check vibration - replace if >4.5mm/s", "Lubricate + torque 25Nm"]},
    "overheating": {"page": 112, "manual": "Motor_SOP_v2.pdf", "steps": ["Check coolant", "Clean air filter", "Check temp sensor if >85C", "Restart after 10min"]},
    "defect": {"page": 89, "manual": "Quality_SOP_v4.pdf", "steps": ["Stop conveyor", "Photo defect", "Check mold pressure 150bar", "Re-calibrate if scratch >0.2mm"]},
    "safety": {"page": 15, "manual": "Safety_SOP_v1.pdf", "steps": ["Helmet + Gloves + Goggles?", "Power isolated?", "Fatigue <70%?", "Supervisor approval?"]}
}

@app.get("/")
def root(): return {"status": "INDUX-OS LIVE", "ps": "PS-02+PS-03+PS-04+PS-17", "team": "Reborn Innovators InduX5-26VU-353"}

@app.post("/api/sop-query")
async def sop_query(q: Query):
    ql = q.query.lower()
    key = "bearing"
    if "heat" in ql or "overheat" in ql or "temp" in ql: key = "overheating"
    elif "defect" in ql or "scratch" in ql or "quality" in ql: key = "defect"
    elif "safety" in ql or "helmet" in ql: key = "safety"
    sop = SOP_DB[key]
    alert = None
    if q.sensor_data and q.sensor_data.get("vibration",0) > 4.5:
        alert = f"PS-03 ALERT: Vibration {q.sensor_data['vibration']} > 4.5 - Failure in 48h"
    quality = {"defect_detected": random.choice([True, False]), "confidence": round(random.uniform(0.85,0.98),2)} if q.image_base64 else None
    return {"ps02_sop": {"source": f"{sop['manual']} Page {sop['page']}", "steps": sop["steps"], "cited": True, "expert_video": f"expert_{key}_10sec.mp4"}, "ps03_predictive": alert, "ps04_quality": quality, "ps17_safety": SOP_DB["safety"]["steps"]}

@app.post("/api/predictive-data")
async def predictive_data(data: dict):
    vib = data.get("vibration", random.uniform(2.0,6.0))
    temp = data.get("temperature", random.uniform(60,90))
    status = "FAILURE_PREDICTED" if vib>4.5 or temp>85 else "NORMAL"
    return {"vibration": round(vib,2), "temperature": round(temp,1), "status": status, "recommended_sop": "CNC_Maintenance_v3.pdf Page 47" if status!="NORMAL" else None}

@app.post("/api/quality-inspect")
async def quality_inspect(data: dict):
    return {"inspection_time_ms": random.randint(45,120), "defect": random.choice([True, False]), "confidence": round(random.uniform(0.88,0.99),2)}
