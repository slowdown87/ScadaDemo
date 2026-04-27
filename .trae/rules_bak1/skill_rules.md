# 技能使用细则

> 本文件是 global_rules 的细则补充，统领性内容见 global_rules

## 技能激活

| 条件 | 技能 |
|------|------|
| Bug/Issue | swe-agent-mode |
| 子任务>3/需执行顺序 | planning |
| 安全/认证/敏感数据 | security |
| 代码修改 | code-review |
| 深度分析/新技术 | guided-ai |
| 复杂多视角决策 | multi-agent-sim |
| 架构设计/技术选型 | architecture |
| 出错/不工作 | debug |
| 重构代码 | refactoring |
| 设计测试 | testing |
| 写文档 | documentation |
| 创建新技能 | skill-creator |

## 常用组合

新功能：planning → swe-agent-mode → testing → code-review
Bug修复：debug → swe-agent-mode → testing
重构：code-review → refactoring → testing
架构决策：architecture → guided-ai

## 冲突解决

### 冲突解决规则链
1. **有安全风险** → safety_rules(优先级1-2) 强制拦截
2. **用户明确要求** → 评估是否违反安全/铁律
   - 不违反 → 服从用户，执行前说明预期
   - 违反 → 停止，解释风险，提供替代方案
3. **铁律冲突** → 铁律优先，但需告知用户

### 自主决策范围

AI可自行决定：
- 简单重构（函数提取、变量重命名）
- 单文件修改（<50行）
- 常规调试（添加日志）
- 代码审查（仅提供报告）

必须用户确认：
- 多文件修改、删除操作、不可逆操作

## 动态协作

并行激活：
- 复杂调试：debug + planning
- 架构决策：architecture + guided-ai

切换规则：遇障碍→planning / 发现风险→security / 需要验证→testing

## 激活后操作

### 通用流程
1. 标注激活的技能
2. 按技能模板执行
3. 完成自检清单
4. 输出结果

### 各技能输出格式
| 技能 | 开头标注 | 结尾 |
|-----|---------|------|
| swe-agent-mode | [激活：swe-agent-mode] | 修复摘要 |
| debug | [激活：debug] | 调试报告 |
| code-review | [激活：code-review] | 审查报告 |
| planning | [激活：planning] | 执行计划 |

### 何时算完成
- 有明确交付物
- 自检清单全部通过
- 用户确认或无异议

## 优先级矩阵

当多个规则/技能冲突时，按此优先级处理：

| 优先级 | 场景 | 处理方式 |
|:------:|------|---------|
| 1 | 安全相关 | 安全 > 一切 |
| 2 | 危险命令 | 停止 → 确认 |
| 3 | 用户明确要求 | 用户的意图优先（见冲突解决规则链）|
| 4 | 项目铁律 | project_rules > 其他 |
| 5 | 复杂任务 | planning > 立即执行 |

### 冲突处理示例
- "删除文件夹" → 危险命令(2) > 用户的删除请求(3)
- "快速修复这个Bug" → planning(5) > 立即执行

## 判断标准

### "简单"定义
| 场景 | 简单 | 复杂 |
|-----|:----:|:----:|
| 重构 | 单函数提取/重命名 | 跨文件职责重组 |
| 修改 | <50行/单文件 | >50行/多文件 |
| 调试 | 添加日志/打印变量 | 跨进程/并发问题 |
| 审查 | 单文件/<200行 | 多文件/核心模块 |

### "危险"定义
需要确认的操作：
- 删除文件/文件夹（rm, rmdir, del）
- 修改系统配置/环境变量
- git push --force
- 批量替换（全局文本替换）
- 执行来路不明的脚本/命令

## 与其他规则配合

| 场景 | 配合规则 |
|-----|---------|
| 新功能开发 | +project_rules（无完整设计不编码）|
| Bug修复 | +meta_rules（执行前检查）|
| 安全审查 | +safety_rules（危险命令、敏感信息）|
| 深度分析 | +global_rules（引导性交互、多元方案）|
| 架构决策 | +architecture skill + guided-ai |
