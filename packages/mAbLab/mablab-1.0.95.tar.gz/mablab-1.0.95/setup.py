from setuptools import setup, find_packages

setup(
    name="mAbLab",
    version="1.0.95",
    author="R. Paul Nobrega",
    author_email="paul@paulnobrega.net",
    description="A library for analyzing monoclonal antibody characteristics by domain.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PaulNobrega/mAbLab",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "antpack",
        "biopython",
        "numpy",
        "Levenshtein",
        "ImmuneBuilder",
        "pandas",
        "scipy",
        "torch",
        "torchaudio",
        "torchvision",
    ],
)
