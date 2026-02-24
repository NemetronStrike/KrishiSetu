#!/usr/bin/env python3
"""
Test Script for Intelligent Decision Making System
Evaluates how well the system handles pest vs disease confusion
"""

import torch
import os
from PIL import Image
from utils import (load_pest_model, load_crop_model, get_calibrated_prediction, 
                   make_intelligent_decision, TemperatureScaling)
import json

def test_decision_system():
    """Test the intelligent decision system with sample predictions"""
    
    # Mock test cases representing common confusion scenarios
    test_cases = [
        {
            "name": "Clear disease case",
            "pest_result": {"class": "aphids", "confidence": 0.3, "uncertain": True, "entropy": 1.8},
            "disease_result": {"class": "Tomato___Early_blight", "confidence": 0.85, "uncertain": False, "entropy": 0.4},
            "crop": "tomato",
            "expected": "disease"
        },
        {
            "name": "Clear pest case", 
            "pest_result": {"class": "bollworm", "confidence": 0.9, "uncertain": False, "entropy": 0.2},
            "disease_result": {"class": "Tomato___healthy", "confidence": 0.7, "uncertain": False, "entropy": 0.6},
            "crop": "tomato",
            "expected": "pest"
        },
        {
            "name": "Both uncertain",
            "pest_result": {"class": "mites", "confidence": 0.4, "uncertain": True, "entropy": 1.9},
            "disease_result": {"class": "Rice___Brown_spot", "confidence": 0.45, "uncertain": True, "entropy": 1.7},
            "crop": "rice", 
            "expected": "uncertain"
        },
        {
            "name": "Close confidences",
            "pest_result": {"class": "armyworm", "confidence": 0.72, "uncertain": False, "entropy": 0.8},
            "disease_result": {"class": "Corn_(maize)___Northern_Leaf_Blight", "confidence": 0.75, "uncertain": False, "entropy": 0.7},
            "crop": "corn",
            "expected": "requires_review"
        },
        {
            "name": "Healthy crop with pest",
            "pest_result": {"class": "grasshopper", "confidence": 0.8, "uncertain": False, "entropy": 0.5},
            "disease_result": {"class": "Wheat___healthy", "confidence": 0.9, "uncertain": False, "entropy": 0.3},
            "crop": "wheat",
            "expected": "pest"
        }
    ]
    
    print("Testing Intelligent Decision Making System")
    print("=" * 50)
    
    correct_decisions = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Pest: {test_case['pest_result']['class']} (conf: {test_case['pest_result']['confidence']:.2f})")
        print(f"Disease: {test_case['disease_result']['class']} (conf: {test_case['disease_result']['confidence']:.2f})")
        
        decision = make_intelligent_decision(
            test_case['pest_result'], 
            test_case['disease_result'], 
            test_case['crop']
        )
        
        print(f"Decision: {decision['decision']}")
        print(f"Confidence: {decision['confidence']:.3f}")
        print(f"Reason: {decision['reason']}")
        print(f"Requires Review: {decision.get('requires_review', False)}")
        
        # Check if decision matches expectation
        if test_case['expected'] == 'requires_review':
            is_correct = decision.get('requires_review', False)
        else:
            is_correct = decision['decision'] == test_case['expected']
        
        if is_correct:
            correct_decisions += 1
            print("✅ CORRECT")
        else:
            print(f"❌ INCORRECT (expected: {test_case['expected']})")
    
    print(f"\n" + "=" * 50)
    print(f"Results: {correct_decisions}/{total_tests} correct ({correct_decisions/total_tests*100:.1f}%)")
    
    return correct_decisions / total_tests

def test_uncertainty_thresholds():
    """Test different uncertainty thresholds"""
    print("\n\nTesting Uncertainty Thresholds")
    print("=" * 50)
    
    # Test with different confidence levels
    confidence_levels = [0.3, 0.5, 0.7, 0.85, 0.95]
    
    for conf in confidence_levels:
        # Mock high entropy (uncertain) case
        mock_probs = torch.tensor([[conf, (1-conf)/8, (1-conf)/8, (1-conf)/8, (1-conf)/8, 
                                   (1-conf)/8, (1-conf)/8, (1-conf)/8, (1-conf)/8]])
        
        from utils import is_uncertain, calculate_entropy
        entropy = calculate_entropy(mock_probs).item()
        uncertain = is_uncertain(mock_probs)
        
        print(f"Confidence: {conf:.2f}, Entropy: {entropy:.3f}, Uncertain: {uncertain}")

def benchmark_performance():
    """Benchmark the decision system performance"""
    print("\n\nBenchmarking Performance")
    print("=" * 50)
    
    import time
    
    # Create mock data for performance testing
    pest_result = {"class": "aphids", "confidence": 0.7, "uncertain": False, "entropy": 0.8}
    disease_result = {"class": "Tomato___Early_blight", "confidence": 0.75, "uncertain": False, "entropy": 0.7}
    
    # Time 1000 decisions
    start_time = time.time()
    for _ in range(1000):
        decision = make_intelligent_decision(pest_result, disease_result, "tomato")
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 1000 * 1000  # Convert to milliseconds
    print(f"Average decision time: {avg_time:.3f} ms")
    print(f"Decisions per second: {1000/(end_time - start_time):.0f}")

if __name__ == "__main__":
    # Run all tests
    accuracy = test_decision_system()
    test_uncertainty_thresholds()
    benchmark_performance()
    
    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print(f"Decision accuracy: {accuracy*100:.1f}%")
    print("System ready for deployment!" if accuracy > 0.8 else "Consider tuning thresholds")