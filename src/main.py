import json
import sys
import os
import argparse
from agents import Agent, Runner

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='AI Agent Runner')
    parser.add_argument('--verbose', action='store_true', help='启用详细输出模式')
    parser.add_argument('--api-key', help='设置OpenAI API密钥')
    parser.add_argument('--base-url', help='设置OpenAI API基础URL')
    parser.add_argument('--model', help='设置模型名称')
    parser.add_argument('input', nargs='?', type=argparse.FileType('r'), 
                        default=sys.stdin, help='JSON输入文件(默认为stdin)')
    args = parser.parse_args()
    print(f"args: {args}")
    try:
        # 初始化Agent
        agent = Agent(name="Assistant", instructions="You are a helpful assistant")
        
        # 设置OpenAI客户端
        if args.base_url:
            from openai import AsyncOpenAI
            from agents import set_default_openai_client, OpenAIChatCompletionsModel, ModelSettings
            
            client = AsyncOpenAI(
                api_key=args.api_key or os.environ.get('OPENAI_API_KEY'),
                base_url=args.base_url,
                timeout=120.0,  # 增加超时时间到120秒
                max_retries=5,  # 增加重试次数到5次
            )
            
            # 使用OpenAIChatCompletionsModel替代默认的ResponsesModel
            model = OpenAIChatCompletionsModel(
                model=args.model or "gpt-3.5-turbo",
                openai_client=client
            )
            
            # 初始化Agent时指定model
            agent = Agent(
                name="Assistant", 
                instructions="You are a helpful assistant",
                model=model,
                model_settings=ModelSettings(
                    temperature=0.7,
                )
            )
            set_default_openai_client(client)
            
        elif args.api_key:
            os.environ['OPENAI_API_KEY'] = args.api_key
        elif 'OPENAI_API_KEY' not in os.environ:
            raise ValueError("请设置OPENAI_API_KEY环境变量或使用--api-key参数")

        # 从stdin读取JSON输入
        try:
            # 检查是否有可用输入
            if args.input.isatty():  # 如果是终端
                input_data = {"prompt": "hello"}
            else:
                # 设置超时读取
                import select
                if select.select([args.input], [], [], 0.0)[0]:  # 非阻塞检查
                    input_data = json.load(args.input)
                else:
                    input_data = {"prompt": "hello"}
        except json.JSONDecodeError:
            input_data = {"prompt": "hello"}
            
        print(f"input_data: {input_data}")
        # 从输入数据获取提示词
        prompt = input_data.get('prompt', '')

        print(f"prompt: {prompt}")
        
        # 运行Agent
        result = Runner.run_sync(agent, prompt)

        # 构建输出JSON
        output = {
            'status': 'success',
            'output': result.final_output
        }
        
        # 输出JSON结果到stdout
        json.dump(output, sys.stdout, ensure_ascii=False)
        sys.stdout.write('\n')
        
        if args.verbose:
            print(f"详细信息: {result}", file=sys.stderr)
            
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # 处理API调用失败
        error_message = f"API调用失败: {str(e)}"
        print(error_message, file=sys.stderr)
        output = {
            'status': 'error',
            'error': error_message
        }
        if args.verbose:
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
    
    # 输出JSON结果到stdout
    json.dump(output, sys.stdout, ensure_ascii=False)
    sys.stdout.write('\n')

if __name__ == "__main__":
    main()
