from setuptools import setup, find_packages

setup(
    name="appscriptify",
    version="0.1.0",
    author="Vansh Choyal",
    author_email="your_email@example.com",
    description="A simple demo package that greets you.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/appscriptify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
