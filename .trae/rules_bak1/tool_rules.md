# 工具使用细则

> 本文件是 global_rules 的细则补充，统领性内容见 global_rules

## 工具分类

| 类型 | Linux命令 | Windows命令 |
|-----|----------|-------------|
| **文件** | cat, grep, find, sed, mkdir | Get-Content, Select-String, Get-ChildItem, mkdir |
| **执行** | python, node, pytest, npm | python, node, npm, npx |
| **Git** | git status/log/diff/add/commit/push | git (同Linux) |
| **搜索** | grep, find | Select-String, Get-ChildItem -Recurse |

> **注意**：Windows PowerShell/命令提示符 与 Linux 命令不完全兼容，优先使用 Trae IDE 内置工具（Read/Write/SearchReplace/Grep/Glob）执行操作。

## 工具选择

| 场景 | 推荐工具 |
|-----|---------|
| 读取文件 | Read |
| 执行命令 | RunCommand |
| 搜索代码 | Grep / SearchCodebase |
| 批量查找 | Glob + Grep |
| 修改文件 | SearchReplace |
| 创建文件 | Write |
| 跟踪任务 | TodoWrite |

### 并行原则
- 独立工具可并行（最多3个）
- 有依赖的工具必须串行

## 使用原则
- **修改前**：先读取了解当前内容
- **执行后**：检查输出结果，分析错误
- **push前**：先检查变更内容，force push 需警告

## 常见陷阱
- 忽略 stderr（错误输出很重要）
- 不检查返回值（假设总是成功）
- 硬编码路径（跨平台兼容性问题）

## 工具组合

常用组合：
- 搜索+分析：Grep + Read
- 批量修改：SearchReplace（多次）
- 验证：RunCommand + Read

效率原则：
- 独立任务可并行
- 批量操作先验证单次
- 复杂脚本先测试再全量

## 输出要求
简要说明执行了什么 → 展示关键输出 → 解释结果含义
