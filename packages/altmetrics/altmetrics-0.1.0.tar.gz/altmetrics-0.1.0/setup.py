from setuptools import find_packages, setup

setup(
    name="altmetrics",
    version="0.1.0",
    description="A package to calculate alternative-aware WER, CER, BLEU, and chrF.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Per Kummervold",
    author_email="Per.Kummervold@nb.no",
    url="https://github.com/peregilk/altmetrics",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "jiwer>=2.0.0",
        "sacrebleu>=2.4.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
