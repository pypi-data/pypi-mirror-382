from setuptools import setup, find_packages

setup(
    name="mou-gui",
    version="0.1.1",
    packages=find_packages(),   # will find the 'mou' folder
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "mou-demo=mou.main:main",
        ],
    },
)
