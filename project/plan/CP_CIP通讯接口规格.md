# CIP清洗系统 - SCADA与PLC通讯接口规格

> 文档版本: v1.0
> 创建日期: 2026-05-13
> 工段: CP (CIP Cleaning In Place)
> PLC: PLC-16 (192.168.2.26)
> 协议: S7 COMM (python-snap7)
> 用途: SCADA Server与PLC-16之间的实时数据通讯

---

## 1. 概述

### 1.1 通讯架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SCADA通讯架构                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           SCADA Server (Python)                         │   │
│  │  • snap7 client (PLC通讯)                                               │   │
│  │  • Redis (实时数据缓存)                                                  │   │
│  │  • MQTT broker (数据发布)                                                │   │
│  │  • WebSocket server (前端推送)                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                          │
│                                      │ S7 COMM (TCP/IP)                        │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           PLC-16 (S7-1500)                              │   │
│  │  • CPU 1515-2 PN                                                        │   │
│  │  • PROFINET通讯                                                        │   │
│  │  • IP: 192.168.2.26                                                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 通讯参数

| 参数 | 值 | 说明 |
|------|-----|------|
| PLC IP | 192.168.2.26 | PLC-16以太网口 |
| PLC Rack | 0 | 机架号 |
| PLC Slot | 1 | 槽位号 |
| 通讯超时 | 5000ms | 连接超时时间 |
| 轮询周期 | 1000ms | 数据读取周期 |
| 重连间隔 | 5000ms | 断线重连间隔 |

---

## 2. 数据块定义

### 2.1 DB块分配表

| DB号 | 名称 | 类型 | 大小 | 用途 |
|------|------|------|------|------|
| DB1 | Global | System | 200字节 | 系统状态、介质状态、罐区状态 |
| DB100 | Zone1 | ZoneData | 300字节 | 1区状态数据 |
| DB101 | Zone2 | ZoneData | 300字节 | 2区状态数据 |
| DB102 | Zone3 | ZoneData | 300字节 | 3区状态数据 |
| DB103 | Zone4 | ZoneData | 300字节 | 4区状态数据 |
| DB104 | Zone5 | ZoneData | 300字节 | 5区状态数据 |
| DB200 | Alarm | Alarm[50] | 1000字节 | 报警信息数组 |
| DB300 | History | History[100] | 5000字节 | 历史记录数组 |
| DB400 | Recipe | Recipe[10] | 2000字节 | 配方数据 |
| DB500 | PID_Temp | PIDParams | 100字节 | 温度PID参数 |
| DB501-505 | PID_Flow[1-5] | PIDParams | 500字节 | 5区流量PID参数 |

### 2.2 全局数据 (DB1)

| 偏移 | 变量名 | 数据类型 | 说明 |
|------|--------|----------|------|
| 0.0 | System.HandsMode | INT | 就地/远程模式 (0=LOCAL, 1=REMOTE) |
| 2.0 | System.AutoMode | BOOL | 自动模式 |
| 4.0 | System.ManualMode | BOOL | 手动模式 |
| 6.0 | System.SystemReady | BOOL | 系统就绪 |
| 8.0 | System.EStop | BOOL | 急停 |
| 10.0 | System.Running | BOOL | 运行中 |
| 12.0 | System.AllIdle | BOOL | 全部待机 |
| 14.0 | System.PLCConnected | BOOL | PLC连接状态 |
| 16.0 | System.HMIConnected | BOOL | HMI连接状态 |
| 18.0 | System.ActiveZones | INT | 活跃区域数 |
| 20.0 | System.AlarmCount | INT | 激活报警数 |
| 22.0 | System.QueueCount | INT | 队列长度 |
| 24.0 | System.SystemTime | LDT | 系统时间 |

### 2.3 区域数据 (DB100-DB104)

