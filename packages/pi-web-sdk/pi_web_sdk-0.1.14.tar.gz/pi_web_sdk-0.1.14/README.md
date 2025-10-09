# PI Web API Python SDK

A modular Python SDK for interacting with the OSIsoft PI Web API. The codebase has been reorganised from a single monolithic module into a structured package that groups related controllers, configuration primitives, and the HTTP client.

## Project Description
pi_web_sdk delivers a consistently structured Python interface for AVEVA PI Web API deployments. It wraps the REST endpoints with typed controllers, rich client helpers, and practical defaults so you can query PI data, manage assets, and orchestrate analytics without hand-crafting HTTP calls. The package is organised for extensibility: add new controllers or override behaviours while keeping a cohesive developer experience.

## Features
- **Typed configuration** via `PIWebAPIConfig` and enums for authentication and WebID formats
- **Reusable HTTP client** `PIWebAPIClient` wrapper around `requests.Session` with centralised error handling
- **Domain-organized controllers** split by functionality (system, assets, data, streams, OMF, etc.) for easier navigation
- **Stream Updates** for incremental data retrieval without websockets (marker-based polling)
- **OMF support** with ORM-style API for creating types, containers, assets, and hierarchies
- **Comprehensive CRUD operations** for all major PI Web API endpoints
- **Event Frame helpers** - High-level convenience methods for complex event frame operations
- **Parsed responses** - Type-safe response wrappers with generic data classes
- **Advanced search** - AFSearch syntax support for querying elements and attributes
- **Real-time streaming** - WebSocket/SSE channel support for live data updates
- **Bulk operations** - Get/update multiple resources in single API calls
- **108 tests** - Comprehensive test coverage for all controllers
- **Backwards-compatible** `aveva_web_api.py` re-export for existing imports

## Installation
This project depends on `requests`. Install it with:

```bash
pip install requests
```

## Quick Start

### Basic Usage
```python
from pi_web_sdk import AuthMethod, PIWebAPIClient, PIWebAPIConfig

config = PIWebAPIConfig(
    base_url="https://your-pi-server/piwebapi",
    auth_method=AuthMethod.ANONYMOUS,
    verify_ssl=False,  # enable in production
)

client = PIWebAPIClient(config)
print(client.home.get())
```

### Working with Assets
```python
# List asset servers
servers = client.asset_server.list()
server_web_id = servers["Items"][0]["WebId"]

# Get databases
databases = client.asset_server.get_databases(server_web_id)
db_web_id = databases["Items"][0]["WebId"]

# Create an element
element = {
    "Name": "MyElement",
    "Description": "Test element",
    "TemplateName": "MyTemplate"
}
client.asset_database.create_element(db_web_id, element)
```

### Working with Streams
```python
# Get stream value
value = client.stream.get_value(stream_web_id)

# Get recorded data
recorded = client.stream.get_recorded(
    web_id=stream_web_id,
    start_time="*-7d",
    end_time="*",
    max_count=1000
)

# Get latest value
latest = client.stream.get_end(stream_web_id)

# Get value at specific time
value_at_time = client.stream.get_recorded_at_time(
    stream_web_id,
    "2024-01-01T12:00:00Z",
    retrieval_mode="AtOrBefore"
)

# Get values at multiple times
values = client.stream.get_recorded_at_times(
    stream_web_id,
    ["2024-01-01T00:00:00Z", "2024-01-01T12:00:00Z", "2024-01-02T00:00:00Z"]
)

# Get interpolated values
interpolated = client.stream.get_interpolated_at_times(
    stream_web_id,
    ["2024-01-01T06:00:00Z", "2024-01-01T18:00:00Z"]
)

# Open real-time streaming channel
channel = client.stream.get_channel(
    stream_web_id,
    include_initial_values=True,
    heartbeat_rate=30
)

# Update stream value
client.stream.update_value(
    web_id=stream_web_id,
    value={"Timestamp": "2024-01-01T00:00:00Z", "Value": 42.5}
)

# Bulk operations for multiple streams
latest_values = client.streamset.get_end([stream_id1, stream_id2, stream_id3])
```

