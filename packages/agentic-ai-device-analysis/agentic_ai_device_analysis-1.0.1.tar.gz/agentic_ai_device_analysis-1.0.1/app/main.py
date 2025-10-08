from fastapi import FastAPI, Request, HTTPException, Body, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional, List, Any
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
import json

from app.core.device_fingerprint import DeviceFingerprint
from app.core.behavior_analysis import BehaviorAnalyzer
from app.db.mongodb import MongoDB

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Device Behavior Analytics",
    description="API for device fingerprinting and behavior analysis with Agentic AI",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Initialize components
mongo_client = MongoDB(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
behavior_analyzer = BehaviorAnalyzer()

# Initialize agentic analyzer
agentic_enabled = os.getenv("ENABLE_AGENTIC_ANALYSIS", "true").lower() == "true"
print("Agentic AI analysis enabled")
    
# Add new API endpoints for agentic analysis
@app.post("/api/agentic/analyze")
async def analyze_with_agentic_ai(device_data: Dict = Body(...)):
    """
    Analyze device data using Agentic AI capabilities
    """
    if not agentic_enabled:
        return {"status": "error", "message": "Agentic analysis not available"}
    
    try:
        session_id = device_data.get("session_id", str(datetime.utcnow().timestamp()))
        
        # Get device fingerprint and behavior data
        fingerprint_data = device_data.get("fingerprint", {})
        behavior_data = device_data.get("behavior", {})
        
        # Create mock analysis result for quick testing
        analysis_result = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "risk_level": "medium",
            "risk_score": 45.5,
            "features": [
                {
                    "name": "canvas_fingerprint",
                    "value": fingerprint_data.get("canvas_fingerprint", ""),
                    "description": "Canvas fingerprint consistency",
                    "agentic_indicator": False
                },
                {
                    "name": "hardware_concurrency",
                    "value": fingerprint_data.get("hardware_concurrency", 0),
                    "description": "Number of logical processors",
                    "agentic_indicator": False
                },
                {
                    "name": "touch_support",
                    "value": fingerprint_data.get("touch_support", False),
                    "description": "Touch support availability",
                    "agentic_indicator": False
                }
            ],
            "insights": [
                {
                    "title": "Moderate Risk Profile",
                    "description": "Some unusual patterns detected, but may be due to legitimate factors.",
                    "severity": "medium"
                }
            ]
        }
        
        # Store analysis result
        await mongo_client.store_agentic_analysis(session_id, analysis_result)
        
        return analysis_result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/agentic/insights/{session_id}")