| 偏移 | 变量名 | 数据类型 | 说明 |
|------|--------|----------|------|
| 0.0 | Zone.ZoneID | INT | 区域ID (1-5) |
| 2.0 | Zone.State | INT | 清洗状态 (0-6) |
| 4.0 | Zone.CurrentStep | INT | 当前步骤索引 |
| 6.0 | Zone.StepTimer | INT | 步骤计时(秒) |
| 8.0 | Zone.Command | INT | 控制命令 |
| 10.0 | Zone.Result | BOOL | 清洗结果 |
| 12.0 | Zone.CurrentMedia | INT | 当前介质 |
| 14.0 | Zone.TempControl | BOOL | 温度控制使能 |
| 16.0 | Zone.TempSP | REAL | 温度设定值 |
| 20.0 | Zone.TempReached | BOOL | 温度达标 |
| 22.0 | Zone.TT_Outlet | REAL | 出口温度(℃) |
| 26.0 | Zone.TT_Return | REAL | 回流温度(℃) |
| 30.0 | Zone.CD | REAL | 电导率(μS/cm) |
| 34.0 | Zone.PT | REAL | 管路压力(MPa) |
| 38.0 | Zone.FT | REAL | 清洗流量(m³/h) |
| 42.0 | Zone.FS | BOOL | 流动开关 |
| 44.0 | Zone.PumpCmd | BOOL | 泵命令 |
| 46.0 | Zone.PumpSpeed | REAL | 泵速度(%) |
| 50.0 | Zone.PumpState | INT | 泵状态 |
| 52.0 | Zone.ValveState | INT | 阀门状态 |

### 2.4 报警数据 (DB200)

| 偏移 | 变量名 | 数据类型 | 说明 |
|------|--------|----------|------|
| 0.0 | Alarm[1].AlarmID | INT | 报警ID |
| 2.0 | Alarm[1].AlarmCode | INT | 报警代码 |
| 4.0 | Alarm[1].AlarmText | STRING[50] | 报警文本 |
| 56.0 | Alarm[1].Level | INT | 报警等级 (0=L0, 1=L1, 2=L2) |
| 58.0 | Alarm[1].ZoneID | INT | 相关区域 (0=全局) |
| 60.0 | Alarm[1].TriggerTime | LDT | 触发时间 |
| 68.0 | Alarm[1].Status | INT | 状态 (0=激活, 1=确认, 2=恢复) |

每个报警占用54字节，数组大小50。

---

## 3. 传感器数据映射

### 3.1 模拟量输入 (AI)

| PLC变量 | 数据类型 | 说明 | 单位 |
|---------|----------|------|------|
| AI_TT_Outlet[1-5] | REAL | 1-5区出口温度 | ℃ |
| AI_TT_Return[1-5] | REAL | 1-5区回流温度 | ℃ |
| AI_Conductivity[1-5] | REAL | 1-5区电导率 | μS/cm |
| AI_Pressure[1-5] | REAL | 1-5区管路压力 | MPa |
| AI_Flow[1-5] | REAL | 1-5区清洗流量 | m³/h |
| AI_TankLevel[1-4] | REAL | 碱/酸/热水/纯水罐液位 | % |
| AI_TankTemp[1-4] | REAL | 碱/酸/热水/纯水罐温度 | ℃ |
| AI_TankConc[1-2] | REAL | 碱/酸罐浓度 | % |

### 3.2 数字量输入 (DI)

| PLC变量 | 数据类型 | 说明 |
|---------|----------|------|
| DI_FlowSwitch[1-5] | BOOL | 1-5区流动开关 |
| DI_PumpOverload[1-5] | BOOL | 1-5区泵过载 |
| DI_ValveFeedback[1-25] | BOOL | 1-25号阀反馈 |
| DI_TankLLSL[1-4] | BOOL | 碱/酸/热水/纯水罐低液位 |
| DI_TankLSH[1-4] | BOOL | 碱/酸/热水/纯水罐高液位 |

### 3.3 数字量输出 (DO)

| PLC变量 | 数据类型 | 说明 |
|---------|----------|------|
| DO_PumpCmd[1-5] | BOOL | 1-5区泵启动命令 |
| DO_PumpSpeed[1-5] | INT | 1-5区泵速度 (0-100%) |
| DO_ValveCmd[1-25] | BOOL | 1-25号阀开命令 |
| DO_SteamValve | INT | 蒸汽阀开度 (0-100%) |
| DO_Buzzer | BOOL | 蜂鸣器 |

