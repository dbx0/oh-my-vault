<p align="center">
  <img src="https://i.ibb.co/mvp9xXR/omv.png" />
</p>

<h2 align="center">Oh My Vault!</h2>

### OpenMediaVault exploiting framework.

Oh My Vault! is the ultimate framework created to exploit and automate pen testing on the [OpenMediaVault](https://www.openmediavault.org/) NAS solution.

[![Python Version](https://img.shields.io/badge/python-3.9+-FF8400)](https://www.python.org) 
[![License](https://img.shields.io/badge/license-GPLv3-FF8400.svg)](https://github.com/blacklanternsecurity/bbot/blob/dev/LICENSE)


## Features

- Find exposed OpenMediaVault instances on Shodan
- Bruteforce credentials
- Test for default credentials
- Read system details (logged)
- Enumerate system users (logged)
- Run remote code on multiple OMV instances (logged)
- Start reverse shell as `root` into the OMV server (logged)


## Installation and usage

### Installation ([pip](https://pypi.org/project/bbot/))
 
Installing OMV is as simple as cloning and running a Python project on any OS. It requires just a terminal and Python 3.9+. 

```bash
git clone https://github.com/dbx0/oh-my-vault
cd oh-my-vault/
pip install -r requirements.txt
```

### Usage

To get started right away, just run it with Python, and you'll be prompted with the options available.

```bash
python omv.py
```

The Oh My Vault right now comes just with the wizard mode, on which you are prompted to choose your options.

## Feedback

If you have any feedback, please reach out to me at X [@malwarebx0](https://x.com/malwarebx0)

## License

[GPL3.0](LICENSE)

