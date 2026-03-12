@echo off

cd C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1

@REM call .venv\Scripts\activate.bat

C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1\.venv\Scripts\python.exe .\src\execute_pipeline.py --noimport --noscale -s res\evaluation-research\test11\xfeat --top_k 4096
C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1\.venv\Scripts\python.exe .\src\execute_pipeline.py --noimport --noscale --sift -s res\evaluation-research\test11\sift --top_k 4096