---

## 4. 报警代码定义

| 报警号 | 描述 | 等级 | 处理建议 |
|--------|------|------|----------|
| CP-001 | 碱液罐液位低 | L2 | 补充碱液 |
| CP-002 | 酸液罐液位低 | L2 | 补充酸液 |
| CP-003 | 热水罐液位低 | L2 | 补充热水 |
| CP-004 | 纯水罐液位低 | L2 | 补充纯水 |
| CP-005 | 清洗温度不达标 | L1 | 检查蒸汽阀/加热器 |
| CP-006 | 电导率超标 | L1 | 增加冲洗时间 |
| CP-008 | 管路压力异常 | L2 | 检查泵/阀门 |
| CP-009 | 清洗泵过载 | L0 | 检查泵/清除堵塞 |
| CP-012 | 1区无流量 | L1 | 检查管路/阀门 |
| CP-013 | 2区无流量 | L1 | 检查管路/阀门 |
| CP-014 | 3区无流量 | L1 | 检查管路/阀门 |
| CP-015 | 4区无流量 | L1 | 检查管路/阀门 |
| CP-016 | 5区无流量 | L1 | 检查管路/阀门 |
| CP-017 | 急停触发 | L0 | 复位急停 |
| CP-018 | 清洗序列非法 | L1 | 检查配方配置 |

---

## 5. 通讯接口代码

### 5.1 PLC通讯客户端