### Stream Updates (Incremental Data Retrieval)
```python
import time

# Register for stream updates
registration = client.stream.register_update(stream_web_id)
marker = registration["LatestMarker"]

# Poll for incremental updates
while True:
    time.sleep(5)  # Wait between polls

    # Retrieve only new data since last marker
    updates = client.stream.retrieve_update(marker)

    for item in updates.get("Items", []):
        print(f"{item['Timestamp']}: {item['Value']}")

    # Update marker for next poll
    marker = updates["LatestMarker"]

# For multiple streams, use streamset
registration = client.streamset.register_updates([stream_id1, stream_id2, stream_id3])
marker = registration["LatestMarker"]

updates = client.streamset.retrieve_updates(marker)
for stream_update in updates.get("Items", []):
    stream_id = stream_update["WebId"]
    for item in stream_update.get("Items", []):
        print(f"Stream {stream_id}: {item['Timestamp']} = {item['Value']}")
```

See [examples/README_STREAM_UPDATES.md](examples/README_STREAM_UPDATES.md) for comprehensive Stream Updates documentation.

### OMF (OSIsoft Message Format) Support
```python
from pi_web_sdk.omf import OMFManager, create_temperature_sensor_type, create_single_asset

# Initialize OMF manager
omf_manager = OMFManager(client, data_server_web_id)

# Create a type definition
sensor_type = create_temperature_sensor_type()
omf_manager.create_type(sensor_type)

# Create a container
container = {"id": "sensor1", "typeId": "TempSensorType"}
omf_manager.create_container(container)

# Send data
data_point = {
    "timestamp": "2024-01-01T00:00:00Z",
    "temperature": 25.5
}
omf_manager.send_data("sensor1", data_point)
```

### OMF Hierarchies
```python
from pi_web_sdk.omf.hierarchy import create_industrial_hierarchy

# Create hierarchy from paths
hierarchy = create_industrial_hierarchy([
    "Plant/Area1/Line1",
    "Plant/Area1/Line2",
    "Plant/Area2/Line3"
])

# Deploy hierarchy
omf_manager.create_hierarchy_from_paths(hierarchy.get_all_paths())
```

### Event Frame Helpers
```python
# Create event frame with attributes in one operation
event = client.event_frame_helpers.create_event_frame_with_attributes(
    database_web_id=db_web_id,
    name="Batch Run 001",
    description="Production batch",
    start_time="2024-01-01T08:00:00Z",
    end_time="2024-01-01T16:00:00Z",
    attributes={
        "Temperature": 95.5,
        "Pressure": 1013.25,
        "Status": "Complete"
    }
)

# Create child event frame
child = client.event_frame_helpers.create_child_event_frame_with_attributes(
    parent_web_id=event["WebId"],
    name="Quality Check",
    description="QC inspection",
    start_time="2024-01-01T15:30:00Z",
    end_time="2024-01-01T15:45:00Z",
    attributes={"Result": "Pass", "Inspector": "John Doe"}
)

# Create complete hierarchy
hierarchy = client.event_frame_helpers.create_event_frame_hierarchy(
    database_web_id=db_web_id,
    root_name="Production Run",
    root_description="Full production cycle",
    start_time="2024-01-01T08:00:00Z",
    end_time="2024-01-01T18:00:00Z",
    root_attributes={"Batch": "B-2024-001"},
    children=[
        {
            "name": "Mixing",
            "start_time": "2024-01-01T08:00:00Z",
            "end_time": "2024-01-01T10:00:00Z",
            "attributes": {"Speed": 1200}
        },
        {
            "name": "Heating",
            "start_time": "2024-01-01T10:00:00Z",
            "end_time": "2024-01-01T14:00:00Z",
            "attributes": {"Target": 95.0}
        }
    ]
)

# Get event frame with all attribute values
event_data = client.event_frame_helpers.get_event_frame_with_attributes(
    event_web_id,
    include_values=True
)
```

See [docs/event_frame_helpers.md](docs/event_frame_helpers.md) for complete documentation.

### Parsed Responses (Type-Safe)
```python
# Get parsed response with type safety
server = client.data_server.get_parsed(web_id)
print(f"Server: {server.name}")
print(f"Version: {server.server_version}")
print(f"Connected: {server.is_connected}")

# List with type safety and iteration
servers = client.data_server.list_parsed()
for server in servers:
    print(f"{server.name}: {server.path}")

# Get points with type safety
points = client.data_server.get_points_parsed(server_web_id)
for point in points:
    print(f"{point.name} ({point.point_type}): {point.engineering_units}")
```

### Advanced Search (AFSearch Syntax)
```python
# Query elements by attributes
elements = client.element.get_elements_query(
    database_web_id,
    query="Name:='Pump*' Type:='Equipment'"
)

# Create persistent attribute search
search = client.element.create_search_by_attribute(
    database_web_id,
    query="Name:='Temperature' Type:='Float64'"
)
search_id = search["WebId"]

# Execute search later
results = client.element.execute_search_by_attribute(search_id)

# Bulk get multiple elements
elements = client.element.get_multiple(
    [web_id1, web_id2, web_id3],
    selected_fields="Name;Path;Description"
)
```

