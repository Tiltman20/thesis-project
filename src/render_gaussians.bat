@echo off
setlocal EnableDelayedExpansion

echo Starting Gaussian Rendering...
echo.

REM --------------------------------------------------
REM Pfade & Environment
REM --------------------------------------------------
set "ROOT=C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1\gaussian-splatting"
set "OUTDIR=%ROOT%\output"

cd /d "%ROOT%"
CALL C:\Users\tilma\miniconda3\Scripts\activate.bat gaussian_splatting

REM --------------------------------------------------
REM Argument pruefen
REM --------------------------------------------------
if "%~1"=="" (
    echo FEHLER: Kein Pfad uebergeben.
    echo Aufruf: render_gaussians.bat ^<Scene-Pfad^>
    goto :EOF
)

set "BASE_DIR=%~1\sparse"

if not exist "%BASE_DIR%" (
    echo FEHLER: Pfad existiert nicht:
    echo %BASE_DIR%
    goto :EOF
)

echo Suche Ordner in:
echo %BASE_DIR%
echo.

REM --------------------------------------------------
REM Ordner sammeln + Groessen berechnen
REM --------------------------------------------------
set INDEX=0

for /d %%D in ("%BASE_DIR%\*") do (
    set /a INDEX+=1
    set "FOLDER[!INDEX!]=%%~fD"

    for /f %%S in ('
        powershell -command "(Get-ChildItem -Recurse -File \"%%D\" | Measure-Object Length -Sum).Sum"
    ') do (
        set "SIZE[!INDEX!]=%%S"
    )
)

if %INDEX%==0 (
    echo Keine Unterordner gefunden.
    goto :EOF
)

REM --------------------------------------------------
REM Anzeige
REM --------------------------------------------------
echo Gefundene Ordner:
echo --------------------------------------------------
for /L %%I in (1,1,%INDEX%) do (
    call echo %%I^) %%FOLDER[%%I]%% [%%SIZE[%%I]%% Bytes]
)
echo --------------------------------------------------

REM --------------------------------------------------
REM Nutzerauswahl
REM --------------------------------------------------
set /p CHOICE=Bitte Nummer auswaehlen: 

if not defined FOLDER[%CHOICE%] (
    echo Ungueltige Auswahl.
    goto :EOF
)

set "SELECTED_FOLDER=!FOLDER[%CHOICE%]!"

echo.
echo Ausgewaehlter Ordner:
echo %SELECTED_FOLDER%
echo.

REM --------------------------------------------------
REM NICHT AUSGEWAEHLTE ORDNER LOESCHEN
REM --------------------------------------------------
echo Loesche nicht ausgewaehlte Ordner...

for /L %%I in (1,1,%INDEX%) do (
    if not "!FOLDER[%%I]!"=="%SELECTED_FOLDER%" (
        echo   Entferne: !FOLDER[%%I]!
        rmdir /s /q "!FOLDER[%%I]!"
    )
)

echo Bereinigung abgeschlossen.
echo.

REM --------------------------------------------------
REM Ausgewaehlten Ordner umbenennen
REM --------------------------------------------------
set "NEW_NAME=0"


for %%~ in ("%SELECTED_FOLDER%") do (
set "PARENT_DIR=%%~dp."
set "OLD_NAME=%%~nx."
)


set "NEW_FOLDER=%PARENT_DIR%%NEW_NAME%"


if exist "%NEW_FOLDER%" (
echo FEHLER: Zielordner existiert bereits:
echo %NEW_FOLDER%
goto :EOF
)


echo Benenne Ordner um:
echo %SELECTED_FOLDER%
echo -> %NEW_FOLDER%


ren "%SELECTED_FOLDER%" "%NEW_NAME%"


REM Pfad aktualisieren
set "SELECTED_FOLDER=%NEW_FOLDER%"

REM --------------------------------------------------
REM Training
REM --------------------------------------------------
echo Starte Training...
python train.py -s %1

REM --------------------------------------------------
REM Neuesten Output-Ordner finden
REM --------------------------------------------------
for /f "eol=| delims=" %%I in (
    'dir "%OUTDIR%" /AD /B /O-D /TW 2^>nul'
) do (
    set "NewestFolder=%%I"
    goto FoundFolder
)

echo Kein Output-Ordner gefunden!
goto :EOF

:FoundFolder
echo.
echo Neuster Output-Ordner:
echo %OUTDIR%\%NewestFolder%
echo.

REM --------------------------------------------------
REM Rendering + Viewer
REM --------------------------------------------------
python render.py -m "%OUTDIR%\%NewestFolder%"

"%ROOT%\SIBR_viewers\install\bin\SIBR_gaussianViewer_app_rwdi.exe" ^
    -m "%OUTDIR%\%NewestFolder%"

endlocal