```python
# plc_client.py
"""
CIP系统PLC通讯客户端
使用python-snap7与S7-1500 PLC通讯
"""

import snap7
from snap7.util import *
import struct
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import json
import redis
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class PLCClient:
    """PLC通讯客户端"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = snap7.client.Client()
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=6379,
            db=0,
            decode_responses=True
        )
        self.mqtt_client = mqtt.Client()
        self.connected = False

        # 轮询周期 (ms)
        self.poll_interval = config.get('poll_interval', 1000)

    def connect(self) -> bool:
        """连接PLC"""
        try:
            self.client.connect(
                self.config['plc_ip'],
                self.config.get('rack', 0),
                self.config.get('slot', 1)
            )
            self.connected = True
            logger.info(f"PLC连接成功: {self.config['plc_ip']}")
            return True
        except Exception as e:
            logger.error(f"PLC连接失败: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开PLC连接"""
        if self.connected:
            self.client.disconnect()
            self.connected = False
            logger.info("PLC已断开")

    def read_db(self, db_number: int, size: int) -> Optional[bytes]:
        """读取数据块"""
        if not self.connected:
            return None
        try:
            return self.client.db_read(db_number, 0, size)
        except Exception as e:
            logger.error(f"读取DB{db_number}失败: {e}")
            return None

    def write_db(self, db_number: int, start: int, data: bytes) -> bool:
        """写入数据块"""
        if not self.connected:
            return False
        try:
            self.client.db_write(db_number, start, data)
            return True
        except Exception as e:
            logger.error(f"写入DB{db_number}失败: {e}")
            return False

    def read_system_status(self) -> Optional[Dict[str, Any]]:
        """读取系统状态 (DB1)"""
        data = self.read_db(1, 200)
        if not data:
            return None

        return {
            'hands_mode': struct.unpack('H', data[0:2])[0],
            'auto_mode': bool(data[2]),
            'manual_mode': bool(data[4]),
            'system_ready': bool(data[6]),
            'e_stop': bool(data[8]),
            'running': bool(data[10]),
            'all_idle': bool(data[12]),
            'plc_connected': bool(data[14]),
            'hmi_connected': bool(data[16]),
            'active_zones': struct.unpack('H', data[18:20])[0],
            'alarm_count': struct.unpack('H', data[20:22])[0],
            'queue_count': struct.unpack('H', data[22:24])[0],
        }

    def read_zone_data(self, zone_id: int) -> Optional[Dict[str, Any]]:
        """读取区域状态数据 (DB100-DB104)"""
        db_number = 100 + zone_id - 1
        data = self.read_db(db_number, 300)
        if not data:
            return None

        return {
            'zone_id': struct.unpack('H', data[0:2])[0],
            'state': struct.unpack('H', data[2:4])[0],
            'current_step': struct.unpack('H', data[4:6])[0],
            'step_timer': struct.unpack('I', data[6:10])[0],
            'command': struct.unpack('H', data[8:10])[0],
            'result': bool(data[10]),
            'current_media': struct.unpack('H', data[12:14])[0],
            'temp_control': bool(data[14]),
            'temp_sp': struct.unpack('f', data[16:20])[0],
            'temp_reached': bool(data[20]),
            'tt_outlet': struct.unpack('f', data[22:26])[0],
            'tt_return': struct.unpack('f', data[26:30])[0],
            'cd': struct.unpack('f', data[30:34])[0],
            'pt': struct.unpack('f', data[34:38])[0],
            'ft': struct.unpack('f', data[38:42])[0],
            'fs': bool(data[42]),
            'pump_cmd': bool(data[44]),
            'pump_speed': struct.unpack('f', data[46:50])[0],
            'pump_state': struct.unpack('H', data[50:52])[0],
            'valve_state': struct.unpack('H', data[52:54])[0],
        }

    def write_zone_command(self, zone_id: int, command: int) -> bool:
        """写入区域控制命令"""
        db_number = 100 + zone_id - 1
        data = bytearray(300)
        struct.pack_into('H', data, 8, command)  # Command偏移量8
        return self.write_db(db_number, 0, bytes(data))

    def read_alarms(self, count: int = 50) -> list:
        """读取报警信息 (DB200)"""
        data = self.read_db(200, 54 * count)
        if not data:
            return []

        alarms = []
        alarm_size = 54
        for i in range(count):
            offset = i * alarm_size
            alarm_id = struct.unpack('H', data[offset:offset+2])[0]
            if alarm_id == 0:
                continue

            alarms.append({
                'alarm_id': alarm_id,
                'alarm_code': struct.unpack('H', data[offset+2:offset+4])[0],
                'level': struct.unpack('H', data[offset+56:offset+58])[0],
                'zone_id': struct.unpack('H', data[offset+58:offset+60])[0],
                'status': struct.unpack('H', data[offset+68:offset+70])[0],
            })
        return alarms

    def publish_to_redis(self, key: str, data: Dict[str, Any]):
        """发布数据到Redis"""
        try:
            self.redis_client.publish(key, json.dumps(data))
            self.redis_client.set(key, json.dumps(data), ex=60)
        except Exception as e:
            logger.error(f"Redis发布失败: {e}")

    def publish_to_mqtt(self, topic: str, data: Dict[str, Any]):
        """发布数据到MQTT"""
        try:
            self.mqtt_client.publish(topic, json.dumps(data))
        except Exception as e:
            logger.error(f"MQTT发布失败: {e}")

    def poll_and_publish(self):
        """轮询PLC数据并发布"""
        # 读取系统状态
        system_status = self.read_system_status()
        if system_status:
            self.publish_to_redis('cip/system/status', system_status)
            self.publish_to_mqtt('cip/system/status', system_status)

        # 读取5区数据
        for zone_id in range(1, 6):
            zone_data = self.read_zone_data(zone_id)
            if zone_data:
                self.publish_to_redis(f'cip/zone/{zone_id}/status', zone_data)
                self.publish_to_mqtt(f'cip/zone/{zone_id}/status', zone_data)

        # 读取报警
        alarms = self.read_alarms()
        self.publish_to_redis('cip/alarms', alarms)
        self.publish_to_mqtt('cip/alarms', alarms)


# 状态映射表
CLEAN_STATE_MAP = {
    0: 'IDLE',       # 待机
    1: 'READY',       # 准备就绪
    2: 'STEP_EXEC',  # 步骤执行中
    3: 'STEP_TRANSITION',  # 步骤切换中
    4: 'COMPLETE',   # 清洗完成
    5: 'PAUSE',      # 暂停
    6: 'FAULT',      # 故障
}

MEDIA_TYPE_MAP = {
    0: 'PURE_WATER',   # 纯水冲洗
    1: 'ALKALI',        # 碱洗
    2: 'ACID',          # 酸洗
    3: 'HOT_WATER',     # 热水洗
    4: 'DISINFECT',     # 消毒液
}

ALARM_LEVEL_MAP = {
    0: 'L0_CRITICAL',  # 严重
    1: 'L1_WARNING',   # 警告
    2: 'L2_INFO',      # 提示
}
```

