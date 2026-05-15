# CIP清洗系统 - 审计追踪规格

> 文档版本: v1.0
> 创建日期: 2026-05-13
> 工段: CP (CIP Cleaning In Place)
> 用途: 操作日志、电子签名、21 CFR Part 11合规

---

## 1. 概述

### 1.1 审计追踪架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           审计追踪系统架构                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          操作事件采集层                                   │   │
│  │                                                                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ 登录/登出│  │ 参数修改│  │ 清洗控制│  │ 报警操作│              │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │   │
│  └────────┼────────────┴────────────┴─────────────┴─────────────────────────┘   │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          审计日志处理层                                  │   │
│  │                                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                     AuditLogger                                    │   │   │
│  │  │  • 事件分类                                                       │   │   │
│  │  │  • 电子签名生成                                                   │   │   │   │
│  │  │  • 防篡改校验                                                     │   │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          安全存储层                                     │   │
│  │                                                                          │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│  │  │                  PostgreSQL (审计表)                               │   │   │
│  │  │  • 事件ID、时间、用户、类型                                         │   │   │
│  │  │  • 操作详情、签名                                                   │   │   │
│  │  │  • 前值/后值                                                       │   │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 合规要求

| 要求 | 说明 | 实现 |
|------|------|------|
| **21 CFR Part 11** | 电子记录/签名法规 | 审计追踪、签名绑定 |
| **数据完整性** | ALCOA+原则 | 不可篡改、完整追溯 |
| **用户身份验证** | 用户名+密码 | 登录日志 |
| **操作不可否认性** | 电子签名 | 操作与签名绑定 |

---

## 2. 审计事件分类

### 2.1 事件类型定义

| 类别 | 代码 | 说明 | 签名要求 |
|------|------|------|----------|
| **用户管理** | AUTH | 登录、登出、密码修改 | 否 |
| **清洗操作** | CLEAN | 启动、暂停、停止、跳步 | 是 |
| **参数修改** | PARAM | PID、配方、报警限值修改 | 是 |
| **配方管理** | RECIPE | 配方创建、修改、删除 | 是 |
| **报警操作** | ALARM | 报警确认、复位 | 是 |
| **数据操作** | DATA | 数据导出、删除 | 是 |
| **系统配置** | SYS | 系统参数、时间修改 | 是 |
| **阀门操作** | VALVE | 手动阀门控制 | 是 |

### 2.2 详细事件清单

| 事件代码 | 事件描述 | 类别 | 签名级别 |
|----------|----------|------|----------|
| AUTH_LOGIN | 用户登录系统 | AUTH | - |
| AUTH_LOGOUT | 用户登出系统 | AUTH | - |
| AUTH_FAIL | 登录失败 | AUTH | - |
| AUTH_PWD_CHANGE | 修改密码 | AUTH | - |
| CLEAN_START | 启动清洗 | CLEAN | L1 |
| CLEAN_PAUSE | 暂停清洗 | CLEAN | L1 |
| CLEAN_RESUME | 恢复清洗 | CLEAN | L1 |
| CLEAN_STOP | 停止清洗 | CLEAN | L1 |
| CLEAN_SKIP | 跳步操作 | CLEAN | L2 |
| CLEAN_ABORT | 中止清洗 | CLEAN | L2 |
| PARAM_PID | 修改PID参数 | PARAM | L2 |
| PARAM_ALARM | 修改报警限值 | PARAM | L2 |
| PARAM_RECIPE | 修改配方参数 | PARAM | L2 |
| RECIPE_CREATE | 创建配方 | RECIPE | L2 |
| RECIPE_MODIFY | 修改配方 | RECIPE | L2 |
| RECIPE_DELETE | 删除配方 | RECIPE | L3 |
| ALARM_ACK | 报警确认 | ALARM | L1 |
| ALARM_RESET | 报警复位 | ALARM | L2 |
| DATA_EXPORT | 数据导出 | DATA | L1 |
| DATA_DELETE | 数据删除 | DATA | L3 |
| VALVE_OPEN | 打开阀门 | VALVE | L1 |
| VALVE_CLOSE | 关闭阀门 | VALVE | L1 |

---

## 3. 数据库设计

### 3.1 审计日志表

