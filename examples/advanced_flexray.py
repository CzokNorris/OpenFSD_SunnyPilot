#!/usr/bin/env python3
"""
Advanced FlexRay Example - Multi-Cycle Communication

This example demonstrates advanced FlexRay features:
- Multi-cycle communication patterns
- Static and dynamic slot usage
- Dual-channel communication
- Message filtering and callbacks
- Cycle-based scheduling
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flexray import FlexRayBusConfig, FlexRayFrame
from flexray.interface import FlexRayPanda, FlexRayMessage, FlexRaySimulator


class FlexRayNode:
    """Simulated FlexRay node for demonstration"""
    
    def __init__(self, name: str, slots: list):
        """
        Initialize node
        
        Args:
            name: Node name
            slots: List of slot IDs this node transmits in
        """
        self.name = name
        self.slots = slots
        self.rx_count = 0
        self.tx_count = 0
    
    def on_message(self, message: FlexRayMessage):
        """Handle received message"""
        if message.slot_id in self.slots:
            return  # Ignore own messages
        
        self.rx_count += 1
        print(f"  [{self.name}] RX Slot {message.slot_id}: {message.payload.hex()}")
    
    def create_message(self, slot_id: int, cycle: int, data: bytes) -> FlexRayMessage:
        """Create a message for transmission"""
        self.tx_count += 1
        return FlexRayMessage(
            slot_id=slot_id,
            cycle_count=cycle,
            channel=FlexRayFrame.CHANNEL_AB,  # Transmit on both channels
            payload=data
        )


def main():
    print("=" * 70)
    print("Advanced FlexRay Example - Multi-Cycle Communication")
    print("=" * 70)
    
    # Create FlexRay configuration
    config = FlexRayBusConfig()
    config.baudrate = 10_000_000
    config.static_slots = 32
    config.cycle_duration = 5000
    
    # Create simulator
    simulator = FlexRaySimulator(config)
    panda = FlexRayPanda(config)
    
    # Create virtual nodes
    ecu1 = FlexRayNode("ECU1", [10, 11, 12])
    ecu2 = FlexRayNode("ECU2", [20, 21, 22])
    ecu3 = FlexRayNode("ECU3", [30, 31, 32])
    
    nodes = [ecu1, ecu2, ecu3]
    
    # Register callbacks
    for node in nodes:
        panda.register_callback(node.on_message)
    
    print("\nNetwork Configuration:")
    print(f"  Baudrate: {config.baudrate / 1_000_000} Mbit/s")
    print(f"  Static slots: {config.static_slots}")
    print(f"  Cycle duration: {config.cycle_duration} µs")
    
    print("\nNodes:")
    for node in nodes:
        print(f"  {node.name}: Slots {node.slots}")
    
    # Initialize communication
    print("\n" + "-" * 70)
    print("Starting communication...")
    
    simulator.start()
    panda.configure(config)
    panda.start()
    
    # Simulate multiple communication cycles
    print("\nSimulating 10 communication cycles...")
    print("-" * 70)
    
    cycle_messages = {
        # Cycle 0: Basic signals
        0: [
            (ecu1, 10, b'\x01\x00\x00\x00'),  # Speed signal
            (ecu2, 20, b'\x00\x50\x00\x00'),  # Steering angle
            (ecu3, 30, b'\x00\x00\x00\x01'),  # Brake status
        ],
        # Cycle 1: Extended signals
        1: [
            (ecu1, 11, b'\x02\x00\x00\x00'),  # Acceleration
            (ecu2, 21, b'\x00\x60\x00\x00'),  # Steering torque
        ],
        # Cycle 2: Status messages
        2: [
            (ecu1, 12, b'\x00\x00\x00\xFF'),  # ECU status
            (ecu3, 31, b'\x00\x00\x10\x00'),  # Brake temperature
        ],
        # Cycle 5: Diagnostic messages
        5: [
            (ecu1, 10, b'\xFF\xFF\xFF\xFF'),  # Diagnostic request
            (ecu2, 20, b'\x00\x00\x00\x00'),  # Diagnostic response
            (ecu3, 32, b'\x12\x34\x56\x78'),  # Error codes
        ],
    }
    
    num_cycles = 10
    for cycle in range(num_cycles):
        print(f"\n--- Cycle {cycle} ---")
        
        # Send scheduled messages for this cycle
        if cycle in cycle_messages:
            for node, slot_id, data in cycle_messages[cycle]:
                message = node.create_message(slot_id, cycle, data)
                
                if panda.send_message(message):
                    simulator.send_message(message)
                    print(f"  [{node.name}] TX Slot {slot_id}: {data.hex()}")
                    
                    # Simulate message reception by other nodes
                    for other_node in nodes:
                        if other_node != node:
                            other_node.on_message(message)
        else:
            print("  (No scheduled messages)")
        
        # Advance simulator cycle
        simulator.advance_cycle()
        
        # Simulate cycle time
        time.sleep(0.1)
    
    # Show statistics
    print("\n" + "=" * 70)
    print("Communication Statistics")
    print("=" * 70)
    
    print("\nPanda Interface:")
    stats = panda.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nNodes:")
    for node in nodes:
        print(f"  {node.name}:")
        print(f"    Transmitted: {node.tx_count} messages")
        print(f"    Received: {node.rx_count} messages")
    
    print(f"\nSimulator:")
    print(f"  Total messages: {len(simulator.get_messages())}")
    print(f"  Current cycle: {simulator.cycle_count}")
    
    # Message analysis
    print("\n" + "-" * 70)
    print("Message Distribution by Slot:")
    print("-" * 70)
    
    slot_counts = {}
    for msg in simulator.get_messages():
        slot_counts[msg.slot_id] = slot_counts.get(msg.slot_id, 0) + 1
    
    for slot_id in sorted(slot_counts.keys()):
        print(f"  Slot {slot_id:2d}: {slot_counts[slot_id]} messages")
    
    # Cleanup
    print("\n" + "-" * 70)
    print("Stopping communication...")
    panda.stop()
    simulator.stop()
    
    print("\n" + "=" * 70)
    print("Advanced example completed!")
    print("=" * 70)


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
