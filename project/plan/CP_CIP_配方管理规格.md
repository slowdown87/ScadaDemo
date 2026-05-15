# CIP清洗系统 - 配方管理规格

> 文档版本: v1.0
> 创建日期: 2026-05-13
> 工段: CP (CIP Cleaning In Place)
> 用途: 清洗配方管理、参数自定义

---

## 1. 概述

### 1.1 配方类型

| 配方类型 | 说明 | 示例 |
|----------|------|------|
| **标准配方** | 预置配方，不可修改 | WTCIP-01, EXCIP-01 |
| **自定义配方** | 用户创建的配方，可编辑/删除 | USER-001 |

### 1.2 配方结构

```
配方 (Recipe)
├── 配方基本信息
│   ├── 配方ID
│   ├── 配方名称
│   ├── 适用区域
│   └── 描述
│
└── 步骤序列 (1-10步)
    ├── 步骤1: 预冲洗
    ├── 步骤2: 碱洗
    ├── 步骤3: 中间冲洗
    ├── 步骤4: 酸洗
    └── 步骤5: 最终冲洗
```

---

## 2. 标准配方

### 2.1 预置配方清单

| 配方ID | 配方名称 | 适用区域 | 总时长 |
|--------|----------|----------|--------|
| WTCIP-01 | 水处理标准清洗 | 1区-水处理 | 45分钟 |
| EXCIP-01 | 茶叶萃取清洗 | 2区-茶叶 | 95分钟 |
| BLCIP-01 | 调配系统清洗 | 3区-调配 | 85分钟 |
| UHCIP-01 | UHT杀菌清洗 | 4区-UHT | 100分钟 |
| PFCIP-01 | 灌装系统清洗 | 5区-灌装 | 85分钟 |

### 2.2 WTCIP-01 水处理标准清洗

```yaml
RecipeID: 1
RecipeName: 'WTCIP-01'
Description: '水处理系统标准清洗程序'
ApplicableZone: 1
StepCount: 5

Steps:
  - StepIndex: 1
    MediaID: 1
    MediaName: '纯水冲洗'
    TargetTemp: 85
    TargetTime: 15
    TargetFlow: 3.0
    PassConductivity: 999  # 不判定

  - StepIndex: 2
    MediaID: 2
    MediaName: '碱洗'
    TargetTemp: 85
    TargetTime: 25
    TargetFlow: 5.0
    PassConductivity: 999

  - StepIndex: 3
    MediaID: 1
    MediaName: '中间冲洗'
    TargetTemp: 70
    TargetTime: 10
    TargetFlow: 3.0
    PassConductivity: 999

  - StepIndex: 4
    MediaID: 3
    MediaName: '酸洗'
    TargetTemp: 60
    TargetTime: 20
    TargetFlow: 5.0
    PassConductivity: 999

  - StepIndex: 5
    MediaID: 1
    MediaName: '最终冲洗'
    TargetTemp: null
    TargetTime: 15
    TargetFlow: 3.0
    PassConductivity: 50  # 合格阈值
```

### 2.3 EXCIP-01 茶叶萃取清洗

```yaml
RecipeID: 2
RecipeName: 'EXCIP-01'
Description: '茶叶前处理及萃取系统清洗程序'
ApplicableZone: 2
StepCount: 5

Steps:
  - StepIndex: 1
    MediaID: 1
    MediaName: '纯水预冲洗'
    TargetTemp: 85
    TargetTime: 20
    TargetFlow: 3.0
    PassConductivity: 999

  - StepIndex: 2
    MediaID: 2
    MediaName: '碱洗'
    TargetTemp: 85
    TargetTime: 35
    TargetFlow: 5.0
    PassConductivity: 999

  - StepIndex: 3
    MediaID: 1
    MediaName: '中间冲洗'
    TargetTemp: 70
    TargetTime: 15
    TargetFlow: 3.0
    PassConductivity: 999

  - StepIndex: 4
    MediaID: 3
    MediaName: '酸洗'
    TargetTemp: 60
    TargetTime: 25
    TargetFlow: 5.0
    PassConductivity: 999

  - StepIndex: 5
    MediaID: 1
    MediaName: '最终冲洗'
    TargetTemp: null
    TargetTime: 20
    TargetFlow: 3.0
    PassConductivity: 50
```

