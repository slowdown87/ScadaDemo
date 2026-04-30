# PLC功能块规格说明书

> 文档版本: v1.0
> 创建日期: 2026-04-29
> 生成方式: 自动生成
> 关联配置: FB_Spec_Template.yaml

---

## 1. 概述

### 1.1 文档目的

本文档定义了茶饮料生产线SCADA系统中使用的所有PLC功能块的规格说明，包括：
- 功能块接口定义（输入/输出参数）
- 功能块参数配置
- 功能块逻辑说明
- 诊断代码定义

### 1.2 适用范围

- 项目: 茶饮料生产线SCADA系统
- PLC型号: Siemens S7-1500
- 编程标准: IEC 61131-3

## 2. 基础控制功能块

### FB_Valve_Control

**名称**: 阀门控制功能块
**描述**: 用于控制气动阀、调节阀的开关及开度调节
**版本**: v1.0
**类别**: 基础控制

#### FB_Valve_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iValve_Open | BOOL | 打开命令 |
| iValve_Close | BOOL | 关闭命令 |
| iValve_Stop | BOOL | 停止命令 |
| iValve_Reset | BOOL | 复位命令 |
| iValve_OpenFB | BOOL | 阀打开反馈 |
| iValve_CloseFB | BOOL | 阀关闭反馈 |
| iValve_Alarm | BOOL | 阀故障信号 |
| iValve_Interlock | BOOL | 阀联锁信号 (默认: FALSE) |
| iAuto_Mode | BOOL | 自动模式 |
| iManual_Speed | INT | 手动调节速度 (默认: 50) 范围: 0-100 |

#### FB_Valve_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qValve_OpenCmd | BOOL | 阀打开命令 |
| qValve_CloseCmd | BOOL | 阀关闭命令 |
| qValve_StopCmd | BOOL | 阀停止命令 |
| qValve_ResetCmd | BOOL | 阀复位命令 |
| qValve_Position | INT | 阀开度位置 0-100% |
| qValve_Status | INT | 阀状态 0=未知,1=关闭中,2=打开中,3=打开,4=关闭,5=故障,6=联锁 |
| qValve_Ready | BOOL | 阀准备就绪 |
| qValve_Warning | BOOL | 阀警告 |
| qValve_Error | BOOL | 阀错误 |

#### FB_Valve_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Timeout_Open | TIME | T#10S | 打开超时时间 |
| Timeout_Close | TIME | T#10S | 关闭超时时间 |
| Enable_Interlock | BOOL | TRUE | 使能联锁检查 |

#### FB_Valve_Control 逻辑说明

- **1.状态判断**: 根据反馈信号判断当前阀状态
- **2.命令处理**: 收到打开/关闭命令后输出脉冲信号
- **3.超时检测**: 超过设定时间未到位触发报警
- **4.联锁检查**: 联锁信号有效时禁止操作
- **5.故障处理**: 故障信号有效时进入故障状态

#### FB_Valve_Control 诊断代码

| 代码 | 描述 |
|------|------|
| V001 | 阀打开超时 |
| V002 | 阀关闭超时 |
| V003 | 阀反馈异常 |
| V004 | 阀联锁激活 |
| V005 | 阀故障 |

---

### FB_Pump_Control

**名称**: 泵控制功能块
**描述**: 用于控制泵的启停、速度调节及状态监控
**版本**: v1.0
**类别**: 基础控制

#### FB_Pump_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iPump_Start | BOOL | 泵启动命令 |
| iPump_Stop | BOOL | 泵停止命令 |
| iPump_Reset | BOOL | 复位命令 |
| iPump_RunFB | BOOL | 泵运行反馈 |
| iPump_Fault | BOOL | 泵故障信号 |
| iPump_Overload | BOOL | 泵过载信号 |
| iPump_Interlock | BOOL | 泵联锁信号 (默认: FALSE) |
| iAuto_Mode | BOOL | 自动模式 |
| iSpeed_Setpoint | INT | 速度设定值 0-100% 范围: 0-100 |

