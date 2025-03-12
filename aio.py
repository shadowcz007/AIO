import os
import sys
import subprocess
import platform
import json
import click

# 默认配置文件内容
DEFAULT_CONFIG = {
    "packages": ["pyinstaller", "openai", "requests","openai-agents"],
    "build_name": "myapp",
    "main_script": "main.py"
}

def load_config(config_path=None):
    """加载配置文件，如果未指定则使用默认配置"""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG

def get_venv_paths():
    """根据操作系统返回虚拟环境的 Python 和 pip 路径"""
    if platform.system() == 'Windows':
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
        pip_path = os.path.join('venv', 'Scripts', 'pip.exe')
    else:
        python_path = os.path.join('venv', 'bin', 'python')
        pip_path = os.path.join('venv', 'bin', 'pip')
    return python_path, pip_path

def create_project_template():
    """创建项目模板，包括 .cursorrules 文件和 hello world 示例"""
    if not os.path.exists('src'):
        os.makedirs('src')
    content='''# 输入输出规则
- 通过标准输入(stdin)接收JSON数据
- 处理结果输出到标准输出(stdout)
- 支持管道操作与其他工具集成

# 命令行规则
- 支持--verbose参数启用详细输出模式
- 支持-h或--help显示帮助信息
- 错误信息输出到stderr

# 数据处理规则
- 使用JSON格式作为输入数据格式
- 捕获并处理JSON解析错误
- 支持多种输出格式转换
- 使用抽象类Output实现格式转换

# 错误处理规则
- 捕获所有可能的异常情况
- 错误信息统一输出到stderr
- 成功执行返回退出码0
- 失败执行返回退出码1

# 扩展性规则
- 支持通过Output子类扩展输出格式
- 保持工具模块化设计
- 确保与其他命令行工具兼容'''
    # 创建 cursorule 文件
    with open('.cursorrules', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 创建 hello world 示例
    hello_world_content = '''import json
import sys
import os
import argparse
from abc import ABC, abstractmethod
from typing import Dict, Any

class Output(ABC):
    """输出格式转换的抽象基类"""
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        pass

class JsonOutput(Output):
    """JSON格式输出"""
    def format(self, data: Dict[str, Any]) -> str:
        return json.dumps(data, ensure_ascii=False)

def process_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理输入数据"""
    try:
        from agents import Agent, Runner
        
        # 初始化Agent
        agent = Agent(name="Assistant", instructions="You are a helpful assistant")
        
        # 从输入数据获取提示词
        prompt = input_data.get('prompt', '')
        
        # 运行Agent
        result = Runner.run_sync(agent, prompt)
        
        return {
            'status': 'success',
            'output': result.final_output
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='AI Agent Runner')
    parser.add_argument('--verbose', action='store_true', help='启用详细输出模式')
    parser.add_argument('--api-key', help='设置OpenAI API密钥')
    parser.add_argument('--base-url', help='设置OpenAI API基础URL')
    parser.add_argument('--output-format', choices=['json'], default='json',
                        help='输出格式 (默认: json)')
    parser.add_argument('input', nargs='?', type=argparse.FileType('r'), 
                        default=sys.stdin, help='JSON输入文件(默认为stdin)')
    
    args = parser.parse_args()

    try:
        # 配置OpenAI API
        if args.base_url:
            from openai import AsyncOpenAI
            from agents import set_default_openai_client
            client = AsyncOpenAI(
                api_key=args.api_key or os.environ.get('OPENAI_API_KEY'),
                base_url=args.base_url
            )
            set_default_openai_client(client)
        elif args.api_key:
            os.environ['OPENAI_API_KEY'] = args.api_key
        elif 'OPENAI_API_KEY' not in os.environ:
            raise ValueError("请设置OPENAI_API_KEY环境变量或使用--api-key参数")

        # 读取输入
        input_data = json.load(args.input)
        
        # 处理输入数据
        result = process_input(input_data)
        
        # 选择输出格式
        output_formatter = JsonOutput()
        
        # 输出结果
        print(output_formatter.format(result))
        
        if args.verbose:
            print(f"详细信息: {result}", file=sys.stderr)
        
        sys.exit(0 if result['status'] == 'success' else 1)
        
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # 创建 README 文件，包含环境变量设置说明
    readme_content = '''# AIO Agent 项目

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
'''
    if not os.path.exists('src'):
        os.makedirs('src')
        
    with open('src/main.py', 'w', encoding='utf-8') as f:
        f.write(hello_world_content)
        
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

@click.group()
def cli():
    """aio - Python 项目打包工具"""
    pass

@cli.command()
@click.option('--config', default=None, help='指定配置文件路径（JSON 格式）')
def init(config):
    """初始化 Python 环境和项目模板"""
    config_data = load_config(config)
    required_packages = config_data["packages"]

    # 创建虚拟环境
    if not os.path.exists('venv'):
        print("正在创建虚拟环境...")
        subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])
    else:
        print("虚拟环境已存在，跳过创建。")

    # 获取虚拟环境路径
    python_path, pip_path = get_venv_paths()

    # 安装必要的包
    print("正在安装必要的包...")
    tsinghua_mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    for package in required_packages:
        try:
            subprocess.check_call([pip_path, 'install', package, '-i', tsinghua_mirror])
        except subprocess.CalledProcessError as e:
            print(f"安装 {package} 失败：{e}")
            sys.exit(1)

    # 创建项目模板
    print("正在创建项目模板...")
    create_project_template()

    print("初始化完成！")

@cli.command()
@click.option('--config', default=None, help='指定配置文件路径（JSON 格式）')
def build(config):
    """打包 Python 项目为 exe 文件"""
    config_data = load_config(config)
    main_script = config_data["main_script"]
    build_name = config_data["build_name"]
    required_packages = config_data["packages"]  # 获取配置的依赖包列表

    if not os.path.exists('venv'):
        print("错误：请先运行 'aio init' 初始化环境！")
        sys.exit(1)

    # 获取虚拟环境路径
    python_path, pip_path = get_venv_paths()

    # 检查主脚本是否存在
    if not os.path.exists(main_script):
        print(f"错误：主脚本 {main_script} 不存在！")
        sys.exit(1)

    # 执行 PyInstaller 打包
    print(f"开始打包 {main_script} 为 {build_name}.exe...")
    try:
        pyinstaller_args = [
            python_path,
            '-m', 'PyInstaller',
            '--onefile',
            f'--name={build_name}',
        ]
        
        # 为所有配置的包添加 hidden-import
        for package in required_packages:
            pyinstaller_args.append(f'--hidden-import={package}')
            
        pyinstaller_args.append(main_script)
        
        subprocess.check_call(pyinstaller_args)
        print(f"打包完成！请查看 dist 目录下的 {build_name} 可执行文件。")
    except subprocess.CalledProcessError as e:
        print(f"打包过程中出现错误：{e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()