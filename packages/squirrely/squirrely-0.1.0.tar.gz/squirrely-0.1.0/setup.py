# cSpell:ignore squirrely
# setup.py
from setuptools import setup, find_packages

setup(
    name="squirrely",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "squirrely=squirrely.main:main",
        ],
    },
    author="K the Owl",
    description="ディレクトリ構成をMarkdownで生成するツール",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="",
    python_requires=">=3.8",
)
