# setup.py
from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8") if (HERE / "README.md").exists() else ""

setup(
    name="LSTM-SAM-TL",                     # distribution name on PyPI (hyphen is fine)
    version="0.1.8",                        # bump when you publish
    description="Bi-LSTM with custom Attention Mechanism and Tuning: Training/Test and TimeSeries CV models",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Samuel Daramola",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "scikit-learn",
        "tensorflow>=2.9",                  # users on Apple Silicon may prefer tensorflow-macos (document this in README)
        "keras-tuner>=1.4.0",              # import is `keras_tuner`, package name uses hyphen
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    project_urls={
        "Homepage": "https://pypi.org/project/LSTM-SAM-TL/",
        # "Source": "https://github.com/your/repo",
        # "Issues": "https://github.com/your/repo/issues",
    },
)
