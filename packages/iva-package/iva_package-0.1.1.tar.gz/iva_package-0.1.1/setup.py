from setuptools import setup, find_packages

setup(
    name="iva_package",          # Package name on PyPI
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,   # Include all files in the package
    install_requires=[],         # Add dependencies if needed
    author="Unknown",
    description="8 Python files",
    python_requires=">=3.9",
)
