# CIP SCADA Backend - 本地部署指南 (Windows)

## 环境要求

- Windows 10/11 或 Windows Server 2019+
- PowerShell 5.1+
- Python 3.10+

## 1. 安装中间件服务

### 方式一: 使用Chocolatey自动安装 (推荐)

```powershell
# 以管理员身份运行
.\install_dependencies.ps1
```

### 方式二: 手动安装

#### PostgreSQL 15
1. 下载 [PostgreSQL Windows安装器](https://www.postgresql.org/download/windows/)
2. 安装时记住设置的postgres用户密码
3. 默认端口: 5432

#### Redis 7
1. 下载 [Memurai](https://www.memurai.com/) (Windows原生Redis) 或
2. 使用 WSL2 + Docker Desktop

#### Mosquitto MQTT
1. 下载 [Mosquitto](https://mosquitto.org/download/)
2. 安装到默认路径

---

## 2. 配置PostgreSQL数据库

### 2.1 创建数据库和用户

以postgres用户身份运行以下命令：

```sql
-- 连接PostgreSQL
psql -U postgres

-- 创建用户
CREATE USER scada WITH PASSWORD 'scada123';

-- 创建数据库
CREATE DATABASE cip_scada OWNER scada;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE cip_scada TO scada;

-- 退出
\q
```

### 2.2 配置pg_hba.conf

编辑 `C:\Program Files\PostgreSQL\15\data\pg_hba.conf`，添加：

```
# IPv4本地连接
host    all             all             127.0.0.1/32            md5
```

### 2.3 重启PostgreSQL服务

```powershell
Restart-Service postgresql*
```

---

## 3. 配置Mosquitto MQTT

### 3.1 创建密码文件

在Mosquitto安装目录创建密码文件：

```powershell
# 生成密码文件
.\mosquitto_passwd.exe -b C:\ProgramFiles\Mosquitto\passwords.txt scada scada123
```

### 3.2 配置mosquitto.conf

编辑 `C:\Program Files\Mosquitto\mosquitto.conf`：

```conf
listener 1883
allow_anonymous false
password_file C:\ProgramFiles\Mosquitto\passwords.txt
```

### 3.3 启动Mosquitto

```powershell
Start-Service mosquitto
```

---

## 4. 配置Redis

Redis默认无需认证即可使用，如需认证：

编辑 `C:\Program Files\Redis\redis.windows.conf`：

```conf
requirepass scada123
```

重启Redis服务：

```powershell
Restart-Service redis*
```

---

## 5. 启动后端应用

### 5.1 创建Python虚拟环境

```powershell
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 5.2 配置环境变量

复制环境变量示例文件：

```powershell
copy .env.example .env
```

根据本地环境修改 `.env` 文件中的连接信息。

### 5.3 启动服务

```powershell
.\start_backend.ps1
```

或者手动启动：

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 6. 验证服务

### 6.1 检查服务状态

```powershell
# 检查PostgreSQL
Test-NetConnection -ComputerName localhost -Port 5432

# 检查Redis
Test-NetConnection -ComputerName localhost -Port 6379

# 检查MQTT
Test-NetConnection -ComputerName localhost -Port 1883

# 检查后端API
Invoke-WebRequest -Uri http://localhost:8000/docs
```

### 6.2 访问API文档

浏览器打开: http://localhost:8000/docs

---

## 7. 常见问题

### Q: PostgreSQL服务无法启动

检查日志: `C:\Program Files\PostgreSQL\15\data\log\*.log`

### Q: Redis连接失败

确认服务正在运行: `Get-Service redis*`

### Q: MQTT连接失败

检查Mosquitto日志: `C:\Program Files\Mosquitto\mosquitto.log`

### Q: 端口被占用

使用以下命令查找占用端口的进程：

```powershell
netstat -ano | findstr :5432
```

---

## 8. 服务停止

```powershell
# 停止后端 (Ctrl+C)

# 停止中间件服务
Stop-Service postgresql*
Stop-Service redis*
Stop-Service mosquitto
```
