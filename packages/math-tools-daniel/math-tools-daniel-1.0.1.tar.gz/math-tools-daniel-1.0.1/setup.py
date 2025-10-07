from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    page_description = f.read()

# Lê dependências de produção (que são vazias neste caso)
try:
    with open("requirements.txt") as f:
        requirements = [line.strip() for line in f.read().splitlines()
                       if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    requirements = []

# Lê dependências de desenvolvimento
try:
    with open("requirements-dev.txt") as f:
        dev_requirements = [line.strip() for line in f.read().splitlines()
                           if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    dev_requirements = []

setup(
    name="math-tools-daniel",
    version="1.0.1",
    author="Daniel Santos",
    author_email="danfergatthi@gmail.com",
    description="Um pacote matemático completo com funções básicas e avançadas",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DanielSantos08/dio_suzano_python_developer/tree/master/math-tools-daniel",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'test': dev_requirements,
    },
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="mathematics, statistics, sequences, fibonacci, prime, factorial",
    project_urls={
        "Bug Reports": "https://github.com/DanielSantos08/dio_suzano_python_developer/math-tools-daniel/issues",
        "Source": "https://github.com/DanielSantos08/dio_suzano_python_developer/math-tools-daniel",
        "Documentation": "https://github.com/DanielSantos08/dio_suzano_python_developer/math-tools-daniel/wiki",
    },
)