#### FB_Pump_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qPump_StartCmd | BOOL | 泵启动命令 |
| qPump_StopCmd | BOOL | 泵停止命令 |
| qPump_ResetCmd | BOOL | 泵复位命令 |
| qPump_Speed | INT | 泵实际速度 0-100% |
| qPump_Status | INT | 泵状态 0=停止,1=启动中,2=运行,3=故障,4=过载,5=联锁 |
| qPump_Ready | BOOL | 泵准备就绪 |
| qPump_Warning | BOOL | 泵警告 |
| qPump_Error | BOOL | 泵错误 |

#### FB_Pump_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Start_Delay | TIME | T#2S | 启动延时 |
| Stop_Delay | TIME | T#3S | 停止延时 |
| Fault_Delay | TIME | T#1S | 故障确认延时 |
| Auto_Start | BOOL | FALSE | 液位联锁自动启动 |

#### FB_Pump_Control 逻辑说明

- **1.启动条件检查**: 检查联锁、手自动模式
- **2.启动命令输出**: 发出启动命令并计时
- **3.运行反馈检测**: 收到运行反馈后进入运行状态
- **4.速度调节**: 根据设定值调节泵速度
- **5.故障处理**: 过载或故障信号触发停机

#### FB_Pump_Control 诊断代码

| 代码 | 描述 |
|------|------|
| P001 | 泵启动超时 |
| P002 | 泵运行中停机 |
| P003 | 泵过载 |
| P004 | 泵联锁激活 |
| P005 | 泵电机过热 |

---

### FB_PID_Control

**名称**: PID控制功能块
**描述**: 通用PID控制器，用于温度、压力、流量、液位等过程控制
**版本**: v1.0
**类别**: 基础控制

#### FB_PID_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iPV | REAL | 过程值(测量值) |
| iSP | REAL | 设定值 |
| iPV_H | REAL | 过程值上限 |
| iPV_L | REAL | 过程值下限 |
| iAuto_Manual | BOOL | 自动/手动切换 TRUE=自动 |
| iManual_Output | REAL | 手动输出值 范围: 0.0-100.0 |
| iTrack_Input | BOOL | 跟踪输入使能 |
| iTrack_Value | REAL | 跟踪值 |
| iSP_Change | BOOL | 设定值变化信号(上升沿) |

#### FB_PID_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qOutput | REAL | PID输出值 0-100% |
| qOutput_RAW | INT | 原始输出值 0-27648 |
| qError | REAL | 当前偏差 SP-PV |
| qError_Deadband | REAL | 死区处理后偏差 |
| qMan_Output | REAL | 手动输出值(回读) |
| qMode | INT | 当前模式 0=手动,1=自动,2=跟踪 |
| qSP_Ramp | REAL | 当前设定值(斜坡后) |
| qAlarm_H | BOOL | 高报警 |
| qAlarm_L | BOOL | 低报警 |
| qAlarm_HH | BOOL | 高高报警 |
| qAlarm_LL | BOOL | 低低报警 |

#### FB_PID_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Kp | REAL | 1.0 | 比例增益 |
| Tn | TIME | T#40S | 积分时间 |
| Tv | TIME | T#10S | 微分时间 |
| Deadband | REAL | 0.5 | 死区宽度 |
| SP_Ramp | REAL | 0.0 | 设定值斜坡变化率 0=禁止 |
| Output_Min | REAL | 0.0 | 输出下限 |
| Output_Max | REAL | 100.0 | 输出上限 |
| Alarm_H_Dev | REAL | 10.0 | 高报警偏差 |
| Alarm_L_Dev | REAL | 10.0 | 低报警偏差 |
| Alarm_HH_Dev | REAL | 20.0 | 高高报警偏差 |
| Alarm_LL_Dev | REAL | 20.0 | 低低报警偏差 |

