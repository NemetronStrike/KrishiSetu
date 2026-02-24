#!/usr/bin/env python3
"""
Temperature Calibration Script for KrishiSetu Models
Run this on validation data to calibrate model confidences
"""

import torch
import os
from PIL import Image
from torchvision import transforms
from utils import load_pest_model, load_crop_model, TemperatureScaling
import json

def load_validation_data(val_dir, class_names):
    """Load validation images and labels"""
    images = []
    labels = []
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    for class_idx, class_name in enumerate(class_names):
        class_dir = os.path.join(val_dir, class_name)
        if os.path.exists(class_dir):
            for img_file in os.listdir(class_dir)[:20]:  # Limit to 20 images per class
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(class_dir, img_file)
                    try:
                        image = Image.open(img_path).convert('RGB')
                        img_tensor = transform(image)
                        images.append(img_tensor)
                        labels.append(class_idx)
                    except Exception as e:
                        print(f"Error loading {img_path}: {e}")
    
    return torch.stack(images), torch.tensor(labels)

def calibrate_model(model, val_images, val_labels, model_name):
    """Calibrate a single model"""
    print(f"Calibrating {model_name}...")
    
    # Get logits for validation set
    model.eval()
    with torch.no_grad():
        logits = model(val_images)
    
    # Calibrate temperature
    temp_scaler = TemperatureScaling()
    temperature = temp_scaler.calibrate(logits, val_labels)
    
    print(f"Optimal temperature for {model_name}: {temperature:.3f}")
    return temperature

def main():
    """Main calibration function"""
    
    # Configuration
    PEST_MODEL_PATH = os.path.join("model", "pest_model_b0.pth")
    PEST_CLASSES = ['aphids', 'armyworm', 'bollworm', 'cutworm', 'grasshopper',
                   'leafhoppers', 'mites', 'stemborer', 'weevil']
    
    CROP_MODELS = {
        'rice': {
            'model_path': os.path.join("model", "rice_disease_model.pth"),
            'classes': ['Rice___Bacterial_leaf_blight', 'Rice___Brown_spot', 'Rice___Leaf_smut', 'Rice___healthy']
        },
        'tomato': {
            'model_path': os.path.join("model", "tomato_disease_model.pth"),
            'classes': ['Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 
                       'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 
                       'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']
        }
    }
    
    calibration_results = {}
    
    # Calibrate pest model (if validation data available)
    val_pest_dir = "validation_data/pest"  # Update this path
    if os.path.exists(val_pest_dir):
        try:
            pest_model = load_pest_model(PEST_MODEL_PATH)
            val_images, val_labels = load_validation_data(val_pest_dir, PEST_CLASSES)
            
            if len(val_images) > 0:
                temperature = calibrate_model(pest_model, val_images, val_labels, "pest_model")
                calibration_results['pest'] = temperature
            else:
                print("No validation images found for pest model")
        except Exception as e:
            print(f"Error calibrating pest model: {e}")
    
    # Calibrate crop disease models
    for crop, config in CROP_MODELS.items():
        val_crop_dir = f"validation_data/{crop}"  # Update this path
        if os.path.exists(val_crop_dir):
            try:
                crop_model = load_crop_model(config['model_path'], len(config['classes']))
                val_images, val_labels = load_validation_data(val_crop_dir, config['classes'])
                
                if len(val_images) > 0:
                    temperature = calibrate_model(crop_model, val_images, val_labels, f"{crop}_model")
                    calibration_results[crop] = temperature
                else:
                    print(f"No validation images found for {crop} model")
            except Exception as e:
                print(f"Error calibrating {crop} model: {e}")
    
    # Save calibration results
    with open('calibration_results.json', 'w') as f:
        json.dump(calibration_results, f, indent=2)
    
    print("\nCalibration complete! Results saved to calibration_results.json")
    print("Update your main.py to use these temperature values:")
    for model_name, temp in calibration_results.items():
        print(f"  {model_name}: {temp:.3f}")

if __name__ == "__main__":
    main()