@echo off
setlocal EnableDelayedExpansion

echo Starting Gaussian Rendering...
echo.

REM --------------------------------------------------
REM Pfade & Environment
REM --------------------------------------------------
set "ROOT=C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1"
set "OUTDIR=%ROOT%\gaussian-splatting\output"

cd /d "%ROOT%\gaussian-splatting"
CALL C:\Users\tilma\miniconda3\Scripts\activate.bat gaussian_splatting

REM --------------------------------------------------
REM Argument pruefen
REM --------------------------------------------------
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

REM --------------------------------------------------
REM Ordner sammeln + Groessen berechnen
REM --------------------------------------------------
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

REM --------------------------------------------------
REM Anzeige
REM --------------------------------------------------
echo Gefundene Ordner:
echo --------------------------------------------------
for /L %%I in (1,1,%INDEX%) do (
    call echo %%I^) %%FOLDER[%%I]%% [%%SIZE[%%I]%% Bytes]
)
echo --------------------------------------------------

@REM REM --------------------------------------------------
@REM REM Nutzerauswahl
@REM REM --------------------------------------------------
@REM set /p CHOICE=Bitte Nummer auswaehlen: 

@REM if not defined FOLDER[%CHOICE%] (
@REM     echo Ungueltige Auswahl.
@REM     goto :EOF
@REM )

@REM set "SELECTED_FOLDER=!FOLDER[%CHOICE%]!"

@REM echo.
@REM echo Ausgewaehlter Ordner:
@REM echo %SELECTED_FOLDER%
@REM echo.

REM --------------------------------------------------
REM Groessten Ordner automatisch auswaehlen
REM --------------------------------------------------
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


for %%I in ("%SELECTED_FOLDER%") do (
    set "PARENT_DIR=%%~dpI"
    set "OLD_NAME=%%~nxI"
)


set "NEW_FOLDER=%PARENT_DIR%%NEW_NAME%"


@REM if exist "%NEW_FOLDER%" (
@REM echo FEHLER: Zielordner existiert bereits:
@REM echo %NEW_FOLDER%
@REM goto :EOF
@REM )


echo Benenne Ordner um:
echo %SELECTED_FOLDER%
echo -> %NEW_FOLDER%

if not exist "%SELECTED_FOLDER%" (
    ren "%SELECTED_FOLDER%" "%NEW_NAME%"
)

REM Pfad aktualisieren
set "SELECTED_FOLDER=%NEW_FOLDER%"

REM --------------------------------------------------
REM Training
REM --------------------------------------------------
echo Starte Training...
echo Selected Folder: %SELECTED_FOLDER%
python train.py -s %BASE_DIR%

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

"%ROOT%\gaussian-splatting\SIBR_viewers\install\bin\SIBR_gaussianViewer_app_rwdi.exe" ^
    -m "%OUTDIR%\%NewestFolder%"

endlocal