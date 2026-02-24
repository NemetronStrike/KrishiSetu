#!/usr/bin/env python3
"""
KrishiSetu Integration Test Script
Tests the backend API endpoints and verifies model loading
"""

import requests
import json
import os
from PIL import Image
import io
import sys

# Test configuration
BACKEND_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_image.jpg"

def create_test_image():
    """Create a simple test image for testing"""
    # Create a simple RGB image
    img = Image.new('RGB', (224, 224), color='green')
    img.save(TEST_IMAGE_PATH)
    print(f"✓ Created test image: {TEST_IMAGE_PATH}")

def test_backend_health():
    """Test if backend server is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/docs")
        if response.status_code == 200:
            print("✓ Backend server is running")
            return True
        else:
            print(f"✗ Backend server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Backend server is not running")
        print("  Start backend with: cd backend && uvicorn main:app --reload")
        return False

def test_prediction_endpoint():
    """Test the /predict endpoint"""
    if not os.path.exists(TEST_IMAGE_PATH):
        create_test_image()
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            data = {'crop': 'tomato'}
            
            response = requests.post(f"{BACKEND_URL}/predict", files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            print("✓ Prediction endpoint working")
            print(f"  Predicted class: {result.get('predicted_class', 'N/A')}")
            print(f"  Solution keys: {list(result.get('solution', {}).keys())}")
            return True
        else:
            print(f"✗ Prediction failed with status: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Prediction test failed: {str(e)}")
        return False

def test_cors_headers():
    """Test CORS headers for frontend integration"""
    try:
        response = requests.options(f"{BACKEND_URL}/predict")
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("✓ CORS headers configured")
            return True
        else:
            print("✗ CORS headers missing")
            return False
            
    except Exception as e:
        print(f"✗ CORS test failed: {str(e)}")
        return False

def cleanup():
    """Clean up test files"""
    if os.path.exists(TEST_IMAGE_PATH):
        os.remove(TEST_IMAGE_PATH)
        print(f"✓ Cleaned up {TEST_IMAGE_PATH}")

def main():
    """Run all integration tests"""
    print("🌾 KrishiSetu Integration Test Suite")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Backend Health
    if test_backend_health():
        tests_passed += 1
    
    # Test 2: Prediction Endpoint
    if test_prediction_endpoint():
        tests_passed += 1
    
    # Test 3: CORS Configuration
    if test_cors_headers():
        tests_passed += 1
    
    print("=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Backend is ready for frontend integration.")
        print("\nNext steps:")
        print("1. Start frontend: cd frontend && npm start")
        print("2. Access app at: http://localhost:3000")
    else:
        print("❌ Some tests failed. Check the issues above.")
        if tests_passed == 0:
            print("\nTroubleshooting:")
            print("1. Make sure backend is running: cd backend && uvicorn main:app --reload")
            print("2. Check if model file exists: backend/model/pest_model_b0.pth")
            print("3. Verify .env file has GEMINI_API_KEY")
    
    cleanup()

if __name__ == "__main__":
    main()