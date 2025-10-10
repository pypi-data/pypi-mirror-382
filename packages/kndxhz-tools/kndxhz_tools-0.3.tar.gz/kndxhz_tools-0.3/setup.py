from setuptools import setup, find_packages

setup(
    name="kndxhz_tools",
    version="0.3",
    packages=find_packages(),
    install_requires=[""],
    entry_points={
        "console_scripts": [
            # 定义命令行脚本（可选）
        ],
    },
    author="kndxhz",
    author_email="kndxhz@163.com",
    description="一个自用的工具集",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kndxhz/kndxhz_tools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
