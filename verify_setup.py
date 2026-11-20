#!/usr/bin/env python3
"""
Verification script for React + FastAPI conversion
Checks that all required files are in place and dependencies are installed
"""

import os
import sys
from pathlib import Path

class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    BLUE = ''
    RESET = ''

def check_file(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"[OK] {description}")
        return True
    else:
        print(f"[XX] {description} - MISSING")
        return False

def check_directory(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).exists():
        print(f"[OK] {description}")
        return True
    else:
        print(f"[XX] {description} - MISSING")
        return False

def main():
    print("\n" + "="*60)
    print("React + FastAPI Conversion Verification")
    print("="*60 + "\n")

    all_good = True

    # Backend Files
    print("Backend Files:")
    all_good &= check_file("backend.py", "FastAPI application")
    all_good &= check_file("requirements-api.txt", "Python dependencies")
    
    # Core modules should still exist
    all_good &= check_directory("core", "Core detection modules")
    all_good &= check_file("core/detector.py", "YOLOv8 detector")
    all_good &= check_file("core/risk_engine.py", "Risk assessment engine")
    all_good &= check_file("core/visualizer.py", "Image visualizer")
    all_good &= check_file("core/report_generator.py", "Report generator")

    print()

    # Frontend Files
    print("Frontend Files:")
    all_good &= check_directory("frontend", "React application root")
    all_good &= check_file("frontend/package.json", "Node dependencies")
    all_good &= check_file("frontend/vite.config.js", "Vite configuration")
    all_good &= check_file("frontend/index.html", "HTML entry point")
    all_good &= check_file("frontend/src/App.jsx", "Main React component")
    all_good &= check_file("frontend/src/main.jsx", "React entry point")
    all_good &= check_directory("frontend/src/components", "React components directory")
    
    # Check key components
    components = [
        "ConfigPanel.jsx",
        "ImageUploader.jsx",
        "KPICard.jsx",
        "DetectionResults.jsx",
        "RiskMatrix.jsx",
        "HazardRegister.jsx",
        "ReportGenerator.jsx"
    ]
    for comp in components:
        all_good &= check_file(f"frontend/src/components/{comp}", f"  Component: {comp}")

    print()

    # Startup Scripts
    print("Startup Scripts:")
    all_good &= check_file("run-full-stack.bat", "Windows startup script")
    all_good &= check_file("run-full-stack.sh", "macOS/Linux startup script")

    print()

    # Documentation
    print("Documentation:")
    all_good &= check_file("REACT_README.md", "Complete React documentation")
    all_good &= check_file("QUICKSTART.md", "Quick start guide")
    all_good &= check_file("MIGRATION_GUIDE.md", "Streamlit to React migration guide")
    all_good &= check_file("CONVERSION_SUMMARY.md", "Conversion summary")

    print()

    # Configuration
    print("Configuration:")
    all_good &= check_file("config.py", "Application configuration")
    all_good &= check_directory("models", "Models directory")
    all_good &= check_directory("models/weights", "Model weights directory")

    print()

    # Summary
    print("=" * 60)
    
    if all_good:
        print("[OK] All verification checks passed!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Install Python dependencies:")
        print("   pip install -r requirements-api.txt")
        print("\n2. Install Node dependencies:")
        print("   cd frontend && npm install")
        print("\n3. Start the application:")
        print("   Windows: run-full-stack.bat")
        print("   macOS/Linux: ./run-full-stack.sh")
        print("\n4. Open browser:")
        print("   http://localhost:3000")
        print("\nFor detailed documentation, see:")
        print("   - QUICKSTART.md (5-minute setup)")
        print("   - REACT_README.md (full documentation)")
        print("   - MIGRATION_GUIDE.md (Streamlit comparison)")
        print()
    else:
        print("[XX] Some verification checks failed!")
        print("=" * 60)
        print("\nPlease check the missing files listed above.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
