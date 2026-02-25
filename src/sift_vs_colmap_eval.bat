@echo off

cd C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1

@REM call .venv\Scripts\activate.bat

C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1\.venv\Scripts\python.exe .\src\execute_pipeline.py --noimport --noscale -s res\evaluation-research\test8\xfeat --top_k 1024
@REM C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1\.venv\Scripts\python.exe .\src\execute_pipeline.py --noimport --noscale --sift -s res\evaluation-research\test7\sift --top_k 1024