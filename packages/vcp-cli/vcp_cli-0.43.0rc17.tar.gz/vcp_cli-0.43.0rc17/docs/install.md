(installing)=
# Installing

To use the VCP CLI tool, you will need:

* Python version 3.10 or greater
* Access to a command-line terminal or shell on a MacOS or Linux systems.
* For the `benchmarks` commands, you will need to be running on an Intel/AMD64 architecture CPU with NVIDIA GPU, running Linux with NVIDIA drivers.
* For other commands (e.g. `data`) you will need a Virtual Cells Platform account ([register here](https://virtualcellmodels.cziscience.com/?register=true))

## From PyPi

The Virtual Cells Platform (VCP) CLI is published to [PyPi](https://pypi.org/project/vcp-cli/).

We recommend installing the tool into a fresh virtual environment, for example using [venv](https://docs.python.org/3/library/venv.html), to create an activate a virtual environment:

```bash
python -m venv vcp-cli
source vcp-cli/bin/activate
```

It can be installed with:

```bash
pip install vcp-cli
```

## Update Package

To update the package to the latest version, run:

```bash
pip install --upgrade vcp-cli
```
