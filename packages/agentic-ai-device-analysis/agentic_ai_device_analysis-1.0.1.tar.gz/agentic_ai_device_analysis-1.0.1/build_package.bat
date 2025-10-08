@echo off
echo Building Agentic AI Device Analysis Package...
echo.

echo Step 1: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info

echo Step 2: Installing build dependencies...
pip install --upgrade build twine wheel

echo Step 3: Building the package...
python -m build

echo Step 4: Checking the built package...
twine check dist/*

echo.
echo Package built successfully!
echo Files created in dist/:
dir dist

echo.
echo To install locally: pip install dist\agentic_ai_device_analysis-1.0.1-py3-none-any.whl
echo To upload to PyPI: twine upload dist/*
echo.
pause