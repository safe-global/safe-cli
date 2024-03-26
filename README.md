[![PyPI version](https://badge.fury.io/py/safe-cli.svg)](https://badge.fury.io/py/safe-cli)
[![Build Status](https://github.com/safe-global/safe-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/safe-global/safe-cli/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/safe-global/safe-cli/badge.svg?branch=main)](https://coveralls.io/github/safe-global/safe-cli?branch=main)
![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)
![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/safeglobal/safe-cli?label=Docker&sort=semver)](https://hub.docker.com/r/safeglobal/safe-cli)

# Safe CLI

Safe CLI is a command-line utility for Safe contracts. You can use it to manage your Safe account from the command line.

It does not rely on Safe{Core} API and can also be used in networks where Safe services are unavailable. Learn more through the [documentation](https://docs.safe.global/advanced/cli-overview).

## Using Docker

**Prerequisite:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Once Docker is installed on your system, run the following command to create new Safe accounts:

```bash
docker run -it safeglobal/safe-cli safe-creator
```

You can also run the following command to run the Safe CLI with an existing Safe:
```bash
docker run -it safeglobal/safe-cli safe-cli <checksummed_safe_address> <ethereum_node_url>
```

## Using Python PIP

**Prerequisite:** [Python](https://www.python.org/downloads/) >= 3.9 (Python 3.12 is recommended).

Once Python is installed on your system, run the following command to install Safe CLI:
```bash
pip3 install -U safe-cli
```

## Usage

```bash
safe-cli [-h] [--history] [--get-safes-from-owner] address node_url

positional arguments:
  address                The address of the Safe, or an owner address if --get-safes-from-owner is specified.
  node_url               Ethereum node url

options:
  -h, --help             Show this help message and exit
  --history              Enable history. By default it's disabled due to security reasons
  --get-safes-from-owner Indicates that address is an owner (Safe Transaction Service is required for this feature)
```


## Safe{Core} API/Protocol

- [Safe Infrastructure](https://github.com/safe-global/safe-infrastructure)
- [Safe Transaction Service](https://github.com/safe-global/safe-transaction-service)
- [Safe Smart Account](https://github.com/safe-global/safe-smart-account)
- [Safe Smart Account deployment info and addreses](https://github.com/safe-global/safe-deployments/tree/main/src/assets)

## Setting up for developing

If you miss something and want to send us a PR:

```bash
git clone https://github.com/safe-global/safe-cli.git
cd safe-cli
stat venv 2>/dev/null || python3 -m venv venv
source venv/bin/activate && pip install -r requirements-dev.txt
pre-commit install -f
```

## Contributors

- [Pedro Arias Ruiz](https://github.com/AsiganTheSunk)
- [Uxío Fuentefría](https://github.com/uxio0)
- [Moisés Fernández](https://github.com/moisses89)
