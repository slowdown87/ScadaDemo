# CIP SCADA Backend

茶饮料生产线CIP清洗系统的后端服务

## 技术栈

- **FastAPI**: 高性能异步API框架
- **PostgreSQL**: 历史数据存储
- **Redis**: 实时数据缓存
- **MQTT**: 消息订阅发布
- **python-snap7**: PLC通讯

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── api/
│   │   └── routers/         # API路由
│   ├── core/
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   └── redis.py         # Redis连接
│   ├── models/              # SQLAlchemy模型
│   ├── schemas/            # Pydantic模式
│   └── services/           # 业务服务
│       ├── plc_service.py   # PLC通讯服务
│       └── data_service.py  # 数据服务
├── tests/                  # 测试文件
├── requirements.txt         # Python依赖
├── .env.example            # 环境变量示例
├── install_dependencies.ps1 # 依赖安装脚本
├── start_backend.ps1       # 启动脚本
└── LOCAL_DEPLOYMENT.md     # 本地部署指南
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Mosquitto MQTT Broker

### 2. 安装中间件

使用Chocolatey自动安装:

```powershell
# 以管理员身份运行
.\install_dependencies.ps1
```

详细安装步骤请参考 [LOCAL_DEPLOYMENT.md](./LOCAL_DEPLOYMENT.md)

### 3. 配置服务

按照 LOCAL_DEPLOYMENT.md 中的说明配置:
1. PostgreSQL数据库和用户
2. Mosquitto认证
3. Redis配置

### 4. 启动应用

```bash
cd backend

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
copy .env.example .env

# 启动服务
.\start_backend.ps1
```

## API接口

### 系统状态

```
GET /api/v1/system/status
```

### 区域监控

```
GET  /api/v1/zones              # 获取所有区域状态
GET  /api/v1/zones/{zone_id}    # 获取指定区域状态
POST /api/v1/zones/command      # 发送控制命令
```

### 报警管理

```
GET /api/v1/alarms              # 获取激活报警
```

### 配方管理

```
GET  /api/v1/recipes            # 获取所有配方
POST /api/v1/recipes/execute     # 执行配方
```

### WebSocket

```
WS /ws/zones                   # 实时区域数据推送
```

## 数据模型

### 区域状态 (ZoneStatus)

| 字段 | 类型 | 说明 |
|------|------|------|
| zone_id | int | 区域ID (1-5) |
| state | string | 清洗状态 |
| current_step | int | 当前步骤 |
| temp_sp | float | 温度设定值 |
| temp_pv | float | 温度当前值 |
| flow_pv | float | 流量当前值 |
| pump_running | bool | 泵运行状态 |

### 清洗状态枚举

| 状态 | 说明 |
|------|------|
| IDLE | 待机 |
| READY | 准备就绪 |
| STEP_EXEC | 步骤执行中 |
| STEP_TRANSITION | 步骤切换中 |
| COMPLETE | 清洗完成 |
| PAUSE | 暂停 |
| FAULT | 故障 |

## PLC通讯

使用python-snap7与PLC-16通讯:

- IP: 192.168.2.100
- Port: 102
- Rack: 0
- Slot: 1
- DB块: DB101-DB105 (5个区域)

## 开发指南

### 添加新接口

1. 在 `app/schemas/` 定义Pydantic模型
2. 在 `app/main.py` 添加路由
3. 在 `tests/` 添加测试用例

### 添加新服务

1. 在 `app/services/` 创建服务文件
2. 在 `app/main.py` 初始化服务
3. 通过 `app.state` 访问服务

## 测试

```bash
# 运行所有测试
pytest

# 运行指定测试
pytest tests/test_api.py

# 查看覆盖率
pytest --cov=app tests/
```

## 部署

### 生产环境

1. 修改 `.env` 中的生产配置
2. 配置反向代理(Nginx)
3. 启用HTTPS
4. 参考 [LOCAL_DEPLOYMENT.md](./LOCAL_DEPLOYMENT.md) 配置各服务