### Analysis Operations
```python
# Get analysis with security
analysis = client.analysis.get(analysis_web_id)

# Get security entries
entries = client.analysis.get_security_entries(analysis_web_id)

# Create security entry
entry = {
    "Name": "Operators",
    "SecurityIdentityWebId": identity_web_id,
    "AllowRights": ["Read", "Execute"]
}
client.analysis.create_security_entry(analysis_web_id, entry)

# Work with analysis templates
template = client.analysis_template.get_by_path("\\\\AnalysisTemplate\\MyTemplate")
client.analysis_template.update(template["WebId"], {"Description": "Updated"})

# Get analysis categories
categories = client.analysis.get_categories(analysis_web_id)
```

## Available Controllers
All controller instances are available as attributes on `PIWebAPIClient`:

### System & Configuration
- `client.home` - Home endpoint
- `client.system` - System information and status
- `client.configuration` - System configuration

### Asset Model
- `client.asset_server` - Asset servers
- `client.asset_database` - Asset databases
- `client.element` - Elements
- `client.element_category` - Element categories
- `client.element_template` - Element templates
- `client.attribute` - Attributes
- `client.attribute_category` - Attribute categories
- `client.attribute_template` - Attribute templates

### Data & Streams
- `client.data_server` - Data servers
- `client.point` - PI Points
- `client.stream` - Stream data operations (including Stream Updates)
- `client.streamset` - Batch stream operations (including Stream Set Updates)

### Analysis & Events
- `client.analysis` - PI Analyses
- `client.analysis_category` - Analysis categories
- `client.analysis_rule` - Analysis rules
- `client.analysis_rule_plugin` - Analysis rule plugins
- `client.analysis_template` - Analysis templates
- `client.event_frame` - Event frames
- `client.event_frame_helpers` - High-level event frame operations
- `client.table` - PI Tables
- `client.table_category` - Table categories

### OMF
- `client.omf` - OSIsoft Message Format endpoint

### Batch & Advanced
- `client.batch` - Batch operations
- `client.calculation` - Calculations
- `client.channel` - Channels

### Supporting Resources
- `client.enumeration_set` - Enumeration sets
- `client.enumeration_value` - Enumeration values
- `client.unit` - Units of measure
- `client.time_rule` - Time rules
- `client.security` - Security operations
- `client.notification` - Notification rules
- `client.metrics` - System metrics

## Package Layout
- `pi_web_sdk/config.py` - Enums and configuration dataclass
- `pi_web_sdk/exceptions.py` - Custom exception types
- `pi_web_sdk/client.py` - Session management and HTTP helpers
- `pi_web_sdk/controllers/` - Individual controller modules grouped by domain
  - `controllers/base.py` - Base controller with shared utilities
  - `controllers/system.py` - System and configuration controllers
  - `controllers/asset.py` - Asset servers, databases, elements, templates
  - `controllers/attribute.py` - Attributes, categories, templates
  - `controllers/data.py` - Data servers and points (with parsed methods)
  - `controllers/stream.py` - Stream and streamset operations (enhanced)
  - `controllers/analysis.py` - Analysis controllers (fully enhanced)
  - `controllers/event.py` - Event frame controller
  - `controllers/event_helpers.py` - High-level event frame helpers
  - `controllers/omf.py` - OMF controller and manager
  - Additional controllers for tables, enumerations, units, security, notifications, etc.
- `pi_web_sdk/models/` - Data models and response classes
  - `models/responses.py` - Generic ItemsResponse[T] and PIResponse[T]
  - `models/data.py` - DataServer and Point models
  - `models/stream.py` - Stream enums (BufferOption, UpdateOption)
  - `models/omf.py` - OMF data models
  - `models/attribute.py` - Attribute models
- `pi_web_sdk/omf/` - OMF support with ORM-style API
  - `omf/orm.py` - Core OMF classes (Type, Container, Asset, Data)
  - `omf/hierarchy.py` - Hierarchy builder utilities
- `docs/` - Comprehensive documentation
- `examples/` - Working code examples
- `tests/` - 108 tests covering all controllers
- `aveva_web_api.py` - Compatibility shim for existing imports

## Extending the SDK
Each controller inherits from `BaseController`, which exposes helper methods and the configured client session. Add new endpoint support by:

