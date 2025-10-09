from setuptools import find_packages, setup

with open("./README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="kasawa",
    version="0.0.5-beta",
    description="I Make module this for using for easy to work",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/x2super/kasawa",
    author="x2super",
    author_email="kasawaonecap@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "cloudscraper",
        "pystyle"
    ],
    python_requires=">=3.10",
)

