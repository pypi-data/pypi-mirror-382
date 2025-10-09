# DASL Client Library

The DASL (Databricks Antimatter Security Lakehouse) Client Library is a Python SDK for interacting with DASL services.
This library provides an interface for interacting with DASL services, allowing you to manage
datasources, rules, workspace configurations, and more from Databricks notebooks.

## Features

* **Simple Authentication**: Automatic workspace detection in Databricks notebooks
* **Datasource Management**: Create, update, list, and delete datasources
* **Rule Management**: Define and manage security detection rules to identify threats
* **Workspace Configuration**: Update and retrieve DASL's workspace-level settings

## Installation

Install from PyPI:

```bash
pip install dasl-client
```

## Quick Start

### Databricks Notebook Environment (Recommended)

The DASL client works best in Databricks notebooks with automatic authentication:

```python
from dasl_client import Client

# Automatically detects Databricks context and authenticates
client = Client.for_workspace()
print("Connected to DASL!")

# List existing datasources
print("Existing datasources:")
for datasource in client.list_datasources():
    print(f"  - {datasource.metadata.name}")

# List detection rules
print("Existing detection rules:")
for rule in client.list_rules():
    print(f"  - {rule.metadata.name}")
```

### Creating a Datasource

```python
from dasl_client import DataSource, Schedule, BronzeSpec, SilverSpec

# Create a new datasource
datasource = Datasource(
    source="aws",
    source_type="cloudtrail",
    autoloader=Autoloader(
        enabled=True,
        schedule=Schedule(
            at_least_every="1h",
            enabled=True
        )
    ),
    bronze=BronzeSpec(
        bronze_table="security_logs_bronze",
        skip_bronze_loading=False
    ),
    silver=SilverSpec(
        # Configure silver layer here, see the API reference for more details
    ),
    gold=GoldSpec(
        # Configure gold layer here, see the API reference for more details
    )
)

# Create the datasource
created_datasource = client.create_datasource(datasource)
print(f"Created datasource: {created.metadata.name}")
```

### Creating a Detection Rule

```python
from dasl_client.types import Rule, Schedule

# Create a new detection rule to detect failed logins
rule = Rule(
    schedule=Schedule(
        at_least_every="2h",
        enabled=True,
    ),
    input=Rule.Input(
        stream=Rule.Input.Stream(
            tables=[
                Rule.Input.Stream.Table(name="http_activity"),
            ],
            filter="disposition = 'Blocked'",
            starting_timestamp=datetime(2025, 7, 8, 16, 47, 30),
        ),
    ),
    output=Rule.Output(
        summary="record was blocked",
    ),
)

try:
    created_rule = client.create_rule("Detect Blocked HTTP Activity", rule)
    print(f"Successfully created rule: {created_rule.metadata.name}")
except Exception as e:
    print(f"Error creating rule: {e}")
```

## Requirements

- Python 3.8+
- Access to a Databricks workspace with DASL enabled
- `databricks-sdk>=0.41.0`
- `pydantic>=2`

## Documentation

For complete DASL Client documentation, examples, and API reference:

- [DASL Client Documentation](https://antimatter-dasl-client.readthedocs-hosted.com/)
- [API Reference](https://antimatter-dasl-client.readthedocs-hosted.com/en/latest/api-reference/)
- [Quickstart Guide](https://antimatter-dasl-client.readthedocs-hosted.com/en/latest/quickstart.html)

## Support

- **Email**: support@antimatter.io
- **Documentation**: [DASL Documentation](https://docs.sl.antimatter.io)
