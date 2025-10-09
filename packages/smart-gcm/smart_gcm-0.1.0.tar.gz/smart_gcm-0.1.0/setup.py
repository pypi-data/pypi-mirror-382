from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="smart-gcm",
    version="0.1.0",
    author="Aakash Varma Nadimpalli",
    author_email="aakashvarma1898@gmail.com",
    description="AI-powered Git commit message generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aakashvarma/smart-gcm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "gcm=smart_commit.cli:main",
        ],
    },
    keywords="git commit conventional-commits ai gemini",
    project_urls={
        "Bug Reports": "https://github.com/aakashvarma/smart-gcm/issues",
        "Source": "https://github.com/aakashvarma/smart-gcm",
    },
)