---

## 3. 配方数据结构

### 3.1 PLC配方结构

```pascal
TYPE "UDT_RecipeData"
    STRUCT
        RecipeID      : Int;              // 配方ID
        RecipeName    : String[30];       // 配方名称
        Description   : String[50];       // 配方描述
        ApplicableZone: Int;               // 适用区域
        StepCount     : Int;              // 步骤数量

        // 步骤序列 (最多10步)
        Steps : ARRAY[1..10] OF "UDT_StepData";

        // 元数据
        IsStandard    : Bool;            // 是否标准配方
        CreatedBy     : String[20];      // 创建者
        CreatedTime   : LDT;             // 创建时间
        ModifiedBy    : String[20];       // 修改者
        ModifiedTime  : LDT;              // 修改时间
    END_STRUCT
END_TYPE

TYPE "UDT_StepData"
    STRUCT
        StepIndex     : Int;             // 步骤索引
        MediaID       : Int;             // 介质ID
        MediaName     : String[20];      // 介质名称

        TargetTemp    : Real;            // 目标温度 (℃)
        TargetTime    : Int;             // 目标时间 (分钟)
        TargetFlow    : Real;            // 目标流量 (m³/h)

        // 电导率判定 (仅最终冲洗步骤)
        PassConductivity : Real;         // 合格阈值 (999=不判定)

        // 实际结果
        ActualTempAvg : Real;            // 实际平均温度
        ActualTime    : Int;             // 实际时间
    END_STRUCT
END_TYPE
```

### 3.2 数据库表结构

```sql
CREATE TABLE cip_recipes (
    recipe_id SERIAL PRIMARY KEY,
    recipe_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(100),
    applicable_zone INTEGER,

    -- 步骤数量
    step_count INTEGER DEFAULT 5,

    -- 元数据
    is_standard BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(50),
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(50),
    modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_recipe_name (recipe_name)
);


CREATE TABLE cip_recipe_steps (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER REFERENCES cip_recipes(recipe_id) ON DELETE CASCADE,

    step_index INTEGER NOT NULL,
    media_id INTEGER NOT NULL,
    media_name VARCHAR(20),

    target_temp REAL,
    target_time INTEGER,
    target_flow REAL,
    pass_conductivity REAL DEFAULT 999,

    -- 索引
    INDEX idx_recipe_step (recipe_id, step_index)
);
```

---

## 4. 配方管理功能

### 4.1 配方列表

