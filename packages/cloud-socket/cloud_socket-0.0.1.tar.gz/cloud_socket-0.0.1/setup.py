from setuptools import setup, find_packages

# Requirements  for the package
with open('requirements.txt') as f:
    requirements = [
        line.strip() for line in
        f.read().splitlines()
        if line.strip() != '' and not line.strip().startswith('#')
    ]

# Read the long description from the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cloud-socket",
    version="0.0.1",
    author="Daniel Olson",
    author_email="daniel@orphos.cloud",
    description="Cloud Socket is a secure websocket application that uses AES-GCM encryption and is build on fastapi. This also allows you to have google cloud run server without cold starts as it always has an open connection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    metadata_version="2.3",  # Enforce an older version
    install_requires=requirements,
    # entry_points={
    #     'console_scripts': ['qq=query_search.cli:cli'],
    # },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    keywords="websocket, socket, encryption, secure",
)
