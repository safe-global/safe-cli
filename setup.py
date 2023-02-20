import setuptools

from safe_cli.version import version

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="safe_cli",
    version=version,
    author="Uxío Fuentefría",
    author_email="uxio@safe.global",
    description="Command Line Interface for Gnosis Safe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gnosis/safe-cli",
    download_url="https://github.com/gnosis/safe-cli/releases",
    license="MIT",
    test_suite="tests",
    install_requires=[
        "colorama>=0.4",
        "prompt_toolkit>=3",
        "pyfiglet>=0.8",
        "pygments>=2",
        "requests>=2",
        "safe-eth-py>=5.0.1",
        "tabulate>=0.8",
    ],
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "safe-cli=safe_cli.main:main",
            "safe-creator=safe_cli.safe_creator:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
