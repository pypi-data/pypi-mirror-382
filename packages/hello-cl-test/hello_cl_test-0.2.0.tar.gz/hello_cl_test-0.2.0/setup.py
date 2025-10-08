from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hello-cl-test",  # Change this to your desired package name
    version="0.2.0",
    author="Mukund Prasad H S",
    author_email="mukund.hs@cirruslabs.io",
    description="A simple Hello World package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mukundprasadhscl/hello-cl",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)