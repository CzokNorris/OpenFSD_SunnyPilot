#!/usr/bin/env python3
"""
FlexRay Panda Basic Example

This example demonstrates basic FlexRay communication using the experimental
Panda FlexRay support. It shows how to:
- Configure a FlexRay bus
- Start communication
- Send and receive messages
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flexray import FlexRayBusConfig, FlexRayFrame
from flexray.interface import FlexRayPanda, FlexRayMessage, FlexRaySimulator


def message_handler(message: FlexRayMessage):
    """Callback for received messages"""
    print(f"Received: Slot={message.slot_id}, Cycle={message.cycle_count}, "
          f"Channel={message.channel}, Data={message.payload.hex()}")


def main():
    print("=" * 60)
    print("FlexRay Panda Basic Example")
    print("=" * 60)
    
    # Create custom configuration
    config = FlexRayBusConfig()
    config.baudrate = 10_000_000  # 10 Mbit/s
    config.static_slots = 64
    config.cycle_duration = 5000  # 5ms
    
    print("\nFlexRay Configuration:")
    print(f"  Baudrate: {config.baudrate / 1_000_000} Mbit/s")
    print(f"  Static slots: {config.static_slots}")
    print(f"  Cycle duration: {config.cycle_duration} µs")
    print(f"  Channel: {config.channel}")
    
    # Initialize FlexRay Panda interface
    # Note: This requires experimental FlexRay-enabled Panda hardware
    panda = FlexRayPanda(config)
    
    # For testing without hardware, use simulator
    use_simulator = True
    if use_simulator:
        print("\nUsing FlexRay simulator (no hardware required)")
        simulator = FlexRaySimulator(config)
        simulator.start()
    
    print("\n" + "-" * 60)
    print("Configuring FlexRay controller...")
    
    if panda.configure(config):
        print("✓ Configuration successful")
    else:
        print("✗ Configuration failed")
        return
    
    print("\nStarting FlexRay communication...")
    if panda.start():
        print("✓ Communication started")
    else:
        print("✗ Failed to start communication")
        return
    
    # Register message callback
    panda.register_callback(message_handler)
    
    print("\n" + "-" * 60)
    print("Sending test messages...")
    
    # Send some test messages
    test_messages = [
        # Slot ID, Cycle, Channel, Payload
        (10, 0, FlexRayFrame.CHANNEL_A, b'\x01\x02\x03\x04'),
        (20, 0, FlexRayFrame.CHANNEL_B, b'\x05\x06\x07\x08'),
        (30, 0, FlexRayFrame.CHANNEL_AB, b'\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10'),
    ]
    
    for slot_id, cycle, channel, payload in test_messages:
        message = FlexRayMessage(
            slot_id=slot_id,
            cycle_count=cycle,
            channel=channel,
            payload=payload
        )
        
        if panda.send_message(message):
            print(f"✓ Sent message: Slot={slot_id}, Channel={channel}, "
                  f"Data={payload.hex()}")
            
            if use_simulator:
                simulator.send_message(message)
        else:
            print(f"✗ Failed to send message: Slot={slot_id}")
        
        time.sleep(0.1)
    
    print("\n" + "-" * 60)
    print("Communication Statistics:")
    stats = panda.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    if use_simulator:
        print(f"\nSimulator messages: {len(simulator.get_messages())}")
        for msg in simulator.get_messages():
            print(f"  - Slot {msg.slot_id}: {msg.payload.hex()}")
    
    print("\n" + "-" * 60)
    print("Stopping FlexRay communication...")
    if panda.stop():
        print("✓ Communication stopped")
    
    if use_simulator:
        simulator.stop()
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
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
