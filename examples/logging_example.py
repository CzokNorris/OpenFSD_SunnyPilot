#!/usr/bin/env python3
"""
FlexRay Data Logging Example

Demonstrates logging FlexRay messages to file and analyzing the data.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flexray import FlexRayBusConfig, FlexRayFrame
from flexray.interface import FlexRayPanda, FlexRayMessage, FlexRaySimulator
from lib.flexray_utils import (
    FlexRayLogger,
    bytes_to_signals,
    signals_to_bytes,
    format_payload_hex
)


def main():
    print("=" * 60)
    print("FlexRay Data Logging Example")
    print("=" * 60)
    
    # Setup configuration
    config = FlexRayBusConfig()
    panda = FlexRayPanda(config)
    simulator = FlexRaySimulator(config)
    
    # Create logger
    log_file = "/tmp/flexray_log.csv"
    logger = FlexRayLogger(log_file)
    
    print(f"\nLogging to: {log_file}")
    
    # Define signal structure for vehicle data
    vehicle_signals = {
        'speed_kmh': (0, 2, '>H'),      # Speed in km/h
        'steering_deg': (2, 2, '>h'),   # Steering angle in degrees
        'throttle_pct': (4, 1, 'B'),    # Throttle position 0-100%
        'brake_pct': (5, 1, 'B'),       # Brake position 0-100%
        'gear': (6, 1, 'B'),            # Current gear
        'status': (7, 1, 'B'),          # Status flags
    }
    
    print("\nSignal definitions:")
    for name, (start, length, fmt) in vehicle_signals.items():
        print(f"  {name:15s}: Byte {start}, Length {length}")
    
    # Initialize
    print("\n" + "-" * 60)
    simulator.start()
    panda.configure(config)
    panda.start()
    
    # Generate and log test data
    print("Generating test data...")
    
    test_scenarios = [
        {'speed_kmh': 0, 'steering_deg': 0, 'throttle_pct': 0, 'brake_pct': 0, 'gear': 0, 'status': 0x01},
        {'speed_kmh': 20, 'steering_deg': 10, 'throttle_pct': 30, 'brake_pct': 0, 'gear': 2, 'status': 0x02},
        {'speed_kmh': 50, 'steering_deg': -5, 'throttle_pct': 60, 'brake_pct': 0, 'gear': 4, 'status': 0x03},
        {'speed_kmh': 80, 'steering_deg': 0, 'throttle_pct': 80, 'brake_pct': 0, 'gear': 5, 'status': 0x03},
        {'speed_kmh': 60, 'steering_deg': -15, 'throttle_pct': 40, 'brake_pct': 20, 'gear': 4, 'status': 0x03},
        {'speed_kmh': 30, 'steering_deg': 0, 'throttle_pct': 0, 'brake_pct': 50, 'gear': 3, 'status': 0x05},
        {'speed_kmh': 0, 'steering_deg': 0, 'throttle_pct': 0, 'brake_pct': 100, 'gear': 0, 'status': 0x01},
    ]
    
    slot_id = 100
    
    for cycle, signals in enumerate(test_scenarios):
        # Pack signals into payload
        payload = signals_to_bytes(signals, vehicle_signals, 8)
        
        # Create message
        message = FlexRayMessage(
            slot_id=slot_id,
            cycle_count=cycle,
            channel=FlexRayFrame.CHANNEL_A,
            payload=payload
        )
        
        # Send and log
        timestamp = time.time()
        panda.send_message(message)
        simulator.send_message(message)
        
        logger.log_message(slot_id, cycle, message.channel, payload, timestamp)
        
        # Display current data
        print(f"\nCycle {cycle}:")
        print(f"  Speed: {signals['speed_kmh']} km/h")
        print(f"  Steering: {signals['steering_deg']}°")
        print(f"  Throttle: {signals['throttle_pct']}%")
        print(f"  Brake: {signals['brake_pct']}%")
        print(f"  Gear: {signals['gear']}")
        print(f"  Payload: {payload.hex()}")
        
        time.sleep(0.2)
    
    # Save log
    print("\n" + "-" * 60)
    print("Saving log file...")
    logger.save()
    print(f"✓ Log saved to {log_file}")
    
    # Display statistics
    print("\n" + "-" * 60)
    print("Statistics:")
    stats = logger.get_statistics()
    for key, value in stats.items():
        if key != 'slot_distribution':
            print(f"  {key}: {value}")
    
    # Demonstrate reading and parsing
    print("\n" + "-" * 60)
    print("Parsing logged messages...")
    
    for i, msg in enumerate(logger.messages[:3]):  # Show first 3
        payload_bytes = bytes.fromhex(msg['payload'])
        parsed_signals = bytes_to_signals(payload_bytes, vehicle_signals)
        
        print(f"\nMessage {i}:")
        print(f"  Timestamp: {msg['timestamp']:.6f}")
        print(f"  Slot: {msg['slot_id']}, Cycle: {msg['cycle']}")
        print(f"  Signals:")
        for name, value in parsed_signals.items():
            print(f"    {name:15s}: {value}")
    
    # Show hex dump
    print("\n" + "-" * 60)
    print("Sample payload hex dump:")
    sample_payload = bytes.fromhex(logger.messages[3]['payload'])
    print(format_payload_hex(sample_payload))
    
    # Cleanup
    print("\n" + "-" * 60)
    panda.stop()
    simulator.stop()
    
    print("\n✓ Logging example completed!")
    print(f"\nYou can analyze the log file with:")
    print(f"  cat {log_file}")
    print(f"  head -5 {log_file}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
