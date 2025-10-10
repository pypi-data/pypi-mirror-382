### r2x-reeds
> R2X Core plugin for translating ReEDS power system models
>
> [![image](https://img.shields.io/pypi/v/r2x-reeds.svg)](https://pypi.python.org/pypi/r2x-reeds)
> [![image](https://img.shields.io/pypi/l/r2x-reeds.svg)](https://pypi.python.org/pypi/r2x-reeds)
> [![image](https://img.shields.io/pypi/pyversions/r2x-reeds.svg)](https://pypi.python.org/pypi/r2x-reeds)
> [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

R2X ReEDS is an [R2X Core](https://github.com/NREL/r2x-core) plugin for parsing [Regional Energy Deployment System (ReEDS)](https://github.com/NREL/ReEDS-2.0) power system model data. It provides a comprehensive parser for NREL's ReEDS model, enabling seamless data exchange with other power system modeling platforms through the R2X Core framework.

## Features

- Read ReEDS inputs and outputs from multiple file formats including CSV and HDF5
- Automatic component mapping for generators, regions, transmission lines, reserves, and emissions data
- Time series support for capacity factors, load profiles, and reserve requirements
- Pattern-based technology categorization to automatically handle different technology variants and naming conventions
- JSON-based configuration through defaults and file mapping specifications
- Built-in validation against actual data files to ensure data integrity

## Quick Start

```console
pip install r2x-reeds
```

```python
from r2x_reeds import ReEDSParser, ReEDSConfig, ReEDSGenerator
from r2x_core.store import DataStore

# Configure
config = ReEDSConfig(
    solve_year=2030,
    weather_year=2012,
    case_name="test_Pacific"
)

# Load data using the default file mapping
file_mapping = ReEDSConfig.get_file_mapping_path()
data_store = DataStore.from_json(
    file_mapping,
    folder="path/to/reeds/outputs"
)

# Parse
parser = ReEDSParser(config, data_store)
system = parser.build_system()

# Access components
generators = list(system.get_components(ReEDSGenerator))
print(f"Built system with {len(generators)} generators")
```

## Supported Components

- Solar generators including utility-scale photovoltaic, distributed photovoltaic, concentrating solar power, and photovoltaic with battery storage
- Wind generators for both onshore and offshore installations
- Thermal generation including coal, natural gas combined cycle and combustion turbine units, and nuclear power plants
- Hydroelectric facilities and energy storage systems
- Regional components modeled at the balancing authority level with transmission region hierarchies
- Transmission interfaces and lines with bidirectional capacity representation
- Reserve requirements by type including spinning reserves, regulation reserves, and flexibility reserves organized by region
- Demand profiles representing load by region over time
- Emission data including carbon dioxide and nitrogen oxide emission rates for each generator

## Documentation

- [Installation Guide](docs/source/install.md) - Installation instructions
- [Configuration Reference](docs/source/references/configuration.md) - Configuration options and defaults
- [API Reference](docs/source/references/api.md) - Complete API documentation
- [Parser Reference](docs/source/references/parser.md) - Parser implementation details
- [Models Reference](docs/source/references/models.md) - Component model documentation
- [R2X Core Documentation](https://github.com/NREL/r2x-core) - Core framework documentation