```sql
CREATE TABLE cip_audit_log (
    -- 主键
    id BIGSERIAL PRIMARY KEY,
    audit_id VARCHAR(36) NOT NULL UNIQUE,  -- UUID

    -- 事件信息
    event_code VARCHAR(30) NOT NULL,        -- 事件代码
    event_category VARCHAR(20) NOT NULL,    -- 事件类别
    event_description VARCHAR(200),         -- 事件描述

    -- 用户信息
    user_id INTEGER,                         -- 用户ID
    user_name VARCHAR(50),                   -- 用户名
    user_role VARCHAR(20),                   -- 用户角色

    -- 签名信息
    signature_required BOOLEAN DEFAULT FALSE, -- 是否需要签名
    signature_data VARCHAR(500),              -- 签名数据(电子签名)
    signed_at TIMESTAMP,                     -- 签名时间

    -- 操作上下文
    zone_id INTEGER,                         -- 相关区域
    batch_id VARCHAR(20),                    -- 相关批次
    equipment_id VARCHAR(30),               -- 相关设备

    -- 操作详情
    action_type VARCHAR(20),                 -- 操作类型
    previous_value TEXT,                     -- 修改前的值
    new_value TEXT,                          -- 修改后的值
    reason TEXT,                             -- 操作原因

    -- 元数据
    ip_address VARCHAR(45),                  -- 客户端IP
    user_agent VARCHAR(200),                 -- 浏览器信息
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_timestamp (timestamp),
    INDEX idx_user (user_id, timestamp),
    INDEX idx_event_category (event_category, timestamp),
    INDEX idx_batch (batch_id),
    INDEX idx_zone (zone_id, timestamp)
);
```

### 3.2 电子签名配置表

```sql
CREATE TABLE cip_signature_config (
    id SERIAL PRIMARY KEY,
    event_code VARCHAR(30) NOT NULL UNIQUE,
    signature_required BOOLEAN DEFAULT FALSE,
    signature_level INTEGER DEFAULT 1,       -- 1=L1单签, 2=L2双签
    approver_role VARCHAR(20),              -- 审批角色要求
    comment_required BOOLEAN DEFAULT FALSE, -- 是否需要注释
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. 电子签名机制

### 4.1 签名级别

| 级别 | 说明 | 要求 | 示例 |
|------|------|------|------|
| **L1** | 单签名 | 操作员确认 | 启动清洗、报警确认 |
| **L2** | 单签名+审批 | 技术员/工程师审批 | 跳步、参数修改 |
| **L3** | 双签名 | 操作员+工程师双重确认 | 删除配方、数据删除 |

### 4.2 签名数据结构

```python
class ElectronicSignature:
    """电子签名"""

    def __init__(
        self,
        user_id: int,
        user_name: str,
        user_role: str,
        action: str,
        reason: str = None,
        password: str = None
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.user_role = user_role
        self.action = action
        self.reason = reason
        self.timestamp = datetime.now()

        # 签名数据生成
        self.signature_data = self._generate_signature_data(password)

    def _generate_signature_data(self, password: str = None) -> str:
        """生成签名数据"""

        # 签名内容 = 用户ID + 用户名 + 操作 + 时间戳 + (密码哈希)
        content = (
            f"{self.user_id}|"
            f"{self.user_name}|"
            f"{self.action}|"
            f"{self.timestamp.isoformat()}"
        )

        if password:
            # 添加密码哈希防止他人冒用
            content += f"|{hashlib.sha256(password.encode()).hexdigest()}"

        # 生成签名
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{content}|{signature}"

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_role": self.user_role,
            "action": self.action,
            "reason": self.reason,
            "signed_at": self.timestamp.isoformat(),
            "signature_data": self.signature_data
        }
```

### 4.3 签名验证

```python
async def verify_signature(signature_data: str) -> bool:
    """验证签名完整性"""

    try:
        parts = signature_data.split('|')

        if len(parts) < 5:
            return False

        # 提取签名内容
        content = '|'.join(parts[:-1])
        original_signature = parts[-1]

        # 重新计算签名
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()

        # 验证签名一致性
        return hmac.compare_digest(original_signature, expected_signature)

    except Exception:
        return False


async def log_with_signature(
    event_code: str,
    user: dict,
    context: dict,
    signature: ElectronicSignature = None
):
    """记录带签名的审计日志"""

    # 如果事件需要签名但未提供，抛出异常
    if requires_signature(event_code) and not signature:
        raise ValueError(f"事件 {event_code} 需要电子签名")

    # 写入审计日志
    audit_log = CipAuditLog(
        audit_id=str(uuid.uuid4()),
        event_code=event_code,
        event_category=get_category(event_code),
        event_description=get_description(event_code),
        user_id=user['user_id'],
        user_name=user['user_name'],
        user_role=user['role'],
        signature_required=signature is not None,
        signature_data=signature.signature_data if signature else None,
        signed_at=signature.timestamp if signature else None,
        zone_id=context.get('zone_id'),
        batch_id=context.get('batch_id'),
        action_type=context.get('action_type'),
        previous_value=context.get('previous_value'),
        new_value=context.get('new_value'),
        reason=context.get('reason'),
        ip_address=context.get('ip_address'),
        user_agent=context.get('user_agent')
    )

    db.add(audit_log)
    db.commit()
