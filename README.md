# AIO Agent 项目

## 项目说明
这是一个基于 AIO (Agent Input/Output) 协议的 Agent 项目。本项目遵循 AIO 协议标准，实现了标准化的 Agent 输入输出行为。

## 环境设置

### 1. OpenAI API 配置
在运行程序前，请先配置 OpenAI API：

Linux/Mac:
```bash
export OPENAI_API_KEY=sk-...
```

Windows:
```cmd
set OPENAI_API_KEY=sk-...
```

也可以在运行时通过命令行参数设置：
```bash
python main.py --api-key YOUR_API_KEY
```

### 2. 自定义 API 基础 URL（可选）
如果需要使用自定义的 API 端点：
```bash
python main.py --base-url YOUR_BASE_URL
```

## 使用说明

### 基本用法
```bash
# 从标准输入读取 JSON
echo '{"prompt": "你好"}' | python main.py

# 启用详细输出模式
echo '{"prompt": "你好"}' | python main.py --verbose

# 从文件读取输入
python main.py input.json
```

### 输入输出格式
- 输入：JSON 格式，包含 "prompt" 字段
- 输出：JSON 格式，包含 "status" 和 "output" 字段

### 示例输出
```json
{
    "status": "success",
    "output": "回复内容"
}
```

## 错误处理
- JSON 解析错误会输出到 stderr
- 程序执行成功返回退出码 0
- 程序执行失败返回退出码 1

## 更多信息
详细的 AIO 协议规范和开发指南，请参考项目文档。
