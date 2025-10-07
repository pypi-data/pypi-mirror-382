from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="elias_ollama",
    version="0.2.0",
    author="Elias Liu",
    author_email="elias.liu120@gmail.com",
    description="一个用于调用Ollama模型的Python工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tenbj/elias_ollama",  # 替换为实际的仓库URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.25.0',
    ],
    entry_points={
        'console_scripts': [
            'elias-ollama=elias_ollama.cli:main',
        ],
    },
)