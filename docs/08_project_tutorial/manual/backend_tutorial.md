# CIP SCADA 后端完整教程

## 目录

1. [后端是什么？](#1-后端是什么)
2. [技术栈介绍](#2-技术栈介绍)
3. [项目结构](#3-项目结构)
4. [核心概念](#4-核心概念)
5. [代码详解](#5-代码详解)
6. [Docker一键启动](#6-docker一键启动)
7. [环境变量配置](#6b-环境变量配置)
8. [运行项目](#7-运行项目)
9. [数据库与数据服务](#8-数据库与数据服务)
10. [API完整列表](#9-api完整列表)
11. [文件路径速查](#10-文件路径速查)
12. [Redis缓存键名详解](#11-redis缓存键名详解)
13. [配方模型详解](#12-配方模型详解)
14. [项目实战练习](#13-项目实战练习)
15. [调试与日志](#14-调试与日志)
16. [测试项目](#12-测试项目)
17. [常见问题](#附录常见问题)

---

## 1. 后端是什么？

### 1.1 生活中的比喻

想象你去餐厅吃饭：

```
你（前端）→ 服务员（后端）→ 厨房（PLC/数据库）
```

- **你** → 发出请求："我要一份宫保鸡丁"
- **服务员** → 接收请求，转达给厨房，记录你的座位
- **厨房** → 真正做饭的地方

**后端就是那个"服务员"，在Web应用中连接用户和真实设备/数据。**

### 1.2 本项目的后端职责

```
┌─────────────────────────────────────────────────────────┐
│                     浏览器/Web前端                        │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP请求 / WebSocket
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   CIP SCADA 后端                         │
│                                                         │
│   1. 接收前端请求                                         │
│   2. 读写PLC设备数据（通过Snap7库）                          │
│   3. 缓存数据到Redis（高速缓存）                            │
│   4. 存储历史数据到PostgreSQL                              │
│   5. 返回结果给前端                                        │
└─────────────────────┬───────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│      PLC        │       │   PostgreSQL    │
│   (西门子PLC)   │       │    (数据库)     │
│   真实设备       │       │   历史记录      │
└─────────────────┘       └─────────────────┘
```

### 1.3 后端能做什么？

| 功能 | 示例 |
|------|------|
| 读取数据 | 获取当前水温、流量、压力 |
| 写入命令 | 启动清洗、停止清洗 |
| 数据处理 | 计算平均值、生成报表 |
| 报警管理 | 检测异常、发送报警 |

### 1.4 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CIP SCADA 系统架构                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ▲
                                    │ HTTP/WebSocket
┌───────────────────────────────────┴───────────────────────────────────────┐
│                                  前端层                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        Web浏览器 / HMI界面                             │  │
│  │    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │    │ 仪表盘    │  │ 趋势图   │  │ 报警列表  │  │    配方管理      │  │  │
│  │    └──────────┘  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
                    HTTP/REST API ◄────► WebSocket
                                    │
┌────────────────────────────────────┴─────────────────────────────────────┐
│                                  后端层 (FastAPI)                            │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │                         API Routes (main.py)                        │  │
│   │  GET /zones  │  POST /command  │  WS /ws/zones  │  GET /alarms     │  │
│   └──────────────┬─────────────────┬─────────────────┬───────────────────┘  │
│                  │                 │                 │                      │
│   ┌──────────────▼─────────────────▼─────────────────▼───────────────────┐  │
│   │                        Service Layer                               │  │
│   │  ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐  │  │
│   │  │  PLCService     │    │  DataService    │    │  RecipeService │  │  │
│   │  │  (读写PLC)      │    │  (数据库操作)   │    │  (配方管理)    │  │  │
│   │  └────────┬────────┘    └────────┬────────┘    └───────┬────────┘  │  │
│   └───────────┼──────────────────────┼──────────────────────┼────────────┘  │
│               │                      │                      │              │
│   ┌───────────▼──────────────────────▼──────────────────────▼───────────┐  │
│   │                         Core Layer                                  │  │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐ │  │
│   │  │  Snap7      │    │  Redis      │    │  SQLAlchemy + asyncpg  │ │  │
│   │  │  (PLC通信)   │    │  (缓存)      │    │  (PostgreSQL)         │ │  │
│   │  └─────────────┘    └─────────────┘    └─────────────────────────┘ │  │
│   └────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
               │                      │                      │
               ▼                      ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│      西门子 PLC       │  │       Redis         │  │    PostgreSQL       │
│                      │  │                     │  │                     │
│  ┌─────────────────┐ │  │  scada:zone:1       │  │  batch_records     │
│  │  DB100 (Zone1)  │ │  │  scada:zone:2       │  │  alarm_records     │
│  │  DB101 (Zone2)  │ │  │  scada:zone:N       │  │  recipes           │
│  │  DB10X (ZoneN)  │ │  │  scada:alarms:*     │  │                     │
│  └─────────────────┘ │  │                     │  │                     │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              设备层                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  温度传感器 │  │  流量计   │  │  电导率仪  │  │   阀门   │  │   泵     │  │
│  │  PT100    │  │  Flow    │  │  Cond    │  │  Valve   │  │  Pump    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.5 数据流向详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据流向                                        │
└─────────────────────────────────────────────────────────────────────────────┘

[用户操作]                          [前端]                           [后端]
    │                                │                                │
    │  点击"启动清洗"                │                                │
    │───────────────────────────────►│                                │
    │                                │ POST /api/v1/zones/command     │
    │                                │ {zone_id: 1, command: START}   │
    │                                │───────────────────────────────►│
    │                                │                                │
    │                                │              ┌────────────────▼───┐
    │                                │              │ PLCService         │
    │                                │              │ 1. 读取DB块数据    │
    │                                │              │ 2. 写入命令START   │
    │                                │              │ 3. 写回PLC         │
    │                                │              └───────▲───────────┘
    │                                │                      │
    │                                │                      │ Snap7
    │                                │                      ▼
    │                                │              ┌───────┴─────────┐
    │                                │              │      PLC        │
    │                                │              │  执行清洗流程   │
    │                                │              └───────▲───────────┘
    │                                │                      │
    │                                │              ┌───────┴─────────┐
    │                                │              │ 轮询读取状态    │
    │                                │              │ state: STEP_EXEC│
    │                                │              └───────▲───────────┘
    │                                │                      │
    │                                │              ┌───────┴─────────┐
    │                                │              │ 更新Redis缓存   │
    │                                │              │ scada:zone:1    │
    │                                │              └───────▲───────────┘
    │                                │                      │
    │                                │ WebSocket推送        │
    │                                │ {state: "STEP_EXEC"} │
    │◄──────────────────────────────│                       │
    │                                │                       │
    │  [界面更新: 执行中...]          │                       │


---

## 2. 技术栈介绍

### 2.1 FastAPI - Web框架

**什么是框架？**
> 框架就是一套"工具箱"，帮你省去写基础代码的麻烦

**为什么用FastAPI？**
- 简单易学
- 自动生成API文档
- 支持异步（高性能）

**对比**：
```python
# 原生（麻烦）
if method == "GET" and path == "/zones":
    return zones_data

# FastAPI（简单）
@app.get("/zones")
async def get_zones():
    return zones_data
```

### 2.2 Redis - 高速缓存

**什么是缓存？**
> 缓存就是"临时记事本"，比数据库快很多

**为什么用Redis？**
- PLC数据1秒可能变化100次，不需要每次都写数据库
- 前端频繁查询，用Redis响应更快

```
无缓存：前端 → 数据库(慢)
有缓存：前端 → Redis(快) → 数据库(慢)
```

### 2.3 Snap7 - PLC通信库

**什么是Snap7？**
> 一个让你用Python和西门子PLC通信的库

```python
# 读取PLC数据
data = client.db_read(db_number, start, size)

# 写入PLC数据
client.db_write(db_number, start, data)
```

### 2.4 异步编程 - asyncio

**什么是异步？**
> 异步就是"一心多用"，不用等待一个任务完成才执行下一个

```python
# 同步（傻等）
result1 = fetch_from_plc()  # 等3秒
result2 = fetch_from_redis()  # 等1秒
# 总共4秒

# 异步（同时做）
result1, result2 = await asyncio.gather(
    fetch_from_plc(),   # 开始任务1
    fetch_from_redis()  # 同时开始任务2
)
# 总共3秒（取最大值）
```

---

## 3. 项目结构

### 3.1 目录树

```
project/backend/
├── app/                    # 主应用目录
│   ├── main.py            # 入口文件，所有API在这里
│   ├── core/              # 核心配置
│   │   ├── config.py      # 配置管理
│   │   ├── redis.py       # Redis连接
│   │   └── database.py    # 数据库连接
│   ├── schemas/           # 数据模型（定义数据结构）
│   │   └── cip.py         # CIP相关的数据模型
│   ├── services/          # 业务逻辑
│   │   ├── plc_service.py # PLC通信服务
│   │   └── data_service.py# 数据处理服务
│   └── models/            # 数据库模型
│       ├── batch.py       # 批次记录表
│       └── alarm.py       # 报警记录表
├── tests/                 # 测试文件
│   ├── conftest.py       # 测试配置
│   ├── test_api.py       # API测试
│   └── test_services.py  # 服务测试
├── requirements.txt      # 依赖列表
└── docker-compose.yml    # Docker配置
```

### 3.2 每个文件的作用

| 文件 | 作用 | 打个比方 |
|------|------|----------|
| main.py | API入口 | 餐厅门口 |
| config.py | 配置管理 | 餐厅营业执照 |
| redis.py | Redis连接 | 临时记事本 |
| plc_service.py | PLC通信 | 和厨房沟通的对讲机 |
| schemas/cip.py | 数据格式 | 菜单模板 |

---

## 4. 核心概念

### 4.1 API是什么？

**API = Application Programming Interface（应用程序接口）**

简单理解：**后端给前端开的"菜单"**

```python
# 定义一个API接口
@app.get("/api/v1/zones")  # 菜单项名称
async def get_zones():     # 厨师做菜
    return zones           # 端菜给客人
```

**HTTP方法**：
| 方法 | 含义 | 例子 |
|------|------|------|
| GET | 获取数据 | 看菜单 |
| POST | 创建数据 | 点菜 |
| PUT | 更新数据 | 改菜 |
| DELETE | 删除数据 | 退菜 |

### 4.2 数据模型（Schema）

**什么是数据模型？**
> 定义数据的"形状"，告诉前端每个字段是什么类型

```python
class RecipeInfo(BaseModel):
    recipe_id: int           # 整数类型的配方ID
    recipe_name: str          # 字符串类型的配方名称
    step_count: int          # 步骤数量
    total_time: int          # 总时间（秒）
```

**为什么需要？**
1. 验证数据是否合法
2. 自动生成API文档
3. 类型提示，减少bug

### 4.3 依赖注入

**什么是依赖注入？**
> 把需要用的东西"注入"进来，而不是自己创建

```python
# 不用依赖注入（自己创建）
def get_zones():
    plc = PLCService()  # 每次都创建新的
    return plc.read_data()

# 用依赖注入（别人给）
def get_zones(plc_service: PLCService = Depends(get_plc_service)):
    return plc_service.read_data()  # 复用同一个
```

### 4.4 WebSocket - 实时通信

**HTTP vs WebSocket**：

| HTTP | WebSocket |
|------|-----------|
| 请求-响应 | 持续连接 |
| 客户端发起 | 双方都可以发 |
| 每次都新建连接 | 一次连接，反复通信 |

```python
# HTTP：像对讲机，每次说话都要按按钮
# WebSocket：像电话，拿起就可以一直说
```

---

## 5. 代码详解

### 5.1 main.py - 入口文件（逐行详解）

```python
# ==================== 导入模块 ====================
from datetime import datetime                     # datetime: 日期时间处理
from typing import List, Optional                # typing: 类型提示（List列表, Optional可选）
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException  # FastAPI核心
from fastapi.middleware.cors import CORSMiddleware # CORS: 跨域资源共享中间件
import asyncio                                    # asyncio: 异步编程

# ==================== 导入项目内部模块 ====================
from app.core.config import get_settings          # 配置管理
from app.core.redis import get_redis, init_redis, close_redis  # Redis操作
from app.services.plc_service import PLCService   # PLC通信服务
from app.services.data_service import DataService  # 数据服务
from app.schemas.cip import ZoneStatus, ...        # 数据模型（Schema）

# ==================== 配置加载 ====================
settings = get_settings()  # 从.env文件读取配置，返回Settings对象

# ==================== CORS配置 ====================
# CORS: 解决浏览器跨域访问限制
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Vue/React开发服务器
    "http://localhost:8080",  # 其他前端框架
    "http://127.0.0.1:3000",  # 备用地址
]

# ==================== 辅助函数 ====================
def build_zone_status(zone_id: int, zone_data: dict) -> ZoneStatus:
    """
    辅助函数：将Redis中的字典数据转换成ZoneStatus对象
    为什么要转换？因为Redis存的是字符串，前端需要正确的数据类型

    参数:
        zone_id: Zone编号（1-5）
        zone_data: Redis返回的字典，如 {"state": "IDLE", "temp_sp": "60.0", ...}
    返回:
        ZoneStatus: 符合Schema定义的数据对象
    """
    return ZoneStatus(
        zone_id=zone_id,
        zone_name=zone_data.get("zone_name", f"Zone-{zone_id}"),  # 默认值：Zone-1
        state=zone_data.get("state", "IDLE"),                      # 默认值：IDLE
        current_step=int(zone_data.get("current_step", "0")),       # 转整数
        current_media=zone_data.get("current_media", "NONE"),
        temp_sp=float(zone_data.get("temp_sp", "0")),             # 转浮点数
        temp_pv=float(zone_data.get("temp_pv", "0")),
        temp_reached=zone_data.get("temp_reached", "false").lower() == "true",  # 转布尔
        flow_pv=float(zone_data.get("flow_pv", "0")),
        conductivity=float(zone_data.get("conductivity", "0")),
        pump_running=zone_data.get("pump_running", "false").lower() == "true",
        step_timer=int(zone_data.get("step_timer", "0")),
        step_time_remaining=int(zone_data.get("step_time_remaining", "0"))
    )

# ==================== 生命周期管理 ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期：启动时和关闭时执行的代码
    类似于JavaScript的 addEventListener('load', ...) 和 addEventListener('unload', ...)

    启动时（yield之前）:
        1. 初始化Redis连接
        2. 创建PLC服务并连接
        3. 创建数据服务

    关闭时（yield之后）:
        1. 断开PLC连接
        2. 关闭Redis连接
    """
    # 1. 初始化Redis
    await init_redis()
    print("✅ Redis连接已建立")

    # 2. 创建PLC服务并连接
    plc_service = PLCService()
    connected = await plc_service.connect()
    if connected:
        print(f"✅ PLC连接成功: {settings.plc_ip}")
        # 3. 启动后台轮询任务
        plc_service.poll_task = asyncio.create_task(plc_service.poll_plc())
    else:
        print(f"⚠️ PLC连接失败，请检查网络和配置")

    # 4. 创建数据服务
    data_service = DataService()
    app.state.data_service = data_service

    # yield分隔：以上是启动，以下是关闭
    yield

    # 关闭时清理资源
    if plc_service.poll_task:
        plc_service.poll_task.cancel()  # 取消轮询任务
    await plc_service.disconnect()      # 断开PLC
    await close_redis()                  # 关闭Redis
    print("🔌 资源已释放")

# ==================== 创建应用实例 ====================
app = FastAPI(
    title=settings.app_name,  # API文档标题
    version=settings.app_version,  # API版本
    lifespan=lifespan  # 生命周期管理函数
)

# ==================== 添加中间件 ====================
app.add_middleware(
    CORSMiddleware,  # 跨域中间件
    allow_origins=ALLOWED_ORIGINS,  # 允许的源
    allow_credentials=True,  # 允许携带凭证（cookies）
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的请求头
)

# ==================== API路由（后续章节详解）====================
```

### 5.2 API路由详解

```python
# ═══════════════════════════════════════════════════════════════
# 路由1: GET / - 根路径，返回应用信息
# ═══════════════════════════════════════════════════════════════
@app.get("/")
async def root():
    """
    访问 http://localhost:8000/ 时调用
    用于检查服务是否正常运行

    返回: 应用名称、状态、版本
    """
    return {
        "app": settings.app_name,      # 从配置读取应用名
        "status": "running",           # 固定值
        "version": settings.app_version  # 从配置读取版本
    }

# ═══════════════════════════════════════════════════════════════
# 路由2: GET /api/v1/zones - 获取所有Zone状态
# ═══════════════════════════════════════════════════════════════
@app.get("/api/v1/zones", response_model=List[ZoneStatus])
async def get_all_zones():
    """
    获取所有Zone的实时状态

    执行流程:
        1. 从Redis获取每个Zone的数据
        2. 转换成ZoneStatus对象
        3. 返回列表

    返回: List[ZoneStatus] - Zone状态列表
    """
    redis = await get_redis()  # 获取Redis连接
    zones = []

    # 遍历所有Zone（1到配置的Zone数量）
    for zone_id in range(1, settings.scada_zone_count + 1):
        # 从Redis获取Zone数据（Hash类型）
        zone_data = await redis.hgetall(f"scada:zone:{zone_id}")

        # 如果有数据，转换成ZoneStatus对象
        if zone_data:
            zones.append(build_zone_status(zone_id, zone_data))

    return zones  # 返回列表，如 [Zone1, Zone2, Zone3, Zone4, Zone5]

# ═══════════════════════════════════════════════════════════════
# 路由3: GET /api/v1/zones/{zone_id} - 获取单个Zone状态
# ═══════════════════════════════════════════════════════════════
@app.get("/api/v1/zones/{zone_id}", response_model=ZoneStatus)
async def get_zone(zone_id: int):
    """
    获取指定Zone的状态

    参数:
        zone_id: Zone编号（通过URL路径传入）

    注意:
        zone_id类型是int，如果传入非数字会返回422错误
        zone_id范围验证在PLCService中进行
    """
    # 参数校验（FastAPI自动）
    if zone_id < 1 or zone_id > settings.scada_zone_count:
        raise HTTPException(status_code=404, detail="Zone not found")

    redis = await get_redis()
    zone_data = await redis.hgetall(f"scada:zone:{zone_id}")

    if not zone_data:
        raise HTTPException(status_code=404, detail="Zone data not found")

    return build_zone_status(zone_id, zone_data)

# ═══════════════════════════════════════════════════════════════
# 路由4: POST /api/v1/zones/command - 发送控制命令
# ═══════════════════════════════════════════════════════════════
@app.post("/api/v1/zones/command", response_model=dict)
async def send_zone_command(command: ZoneControlCommand):
    """
    发送控制命令到PLC

    请求体:
        {
            "zone_id": 1,      # Zone编号
            "command": "START" # 命令：START/STOP/PAUSE/RESET
        }

    执行流程:
        1. 获取PLC服务
        2. 调用send_command
        3. 返回结果
    """
    # 从app.state获取PLC服务（由lifespan创建）
    plc_service: PLCService = app.state.plc_service

    # 发送命令
    success = await plc_service.send_command(command.zone_id, command.command)

    if success:
        return {
            "status": "ok",
            "message": f"Command {command.command} sent to zone {command.zone_id}"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to send command")
```

### 5.3 PLC服务详解

```python
# ═══════════════════════════════════════════════════════════════
# PLCService - 与西门子PLC通信的服务类
# ═══════════════════════════════════════════════════════════════

class PLCService:
    """PLC通信服务类"""

    def __init__(self):
        """初始化：设置默认参数"""
        self.client = None           # Snap7客户端对象
        self.connected = False       # 连接状态标志
        self.poll_task = None        # 后台轮询任务

        # PLC DB块配置
        self.db_zone_offset = 100    # Zone 1 = DB100, Zone 2 = DB101...
        self.db_zone_size = 500      # 每个DB块500字节

        # 数据偏移量定义（DB块内的内存地址）
        self.zone_state_offsets = {
            'zone_id': 0,            # 偏移0: Zone ID (2字节INT)
            'state': 2,              # 偏移2: 状态 (2字节INT)
            'temp_sp': 8,            # 偏移8: 温度设定值 (4字节REAL)
            'temp_pv': 12,           # 偏移12: 温度当前值 (4字节REAL)
            'flow_pv': 16,           # 偏移16: 流量 (4字节REAL)
            'conductivity': 20,      # 偏移20: 电导率 (4字节REAL)
            'pump_running': 24,      # 偏移24: 泵运行状态 (1字节BOOL)
            'alarm_code': 36,        # 偏移36: 报警代码 (2字节INT)
        }

    # ═══════════════════════════════════════════════════════════
    # 方法1: connect() - 连接PLC
    # ═══════════════════════════════════════════════════════════
    async def connect(self) -> bool:
        """
        建立与PLC的TCP连接

        使用Snap7库通过以太网连接西门子PLC

        返回: True=连接成功, False=连接失败
        """
        try:
            # 创建Snap7客户端
            self.client = snap7.client.Client()

            # 连接PLC（参数来自.env配置）
            self.client.connect(
                settings.plc_ip,      # PLC IP地址
                settings.plc_rack,    # 机架号，通常是0
                settings.plc_slot,    # 插槽号，通常是1
                settings.plc_tcp_port # TCP端口，默认102
            )

            self.connected = True
            print(f"🔌 PLC已连接: {settings.plc_ip}")
            return True

        except Exception as e:
            print(f"❌ PLC连接失败: {e}")
            self.connected = False
            return False

    # ═══════════════════════════════════════════════════════════
    # 方法2: send_command() - 发送控制命令
    # ═══════════════════════════════════════════════════════════
    async def send_command(self, zone_id: int, command: str) -> bool:
        """
        发送控制命令到指定Zone

        参数:
            zone_id: Zone编号（1-5）
            command: 命令字符串（START/STOP/PAUSE/RESET）

        执行流程:
            1. 参数验证
            2. 读取当前DB块数据
            3. 修改命令字节
            4. 写回PLC

        返回: True=成功, False=失败
        """
        # 1. 检查连接
        if not self.connected or not self.client:
            return False

        # 2. 参数验证
        if zone_id < 1 or zone_id > settings.scada_zone_count:
            return False

        # 3. 命令映射成数字
        cmd_map = {"START": 1, "STOP": 2, "PAUSE": 3, "RESET": 4}
        cmd_value = cmd_map.get(command.upper())
        if not cmd_value:
            print(f"未知命令: {command}")
            return False

        try:
            # 4. 计算DB块编号（Zone 1 = DB100）
            db_number = self.db_zone_offset + zone_id

            # 5. 读取DB块数据（500字节）
            data = self.client.db_read(db_number, 0, self.db_zone_size)

            # 6. 写入命令到偏移50的位置
            # _write_int是我们自己写的辅助函数
            self._write_int(data, 50, cmd_value)

            # 7. 把修改后的数据写回PLC
            self.client.db_write(db_number, 0, data)

            print(f"📤 已发送命令 {command} 到 Zone {zone_id}")
            return True

        except Exception as e:
            print(f"发送命令失败: {e}")
            return False

    # ═══════════════════════════════════════════════════════════
    # 方法3: poll_plc() - 轮询PLC数据
    # ═══════════════════════════════════════════════════════════
    async def poll_plc(self):
        """
        后台任务：定期读取PLC数据并更新Redis

        这是整个系统的核心循环，不断从PLC读取数据存入Redis

        执行流程:
            while True:
                1. 读取所有Zone数据
                2. 写入Redis缓存
                3. 等待一段时间
        """
        reconnect_delay = 1.0  # 重连延迟（秒）
        max_delay = 60.0       # 最大延迟

        while self.connected:
            try:
                # 1. 读取所有Zone数据
                await self.read_all_zones()

                # 2. 重置延迟（恢复正常）
                reconnect_delay = 1.0

                # 3. 等待配置的间隔时间
                await asyncio.sleep(settings.scada_refresh_interval_ms / 1000.0)

            except asyncio.CancelledError:
                # 任务被取消，优雅退出
                break

            except Exception as e:
                print(f"轮询错误: {e}")

                # 指数退避：1s → 2s → 4s → 8s...（最多60s）
                reconnect_delay = min(reconnect_delay * 2, max_delay)
                await asyncio.sleep(reconnect_delay)
```

**执行流程**：
```
前端调用 GET /api/v1/zones
    ↓
FastAPI路由匹配
    ↓
执行 get_all_zones() 函数
    ↓
从Redis获取数据
    ↓
转换成标准格式返回
    ↓
前端收到JSON数据
```

### 5.3 plc_service.py - PLC通信

```python
class PLCService:
    def __init__(self):
        # Snap7客户端，用于和PLC通信
        self.client: Optional[snap7.client.Client] = None
        self.connected = False

        # PLC的DB块配置
        self.db_zone_offset = 100   # Zone 1 用 DB100
        self.db_zone_size = 500     # 每个DB块500字节

        # 状态数据的偏移量（内存地址）
        self.zone_state_offsets = {
            'zone_id': 0,
            'state': 2,           # 状态在偏移2的位置
            'temp_sp': 8,         # 温度设定值在偏移8
            'temp_pv': 12,        # 温度当前值在偏移12
            # ...
        }

    async def connect(self) -> bool:
        """连接PLC"""
        try:
            self.client = snap7.client.Client()
            self.client.connect(
                settings.plc_ip,    # PLC的IP地址
                settings.plc_rack,
                settings.plc_slot,
                settings.plc_tcp_port
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"PLC连接失败: {e}")
            return False

    async def read_zone_data(self, zone_id: int) -> dict:
        """读取单个Zone的数据"""
        if not self.connected:
            return {}

        try:
            # 1. 确定要读哪个DB块（DB100 = Zone1, DB101 = Zone2...）
            db_number = self.db_zone_offset + zone_id

            # 2. 读取DB块数据（500字节）
            data = self.client.db_read(db_number, 0, self.db_zone_size)

            # 3. 解析数据（从原始字节提取温度、压力等）
            temp_sp = self._read_real(data, self.zone_state_offsets['temp_sp'])

            # 4. 返回字典
            return {
                "temp_sp": str(temp_sp),
                "state": "IDLE",
                # ...
            }
        except Exception as e:
            print(f"读取Zone {zone_id} 失败: {e}")
            return {}

    async def send_command(self, zone_id: int, command: str) -> bool:
        """发送控制命令到PLC"""
        if not self.connected:
            return False

        try:
            # 1. 读取当前DB块数据
            db_number = self.db_zone_offset + zone_id
            data = self.client.db_read(db_number, 0, self.db_zone_size)

            # 2. 把命令转换成数字
            cmd_map = {"START": 1, "STOP": 2, "PAUSE": 3}
            cmd_value = cmd_map.get(command.upper())
            if not cmd_value:
                return False

            # 3. 写入命令到DB块偏移50的位置
            self._write_int(data, 50, cmd_value)

            # 4. 把数据写回PLC
            self.client.db_write(db_number, 0, data)
            return True
        except Exception as e:
            print(f"发送命令失败: {e}")
            return False
```

### 5.4 数据流向完整示例

**场景：用户点击"启动清洗"按钮**

```
1. 前端发送请求
POST /api/v1/zones/command
{"zone_id": 1, "command": "START"}

2. 后端接收请求 (main.py)
@app.post("/api/v1/zones/command")
async def send_zone_command(command: ZoneControlCommand):
    plc_service = app.state.plc_service  # 获取PLC服务
    success = await plc_service.send_command(
        command.zone_id,
        command.command
    )
    return {"status": "ok"}

3. PLC服务处理 (plc_service.py)
async def send_command(zone_id, command):
    - 读取DB块
    - 写入命令(START=1)
    - 写回PLC

4. PLC执行命令
- PLC程序检测到DB100.50=1
- 启动清洗流程

5. 后端持续轮询PLC状态
async def poll_plc():
    while True:
        data = read_zone_data()  # 读取所有Zone
        await redis.hset(...)    # 更新Redis缓存
        await asyncio.sleep(0.1)

6. 前端通过WebSocket获取实时状态
WS /ws/zones
← {"type": "zone_update", "data": {"zone_id": 1, "state": "STEP_EXEC", ...}}
```

### 5.5 schemas/cip.py - 数据模型

```python
# 枚举类型 - 定义有限的选项
class CleanState(str, Enum):
    IDLE = "IDLE"           # 空闲
    READY = "READY"          # 就绪
    STEP_EXEC = "STEP_EXEC"  # 执行中
    FAULT = "FAULT"          # 故障

# Zone状态 - 完整的数据结构
class ZoneStatus(BaseModel):
    zone_id: int              # Zone编号（1-5）
    zone_name: str            # Zone名称
    state: CleanState         # 当前状态（枚举）
    current_step: int         # 当前步骤
    current_media: MediaType  # 当前介质
    temp_sp: float            # 温度设定值
    temp_pv: float            # 温度当前值
    temp_reached: bool        # 温度是否到达
    flow_pv: float            # 流量
    conductivity: float       # 电导率
    pump_running: bool       # 泵是否运行
    step_timer: int           # 步骤计时
    step_time_remaining: int  # 剩余时间

# 控制命令 - 带验证
class ZoneControlCommand(BaseModel):
    zone_id: int = Field(..., ge=1, le=5)  # 必须1-5之间
    command: str = Field(...)               # 必须提供
```

---

## 6. Docker一键启动

### 6.1 什么是Docker？

**Docker = 集装箱**
> 把应用和它的"行李"（依赖、环境）打包在一起，到哪都能运行

**不用Docker的问题**：
```
你的电脑：安装了Python 3.8，能运行 ✅
同事电脑：安装了Python 2.7，运行失败 ❌
服务器：没有Python，需要从头安装 ❌
```

**用Docker的好处**：
```
一个配置文件 → 任何电脑都能运行完全相同的环境
```

### 6.2 docker-compose.yml 配置详解

```yaml
# project/backend/docker-compose.yml

services:  # 定义3个服务
  # 服务1: PostgreSQL数据库
  postgres:
    image: postgres:15-alpine  # 使用轻量级PostgreSQL镜像
    container_name: cip_scada_postgres  # 容器名称
    environment:  # 数据库配置
      POSTGRES_USER: scada      # 用户名
      POSTGRES_PASSWORD: scada123  # 密码
      POSTGRES_DB: cip_scada    # 数据库名
    ports:
      - "5432:5432"  # 主机:容器 端口映射
    volumes:
      - postgres_data:/var/lib/postgresql/data  # 数据持久化
    healthcheck:  # 健康检查
      test: ["CMD-SHELL", "pg_isready -U scada"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 服务2: Redis缓存
  redis:
    image: redis:7-alpine
    container_name: cip_scada_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  # 服务3: MQTT消息代理（可选，用于物联网上传）
  mqtt:
    image: eclipse-mosquitto:2
    container_name: cip_scada_mqtt
    ports:
      - "1883:1883"  # MQTT端口
      - "9001:9001"  # WebSocket端口

  # 服务4: 后端应用
  backend:
    build: .  # 使用当前目录的Dockerfile构建
    container_name: cip_scada_backend
    ports:
      - "8000:8000"  # 后端端口
    env_file:
      - .env  # 环境变量文件
    depends_on:
      postgres:
        condition: service_healthy  # 等待postgres就绪
      redis:
        condition: service_healthy
    volumes:
      - ./app:/app/app  # 代码热更新
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:  # 定义持久化卷
  postgres_data:
  redis_data:
  mqtt_data:
```

### 6.3 启动所有服务

```bash
# 进入后端目录
cd project/backend

# 第一次启动（构建并启动所有服务）
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 停止所有服务
docker-compose down

# 停止并删除数据（慎用！）
docker-compose down -v
```

### 6.4 Docker命令速查

| 命令 | 说明 |
|------|------|
| `docker-compose up -d` | 后台启动所有服务 |
| `docker-compose down` | 停止所有服务 |
| `docker-compose ps` | 查看运行状态 |
| `docker-compose logs -f` | 查看日志 |
| `docker-compose restart backend` | 重启后端 |
| `docker-compose exec postgres psql -U scada` | 进入数据库 |

---

## 6B. 环境变量配置

### 6B.1 什么是环境变量？

**环境变量 = 程序的"配置文件"**

为什么不用硬编码？
```python
# ❌ 硬编码（不好）
PLC_IP = "192.168.2.100"  # 写死了，换环境要改代码

# ✅ 环境变量（好）
PLC_IP = os.getenv("PLC_IP", "192.168.2.100")  # 从外部读取
```

### 6B.2 .env 文件配置

创建 `project/backend/.env` 文件：

```bash
# project/backend/.env

# ===== 应用配置 =====
APP_NAME=CIP_SCADA_Backend
APP_VERSION=1.0.0
DEBUG=false                    # 生产环境设为false
LOG_LEVEL=INFO

# ===== 服务器配置 =====
HOST=0.0.0.0
PORT=8000

# ===== 数据库配置 =====
DATABASE_URL=postgresql+asyncpg://scada:scada123@localhost:5432/cip_scada
# 格式: postgresql+asyncpg://用户名:密码@主机:端口/数据库名

# ===== Redis配置 =====
REDIS_URL=redis://localhost:6379/0
# 格式: redis://主机:端口/数据库编号

# ===== MQTT配置（可选）=====
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_USERNAME=scada
MQTT_PASSWORD=scada123

# ===== PLC通信配置 =====
PLC_IP=192.168.2.100         # PLC的IP地址
PLC_RACK=0                   # PLC机架号
PLC_SLOT=1                   # PLC插槽号
PLC_TCP_PORT=102             # TCP端口（西门子默认102）

# ===== SCADA系统配置 =====
SCADA_ZONE_COUNT=5           # Zone数量（1-5）
SCADA_REFRESH_INTERVAL_MS=100  # 轮询间隔（毫秒）
```

### 6B.3 配置加载原理

```python
# app/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 定义配置项和默认值
    app_name: str = "CIP SCADA Backend"
    plc_ip: str = "192.168.2.100"  # 默认值
    scada_zone_count: int = 5

    class Config:
        env_file = ".env"  # 从.env文件加载
        case_sensitive = False  # 大小写不敏感

@lru_cache()  # 缓存，避免重复读取
def get_settings() -> Settings:
    return Settings()
```

---

## 7. 运行项目

### 6.1 安装依赖

```bash
# 进入后端目录
cd project/backend

# 安装Python依赖
pip install fastapi uvicorn asyncpg sqlalchemy redis python-snap7 pydantic pydantic-settings python-dotenv httpx pytest pytest-asyncio
```

### 6.2 启动Redis（必须）

Redis用于缓存数据，需要先启动：

```bash
# 使用Docker启动Redis
docker run -d -p 6379:6379 redis:7-alpine

# 或者本地已安装Redis
redis-server
```

### 6.3 启动后端

```bash
# 开发模式（代码修改后自动重启）
cd project/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问API文档
# 打开浏览器：http://localhost:8000/docs
```

### 6.4 访问自动文档

FastAPI会自动生成API文档：

| 地址 | 说明 |
|------|------|
| http://localhost:8000/docs | Swagger UI（推荐） |
| http://localhost:8000/redoc | ReDoc |

---

## 12. 测试项目

### 7.1 运行测试

```bash
cd project/backend

# 运行所有测试
pytest tests/ -v

# 运行特定文件
pytest tests/test_api.py -v

# 查看详细输出
pytest tests/ -v --tb=long
```

### 7.2 测试说明

| 测试文件 | 测试内容 |
|----------|----------|
| test_api.py | API接口测试（15个） |
| test_services.py | PLC服务测试（10个） |

### 7.3 手动测试API

使用curl或Postman：

```bash
# 测试根路径
curl http://localhost:8000/

# 获取所有Zone状态
curl http://localhost:8000/api/v1/zones

# 发送控制命令
curl -X POST http://localhost:8000/api/v1/zones/command \
  -H "Content-Type: application/json" \
  -d '{"zone_id": 1, "command": "START"}'
```

---

## 8. 数据库与数据服务

### 8.1 PostgreSQL - 关系型数据库

**什么是数据库？**
> 数据库 = 永久存储数据的"仓库"

**PostgreSQL vs Redis**：
| PostgreSQL | Redis |
|------------|------|
| 磁盘存储（容量大） | 内存存储（速度快） |
| 复杂查询支持 | 简单键值查询 |
| 历史数据 | 实时数据 |

### 8.2 SQLAlchemy - Python数据库 ORM

**ORM = Object Relational Mapping（对象关系映射）**
> 把数据库表变成Python对象，不用写SQL也能操作数据库

```python
# ❌ 写SQL（麻烦）
result = db.execute("SELECT * FROM batch_records WHERE zone_id = 1")

# ✅ 用ORM（简单）
result = db.query(BatchRecordModel).filter_by(zone_id=1)
```

### 8.3 数据库连接配置

```python
# app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,      # 打印SQL语句（调试用）
    pool_pre_ping=True,        # 连接前检查是否有效
    pool_size=10,             # 连接池大小
    max_overflow=20            # 最大额外连接数
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,   # 提交后不自动过期
    autocommit=False,          # 手动提交
    autoflush=False            # 手动刷新
)

# Base是所有模型的基类
Base = declarative_base()
```

### 8.4 批次记录模型（BatchRecordModel）

**文件位置**：`app/models/batch.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, JSON
from app.core.database import Base

class BatchRecordModel(Base):
    __tablename__ = "batch_records"  # 表名

    # 主键和索引
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(String(50), unique=True, index=True)  # 唯一索引

    # 基本信息
    zone_id = Column(Integer, nullable=False, index=True)      # Zone编号
    zone_name = Column(String(50), nullable=False)            # Zone名称
    recipe_id = Column(Integer, nullable=False)               # 配方ID
    recipe_name = Column(String(50), nullable=False)           # 配方名称

    # 时间记录
    start_time = Column(DateTime, nullable=False)             # 开始时间
    end_time = Column(DateTime, nullable=False)               # 结束时间
    total_time = Column(Integer, nullable=False)             # 总时长(秒)

    # 执行结果
    result = Column(Boolean, nullable=False)                 # 是否成功
    final_conductivity = Column(Float)                      # 最终电导率
    fail_reason = Column(String(200))                        # 失败原因

    steps_data = Column(JSON)                                # 步骤详情(JSON)

    created_at = Column(DateTime, default=datetime.now)      # 创建时间
```

**表结构可视化**：
```
┌─────────────────────────────────────────────┐
│           batch_records 表                   │
├─────────────────────────────────────────────┤
│ id          │ 主键，自增                     │
│ record_id   │ 唯一标识，"BATCH-2024-001"    │
│ zone_id     │ Zone编号，1-5                  │
│ recipe_id   │ 配方ID，1-10                   │
│ start_time  │ 开始时间                       │
│ end_time    │ 结束时间                       │
│ total_time  │ 总时长（秒）                   │
│ result      │ 是否成功（true/false）         │
│ final_conductivity │ 最终电导率（清洗效果）   │
│ fail_reason │ 失败原因                       │
│ steps_data  │ 步骤详情（JSON格式）            │
└─────────────────────────────────────────────┘
```

### 8.5 报警记录模型（AlarmRecordModel）

**文件位置**：`app/models/alarm.py`

```python
class AlarmRecordModel(Base):
    __tablename__ = "alarm_records"

    id = Column(Integer, primary_key=True, index=True)
    alarm_id = Column(Integer, nullable=False, index=True)    # 报警ID
    alarm_code = Column(Integer, nullable=False, index=True)  # 报警代码
    alarm_text = Column(String(100), nullable=False)          # 报警描述
    level = Column(String(20), nullable=False)                # 报警级别：L1/L2/L3

    zone_id = Column(Integer, nullable=False, index=True)    # Zone编号

    trigger_time = Column(DateTime, nullable=False, index=True)  # 触发时间
    ack_time = Column(DateTime)                              # 确认时间
    ack_user = Column(String(50))                            # 确认用户
    status = Column(String(20), nullable=False)             # 状态：ACTIVE/ACKED/CLEARED

    created_at = Column(DateTime, default=datetime.now)
```

**报警级别说明**：
| 级别 | 含义 | 颜色 |
|------|------|------|
| L1 | 紧急报警 | 红色 |
| L2 | 重要报警 | 橙色 |
| L3 | 一般报警 | 黄色 |

### 8.6 DataService - 数据服务层

**文件位置**：`app/services/data_service.py`

数据服务层负责数据库的增删改查操作：

```python
class DataService:

    # 保存批次记录
    async def save_batch_record(self, record_data: dict) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                record = BatchRecordModel(**record_data)
                session.add(record)
                await session.commit()  # 提交事务
                return True
            except Exception as e:
                await session.rollback()  # 出错回滚
                return False

    # 查询批次记录（支持过滤和分页）
    async def get_batch_records(
        self,
        zone_id: Optional[int] = None,      # 按Zone过滤
        start_time: Optional[datetime] = None,  # 开始时间
        end_time: Optional[datetime] = None,    # 结束时间
        limit: int = 100                     # 返回条数限制
    ) -> List[dict]:
        limit = min(limit, 1000)  # 最多返回1000条

        async with AsyncSessionLocal() as session:
            query = select(BatchRecordModel)

            # 动态添加过滤条件
            if zone_id:
                query = query.where(BatchRecordModel.zone_id == zone_id)
            if start_time:
                query = query.where(BatchRecordModel.start_time >= start_time)
            if end_time:
                query = query.where(BatchRecordModel.end_time <= end_time)

            # 按时间倒序，限制条数
            query = query.order_by(desc(BatchRecordModel.start_time)).limit(limit)

            result = await session.execute(query)
            records = result.scalars().all()

            # 转换为字典列表
            return [
                {
                    "id": record.id,
                    "record_id": record.record_id,
                    "zone_id": record.zone_id,
                    "recipe_name": record.recipe_name,
                    "start_time": record.start_time,
                    "result": record.result,
                    # ... 更多字段
                }
                for record in records
            ]

    # 查询报警历史
    async def get_alarm_history(
        self,
        zone_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[dict]:
        # 和get_batch_records类似，但查询alarm_records表
        ...
```

### 8.7 报警处理流程

```
┌─────────────────────────────────────────────────────────────┐
│                     报警产生流程                              │
└─────────────────────────────────────────────────────────────┘

1. PLC检测异常
   ├── 温度超上限 (>85°C)
   ├── 温度超下限 (<15°C)
   ├── 电导率超标 (>50μS/cm)
   ├── 流量异常 (<5L/min)
   └── 泵故障

2. PLC写入报警数据到DB块
   └── DB块偏移36: alarm_code (INT)
   └── DB块偏移38: alarm_level (INT)
   └── DB块偏移40: alarm_text (STRING)

3. 后端轮询检测到报警
   └── plc_service.poll_plc() 读取DB块
   └── 判断是否有新报警

4. 后端处理报警
   └── 保存到Redis: scada:alarms:active
   └── 保存到PostgreSQL: alarm_records表

5. 前端显示报警
   └── GET /api/v1/alarms 获取活跃报警
   └── WebSocket推送实时报警
```

---

## 9. API完整列表

### 9.1 所有API接口

| 方法 | 路径 | 说明 | 返回 |
|------|------|------|------|
| GET | `/` | 根路径 | 应用信息 |
| GET | `/api/v1/system/status` | 系统状态 | SystemStatus |
| GET | `/api/v1/zones` | 所有Zone状态 | ZoneStatus[] |
| GET | `/api/v1/zones/{zone_id}` | 单个Zone状态 | ZoneStatus |
| POST | `/api/v1/zones/command` | 发送控制命令 | Result |
| GET | `/api/v1/alarms` | 活跃报警列表 | AlarmInfo[] |
| GET | `/api/v1/recipes` | 配方列表 | RecipeInfo[] |
| POST | `/api/v1/recipes/execute` | 执行配方 | Result |
| WS | `/ws/zones` | 实时数据推送 | WebSocket |

### 9.2 请求/响应示例

**获取Zone状态**：
```bash
GET /api/v1/zones/1

# 响应
{
  "zone_id": 1,
  "zone_name": "Zone-1",
  "state": "IDLE",
  "current_step": 0,
  "current_media": "PURE_WATER",
  "temp_sp": 60.0,
  "temp_pv": 25.5,
  "temp_reached": false,
  "flow_pv": 0.0,
  "conductivity": 0.5,
  "pump_running": false,
  "step_timer": 0,
  "step_time_remaining": 0
}
```

**发送控制命令**：
```bash
POST /api/v1/zones/command
Content-Type: application/json

{
  "zone_id": 1,
  "command": "START"
}

# 响应
{
  "status": "ok",
  "message": "Command START sent to zone 1"
}
```

---

## 10. 文件路径速查

### 10.1 项目文件结构

```
project/backend/
├── app/
│   ├── main.py                    ← API入口
│   ├── core/
│   │   ├── config.py             ← 配置管理
│   │   ├── database.py           ← 数据库连接
│   │   └── redis.py              ← Redis连接
│   ├── schemas/
│   │   └── cip.py                ← 数据模型
│   ├── services/
│   │   ├── plc_service.py        ← PLC通信
│   │   └── data_service.py       ← 数据服务
│   └── models/
│       ├── batch.py              ← 批次表
│       ├── alarm.py              ← 报警表
│       └── recipe.py             ← 配方表
├── tests/
│   ├── conftest.py               ← 测试配置
│   ├── test_api.py               ← API测试
│   └── test_services.py          ← 服务测试
├── docker-compose.yml             ← Docker配置
├── Dockerfile                     ← Docker镜像
├── requirements.txt               ← Python依赖
├── .env.example                  ← 环境变量模板
└── pytest.ini                    ← pytest配置
```

### 10.2 关键代码位置

| 功能 | 文件 | 行号 |
|------|------|------|
| API定义 | main.py | 74-173 |
| PLC连接 | plc_service.py | 37-53 |
| 轮询逻辑 | plc_service.py | 67-92 |
| 发送命令 | plc_service.py | 145-170 |
| 数据模型 | schemas/cip.py | 26-101 |
| 数据库连接 | database.py | 7-21 |
| Redis连接 | redis.py | 9-25 |

---

## 11. Redis缓存键名详解

### 11.1 键名命名规则

Redis使用**冒号分隔**的键名，类似文件路径：

```
scada:zone:1          # 层级结构清晰
scada:alarms:active   # 分类明确
```

### 11.2 完整键名清单

| 键名 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `scada:zone:{id}` | Hash | Zone状态数据 | `{"state": "IDLE", "temp_sp": "60"}` |
| `scada:alarms:active` | Set | 活跃报警ID集合 | `{"1", "2", "3"}` |
| `scada:alarm:{id}` | Hash | 单个报警详情 | `{"code": "1001", "text": "高温报警"}` |
| `scada:recipes` | Hash | 配方列表 | `{"1": "{...}", "2": "{...}"}` |
| `scada:recipe:{id}` | Hash | 单个配方详情 | `{"name": "标准清洗", "steps": "5"}` |
| `scada:system:status` | Hash | 系统状态 | `{"running": "true"}` |

### 11.3 Zone状态数据结构

```python
# 键名: scada:zone:1 (Zone 1的状态)
# 类型: Hash (字段值对)

scada:zone:1 = {
    "zone_id": "1",                    # Zone编号
    "zone_name": "Zone-1",              # Zone名称
    "state": "IDLE",                   # 状态：IDLE/READY/STEP_EXEC/PAUSE/FAULT
    "current_step": "0",                # 当前步骤编号
    "current_media": "PURE_WATER",      # 当前介质
    "temp_sp": "60.0",                 # 温度设定值(°C)
    "temp_pv": "25.5",                 # 温度当前值(°C)
    "temp_reached": "false",           # 温度是否到达设定值
    "flow_pv": "0.0",                  # 流量当前值(L/min)
    "conductivity": "0.5",             # 电导率(μS/cm)
    "pump_running": "false",            # 泵运行状态
    "step_timer": "0",                  # 步骤已运行时间(秒)
    "step_time_remaining": "0",        # 步骤剩余时间(秒)
    "alarm_code": "0",                  # 当前报警代码
    "alarm_text": ""                    # 当前报警文本
}
```

### 11.4 为什么用Hash而不是普通Key？

```python
# ❌ 普通Key（每个字段一个键）
scada:zone:1:state = "IDLE"
scada:zone:1:temp_sp = "60.0"
scada:zone:1:temp_pv = "25.5"
# 问题：读取要发3次请求

# ✅ Hash（一个键包含所有字段）
scada:zone:1 = {state: "IDLE", temp_sp: "60.0", ...}
# 优点：一次请求获取所有数据
await redis.hgetall("scada:zone:1")  # 获取所有字段
await redis.hget("scada:zone:1", "temp_pv")  # 获取单个字段
```

---

## 12. 配方模型详解

### 12.1 RecipeModel 数据库结构

**文件位置**：`app/models/recipe.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.core.database import Base

class RecipeModel(Base):
    __tablename__ = "recipes"  # 表名

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, unique=True, nullable=False, index=True)

    # 基本信息
    recipe_name = Column(String(50), nullable=False)
    description = Column(String(200))

    # 步骤配置
    step_count = Column(Integer, nullable=False)
    steps_data = Column(JSON)  # JSON格式存储步骤详情

    # 时间配置
    total_time = Column(Integer, nullable=False)  # 总时间(秒)

    # 启用状态
    enable = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Recipe {self.recipe_id}: {self.recipe_name}>"
```

### 12.2 steps_data JSON结构示例

```json
{
  "steps": [
    {
      "step_no": 1,
      "media": "PRE_RINSE",
      "duration": 120,
      "temp_sp": 25,
      "flow_sp": 100,
      "conductivity_max": null
    },
    {
      "step_no": 2,
      "media": "CAUSTIC",
      "duration": 300,
      "temp_sp": 60,
      "flow_sp": 80,
      "conductivity_max": 50
    },
    {
      "step_no": 3,
      "media": "RINSE",
      "duration": 180,
      "temp_sp": 25,
      "flow_sp": 100,
      "conductivity_max": 10
    }
  ]
}
```

### 12.3 配方执行流程

```
1. 用户选择配方（Recipe 2: 深度清洗）
       ↓
2. 前端调用 POST /api/v1/recipes/execute
   {zone_id: 1, recipe_id: 2}
       ↓
3. 后端校验配方存在且启用
       ↓
4. 后端调用 plc_service.start_recipe(1, 2)
       ↓
5. 后端写入PLC DB块：
   - DB101.50 = 1 (启动命令)
   - DB101.52 = 2 (配方ID)
       ↓
6. PLC程序开始执行配方
```

---

## 13. 项目实战练习

### 练习1：添加获取批次记录API

**目标**：添加 `GET /api/v1/batch` 接口，查询历史批次记录

**步骤**：

1. 在 `schemas/cip.py` 添加响应模型
```python
# schemas/cip.py
class BatchRecord(BaseModel):
    record_id: str
    zone_id: int
    recipe_name: str
    start_time: datetime
    result: bool
```

2. 在 `main.py` 添加路由
```python
# main.py
from app.schemas.cip import BatchRecord

@app.get("/api/v1/batch", response_model=List[BatchRecord])
async def get_batch_records(
    zone_id: Optional[int] = None,
    limit: int = 100
):
    data_service = app.state.data_service
    return await data_service.get_batch_records(zone_id, limit)
```

3. 运行测试
```bash
pytest tests/test_api.py -v -k "batch"
```

---

### 练习2：添加确认报警API

**目标**：添加 `POST /api/v1/alarms/{alarm_id}/ack` 确认报警接口

**步骤**：

1. 添加确认逻辑到 `data_service.py`
```python
async def ack_alarm(self, alarm_id: int, user: str) -> bool:
    # 1. 更新Redis中的报警状态
    # 2. 更新数据库中的确认时间和用户
    # 3. 从活跃报警Set中移除
    pass
```

2. 在 `main.py` 添加路由
```python
@app.post("/api/v1/alarms/{alarm_id}/ack")
async def ack_alarm(alarm_id: int, user: str = "operator"):
    # 调用 data_service.ack_alarm()
    pass
```

---

### 练习3：添加获取统计数据API

**目标**：添加统计接口，返回清洗次数、成功率等

**实现提示**：
```python
@app.get("/api/v1/statistics")
async def get_statistics(days: int = 7):
    # 1. 查询最近N天的批次记录
    records = await data_service.get_batch_records(limit=10000)

    # 2. 计算统计数据
    total = len(records)
    success = sum(1 for r in records if r.result)
    rate = success / total if total > 0 else 0

    # 3. 按Zone分组统计
    by_zone = {}
    for zone_id in range(1, 6):
        zone_records = [r for r in records if r.zone_id == zone_id]
        by_zone[zone_id] = {
            "count": len(zone_records),
            "success_rate": calc_rate(zone_records)
        }

    return {
        "total_count": total,
        "success_rate": rate,
        "by_zone": by_zone
    }
```

---

## 14. 调试与日志

### 14.1 查看后端日志

```bash
# 本地运行
uvicorn app.main:app --reload --log-level debug

# Docker环境
docker-compose logs -f backend
docker-compose logs -f backend --tail=100  # 最近100行
```

### 14.2 日志级别

| 级别 | 用途 | 输出量 |
|------|------|--------|
| DEBUG | 详细调试信息 | 很多 |
| INFO | 一般信息 | 中等 |
| WARNING | 警告 | 较少 |
| ERROR | 错误 | 少 |

### 14.3 常用调试技巧

**1. 查看Redis数据**
```bash
# 进入Redis容器
docker-compose exec redis redis-cli

# 查看Zone数据
KEYS scada:zone:*       # 列出所有Zone键
HGETALL scada:zone:1    # 查看Zone1的数据
SMEMBERS scada:alarms:active  # 查看活跃报警
```

**2. 查看数据库数据**
```bash
# 进入PostgreSQL
docker-compose exec postgres psql -U scada -d cip_scada

# 查看表数据
SELECT * FROM batch_records LIMIT 10;
SELECT * FROM alarm_records WHERE status = 'ACTIVE';
```

**3. 测试PLC连接**
```python
# 在Python中测试
from app.services.plc_service import PLCService

plc = PLCService()
connected = await plc.connect()
print(f"PLC连接状态: {connected}")

if connected:
    data = await plc.read_zone_data(1)
    print(f"Zone1数据: {data}")
    await plc.disconnect()
```

### 14.4 常见问题排查

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| API返回500 | PLC未连接 | 检查PLC IP配置 |
| WebSocket无数据 | Redis未启动 | `docker-compose up -d redis` |
| 数据不更新 | 轮询被中断 | 检查poll_plc是否正常运行 |
| 前端跨域错误 | CORS配置 | 检查main.py的ALLOWED_ORIGINS |

---

## 附录A：术语表

### A.1 技术术语

| 术语 | 英文 | 解释 | 在本项目中的位置 |
|------|------|------|-----------------|
| 后端 | Backend | 服务器端代码，处理业务逻辑 | `app/main.py` |
| 前端 | Frontend | 用户界面代码 | Web浏览器/HMI |
| API | Application Programming Interface | 应用程序接口 | `GET /api/v1/zones` |
| REST | Representational State Transfer | 一种API设计风格 | HTTP方法+URL |
| WebSocket | - | 双向实时通信协议 | `/ws/zones` |
| 异步 | Async/Await | 非阻塞编程方式 | `async def xxx()` |
| ORM | Object Relational Mapping | 对象关系映射 | SQLAlchemy |
| 缓存 | Cache | 临时存储加速访问 | Redis |
| 轮询 | Polling | 定期检查数据变化 | `poll_plc()` |

### A.2 CIP相关术语

| 术语 | 英文全称 | 解释 |
|------|----------|------|
| CIP | Clean-In-Place | 在线清洗，无需拆卸设备 |
| Zone | - | 清洗区域/清洗单元 |
| 配方 | Recipe | 清洗步骤和参数配置 |
| 介质 | Media | 清洗用的液体（碱液、酸液、水等） |
| 电导率 | Conductivity | 水的纯净度指标，μS/cm |
| 步骤 | Step | 清洗过程中的一个阶段 |

### A.3 PLC相关术语

| 术语 | 解释 | 在本项目中的位置 |
|------|------|-----------------|
| DB块 | Data Block，数据块，存储数据 | `DB100`-`DB105` |
| DB号 | DB块编号 | `db_number = 100 + zone_id` |
| 偏移量 | Offset，数据在块中的位置 | `offset 8 = temp_sp` |
| Rack | PLC机架号 | `settings.plc_rack = 0` |
| Slot | PLC插槽号 | `settings.plc_slot = 1` |
| REAL | 32位浮点数 | 温度、流量值 |
| INT | 16位整数 | 状态、步骤号 |
| BOOL | 布尔值 | 开关、运行状态 |

### A.4 状态枚举

| 状态码 | 状态名 | 含义 |
|--------|--------|------|
| 0 | IDLE | 空闲 |
| 1 | READY | 就绪 |
| 2 | STEP_EXEC | 执行中 |
| 3 | PAUSE | 暂停 |
| 4 | FAULT | 故障 |

### A.5 报警级别

| 级别 | 颜色 | 含义 |
|------|------|------|
| L1 | 红色 | 紧急报警，需立即处理 |
| L2 | 橙色 | 重要报警，需尽快处理 |
| L3 | 黄色 | 一般报警，注意观察 |

---

## 附录B：常见问题

### Q1: 什么是DB块？

**DB块（Data Block）** 是西门子PLC中存储数据的区域，类似数组：
```python
DB100 = [
    offset 0: zone_id (2字节),
    offset 2: state (2字节),
    offset 8: temp_sp (4字节),
    ...
]
```

### Q2: 为什么要轮询PLC？

PLC不像数据库，没有"推送"机制。后端必须定期主动读取：
```python
while True:
    data = plc.read()  # 主动拉取
    await asyncio.sleep(1)  # 等1秒
```

### Q3: Redis和数据库的区别？

| Redis | PostgreSQL |
|-------|-----------|
| 内存存储（极快） | 磁盘存储（持久） |
| 临时数据 | 永久数据 |
| Zone实时状态 | 历史记录 |

### Q4: 什么是CORS？

**跨域资源共享**，浏览器安全机制：
```
前端运行在 http://localhost:3000
后端运行在 http://localhost:8000
不同端口 = 不同域，浏览器默认禁止访问
CORS就是告诉浏览器："允许这个网站访问"
```

---

## 学习路径建议

1. **第一天**：安装Docker，看懂docker-compose配置
2. **第二天**：配置.env环境变量，理解配置管理
3. **第三天**：看懂main.py的API定义
4. **第四天**：理解plc_service.py的通信逻辑
5. **第五天**：学习Redis缓存和PostgreSQL数据库
6. **第六天**：写自己的API接口
7. **第七天**：写单元测试

---

## 进阶主题

| 主题 | 说明 |
|------|------|
| Docker生产部署 | 使用Nginx反向代理、HTTPS配置 |
| 数据库迁移 | 使用Alembic管理数据库版本 |
| 日志系统 | 结构化日志、日志收集分析 |
| 监控告警 | Prometheus + Grafana监控 |
| API认证 | JWT Token认证 |
| MQTT集成 | 设备数据上报云平台 |

---

*文档版本：1.3*
*最后更新：2026-05-14*
