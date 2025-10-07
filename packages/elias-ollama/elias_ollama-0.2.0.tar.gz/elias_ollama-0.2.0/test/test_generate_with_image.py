import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_toolkit.ollama_client import OllamaClient

# 测试参数
image_path = r"C:\Users\Administrator\Desktop\test\638948447558127941.png"
model_name = "qwen2.5vl:latest"

print("===== 测试generate方法处理图片 ======")
print(f"测试图片: {image_path}")
print(f"使用模型: {model_name}")

# 检查图片文件是否存在
if not os.path.exists(image_path):
    print(f"错误: 图片文件 '{image_path}' 不存在。请确保文件路径正确。")
    exit(1)

# 获取文件大小
file_size = os.path.getsize(image_path)
print(f"图片文件大小: {file_size} 字节")

try:
    # 初始化Ollama客户端
    client = OllamaClient()
    
    print("\n调用generate方法分析图片...")
    # 测试generate方法处理带图片的请求
    response = client.generate(
        prompt="请分析这张图片的内容",
        model=model_name,
        images=[image_path],  # 使用正确的参数名和格式
        stream=False
    )
    
    print(f"\ngenerate方法返回结果:")
    print(f"响应类型: {type(response)}")
    print(f"响应内容:\n{response}")
    
    print("\n===== 测试完成 ======")
    exit(0)
    
except Exception as e:
    print(f"\n测试出错: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n===== 测试失败 ======")
    exit(1)