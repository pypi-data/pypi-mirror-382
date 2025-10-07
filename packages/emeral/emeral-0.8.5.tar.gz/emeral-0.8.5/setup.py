from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # 基本信息
    name="emeral",
    version="0.8.5",
    author="ga.ga.ga.ga.ga",
    author_email="1602422136@qq.com",
    description="A library for making simple 2D games",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    
    packages=find_packages(),
    
    # Python版本要求
    python_requires=">=3.7",
    
    # 依赖
    install_requires=[
        "pygame>=2.0.0",     # 游戏库
        "pywin32; sys_platform == 'win32'",  # Windows专用，仅Windows安装
        "numpy>=1.20.0",     # 数值计算
        "pillow>=8.0.0"      # 图像处理（注意：包名是pillow，但import用PIL）
    ],
    
    # 分类器
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    
    # 许可证
    license="MIT",
    
    # 关键词
    keywords="emeral",
    
    # 包含数据文件
    include_package_data=True,
    package_data={
        "emeral": ["resources/*.png"],
    }
)