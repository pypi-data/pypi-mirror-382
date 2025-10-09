"""
Setup script for StringSight package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stringsight",
    version="0.1.0",
    author="Lisa Dunlap",
    description="Explain Large Language Model Behavior Patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "tqdm>=4.65.0",
        "pydantic>=1.8.0",
        "litellm>=1.0.0",
        "sentence-transformers>=2.2.0",
        "hdbscan>=0.8.29",
        "umap-learn>=0.5.3",
        "wandb>=0.15.0",
        "openai>=1.0.0",
        "plotly>=5.15.0",
        "pyarrow>=12.0.0",
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "python-multipart>=0.0.6",
        "omegaconf>=2.3.0",
        "nltk>=3.8.0",
        "rouge-score>=0.1.2",
        "markdown>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "viz": [
            "streamlit>=1.28.0",
            "gradio>=4.0.0",
            "plotly>=5.15.0",
        ],
        "ml": [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "datasets>=2.14.0",
            "vllm>=0.3.0",
        ],
        "full": [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "datasets>=2.14.0",
            "vllm>=0.3.0",
            "streamlit>=1.28.0",
            "gradio>=4.0.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stringsight=stringsight.cli:main",
        ],
    },
) 