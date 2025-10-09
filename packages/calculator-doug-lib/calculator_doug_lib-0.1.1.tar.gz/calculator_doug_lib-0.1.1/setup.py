from setuptools import setup, find_packages

# Lendo o README.md para o PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="calculator-doug-lib",  # ⚡ Nome com hífen para o PyPI
    version="0.1.1",
    description="Biblioteca de operações matemáticas básicas em Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Douglas Lima",
    author_email="douglasbolislima@gmail.com",
    url="https://github.com/douglasbolis/ps_calculadora_lib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
