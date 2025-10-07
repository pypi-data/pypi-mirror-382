<img src="qoqo_Logo_vertical_color.png" alt="qoqo logo" width="300" />

# qoqo-iqm

IQM-backend for the qoqo/roqoqo quantum toolkit by [HQS Quantum Simulations](https://quantumsimulations.de).

The qoqo_iqm/roqoqo-iqm packages provide backends for qoqo/roqoqo that allow the users to run quantum circuits on the IQM web API testbed.
The testbed is  accessed via a web REST-API.
To run circuits or QuantumPrograms with this backend you need a valid access token. The access token can be set via the environment variable `IQM_TOKEN`.

This repository contains two components:

* The qoqo_iqm backend for the qoqo python interface to roqoqo
* The roqoqo-iqm backend for roqoqo directly

## qoqo_iqm

[![Documentation Status](https://img.shields.io/badge/docs-documentation-green)](https://hqsquantumsimulations.github.io/qoqo_iqm/)
[![GitHub Workflow Status](https://github.com/HQSquantumsimulations/qoqo_iqm/workflows/ci_tests/badge.svg)](https://github.com/HQSquantumsimulations/qoqo_iqm/actions)
[![PyPI](https://img.shields.io/pypi/v/qoqo_iqm)](https://pypi.org/project/qoqo_iqm/)
[![PyPI - Format](https://img.shields.io/pypi/format/qoqo_iqm)](https://pypi.org/project/qoqo_iqm/)


### Installation

We provide pre-built binaries for linux, macos and windows on x86_64 hardware and macos on arm64. Simply install the pre-built wheels with

```shell
pip install qoqo_iqm
```

## roqoqo-iqm

[![Crates.io](https://img.shields.io/crates/v/roqoq-iqm)](https://crates.io/crates/roqoqo-iqm)
[![GitHub Workflow Status](https://github.com/HQSquantumsimulations/qoqo_mock/workflows/ci_tests/badge.svg)](https://github.com/HQSquantumsimulations/qoqo_iqm/actions)
[![docs.rs](https://img.shields.io/docsrs/roqoqo-iqm)](https://docs.rs/roqoqo-iqm/)
![Crates.io](https://img.shields.io/crates/l/roqoqo-iqm)

IQM-Backend for the roqoqo quantum toolkit by [HQS Quantum Simulations](https://quantumsimulations.de).


## Contributing

We welcome contributions to the project. If you want to contribute code, please have a look at CONTRIBUTE.md for our code contribution guidelines.

## OpenSSL

Acknowledgments related to using OpenSSL for http requests:

"This product includes software developed by the OpenSSL Project
for use in the OpenSSL Toolkit (http://www.openssl.org/)."

This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com).  This product includes software written by Tim
Hudson (tjh@cryptsoft.com).

## General Notes

This project has been partially supported by [QExa](https://meetiqm.com/technology/qexa/).
