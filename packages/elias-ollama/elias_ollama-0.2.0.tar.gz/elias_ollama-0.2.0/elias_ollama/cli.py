#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from elias_ollama.ollama_client import OllamaClient


def main():
    """
    命令行入口函数
    """
    parser = argparse.ArgumentParser(description='Ollama模型调用工具')
    
    # 基本参数
    parser.add_argument('prompt', type=str, nargs='?', help='提示文本')
    parser.add_argument('--model', '-m', type=str, help='要使用的模型名称')
    parser.add_argument('--url', '-u', type=str, default='http://localhost:11434', help='Ollama API的URL')
    parser.add_argument('--no-stream', action='store_true', help='禁用流式输出')
    
    # 文件上传参数
    parser.add_argument('--image', '-i', type=str, action='append', help='要上传的图片文件路径，可以多次使用')
    parser.add_argument('--file', '-f', type=str, action='append', help='要上传的其他文件路径，可以多次使用')
    
    # 其他操作
    parser.add_argument('--list-models', action='store_true', help='列出可用的模型')
    parser.add_argument('--chat', action='store_true', help='使用聊天模式')
    
    args = parser.parse_args()
    
    # 创建客户端
    client = OllamaClient(base_url=args.url, default_model=args.model or "qwen3")
    
    # 列出模型
    if args.list_models:
        models = client.list_models()
        if models:
            print("可用模型列表:")
            for model in models:
                print(f"- {model['name']}")
        else:
            print("没有找到可用的模型")
        return
    
    # 检查是否提供了提示文本
    if not args.prompt:
        # 如果没有提供提示文本且不是列出模型，则进入交互模式
        interactive_mode(client, args)
    else:
        # 执行单次请求
        if args.chat:
            # 聊天模式
            messages = [{"role": "user", "content": args.prompt}]
            client.chat(messages, model=args.model, stream=not args.no_stream)
        else:
            # 生成模式
            client.generate(
                args.prompt,
                model=args.model,
                stream=not args.no_stream,
                images=args.image,
                files=args.file
            )


def interactive_mode(client, args):
    """
    交互模式，允许用户持续输入提示
    """
    print(f"进入Ollama交互模式（模型: {client.default_model}, URL: {client.base_url}）")
    print("输入'quit'或'exit'退出，输入'!models'列出可用模型")
    
    if args.chat:
        # 聊天模式，保存对话历史
        messages = []
        
        while True:
            try:
                prompt = input("\n用户: ")
                if prompt.lower() in ('quit', 'exit'):
                    break
                if prompt.lower() == '!models':
                    models = client.list_models()
                    if models:
                        print("\n可用模型列表:")
                        for model in models:
                            print(f"- {model['name']}")
                    else:
                        print("\n没有找到可用的模型")
                    continue
                
                # 添加用户消息到历史
                messages.append({"role": "user", "content": prompt})
                
                # 调用模型
                print("\nAI:", end="", flush=True)
                response = client.chat(messages, stream=not args.no_stream)
                
                # 添加AI响应到历史
                messages.append({"role": "assistant", "content": response})
            except KeyboardInterrupt:
                print("\n中断输入")
                break
            except EOFError:
                break
    else:
        # 生成模式，不保存对话历史
        while True:
            try:
                prompt = input("\n> ")
                if prompt.lower() in ('quit', 'exit'):
                    break
                if prompt.lower() == '!models':
                    models = client.list_models()
                    if models:
                        print("\n可用模型列表:")
                        for model in models:
                            print(f"- {model['name']}")
                    else:
                        print("\n没有找到可用的模型")
                    continue
                
                client.generate(prompt, stream=not args.no_stream)
            except KeyboardInterrupt:
                print("\n中断输入")
                break
            except EOFError:
                break


if __name__ == '__main__':
    main()