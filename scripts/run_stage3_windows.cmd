@echo off
setlocal
pushd "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
    echo Expected the existing .venv environment. See README.md for a fresh clone.
    popd
    exit /b 2
)
set "OMP_NUM_THREADS=1"
set "MKL_NUM_THREADS=1"
set "OPENBLAS_NUM_THREADS=1"
set "CUBLAS_WORKSPACE_CONFIG=:4096:8"
if "%~1"=="" (
    ".venv\Scripts\python.exe" "scripts\stage3.py" verify
) else (
    ".venv\Scripts\python.exe" "scripts\stage3.py" %*
)
set "stage3_exit=%ERRORLEVEL%"
popd
exit /b %stage3_exit%
