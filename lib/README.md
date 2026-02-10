# FlexRay Library Utilities

This directory contains utility functions and helper classes for working with FlexRay data.

## Overview

The `flexray_utils.py` module provides:

- **Signal Processing**: Pack and unpack signals from FlexRay payloads
- **Data Logging**: Log FlexRay messages to CSV files
- **Validation**: Validate FlexRay configurations
- **Formatting**: Format payloads for display and debugging
- **Bus Analysis**: Calculate bus utilization and timing

## Key Functions

### Signal Processing

```python
from lib.flexray_utils import bytes_to_signals, signals_to_bytes

# Define signal layout
signal_map = {
    'speed': (0, 2, '>H'),      # Byte 0-1: unsigned 16-bit big-endian
    'steering': (2, 2, '>h'),   # Byte 2-3: signed 16-bit big-endian
    'brake': (4, 1, 'B'),       # Byte 4: unsigned 8-bit
}

# Pack signals
signals = {'speed': 50, 'steering': -10, 'brake': 1}
payload = signals_to_bytes(signals, signal_map, 8)

# Unpack signals
parsed = bytes_to_signals(payload, signal_map)
print(parsed)  # {'speed': 50, 'steering': -10, 'brake': 1}
```

### Data Logging

```python
from lib.flexray_utils import FlexRayLogger

# Create logger
logger = FlexRayLogger('flexray.csv')

# Log messages
logger.log_message(slot_id=10, cycle=0, channel=1, 
                  payload=b'\x01\x02\x03\x04', timestamp=time.time())

# Save to file
logger.save()

# Get statistics
stats = logger.get_statistics()
print(f"Logged {stats['total_messages']} messages")
```

### Configuration Validation

```python
from lib.flexray_utils import validate_cycle_timing
from flexray import FlexRayBusConfig

config = FlexRayBusConfig()
issues = validate_cycle_timing(config)

if issues:
    print("Configuration issues:")
    for issue in issues:
        print(f"  - {issue}")
```

### Hex Formatting

```python
from lib.flexray_utils import format_payload_hex

payload = b'\x01\x02\x03\x04\x05\x06\x07\x08'
print(format_payload_hex(payload))
# Output:
# 0000  01 02 03 04 05 06 07 08  ........
```

## Examples

See `examples/logging_example.py` for a complete demonstration of using these utilities.

## Signal Map Format

Signal maps use the format: `(start_byte, length, struct_format)`

Common struct formats:
- `'B'`: unsigned 8-bit (0-255)
- `'b'`: signed 8-bit (-128 to 127)
- `'>H'`: big-endian unsigned 16-bit
- `'>h'`: big-endian signed 16-bit
- `'>I'`: big-endian unsigned 32-bit
- `'>i'`: big-endian signed 32-bit
- `'<H'`: little-endian unsigned 16-bit

For more formats, see Python's `struct` module documentation.
