# 前台启动 FastAPI 开发服务器，关闭此窗口即停止服务
# Windows PowerShell 5.x 需 UTF-8 BOM 保存本文件，否则中文会乱码
if ($PSVersionTable.PSVersion.Major -lt 6) {
    try { chcp 65001 | Out-Null } catch {}
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
}
Set-Location $PSScriptRoot
function Get-EnvValue {
    param(
        [string]$Key,
        [string]$Default
    )
    if (-not (Test-Path ".env")) {
        return $Default
    }
    foreach ($line in Get-Content ".env") {
        if ($line -match "^\s*$Key=(.+)$") {
            return $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return $Default
}

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "未找到 .env，已从 .env.example 复制" -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
    } else {
        Write-Host "错误: 缺少 .env 与 .env.example" -ForegroundColor Red
        exit 1
    }
}

$venvPython = Join-Path (Join-Path $PSScriptRoot ".venv") "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "首次运行，正在创建虚拟环境并安装依赖..." -ForegroundColor Yellow
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "正在执行数据库迁移 (alembic upgrade head)..." -ForegroundColor DarkGray
& $venvPython -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "数据库迁移失败，请检查 MySQL 是否已启动及 .env 中的 DATABASE_URL" -ForegroundColor Red
    exit $LASTEXITCODE
}

$apiHost = Get-EnvValue -Key "API_HOST" -Default "0.0.0.0"
$apiPort = Get-EnvValue -Key "API_PORT" -Default "8000"

Write-Host "启动后端: http://127.0.0.1:$apiPort" -ForegroundColor Green
Write-Host "API 文档: http://127.0.0.1:$apiPort/docs" -ForegroundColor Green
Write-Host "前端代理默认指向 http://localhost:8000，若修改 API_PORT 请同步 frontend/.env.development" -ForegroundColor DarkGray

& $venvPython -m uvicorn app.main:app --reload --host $apiHost --port $apiPort
