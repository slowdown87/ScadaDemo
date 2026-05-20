# CIP SCADA Backend - 依赖安装脚本 (Windows)
# 使用Chocolatey安装PostgreSQL、Redis、Mosquitto

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "错误: 需要管理员权限运行此脚本" -ForegroundColor Red
    Write-Host "请右键点击PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CIP SCADA Backend - 依赖安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Chocolatey是否安装
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Chocolatey未安装，正在安装..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "Chocolatey安装完成" -ForegroundColor Green
}

Write-Host ""
Write-Host "开始安装中间件服务..." -ForegroundColor Cyan
Write-Host ""

# 1. 安装PostgreSQL
Write-Host "[1/3] 安装 PostgreSQL 15..." -ForegroundColor Yellow
choco install postgresql --version=15.8.0 -y --params "/InstallDatasources:false"
if ($LASTEXITCODE -eq 0) {
    Write-Host "PostgreSQL 安装成功" -ForegroundColor Green
} else {
    Write-Host "PostgreSQL 安装失败，请手动安装" -ForegroundColor Red
}

Write-Host ""
Write-Host "[2/3] 安装 Redis..." -ForegroundColor Yellow
choco install redis-64 -y
if ($LASTEXITCODE -eq 0) {
    Write-Host "Redis 安装成功" -ForegroundColor Green
} else {
    Write-Host "Redis 安装失败，请手动安装" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/3] 安装 Mosquitto MQTT Broker..." -ForegroundColor Yellow
choco install mosquitto -y
if ($LASTEXITCODE -eq 0) {
    Write-Host "Mosquitto 安装成功" -ForegroundColor Green
} else {
    Write-Host "Mosquitto 安装失败，请手动安装" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "依赖安装完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor Cyan
Write-Host "1. 配置PostgreSQL数据库" -ForegroundColor White
Write-Host "2. 配置Mosquitto用户认证" -ForegroundColor White
Write-Host "3. 运行 start_backend.ps1 启动服务" -ForegroundColor White
Write-Host ""
