from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="telegram-calendar",
    version="0.3.0",
    author="S-i1-V",
    author_email="vanosaprikin@gmail.com",
    description="Telegram calendar builder library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SI1V/tg_calendar.git",
    packages=find_packages(exclude=["example", "venv", "tests*"]),
    python_requires='>=3.10',
    install_requires=[
        "aiogram>=3.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
