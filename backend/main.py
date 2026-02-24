from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import os
import logging
import time
from collections import defaultdict
from typing import Dict, Any

import torch

from utils import (load_crop_model, load_pest_model, get_prediction, get_prediction_confidence, 
                   get_gemini_solution, get_calibrated_prediction, make_intelligent_decision, 
                   TemperatureScaling)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting
rate_limit_storage: Dict[str, list] = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

app = FastAPI(
    title="KrishiSetu API",
    description="Crop Disease and Pest Detection API",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit"""
    now = time.time()
    # Clean old requests
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip] 
        if now - req_time < RATE_LIMIT_WINDOW
    ]
    
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    rate_limit_storage[client_ip].append(now)
    return True

def validate_image(contents: bytes) -> None:
    """Validate uploaded image"""
    # Check file size (10MB limit)
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
    
    # Check if it's a valid image
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # Verify it's a valid image
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Remove dimension checks
    image = Image.open(io.BytesIO(contents))
    width, height = image.size
    logger.info(f"Uploaded image dimensions: {width}x{height}")

# Pest model configuration
PEST_MODEL_PATH = os.path.join("model", "pest_model_b0.pth")
PEST_CLASSES = [
    'aphids', 'armyworm', 'bollworm', 'cutworm', 'grasshopper',
    'leafhoppers', 'mites', 'stemborer', 'weevil'
]

# Crop-specific model configuration
CROP_MODELS = {
    'rice': {
        'disease_model_path': os.path.join("model", "rice_disease_model.pth"),
        'healthy_model_path': os.path.join("model", "rice_healthy_model.pth"),
        'classes': ['BrownSpot', 'Healthy', 'Hispa', 'LeafBlast']
    },
    'wheat': {
        'disease_model_path': os.path.join("model", "wheat_disease_model.pth"),
        'healthy_model_path': os.path.join("model", "wheat_healthy_model.pth"),
        'classes': ['Healthy', 'septoria', 'stripe_rust']
    },
    'corn': {
        'disease_model_path': os.path.join("model", "corn_disease_model.pth"),
        'healthy_model_path': os.path.join("model", "corn_healthy_model.pth"),
        'classes': ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']
    },
    'tomato': {
        'disease_model_path': os.path.join("model", "tomato_disease_model.pth"),
        'healthy_model_path': os.path.join("model", "tomato_healthy_model.pth"),
        'classes': ['Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']
    },
    'potato': {
        'disease_model_path': os.path.join("model", "potato_disease_model.pth"),
        'healthy_model_path': os.path.join("model", "potato_healthy_model.pth"),
        'classes': ['Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight']
    },
    'cotton': {
        'disease_model_path': os.path.join("model", "cotton_disease_model.pth"),
        'healthy_model_path': os.path.join("model", "cotton_healthy_model.pth"),
        'classes': ['diseased cotton leaf', 'diseased cotton plant', 'fresh cotton leaf', 'fresh cotton plant']
    },
    'sugarcane': {
        'disease_model_path': os.path.join("model", "sugarcane_disease_model.pth"),
        'healthy_model_path': os.path.join("model", "sugarcane_healthy_model.pth"),
        'classes': ['Healthy', 'Mosaic', 'RedRot', 'Rust', 'Yellow']
    }
}

# Cache for loaded models and temperature scalers
loaded_models = {}
pest_model = None
temperature_scalers = {}

# Load pest model at startup
try:
    pest_model = load_pest_model(PEST_MODEL_PATH)
    if pest_model:
        pest_model.eval()
        # Initialize temperature scaler for pest model
        temperature_scalers['pest'] = TemperatureScaling()
        logger.info("Pest model loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading pest model: {str(e)}")
    pest_model = None

@app.post("/predict")
async def predict(
    request: Request,
    file: UploadFile = File(...),
    crop: str = Form(...)
):
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Rate limiting
        if not check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate filename
        if not file.filename or len(file.filename) > 255:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Read and validate file contents
        contents = await file.read()
        validate_image(contents)
        
        # Process image
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        logger.info(f"Processing image: {file.filename} for crop: {crop} from IP: {client_ip}")
        
        # Validate and normalize crop input
        crop_lower = crop.lower().strip()
        if not crop_lower or len(crop_lower) > 50:
            raise HTTPException(status_code=400, detail="Invalid crop name")
        
        # Check if crop is supported
        if crop_lower not in CROP_MODELS:
            supported_crops = list(CROP_MODELS.keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Crop '{crop}' not supported. Supported crops: {', '.join(supported_crops)}"
            )
        
        # 1. PEST DETECTION (Universal for all crops)
        pest_result = None
        if pest_model is not None:
            try:
                pest_result = get_calibrated_prediction(
                    pest_model, image, PEST_CLASSES, 
                    temperature_scalers.get('pest')
                )
                logger.info(f"Pest prediction: {pest_result['class']} (confidence: {pest_result['confidence']:.3f}, uncertain: {pest_result['uncertain']})")
            except Exception as e:
                logger.error(f"Pest prediction failed: {e}")
        
        # 2. HEALTHY CHECK (Crop-specific binary classifier)
        healthy_result = None
        healthy_key = f"{crop_lower}_healthy"
        if healthy_key not in loaded_models:
            try:
                model_config = CROP_MODELS[crop_lower]
                if os.path.exists(model_config['healthy_model_path']):
                    model = load_crop_model(model_config['healthy_model_path'], 2)  # Binary: Healthy, Not Healthy
                    loaded_models[healthy_key] = {
                        'model': model,
                        'classes': ['Healthy', 'Not Healthy']
                    }
                    temperature_scalers[healthy_key] = TemperatureScaling()
                    logger.info(f"Loaded {crop} healthy model successfully")
            except Exception as e:
                logger.error(f"Error loading {crop} healthy model: {str(e)}")
        
        if healthy_key in loaded_models:
            try:
                healthy_model_data = loaded_models[healthy_key]
                model = healthy_model_data['model']
                classes = healthy_model_data['classes']
                
                healthy_result = get_calibrated_prediction(
                    model, image, classes, 
                    temperature_scalers.get(healthy_key)
                )
                logger.info(f"Healthy check: {healthy_result['class']} (confidence: {healthy_result['confidence']:.3f})")
            except Exception as e:
                logger.error(f"Healthy check failed: {e}")
        
        # 3. DISEASE DETECTION (Crop-specific)
        # 3. DISEASE DETECTION (Crop-specific)
        # Load crop-specific model if not already loaded
        if crop_lower not in loaded_models:
            try:
                model_config = CROP_MODELS[crop_lower]
                model = load_crop_model(model_config['disease_model_path'], len(model_config['classes']))
                loaded_models[crop_lower] = {
                    'model': model,
                    'classes': model_config['classes']
                }
                # Initialize temperature scaler for this crop
                temperature_scalers[crop_lower] = TemperatureScaling()
                logger.info(f"Loaded {crop} disease model successfully")
            except Exception as e:
                logger.error(f"❌ Error loading {crop} disease model: {str(e)}")
        
        # Get disease prediction if model available
        disease_result = None
        if crop_lower in loaded_models:
            try:
                crop_model_data = loaded_models[crop_lower]
                model = crop_model_data['model']
                classes = crop_model_data['classes']
                
                disease_result = get_calibrated_prediction(
                    model, image, classes, 
                    temperature_scalers.get(crop_lower)
                )
                logger.info(f"Disease prediction: {disease_result['class']} (confidence: {disease_result['confidence']:.3f}, uncertain: {disease_result['uncertain']})")
            except Exception as e:
                logger.error(f"Disease prediction failed: {e}")
        
        if not pest_result and not disease_result and not healthy_result:
            raise HTTPException(status_code=500, detail="No models available for prediction")
        
        # 4. INTELLIGENT DECISION MAKING WITH HEALTHY CHECK
        # If healthy model says "Healthy" with reasonable confidence, return immediately
        if healthy_result and healthy_result['class'] == 'Healthy' and healthy_result['confidence'] > 0.60:
            # Double-check: if pest model is very confident, flag for review
            if pest_result and pest_result['confidence'] > 0.85:
                logger.info("Healthy detected but pest model very confident - flagging for review")
                return JSONResponse(content={
                    "predicted_class": "Uncertain - Review Required",
                    "confidence": healthy_result['confidence'],
                    "prediction_type": "uncertain",
                    "health_status": "Unknown",
                    "requires_review": True,
                    "solution": {
                        "problem": "Conflicting predictions detected",
                        "occurrence": "System needs expert review",
                        "natural_remedies": ["Inspect crop manually"],
                        "chemical_remedies": [],
                        "additional_advice": "Please consult an agricultural expert for accurate diagnosis."
                    }
                })
            
            return JSONResponse(content={
                "predicted_class": "Healthy",
                "confidence": healthy_result['confidence'],
                "prediction_type": "healthy",
                "health_status": "Healthy",
                "solution": {
                    "problem": "No issues detected",
                    "occurrence": "Crop is healthy",
                    "natural_remedies": ["Continue regular watering", "Maintain proper spacing"],
                    "chemical_remedies": [],
                    "additional_advice": "Your crop is in good health. Continue regular maintenance."
                }
            })
        
        # If healthy model says "Not Healthy", proceed with pest/disease analysis
        if pest_result and disease_result:
            decision = make_intelligent_decision(pest_result, disease_result, crop_lower)
            
            # Determine health status
            health_status = "Unhealthy" if decision['decision'] in ['pest', 'disease'] else "Unknown"
            predicted_class = decision.get('primary_prediction', {}).get('class', 'Unknown')
            
            response_data = {
                "predicted_class": predicted_class,
                "confidence": decision['confidence'],
                "prediction_type": decision['decision'],
                "health_status": health_status,
                "requires_review": decision.get('requires_review', False)
            }
            
            if decision['decision'] in ['pest', 'disease'] and decision.get('primary_prediction'):
                try:
                    solution = get_gemini_solution(crop, predicted_class)
                    response_data["solution"] = solution
                except Exception as e:
                    logger.error(f"Solution generation failed: {e}")
                    response_data["solution"] = {
                        "problem": f"Detected: {predicted_class}",
                        "occurrence": "Issue detected in crop",
                        "natural_remedies": ["Consult local agricultural expert"],
                        "chemical_remedies": [],
                        "additional_advice": "Professional consultation recommended."
                    }
            
            logger.info(f"Final decision: {decision['decision']} with confidence {decision['confidence']:.3f}")
            return JSONResponse(content=response_data)
        
        # Fallback if only one model available
        elif disease_result:
            predicted_class = disease_result['class']
            health_status = "Healthy" if 'healthy' in predicted_class.lower() else "Unhealthy"
            solution = get_gemini_solution(crop, predicted_class)
            return JSONResponse(content={
                "predicted_class": predicted_class,
                "confidence": disease_result['confidence'],
                "prediction_type": "disease",
                "health_status": health_status,
                "requires_review": disease_result.get('uncertain', False),
                "solution": solution
            })
        
        elif pest_result:
            solution = get_gemini_solution(crop, pest_result['class'])
            return JSONResponse(content={
                "predicted_class": pest_result['class'],
                "confidence": pest_result['confidence'],
                "prediction_type": "pest",
                "health_status": "Unhealthy",
                "requires_review": pest_result.get('uncertain', False),
                "solution": solution
            })
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@app.get("/")
async def root():
    return {"message": "KrishiSetu API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check if models are loaded
        pest_status = "loaded" if pest_model is not None else "not_loaded"
        disease_models_count = len(loaded_models)
        
        return {
            "status": "healthy",
            "pest_model": pest_status,
            "disease_models_loaded": disease_models_count,
            "supported_crops": list(CROP_MODELS.keys()),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/models-status")
async def models_status():
    """Detailed model status endpoint"""
    try:
        status = {
            "pest_model": "loaded" if pest_model is not None else "not_loaded"
        }
        for crop in CROP_MODELS.keys():
            status[f"{crop}_disease_model"] = "loaded" if crop in loaded_models else "not_loaded"
        return status
    except Exception as e:
        logger.error(f"Model status check failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model status")