1. Create a new controller module under `pi_web_sdk/controllers/`
2. Register it in `pi_web_sdk/controllers/__init__.py`
3. Add it to `pi_web_sdk/client.py` in the `PIWebAPIClient.__init__` method

Example:
```python
from .base import BaseController

class MyController(BaseController):
    def get(self, web_id: str) -> Dict:
        return self.client.get(f"myresource/{web_id}")
```

## Testing
Run the test suite:

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_omf_endpoint.py -v

# Run with integration marker
pytest -m integration
```

## Deployment

### Quick Deployment

```bash
# Validate package
python deploy.py --check

# Deploy to TestPyPI (recommended first)
python deploy.py --test

# Deploy to PyPI
python deploy.py --prod
```

### Prerequisites
- PyPI and TestPyPI accounts
- API tokens configured in `~/.pypirc`
- Build tools: `pip install build twine`

See [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) for quick start guide or [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive instructions.

## Documentation & Examples
- [PI Web API Reference](https://docs.aveva.com/bundle/pi-web-api-reference/page/help/getting-started.html)
- [OMF Documentation](https://docs.aveva.com/)
- [Stream Updates Guide](examples/README_STREAM_UPDATES.md) - Comprehensive guide for incremental data retrieval
- [Stream Updates Examples](examples/stream_updates_example.py) - Working code examples
- [Event Frame Helpers Documentation](docs/event_frame_helpers.md) - High-level event frame operations
- [Parsed Responses Documentation](docs/parsed_responses.md) - Type-safe response wrappers
- [Controller Additions Summary](docs/CONTROLLER_ADDITIONS_SUMMARY.md) - Complete list of all enhancements
- See `examples/` directory for more usage examples

## Recent Additions

### Comprehensive Controller Enhancements (v2025.10)
Major enhancement to the SDK with 78 new methods and 108 tests covering the full PI Web API surface:

**Analysis Controllers** (46 methods)
- Full CRUD operations for analyses, templates, categories, rules, and plugins
- Security management (get, create, update, delete security entries)
- Category associations
- Analysis rule management

**Element Enhancements** (7 methods)
- `get_multiple()` - Bulk retrieval of elements
- `get_elements_query()` - AFSearch syntax support for powerful queries
- `create_search_by_attribute()` / `execute_search_by_attribute()` - Persistent searches
- `add_referenced_element()` / `remove_referenced_element()` - Reference management
- `get_notification_rules()` / `create_notification_rule()` - Notification support

**Stream Enhancements** (11 methods)
- `get_end()` - Latest recorded value
- `get_recorded_at_time()` / `get_recorded_at_times()` - Point-in-time retrieval
- `get_interpolated_at_times()` - Interpolated values at specific times
- `get_channel()` - Real-time WebSocket/SSE streaming channels
- All methods available for single streams (`StreamController`) and multiple streams (`StreamSetController`)

**Event Frame Helpers** (6 methods)
- `create_event_frame_with_attributes()` - Create event frame and attributes in one call
- `create_child_event_frame_with_attributes()` - Create child with attributes
- `create_event_frame_hierarchy()` - Build complete hierarchies
- `get_event_frame_with_attributes()` - Retrieve with all attribute values
- `update_event_frame_attributes()` - Bulk attribute updates
- `close_event_frame()` - Close with optional value capture

**Parsed Responses** (Type-safe data classes)
- Generic `ItemsResponse[T]` and `PIResponse[T]` wrappers
- Support for iteration, indexing, and len()
- Added `*_parsed()` methods to DataServer and Point controllers
- Automatic deserialization to typed objects

See [docs/CONTROLLER_ADDITIONS_SUMMARY.md](docs/CONTROLLER_ADDITIONS_SUMMARY.md) for complete details.

### Stream Updates (v2025.01)
Stream Updates provides an efficient way to retrieve incremental data updates without websockets. Key features:
- **Marker-based tracking** - Maintains position in data stream
- **Single or multiple streams** - Support for individual streams and stream sets
- **Metadata change detection** - Notifies when data is invalidated
- **Unit conversion** - Convert values during retrieval
- **Selected fields** - Filter response data

```python
# Register once
registration = client.stream.register_update(stream_web_id)
marker = registration["LatestMarker"]

# Poll repeatedly for new data only
while True:
    time.sleep(5)
    updates = client.stream.retrieve_update(marker)
    # Process updates["Items"]
    marker = updates["LatestMarker"]
```

**Requirements**: PI Web API 2019+ with Stream Updates feature enabled

See [examples/README_STREAM_UPDATES.md](examples/README_STREAM_UPDATES.md) for complete documentation.

## License
See LICENSE file for details.

