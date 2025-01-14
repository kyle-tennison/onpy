# OnPy

[![CI Tests](https://github.com/kyle-tennison/onpy/actions/workflows/validate.yml/badge.svg)](https://github.com/kyle-tennison/onpy/actions/workflows/validate.yml)
[![MIT License](https://img.shields.io/github/license/kyle-tennison/onpy?color=yellow)](https://opensource.org/license/mit)
[![PyPi Version](https://img.shields.io/pypi/v/onpy?color=blue)](https://pypi.org/project/onpy/)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat)](https://github.com/psf/black)

## Overview

**OnPy is an unofficial Python API for building 3D models in [Onshape](https://Onshape.com)**

In OnPy you can:

- Build 2D sketches
- Extrude to create 3D geometries
- Interface with other Onshape features

## Installation & Authentication

You can install OnPy with pip:

```
pip install onpy
```

The first time you run OnPy, you will need to load your [Onshape developer keys](https://dev-portal.Onshape.com/keys). OnPy will automatically prompt you the first time it runs. You can trigger this dialogue with:

```
$ python -c "from onpy import Client;Client()"
```

Then, you can provide your keys:

```
$ python -c "from onpy import Client;Client()"

OnPy needs your Onshape credentials.
navigate to https://dev-portal.Onshape.com/keys and generate a pair of access & secret keys. Paste them here when prompted:

secret key: ...
access key: ...
```

Alternatively, you can set your Onshape keys as environment variables

- `ONSHAPE_DEV_SECRET` - The developer secret key
- `ONSHAPE_DEV_ACCESS` - The developer "access" key

### What is OnPy for?

OnPy is a high level Python API for Onshape. It enables third-party apps to leverage the same features as the Onshape modeler from Python.

Onshape natively supports [FeatureScript](https://cad.Onshape.com/FsDoc/); an Onshape native scripting language used for defining Onshape features. FeatureScript is a vastly powerful tool—many of it's strengths are leveraged in this package. However, FeatureScript is created to define individual features; there is no way to parametrically generate a design with it.

Instead, OnPy interfaces with Onshape's APIs to create designs that function the same as ones generated in the web UI.

### Disclaimer

OnPy connects to the user's Onshape account using developer keys they provide, which are generated via Onshape's [developer portal](https://cad.Onshape.com/appstore/dev-portal). By generating and using these keys, you agree to [Onshape's Terms of Use](https://www.onshape.com/en/legal/terms-of-use).

When using OnPy, all API calls to Onshape are made on the user's behalf. As a user, you are solely responsible for adhering to Onshape's Terms of Use, and you accept full accountability for any actions taken through OnPy.

OnPy is provided "as is," without warranty of any kind, either express or implied. OnPy assumes no responsibility for any violations of Onshape's Terms of Use arising from its use. Furthermore, OnPy is not liable for any consequences, damages, or losses resulting from the user's misuse of the API or non-compliance with Onshape's Terms of Use.

By using OnPy, you agree to these terms and accept all associated risks and liabilities.


### Syntax Overview

The following is from [`examples/cylinder.py`](examples/cylinder.py) :

```python
import onpy

# we'll create a new document, then reference the default partstudio
document = onpy.create_document("Cylinder Example")
partstudio = document.get_partstudio()

# now, we'll define a sketch
sketch = partstudio.add_sketch(
    plane=partstudio.features.top_plane,  # we define the plane to draw on
    name="New Sketch",  # and we name the sketch
)

# in this new sketch, we'll draw a circle
sketch.add_circle(center=(0, 0), radius=0.5)  # the default units are inches

# next, we'll extrude the sketch. the syntax is similar
extrude = partstudio.add_extrude(
    faces=sketch,  # we'll extrude the entire sketch ...
    distance=1,  # ... by one inch
)
```

If we look in our browser, we'll see a new document aptly named "Cylinder Example."

![A screenshot of the code output](.github/media/readme_screenshot.png)

## User Guide

For a more in-depth guide on how to use OnPy, view the [user guide](/guide.md). This gives a detailed explanation on how to use all of OnPy's features.

## Contributing

OnPy is obviously in it's earliest stage. All contributors are gratefully welcomed.

This module is structured to be as idiomatic as possible, while also following some of Onshape's layout quirks. There is no strict rules for this repository, but it's a good idea to try to stick with the flow of other things.