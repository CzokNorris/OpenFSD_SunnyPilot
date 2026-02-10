# Getting Started with FlexRay Panda Experiments

This guide will help you get started with the FlexRay experimental support in OpenFSD_SunnyPilot.

## What is FlexRay?

FlexRay is an automotive network communication protocol designed for:
- **High-speed communication** up to 10 Mbit/s
- **Deterministic timing** with time-triggered scheduling
- **Fault tolerance** via redundant dual-channel design
- **Safety-critical systems** in modern vehicles

It's commonly used in luxury vehicles from Audi, BMW, Mercedes-Benz, and others.

## Quick Start

### 1. Verify Installation

```bash
# Clone the repository
git clone https://github.com/CzokNorris/OpenFSD_SunnyPilot.git
cd OpenFSD_SunnyPilot

# Verify Python is available
python3 --version
```

### 2. Run the Test Suite

```bash
# Run all tests
python3 tests/test_flexray.py

# You should see:
# SUCCESS: All tests passed!
```

### 3. Run Your First Example

```bash
# Run the basic FlexRay example
python3 examples/basic_flexray.py
```

This will:
- Configure a FlexRay bus
- Start communication
- Send test messages
- Display statistics

### 4. Try the Simulator

The built-in simulator allows testing without hardware:

```python
from flexray import FlexRayBusConfig
from flexray.interface import FlexRaySimulator, FlexRayMessage

# Create simulator
config = FlexRayBusConfig()
sim = FlexRaySimulator(config)
sim.start()

# Send a message
msg = FlexRayMessage(
    slot_id=10,
    cycle_count=0,
    channel=1,
    payload=b'\x01\x02\x03\x04'
)
sim.send_message(msg)

# Check messages
print(f"Sent {len(sim.get_messages())} messages")
```

## Examples Overview

### Basic Example
**File**: `examples/basic_flexray.py`
- Simple FlexRay communication
- Single message transmission
- Basic configuration

### Advanced Example
**File**: `examples/advanced_flexray.py`
- Multi-node simulation
- Cycle-based scheduling
- Message callbacks
- Statistics gathering

### Logging Example
**File**: `examples/logging_example.py`
- Data logging to CSV
- Signal parsing
- Hex dump formatting
- Data analysis

## Configuration

### Bus Configuration

```python
from flexray import FlexRayBusConfig

config = FlexRayBusConfig()
config.baudrate = 10_000_000       # 10 Mbit/s
config.static_slots = 64           # Number of static slots
config.dynamic_slots = 128         # Number of dynamic slots
config.cycle_duration = 5000       # 5ms cycle
config.channel = 0x03              # Both channels (A+B)
```

### Message Creation

```python
from flexray.interface import FlexRayMessage
from flexray import FlexRayFrame

message = FlexRayMessage(
    slot_id=10,                        # Slot ID (1-2047)
    cycle_count=0,                     # Cycle counter (0-63)
    channel=FlexRayFrame.CHANNEL_A,    # Channel A, B, or both
    payload=b'\x01\x02\x03\x04'       # Up to 254 bytes
)
```

## Working with Signals

### Define Signal Layout

```python
from lib.flexray_utils import signals_to_bytes, bytes_to_signals

# Define how signals are packed in payload
signal_map = {
    'vehicle_speed': (0, 2, '>H'),     # Bytes 0-1: speed in km/h
    'steering_angle': (2, 2, '>h'),    # Bytes 2-3: steering in degrees
    'throttle_pos': (4, 1, 'B'),       # Byte 4: throttle 0-100%
    'brake_pressure': (5, 1, 'B'),     # Byte 5: brake pressure
}

# Pack signals into payload
signals = {
    'vehicle_speed': 60,
    'steering_angle': -10,
    'throttle_pos': 50,
    'brake_pressure': 0
}
payload = signals_to_bytes(signals, signal_map, 8)

# Unpack signals from payload
parsed = bytes_to_signals(payload, signal_map)
print(parsed['vehicle_speed'])  # 60
```

## Hardware Support

⚠️ **Important**: Standard Panda devices do NOT support FlexRay natively.

For actual FlexRay communication, you need:

1. **Custom Hardware**
   - Modified Panda with FlexRay transceiver
   - FlexRay controller (e.g., NXP TJA1080)
   - Appropriate termination resistors (80-120Ω)

2. **Modified Firmware**
   - Custom Panda firmware with FlexRay support
   - Low-level driver implementation

3. **Test Setup**
   - FlexRay-enabled vehicle or test bench
   - Proper wiring harness
   - Protocol analyzer (recommended)

## Development Workflow

### 1. Design Phase
- Define message schedule
- Design signal layouts
- Plan slot allocation

### 2. Simulation Phase
- Test with simulator
- Validate timing
- Verify message flow

### 3. Hardware Phase
- Deploy to custom Panda
- Test with real vehicle
- Analyze bus behavior

## Troubleshooting

### Issue: Tests fail
**Solution**: Check Python version (3.7+)
```bash
python3 --version
```

### Issue: Import errors
**Solution**: Run from repository root
```bash
cd OpenFSD_SunnyPilot
python3 examples/basic_flexray.py
```

### Issue: Timing violations
**Solution**: Validate configuration
```python
from lib.flexray_utils import validate_cycle_timing
issues = validate_cycle_timing(config)
print(issues)
```

## Best Practices

1. **Start with Simulator**: Always test with simulator before hardware
2. **Validate Timing**: Check cycle timing before deployment
3. **Log Data**: Use logging utilities for debugging
4. **Handle Errors**: Implement proper error handling
5. **Safety First**: Never test on public roads

## Next Steps

1. **Read Documentation**: See `docs/FLEXRAY.md` for detailed info
2. **Study Examples**: Run and modify example scripts
3. **Experiment**: Try different configurations
4. **Contribute**: Share improvements and findings

## Resources

- [FlexRay Specification](https://svn.ipd.kit.edu/nlrp/public/FlexRay/)
- [comma.ai Panda](https://github.com/commaai/panda)
- [Vector FlexRay Documentation](https://www.vector.com/int/en/products/products-a-z/protocols/flexray/)

## Support

For questions or issues:
1. Check existing documentation
2. Review example code
3. Open an issue on GitHub

---

**Remember**: This is experimental software. Use responsibly and safely!