```

---

## 5. 操作日志记录

### 5.1 装饰器方式记录

```python
from functools import wraps

def audit_log(event_code: str, signature_level: int = None):
    """审计日志装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取当前用户
            user = get_current_user()

            # 获取上下文
            context = extract_context(args, kwargs)

            # 如果需要签名，弹出签名对话框
            if signature_level:
                signature = await request_signature(
                    event_code,
                    user,
                    context
                )
            else:
                signature = None

            # 执行操作
            result = await func(*args, **kwargs)

            # 记录审计日志
            await log_with_signature(
                event_code=event_code,
                user=user,
                context=context,
                signature=signature
            )

            return result

        return wrapper
    return decorator


# 使用示例
@router.post("/cleaning/start")
@audit_log("CLEAN_START", signature_level=1)
async def start_cleaning(zone_id: int, recipe_id: int):
    """启动清洗"""
    # 业务逻辑
    pass
```

### 5.2 中间件自动记录

```python
# audit_middleware.py
class AuditMiddleware:
    """审计中间件 - 自动记录所有API调用"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 忽略健康检查等内部接口
            if self._should_audit(scope):
                await self._log_request(scope, receive)

        await self.app(scope, receive, send)

    def _should_audit(self, scope) -> bool:
        """判断是否需要审计"""
        path = scope.get("path", "")
        method = scope.get("method", "")

        # 忽略静态文件和健康检查
        if path.startswith("/static"):
            return False
        if path == "/health":
            return False

        # POST/PUT/DELETE 操作需要审计
        return method in ["POST", "PUT", "DELETE", "PATCH"]

    async def _log_request(self, scope, receive):
        """记录请求"""
        user = await get_user_from_scope(scope)
        body = await self._get_body(receive)

        audit_log = CipAuditLog(
            audit_id=str(uuid.uuid4()),
            event_code="API_CALL",
            event_category="API",
            event_description=f"{scope['method']} {scope['path']}",
            user_id=user.get('user_id'),
            user_name=user.get('user_name'),
            user_role=user.get('role'),
            new_value=body[:1000],  # 限制长度
            ip_address=get_client_ip(scope)
        )

        db.add(audit_log)
        await db.commit()
