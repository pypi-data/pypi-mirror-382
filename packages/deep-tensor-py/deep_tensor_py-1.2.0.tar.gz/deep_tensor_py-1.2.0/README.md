<h1 align="center"> deep-tensor-py </h1>

<div align="center">

[![Unit tests](https://github.com/alexgdebeer/deep-tensor-py/actions/workflows/run_tests.yaml/badge.svg)](https://github.com/alexgdebeer/deep-tensor-py/actions/workflows/run_tests.yaml)
[![Docs build](https://github.com/DeepTransport/deep-tensor-py/actions/workflows/publish_docs.yaml/badge.svg)](https://github.com/DeepTransport/deep-tensor-py/actions/workflows/publish_docs.yaml)
[![PyPI version](https://badge.fury.io/py/deep-tensor-py.svg)](https://badge.fury.io/py/deep-tensor-py)

</div>

This package contains a [PyTorch](https://pytorch.org) implementation of the deep inverse Rosenblatt transport (DIRT) algorithm introduced by Cui and Dolgov [[1](#1)].

## Installation

To install the package, use pip:

```{python}
pip install deep-tensor-py
```

The package can then be imported using

```{python}
import deep_tensor as dt
```

## Examples and Documentation

Examples and documentation are available on the package [website](https://deeptransport.github.io/deep-tensor-py/).

## References

[<a id="1">1</a>] 
Cui, T and Dolgov, S (2022). 
*[Deep composition of tensor-trains using squared inverse Rosenblatt transports](https://doi.org/10.1007/s10208-021-09537-5).* 
Foundations of Computational Mathematics **22**, 1863–1922.
