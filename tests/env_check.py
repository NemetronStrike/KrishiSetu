#!/usr/bin/env python3
"""
Environment Check Script for KrishiSetu
Verifies all requirements are met for integration testing
"""

import os
import sys
import subprocess
import importlib

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} (not installed)")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} (missing: {filepath})")
        return False

def check_node_npm():
    """Check Node.js and npm"""
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        
        if node_result.returncode == 0 and npm_result.returncode == 0:
            print(f"✅ Node.js {node_result.stdout.strip()}")
            print(f"✅ npm {npm_result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js or npm not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js or npm not found")
        return False

def check_env_file():
    """Check .env file and GEMINI_API_KEY"""
    env_path = os.path.join("backend", ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            if "GEMINI_API_KEY" in content:
                print("✅ .env file with GEMINI_API_KEY")
                return True
            else:
                print("❌ .env file missing GEMINI_API_KEY")
                return False
    else:
        print("❌ .env file not found")
        return False

def main():
    """Run all environment checks"""
    print("🌾 KrishiSetu Environment Check")
    print("=" * 40)
    
    checks_passed = 0
    total_checks = 0
    
    # Python version
    total_checks += 1
    if check_python_version():
        checks_passed += 1
    
    # Python packages
    packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('torch', 'torch'),
        ('torchvision', 'torchvision'),
        ('PIL', 'PIL'),
        ('google-generativeai', 'google.generativeai'),
        ('python-dotenv', 'dotenv'),
        ('requests', 'requests')
    ]
    
    for package_name, import_name in packages:
        total_checks += 1
        if check_package(package_name, import_name):
            checks_passed += 1
    
    # Node.js and npm
    total_checks += 1
    if check_node_npm():
        checks_passed += 1
    
    # Files
    files_to_check = [
        ("backend/main.py", "Backend main file"),
        ("backend/utils.py", "Backend utils file"),
        ("backend/model/pest_model_b0.pth", "Pest classification model"),
        ("backend/model/pest_model_b0_def.py", "Model definition"),
        ("frontend/package.json", "Frontend package.json"),
        ("frontend/src/App.tsx", "Frontend App component")
    ]
    
    for filepath, description in files_to_check:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1
    
    # Environment file
    total_checks += 1
    if check_env_file():
        checks_passed += 1
    
    print("=" * 40)
    print(f"Checks passed: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 Environment is ready for integration testing!")
        print("\nNext steps:")
        print("1. Run: python test_integration.py")
        print("2. Or run: start_integration_test.bat")
    else:
        print("❌ Environment setup incomplete.")
        print("\nTo fix missing packages:")
        print("pip install fastapi uvicorn torch torchvision pillow python-dotenv requests python-multipart pydantic google-generativeai efficientnet_pytorch")
        print("\nTo fix missing .env file:")
        print("Create backend/.env with: GEMINI_API_KEY=your_api_key_here")

if __name__ == "__main__":
    main()