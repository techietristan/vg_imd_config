# Vertiv™ Geist™ IMD Configuration Script v0.1.0

![language](https://img.shields.io/badge/language-Python-239120)
![OS](https://img.shields.io/badge/OS-linux%2C%20windows%2C%20macOS-0078D4)
## Overview
### This unofficial script interacts with the the Vertiv™ Geist™ IMD ([Interchangeable Monitoring Device](https://www.vertiv.com/globalassets/products/critical-power/power-distribution/vertiv-geist-rpdu-imd-data-sheet-en.pdf)) API for configuration and firmware upgrades. It is compatible with IMD-03x firmware versions 5 and 6. For API reference, see the [Geist™ API Specification](https://www.vertiv.com/4a5013/globalassets/products/critical-power/power-distribution/geist-api-specification-api-specifications-sl-70874.pdf).

![image](images/imd_script_demo.gif)


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Dependencies](#dependencies)
- [Updates](#updates)
- [API](#api)


## Installation <a name='installation'></a>

Ensure you have **Python** v3.12 or later, **pip3**, **pipenv** and **Git** installed. See the [Dependencies](#dependencies) section for OS-specific instructions.
### Clone the repo and cd into its directory:

    > git clone https://github.com/techietristan/vg_imd_config.git
    > cd vg_imd_config

### Install dependencies with pipenv:
#### Option 1: 
#### To run the script in its own environment, use pipenv shell:
    > pipenv shell
    Launching subshell in virtual environment...
    ...
#### Install dependencies:
    (vg_imd_config) > pipenv install
#### From the pipenv shell, use python to run the script:
    (vg_imd_config) > python3 .
---

#### Option 2: 
#### To run the script without launching the pipenv shell, use pipenv run:
    > pipenv run pipenv install
    > pipenv run python3 .
---

#### Option 3: 
#### To install the dependencies globally, use pipenv install --system:
    > pipenv install --system
    ...
    Installing dependencies from Pipfile.lock (5169c0)...
    All dependencies are now up-to-date!
#### Run the script using Python.
    > python3 .
---

## First Run

#### On first run, the script will prompt you to create copies of the default config and prompts .json files:

    Welcome to the Vertiv Geist IMD Configuration Script!

    No config files found. Do you want to make a copy of the default config file 'default_config.json'? ('y' or 'n'): y
    Copied 'default_config.json' to 'config.json'.
    No prompts files found. Do you want to make a copy of the default prompts file 'default_prompts.json'? ('y' or 'n'): y
    Copied 'default_prompts.json' to 'prompts.json'.

#### These copied files can be edited to suit your needs. On subsequent runs, they will determine the behavior of the script.The script will prompt you to set default values for the prompts file:

    Do you want to set defaults for 'prompts.json'? y
    Encrypted defaults found in 'prompts.json'. Please set a passphrase for encrypting and decrypting these values.
    Please enter the encryption passphrase:
    ...
    Please enter the default password again: 
    Defaults written to 'prompts.json'!

#### Once these values have been saved, setup is complete and the script will proceed to prompt you for the unique values for the next IMD to be configured.



## Usage <a name='usage'></a>


#### Ensure that you have a static IP set for the ethernet port you're using to connect to the IMD. This IP should be in the same subnet as the IMD (192.168.123.123 is the default IMD IP address). Select an IP address in the same subnet (192.168.123.0/24), for example, 192.168.123.100.


#### By default, the script will run in interactive mode:
    > python3 vg_imd_config/

    Welcome to the Vertiv Geist IMD Configuration Script!
#### The script will read prompts from an editable .json file. 
#### Enter the configuration details for the IMD you're configuring:
    Please enter the rack row (e.g. '7'): 4
    ...
    Please enter the password (Press 'Enter' to use the default password): 
#### When finished, you'll be prompted to push the configuration to the IMD:
    Configure the currently connected IMD with the following parameters?

        Username and Password: hacker, *******
        ...
        Rack Location: R04-02/B
#### The script will push the configuration in the order specified in the 'api_call_sequence' section of the prompts .json file:
    ✔ Username and Password set successfully!
    ...
    ✔ Static IP removed successfully!

#### When complete, you'll be prompted to configure the next IMD and the process will repeat:
    IMD configuration successful!
    Would you like to configure another IMD? (y or n): 

#### By default, the script will check the current IMD firmware and compare it against the target version listed in the config file. If these versions differ, you'll be asked whether you want to perform a firmware upgrade. The script will automatically download the firmware listed in the config file and store it in the 'firmware' directory. It will then be available for subsequent firmware updates.
#### To perform a standalone firmware update, run the script with the -u or --upgrade flags:
    > python3 vg_imd_config/ -u
    # or
    > python3 vg_imd_config/ --upgrade
#### To skip the firmware version check, run the script with the --skip_firmware_check flag:
    > python3 vg_imd_config/ --skip_firmware_check

## Options <a name='options'></a>

#### To see a list of options, run the script with the `--help` flag.
    (vg_imd_config) > python3 . --help
    usage: Vertiv™ Geist™ IMD Configuration Script [-h] [-a IMD_IP_ADDRESS] [-c CONFIG_FILE] [-f] [-p] [-r] [-u] [--prompts_file PROMPTS_FILE] [--reset_script] [--skip_firmware_check] [--spinner SPINNER]

    Unofficial script for configuring and upgrading Vertiv™ Geist™ IMDs

    options:
    -h, --help            show this help message and exit
    -a IMD_IP_ADDRESS, --imd_ip_address IMD_IP_ADDRESS
                            Specify the IP address of the IMD to be configured.
    -c CONFIG_FILE, --config_file CONFIG_FILE
                            Specify the configuration file to use.
    -f, --get_firmware_version
                            Get the firmware version of the currently connected IMD.
    -p, --set_password    Set the username and password for the currently connected IMD.
    -r, --reset_imd       Reset the currently connected IMD to factory defaults.
    -u, --upgrade         Upgrade the firmware of the currently connected IMD.
    --prompts_file PROMPTS_FILE
                            Specify the interactive prompts file to use.
    --reset_script        Remove all customized config and prompts files leaving only the default templates for these files.
    --skip_firmware_check
                            Don't check the current IMD firmware version.
    --spinner SPINNER     Set the spinner to use during lengthy script operations (see https://github.com/sindresorhus/cli-spinners).

## Dependencies <a name='dependencies'></a>
Ensure you have [Python v3.12](https://www.python.org/downloads/) or later, [pip3](https://pypi.org/project/pip/), [pipenv](https://pipenv.pypa.io/en/latest/) and [Git](https://git-scm.com/downloads) installed:
### Windows
Confirm that you have Python v.3.12 or later installed:

    > python3 --version
    Python 3.12.7

If not, download it from the the official [Python Releases for Windows](https://www.python.org/downloads/windows/) page or install it using winget:

    winget install -e --id Python.Python.3.0

Confirm that you have pip3 installed:

    > pip3 --version
    pip 24.2 from /usr/lib/python3.12/site-packages/pip (python 3.12)

Use pip to install pipenv
    
    > pip3 install pipenv

Confirm that you have Git installed:

    > git --version
    git version 2.47.0

If not, download it from the the official [Git Download for Windows](https://git-scm.com/downloads/win/) page or install it using winget:

    winget install -e --id Git.Git

---
### macOS
From the terminal, install Homebrew using the following command:

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Add the following line to the bottom of your `~/.profile` file:

    export PATH="/usr/local/opt/python/libexec/bin:$PATH"

Install Python, pipenv, and Git using Homebrew:

    brew install python pipenv git

---
### Linux

#### Debian, Ubuntu, Linux Mint
    sudo apt install -y python3 pipenv git

#### CentOS, Fedora, RHEL
    sudo yum install -y python3 pipenv git

#### Arch, Manjaro
    sudo pacman -S python3 python-pipenv git

## Updates <a name='updates'></a>
To update the script, cd into its directory pull the latest commit from the main branch:

    cd vg_imd_config
    git pull origin main

## API <a name='api'></a>

This script is early in its development. The API for the .json configuration and prompts files is *not* stable. Please use with caution.