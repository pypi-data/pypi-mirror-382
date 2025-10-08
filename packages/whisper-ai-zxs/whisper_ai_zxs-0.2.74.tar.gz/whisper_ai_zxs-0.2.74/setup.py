from setuptools import setup, find_packages

setup(
    name="whisper_ai_zxs",  # 你的包名
    version="0.2.74",  # 版本号
    author="植想说",
    author_email="lizhenhua@zxslife.com",
    description="植想说的AI客服工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_package",  # 你的 GitHub 地址
    packages=find_packages(),  # 自动发现包
    install_requires=[
        "openai",
        "pymysql",
        "requests",
        "typing_extensions",
        "openpyxl",
        "cryptography"
       # "numpy",  # 如果你的包依赖第三方库，在这里列出
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # 适用的 Python 版本
)
