import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_toolkit.ollama_client import OllamaClient

# 设置中文字体支持
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 测试图片路径
image_path = r"C:\Users\Administrator\Desktop\test\638948447558127941.png"  # 从之前的测试脚本获取的正确路径
model_name = "qwen2.5vl:latest"

def test_image_recognition():
    print("===== 开始图片识别测试 =====")
    print(f"测试图片: {image_path}")
    print(f"使用模型: {model_name}")
    
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图片文件 '{image_path}' 不存在。请确保文件路径正确。")
        return False
    
    # 获取文件大小
    file_size = os.path.getsize(image_path)
    print(f"图片文件大小: {file_size} 字节")
    
    try:
        # 初始化Ollama客户端
        client = OllamaClient()
        
        # 构建消息
        messages = [
            {
                "role": "user",
                "content": "请分析这张图片里有什么内容？"
            }
        ]
        
        print("\n准备发送请求到Ollama服务器...")
        print("提示: 分析图片可能需要较多系统资源，这是正常的")
        print("如果遇到资源限制问题，请考虑使用较小的模型或增加系统资源")
        
        # 调用chat方法进行图片分析
        response = client.chat(
            model=model_name,
            messages=messages,
            images=[image_path],  # 正确的参数名是images，应该是一个列表
            stream=False
        )
        
        print("\n请求发送成功，正在处理响应...")
        print(f"响应类型: {type(response)}")
        
        if isinstance(response, dict):
            print(f"响应包含的键: {list(response.keys())}")
            if 'message' in response and isinstance(response['message'], dict):
                print(f"消息内容: {response['message'].get('content', '无内容')}")
            else:
                print("响应中未找到message字段或message不是字典类型")
        else:
            print(f"响应内容: {response}")
            
        print("\n===== 测试完成 =====")
        return True
        
    except Exception as e:
        print(f"\n测试出错: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print("错误堆栈:")
        traceback.print_exc()
        print("\n===== 测试失败 =====")
        return False

if __name__ == "__main__":
    test_image_recognition()