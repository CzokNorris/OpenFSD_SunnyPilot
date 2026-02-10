# FlexRay Panda Experiments

This repository contains experimental support for FlexRay communication protocol with Panda devices. FlexRay is a high-speed, deterministic automotive communication protocol used in modern luxury vehicles (Audi, BMW, Mercedes-Benz, etc.).

## Overview

FlexRay is an automotive network communication protocol that provides:
- High-speed communication (up to 10 Mbit/s)
- Deterministic behavior with time-triggered communication
- Redundancy via dual-channel configuration
- Fault-tolerant design for safety-critical applications

This experimental implementation aims to add FlexRay support to the Panda ecosystem for research and development purposes.

## Features

- **FlexRay Protocol Implementation**: Complete protocol definitions and constants
- **Panda Interface**: High-level API for FlexRay communication
- **Simulator**: Software simulator for testing without hardware
- **Examples**: Sample code demonstrating FlexRay usage
- **Configuration**: Flexible bus configuration options

## Project Structure

```
.
├── flexray/              # FlexRay protocol implementation
│   ├── __init__.py      # Package initialization
│   ├── protocol.py      # Protocol definitions and constants
│   └── interface.py     # Panda interface and simulator
├── examples/            # Example scripts
│   └── basic_flexray.py # Basic usage example
├── docs/                # Documentation
│   └── FLEXRAY.md       # FlexRay protocol documentation
├── tests/               # Test suite
└── README.md           # This file
```

## Requirements

**Hardware** (for actual FlexRay communication):
- Custom Panda device with FlexRay transceiver
- FlexRay-enabled vehicle or test bench
- Appropriate FlexRay wiring harness

**Software**:
- Python 3.7 or higher
- No additional dependencies for basic functionality

## Installation

Clone this repository:

```bash
git clone https://github.com/CzokNorris/OpenFSD_SunnyPilot.git
cd OpenFSD_SunnyPilot
```

## Quick Start

### Using the Simulator

For testing without hardware, use the built-in simulator:

```python
from flexray import FlexRayBusConfig
from flexray.interface import FlexRaySimulator, FlexRayMessage

# Create and configure simulator
config = FlexRayBusConfig()
simulator = FlexRaySimulator(config)
simulator.start()

# Send a test message
message = FlexRayMessage(
    slot_id=10,
    cycle_count=0,
    channel=0x01,  # Channel A
    payload=b'\x01\x02\x03\x04'
)
simulator.send_message(message)

# Get all messages
messages = simulator.get_messages()
print(f"Sent {len(messages)} messages")
```

### Run the Example

```bash
python examples/basic_flexray.py
```

This will demonstrate:
- FlexRay bus configuration
- Starting communication
- Sending test messages
- Monitoring statistics

## FlexRay Configuration

The `FlexRayBusConfig` class provides configuration options:

```python
from flexray import FlexRayBusConfig

config = FlexRayBusConfig()
config.baudrate = 10_000_000      # 10 Mbit/s
config.static_slots = 64          # Number of static slots
config.dynamic_slots = 128        # Number of dynamic slots
config.cycle_duration = 5000      # Communication cycle (5ms)
config.channel = 0x03             # Use both channels (A+B)
```

## Key Concepts

### Communication Cycle

FlexRay uses a time-triggered communication cycle consisting of:
- **Static Segment**: Fixed-time slots for deterministic communication
- **Dynamic Segment**: Event-driven slots for flexible communication
- **Network Idle Time**: Time for clock synchronization

### Channels

FlexRay supports dual-channel operation:
- **Channel A**: Primary communication channel
- **Channel B**: Redundant channel for fault tolerance
- **Both**: Messages can be sent on both channels simultaneously

### Frame Structure

A FlexRay frame contains:
- Header (5 bytes): Slot ID, cycle count, and flags
- Payload (0-254 bytes): Message data
- Trailer (3 bytes): 24-bit CRC for error detection

## Hardware Support

⚠️ **Note**: This is experimental code. Standard Panda devices do NOT support FlexRay natively.

To use FlexRay with Panda, you need:
1. Custom Panda hardware with FlexRay transceiver (e.g., NXP TJA1080)
2. Modified Panda firmware with FlexRay support
3. Appropriate FlexRay bus termination (typically 80-120Ω)

## Development Status

This is experimental software under active development:

- [x] Protocol definitions and constants
- [x] Basic message structure
- [x] Configuration management
- [x] Software simulator
- [x] Example code
- [ ] Hardware driver implementation
- [ ] Firmware integration
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Advanced features (FIBEX support, schedule management)

## Safety and Disclaimer

⚠️ **Important Safety Information**:

- This is experimental research code
- DO NOT use in production vehicles
- Incorrect FlexRay communication can affect vehicle safety systems
- Only use with proper test equipment and safeguards
- Ensure compliance with local regulations

## Contributing

This is an experimental project. Contributions, ideas, and feedback are welcome!

## Resources

### FlexRay Protocol
- [FlexRay Specification v3.0.1](https://svn.ipd.kit.edu/nlrp/public/FlexRay/FlexRay%E2%84%A2%20Protocol%20Specification%20Version%203.0.1.pdf)
- [FlexRay Consortium](http://www.flexray.com/)

### comma.ai Panda
- [Panda GitHub Repository](https://github.com/commaai/panda)
- [Panda Hardware Documentation](https://github.com/commaai/panda/tree/master/docs)
- [comma.ai Blog: FlexRay Experiments](https://blog.comma.ai/hacking-an-audi-performing-a-man-in-the-middle-attack-on-flexray/)

### Automotive Communication
- [Vector FlexRay Documentation](https://www.vector.com/int/en/products/products-a-z/protocols/flexray/)
- [NXP FlexRay Solutions](https://www.nxp.com/products/interfaces/in-vehicle-network/flexray:MC_71493)

## License

This project builds on the sunnypilot and openpilot ecosystem. Please refer to the respective licenses of those projects.

## Acknowledgments

- comma.ai for the Panda platform
- FlexRay Consortium for the protocol specification
- sunnypilot community for inspiration

---

**Status**: 🚧 Experimental - Work in Progress

For questions or discussions, please open an issue on GitHub.
