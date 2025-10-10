from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="extended-sklearn-metrics",
    version="0.4.0",
    author="Subashanan Nair",
    author_email="subashnair12@gmail.com",
    description="Comprehensive evaluation library for scikit-learn models with advanced metrics, custom thresholds, and visualizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/subashanannair/extended-sklearn-metrics",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "extended_sklearn_metrics": ["*.py"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.8",
    install_requires=["numpy>=1.24.0", "pandas>=2.0.0", "scikit-learn>=1.3.0"],
)
