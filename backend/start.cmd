@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".env" (
    if exist ".env.example" (
        echo 未找到 .env，已从 .env.example 复制
        copy /y ".env.example" ".env" >nul
    ) else (
        echo 错误: 缺少 .env 与 .env.example
        exit /b 1
    )
)

set "API_HOST=0.0.0.0"
set "API_PORT=8000"
for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do (
    if /i "%%~A"=="API_HOST" set "API_HOST=%%~B"
    if /i "%%~A"=="API_PORT" set "API_PORT=%%~B"
)

if not exist ".venv\Scripts\python.exe" (
    echo 首次运行，正在创建虚拟环境并安装依赖...
    py -3 -m venv .venv
    if errorlevel 1 (
        python -m venv .venv
        if errorlevel 1 exit /b 1
    )
    call ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 exit /b 1
    call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 exit /b 1
)

echo 正在执行数据库迁移 (alembic upgrade head)...
call ".venv\Scripts\python.exe" -m alembic upgrade head
if errorlevel 1 (
    echo 数据库迁移失败，请检查 MySQL 是否已启动及 .env 中的 DATABASE_URL
    exit /b 1
)

echo 启动后端: http://127.0.0.1:%API_PORT%
echo API 文档: http://127.0.0.1:%API_PORT%/docs
echo 前端代理默认指向 http://localhost:8000，若修改 API_PORT 请同步 frontend/.env.development
call ".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host %API_HOST% --port %API_PORT%