### 5.2 配置文件

```yaml
# plc_comm_config.yaml
plc:
  plc_ip: "192.168.2.26"
  rack: 0
  slot: 1
  connection_timeout: 5000
  poll_interval: 1000
  reconnect_interval: 5000

redis:
  host: "localhost"
  port: 6379
  db: 0

mqtt:
  broker: "localhost"
  port: 1883
  topic_prefix: "cip"

databases:
  system: 1
  zones:
    - 100  # Zone1
    - 101  # Zone2
    - 102  # Zone3
    - 103  # Zone4
    - 104  # Zone5
  alarm: 200
  history: 300
  recipe: 400
  pid_temp: 500
  pid_flow_start: 501
```

---

## 6. WebSocket数据推送

### 6.1 推送消息格式

```typescript
// 区域状态推送
interface ZoneStatusMessage {
  type: 'zone_status';
  zone_id: number;
  timestamp: number;
  data: {
    state: string;        // 'IDLE' | 'READY' | 'STEP_EXEC' | ...
    current_step: number;
    step_timer: number;
    tt_outlet: number;    // 出口温度
    tt_return: number;   // 回流温度
    cd: number;           // 电导率
    pt: number;           // 压力
    ft: number;           // 流量
    fs: boolean;          // 流动开关
    temp_reached: boolean;
    current_media: string;
    pump_speed: number;
  };
}

// 报警推送
interface AlarmMessage {
  type: 'alarm';
  timestamp: number;
  data: {
    alarm_id: number;
    alarm_code: number;
    level: string;        // 'L0_CRITICAL' | 'L1_WARNING' | 'L2_INFO'
    zone_id: number;
    status: string;       // 'ACTIVE' | 'ACKED' | 'CLEARED'
    trigger_time: string;
  };
}

// 系统状态推送
interface SystemStatusMessage {
  type: 'system_status';
  timestamp: number;
  data: {
    hands_mode: string;
    auto_mode: boolean;
    system_ready: boolean;
    e_stop: boolean;
    running: boolean;
    all_idle: boolean;
    active_zones: number;
    alarm_count: number;
    queue_count: number;
  };
}
```

### 6.2 订阅主题

| 主题 | 说明 | 频率 |
|------|------|------|
| cip/system/status | 系统状态 | 1s |
| cip/zone/+/status | 各区状态 | 1s |
| cip/alarms | 报警信息 | 事件触发 |
| cip/tank/+/status | 罐区状态 | 5s |

---

## 7. 错误处理

### 7.1 错误码定义

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| E001 | PLC连接超时 | 检查网络/PLC状态 |
| E002 | PLC连接拒绝 | 检查IP/端口配置 |
| E003 | 数据读取失败 | 重试/检查PLC |
| E004 | 数据写入失败 | 重试/检查PLC |
| E005 | 通讯超时 | 增加超时时间 |
| E006 | 数据校验失败 | 检查数据完整性 |

### 7.2 重连策略

```
连接失败 → 等待5秒 → 重试 → 失败 → 等待10秒 → 重试 → ... → 最大等待60秒
```

---

## 8. 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 通讯周期 | ≤1s | 数据读取+推送 |
| 延迟 | ≤500ms | PLC→SCADA→前端 |
| 连接成功率 | ≥99.9% | 正常运行时间 |
| 重连时间 | ≤10s | 断线后恢复 |

---

**文档状态**: ✅ 已完成
**版本**: v1.0
