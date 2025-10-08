import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))


# you need to change all these
VERSION = '1.1.6'
DESCRIPTION = 'ZX_RPA - 机器人流程自动化工具库，提供统一、简洁的API接口'

# 单独安装某个功能模块，需要在extras_require中添加依赖项
# 例如：pip install zx_rpa[qiniu]
setup(
    name="zx_rpa",
    version=VERSION,
    author="zang xin",
    author_email="zangxincz@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        'zx_rpa.system': ['UnRAR.exe'],
        'zx_rpa': ['*.yaml', '*.json']
    },
    include_package_data=True,
    install_requires=[
        # 核心依赖 - 所有模块都需要
        "requests",      # HTTP请求库
        "loguru",         # 日志库
        "PyYAML",           # YAML配置文件处理
    ],
    extras_require={
        # 云存储功能
        "qiniu": ["qiniu"],

        # 数据库功能
        "mysql": ["pymysql"],

        # 浏览器自动化功能（伊性坊等平台）
        "browser": ["DrissionPage"],

        # excel 
        "excel": ["openpyxl"],

        # 完整安装（包含所有可选依赖）
        "all": [
            "qiniu",
            "pymysql",
            "DrissionPage",
            "openpyxl"
        ]
    },
    python_requires=">=3.8",
)