```

---

## 6. 审计查询

### 6.1 审计日志查询API

```python
@router.get("/audit/logs")
async def get_audit_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    event_category: Optional[str] = None,
    zone_id: Optional[int] = None,
    batch_id: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0
):
    """查询审计日志"""

    query = db.query(CipAuditLog)

    # 条件过滤
    if start_date:
        query = query.filter(CipAuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(CipAuditLog.timestamp <= end_date)
    if user_id:
        query = query.filter(CipAuditLog.user_id == user_id)
    if event_category:
        query = query.filter(CipAuditLog.event_category == event_category)
    if zone_id:
        query = query.filter(CipAuditLog.zone_id == zone_id)
    if batch_id:
        query = query.filter(CipAuditLog.batch_id == batch_id)

    # 按时间倒序
    logs = query.order_by(
        CipAuditLog.timestamp.desc()
    ).offset(offset).limit(limit).all()

    # 统计总数
    total = query.count()

    return {
        "logs": logs,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/audit/log/{audit_id}")
async def get_audit_log_detail(audit_id: str):
    """获取审计日志详情"""

    log = db.query(CipAuditLog).filter(
        CipAuditLog.audit_id == audit_id
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="审计日志不存在")

    # 验证签名
    if log.signature_data:
        log.signature_valid = await verify_signature(log.signature_data)
    else:
        log.signature_valid = None

    return log
```

### 6.2 签名验证

```python
@router.post("/audit/verify-signature/{audit_id}")
async def verify_audit_signature(audit_id: str):
    """验证审计日志签名"""

    log = db.query(CipAuditLog).filter(
        CipAuditLog.audit_id == audit_id
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="审计日志不存在")

    if not log.signature_data:
        return {"verified": None, "message": "无需验证"}

    verified = await verify_signature(log.signature_data)

    return {
        "verified": verified,
        "message": "签名有效" if verified else "签名无效或已篡改"
    }
```

---

## 7. HMI显示

### 7.1 审计日志查询

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  审计日志                                                    [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  筛选条件:                                                                    │
│  日期: [2026-05-06▼]~[2026-05-13▼]  类别: [全部▼]  用户: [全部▼]            │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 时间              │ 类别 │ 用户   │ 事件描述                    │ 签名  │   │
│  ├───────────────────┼───────┼────────┼─────────────────────────────┼───────┤   │
│  │ 05-13 17:35:21  │ CLEAN │ 张三   │ 1区清洗启动                 │ ✓    │   │
│  │ 05-13 17:30:15  │ PARAM │ 李四   │ 修改PID参数 Kp=2.5→3.0     │ ✓    │   │
│  │ 05-13 17:25:03  │ AUTH  │ 李四   │ 登录系统                   │      │   │
│  │ 05-13 17:20:45  │ ALARM │ 张三   │ 报警确认 CP-005            │ ✓    │   │
│  │ 05-13 17:15:30  │ RECIPE│ 王五   │ 创建配方 USER-NEW-01       │ ✓    │   │
│  │ 05-13 17:10:12  │ CLEAN │ 张三   │ 5区清洗停止                 │ ✓    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  显示 1-6/1,234 条  [上一页] [下一页]  [导出]  [筛选]                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 电子签名对话框

```
┌───────────────────────────────────────────────────────────────┐
│  电子签名                                                    │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  操作: 启动清洗                                              │
│  区域: 1区-水处理                                            │
│  配方: WTCIP-01                                              │
│                                                               │
│  请输入操作原因 (可选):                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 日常清洗，按计划执行                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  用户: 张三 (操作员)                                         │
│  密码: [************************]                             │
│                                                               │
│           [取消]                          [确认并签名]         │
└───────────────────────────────────────────────────────────────┘
```

### 7.3 签名详情

```
┌───────────────────────────────────────────────────────────────┐
│  签名详情                                                    │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  操作: 1区清洗启动                                            │
│  时间: 2026-05-13 17:35:21                                    │
│                                                               │
│  签名信息:                                                    │
│  ─────────────────────────────────────────────               │
│  用户: 张三                                                   │
│  角色: 操作员                                                 │
│  签名级别: L1 (单签名)                                        │
│  签名时间: 2026-05-13 17:35:21                               │
│                                                               │
│  签名验证: ✓ 有效                                             │
│                                                               │
│  签名数据:                                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 1|张三|start_cleaning|2026-05-13T17:35:21|            │ │
│  │ a7f2b8c3d4e5...                                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│                                                    [关闭]     │
└───────────────────────────────────────────────────────────────┘
```

---

## 8. 审计报告

### 8.1 审计报告生成

```python
@router.get("/audit/report")
async def generate_audit_report(
    start_date: datetime,
    end_date: datetime,
    format: str = "html"  # html, pdf
):
    """生成审计报告"""

    # 查询时间段内的审计日志
    logs = db.query(CipAuditLog).filter(
        CipAuditLog.timestamp >= start_date,
        CipAuditLog.timestamp <= end_date
    ).order_by(CipAuditLog.timestamp).all()

    # 统计
    stats = {
        "total_events": len(logs),
        "by_category": {},
        "by_user": {},
        "signature_required": sum(1 for l in logs if l.signature_required),
        "signature_provided": sum(1 for l in logs if l.signature_data)
    }

    for log in logs:
        # 按类别统计
        if log.event_category not in stats["by_category"]:
            stats["by_category"][log.event_category] = 0
        stats["by_category"][log.event_category] += 1

        # 按用户统计
        if log.user_name not in stats["by_user"]:
            stats["by_user"][log.user_name] = 0
        stats["by_user"][log.user_name] += 1

    report = {
        "title": "CIP系统审计报告",
        "period": f"{start_date} 至 {end_date}",
        "generated_at": datetime.now(),
        "statistics": stats,
        "logs": [
            {
                "timestamp": l.timestamp.isoformat(),
                "event_code": l.event_code,
                "event_description": l.event_description,
                "user_name": l.user_name,
                "user_role": l.user_role,
                "signature": "✓" if l.signature_data else "-",
                "zone_id": l.zone_id,
                "batch_id": l.batch_id
            }
            for l in logs
        ]
    }

    return report
```

---

## 9. 数据保留

| 数据类型 | 保留时间 | 说明 |
|----------|----------|------|
| 审计日志 | **180天** | 21 CFR Part 11要求 |
| 电子签名 | **180天** | 与审计日志同步 |
| 用户会话 | 90天 | 会话日志 |

---

**文档状态**: ✅ 已完成
**版本**: v1.0
**依赖**: 批次追踪规格 ✅
