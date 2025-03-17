@echo off
setlocal enabledelayedexpansion

:: Percorsi ai file e strumenti
set ENERGYBRIDGE=energibridge\energibridge.exe
set GRADLE_CMD=gradle
set OUTPUT_FILE=results.csv
set TEMP_FILE=temp_tasks.txt

 Pulizia del file temporaneo
if exist %TEMP_FILE% del %TEMP_FILE%

:: Estrai la sequenza dei task con --dry-run
echo Rilevamento task da 'gradle build --rerun-tasks --dry-run'...
call %GRADLE_CMD% build --rerun-tasks --dry-run > %TEMP_FILE%

if not exist %TEMP_FILE% (
    echo Errore: il file %TEMP_FILE% non è stato creato.
    exit /b 1
)

echo Contenuto di %TEMP_FILE%:
type %TEMP_FILE%
echo Fine del contenuto di %TEMP_FILE%

:: Reset variabile TASKS
set TASKS=

:: Estrai i task dall'output e rimuovi il prefisso ":"
for /f "tokens=1 delims= " %%T in ('findstr /R /C:"^:.* SKIPPED" %TEMP_FILE%') do (
    echo %%T | findstr /R /C:"^:.* SKIPPED" > nul
    set "TASK=%%T"
    set TASK=!TASK:~1!  
    echo Trovato task: !TASK!
    set TASKS=!TASKS! !TASK!
)

:: Loop attraverso i task estratti
for %%T in (!TASKS!) do (
    echo Running step: %%T
    %ENERGYBRIDGE% -o %OUTPUT_FILE% --summary cmd /c "%GRADLE_CMD% %%T"
    echo Finished step: %%T
)

:: Pulizia finale
::del %TEMP_FILE%
echo Analisi completata.
exit /b