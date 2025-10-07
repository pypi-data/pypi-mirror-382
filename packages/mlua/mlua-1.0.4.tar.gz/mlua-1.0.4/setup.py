from setuptools import setup, find_packages

with open("README.MD", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mlua",
    version="1.0.4",
    author="FreeStar007",
    author_email="3089666858@qq.com",
    description="一个基于 lupa 模块的轻量级扩展库，提供了便捷的 Lua 模块加载与管理功能。",
    license="Apache-2.0",
    license_files=["LICENSE"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FreeStar007/mlua",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
        "lupa",
        "colorama"
    ],
)
