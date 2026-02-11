@echo off
REM Batch MIDI processing script for Windows

setlocal enabledelayedexpansion

set "INPUT_DIR=%~1"
if "%INPUT_DIR%"==" set "INPUT_DIR=."

set "OUTPUT_DIR=%~2"
if "%OUTPUT_DIR%"=="" set "OUTPUT_DIR=processed"

echo MIDI Clean V3 - Batch Processor
echo ================================
echo Input:  %INPUT_DIR%
echo Output: %OUTPUT_DIR%
echo.

REM Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

set count=0

REM Process each MIDI file
for %%f in ("%INPUT_DIR%\*.mid" "%INPUT_DIR%\*.midi") do (
    set /a count+=1
    echo [!count!] Processing: %%~nxf
    
    python midi_clean.py "%%f" "%OUTPUT_DIR%\%%~nxf" ^
        --quantize 1/16 ^
        --straighten ^
        --vel-scale 0.9 ^
        --dedupe
    
    echo.
)

echo.
echo Batch processing complete
echo   Processed: !count! files
echo   Output: %OUTPUT_DIR%\

pause
