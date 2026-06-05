# 前台启动前端开发服务器，关闭此窗口即停止服务
# Windows PowerShell 5.x 需 UTF-8 BOM 保存本文件，否则中文会乱码
if ($PSVersionTable.PSVersion.Major -lt 6) {
    try { chcp 65001 | Out-Null } catch {}
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
}
Set-Location $PSScriptRoot

if (-not (Test-Path "node_modules")) {
    Write-Host "首次运行，正在安装依赖..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "启动前端: http://localhost:5173 (端口被占用时会自动切换)" -ForegroundColor Green
Write-Host "API 代理目标见 .env.development，当前需后端运行在 8000" -ForegroundColor DarkGray
npm run dev
