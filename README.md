# AIO：Agent协议设计

本设计旨在创建一个通用的Agent协议，通过标准输入（stdin）接收JSON数据，并将其处理结果输出到标准输出（stdout）。这种设计支持管道操作，方便与其他工具集成。

## 1. 命令行参数

默认情况下，工具从stdin读取JSON，并将结果输出到stdout。

**可选参数：**

* `--verbose`：启用详细输出模式，将额外信息输出到stderr。
* `-h` 或 `--help`：显示帮助信息。

**示例：**

```bash
echo '{"key": "value"}' | mytool
```

## 2. JSON解析

* 使用Python的`json.load(sys.stdin)`解析stdin中的JSON数据。
* 若JSON格式错误，则捕获`json.JSONDecodeError`，将错误信息输出到stderr，并返回退出码1。

## 3. 输出模块

* 数据经过内部处理后，转换为指定格式（默认为TXT）并输出到stdout。
* 通过抽象类 `Output` 来实现不同格式的输出。

## 4. 错误处理

* 捕获JSON解析错误、不支持的格式等异常。
* 错误信息输出到stderr。
* 成功执行返回退出码0，失败返回退出码1。

## 5. 帮助信息

* 通过`-h`或`--help`参数显示工具的使用说明，明确说明工具从stdin读取JSON并输出到stdout。

## 6. 示例实现（Python）

以下是一个Python示例，展示了上述设计方案：

```python
import sys
import json
import argparse

# 输出格式的抽象基类
class Output:
    def write(self, data):
        raise NotImplementedError

# TXT格式输出
class TxtOutput(Output):
    def write(self, data):
        sys.stdout.write(str(data) + '\n')

#创建默认输出实例。
output = TxtOutput()

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

将上述代码保存为`mytool.py`。

## 7. 管道操作

* 工具可以与其他命令组合使用，实现复杂的数据处理流程。

**输入：**

* 工具从stdin读取JSON数据。

**输出：**

* 转换后的数据输出到stdout。

**错误处理：**

* JSON解析错误或格式不支持时，错误信息输出到stderr，退出码为1。

**扩展性：**

* 通过添加新的`Output`子类，可以轻松支持更多格式（如XML）。
