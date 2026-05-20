# CIP SCADA Backend - 启动脚本 (Windows)
# 启动PostgreSQL、Redis、Mosquitto和后端应用

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CIP SCADA Backend - 启动服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# 1. 启动PostgreSQL服务
Write-Host "[1/4] 启动 PostgreSQL..." -ForegroundColor Yellow
try {
    Start-Service postgresql* -ErrorAction Stop
    Write-Host "PostgreSQL 服务已启动" -ForegroundColor Green
} catch {
    Write-Host "PostgreSQL 服务启动失败，可能未安装或未配置" -ForegroundColor Red
    Write-Host "提示: 运行 install_dependencies.ps1 安装依赖" -ForegroundColor Yellow
}

# 2. 启动Redis服务
Write-Host ""
Write-Host "[2/4] 启动 Redis..." -ForegroundColor Yellow
try {
    Start-Service redis* -ErrorAction Stop
    Write-Host "Redis 服务已启动" -ForegroundColor Green
} catch {
    Write-Host "Redis 服务启动失败，可能未安装或未配置" -ForegroundColor Red
}

# 3. 启动Mosquitto MQTT服务
Write-Host ""
Write-Host "[3/4] 启动 Mosquitto MQTT..." -ForegroundColor Yellow
try {
    Start-Service mosquitto -ErrorAction Stop
    Write-Host "Mosquitto 服务已启动" -ForegroundColor Green
} catch {
    Write-Host "Mosquitto 服务启动失败，可能未安装或未配置" -ForegroundColor Red
}

# 4. 启动后端应用
Write-Host ""
Write-Host "[4/4] 启动后端应用..." -ForegroundColor Yellow

# 切换到backend目录
$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendDir

# 检查虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "使用虚拟环境..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"

    # 检查数据库是否配置
    if (-not (Test-Path ".env")) {
        Write-Host "未找到.env文件，复制.env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "已创建.env文件，请根据需要修改数据库配置" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "启动 FastAPI 应用..." -ForegroundColor Green
    Write-Host "API地址: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    # 使用系统Python
    Write-Host "使用系统Python..." -ForegroundColor Cyan

    # 检查.env
    if (-not (Test-Path ".env")) {
        Write-Host "未找到.env文件，复制.env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "已创建.env文件，请根据需要修改数据库配置" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "启动 FastAPI 应用..." -ForegroundColor Green
    Write-Host "API地址: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}