#### FB_PID_Control 逻辑说明

- **1.PV范围检查**: 检查过程值是否在合理范围
- **2.偏差计算**: 计算SP-PV，考虑死区
- **3.设定值斜坡**: 根据设定值变化率平滑过渡
- **4.PID计算**: 执行PID算法计算输出
- **5.输出限幅**: 将输出限制在设定范围内
- **6.报警判断**: 根据偏差生成各类报警

#### FB_PID_Control 诊断代码

| 代码 | 描述 |
|------|------|
| PID001 | 过程值超上限 |
| PID002 | 过程值超下限 |
| PID003 | 设定值超范围 |
| PID004 | 输出饱和 |

---

## 3. 工艺控制功能块

### FB_Level_Control

**名称**: 液位控制功能块
**描述**: 储罐液位控制，带高低液位联锁保护
**版本**: v1.0
**类别**: 工艺控制
**父功能块**: FB_PID_Control

#### FB_Level_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iLevel_PV | REAL | 液位过程值 % |
| iLevel_SP | REAL | 液位设定值 % |
| iAuto_Mode | BOOL | 自动模式 |
| iManual_Output | REAL | 手动输出值 |
| iLevel_H | REAL | 高液位报警值 % (默认: 90.0) |
| iLevel_L | REAL | 低液位报警值 % (默认: 20.0) |
| iLevel_HH | REAL | 高高液位联锁值 % (默认: 95.0) |
| iLevel_LL | REAL | 低低液位联锁值 % (默认: 10.0) |

#### FB_Level_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qOutput | REAL | 输出值 0-100% |
| qLevel_Status | INT | 液位状态 0=正常,1=高,2=低,3=高高联锁,4=低低联锁 |
| qPump_Start | BOOL | 泵启动命令(输液用) |
| qPump_Stop | BOOL | 泵停止命令 |
| qValve_Open | BOOL | 阀打开命令(输液用) |
| qValve_Close | BOOL | 阀关闭命令 |
| qAlarm_H | BOOL | 高液位报警 |
| qAlarm_L | BOOL | 低液位报警 |
| qAlarm_HH | BOOL | 高高液位联锁 |
| qAlarm_LL | BOOL | 低低液位联锁 |

#### FB_Level_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Kp | REAL | 2.0 |  |
| Tn | TIME | T#60S |  |
| Deadband | REAL | 1.0 |  |
| Output_Min | REAL | 0.0 |  |
| Output_Max | REAL | 100.0 |  |

---

### FB_Temperature_Control

**名称**: 温度控制功能块
**描述**: 温度控制，带升降温速率限制及过热保护
**版本**: v1.0
**类别**: 工艺控制
**父功能块**: FB_PID_Control

#### FB_Temperature_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iTemp_PV | REAL | 温度过程值 ℃ |
| iTemp_SP | REAL | 温度设定值 ℃ |
| iAuto_Mode | BOOL | 自动模式 |
| iManual_Output | REAL | 手动输出值 |
| iHeat_Request | BOOL | 加热请求 |
| iCool_Request | BOOL | 冷却请求 |
| iTemp_H | REAL | 高报警值 ℃ |
| iTemp_L | REAL | 低报警值 ℃ |
| iTemp_HH | REAL | 超温联锁值 ℃ |

#### FB_Temperature_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qOutput | REAL | 输出值 0-100% |
| qHeat_Output | REAL | 加热输出 0-100% |
| qCool_Output | REAL | 冷却输出 0-100% |
| qHeat_Request | BOOL | 加热器使能 |
| qCool_Request | BOOL | 冷却阀使能 |
| qTemp_Status | INT | 温度状态 0=正常,1=高,2=低,3=超温联锁 |
| qAlarm_H | BOOL | 高报警 |
| qAlarm_L | BOOL | 低报警 |
| qAlarm_HH | BOOL | 超温联锁 |

