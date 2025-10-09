# zea <img src="https://raw.githubusercontent.com/tue-bmd/zea/main/docs/_static/zea-logo.png" width="120" height="120" align="right" alt="zea Logo" />


[![PyPI version](https://img.shields.io/pypi/v/zea)](https://pypi.org/project/zea/)
[![Continuous integration](https://github.com/tue-bmd/zea/actions/workflows/tests.yaml/badge.svg)](https://github.com/tue-bmd/zea/actions/workflows/tests.yaml)
[![Documentation Status](https://readthedocs.org/projects/zea/badge/?version=latest)](https://zea.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/tue-bmd/zea)](https://github.com/tue-bmd/zea/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/tue-bmd/zea/branch/main/graph/badge.svg)](https://codecov.io/gh/tue-bmd/zea)
[![status](https://joss.theoj.org/papers/fa923917ca41761fe0623ca6c350017d/status.svg)](https://joss.theoj.org/papers/fa923917ca41761fe0623ca6c350017d)
[![GitHub stars](https://img.shields.io/github/stars/tue-bmd/zea?style=social)](https://github.com/tue-bmd/zea/stargazers)

Welcome to the `zea` package: *A Toolbox for Cognitive Ultrasound Imaging.*

- 📚 Full documentation: [zea.readthedocs.io](https://zea.readthedocs.io)
- 🔬 Try hands-on examples (with Colab): [Examples & Tutorials](https://zea.readthedocs.io/en/latest/examples.html)
- ⚙️ Installation guide: [Installation](https://zea.readthedocs.io/en/latest/installation.html)

`zea` is a Python library that offers ultrasound signal processing, image reconstruction, and deep learning. Currently, `zea` offers:

- A flexible ultrasound signal processing and image reconstruction pipeline written in your favorite deep learning framework.
- A complete set of data acquisition loading tools for ultrasound data and acquisition parameters, designed for deep learning workflows.
- A collection of pretrained models for ultrasound image and signal processing.
- **Multi-Backend Support via [Keras3](https://keras.io/keras_3/):** You can use [PyTorch](https://github.com/pytorch/pytorch), [TensorFlow](https://github.com/tensorflow/tensorflow), or [JAX](https://github.com/google/jax).

> [!WARNING]
> **Beta!**
> This package is highly experimental and under active development. It is mainly used to support [our research](https://www.tue.nl/en/research/research-groups/signal-processing-systems/biomedical-diagnostics-lab) and as a basis for our publications. That being said, we are happy to share it with the ultrasound community and hope it will be useful for your research as well.

> [!NOTE]
> 📖 Please cite `zea` in your publications if it helps your research. You can find citation info [here](https://zea.readthedocs.io/en/latest/getting-started.html#citation).
