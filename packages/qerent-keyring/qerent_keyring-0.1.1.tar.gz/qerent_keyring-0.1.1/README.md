# Qerent Keyring

The `qerent-keyring` package provides authentication for consuming Python packages from Qerent Distribution.

The package is an extension to [keyring](https://pypi.org/project/keyring), which will automatically find and use it once installed.

[pip](https://pypi.org/project/pip) will use `keyring` to find credentials.

## Installation

To install this package, run the following `pip` command:

```
pip install qerent-keyring
```

## Usage
### Requirements

- `python` version >=3.9
- `qerent` CLI.
- `pip` version >=19.2

### Installing packages from Qerent Distribution

Once `qerent-keyring` is installed, to consume a package, use the following `pip` command, replacing **<package_name>** with the package you want to install:

```
pip install <package_name> --extra-index-url https://distribution.qerent.ai/python/pypi/simple
```

