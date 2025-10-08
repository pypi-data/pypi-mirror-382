<div align="center">
<img width="60px" src="https://pts-project.org/logos/colander-data-converter/colander-data-converter-logo.png">
<h1>Colander Data Converter</h1>
<p>
A set of helpers to manipulate Colander data.
</p>
<p>
<img src="https://img.shields.io/badge/License-GPL_v3-8A2BE2">
<img src="https://img.shields.io/pypi/v/colander-data-converter?&label=PyPi%20distribution&color=8A2BE2">
</p>
<p>
<a href="https://pts-project.org">Website</a> |
<a href="https://pts-project.org/colander-data-converter/">Documentation</a> |
<a href="https://github.com/PiRogueToolSuite/colander-data-converter">GitHub</a> |
<a href="https://discord.gg/qGX73GYNdp">Support</a>
</p>
<p>
<img src="https://github.com/PiRogueToolSuite/colander-data-converter/actions/workflows/build.yml/badge.svg">
<a href="https://codecov.io/gh/PiRogueToolSuite/colander-data-converter" >
<img src="https://codecov.io/gh/PiRogueToolSuite/colander-data-converter/graph/badge.svg?token=P1Y783DUDA"/>
</a>
</p>
</div>

> ⚠️ *This project is currently under active development and is not suitable for production use. Breaking changes may occur without notice. A stable release will be published to PyPI once development stabilizes.*

Colander Data Converter is part of the [PiRogue Tool Suite (PTS)](https://pts-project.org) ecosystem, created to assist investigators, researchers, and civil society organizations in performing mobile forensics and digital investigations.

`colander_data_converter` is a Python library that enables interoperability between cyber threat intelligence (CTI) platforms by converting structured threat data between different formats — notably **MISP**, **STIX 2.1**, and **Colander**. Colander data format is an opinionated data format focused on usability and interoperability.

It's designed for developers, CTI analysts, and investigators who need to normalize, migrate, or integrate threat data across systems that use different schemas.

![](https://github.com/PiRogueToolSuite/colander-data-converter/raw/main/docs/_static/img/conversions.png)

## Key features

- 🔄 Convert between **MISP**, **STIX 2.1**, and **Colander**
- 📦 Preserve relationships, metadata, and object references
- 🧩 Easily integrated into existing pipelines and CTI platforms
- ⚙️ CLI and programmatic usage
- 📖 Open-source and extensible

## Who is this for?

- **CTI developers** integrating systems or building bridges across tools
- **Threat analysts** converting incoming feeds for unified analysis
- **Security researchers** working with mixed-format CTI datasets
- **Organizations** using Colander for collaborative investigations

## Installation
`colander_data_converter` requires Python 3.12 or higher.

**Once released**, install with:
```
pip install colander_data_converter
```

## Usage examples
### Stix 2.1 to Colander

![](https://pts-project.org/colander-data-converter/_images/stix2_mermaid.png)

```python
import json
from colander_data_converter.converters.stix2.converter import Stix2Converter
from colander_data_converter.converters.stix2.models import Stix2Bundle

with open("path/to/stix2_bundle.json", "r") as f:
    raw = json.load(f)
stix2_bundle = Stix2Bundle.load(raw)
colander_feed = Stix2Converter.stix2_to_colander(stix2_bundle)
```

### Generate Graphviz DOT file

![](https://pts-project.org/colander-data-converter/_images/graphviz.png)

```python
import json

from colander_data_converter.base.models import ColanderFeed
from colander_data_converter.exporters.graphviz import GraphvizExporter

# Load the feed
with open("path/to/colander_feed.json", "r") as f:
    raw = json.load(f)
colander_feed = ColanderFeed.load(raw)

# Export the feed as a graph
exporter = GraphvizExporter(colander_feed)
with open("path/to/colander_feed.dot", "w") as f:
    exporter.export(f)
```

## Contributing

We welcome community contributions! You can:

* Report bugs or suggest improvements via [Issues](https://github.com/PiRogueToolSuite/colander-data-converter/issues)
* Submit pull requests for format support or enhancements on [GitHub](https://github.com/PiRogueToolSuite/colander-data-converter)
* Help document conversion edge cases or gaps
* Join our [Discord server](https://discord.gg/qGX73GYNdp)

### Development setup

1. Install Python 3.12 or higher.
2. Install [uv](https://docs.astral.sh/uv/).
3. Clone the project repository:

```
git clone https://github.com/PiRogueToolSuite/colander-data-converter
cd colander-data-converter
uv sync
```

Before submitting a PR, execute run the test suite and the pre-commit checks:
```
tox run -e fix,3.12,docs
```
