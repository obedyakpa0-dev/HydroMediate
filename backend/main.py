"""
FastAPI Backend Application for HydroMediate - Community Borehole AI Mediator
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from mediator_engine import MediatorEngine
from ai import generate_mediator_turn_response, HAS_GEMINI

app = FastAPI(
    title="HydroMediate API",
    description="AI-Powered Community Borehole Dispute Mediator System",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: Dict[str, MediatorEngine] = {}

def get_engine(session_id: str = "default_session") -> MediatorEngine:
    if session_id not in sessions:
        sessions[session_id] = MediatorEngine(session_id)
    return sessions[session_id]

class StartRequest(BaseModel):
    session_id: Optional[str] = "default_session"

class StepRequest(BaseModel):
    session_id: Optional[str] = "default_session"
    user_message: Optional[str] = None

class ShockRequest(BaseModel):
    session_id: Optional[str] = "default_session"

class ProbeRequest(BaseModel):
    session_id: Optional[str] = "default_session"

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": "HydroMediate AI Mediator",
        "gemini_active": HAS_GEMINI,
        "docs": "/docs"
    }



@app.post("/api/negotiation/start")
def start_negotiation(req: StartRequest):
    session_id = req.session_id or "default_session"
    engine = MediatorEngine(session_id)
    sessions[session_id] = engine
    return {
        "message": "Negotiation session initialized",
        "state": engine.state.dict()
    }

@app.post("/api/negotiation/step")
def step_negotiation(req: StepRequest):
    session_id = req.session_id or "default_session"
    engine = get_engine(session_id)
    
    res = engine.process_step(req.user_message)
    
    # Try generating Gemini AI text if available and user provided input
    if HAS_GEMINI and req.user_message:
        ai_response = generate_mediator_turn_response(engine.state.dict(), req.user_message)
        if ai_response:
            ai_msg = {
                "turn": engine.state.current_turn,
                "speaker": "Mediator AI (Groq llama-3.3-70b)",
                "role": "mediator",
                "text": ai_response
            }
            engine.state.messages.append(ai_msg)
            res["latest_message"] = ai_msg

    return {
        "state": engine.state.dict(),
        "latest_message": res["latest_message"]
    }

@app.post("/api/negotiation/probe_report")
def probe_report(req: ProbeRequest):
    session_id = req.session_id or "default_session"
    engine = get_engine(session_id)
    result = engine.probe_fabricated_report()
    return {
        "result": result,
        "state": engine.state.dict()
    }

@app.post("/api/negotiation/trigger_shock")
def trigger_shock(req: ShockRequest):
    session_id = req.session_id or "default_session"
    engine = get_engine(session_id)
    result = engine.trigger_yield_shock()
    return {
        "result": result,
        "state": engine.state.dict()
    }

@app.get("/api/negotiation/ledger")
def get_ledger(session_id: str = "default_session"):
    engine = get_engine(session_id)
    return {
        "session_id": session_id,
        "claims": [c.dict() for c in engine.state.claims]
    }

@app.get("/api/negotiation/accord")
def get_accord(session_id: str = "default_session"):
    engine = get_engine(session_id)
    accord = engine.generate_enforceable_accord()
    return {
        "accord": accord
    }

# Mount static frontend files
from fastapi.staticfiles import StaticFiles
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {
            "status": "online",
            "app": "HydroMediate AI Mediator",
            "gemini_active": HAS_GEMINI,
            "docs": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 55210))
    uvicorn.run("main:app", host="localhost", port=port, reload=False)
