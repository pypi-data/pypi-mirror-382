# igem_registry_api

*A high-level Python interface for the new iGEM Registry REST API (2025 Beta)*

[![PyPI](https://img.shields.io/pypi/v/igem_registry_api.svg)](https://pypi.org/project/igem_registry_api/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-black.svg)](https://github.com/igem-munich/igem_registry_api)


## Introduction

The [**iGEM Registry of Standard Biological Parts**](https://registry.igem.org) is a global, community-driven repository of genetic components that originated in **2003** with the *International Genetically Engineered Machine (iGEM)* competition, a worldwide event where students design and build synthetic biological systems.

Over two decades of competition have led to a collection of **more than 75,000 registered biological parts**, forming one of the largest open genetic design repositories in existence.

In **August 2025**, the Registry underwent a [complete overhaul](https://registry.igem.org/about/2025-announcement). The new version introduced not only a modernized user interface, but also, for the first time, a comprehensive **REST API** for programmatic access.

However, the API's official [Swagger documentation](https://api.registry.igem.org/docs) remains **incomplete**, it provides endpoint listings but **no schemas, field definitions, or data types**. This makes auto-generated clients impossible and manual interaction cumbersome.

To address this gap, the **iGEM Munich 2025** team developed `igem_registry_api`: a **fully validated, Pythonic, and biologist-friendly** wrapper for the new Registry API. This package reconstructs the missing schemas from the Registry's public [backend source code](https://gitlab.igem.org/hq-tech/registry), providing a **complete, typed, and intuitive interface** for working with Registry data.


## Key features

- **Full Pydantic schema validation** \
All models are backed by strict type validation using [Pydantic v2](https://docs.pydantic.dev), ensuring consistency, type safety, and helpful error feedback.

- **Typed models for all Registry entities** \
Including `Part`, `Account`, `Organisation`, `Author`, `License`, `Annotation`, and more — each reflecting the real backend schema and relations between objects.

- **Transparent API communication** \
Built on top of [`requests`](https://docs.python-requests.org), with robust handling for authentication, headers, and pagination.

- **Adaptive rate-limit handling** \
Automatically detects Registry rate limits and throttles requests intelligently, preventing crashes during large data retrievals.

- **Streamlined endpoint mapping** \
Logical restructuring of endpoints for intuitive traversal between related objects.

- **Integrated logging and progress tracking** \
Rich, human-readable logging output and optional progress callbacks for long-running queries.

- **Extensible and modular**  \
The package is built around independent but interlinked Pydantic models,easy to extend, but consistent across modules.

- **Sophisticated downstream applications** \
While the official Registry currently lacks many analysis tools, this package enables advanced programmatic workflows, such as:
  - Running **local BLAST** searches on downloaded Registry sequences
  - Integrating Registry data with tools like **Geneious Prime** or other bioinformatics pipelines for local part analysis
  - Integrating with lab automation and electronic lab notebooks, such as **Benchling** or **eLabFTW** for streamlined part assembly and experimental use


## Installation

### From PyPI

```bash
pip install igem_registry_api
```

### From source

```bash
git clone https://github.com/igem-munich/igem_registry_api.git
cd igem_registry_api
uv sync
```


## Quick start

The package is designed for immediate usability with minimal setup. For example, to connect anonymously and list public parts:

```python
from igem_registry_api import Client, Part

client = Client()
client.connect()

parts = Part.fetch(client, limit=5)
for p in parts:
    print(p.name, p.uuid)
```

To authenticate with your iGEM account and access private data:

```python
client.sign_in("username", "password")
account = client.account()
print(account.parts())
```

For more comprehensive usage, including authors, annotations, and composition loading, see the example scripts below.


## Examples

A collection of runnable examples is provided under `examples/`. They demonstrate practical workflows using the Registry API client.
- `quickstart.py`: basic connection, authentication, and simple part retrieval.
- `users_orgs.py`: querying user accounts and their affiliated organisations.
- `part_retrieve.py`: fetching and inspecting specific parts by UUID or name with their sequences, annotations, and compatibilities.
- `part_metadata.py`: exploring part metadata, including part types, categories, and licenses.
- `registry_dump.py`: downloading large portions of the Registry with automatic pagination and rate-limit handling.
- `registry_blast.py`: running a local BLAST search against downloaded Registry sequences (a capability not provided by the official Registry itself).

Each script is self-contained and can be executed directly after installing dependencies.


## Development and contributions

This project currently provides full programmatic read interface to all public Registry resources with models including `Part`, `Account`, `Organisation`, `Type`, `Category`, `License`, and `Annotation`. Write operations (e.g., creating or updating parts) and support for `Collection` and `Documentation` models are planned for future releases.

### Local development

Contributions are very welcome. You can:
 - Report issues or suggest improvements on GitHub Issues
 - Fork the repository and open a pull request

To set up a local development environment:

```bash
git clone https://github.com/igem-munich/igem_registry_api.git
cd igem_registry_api
uv sync --extra dev
```

Run tests or examples with:
```bash
pytest
python examples/quickstart.py
```

### Roadmap

Planned additions include:
- Write (POST/PUT/PATCH/DELETE) support for Registry objects
- Collection and Documentation models
- Batch upload utilities and enhanced error reporting
- Richer integrations with analysis frameworks


## License

Released under the MIT License.

Developed by the iGEM Munich 2025 team as a contribution to the iGEM community. The package is designed for general use by all teams and researchers working with the iGEM Registry.