#### FB_Temperature_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Kp | REAL | 1.5 |  |
| Tn | TIME | T#40S |  |
| Tv | TIME | T#5S |  |
| Heat_Rate_Limit | REAL | 5.0 | 升温速率限制 ℃/min |
| Cool_Rate_Limit | REAL | 3.0 | 降温速率限制 ℃/min |
| Deadband | REAL | 0.5 |  |

---

### FB_Pressure_Control

**名称**: 压力控制功能块
**描述**: 压力控制，带超压联锁保护
**版本**: v1.0
**类别**: 工艺控制
**父功能块**: FB_PID_Control

#### FB_Pressure_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iPress_PV | REAL | 压力过程值 MPa |
| iPress_SP | REAL | 压力设定值 MPa |
| iAuto_Mode | BOOL | 自动模式 |
| iManual_Output | REAL | 手动输出值 |
| iPress_H | REAL | 高报警值 MPa |
| iPress_L | REAL | 低报警值 MPa |
| iPress_HH | REAL | 超压联锁值 MPa |

#### FB_Pressure_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qOutput | REAL | 输出值 0-100% |
| qValve_Position | INT | 调节阀开度 0-100% |
| qPress_Status | INT | 压力状态 0=正常,1=高,2=低,3=超压联锁 |
| qAlarm_H | BOOL | 高报警 |
| qAlarm_L | BOOL | 低报警 |
| qAlarm_HH | BOOL | 超压联锁 |
| qRelief_Open | BOOL | 泄压阀打开命令 |

#### FB_Pressure_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Kp | REAL | 2.0 |  |
| Tn | TIME | T#30S |  |
| Deadband | REAL | 0.02 | MPa |
| Relief_Delay | TIME | T#2S | 泄压延时 |

---

### FB_Flow_Control

**名称**: 流量控制功能块
**描述**: 管道流量控制，带高低流量报警
**版本**: v1.0
**类别**: 工艺控制
**父功能块**: FB_PID_Control

#### FB_Flow_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iFlow_PV | REAL | 流量过程值 m³/h |
| iFlow_SP | REAL | 流量设定值 m³/h |
| iAuto_Mode | BOOL | 自动模式 |
| iManual_Output | REAL | 手动输出值 |
| iFlow_H | REAL | 高报警值 m³/h |
| iFlow_L | REAL | 低报警值 m³/h |

#### FB_Flow_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qOutput | REAL | 输出值 0-100% |
| qValve_Position | INT | 调节阀开度 0-100% |
| qFlow_Status | INT | 流量状态 0=正常,1=高,2=低 |
| qAlarm_H | BOOL | 高报警 |
| qAlarm_L | BOOL | 低报警 |

#### FB_Flow_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Kp | REAL | 1.0 |  |
| Tn | TIME | T#20S |  |
| Deadband | REAL | 0.1 |  |

---

### FB_Brix_Control

**名称**: 糖度控制功能块
**描述**: 调配罐糖度控制，通过调节糖浆阀实现目标Brix值控制
**版本**: v1.0
**类别**: 工艺控制
**父功能块**: FB_PID_Control

#### FB_Brix_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iBrix_PV | REAL | 糖度过程值 °Brix |
| iBrix_SP | REAL | 糖度设定值 °Brix |
| iAuto_Manual | BOOL | 自动/手动切换 TRUE=自动 |
| iManual_Output | REAL | 手动输出值 范围: 0.0-100.0 |
| iBrix_H | REAL | 高报警值 °Brix (默认: 15.0) |
| iBrix_L | REAL | 低报警值 °Brix (默认: 10.0) |
| iBrix_HH | REAL | 高高报警值 °Brix (默认: 16.0) |
| iBrix_LL | REAL | 低低报警值 °Brix (默认: 9.0) |
| iSyrup_Flow_PV | REAL | 糖浆流量过程值 L/h |
| iSyrup_Brix | REAL | 糖浆浓度 °Brix (默认: 65.0) |

