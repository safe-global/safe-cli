import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="safe_cli",
    version="0.1.0",
    author="Uxío Fuentefría",
    author_email="uxio@gnosis.io",
    description="Command Line Interface for Gnosis Safe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gnosis/safe-cli",
    download_url="https://github.com/gnosis/safe-cli/releases",
    license="MIT",
    test_suite="tests",
    install_requires=["gnosis-py"],
    packages=["safe_cli"],
    package_data={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
