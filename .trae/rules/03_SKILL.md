# 技能与协作

## 技能选择

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

| 场景 | 技能组合 |
|------|----------|
| 新功能 | planning → swe-agent-mode → testing → code-review |
| Bug修复 | debug → swe-agent-mode → testing |
| 重构 | code-review → refactoring → testing |
| 架构决策 | architecture → guided-ai |

## 激活流程

1. 标注激活的技能：`[激活：xxx]`
2. 按技能模板执行
3. 完成自检清单
4. 输出结果

## 冲突解决规则链

1. **有安全风险** → 强制拦截
2. **用户明确要求** → 评估是否违反安全/铁律
   - 不违反 → 服从，执行前说明预期
   - 违反 → 停止，解释风险，提供替代
3. **铁律冲突** → 铁律优先，告知用户

## 自主决策范围

**AI可自行决定：**
- 简单重构（单函数提取/重命名）
- 单文件修改（<50行）
- 常规调试（添加日志）
- 代码审查（仅提供报告）

**必须用户确认：**
- 多文件修改、删除操作、不可逆操作

## 动态协作

| 场景 | 技能组合 |
|------|----------|
| 复杂调试 | debug + planning |
| 架构决策 | architecture + guided-ai |

**切换规则**：遇障碍→planning / 发现风险→security / 需要验证→testing

## 判断标准

| 场景 | 简单 | 复杂 |
|------|------|------|
| 重构 | 单函数提取/重命名 | 跨文件职责重组 |
| 修改 | <50行/单文件 | >50行/多文件 |
| 调试 | 添加日志/打印变量 | 跨进程/并发问题 |
| 审查 | 单文件/<200行 | 多文件/核心模块 |