#### FB_Brix_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qOutput | REAL | 输出值 0-100% |
| qValve_Position | INT | 调节阀开度 0-100% |
| qBrix_Error | REAL | 当前偏差 SP-PV |
| qBrix_Status | INT | 状态 0=正常,1=高,2=低,3=高高联锁,4=低低联锁 |
| qSyrup_Flow_SP | REAL | 糖浆流量设定值 L/h |
| qAlarm_H | BOOL | 高报警 |
| qAlarm_L | BOOL | 低报警 |
| qAlarm_HH | BOOL | 高高报警 |
| qAlarm_LL | BOOL | 低低报警 |

#### FB_Brix_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Kp | REAL | 2.0 | 比例增益 |
| Tn | TIME | T#45S | 积分时间 |
| Deadband | REAL | 0.2 | 死区宽度 °Brix |
| Output_Min | REAL | 0.0 | 输出下限 % |
| Output_Max | REAL | 100.0 | 输出上限 % |
| Syrup_Conc | REAL | 65.0 | 糖浆浓度 °Brix |

#### FB_Brix_Control 逻辑说明

- **1.偏差计算**: 计算设定值与过程值的偏差
- **2.PID计算**: 根据偏差计算输出值
- **3.流量换算**: 根据糖浆浓度计算所需流量
- **4.报警判断**: 判断是否触发各类报警

#### FB_Brix_Control 诊断代码

| 代码 | 描述 |
|------|------|
| BRX001 | 糖度高于高高限 |
| BRX002 | 糖度低于低低限 |
| BRX003 | 糖度偏差超限 |
| BRX004 | 糖浆流量异常 |

---

### FB_PH_Control

**名称**: pH控制功能块
**描述**: 调配罐pH控制，通过调节酸液阀实现目标pH值控制
**版本**: v1.0
**类别**: 工艺控制
**父功能块**: FB_PID_Control

#### FB_PH_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iPH_PV | REAL | pH过程值 |
| iPH_SP | REAL | pH设定值 |
| iAuto_Manual | BOOL | 自动/手动切换 TRUE=自动 |
| iManual_Output | REAL | 手动输出值 范围: 0.0-100.0 |
| iPH_H | REAL | 高报警值 (默认: 6.5) |
| iPH_L | REAL | 低报警值 (默认: 4.5) |
| iPH_HH | REAL | 高高报警值 (默认: 7.0) |
| iPH_LL | REAL | 低低报警值 (默认: 4.0) |
| iAcid_Concentration | REAL | 酸液浓度 % (默认: 50.0) |

#### FB_PH_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qOutput | REAL | 输出值 0-100% |
| qValve_Position | INT | 调节阀开度 0-100% |
| qPH_Error | REAL | 当前偏差 SP-PV |
| qPH_Status | INT | 状态 0=正常,1=高,2=低,3=高高联锁,4=低低联锁 |
| qAcid_Flow_SP | REAL | 酸液流量设定值 L/h |
| qAlarm_H | BOOL | 高报警 |
| qAlarm_L | BOOL | 低报警 |
| qAlarm_HH | BOOL | 高高报警 |
| qAlarm_LL | BOOL | 低低报警 |

#### FB_PH_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Kp | REAL | 3.0 | 比例增益 |
| Tn | TIME | T#30S | 积分时间 |
| Deadband | REAL | 0.1 | 死区宽度 |
| Output_Min | REAL | 0.0 | 输出下限 % |
| Output_Max | REAL | 100.0 | 输出上限 % |

#### FB_PH_Control 逻辑说明

- **1.pH-浓度转换**: pH值与H+浓度非线性转换
- **2.偏差计算**: 计算设定值与过程值的偏差
- **3.PID计算**: 根据偏差计算输出值(考虑非线性)
- **4.滴定曲线补偿**: 根据pH-酸添加量曲线进行补偿
- **5.报警判断**: 判断是否触发各类报警

#### FB_PH_Control 诊断代码

