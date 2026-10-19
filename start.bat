@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

where py >nul 2>&1 && set "PY=py -3"
if not defined PY set "PY=python"

if not exist "venv\Scripts\python.exe" (
  echo [Agora] 创建虚拟环境...
  %PY% -m venv venv
  if errorlevel 1 (
    echo 未找到可用的 Python。请先安装 Python 3，并确保 py 或 python 在 PATH 中。
    pause
    exit /b 1
  )
)

fc /b requirements.txt "venv\.reqs.stamp" >nul 2>&1
if errorlevel 1 (
  echo [Agora] 安装依赖...
  venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 (
    echo 依赖安装失败。
    pause
    exit /b 1
  )
  copy /y requirements.txt "venv\.reqs.stamp" >nul
)

echo [Agora] 启动 http://localhost:5000
echo 关闭此窗口即停止服务。
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:5000"
venv\Scripts\python.exe app.py
if errorlevel 1 pause