```python
# recipe_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])


class RecipeStep(BaseModel):
    step_index: int
    media_id: int
    media_name: str
    target_temp: Optional[float]
    target_time: int
    target_flow: float
    pass_conductivity: float


class Recipe(BaseModel):
    recipe_id: int
    recipe_name: str
    description: Optional[str]
    applicable_zone: Optional[int]
    step_count: int
    steps: List[RecipeStep]
    is_standard: bool


@router.get("/", response_model=List[Recipe])
async def get_recipes(standard_only: bool = False):
    """获取配方列表"""

    query = db.query(Recipe)
    if standard_only:
        query = query.filter(Recipe.is_standard == True)

    recipes = query.all()
    return recipes


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    """获取配方详情"""

    recipe = db.query(Recipe).filter(
        Recipe.recipe_id == recipe_id
    ).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")

    return recipe


@router.post("/", response_model=Recipe)
async def create_recipe(recipe: Recipe, current_user: str):
    """创建新配方"""

    # 检查名称是否重复
    existing = db.query(Recipe).filter(
        Recipe.recipe_name == recipe.recipe_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="配方名称已存在")

    # 创建配方
    new_recipe = Recipe(
        recipe_name=recipe.recipe_name,
        description=recipe.description,
        applicable_zone=recipe.applicable_zone,
        step_count=recipe.step_count,
        is_standard=False,
        created_by=current_user,
        created_time=datetime.now()
    )

    db.add(new_recipe)
    db.flush()

    # 创建步骤
    for step in recipe.steps:
        new_step = RecipeStep(
            recipe_id=new_recipe.recipe_id,
            step_index=step.step_index,
            media_id=step.media_id,
            media_name=step.media_name,
            target_temp=step.target_temp,
            target_time=step.target_time,
            target_flow=step.target_flow,
            pass_conductivity=step.pass_conductivity
        )
        db.add(new_step)

    db.commit()
    db.refresh(new_recipe)

    return new_recipe


@router.put("/{recipe_id}", response_model=Recipe)
async def update_recipe(recipe_id: int, recipe: Recipe, current_user: str):
    """更新配方"""

    # 检查配方是否存在
    existing = db.query(Recipe).filter(
        Recipe.recipe_id == recipe_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="配方不存在")

    # 检查是否为标准配方
    if existing.is_standard:
        raise HTTPException(status_code=403, detail="标准配方不可修改")

    # 更新配方信息
    existing.recipe_name = recipe.recipe_name
    existing.description = recipe.description
    existing.applicable_zone = recipe.applicable_zone
    existing.step_count = recipe.step_count
    existing.modified_by = current_user
    existing.modified_time = datetime.now()

    # 删除旧步骤
    db.query(RecipeStep).filter(
        RecipeStep.recipe_id == recipe_id
    ).delete()

    # 创建新步骤
    for step in recipe.steps:
        new_step = RecipeStep(
            recipe_id=recipe_id,
            step_index=step.step_index,
            media_id=step.media_id,
            media_name=step.media_name,
            target_temp=step.target_temp,
            target_time=step.target_time,
            target_flow=step.target_flow,
            pass_conductivity=step.pass_conductivity
        )
        db.add(new_step)

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: int):
    """删除配方"""

    recipe = db.query(Recipe).filter(
        Recipe.recipe_id == recipe_id
    ).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")

    if recipe.is_standard:
        raise HTTPException(status_code=403, detail="标准配方不可删除")

    db.delete(recipe)
    db.commit()

    return {"message": "配方已删除"}


@router.post("/{recipe_id}/copy")
async def copy_recipe(recipe_id: int, new_name: str, current_user: str):
    """复制配方"""

    source = db.query(Recipe).filter(
        Recipe.recipe_id == recipe_id
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="源配方不存在")

    # 创建副本
    new_recipe = Recipe(
        recipe_name=new_name,
        description=source.description,
        applicable_zone=source.applicable_zone,
        step_count=source.step_count,
        is_standard=False,
        created_by=current_user,
        created_time=datetime.now()
    )

    db.add(new_recipe)
    db.flush()

    # 复制步骤
    steps = db.query(RecipeStep).filter(
        RecipeStep.recipe_id == recipe_id
    ).all()

    for step in steps:
        new_step = RecipeStep(
            recipe_id=new_recipe.recipe_id,
            step_index=step.step_index,
            media_id=step.media_id,
            media_name=step.media_name,
            target_temp=step.target_temp,
            target_time=step.target_time,
            target_flow=step.target_flow,
            pass_conductivity=step.pass_conductivity
        )
        db.add(new_step)

    db.commit()
    db.refresh(new_recipe)

    return new_recipe
```

---

## 5. 配方验证

### 5.1 参数校验规则

```python
def validate_recipe(recipe: Recipe) -> List[str]:
    """验证配方参数"""

    errors = []

    # 步骤数量检查
    if recipe.step_count < 1 or recipe.step_count > 10:
        errors.append("步骤数量应在1-10之间")

    # 步骤索引连续性检查
    step_indices = [s.step_index for s in recipe.steps]
    if sorted(step_indices) != list(range(1, recipe.step_count + 1)):
        errors.append("步骤索引应连续")

    # 温度范围检查
    for step in recipe.steps:
        if step.target_temp is not None:
            if step.target_temp < 0 or step.target_temp > 100:
                errors.append(f"步骤{step.step_index}: 温度应在0-100℃之间")

    # 时间范围检查
    for step in recipe.steps:
        if step.target_time < 1 or step.target_time > 120:
            errors.append(f"步骤{step.step_index}: 时间应在1-120分钟之间")

    # 流量范围检查
    for step in recipe.steps:
        if step.target_flow < 0.1 or step.target_flow > 10:
            errors.append(f"步骤{step.step_index}: 流量应在0.1-10m³/h之间")

    # 电导率阈值检查
    for step in recipe.steps:
        if step.pass_conductivity != 999:  # 非不判定
            if step.pass_conductivity < 1 or step.pass_conductivity > 1000:
                errors.append(f"步骤{step.step_index}: 电导率阈值应在1-1000μS/cm之间")

    # 最终冲洗必须判定电导率
    last_step = recipe.steps[-1]
    if last_step.pass_conductivity == 999:
        errors.append("最终冲洗步骤必须设置电导率合格判定")

    return errors
```