| 代码 | 描述 |
|------|------|
| PH001 | pH高于高高限 |
| PH002 | pH低于低低限 |
| PH003 | pH偏差超限 |
| PH004 | 酸液流量异常 |

---

## 4. 批次控制功能块

### FB_Batch_Control

**名称**: 批次控制功能块
**描述**: 调配批次顺序控制，管理批次生产的各个步骤
**版本**: v1.0
**类别**: 批次控制

#### FB_Batch_Control 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iBatch_Start | BOOL | 批次开始命令 |
| iBatch_Stop | BOOL | 批次停止命令 |
| iBatch_Pause | BOOL | 批次暂停命令 |
| iBatch_Resume | BOOL | 批次恢复命令 |
| iBatch_Abort | BOOL | 批次中止命令 |
| iStep_Complete | BOOL | 步骤完成信号 |
| iStep_Ready | BOOL | 步骤准备就绪 |
| iRecipe_Select | INT | 配方选择 1=绿茶,2=红茶,3=乌龙茶 |
| iAuto_Mode | BOOL | 自动模式 |

#### FB_Batch_Control 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qBatch_Status | INT | 批次状态 0=空闲,1=运行,2=暂停,3=完成,4=停止,5=中止,6=故障 |
| qCurrent_Step | INT | 当前步骤号 |
| qStep_Command | INT | 步骤命令 1=开始配料,2=添加茶汁,3=添加糖浆... |
| qStep_Time_Remaining | TIME | 当前步骤剩余时间 |
| qBatch_Time_Remaining | TIME | 批次剩余总时间 |
| qBatch_Progress | INT | 批次完成进度 0-100% |
| qBatch_Complete | BOOL | 批次完成信号 |
| qBatch_Fault | BOOL | 批次故障信号 |
| qAlarm | BOOL | 批次报警 |

#### FB_Batch_Control 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Step_Timeout | TIME | T#30M | 步骤超时时间 |
| Batch_Timeout | TIME | T#2H | 批次总超时时间 |
| Max_Retries | INT | 3 | 最大重试次数 |
| Auto_Continue | BOOL | FALSE | 步骤完成后自动继续 |

#### FB_Batch_Control 批次步骤

| 步骤 | 名称 | 动作 | 目标 | 时间限制 |
|------|------|------|------|----------|
| 1 | 添加纯水 | ADD_WATER | 液位30% | T#5M |
| 2 | 添加茶浓缩汁 | ADD_TEA | Brix 2.5° | T#10M |
| 3 | 添加糖浆 | ADD_SYRUP | Brix目标值±1.0 | T#5M |
| 4 | 添加酸液 | ADD_ACID | pH目标值±0.5 | T#3M |
| 5 | 添加香精 | ADD_FLAVOR | 时间到 | T#1M |
| 6 | 补水至目标量 | ADD_WATER_FINAL | 液位100% | T#3M |
| 7 | 搅拌混合 | MIXING | 时间到 | T#15M |

#### FB_Batch_Control 逻辑说明

- **1.配方加载**: 根据配方选择加载参数
- **2.步骤执行**: 按顺序执行各步骤
- **3.条件判断**: 判断步骤完成条件是否满足
- **4.超时检测**: 步骤或批次超时检测
- **5.异常处理**: 故障、重试、停止处理

#### FB_Batch_Control 诊断代码

| 代码 | 描述 |
|------|------|
| B001 | 步骤超时 |
| B002 | 批次超时 |
| B003 | 步骤条件不满足 |
| B004 | 批次重试次数超限 |
| B005 | 配方数据无效 |

---

## 5. UHT杀菌专用功能块

### FB_UHT_Temperature_Profile

**名称**: UHT温度曲线控制功能块
**描述**: UHT杀菌机温度分段控制，确保温度曲线符合工艺要求
**版本**: v1.0
**类别**: UHT控制

