import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    setuptools.setup(
    name="work-MCP", # 替换为您的包名
    version="0.0.1", # 您的包的初始版本
    author="QJYJH", # 您的名字
    author_email="x2683288092@gmail.com", # 您的邮箱
    description="A small example package for MCP", # 项目的简短描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/yourusername/my_mcp_project", # 项目的URL
    packages=setuptools.find_packages(),
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
    python_requires='>=3.10', # 指定项目依赖的Python版本 [12]
    install_requires=[
    # 在此列出您的项目依赖项，例如：
    # "requests",
    "mcp[cli]" # 如果您的项目依赖于MCP [12]
    ],
    )