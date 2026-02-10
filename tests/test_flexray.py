"""
Unit tests for FlexRay protocol implementation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flexray import (
    FlexRayBusConfig,
    FlexRayFrame,
    FlexRayState,
    FlexRayCommand,
    calculate_frame_crc,
    format_frame_id,
)
from flexray.interface import FlexRayMessage, FlexRayPanda, FlexRaySimulator


def test_bus_config():
    """Test FlexRay bus configuration"""
    print("Testing FlexRay bus configuration...")
    
    config = FlexRayBusConfig()
    
    # Check defaults
    assert config.baudrate == 10_000_000, "Default baudrate should be 10 Mbit/s"
    assert config.static_slots == 64, "Default static slots should be 64"
    assert config.cycle_duration == 5000, "Default cycle duration should be 5000 µs"
    
    # Test to_dict conversion
    config_dict = config.to_dict()
    assert 'baudrate' in config_dict
    assert 'static_slots' in config_dict
    assert config_dict['baudrate'] == 10_000_000
    
    print("✓ Bus configuration tests passed")


def test_message_creation():
    """Test FlexRay message creation"""
    print("Testing FlexRay message creation...")
    
    # Create a message
    message = FlexRayMessage(
        slot_id=10,
        cycle_count=5,
        channel=FlexRayFrame.CHANNEL_A,
        payload=b'\x01\x02\x03\x04'
    )
    
    assert message.slot_id == 10
    assert message.cycle_count == 5
    assert message.channel == FlexRayFrame.CHANNEL_A
    assert message.payload == b'\x01\x02\x03\x04'
    assert message.timestamp > 0
    
    print("✓ Message creation tests passed")


def test_message_serialization():
    """Test message serialization and deserialization"""
    print("Testing message serialization...")
    
    # Create a message
    original = FlexRayMessage(
        slot_id=100,
        cycle_count=10,
        channel=FlexRayFrame.CHANNEL_AB,
        payload=b'\xAA\xBB\xCC\xDD\xEE\xFF'
    )
    
    # Serialize to bytes
    data = original.to_bytes()
    assert isinstance(data, bytes)
    assert len(data) > len(original.payload)  # Should include header and CRC
    
    # Deserialize
    restored = FlexRayMessage.from_bytes(data)
    assert restored.slot_id == original.slot_id
    assert restored.cycle_count == original.cycle_count
    assert restored.channel == original.channel
    assert restored.payload == original.payload
    
    print("✓ Message serialization tests passed")


def test_crc_calculation():
    """Test CRC calculation"""
    print("Testing CRC calculation...")
    
    header = b'\x00\x0A\x01\x00'
    payload = b'\x01\x02\x03\x04'
    
    crc = calculate_frame_crc(header, payload)
    
    # CRC should be 24-bit value
    assert 0 <= crc <= 0xFFFFFF
    
    # Same input should give same CRC
    crc2 = calculate_frame_crc(header, payload)
    assert crc == crc2
    
    # Different input should give different CRC
    different_payload = b'\x05\x06\x07\x08'
    crc3 = calculate_frame_crc(header, different_payload)
    assert crc != crc3
    
    print("✓ CRC calculation tests passed")


def test_frame_id_formatting():
    """Test frame ID formatting"""
    print("Testing frame ID formatting...")
    
    frame_id = format_frame_id(10, 5)
    assert frame_id == "FR_0010_C05"
    
    frame_id = format_frame_id(2047, 63)
    assert frame_id == "FR_2047_C63"
    
    # Test invalid slot ID
    try:
        format_frame_id(0, 0)  # Below minimum
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        format_frame_id(2048, 0)  # Above maximum
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ Frame ID formatting tests passed")


def test_panda_interface():
    """Test FlexRay Panda interface"""
    print("Testing FlexRay Panda interface...")
    
    config = FlexRayBusConfig()
    panda = FlexRayPanda(config)
    
    # Initial state should be DEFAULT_CONFIG
    assert panda.get_state() == FlexRayState.DEFAULT_CONFIG
    
    # Configure
    assert panda.configure(config) == True
    assert panda.get_state() == FlexRayState.READY
    
    # Start communication
    assert panda.start() == True
    assert panda.get_state() == FlexRayState.NORMAL_ACTIVE
    
    # Send a message
    message = FlexRayMessage(
        slot_id=50,
        cycle_count=0,
        channel=FlexRayFrame.CHANNEL_A,
        payload=b'\x12\x34\x56\x78'
    )
    assert panda.send_message(message) == True
    
    # Get statistics
    stats = panda.get_statistics()
    assert 'state' in stats
    assert stats['state'] == FlexRayState.NORMAL_ACTIVE
    
    # Stop communication
    assert panda.stop() == True
    assert panda.get_state() == FlexRayState.HALT
    
    print("✓ Panda interface tests passed")


def test_simulator():
    """Test FlexRay simulator"""
    print("Testing FlexRay simulator...")
    
    config = FlexRayBusConfig()
    simulator = FlexRaySimulator(config)
    
    # Start simulator
    assert simulator.running == False
    simulator.start()
    assert simulator.running == True
    assert simulator.cycle_count == 0
    
    # Send messages
    message1 = FlexRayMessage(slot_id=10, cycle_count=0, channel=1, payload=b'\x01\x02')
    message2 = FlexRayMessage(slot_id=20, cycle_count=0, channel=1, payload=b'\x03\x04')
    
    simulator.send_message(message1)
    simulator.send_message(message2)
    
    messages = simulator.get_messages()
    assert len(messages) == 2
    assert messages[0].slot_id == 10
    assert messages[1].slot_id == 20
    
    # Advance cycles
    simulator.advance_cycle()
    assert simulator.cycle_count == 1
    
    # Advance to cycle 63, then one more to wrap to 0
    for _ in range(62):  # Advance 62 more times to reach cycle 63
        simulator.advance_cycle()
    assert simulator.cycle_count == 63
    
    simulator.advance_cycle()  # One more to wrap to 0
    assert simulator.cycle_count == 0  # Should wrap around from 63 to 0
    
    # Stop simulator
    simulator.stop()
    assert simulator.running == False
    
    print("✓ Simulator tests passed")


def test_slot_id_validation():
    """Test slot ID validation"""
    print("Testing slot ID validation...")
    
    panda = FlexRayPanda()
    panda.configure(FlexRayBusConfig())
    panda.start()
    
    # Valid slot IDs
    valid_message = FlexRayMessage(
        slot_id=FlexRayFrame.MIN_SLOT_ID,
        cycle_count=0,
        channel=1,
        payload=b'\x00'
    )
    assert panda.send_message(valid_message) == True
    
    valid_message = FlexRayMessage(
        slot_id=FlexRayFrame.MAX_SLOT_ID,
        cycle_count=0,
        channel=1,
        payload=b'\x00'
    )
    assert panda.send_message(valid_message) == True
    
    # Invalid slot ID (too low)
    try:
        invalid_message = FlexRayMessage(
            slot_id=0,
            cycle_count=0,
            channel=1,
            payload=b'\x00'
        )
        panda.send_message(invalid_message)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Invalid slot ID (too high)
    try:
        invalid_message = FlexRayMessage(
            slot_id=FlexRayFrame.MAX_SLOT_ID + 1,
            cycle_count=0,
            channel=1,
            payload=b'\x00'
        )
        panda.send_message(invalid_message)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ Slot ID validation tests passed")


def test_payload_length_validation():
    """Test payload length validation"""
    print("Testing payload length validation...")
    
    panda = FlexRayPanda()
    panda.configure(FlexRayBusConfig())
    panda.start()
    
    # Valid payload (maximum length)
    max_payload = b'\x00' * FlexRayFrame.MAX_PAYLOAD_LENGTH
    valid_message = FlexRayMessage(
        slot_id=10,
        cycle_count=0,
        channel=1,
        payload=max_payload
    )
    assert panda.send_message(valid_message) == True
    
    # Invalid payload (too large)
    try:
        oversized_payload = b'\x00' * (FlexRayFrame.MAX_PAYLOAD_LENGTH + 1)
        invalid_message = FlexRayMessage(
            slot_id=10,
            cycle_count=0,
            channel=1,
            payload=oversized_payload
        )
        panda.send_message(invalid_message)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ Payload length validation tests passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running FlexRay Protocol Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_bus_config,
        test_message_creation,
        test_message_serialization,
        test_crc_calculation,
        test_frame_id_formatting,
        test_panda_interface,
        test_simulator,
        test_slot_id_validation,
        test_payload_length_validation,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
            print()
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed.append(test.__name__)
            print()
    
    print("=" * 60)
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed:")
        for name in failed:
            print(f"  - {name}")
        return False
    else:
        print("SUCCESS: All tests passed!")
        return True
    print("=" * 60)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
