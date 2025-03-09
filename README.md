# AIO
一种agent协议的设计


从标准输入（stdin）读取 JSON 数据，并将结果输出到标准输出（stdout）。这种设计非常适合管道操作，可以与其他工具无缝集成。以下是详细的设计方案和示例实现。

1. 命令行参数设计
工具默认从 stdin 读取 JSON 数据，并将结果输出到 stdout。
支持以下可选参数：
--verbose：启用详细输出模式，将额外信息输出到 stderr。
-h 或 --help：显示帮助信息。

# 从 stdin 读取 JSON，输出 TXT 格式到 stdout
echo '{"key": "value"}' | mytool

2. JSON 解析
从 stdin 读取 JSON 数据，使用 Python 的 json.load(sys.stdin) 解析。
如果 JSON 格式不正确，捕获错误并将消息输出到 stderr，返回退出码 1。

3. 输出模块
内部处理后，数据转换为对应格式并输出到 stdout。

4. 错误处理
捕获 JSON 解析错误、不支持的格式等异常，将错误信息输出到 stderr。
成功执行返回退出码 0，失败返回退出码 1。

5. 帮助信息
通过 -h 或 --help 参数提供使用说明，清晰说明工具从 stdin 读取 JSON 并输出到 stdout。

示例实现（Python）
以下是一个完整的 Python 实现，展示了上述设计方案：
```python
import sys
import json
import argparse

# 输出格式的抽象基类
class Output:
    def write(self, data):
        raise NotImplementedError

# TXT 格式输出
class TxtOutput(Output):
    def write(self, data):
        sys.stdout.write(str(data) + '\n')

# 主函数
def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="从 stdin 读取 JSON 并转换为指定格式输出到 stdout")
    parser.add_argument('--verbose', action='store_true', help="启用详细输出")
    args = parser.parse_args()

    # 从 stdin 读取并解析 JSON
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.stderr.write("错误: JSON 格式不正确\n")
        sys.exit(1)

    # 执行输出
    try:
        output.write(data)
        if args.verbose:
            sys.stderr.write("处理完成\n")
    except Exception as e:
        sys.stderr.write(f"错误: {str(e)}\n")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

将上述代码保存为 mytool.py。

5. 管道操作
可以将工具与其他命令组合使用


输入：工具从 stdin 读取 JSON 数据。
输出：转换后的数据输出到 stdout。
错误处理：JSON 解析错误或格式不支持时，错误信息输出到 stderr，退出码为 1。
扩展性：通过添加新的 Output 子类，可以轻松支持更多格式（如 xml）。
