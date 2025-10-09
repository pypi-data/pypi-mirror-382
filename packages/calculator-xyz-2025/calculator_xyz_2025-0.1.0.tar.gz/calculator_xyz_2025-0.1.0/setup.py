from setuptools import setup, find_packages

# Lendo o README.md para o PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="calculator_xyz_2025",  
    version="0.1.0",
    description="Biblioteca de operações matemáticas básicas em Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Paulo Sérgio dos Santos Júnior",
    author_email="paulossjunior@gmail.com",
    url="https://github.com/paulossjunior/calculatora-fastapi-lib_xxx",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)