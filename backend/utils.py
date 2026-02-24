import os
import time
import json
import logging
import torch
import numpy as np

from PIL import Image
from torchvision import transforms
from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# Logging
# --------------------------------------------------
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Environment setup
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in environment variables")

# --------------------------------------------------
# Gemini client (official SDK)
# --------------------------------------------------
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
GEMINI_MODEL = "gemini-flash-latest"  # Stable & fast

# --------------------------------------------------
# Model imports
# --------------------------------------------------
from model.pest_model_b0_def import PestClassifier
from model.crop_disease_model_b3_def import CropDiseaseClassifier

# --------------------------------------------------
# Load Pest Model
# --------------------------------------------------
def load_pest_model(model_path: str):
    try:
        if not os.path.exists(model_path):
            logger.error(f"Pest model file not found: {model_path}")
            return None

        model = PestClassifier(num_classes=9)
        state_dict = torch.load(model_path, map_location="cpu")
        model.load_state_dict(state_dict)
        model.eval()

        logger.info(f"Pest model loaded from {model_path}")
        return model

    except Exception as e:
        logger.error(f"Pest model loading error: {e}")
        return None

# --------------------------------------------------
# Load Crop Disease Model
# --------------------------------------------------
def load_crop_model(model_path: str, num_classes: int):
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        model = CropDiseaseClassifier(num_classes)
        checkpoint = torch.load(model_path, map_location="cpu")

        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            model.load_state_dict(checkpoint)

        model.eval()
        logger.info(f"Crop model loaded from {model_path}")
        return model

    except Exception as e:
        logger.error(f"Crop model loading error: {e}")
        raise

# --------------------------------------------------
# Prediction Confidence
# --------------------------------------------------
def get_prediction_confidence(model, image: Image.Image) -> float:
    try:
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        img_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            return torch.max(probs).item()

    except Exception as e:
        logger.error(f"Confidence calculation error: {e}")
        return 0.0

# --------------------------------------------------
# Prediction Label
# --------------------------------------------------
def get_prediction(model, image: Image.Image, class_names: list) -> str:
    try:
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        img_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(img_tensor)
            _, predicted = torch.max(outputs, 1)
            idx = predicted.item()

        return class_names[idx] if idx < len(class_names) else class_names[0]

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return class_names[0] if class_names else "unknown"

# --------------------------------------------------
# Gemini AI Advisory (REALISTIC + SAFE)
# --------------------------------------------------
def get_gemini_solution(crop: str, pest: str) -> dict:
    logger.info(f"Generating advisory for crop={crop}, issue={pest}")

    prompt = f"""
You are an experienced agricultural extension officer in India.

Crop: {crop}
Pest or Disease: {pest}

Provide PRACTICAL and FARMER-FRIENDLY advice.

RULES:

1. Natural remedies:
   - Must be realistic and commonly practiced
   - Examples: neem oil, neem seed kernel extract, garlic-chilli spray,
     cow urine solution, removing infected leaves, proper spacing,
     avoiding excess irrigation
   - Write simple, easy-to-follow steps

2. Chemical remedies:
   - Mention REAL and commonly used chemicals in India
   - Examples:
     Mancozeb, Carbendazim, Propiconazole, Azoxystrobin,
     Imidacloprid, Thiamethoxam, Chlorpyrifos, Metalaxyl
   - Include approximate dosage (per liter of water)
   - ALWAYS include safety precautions:
       • wear gloves and mask
       • do not spray in strong wind
       • avoid overdosing
       • follow waiting period before harvest

3. Language:
   - Simple English
   - Short sentences
   - No technical jargon

Return ONLY valid JSON in this exact format:
{{
  "problem": "...",
  "occurrence": "...",
  "natural_remedies": [
    "...",
    "..."
  ],
  "chemical_remedies": [
    "...",
    "..."
  ],
  "additional_advice": "..."
}}
"""

    for attempt in range(3):
        try:
            logger.info(f"Gemini attempt {attempt + 1}/3")

            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            text = response.text.strip()

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                import re
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    return json.loads(match.group())

                raise ValueError("Invalid JSON from Gemini")

        except Exception as e:
            logger.error(f"Gemini error (attempt {attempt + 1}): {e}")
            time.sleep(3)

    logger.warning("Gemini failed, using fallback")
    return _get_fallback_solution(crop, pest)

# --------------------------------------------------
# Temperature Scaling for Calibration
# --------------------------------------------------
class TemperatureScaling:
    def __init__(self):
        self.temperature = 1.0
    
    def calibrate(self, logits, labels, max_iter=50, lr=0.01):
        """Calibrate temperature on validation set"""
        temperature = torch.nn.Parameter(torch.ones(1) * 1.5)
        optimizer = torch.optim.LBFGS([temperature], lr=lr, max_iter=max_iter)
        
        def eval_loss():
            optimizer.zero_grad()
            loss = torch.nn.functional.cross_entropy(logits / temperature, labels)
            loss.backward()
            return loss
        
        optimizer.step(eval_loss)
        self.temperature = temperature.item()
        return self.temperature
    
    def apply(self, logits):
        """Apply temperature scaling to logits"""
        return torch.nn.functional.softmax(logits / self.temperature, dim=1)

# --------------------------------------------------
# Uncertainty Detection
# --------------------------------------------------
def calculate_entropy(probs):
    """Calculate entropy for uncertainty estimation"""
    return -torch.sum(probs * torch.log(probs + 1e-8), dim=1)

