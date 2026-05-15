---
name: "advanced-planning"
description: "先进规划技能。整合ReAct、Plan-Execute、Reflexion等前沿Agent Planning技术。适用于复杂长任务、多阶段项目、自我纠错等场景。当用户需要深度规划、复杂任务分解或迭代优化时激活。"
---

# Advanced Planning Skill (先进规划技能)

> 本文档整合了2025-2026年最新的Agent Planning技术，包括ReAct、Plan-Execute、Reflexion、Task Decomposition等前沿范式。

## 1. 核心理念：Plan-Execute-Reflect循环

最先进的planning系统采用**三层架构**：

```
┌─────────────────────────────────────────────────────────────┐
│                    PLANNING LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Meta-Plan  │→ │ Decompose   │→ │ Route/Select        │  │
│  │  Generation │  │ & Structure │  │ Strategy             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                    EXECUTION LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Action    │→ │   Tool      │→ │   State             │  │
│  │   Select    │  │   Execute   │  │   Update            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                   REFLECTION LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Evaluate   │→ │  Critique   │→ │  Revise &          │  │
│  │  Result     │  │  Reasoning  │  │  Backtrack          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 2. 核心范式详解

### 2.1 ReAct (Reasoning + Acting)

**原理**：交替进行推理和行动，让模型"边想边做"。

```python
class ReActAgent:
    """
    ReAct = Reason + Act
    核心循环: Thought → Action → Observation → Thought...
    """
    def __init__(self, llm, tools, max_iterations=10):
        self.llm = llm
        self.tools = tools
        self.max_iterations = max_iterations

    def run(self, task: str) -> str:
        history = []
        context = ""

        for i in range(self.max_iterations):
            # Step 1: Reason (生成思维链)
            thought = self.reason(task, context, history)

            # Step 2: Decide action
            action = self.decide_action(thought, self.tools)

            # Step 3: Execute
            if action is None:
                # 无需更多行动，直接回答
                return thought
            result = self.execute_action(action)

            # Step 4: Update context
            context += f"\nAction: {action}\nResult: {result}"
            history.append({"thought": thought, "action": action, "result": result})

        return context

    def reason(self, task, context, history) -> str:
        prompt = f"""Task: {task}
Context: {context}
History: {history}

根据任务和上下文，进行推理分析。
区分已完成和未完成的部分。
"""
        return self.llm.generate(prompt)

    def decide_action(self, thought: str, tools) -> Optional[dict]:
        # 解析thought，决定是否需要调用工具
        pass

    def execute_action(self, action: dict):
        tool_name = action["tool"]
        tool_args = action["args"]
        return self.tools[tool_name](**tool_args)
```

### 2.2 Plan-Execute (计划-执行分离)

**原理**：先制定完整计划，再逐步执行，适合复杂长任务。

```python
class PlanExecuteAgent:
    """
    Plan-Execute Pattern
    关键思想：计划制定和执行分离
    - Planner: 负责任务分解和计划生成
    - Executor: 负责逐个执行子任务
    - Supervisor: 监控执行，决策是否需要replan
    """
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.planner = Planner(llm)
        self.executor = Executor(llm, tools)
        self.supervisor = Supervisor(llm)

    def run(self, task: str) -> str:
        # Phase 1: Planning - 生成任务分解
        plan = self.planner.create_plan(task)
        print(f"📋 原始计划: {plan}")

        # Phase 2: Execute - 逐个执行，支持动态调整
        results = []
        current_plan = plan

        for step_idx, step in enumerate(current_plan):
            print(f"\n🔄 执行步骤 {step_idx + 1}: {step['description']}")

            # 执行当前步骤
            result = self.executor.execute(step)
            results.append(result)

            # Supervisor检查：是否需要replan？
            should_replan, updated_plan = self.supervisor.evaluate(
                original_task=task,
                completed_steps=results,
                remaining_plan=current_plan[step_idx + 1:]
            )

            if should_replan:
                print("⚠️ 检测到问题，重新规划...")
                current_plan = updated_plan
            else:
                current_plan = current_plan[step_idx + 1:]

        return self.format_results(results)

class Planner:
    """任务分解器 - 使用CoT思维链"""
    def create_plan(self, task: str) -> List[dict]:
        prompt = f"""将以下任务分解为可执行的步骤：

Task: {task}

要求：
1. 每个步骤必须清晰、可执行
2. 步骤之间有明确的依赖关系
3. 考虑可能的失败点和回退策略

输出格式（JSON）：
{{
  "steps": [
    {{"id": 1, "description": "...", "dependencies": [], "rollback": "..."}},
    ...
  ]
}}
"""
        return self.llm.generate_json(prompt)

class Supervisor:
    """监督器 - 决策是否需要replan"""
    def evaluate(self, original_task, completed_steps, remaining_plan) -> Tuple[bool, List]:
        prompt = f"""评估当前执行状态：

原始任务: {original_task}
已完成步骤: {completed_steps}
剩余计划: {remaining_plan}

判断：
1. 已完成步骤是否推进了任务？
2. 剩余计划是否仍然合理？
3. 是否需要重新规划？

输出：{{"should_replan": bool, "updated_plan": [...]}}
"""
        result = self.llm.generate_json(prompt)
        return result["should_replan"], result.get("updated_plan", remaining_plan)
