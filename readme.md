# Vertiv™ Geist™ IMD Configuration Script v0.1.0

# Overview
### This unofficial script interacts with the the Vertiv™ Geist™ IMD ([Interchangeable Monitoring Device](https://www.vertiv.com/globalassets/products/critical-power/power-distribution/vertiv-geist-rpdu-imd-data-sheet-en.pdf)) API for configuration and firmware upgrades. It is compatible with IMD-03x firmware versions 5 and 6. For API reference, see the [Geist™ API Specification](https://www.vertiv.com/4a5013/globalassets/products/critical-power/power-distribution/geist-api-specification-api-specifications-sl-70874.pdf).

## Table of Contents
- [Installation](#-installation)
- [Usage](#-usage)
- [Options](#-Options)
- [API](#-API)

![image](images/imd_script_demo.gif)

## Installation
Ensure you have [Python v3.12](https://www.python.org/downloads/) or later, [pip3](https://pypi.org/project/pip/), [pipenv](https://pipenv.pypa.io/en/latest/) and [Git](https://git-scm.com/downloads) installed.
```shell
# Clone the repo and cd into its directory:

    git clone https://github.com/techietristan/vg_imd_config.git
    cd vg_imd_config

# Install dependencies with pipenv.

    # Option 1: To install the dependencies globally, use pipenv install --system:
    > pipenv install --system
    ...
    Installing dependencies from Pipfile.lock (5169c0)...
    All dependencies are now up-to-date!
        # Run the script using Python.
        > python3 .

    # Option 2: To run the script in its own environment, use pipenv shell:
    > pipenv shell
    Launching subshell in virtual environment...
    ...
    (vg_imd_config) > pipenv install
        # After launching the pipenv shell, use python to run the script:
        (vg_imd_config) > python3 .
        # Alternately, to run the script without launching the pipenv shell, use pipenv run:
        > pipenv run pipenv install
        > pipenv run python3 .

# On first run, the script will create copes of the default config and prompts .json files. These copies can be edited to suit your needs. On subsequent runs, these files will determine the behavior of the script.
```

## Usage
```shell
# By default, the script will run in interactive mode:
    > python3 vg_imd_config/

    Welcome to the Vertiv Geist IMD Configuration Script!
# The script will read prompts from and editable .json file. Enter the configuration details for the IMD you're configuring:
    Please enter the rack row (e.g. '7'): 4
    ...
    Please enter the password (Press 'Enter' to use the default password): 
# When finished, you'll be prompted to push the configuration to the IMD:
    Configure the currently connected IMD with the following parameters?

        Username and Password: hacker, *******
        ...
        Rack Location: R04-02/B
# The script will push the configuration in the order specified in the .json file:
    ✔ Username and Password set successfully!
    ...
    ✔ Static IP removed successfully!

# When complete, you'll be prompted to configure the next IMD and the process will repeat:
    IMD configuration successful!
    Would you like to configure another IMD? (y or n): 

```

## Options
To see a list of options, run the script with the `--help` flag.
```shell
> python . --help
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
                        Don`t check the current IMD firmware version.
  --spinner SPINNER     Set the spinner to use during lengthy script operations (see https://github.com/manrajgrover/halo).
```

## API
This script is early in its development. The API for the .json configuration and prompts files is *not* stable. Please use with caution.