def is_uncertain(probs, confidence_threshold=0.7, entropy_threshold=1.0):
    """Determine if prediction is uncertain"""
    max_prob = torch.max(probs, dim=1)[0]
    entropy = calculate_entropy(probs)
    
    return (max_prob < confidence_threshold) or (entropy > entropy_threshold)

# --------------------------------------------------
# Enhanced Prediction with Calibration
# --------------------------------------------------
def get_calibrated_prediction(model, image: Image.Image, class_names: list, temperature_scaler=None):
    """Get prediction with calibrated confidence"""
    try:
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),  # Added horizontal flip
            transforms.RandomRotation(degrees=15),  # Added random rotation
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        img_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            logits = model(img_tensor)
            
            if temperature_scaler:
                probs = temperature_scaler.apply(logits)
            else:
                probs = torch.nn.functional.softmax(logits, dim=1)
            
            max_prob, predicted = torch.max(probs, 1)
            idx = predicted.item()
            confidence = max_prob.item()
            
            # Calculate uncertainty
            uncertain = is_uncertain(probs)
            entropy = calculate_entropy(probs).item()

        return {
            'class': class_names[idx] if idx < len(class_names) else class_names[0],
            'confidence': confidence,
            'uncertain': uncertain.item() if torch.is_tensor(uncertain) else uncertain,
            'entropy': entropy,
            'all_probs': probs.squeeze().tolist()
        }

    except Exception as e:
        logger.error(f"Calibrated prediction error: {e}")
        return {
            'class': class_names[0] if class_names else "unknown",
            'confidence': 0.0,
            'uncertain': True,
            'entropy': 2.0,
            'all_probs': []
        }

# --------------------------------------------------
# Intelligent Decision Making
# --------------------------------------------------
def make_intelligent_decision(pest_result, disease_result, crop):
    """Make intelligent decision between pest and disease predictions"""
    
    # PRIORITY 1: If disease model detects a specific disease (not healthy), strongly prefer it
    disease_class = disease_result['class'].lower()
    if 'healthy' not in disease_class:
        disease_conf = disease_result['confidence']
        pest_conf = pest_result['confidence']
        
        # Disease detected with reasonable confidence - prefer disease over pest
        if disease_conf > 0.5:
            return {
                'decision': 'disease',
                'primary_prediction': disease_result,
                'confidence': disease_conf,
                'reason': f'Disease model detected specific disease: {disease_result["class"]}',
                'requires_review': disease_result.get('uncertain', False)
            }
    
    # PRIORITY 2: If both uncertain, flag for review
    if pest_result.get('uncertain', False) and disease_result.get('uncertain', False):
        return {
            'decision': 'uncertain',
            'primary_prediction': None,
            'confidence': 0.0,
            'reason': 'Both pest and disease predictions are uncertain',
            'requires_review': True
        }
    
    # PRIORITY 3: If disease says healthy, check pest
    if 'healthy' in disease_class:
        if pest_result['confidence'] > 0.7:
            return {
                'decision': 'pest',
                'primary_prediction': pest_result,
                'confidence': pest_result['confidence'],
                'reason': 'Crop appears healthy, pest detected with high confidence',
                'requires_review': pest_result.get('uncertain', False)
            }
    
    # PRIORITY 4: Compare confidences with large margin favoring disease
    pest_conf = pest_result['confidence']
    disease_conf = disease_result['confidence']
    
    # Strongly favor disease model for disease detection
    if disease_conf > 0.4 and 'healthy' not in disease_class:
        return {
            'decision': 'disease',
            'primary_prediction': disease_result,
            'confidence': disease_conf,
            'reason': f'Disease model detected: {disease_result["class"]}',
            'requires_review': disease_conf < 0.6
        }
    
    # Only use pest if disease confidence is very low
    if pest_conf > disease_conf + 0.3:
        return {
            'decision': 'pest',
            'primary_prediction': pest_result,
            'confidence': pest_conf,
            'reason': f'Pest confidence significantly higher',
            'requires_review': True
        }
    
    # Default: prefer disease model
    return {
        'decision': 'disease',
        'primary_prediction': disease_result,
        'confidence': disease_conf,
        'reason': 'Defaulting to disease model for crop-specific analysis',
        'requires_review': True
    }

# --------------------------------------------------
# Fallback Advisory
# --------------------------------------------------
def _get_fallback_solution(crop: str, pest: str) -> dict:
    return {
        "problem": f"{pest} is affecting {crop} and can reduce yield if not managed early.",
        "occurrence": "This problem usually increases during humid or rainy conditions.",
        "natural_remedies": [
            "Remove and destroy infected plant parts from the field.",
            "Spray neem oil at 3 ml per liter of water every 7 days.",
            "Maintain proper plant spacing and avoid water stagnation.",
            "Keep the field clean and free from weeds."
        ],
        "chemical_remedies": [
            "Spray Mancozeb 75% WP at 2.5 grams per liter of water.",
            "If problem is severe, use Propiconazole 25% EC at 1 ml per liter.",
            "Wear gloves and mask during spraying.",
            "Do not harvest the crop for at least 7 days after spraying."
        ],
        "additional_advice": (
            "Check the field weekly. Early treatment gives better control. "
            "Consult local agriculture officers for region-specific guidance."
        )
    }

# Add a function to calculate health status based on analysis results
def calculate_health_status(pest_result, disease_result):
    if not pest_result and not disease_result:
        return "Healthy"

    pest_conf = pest_result['confidence'] if pest_result else 0
    disease_conf = disease_result['confidence'] if disease_result else 0

    if pest_conf > 0.8 or disease_conf > 0.8:
        return "Bad"
    elif pest_conf > 0.5 or disease_conf > 0.5:
        return "Average"
    else:
        return "Good"
