@echo off
setlocal EnableDelayedExpansion

echo Starting Gaussian Rendering...
echo.

set "ROOT=C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1"
set "OUTDIR=%ROOT%\gaussian-splatting\output"

cd /d "%ROOT%\gaussian-splatting"
CALL C:\Users\tilma\miniconda3\Scripts\activate.bat gaussian_splatting

if "%~1"=="" (
    echo FEHLER: Kein Pfad uebergeben.
    echo Aufruf: render_gaussians.bat ^<Scene-Pfad^>
    goto :EOF
)

set "BASE_DIR=%ROOT%\%1"

echo "BaseDir: %BASE_DIR%"

if not exist "%BASE_DIR%\sparse" (
    echo FEHLER: Pfad existiert nicht:
    echo %BASE_DIR%
    goto :EOF
)

echo Suche Ordner in:
echo %BASE_DIR%
echo.

set INDEX=0

for /d %%D in ("%BASE_DIR%\sparse\*") do (
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

echo Gefundene Ordner:
echo --------------------------------------------------
for /L %%I in (1,1,%INDEX%) do (
    call echo %%I^) %%FOLDER[%%I]%% [%%SIZE[%%I]%% Bytes]
)
echo --------------------------------------------------

set "MAX_SIZE=-1"
set "MAX_INDEX="

for /L %%I in (1,1,%INDEX%) do (
    if !SIZE[%%I]! GTR !MAX_SIZE! (
        set "MAX_SIZE=!SIZE[%%I]!"
        set "MAX_INDEX=%%I"
    )
)

if not defined MAX_INDEX (
    echo Konnte keinen groessten Ordner bestimmen.
    goto :EOF
)

set "SELECTED_FOLDER=!FOLDER[%MAX_INDEX%]!"

echo.
echo Automatisch ausgewaehlter Ordner (groesster):
echo %SELECTED_FOLDER%
echo.

echo Loesche nicht ausgewaehlte Ordner...

for /L %%I in (1,1,%INDEX%) do (
    if not "!FOLDER[%%I]!"=="%SELECTED_FOLDER%" (
        echo   Entferne: !FOLDER[%%I]!
        rmdir /s /q "!FOLDER[%%I]!"
    )
)

echo Bereinigung abgeschlossen.
echo.

set "NEW_NAME=0"


for %%I in ("%SELECTED_FOLDER%") do (
    set "PARENT_DIR=%%~dpI"
    set "OLD_NAME=%%~nxI"
)


set "NEW_FOLDER=%PARENT_DIR%%NEW_NAME%"

echo Benenne Ordner um:
echo %SELECTED_FOLDER%
echo -> %NEW_FOLDER%

if not exist "%SELECTED_FOLDER%" (
    ren "%SELECTED_FOLDER%" "%NEW_NAME%"
)

set "SELECTED_FOLDER=%NEW_FOLDER%"

echo Starte Training...
echo Selected Folder: %SELECTED_FOLDER%
python train.py -s %BASE_DIR%

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

python render.py -m "%OUTDIR%\%NewestFolder%"

"%ROOT%\gaussian-splatting\SIBR_viewers\install\bin\SIBR_gaussianViewer_app_rwdi.exe" ^
    -m "%OUTDIR%\%NewestFolder%"

endlocal