from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="printfxpy",
    version="1.0.6",
    description="A simple and colorful text printing library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="kaedeek",
    license="MIT",
    packages=find_packages(include=["printfx", "printfx.*"]),
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.8, <3.14",
    url="https://github.com/kaedeek/printfxpy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)