#### FB_UHT_Temperature_Profile 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iTemp_Preheat | REAL | 预热段温度 PV |
| iTemp_Sterilize | REAL | 杀菌段温度 PV |
| iTemp_Holding | REAL | 保温段温度 PV |
| iTemp_Cooling | REAL | 冷却段温度 PV |
| iFlow_Rate | REAL | 产品流量 |
| iAuto_Mode | BOOL | 自动模式 |
| iStart | BOOL | 启动命令 |
| iStop | BOOL | 停止命令 |

#### FB_UHT_Temperature_Profile 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qPreheat_Ctrl | REAL | 预热段控制输出 |
| qSterilize_Ctrl | REAL | 杀菌段控制输出 |
| qCooling_Ctrl | REAL | 冷却段控制输出 |
| qSteam_Valve | REAL | 蒸汽调节阀开度 |
| qCooling_Valve | REAL | 冷却水阀开度 |
| qProduct_Valve | BOOL | 产品进料阀 |
| qDrain_Valve | BOOL | 排放阀 |
| qStatus | INT | 状态 0=停止,1=预热,2=杀菌,3=运行中,4=冷却,5=故障 |
| qCCP_OK | BOOL | 关键控制点正常 |
| qAlarm | BOOL | 报警 |
| qHold_Status | BOOL | 保温状态保持中 |

#### FB_UHT_Temperature_Profile 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Preheat_Temp | REAL | 80.0 | 预热温度设定 ℃ |
| Sterilize_Temp | REAL | 135.0 | 杀菌温度设定 ℃ |
| Holding_Temp_Min | REAL | 130.0 | 保温温度下限 ℃ |
| Cooling_Temp_Max | REAL | 35.0 | 冷却温度上限 ℃ |
| Sterilize_Time | REAL | 15.0 | 杀菌时间秒 |
| Flow_Rate_Nom | REAL | 3000.0 | 额定流量 L/h |
| Temp_Dev_Alarm | REAL | 2.0 | 温度报警偏差 ℃ |
| Temp_Dev_Interlock | REAL | 5.0 | 温度联锁偏差 ℃ |

#### FB_UHT_Temperature_Profile 逻辑说明

- **1.温度监测**: 实时监测各段温度
- **2.流量计算**: 根据流量计算保持时间
- **3.杀菌判定**: 温度>130℃持续15s以上
- **4.偏差报警**: 温度偏差超限报警
- **5.联锁动作**: 温度低于130℃持续10s关闭进料

#### FB_UHT_Temperature_Profile CCP监控点

| 监控点 | 位置 | 参数 | 限值 | 持续时间 | 动作 |
|--------|------|------|------|----------|------|
| CCP-1 | 杀菌段 | 温度 | ≥130℃ | ≥15s | 温度低于限值10s关闭进料阀 |

---

## 6. 灌装系统专用功能块

### FB_Speed_Sync

**名称**: 高速速度同步功能块
**描述**: 用于吹瓶机、灌装机、旋盖机之间的速度同步控制
**版本**: v2.0
**类别**: 灌装控制

#### FB_Speed_Sync 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iMaster_Speed | REAL | 主令速度 瓶/h |
| iMaster_Actual | REAL | 主令实际速度 |
| iSlave1_Actual | REAL | 从机1实际速度 |
| iSlave2_Actual | REAL | 从机2实际速度 |
| iSync_Enable | BOOL | 同步使能 |
| iMaster_Ready | BOOL | 主令就绪 |
| iEmergency_Stop | BOOL | 急停信号 (默认: FALSE) |

#### FB_Speed_Sync 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qMaster_Speed_SP | REAL | 主令速度设定 |
| qSlave1_Speed_SP | REAL | 从机1速度设定 |
| qSlave2_Speed_SP | REAL | 从机2速度设定 |
| qSync_Status | INT | 同步状态 0=停止,1=同步,2=偏差报警,3=故障 |
| qDeviation | REAL | 速度偏差 ‰ |
| qSync_OK | BOOL | 同步正常 |

