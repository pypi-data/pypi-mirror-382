from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="plain-flags-sdk",
    version="1.0.3",
    packages=find_packages(where="src"),
    author="Andrei Leonte",
    author_email="andrei.leonte.dev@gmail.com",
    url="https://plainflags.dev",
    description="Python SDK for the Plain Flags free feature flag system",
    package_dir={"": "src"},
    install_requires=["aiohttp"],
    long_description=description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Adjust according to your license
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.6"  # Specify minimum Python version
)
