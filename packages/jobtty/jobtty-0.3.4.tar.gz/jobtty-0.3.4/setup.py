from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jobtty",
    version="0.3.4",
    author="Croscom Software",
    author_email="konrad.zdzieba@croscomsoftware.com",
    description="🚀 Terminal Job Board - Find your next role from the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/croscomsoftware/jobtty",
    packages=find_packages(include=['jobtty', 'jobtty.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "requests>=2.28.0",
        "stripe>=5.0.0",
        "keyring>=23.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "qrcode[pil]>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
        "git": [
            "GitPython>=3.1.0",
        ],
        "collaboration": [
            "websockets>=11.0.0",
        ],
        "challenges": [
            "docker>=6.0.0",
        ],
        "all": [
            "GitPython>=3.1.0",
            "websockets>=11.0.0", 
            "docker>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jobtty=jobtty.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)