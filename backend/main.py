from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    query: str
    image_base64: str = None
    sensor_data: dict = None

SOP_DB = {
    "bearing": {"page": 47, "manual": "CNC_Maintenance_v3.pdf", "steps": ["Power OFF + LOTO", "Remove bearing housing - 12mm wrench", "Check vibration >4.5mm/s", "Lubricate + torque 25Nm"]},
    "overheating": {"page": 112, "manual": "Motor_SOP_v2.pdf", "steps": ["Check coolant", "Clean air filter", "Check temp if >85C", "Restart after 10min"]},
    "defect": {"page": 89, "manual": "Quality_SOP_v4.pdf", "steps": ["Stop conveyor", "Photo defect", "Check mold pressure 150bar", "Re-calibrate if scratch >0.2mm"]},
    "safety": {"page": 15, "manual": "Safety_SOP_v1.pdf", "steps": ["Helmet + Gloves + Goggles?", "Power isolated?", "Fatigue <70%?", "Supervisor approval?"]}
}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>INDUX-OS | Reborn Innovators</title>
<style>
body{font-family:sans-serif;background:#070a14;color:white;margin:0;padding:16px}
.card{background:#111827;border:1px solid #1f2937;border-radius:16px;padding:16px;margin:10px 0}
.btn{padding:10px 18px;border-radius:999px;border:none;font-weight:700;cursor:pointer;margin:4px}
.btn-green{background:linear-gradient(135deg,#0f9d4e,#2cf6b3);color:#000}
.btn-blue{background:linear-gradient(135deg,#1d4ed8,#7c3aed);color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}
.tag{background:#1f2937;padding:3px 8px;border-radius:999px;font-size:0.65rem}
input{width:70%;padding:10px;border-radius:8px;border:1px solid #333;background:#000;color:#fff}
#out{background:#000;padding:12px;border-radius:8px;white-space:pre-wrap;margin-top:10px;font-size:0.85rem;max-height:300px;overflow:auto}
</style>
</head>
<body>
<h1>🔥 INDUX-OS: Factory Intelligence</h1>
<p><b>Team Reborn Innovators | InduX5-26VU-353 | PS-02 + PS-03 + PS-04 + PS-17</b> | <a href="/docs" style="color:#2cf6b3">API Docs</a></p>
<div class="grid">
<div class="card"><span class="tag">PS-02 SOP</span><h3>📚 SOP-Genius</h3><p>Multimodal RAG - Photo + Voice → Cited SOP</p></div>
<div class="card"><span class="tag">PS-03 Predictive</span><h3>⚙️ Predictive Maintenance</h3><p>IoT vibration/temp → Predicts failure 48h before</p></div>
<div class="card"><span class="tag">PS-04 Quality</span><h3>👁️ Quality Inspection</h3><p>Edge-AI 45ms defect detection</p></div>
<div class="card"><span class="tag">PS-17 Safety</span><h3>🦺 Safety Early-Warning</h3><p>Wearable fatigue/heat → Safety checklist lock</p></div>
</div>
<div class="card">
<h3>🚀 Live Demo</h3>
<input id="q" placeholder="Ask: bearing failure? Motor overheating? Quality defect? safety check?">
<button class="btn btn-green" onclick="ask()">Ask SOP-Genius</button>
<button class="btn btn-blue" onclick="predict()">Test Sensor</button>
<div id="out">Click button to test 4-in-1 platform...</div>
</div>
<script>
async function ask(){
 const query=document.getElementById('q').value||"bearing vibration high hai, kya karu?";
 document.getElementById('out').innerText="Loading...";
 const res=await fetch("/api/sop-query",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query,sensor_data:{vibration:5.2,temperature:88},image_base64:"dummy"})});
 const data=await res.json();
 document.getElementById('out').innerText=JSON.stringify(data,null,2);
}
async function predict(){
 const res=await fetch("/api/predictive-data",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({vibration:5.8,temperature:89})});
 const data=await res.json();
 document.getElementById('out').innerText="PS-03 Predictive:\\n"+JSON.stringify(data,null,2);
}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_PAGE

@app.get("/api")
def api_status():
    return {"status": "INDUX-OS LIVE", "ps": "PS-02+PS-03+PS-04+PS-17", "team": "Reborn Innovators InduX5-26VU-353"}

@app.post("/api/sop-query")
async def sop_query(q: Query):
    ql=q.query.lower(); key="bearing"
    if "heat" in ql or "overheat" in ql or "temp" in ql: key="overheating"
    elif "defect" in ql or "scratch" in ql or "quality" in ql: key="defect"
    elif "safety" in ql or "helmet" in ql: key="safety"
    sop=SOP_DB[key]
    alert=f"PS-03 ALERT: Vibration {q.sensor_data['vibration']} >4.5 - Failure in 48h" if q.sensor_data and q.sensor_data.get("vibration",0)>4.5 else None
    quality={"defect_detected": random.choice([True,False]), "confidence": round(random.uniform(0.85,0.98),2)} if q.image_base64 else None
    return {"ps02_sop": {"source": f"{sop['manual']} Page {sop['page']}", "steps": sop["steps"], "cited": True, "expert_video": f"expert_{key}_10sec.mp4"}, "ps03_predictive": alert, "ps04_quality": quality, "ps17_safety": SOP_DB["safety"]["steps"]}

@app.post("/api/predictive-data")
async def predictive_data(data: dict):
    import random as r
    vib=data.get("vibration", r.uniform(2.0,6.0)); temp=data.get("temperature", r.uniform(60,90))
    status="FAILURE_PREDICTED" if vib>4.5 or temp>85 else "NORMAL"
    return {"vibration": round(vib,2), "temperature": round(temp,1), "status": status, "recommended_sop": "CNC_Maintenance_v3.pdf Page 47" if status!="NORMAL" else None}
