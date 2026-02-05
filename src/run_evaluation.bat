@echo off

@REM Build venv with requirements:
echo Creating virtual environment...

python -m venv .venv
call .venv\Scripts\activate.bat
pip install opencv-python
pip install scikit-image

@REM Run evaluation script:
echo Running evaluation script...
python run_evaluation.py

@REM Deactivate and delete venv
deactivate