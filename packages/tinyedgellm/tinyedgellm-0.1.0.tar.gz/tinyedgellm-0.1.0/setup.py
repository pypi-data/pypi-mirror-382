from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tinyedgellm",
    version="0.1.0",
    author="Krishna Bajpai, Vedanshi Gupta",
    author_email="krishna@krishnabajpai.me, vedanshigupta158@gmail.com",
    description="A modular framework for LLM quantization, structured pruning, and edge deployment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krish567366/tinyedgellm",
    license="MIT",
    packages=find_packages(),
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
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.20.0",
        "onnxruntime>=1.14.0",
        "bitsandbytes>=0.41.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "tqdm>=4.64.0",
        "psutil>=5.8.0",
        "accelerate>=0.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocs-git-revision-date-localized-plugin>=1.2.0",
            "mkdocs-git-committers-plugin-2>=2.2.0",
            "mkdocs-minify-plugin>=0.8.0",
            "pymdown-extensions>=10.0.0",
        ],
        "tflite": [
            "tflite-runtime>=2.11.0",
        ],
    },
)