async def get_agentic_insights(session_id: str):
    """
    Get agentic insights for a specific session
    """
    if not agentic_enabled:
        return {"status": "error", "message": "Agentic analysis not available"}
    
    try:
        analysis_history = await mongo_client.get_agentic_analysis_history(session_id)
        if not analysis_history:
            return {"status": "not_found", "message": "No analysis found for this session"}
        
        return {"status": "success", "insights": analysis_history}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def home(request: Request):
    """Serve the main application page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/device/profile")
async def create_device_profile(request: Request, fingerprint_data: Dict = Body(None)) -> Dict:
    """Create or update device profile based on fingerprint with agentic analysis."""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    session_id = request.headers.get("x-session-id")
    
    # Create fingerprint with enhanced attributes from request body
    fingerprint = DeviceFingerprint(
        ip_address=client_ip,
        user_agent=user_agent,
        session_id=session_id,
        **fingerprint_data if fingerprint_data else {}
    )
    
    # Generate fingerprint hash for consistent identification
    fingerprint_dict = fingerprint.to_dict()
    fingerprint_hash = fingerprint.generate_fingerprint_hash()
    uniqueness_score = fingerprint.calculate_uniqueness_score()
    
    # Store fingerprint and get profile ID
    profile_id = await mongo_client.store_device_profile(fingerprint)
    
    # Find similar profiles
    similar_profiles = await mongo_client.get_similar_profiles(fingerprint)
    
    # Get historical context data for this device
    context_data = await mongo_client.get_device_context(fingerprint)
    
    # Perform agentic analysis if we have a session ID and agentic analyzer is available
    agentic_result = {}
    if session_id and agentic_enabled and agentic_analyzer:
        try:
            # Get latest behavior data if available
            latest_behavior = await mongo_client.get_latest_behavior(session_id)
            
            # Analyze with agentic analyzer using dictionary approach
            agentic_result = agentic_analyzer.analyze(
                session_id=session_id,
                fingerprint_data=fingerprint_dict,
                behavior_data=latest_behavior if latest_behavior else {},
                context_data=context_data
            )
            
            # Store analysis result
            await mongo_client.store_agentic_analysis(profile_id, agentic_result)
        except Exception as e:
            print(f"Agentic analysis error: {e}")
            agentic_result = {"error": str(e)}
    
    return {
        "profile_id": profile_id,
        "similar_profiles_count": len(similar_profiles),
        "device_info": fingerprint.parse_user_agent(),
        "fingerprint_hash": fingerprint_hash,
        "uniqueness_score": uniqueness_score,
        "agentic_analysis": agentic_result
    }

@app.post("/api/behavior/analyze")
async def analyze_behavior(behavior: UserBehavior) -> Dict:
    """Analyze user behavior and return risk assessment with agentic insights."""
    # Store behavior data
    behavior_id = await mongo_client.store_behavior(behavior)
    
    # Get historical behaviors for this session
    historical_behaviors = await mongo_client.get_device_behaviors(behavior.session_id)
    
    # Train behavior model if we have enough data
    if len(historical_behaviors) >= 5:
        behavior_analyzer.train([UserBehavior(**b) for b in historical_behaviors])
    
    # Analyze current behavior
    analysis_result = behavior_analyzer.analyze(behavior)
    
    # Get device fingerprint for this session
    fingerprint = await mongo_client.get_device_fingerprint_by_session(behavior.session_id)
    
    # Get context data for agentic analysis
    context_data = await mongo_client.get_device_context(fingerprint) if fingerprint else {}
    
    # Perform agentic analysis
    agentic_result = {}
    if agentic_enabled and agentic_analyzer and fingerprint:
        try:
            device_attrs = DeviceAttributes(
                session_id=behavior.session_id,
                fingerprint_data=fingerprint.to_dict() if fingerprint else {},
                behavior_data=behavior.model_dump(),
                context_data=context_data
            )
            
            agentic_result = agentic_analyzer.analyze(device_attrs)
            
            # Store agentic analysis result
            await mongo_client.store_agentic_analysis(fingerprint.id, agentic_result)
        except Exception as e:
            print(f"Agentic analysis error: {e}")
            agentic_result = {"error": str(e)}
    
    return {
        "behavior_id": behavior_id,
        "risk_score": analysis_result["risk_score"],
        "features": analysis_result["features"],
        "agentic_analysis": agentic_result,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/device/{profile_id}")
async def get_device_profile(profile_id: str) -> Dict:
    """Retrieve device profile and its behavior history with agentic insights."""
    profile = await mongo_client.get_device_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get agentic analysis history
    agentic_history = await mongo_client.get_agentic_analysis_history(profile_id)
    
    # Add agentic analysis to profile
    profile["agentic_analysis_history"] = agentic_history
    
    return profile

@app.post("/api/agentic/analyze")
async def perform_agentic_analysis(device_data: Dict[str, Any] = Body(...)) -> Dict:
    """Perform comprehensive agentic analysis on device attributes."""
    if not agentic_enabled:
        return {
            "session_id": device_data.get("session_id", "unknown"),
            "analysis_result": {"error": "Agentic analysis not available"},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    session_id = device_data.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
        
    fingerprint_data = device_data.get("fingerprint_data")
    behavior_data = device_data.get("behavior_data")
    context_data = device_data.get("context_data")
    
    # Get stored fingerprint and behavior data if not provided
    if not fingerprint_data:
        fingerprint = await mongo_client.get_device_fingerprint_by_session(session_id)
        fingerprint_data = fingerprint.to_dict() if fingerprint else {}
    
    if not behavior_data:
        latest_behavior = await mongo_client.get_latest_behavior(session_id)
        behavior_data = latest_behavior if latest_behavior else {}
    
    if not context_data:
        fingerprint = await mongo_client.get_device_fingerprint_by_session(session_id)
        context_data = await mongo_client.get_device_context(fingerprint) if fingerprint else {}
    
    try:
        # Perform agentic analysis using dictionary approach
        analysis_result = agentic_analyzer.analyze(
            session_id=session_id,
            fingerprint_data=fingerprint_data,
            behavior_data=behavior_data,
            context_data=context_data,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Store analysis result if we have a fingerprint
        fingerprint = await mongo_client.get_device_fingerprint_by_session(session_id)
        if fingerprint:
            await mongo_client.store_agentic_analysis(fingerprint.id, analysis_result)
        
        return {
            "session_id": session_id,
            "analysis_result": analysis_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "session_id": session_id,
            "analysis_result": {"error": f"Analysis error: {str(e)}"},
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/agentic/insights/{session_id}")
async def get_agentic_insights(session_id: str) -> Dict:
    """Get agentic insights for a specific session."""
    # Get fingerprint for this session
    fingerprint = await mongo_client.get_device_fingerprint_by_session(session_id)
    if not fingerprint:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get agentic analysis history
    agentic_history = await mongo_client.get_agentic_analysis_history(fingerprint.id)
    
    # Get latest behavior data
    latest_behavior = await mongo_client.get_latest_behavior(session_id)
    
    return {
        "session_id": session_id,
        "device_info": fingerprint.parse_user_agent(),
        "fingerprint_hash": fingerprint.generate_fingerprint_hash(),
        "uniqueness_score": fingerprint.calculate_uniqueness_score(),
        "latest_behavior": latest_behavior,
        "agentic_insights": agentic_history,
        "timestamp": datetime.utcnow().isoformat()
    }