import ollama_toolkit
from ollama_toolkit.ollama_client import OllamaClient

print("Ollama toolkit imported successfully!")
print(f"Package version: {ollama_toolkit.__version__ if hasattr(ollama_toolkit, '__version__') else 'unknown'}")

# 创建客户端实例
print("Creating OllamaClient instance...")
client = OllamaClient()
print("OllamaClient instance created successfully!")
print(f"Default model: {client.default_model}")
print(f"Base URL: {client.base_url}")

print("\nTest completed successfully!")