"""
Setup script for HalluNox package.

This file provides backward compatibility for pip installs that don't support
pyproject.toml and ensures proper package installation.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Package metadata
setup(
    name="hallunox",
    version="0.6.3",
    author="Nandakishor M",
    author_email="support@convaiinnovations.com",
    description="A confidence-aware routing system for LLM hallucination detection using multi-signal approach",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/convai-innovations/hallunox",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.13.0",
        "transformers>=4.21.0",
        "datasets>=2.0.0",
        "FlagEmbedding>=1.2.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.21.0",
        "tqdm>=4.64.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "training": [
            "wandb>=0.12.0",
            "tensorboard>=2.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hallunox-train=hallunox.training:main",
            "hallunox-infer=hallunox.inference:main",
        ],
    },
    package_data={
        "hallunox": ["*.txt", "*.md", "*.yaml", "*.yml"],
    },
    include_package_data=True,
    license="AGPL-3.0",
    keywords=[
        "hallucination-detection",
        "llm",
        "confidence-estimation", 
        "model-reliability",
        "uncertainty-quantification",
        "ai-safety",
    ],
)