# mini-swe-agent 参考资料

> 来源：[SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)
> Princeton & Stanford 团队开发，SWE-bench 基准测试开源方案

## 核心数据

| 项目 | 值 |
|-----|---|
| **代码量** | ~100 行核心 Agent 类 |
| **性能** | SWE-bench verified >74% |
| **支持模型** | 所有 LLM via litellm |
| **License** | MIT |

## 项目结构

```
mini-swe-agent/
├── src/minisweagent/
│   ├── agents/default.py       # 核心 Agent 类 (~150行)
│   ├── environments/local.py  # 本地执行环境 (~100行)
│   ├── models/litellm_model.py # LLM 接口
│   └── run/hello_world.py     # 使用示例 (~60行)
├── config/                    # YAML 配置
└── pyproject.toml
```

## 核心架构

### 组件

| 组件 | 文件 | 职责 |
|-----|------|------|
| **Agent** | `agents/default.py` | 主循环控制 |
| **Environment** | `environments/local.py` | 执行 bash 命令 |
| **Model** | `models/litellm_model.py` | 调用 LLM |

### 控制流

```python
while True:
    message = model.query(messages)    # 1. 问 LLM
    outputs = env.execute(actions)     # 2. 执行 bash
    messages.append(observation)         # 3. 记录结果
    if check_complete(output):          # 4. 检查是否完成
        break
```

## 关键设计哲学

### 1. 只用 bash

不需要复杂工具，LM 自己会用 shell 完成一切：
- 读文件：`cat`, `grep`, `find`
- 写文件：`echo`, `vim`, `sed`
- 执行：`bash`, `python`
- Git：`git diff`, `git commit`

### 2. 线性历史

```
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Issue 描述"},
    {"role": "assistant", "content": "思考 + actions"},
    {"role": "user", "content": "观察结果"},
    ...
]
```

每步只是 append，可调试、可回放。

### 3. 独立执行

每次 `subprocess.run()` 都是独立进程：
- 不会因 shell 状态导致问题
- 容易在 Docker/Sandbox 中运行
- 容易并行化

## Agent 类核心代码

```python
class DefaultAgent:
    def run(self, task: str) -> dict:
        self.messages = [
            system_message,
            user_message(task)
        ]
        while True:
            self.step()
            if self.messages[-1]["role"] == "exit":
                break
        return self.messages[-1]["extra"]

    def step(self):
        message = self.model.query(self.messages)
        outputs = self.env.execute(message["actions"])
        self.messages.append(observation(outputs))
```

## Environment 类核心代码

```python
class LocalEnvironment:
    def execute(self, action: dict) -> dict:
        result = subprocess.run(
            action["command"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return {
            "output": result.stdout,
            "returncode": result.returncode
        }
```

## Prompt 模板要点

System prompt 包含：
1. **角色定义**：你是软件工程师
2. **可用命令**：bash 命令列表
3. **输出格式**：思考 + actions（JSON 格式）
4. **结束条件**：输出 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`

## 使用方式

### Python API

```python
from minisweagent import DefaultAgent, LocalEnvironment, LitellmModel

agent = DefaultAgent(
    LitellmModel(model_name="gpt-4o"),
    LocalEnvironment()
)
agent.run("Fix the login bug")
```

### CLI

```bash
pip install mini-swe-agent
mini -t "Fix the login bug" -m gpt-4o
```

## 性能对比

| 方案 | SWE-bench Verified |
|-----|-------------------|
| mini-swe-agent + Gemini 3 Pro | 74% |
| SWE-agent + Claude 3.7 | ~65% |
| 之前 SOTA | ~50% |

## 值得借鉴的点

1. **简单比复杂好**：100 行核心代码比 1000 行框架更易理解
2. **bash 是万能工具**：不需要给 LLM 太多特殊工具
3. **线性历史**：易于调试和优化
4. **独立执行**：状态隔离，稳定性高

## 参考链接

- [GitHub](https://github.com/SWE-agent/mini-swe-agent)
- [文档](https://mini-swe-agent.com/latest/)
- [论文](https://arxiv.org/abs/2405.15793)
