#!/usr/bin/env python3
"""
Verification script for Construction Safety AI project structure and key files.
"""

import sys
from pathlib import Path


def check_file(filepath: str, description: str) -> bool:
    if Path(filepath).exists():
        print(f"[OK] {description}")
        return True
    print(f"[XX] {description} - MISSING ({filepath})")
    return False


def check_directory(dirpath: str, description: str) -> bool:
    if Path(dirpath).is_dir():
        print(f"[OK] {description}")
        return True
    print(f"[XX] {description} - MISSING ({dirpath})")
    return False


def main():
    print("\n" + "=" * 60)
    print("Construction Safety AI - Project Verification")
    print("=" * 60 + "\n")

    all_good = True

    print("Backend Files:")
    all_good &= check_file("backend.py", "FastAPI application")
    all_good &= check_file("config.py", "Application configuration")
    all_good &= check_file("requirements-api.txt", "Python dependencies")
    all_good &= check_directory("core", "Core modules directory")
    for mod in (
        "core/__init__.py",
        "core/detector.py",
        "core/label_mapping.py",
        "core/legal_assessment.py",
        "core/legal_references.py",
        "core/report_generator.py",
        "core/risk_engine.py",
        "core/visualizer.py",
    ):
        all_good &= check_file(mod, f"  Module: {mod}")

    print("\nFrontend Files:")
    all_good &= check_directory("frontend", "React application root")
    all_good &= check_file("frontend/package.json", "Node dependencies")
    all_good &= check_file("frontend/vite.config.js", "Vite configuration")
    all_good &= check_file("frontend/index.html", "HTML entry point")
    all_good &= check_file("frontend/src/App.jsx", "Main React component")
    all_good &= check_file("frontend/src/App.css", "Application stylesheet")
    all_good &= check_file("frontend/src/main.jsx", "React entry point")
    all_good &= check_directory("frontend/src/components", "React components directory")
    for comp in (
        "ConfigPanel.jsx",
        "ImageUploader.jsx",
        "KPICard.jsx",
        "DetectionResults.jsx",
        "HazardRegister.jsx",
        "ReportGenerator.jsx",
        "SiteProfile.jsx",
        "LegalAssessment.jsx",
    ):
        all_good &= check_file(f"frontend/src/components/{comp}", f"  Component: {comp}")

    print("\nTests, Scripts & Assets:")
    all_good &= check_directory("tests", "Test suite directory")
    all_good &= check_file("tests/test_detection.py", "API & detection tests")
    all_good &= check_file("tests/test_legal_assessment.py", "Legal assessment tests")
    all_good &= check_file("run-full-stack.bat", "Windows startup script")
    all_good &= check_file("run-full-stack.sh", "macOS/Linux startup script")
    all_good &= check_file("README.md", "Project README")
    all_good &= check_file("models/weights/best.pt", "Trained YOLO weights")
    all_good &= check_file("samples/sample_site.jpg", "Sample site image")

    print("\n" + "=" * 60)
    if all_good:
        print("[OK] All repository structure checks passed!")
        print("=" * 60 + "\n")
    else:
        print("[XX] Some verification checks failed!")
        print("=" * 60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
