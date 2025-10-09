# DPS - Docker Pull Smart
# 项目名称: dps_liumou_Stable
# 命令名称: dps

from setuptools import setup, find_packages

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
def parse_requirements(filename):
    """解析requirements.txt文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="dps_liumou_Stable",
    version="1.0.2",
    author="坐公交也用券",
    author_email="liumou.site@qq.com",
    description="智能Docker镜像拉取工具 - 自动选择最优镜像源",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/liumou/dps_liumou_Stable",
    project_urls={
        "Bug Tracker": "https://gitee.com/liumou/dps_liumou_Stable/issues",
        "Documentation": "https://gitee.com/liumou/dps_liumou_Stable/blob/main/README.md",
        "Source": "https://gitee.com/liumou/dps_liumou_Stable",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords="docker pull mirror accelerate smart intelligent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=parse_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "dps=dps_liumou_Stable:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["Windows", "Linux", "macOS"],
)