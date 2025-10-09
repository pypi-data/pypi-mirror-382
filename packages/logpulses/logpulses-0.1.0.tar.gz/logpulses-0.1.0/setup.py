from setuptools import setup, find_packages

setup(
    name="logpulses",
    version="0.1.0",
    description="A structured logging package for Python applications",
    author="Hariharan S",
    packages=find_packages(),
    install_requires=["psutil"],
    python_requires=">=3.8",
)