```

### 2.3 Reflexion (自我反思)

**原理**：执行后进行自我反思，从失败中学习调整。

```python
class ReflexionAgent:
    """
    Reflexion = Execute → Reflect → Revise
    核心：从失败中学习，改进行动策略
    """
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.short_term_memory = []
        self.long_term_memory = []  # 经验库

    def run(self, task: str) -> str:
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            # 执行
            result, success = self.execute_once(task)

            if success:
                # 成功：存入经验库
                self.learn_from_experience(task, result, success=True)
                return result

            # 失败：反思
            reflection = self.reflect(task, result, self.short_term_memory)
            self.short_term_memory.append(reflection)

            # 根据反思调整策略
            task = self.revise_task(task, reflection)
            attempts += 1

        return "多次尝试后仍失败，请人工介入"

    def execute_once(self, task: str) -> Tuple[str, bool]:
        """执行一次尝试"""
        # 类似ReAct的执行逻辑
        pass

    def reflect(self, task: str, result: str, memory: list) -> dict:
        prompt = f"""反思以下执行结果：

任务: {task}
结果: {result}
历史记忆: {memory}

分析：
1. 哪里出了问题？
2. 根本原因是什么？
3. 下次如何改进？

输出格式：
{{
  "what_went_wrong": "...",
  "root_cause": "...",
  "improvement": "..."
}}
"""
        return self.llm.generate_json(prompt)

    def learn_from_experience(self, task: str, result: str, success: bool):
        """将经验存入长期记忆"""
        self.long_term_memory.append({
            "task_pattern": self.extract_pattern(task),
            "result": result,
            "success": success
        })

    def revise_task(self, task: str, reflection: dict) -> str:
        """根据反思修订任务描述"""
        return f"{task}\n\n[Previous attempt failed: {reflection['root_cause']}]"
```

## 3. 任务分解策略 (Task Decomposition)

### 3.1 层级分解 (Hierarchical Decomposition)

```
Goal
  ↓
┌─────────────────────────────────────────┐
│ Level 1: Epic Tasks (2-5个)             │
│   ├─ Epic A                             │
│   └─ Epic B                             │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ Level 2: Features (每个Epic 3-7个)       │
│   ├─ Feature A1, A2                     │
│   └─ Feature B1, B2                     │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ Level 3: Sub-tasks (每个Feature 5-15个)  │
│   ├─ Subtask A1.1, A1.2                 │
│   └─ Subtask B1.1, B1.2                 │
└─────────────────────────────────────────┘
```

### 3.2 并行分解 (DAG-based Parallelization)

```python
class DAGPlanner:
    """
    有向无环图任务规划
    核心：识别可并行执行的任务
    """
    def __init__(self, llm):
        self.llm = llm
        self.graph = {}

    def decompose(self, task: str) -> dict:
        prompt = f"""将任务分解为DAG结构：

Task: {task}

分析：
1. 列出所有子任务
2. 标注每个子任务的依赖关系
3. 识别哪些可以并行执行

输出：
{{
  "nodes": [
    {{"id": "A", "task": "...", "deps": []}},
    {{"id": "B", "task": "...", "deps": ["A"]}},
    ...
  ],
  "parallel_groups": [["A", "B"], ["C"], ["D", "E"]]
}}
"""
        return self.llm.generate_json(prompt)

    def execute_dag(self, dag: dict) -> List[str]:
        results = {}
        executed = set()

        # 按层级执行，每层内可并行
        for level_nodes in dag["nodes_by_level"]:
            # 并行执行同一层级的任务
            level_results = parallel_execute(
                [self.execute_node(n) for n in level_nodes],
                max_workers=4
            )

            for node_id, result in zip(level_nodes, level_results):
                results[node_id] = result
                executed.add(node_id)

        return results

    def execute_node(self, node: dict) -> str:
        deps_met = all(
            self.check_dependency(dep, results)
            for dep in node.get("deps", [])
        )
        if not deps_met:
            return "BLOCKED"
        # 执行逻辑...
```

## 4. 状态管理 (State Management)

```python
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import json

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class Task:
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    dependencies: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

@dataclass
class ExecutionState:
    """全局执行状态"""
    task: str
    plan: List[Task]
    current_step: int = 0
    context: dict = field(default_factory=dict)
    history: list = field(default_factory=list)
    blockers: list = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "task": self.task,
            "plan": [
                {"id": t.id, "description": t.description, "status": t.status.value}
                for t in self.plan
            ],
            "current_step": self.current_step,
            "context": self.context,
            "history": self.history,
            "blockers": self.blockers
        }, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "ExecutionState":
        data = json.loads(json_str)
        return cls(**data)
