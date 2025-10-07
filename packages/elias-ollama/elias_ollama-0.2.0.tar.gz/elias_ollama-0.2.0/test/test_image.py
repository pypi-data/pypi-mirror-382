# 导入必要的模块
from ollama_toolkit.ollama_client import OllamaClient
import sys
import io
import os
import datetime

# 创建日志目录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建日志文件
log_file = os.path.join(log_dir, f"test_image_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 打开日志文件
f = open(log_file, 'w', encoding='utf-8')
print(f"输出将同时写入日志文件: {log_file}")

# 确保中文显示正常
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置输出重定向到文件和控制台
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()  # 确保立即写入
    def flush(self):
        for f in self.files:
            f.flush()

# 先确保stdout编码正确，再进行重定向
sys.stdout = Tee(sys.stdout, f)

# 创建客户端实例
client = OllamaClient(base_url="http://localhost:11434", default_model="qwen3")

# 测试图片分析功能
def test_image_analysis():
    try:
        print("开始测试图片分析功能...")
        
        # 列出可用模型，确认qwen2.5vl模型存在
        print("\n1. 列出可用模型:")
        models = client.list_models()
        for model in models:
            print(f"- {model['name']}")
        
        # 设置图片路径和模型
        image_path = r"C:\Users\Administrator\Desktop\test\638948447558127941.png"
        model = "qwen2.5vl:latest"
        prompt = "详细分析这张图片"
        
        print(f"\n2. 准备分析图片:")
        print(f"- 图片路径: {image_path}")
        print(f"- 使用模型: {model}")
        print(f"- 提示文本: {prompt}")
        
        # 尝试分析图片
        print("\n3. 开始分析图片...")
        response = client.generate(prompt, images=[image_path], model=model)
        
        print("\n4. 分析结果:")
        print(f"{response}")
        
    except Exception as e:
        print(f"\n测试出错:")
        import traceback
        traceback.print_exc()

# 运行测试
if __name__ == "__main__":
    test_image_analysis()
    print("\n测试完成")