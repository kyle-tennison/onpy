# OnPy

[![CI Tests](https://github.com/kyle-tennison/onpy/actions/workflows/validate.yml/badge.svg)](https://github.com/kyle-tennison/onpy/actions/workflows/validate.yml)
[![MIT License](https://img.shields.io/github/license/kyle-tennison/onpy?color=yellow)](https://opensource.org/license/mit)
[![PyPi Version](https://img.shields.io/pypi/v/onpy?color=blue)](https://pypi.org/project/onpy/)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat)](https://github.com/psf/black)

## Overview

**OnPy is an unofficial Python API for building 3D models in [Onshape](https://onshape.com).**

With OnPy, you can:

- Build 2D sketches  
- Extrude to create 3D geometries  
- Interface with other Onshape features  

## Installation & Authentication

Install OnPy using pip:

```bash
pip install onpy
```

The first time you run OnPy, you will need to load your [Onshape developer keys](https://dev-portal.onshape.com/keys). OnPy will automatically prompt you for these keys. You can trigger this dialogue manually with:

```bash
python -c "from onpy import Client; Client()"
```

You’ll then be prompted to provide your keys:

```plaintext
OnPy needs your Onshape credentials.  
Navigate to https://dev-portal.onshape.com/keys and generate a pair of access & secret keys. Paste them here when prompted:  

Secret key: ...  
Access key: ...  
```

Alternatively, you can set your Onshape keys as environment variables:

- `ONSHAPE_DEV_SECRET` - Your developer secret key  
- `ONSHAPE_DEV_ACCESS` - Your developer access key  

### What is OnPy for?

OnPy is a high-level Python API for Onshape. It enables third-party apps to use the same features as the Onshape modeler directly from Python.

Onshape natively supports [FeatureScript](https://cad.onshape.com/FsDoc/), a scripting language for defining Onshape features. FeatureScript is powerful, and many of its strengths are leveraged in this package. However, it is designed to define individual features and cannot parametrically generate entire designs.

OnPy bridges this gap by interfacing with Onshape's APIs to create designs equivalent to those made in the web UI.

### Disclaimer

OnPy connects to your Onshape account using developer keys that you provide, which are generated via Onshape's [developer portal](https://cad.onshape.com/appstore/dev-portal). By generating and using these keys, you agree to [Onshape's Terms of Use](https://www.onshape.com/en/legal/terms-of-use).

When using OnPy, all API calls to Onshape are made on your behalf. As a user, you are responsible for adhering to Onshape's Terms of Use and accept full accountability for any actions taken through OnPy.

OnPy is provided "as is," without warranty of any kind, either express or implied. It assumes no responsibility for any violations of Onshape's Terms of Use arising from its use. Additionally, OnPy is not liable for any consequences, damages, or losses resulting from misuse of the API or non-compliance with Onshape's Terms of Use.

By using OnPy, you agree to these terms and accept all associated risks and liabilities.

### Syntax Overview

The following example is from [`examples/cylinder.py`](examples/cylinder.py):

```python
import onpy

# Create a new document, then reference the default Part Studio
document = onpy.create_document("Cylinder Example")
partstudio = document.get_partstudio()

# Define a sketch
sketch = partstudio.add_sketch(
    plane=partstudio.features.top_plane,  # Define the plane to draw on
    name="New Sketch",  # Name the sketch
)

# Draw a circle in the sketch
sketch.add_circle(center=(0, 0), radius=0.5)  # Default units are inches

# Extrude the sketch
extrude = partstudio.add_extrude(
    faces=sketch,  # Extrude the entire sketch ...
    distance=1,  # ... by one inch
)
```

After running the above code, you’ll see a new document in your browser, aptly named "Cylinder Example."

![A screenshot of the code output](.github/media/readme_screenshot.png)

## User Guide

For a more in-depth guide on how to use OnPy, refer to the [user guide](/guide.md). It provides a detailed explanation of all of OnPy's features.

## Contributing

OnPy is still in its earliest stages, and all contributions are welcome.

This module is designed to be as idiomatic as possible while following some of Onshape's layout quirks. There are no strict rules for contributing, but it’s a good idea to align with the existing structure.