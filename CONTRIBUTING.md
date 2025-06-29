# Contributing

# Setup

## Manual Setup Requirements

You must have the following installed to proceed with contributing to this project. 

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
  - You'll know you did it right if you can run `git --version` and you see a response like `git version x.x.x`
- [python](https://www.python.org/downloads/)
  - You'll know you did it right if you can run `python --version` and you see a response like `Python x.x.x`
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
  - You'll know you did it right if you can run `uv --version` and you see a response like `uv 0.4.7 (a178051e8 2024-09-07)`
- Linux and/or MacOS
  - This project is not tested on Windows, so it is recommended to use a Linux or MacOS machine, or use a tool like [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) for windows users.
- [anvil](https://book.getfoundry.sh/reference/anvil/)
  - You'll know you did it right if you can run `anvil --version` and you see a response like `anvil 0.2.0 (b1f4684 2024-05-24T00:20:06.635557000Z)`
- [just](https://github.com/casey/just)
  - You'll know you did it right if you can run `just --version` and you see a response like `just 1.35.0`

## Dev Container Setup Requirements

- [Docker](https://www.docker.com/)
  - You'll know you did it right if you can run `docker --version` and you see a response like `Docker version x.x.x, build xxxxxxx`
- [VSCode](https://code.visualstudio.com/)

# Local Development 

Follow the steps to clone the repo for you to make changes to this project.

1. Clone the repo

```bash
git clone https://github.com/safe-global/safe-cli
cd safe-cli
```

2. Sync dependencies

*This repo uses uv to manage python dependencies and version. So you don't have to deal with virtual environments (much)*

```bash
uv sync --all-extras
```

3. Create a new branch

```bash
git checkout -b <branch_name>
```

And start making your changes! Once you're done, you can commit your changes and push them to your forked repo.

```bash
git add .
git commit -m 'your commit message'
git push <your_forked_github>
```
