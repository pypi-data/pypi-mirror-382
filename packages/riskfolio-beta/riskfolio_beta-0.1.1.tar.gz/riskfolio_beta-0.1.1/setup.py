from setuptools import setup, find_packages

setup(
    name="finattrib",                       # 库的名字
    version="0.1.0",                        # 版本号
    author="Your Name",
    author_email="you@example.com",
    description="A toolkit for RWA attribution, G-SIB scoring, and TCE optimization in fixed income portfolios.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/finattrib",  # 你的GitHub地址
    packages=find_packages(),               # 自动查找子包
    install_requires=[                      # 安装依赖
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "matplotlib>=3.5.0",
        "scipy>=1.9.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)