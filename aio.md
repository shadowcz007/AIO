# AIO：Agent通用协议

## 一、协议概述

AIO (Agent Input/Output) 是一个通用的Agent协议标准，用于规范化Agent的输入输出行为。本协议旨在提供统一的接口规范，便于Agent之间的互操作和工具链集成。

### 1. 核心规范

#### 1.1 输入/输出规范
- 通过标准输入(stdin)接收JSON格式数据
- 将处理结果输出到标准输出(stdout)
- 错误信息输出到标准错误(stderr)
- 支持管道操作，便于工具链集成

#### 1.2 数据格式规范
- 输入数据必须为JSON格式
- 支持多种输出格式（默认TXT）
- 使用抽象类Output实现格式转换
- 保证输出格式的一致性

#### 1.3 错误处理规范
- 必须处理JSON解析异常
- 成功执行返回退出码0
- 失败执行返回退出码1
- 错误信息统一输出到stderr

## 二、AIO工具集

### 1. aio-cli 项目管理工具

aio-cli是AIO协议的官方实现工具，提供了完整的Agent项目生命周期管理功能。

#### 1.1 核心功能
- 项目脚手架：快速创建符合AIO规范的项目结构
- OpenAI Agents集成：内置OpenAI Agents SDK支持
- 多Agent协作：支持Agent间的交互和任务分发
- 调试与监控：内置跟踪和调试功能

#### 1.2 标准项目结构
```
my-agent/
├── venv/                # Python虚拟环境
├── cursorule/          # Agent规则配置
├── src/
│   ├── main.py        # 主程序入口
│   ├── agents/        # Agent定义
│   └── tools/         # 工具函数
└── dist/              # 打包输出目录
```

### 2. OpenAI Agents集成

#### 2.1 Agent配置
```python
from agents import Agent, Guardrail

# Agent定义
agent = Agent(
    name="数据处理Agent",
    instructions="处理输入的JSON数据",
    tools=[process_json]
)

# 护栏配置
input_guard = Guardrail(
    name="输入检查",
    validation_rules=["不含敏感信息", "数据格式正确"]
)
```

#### 2.2 工具开发
```python
from agents import function_tool

@function_tool
def process_json(data: dict) -> dict:
    # 实现数据处理逻辑
    return processed_data
```

### 3. 开发指南

#### 3.1 命令行支持
- --verbose：启用详细输出模式
- -h 或 --help：显示帮助信息

#### 3.2 扩展开发
```python
# 自定义输出格式
class CustomOutput(Output):
    def write(self, data):
        # 实现自定义输出逻辑
        pass
```

#### 3.3 快速开始
```bash
# 初始化项目
python aio.py init my-agent

# 开发实现

# 打包发布
python aio.py build
```

## 四、实现示例

### 1. 基础AIO Agent实现

```python
from agents import Agent, Runner, function_tool
from typing import Dict, Any

@function_tool
def process_json_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """处理输入的JSON数据"""
    # 数据处理逻辑
    return {
        "processed": True,
        "result": data
    }

# 创建符合AIO规范的Agent
aio_agent = Agent(
    name="AIO数据处理Agent",
    instructions="按照AIO协议处理输入数据",
    tools=[process_json_data]
)

async def handle_input():
    try:
        # 从stdin读取JSON数据
        input_data = json.loads(sys.stdin.read())
        
        # 执行Agent处理
        result = await Runner.run(aio_agent, input=input_data)
        
        # 输出结果到stdout
        print(json.dumps(result.final_output))
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(handle_input()))
```

### 2. 多Agent协作示例

```python
from agents import Agent, Runner

# 数据验证Agent
validator_agent = Agent(
    name="数据验证Agent",
    instructions="验证输入数据的格式和内容",
)

# 数据处理Agent
processor_agent = Agent(
    name="数据处理Agent",
    instructions="处理已验证的数据",
)

# 主控Agent
controller_agent = Agent(
    name="控制Agent",
    instructions="协调数据验证和处理流程",
    handoffs=[validator_agent, processor_agent]
)

async def process_pipeline(input_data: dict):
    try:
        result = await Runner.run(
            controller_agent, 
            input=json.dumps(input_data)
        )
        return result.final_output
    except Exception as e:
        raise RuntimeError(f"处理失败: {str(e)}")
```

### 3. 命令行工具示例

```python
import click
import json
from typing import Optional

@click.command()
@click.option('--verbose', is_flag=True, help='启用详细输出模式')
@click.option('--format', default='txt', help='输出格式(txt/json)')
def main(verbose: bool, format: str):
    """AIO协议示例工具"""
    try:
        # 读取输入
        input_data = json.loads(sys.stdin.read())
        
        if verbose:
            print(f"接收到输入: {input_data}", file=sys.stderr)
            
        # 处理数据
        result = process_data(input_data)
        
        # 格式化输出
        if format == 'json':
            print(json.dumps(result))
        else:
            print(result)
            
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    main()
```

### 4. 使用示例

```bash
# 基本使用
echo '{"data": "test"}' | python aio_tool.py

# 启用详细模式
echo '{"data": "test"}' | python aio_tool.py --verbose

# 指定JSON输出
echo '{"data": "test"}' | python aio_tool.py --format json

# 管道操作
cat data.json | python aio_tool.py | jq .
```


获取配置信息

method：help（通过stdio、http-GET请求）获取

需要返回类型：stdio、mcp、http
```bash
echo '{"jsonrpc": "2.0","method": "help","id":1}' | xxxx
```

如果返回的type是mcp，则按照mcp的调用使用即可。
如果是stdio和http：按照aio标准


method：start
根据不同类型，使用不同的启动服务方式，如果help配置里没有返回start，则不需要初始化启动服务

启动服务
```bash
echo '{"jsonrpc": "2.0","method": "start"}' | xxxx
```

method：input
通用的输入，用于传递输入的数据作为agent的数据

调用方法
```bash
echo '{"jsonrpc": "2.0","method": "input"}' | xxxx
```