---

## 6. HMI显示

### 6.1 配方列表

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  配方管理                                                    [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  配方类型:  ●全部  ○标准配方  ○自定义配方                                     │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 配方名称           │ 适用区域    │ 步骤数 │ 总时长   │ 类型    │ 操作     │   │
│  ├───────────────────┼────────────┼────────┼──────────┼─────────┼─────────┤   │
│  │ WTCIP-01         │ 1区-水处理  │   5    │ 45min   │ 标准    │ [查看]  │   │
│  │ EXCIP-01         │ 2区-茶叶    │   5    │ 95min   │ 标准    │ [查看]  │   │
│  │ BLCIP-01         │ 3区-调配    │   5    │ 85min   │ 标准    │ [查看]  │   │
│  │ UHCIP-01         │ 4区-UHT    │   5    │ 100min  │ 标准    │ [查看]  │   │
│  │ PFCIP-01         │ 5区-灌装    │   5    │ 85min   │ 标准    │ [查看]  │   │
│  ├───────────────────┼────────────┼────────┼──────────┼─────────┼─────────┤   │
│  │ USER-茶叶高温工艺  │ 2区-茶叶    │   6    │ 110min  │ 自定义   │[编辑][删除]│   │
│  │ USER-快速清洗     │ 通用        │   3    │ 30min   │ 自定义   │[编辑][删除]│   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [新建配方]  [导入]  [导出]                                                    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 配方详情

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  配方详情 - EXCIP-01                                            [子画面]     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 配方信息                                                              │   │
│  │ ──────────────────────────────────────────────────────────────────── │   │
│  │ 配方名称: EXCIP-01                                                 │   │
│  │ 配方描述: 茶叶前处理及萃取系统清洗程序                                  │   │
│  │ 适用区域: 2区-茶叶                                                  │   │
│  │ 步骤数量: 5                                                         │   │
│  │ 标准时长: 95分钟                                                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 步骤定义                                                              │   │
│  │ ┌────┬────────┬────────┬────────┬───────┬───────┬────────┐         │   │
│  │ │步骤 │ 介质   │ 目标温度 │ 目标时间│ 目标流量│ 电导判定│ 操作     │   │
│  │ ├────┼────────┼────────┼────────┼───────┼───────┼────────┤         │   │
│  │ │  1 │ 纯水冲洗│  85℃  │  20min │ 3m³/h │  --   │ [编辑]  │   │
│  │ │  2 │ 碱洗    │  85℃  │  35min │ 5m³/h │  --   │ [编辑]  │   │
│  │ │  3 │ 中间冲洗│  70℃  │  15min │ 3m³/h │  --   │ [编辑]  │   │
│  │ │  4 │ 酸洗    │  60℃  │  25min │ 5m³/h │  --   │ [编辑]  │   │
│  │ │  5 │ 最终冲洗│  --    │  20min │ 3m³/h │ ≤50μS │ [编辑]  │   │
│  │ └────┴────────┴────────┴────────┴───────┴───────┴────────┘         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 配方预览 (温度曲线)                                                    │   │
│  │ 90 ┤                                                                │   │
│  │    │                    ╭── 85℃                                     │   │
│  │ 85 ┤────────────────╯                                                │   │
│  │    │                ╭── 70℃                                         │   │
│  │ 70 ┤────────────╯                                                    │   │
│  │    │            ╭── 60℃                                             │   │
│  │ 60 ┤────────╯                                                        │   │
│  │    └───────────────────────────────────────                         │   │
│  │       20   35   15   25   20 (min)                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [返回列表]                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 新建/编辑配方

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  编辑配方                                                    [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 配方信息                                                              │   │
│  │ 配方名称: [EXCIP-01___________] (标准配方不可修改)                      │   │
│  │ 配方描述: [茶叶前处理及萃取系统清洗程序________________________]       │   │
│  │ 适用区域: [2区-茶叶▼]                                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 步骤编辑                                                              │   │
│  │ ┌────┬────────┬────────┬────────┬───────┬─────────────────┐           │   │
│  │ │步骤 │ 介质[▼]│ 温度(℃)│ 时间(min)│流量(m³/h)│ 电导判定(μS/cm) │   │   │
│  │ ├────┼────────┼────────┼────────┼───────┼─────────────────┤           │   │
│  │ │  1 │ 纯水冲洗│ [85]  │  [20]  │ [3.0] │ [不判定▼]       │   │   │
│  │ │  2 │ 碱洗    │ [85]  │  [35]  │ [5.0] │ [不判定▼]       │   │   │
│  │ │  3 │ 中间冲洗│ [70]  │  [15]  │ [3.0] │ [不判定▼]       │   │   │
│  │ │  4 │ 酸洗    │ [60]  │  [25]  │ [5.0] │ [不判定▼]       │   │   │
│  │ │  5 │ 最终冲洗│ [--]  │  [20]  │ [3.0] │ [50]           │   │   │
│  │ └────┴────────┴────────┴────────┴───────┴─────────────────┘           │   │
│  │ [+ 添加步骤]  [- 删除步骤]                                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 配方预览                                                              │   │
│  │ 总时长: 95分钟  (25+35+15+15+20)                                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│           [取消]                                      [保存]  [另存为]           │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 介质选择下拉框

```
┌─────────────────┐
│ 纯水冲洗         │ ← 当前选择
├─────────────────┤
│ 纯水冲洗         │
│ 碱洗 (2% NaOH)  │
│ 酸洗 (1% HNO₃)  │
│ 热水冲洗         │
│ 消毒液冲洗       │
│ 不判定           │
└─────────────────┘
```

---

## 7. 权限管理

| 操作 | 操作员 | 技术员 | 工程师 | 管理员 |
|------|--------|--------|--------|--------|
| 查看配方 | ✅ | ✅ | ✅ | ✅ |
| 使用配方 | ✅ | ✅ | ✅ | ✅ |
| 创建自定义配方 | ❌ | ✅ | ✅ | ✅ |
| 编辑自定义配方 | ❌ | ✅ | ✅ | ✅ |
| 删除自定义配方 | ❌ | ✅ | ✅ | ✅ |
| 编辑标准配方 | ❌ | ❌ | ❌ | ✅ |
| 删除标准配方 | ❌ | ❌ | ❌ | ❌ |

---

## 8. 配方导入导出

### 8.1 导出格式 (JSON)

```json
{
  "export_time": "2026-05-13T14:00:00",
  "export_by": "admin",
  "recipes": [
    {
      "recipe_id": 1,
      "recipe_name": "WTCIP-01",
      "description": "水处理系统标准清洗程序",
      "applicable_zone": 1,
      "step_count": 5,
      "is_standard": true,
      "steps": [
        {
          "step_index": 1,
          "media_id": 1,
          "media_name": "纯水冲洗",
          "target_temp": 85,
          "target_time": 15,
          "target_flow": 3.0,
          "pass_conductivity": 999
        }
      ]
    }
  ]
}
```

### 8.2 导入校验

```python
@router.post("/import")
async def import_recipes(file: UploadFile, current_user: str):
    """导入配方"""

    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="仅支持JSON格式")

    content = await file.read()
    data = json.loads(content)

    imported_count = 0
    errors = []

    for recipe_data in data.get('recipes', []):
        # 验证配方数据
        recipe = Recipe(**recipe_data)
        validation_errors = validate_recipe(recipe)

        if validation_errors:
            errors.append({
                'recipe_name': recipe_data.get('recipe_name'),
                'errors': validation_errors
            })
            continue

        # 检查是否与现有配方冲突
        existing = db.query(Recipe).filter(
            Recipe.recipe_name == recipe.recipe_name
        ).first()

        if existing:
            errors.append({
                'recipe_name': recipe.recipe_name,
                'errors': ['配方名称已存在']
            })
            continue

        # 创建配方
        # ... (同创建配方)

        imported_count += 1

    return {
        'imported': imported_count,
        'errors': errors
    }
```

---

**文档状态**: ✅ 已完成
**版本**: v1.0
**依赖**: 子任务10 (Profinet通讯) ✅