#### FB_Speed_Sync 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Sync_Tolerance | REAL | 3.0 | 同步偏差允许值 ‰ |
| Response_Time | TIME | T#10ms | 响应时间 <10ms |
| Master_Speed_Min | REAL | 50000.0 | 最低速度 瓶/h |
| Master_Speed_Max | REAL | 58000.0 | 最高速度 瓶/h |

#### FB_Speed_Sync 逻辑说明

- **1.主令速度计算**: 根据主令编码器计算实际速度
- **2.从机速度采集**: 采集两个从机的实际速度
- **3.偏差计算**: 计算与主令的速度偏差
- **4.同步判定**: 偏差<3‰判定为同步正常
- **5.故障处理**: 偏差超限或急停进入故障状态

#### FB_Speed_Sync 诊断代码

| 代码 | 描述 |
|------|------|
| SS001 | 速度偏差超限 |
| SS002 | 主令速度异常 |
| SS003 | 从机响应超时 |

---

### FB_Capping_Torque

**名称**: 旋盖扭矩控制功能块
**描述**: 用于控制旋盖机的扭矩，确保瓶盖密封性
**版本**: v2.0
**类别**: 灌装控制

#### FB_Capping_Torque 输入参数

| 名称 | 类型 | 描述 |
|------|------|------|
| iTorque_PV | REAL | 扭矩过程值 Nm |
| iTorque_SP | REAL | 扭矩设定值 Nm (默认: 0.5) |
| iSpeed_PV | REAL | 旋盖速度 瓶/h |
| iAuto_Mode | BOOL | 自动模式 |
| iStart | BOOL | 启动命令 |
| iStop | BOOL | 停止命令 |

#### FB_Capping_Torque 输出参数

| 名称 | 类型 | 描述 |
|------|------|------|
| qTorque_Output | REAL | 扭矩输出 0-100% |
| qSpeed_Output | REAL | 速度输出 0-100% |
| qTorque_OK | BOOL | 扭矩合格 |
| qTorque_Status | INT | 状态 0=停止,1=运行,2=扭矩低,3=扭矩高,4=故障 |
| qAlarm_L | BOOL | 扭矩低报警 <0.3Nm |
| qAlarm_H | BOOL | 扭矩高报警 >0.7Nm |
| qReject | BOOL | 剔除信号 |

#### FB_Capping_Torque 参数定义

| 名称 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| Torque_Min | REAL | 0.3 | 扭矩下限 Nm |
| Torque_Max | REAL | 0.7 | 扭矩上限 Nm |
| Kp | REAL | 2.0 | 比例增益 |
| Deadband | REAL | 0.05 | 死区 Nm |

#### FB_Capping_Torque 逻辑说明

- **1.扭矩监测**: 实时监测旋盖扭矩
- **2.范围判定**: 判断扭矩是否在0.3-0.7Nm范围内
- **3.速度调节**: 根据扭矩偏差调节电机速度
- **4.剔除判定**: 扭矩超限产品剔除
- **5.报警输出**: 扭矩异常报警

#### FB_Capping_Torque 诊断代码

| 代码 | 描述 |
|------|------|
| CT001 | 扭矩低于下限 |
| CT002 | 扭矩高于上限 |
| CT003 | 连续5个扭矩异常 |

---

## 7. 版本管理

**当前版本**: v2.0
**生效日期**: 2026-04-29
**编制人**: SCADA系统
**审批人**: 待确认

### 版本历史

| 版本 | 日期 | 作者 | 变更内容 | 状态 |
|------|------|------|----------|------|
| v1.0 | 2026-04-29 | SCADA系统 | 初始版本 | draft |
| v2.0 | 2026-04-29 | SCADA系统 | 新增灌装系统功能块(速度同步、扭矩控制)，支持BF/PF/CG三PLC同步架构 | draft |

---

*本文档由系统自动生成，生成时间: 2026-04-29*