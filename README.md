> ## ⚠️ Deprecated (legacy make87 app-platform SDK)
>
> This SDK supported the legacy make87 "application SDK integration" workflow.
> make87 has pivoted to a CLI/agent-based device management workflow.
>
> **This package is unmaintained and will receive no further updates or fixes.**
> If you are still using it, pin your dependency and migrate off this package.
>
> Status: Deprecated • Maintenance: none

![make87 Banner Logo](https://make87-files.nyc3.digitaloceanspaces.com/assets/branding/logo/make87_ME_1d_cv_cropped.svg)
# make87 SDK for Python

## Overview

The make87 SDK for Python provides tools and libraries to interact with the make87 platform. This SDK is designed to be compatible with Python versions 3.9 to 3.12.

## Installation

To install the SDK, use pip:

```bash
pip install make87
```

### Dependencies

The SDK has the following dependencies:

- `protobuf==4.25.5`
- `eclipse-zenoh==1.2.1`
- `pydantic>=2.9.2,<3.0.0`

For optional storage support, you can install additional dependencies:

```bash
pip install make87[storage]
```

For development, you can install the development dependencies:
```bash
pip install make87[dev]
```

## Documentation
To build the documentation locally, navigate to the docs directory and install the required dependencies:

```bash
cd docs
pip install -r requirements.txt
```

Then, build the documentation using MkDocs:

```bash
mkdocs build
```

## Contributing

This repository is archived and unmaintained. Issues and pull requests are not accepted.
