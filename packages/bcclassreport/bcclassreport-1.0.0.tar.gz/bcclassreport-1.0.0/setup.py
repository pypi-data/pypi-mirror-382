from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    "numpy>=1.19.0",
    "matplotlib>=3.3.0",
    "scikit-learn>=0.24.0",
]

setup(
    name="bcclassreport",
    version="1.0.0",
    author="Nachiket Mehendale",
    author_email="your.email@example.com",  # Update this
    description="Simple, intuitive binary classification metrics and visualizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nachiket-Mehendale/bcclassreport",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="binary classification confusion matrix metrics visualization machine-learning",
    project_urls={
        "Bug Reports": "https://github.com/Nachiket-Mehendale/bcclassreport/issues",
        "Source": "https://github.com/Nachiket-Mehendale/bcclassreport",
    },
)