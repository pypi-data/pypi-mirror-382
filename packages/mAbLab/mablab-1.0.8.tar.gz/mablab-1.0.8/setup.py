from setuptools import setup, find_packages

setup(
    name="mAbLab",
    version="1.0.8",
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
        "antpack==0.3.6.1",
        "biopython==1.84",
        "numpy<=1.21.6",
        "Levenshtein==0.26.1",
        "ImmuneBuilder==1.2",
        "pandas<=1.3.5",
        "scipy<=1.7.3",
        "torch==1.13.1",
        "torchaudio==0.13.1",
        "torchvision==0.14.1",
    ],
)
