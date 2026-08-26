from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import json
from datetime import datetime
from collections import defaultdict

# Load the trained model
model = joblib.load('bot_detector.joblib')

# Feature names in the same order as training
FEATURE_NAMES = [
    "interaction_duration", "mouse_count", "mouse_speed_mean",
    "mouse_speed_variance", "click_count", "click_interval_variance",
    "scroll_count", "keyboard_count", "request_frequency",
    "webdriver_flag", "touch_support", "viewport_width",
    "viewport_height", "timezone_offset", "hardware_concurrency",
]

# Human-readable descriptions for each feature, used in explanations
FEATURE_LABELS = {
    "interaction_duration": "very short time on page",
    "mouse_count": "very few mouse movements",
    "mouse_speed_mean": "unusually fast/robotic mouse speed",
    "mouse_speed_variance": "unnaturally consistent mouse speed",
    "click_count": "unusual click count",
    "click_interval_variance": "mechanically-timed clicks",
    "scroll_count": "little to no scrolling",
    "keyboard_count": "little to no keyboard activity",
    "request_frequency": "abnormally high request rate",
    "webdriver_flag": "automation tool detected (webdriver flag)",
    "touch_support": "unusual touch/device signal",
    "viewport_width": "unusual viewport width",
    "viewport_height": "unusual viewport height",
    "timezone_offset": "unusual timezone signal",
    "hardware_concurrency": "unusual hardware signal",
}

def get_top_reasons(features_array, top_n=3):
    """Combine global feature importance with this request's values
    to surface the most likely reasons behind the decision."""
    importances = model.feature_importances_
    values = features_array[0]

    ranked_idx = sorted(range(len(importances)), key=lambda i: importances[i], reverse=True)
    top_idx = ranked_idx[:top_n]

    reasons = []
    for i in top_idx:
        name = FEATURE_NAMES[i]
        reasons.append({
            "feature": name,
            "value": round(float(values[i]), 3),
            "importance": round(float(importances[i]), 4),
            "description": FEATURE_LABELS.get(name, name),
        })
    return reasons

# Create FastAPI app
app = FastAPI(title="PassiveGuard", description="Passive Bot Detection System")

# Enable CORS (so frontend can call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store request history for dashboard
request_history = {
    "total_requests": 0,
    "human_count": 0,
    "bot_count": 0,
    "suspicious_count": 0,
    "allowed": 0,
    "challenged": 0,
    "blocked": 0,
}

# Request model
class TelemetryRequest(BaseModel):
    interaction_duration: float
    mouse_count: int
    mouse_speed_mean: float
    mouse_speed_variance: float
    click_count: int
    click_interval_variance: float
    scroll_count: int
    keyboard_count: int
    request_frequency: float
    webdriver_flag: int
    touch_support: int
    viewport_width: int
    viewport_height: int
    timezone_offset: int
    hardware_concurrency: int

# Explainability reason model
class Reason(BaseModel):
    feature: str
    value: float
    importance: float
    description: str

# Response model
class RiskResponse(BaseModel):
    risk_score: float
    classification: str
    decision: str
    confidence: float
    top_reasons: list[Reason]

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "PassiveGuard API is running"}

# Main risk evaluation endpoint
@app.post("/api/risk/evaluate", response_model=RiskResponse)
def evaluate_risk(telemetry: TelemetryRequest):
    try:
        # Convert request to feature array
        features = [
            telemetry.interaction_duration,
            telemetry.mouse_count,
            telemetry.mouse_speed_mean,
            telemetry.mouse_speed_variance,
            telemetry.click_count,
            telemetry.click_interval_variance,
            telemetry.scroll_count,
            telemetry.keyboard_count,
            telemetry.request_frequency,
            telemetry.webdriver_flag,
            telemetry.touch_support,
            telemetry.viewport_width,
            telemetry.viewport_height,
            telemetry.timezone_offset,
            telemetry.hardware_concurrency,
        ]

        # Reshape for model prediction
        features_array = [features]

        # Get prediction and probability
        prediction = model.predict(features_array)[0]
        probabilities = model.predict_proba(features_array)[0]

        # Get explainability info
        top_reasons = get_top_reasons(features_array)

        # Map prediction to label
        label_map = {0: "human", 1: "bot", 2: "suspicious"}
        classification = label_map[prediction]

        # Get risk score (probability of being bot)
        risk_score = probabilities[1]  # Bot probability

        # Determine decision based on risk thresholds
        if risk_score < 0.3:
            decision = "allow"
            request_history["allowed"] += 1
        elif risk_score < 0.7:
            decision = "challenge"
            request_history["challenged"] += 1
        else:
            decision = "block"
            request_history["blocked"] += 1

        # Update statistics
        request_history["total_requests"] += 1
        if classification == "human":
            request_history["human_count"] += 1
        elif classification == "bot":
            request_history["bot_count"] += 1
        else:
            request_history["suspicious_count"] += 1

        # Get confidence
        confidence = max(probabilities)

        return RiskResponse(
            risk_score=round(risk_score, 4),
            classification=classification,
            decision=decision,
            confidence=round(confidence, 4),
            top_reasons=top_reasons
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Challenge verification endpoint
@app.post("/api/challenge/verify")
def verify_challenge(data: dict):
    try:
        if "challenge_response" in data:
            return {
                "verified": True,
                "message": "Challenge passed",
                "status": "authorized"
            }
        else:
            return {
                "verified": False,
                "message": "Challenge failed",
                "status": "denied"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Dashboard endpoint
@app.get("/api/dashboard")
def get_dashboard():
    try:
        total = request_history["total_requests"]
        if total == 0:
            percentages = {"human": 0, "bot": 0, "suspicious": 0, "allowed": 0, "challenged": 0, "blocked": 0}
        else:
            percentages = {
                "human": round((request_history["human_count"] / total) * 100, 1),
                "bot": round((request_history["bot_count"] / total) * 100, 1),
                "suspicious": round((request_history["suspicious_count"] / total) * 100, 1),
                "allowed": round((request_history["allowed"] / total) * 100, 1),
                "challenged": round((request_history["challenged"] / total) * 100, 1),
                "blocked": round((request_history["blocked"] / total) * 100, 1),
            }

        return {
            "total_requests": request_history["total_requests"],
            "human_count": request_history["human_count"],
            "bot_count": request_history["bot_count"],
            "suspicious_count": request_history["suspicious_count"],
            "allowed": request_history["allowed"],
            "challenged": request_history["challenged"],
            "blocked": request_history["blocked"],
            "percentages": percentages,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Protected API endpoint
@app.get("/api/resident/profile")
def get_resident_profile():
    return {
        "message": "Protected API - Demo Data",
        "status": "authorized",
        "data": {
            "profile_id": "demo_001",
            "access_level": "standard",
            "created_at": datetime.now().isoformat()
        }
    }

# Root endpoint
@app.get("/")
def read_root():
    return {
        "name": "PassiveGuard",
        "version": "1.0.0",
        "description": "Privacy-Preserving Passive Bot Detection",
        "endpoints": {
            "health": "/health",
            "evaluate_risk": "/api/risk/evaluate (POST)",
            "verify_challenge": "/api/challenge/verify (POST)",
            "dashboard": "/api/dashboard (GET)",
            "profile": "/api/resident/profile (GET)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PassiveGuard API Server...")
    print("📍 Server running at: http://localhost:8000")
    print("📚 API Docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)