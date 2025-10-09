from setuptools import setup, find_packages

# Lendo o README.md para o PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="super_calculadora_e_KNUCKLES",  # ⚡ Nome com hífen para o PyPI
    version="0.1.0",
    description="Biblioteca BASICA.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rafael Deps ",
    author_email="rafaeldeps15@gmail.com",
    url="https://github.com/RafaelDeps/testes_Lib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
