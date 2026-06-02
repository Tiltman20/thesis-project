@echo off

echo Creating virtual environment...

python -m venv .venv
call .venv\Scripts\activate.bat
pip install opencv-python
pip install scikit-image

echo Running evaluation script...
python run_evaluation.py

deactivate