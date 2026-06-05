@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "node_modules\" (
    echo 首次运行，正在安装依赖...
    call npm install
    if errorlevel 1 exit /b 1
)

echo 启动前端: http://localhost:5173 (端口被占用时会自动切换)
echo API 代理目标见 .env.development，当前需后端运行在 8000
call npm run dev
