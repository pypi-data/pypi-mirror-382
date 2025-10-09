from setuptools import setup, find_packages
import io
import re
import os

here = os.path.abspath(os.path.dirname(__file__))

def read(fname):
    with io.open(os.path.join(here, fname), encoding='utf-8') as f:
        return f.read()

def read_version():
    ver_file = os.path.join(here, "mwdrive", "version.py")
    text = read(os.path.relpath(ver_file, here))
    m = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', text)
    if m:
        return m.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="mwdrive",  # <-- 改为你要上传到 PyPI 的包名
    version=read_version(),
    description="Motor Driver Control Library for products from CyberBeast",
    long_description=read("README.md") if os.path.exists(os.path.join(here, "README.md")) else "",
    long_description_content_type="text/markdown",
    author="CyberBeast",
    packages=find_packages(),  # 会在项目根找到 mwdrive/
    include_package_data=True,
    scripts=[
        "scripts/mtool",
        "scripts/mtool.bat",
    ],
    install_requires=[
        # 在这里列出运行时依赖，例如 "pyusb>=1.2.1"
    ],
    # 如果希望安装后生成命令行脚本，可在此处添加 entry_points
    # entry_points={
    #     "console_scripts": [
    #         "mtool=mwdrive.mtool:main",
    #     ],
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
