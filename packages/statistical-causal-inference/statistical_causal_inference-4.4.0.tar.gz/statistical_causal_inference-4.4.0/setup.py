"""
Statistical Causal Inference Package Setup
High-performance causal attribution and inference algorithms
"""
from setuptools import setup, find_packages

setup(
    name="statistical-causal-inference",
    version="4.4.0",
    author="CausalMMA Team",
    author_email="durai@infinidatum.net",
    description="Production-ready causal attribution and inference API with comprehensive monitoring, testing, and LLM integration",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rdmurugan/statistical-causal-inference",
    project_urls={
        "Bug Tracker": "https://github.com/rdmurugan/statistical-causal-inference/issues",
        "Documentation": "https://github.com/rdmurugan/statistical-causal-inference",
        "Source Code": "https://github.com/rdmurugan/statistical-causal-inference",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="causal-inference, machine-learning, statistics, llm, artificial-intelligence, performance, scalability, async, vectorization",
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "networkx>=2.6.0",
        "scipy>=1.7.0",
        "matplotlib>=3.3.0",
        "plotly>=5.0.0",
        "openai>=1.0.0",
        "numba>=0.56.0",
        "dask>=2022.1.0",
        "psutil>=5.8.0",
        "pyyaml>=6.0.0",
        "aiofiles>=23.0.0",
        "pyarrow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "full": [
            "langchain>=0.0.200",
            "llama-index>=0.7.0",
            "transformers>=4.20.0",
            "torch>=1.11.0",
            "streamlit>=1.25.0",
            "anthropic>=0.7.0",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