```

## 5. 记忆系统 (Memory System)

```python
class MemorySystem:
    """
    三层记忆架构：
    - Working Memory: 当前任务上下文
    - Episodic Memory: 历史执行记录
    - Semantic Memory: 结构化知识
    """
    def __init__(self):
        self.working = {}      # 当前上下文
        self.episodic = []      # 经验历史
        self.semantic = {}      # 知识库

    def store_episode(self, episode: dict):
        """存储执行片段"""
        self.episodic.append({
            "timestamp": self.now(),
            "task": episode["task"],
            "steps": episode["steps"],
            "success": episode["success"],
            "lessons": episode.get("lessons", [])
        })

    def retrieve_relevant(self, query: str, top_k: int = 5) -> list:
        """检索相关记忆"""
        # 基于相似度检索
        scores = [
            (i, self.similarity(query, ep["task"]))
            for i, ep in enumerate(self.episodic)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [self.episodic[i] for i, _ in scores[:top_k]]

    def consolidate(self):
        """记忆整合：将短期经验转化为长期知识"""
        recent = self.episodic[-10:]

        patterns = self.extract_patterns(recent)
        for pattern in patterns:
            if pattern["confidence"] > 0.8:
                self.semantic[pattern["key"]] = pattern["knowledge"]

    def extract_patterns(self, episodes: list) -> list:
        """从经验中提取模式"""
        prompt = f"""从以下执行记录中提取可复用的模式：

{episodes}

输出格式：
{{
  "patterns": [
    {{"key": "pattern_name", "knowledge": "...", "confidence": 0.9}},
    ...
  ]
}}
"""
        return self.llm.generate_json(prompt)["patterns"]
```

## 6. 多Agent协作 (Multi-Agent Planning)

```python
class MultiAgentPlanner:
    """
    多Agent协作规划模式：
    - Orchestrator: 负责任务分配和协调
    - Planner Agent: 负责制定计划
    - Executor Agents: 负责执行具体任务
    - Critic Agent: 负责评估和反馈
    """
    def __init__(self, llm_factory):
        self.orchestrator = Orchestrator(llm_factory.create("coordinator"))
        self.planner = PlannerAgent(llm_factory.create("planner"))
        self.executors = [
            ExecutorAgent(llm_factory.create(f"executor_{i}"))
            for i in range(3)
        ]
        self.critic = CriticAgent(llm_factory.create("critic"))

    def plan_and_execute(self, task: str) -> str:
        # Step 1: Orchestrator分解任务给各Agent
        subtasks = self.orchestrator.decompose(task)

        # Step 2: Planner制定执行计划
        plan = self.planner.create_plan(subtasks)

        # Step 3: 并行执行 + Critic监控
        for phase in plan["phases"]:
            phase_results = self.execute_phase_parallel(phase)

            # Critic评估
            evaluation = self.critic.evaluate(phase, phase_results)

            if not evaluation["pass"]:
                # 不通过则replan
                plan = self.planner.replan(plan, phase, evaluation)

        return self.compile_results(plan)

    def execute_phase_parallel(self, phase: dict) -> List[str]:
        """并行执行同一阶段的任务"""
        tasks = phase["tasks"]
        with ThreadPoolExecutor(max_workers=len(self.executors)) as executor:
            futures = [
                executor.submit(executor.execute, task)
                for executor, task in zip(self.executors, tasks)
            ]
            return [f.result() for f in futures]
```

## 7. 最佳实践检查清单

### 执行前检查
```
[ ] 任务目标清晰明确
[ ] 边界条件和约束已识别
[ ] 成功标准已定义
[ ] 资源需求已评估
[ ] 潜在风险已识别
```

### 规划完整性检查
```
[ ] 子任务有明确的输入/输出
[ ] 依赖关系已标注
[ ] 失败回退策略已制定
[ ] 验证方式已定义
[ ] 执行顺序合理
```

### 执行中监控
```
[ ] 每步执行有日志记录
[ ] 异常情况被及时捕获
[ ] 执行结果被验证
[ ] 上下文保持一致
[ ] 必要时触发replan
```

### 反思与改进
```
[ ] 成功经验被记录
[ ] 失败教训被分析
[ ] 模式被提取和复用
[ ] 记忆被定期整合
```

## 8. 技术选型建议

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| 简单问答 | ReAct | 快速响应，轻量 |
| 复杂多步骤任务 | Plan-Execute | 计划可控，易于调试 |
| 需要从失败中学习 | Reflexion | 自我改进能力 |
| 大规模任务分解 | DAG + 并行 | 效率最大化 |
| 多方协作需求 | Multi-Agent | 专业化分工 |

## 9. 参考资料

- [TodoEvolve: Learning to Architect Agent Planning Systems](https://www.arxiv.org/pdf/2602.07839) (2026)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://react-lm.github.io/)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [LangGraph Complete Guide](https://artificial-intelligence-wiki.com/agentic-ai/agent-architectures-and-components/langgraph-complete-guide/) (2025)
- [AutoGen Multi-Agent Framework](https://microsoft.github.io/autogen/) (v0.4, 2025)
- [SkillX: Automatically Constructing Skill Knowledge Bases](https://arxiv.org/pdf/2604.04804v2) (2026)
- [ReCAP: Recursive Context-Aware Planning](https://openreview.net/forum?id=r2ykUnzuGt)
