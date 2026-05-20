"""
MLDeploy Pro - Python ML Service
Handles model training, building, and inference serving.
"""
import os
import json
import uuid
import time
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
PREDICTION_COUNTER = Counter(
    'ml_predictions_total', 
    'Total predictions', 
    ['model_id', 'status']
)
PREDICTION_LATENCY = Histogram(
    'ml_prediction_latency_seconds', 
    'Prediction latency', 
    ['model_id']
)
BUILD_COUNTER = Counter(
    'ml_builds_total', 
    'Total model builds', 
    ['status']
)

# In-memory registries (replace with Redis/DB in production)
MODEL_REGISTRY = {}
DEPLOYMENT_REGISTRY = {}

class BuildRequest(BaseModel):
    model_id: str
    version: str
    framework: str = "sklearn"

class PredictRequest(BaseModel):
    deployment_id: str
    input_data: dict

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    active_models: int
    active_deployments: int

app = FastAPI(
    title="MLDeploy Pro - ML Service",
    description="Python microservice for model training, building, and inference",
    version="1.0.0"
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        active_models=len(MODEL_REGISTRY),
        active_deployments=len(DEPLOYMENT_REGISTRY)
    )

@app.get("/health/{deployment_id}")
async def deployment_health(deployment_id: str):
    """Check health of specific deployment"""
    deployment = DEPLOYMENT_REGISTRY.get(deployment_id)
    if not deployment:
        return {
            "is_healthy": False, 
            "status": "not_found", 
            "cpu_usage": None, 
            "memory_usage": None
        }
    
    return {
        "is_healthy": deployment.get("status") == "running",
        "status": deployment.get("status", "unknown"),
        "cpu_usage": 0.15,
        "memory_usage": 0.42
    }

@app.post("/build")
async def build_model(request: BuildRequest, background_tasks: BackgroundTasks):
    """Build and package a model as Docker image"""
    logger.info(f"Building model {request.model_id} version {request.version}")
    
    build_id = str(uuid.uuid4())
    
    # Queue background build
    background_tasks.add_task(
        _build_model_async,
        build_id=build_id,
        model_id=request.model_id,
        version=request.version,
        framework=request.framework
    )
    
    BUILD_COUNTER.labels(status="started").inc()
    
    return {
        "build_id": build_id,
        "status": "building",
        "message": "Build queued. Check status endpoint for progress."
    }

async def _build_model_async(build_id: str, model_id: str, version: str, framework: str):
    """Async model building process"""
    try:
        logger.info(f"[{build_id}] Starting build for {model_id}")
        
        # Simulate build process
        await _simulate_delay(2)
        
        image_uri = f"mldeploy/{model_id}:{version}"
        endpoint_url = f"http://localhost:8001/models/{model_id}/{version}"
        
        # Register deployment
        DEPLOYMENT_REGISTRY[build_id] = {
            "model_id": model_id,
            "version": version,
            "image_uri": image_uri,
            "endpoint_url": endpoint_url,
            "status": "running",
            "built_at": datetime.utcnow().isoformat()
        }
        
        BUILD_COUNTER.labels(status="success").inc()
        logger.info(f"[{build_id}] Build completed: {image_uri}")
        
    except Exception as e:
        BUILD_COUNTER.labels(status="failed").inc()
        logger.error(f"[{build_id}] Build failed: {str(e)}")
        raise

@app.post("/predict")
async def predict(request: PredictRequest):
    """Make prediction using deployed model"""
    start_time = time.time()
    
    deployment = DEPLOYMENT_REGISTRY.get(request.deployment_id)
    if not deployment:
        PREDICTION_COUNTER.labels(model_id="unknown", status="error").inc()
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    try:
        model_id = deployment["model_id"]
        
        # Simulate inference
        import random
        prediction = {
            "model_id": model_id,
            "version": deployment["version"],
            "prediction": random.choice([0, 1]),
            "confidence": round(random.uniform(0.7, 0.99), 4),
            "input_features": len(request.input_data)
        }
        
        latency = time.time() - start_time
        PREDICTION_LATENCY.labels(model_id=model_id).observe(latency)
        PREDICTION_COUNTER.labels(model_id=model_id, status="success").inc()
        
        return {
            "output": prediction,
            "latency_ms": round(latency * 1000, 2),
            "deployment_id": request.deployment_id
        }
        
    except Exception as e:
        PREDICTION_COUNTER.labels(
            model_id=deployment["model_id"], 
            status="error"
        ).inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/{model_id}/upload")
async def upload_model(
    model_id: str,
    version: str = "1.0.0",
    file: UploadFile = File(...)
):
    """Upload a trained model file"""
    model_dir = f"./artifacts/{model_id}/{version}"
    os.makedirs(model_dir, exist_ok=True)
    
    file_path = f"{model_dir}/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    MODEL_REGISTRY[model_id] = {
        "version": version,
        "file_path": file_path,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    return {
        "model_id": model_id,
        "version": version,
        "file_path": file_path,
        "status": "uploaded"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/models")
async def list_models():
    """List all registered models"""
    return {
        "models": [
            {"id": k, **v} 
            for k, v in MODEL_REGISTRY.items()
        ]
    }

@app.get("/deployments")
async def list_deployments():
    """List all active deployments"""
    return {
        "deployments": [
            {"id": k, **v} 
            for k, v in DEPLOYMENT_REGISTRY.items()
        ]
    }

async def _simulate_delay(seconds: int):
    """Simulate async work"""
    await __import__('asyncio').sleep(seconds)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)