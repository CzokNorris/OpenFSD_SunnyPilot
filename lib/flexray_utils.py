"""
FlexRay Utilities

Helper functions and utilities for working with FlexRay messages and data.
"""

from typing import List, Dict, Tuple, Any
import struct


def bytes_to_signals(data: bytes, signal_map: Dict[str, Tuple[int, int, str]]) -> Dict[str, Any]:
    """
    Extract signals from FlexRay payload bytes
    
    Args:
        data: Raw payload bytes
        signal_map: Dictionary mapping signal names to (start_byte, length, format)
                   format is struct format string ('B', 'H', 'I', etc.)
    
    Returns:
        Dictionary of signal names to values
    
    Example:
        signal_map = {
            'speed': (0, 2, '>H'),      # 2-byte big-endian unsigned
            'steering': (2, 2, '>h'),    # 2-byte big-endian signed
            'brake': (4, 1, 'B'),        # 1-byte unsigned
        }
        signals = bytes_to_signals(payload, signal_map)
    """
    signals = {}
    
    for name, (start, length, fmt) in signal_map.items():
        signal_data = data[start:start+length]
        if len(signal_data) == length:
            signals[name] = struct.unpack(fmt, signal_data)[0]
        else:
            signals[name] = None
    
    return signals


def signals_to_bytes(signals: Dict[str, Any], signal_map: Dict[str, Tuple[int, int, str]], 
                     payload_length: int = 8) -> bytes:
    """
    Pack signals into FlexRay payload bytes
    
    Args:
        signals: Dictionary of signal names to values
        signal_map: Dictionary mapping signal names to (start_byte, length, format)
        payload_length: Total payload length (default 8 bytes)
    
    Returns:
        Packed payload bytes
    
    Example:
        signals = {'speed': 50, 'steering': -10, 'brake': 1}
        signal_map = {
            'speed': (0, 2, '>H'),
            'steering': (2, 2, '>h'),
            'brake': (4, 1, 'B'),
        }
        payload = signals_to_bytes(signals, signal_map, 8)
    """
    # Start with zeros
    data = bytearray(payload_length)
    
    for name, value in signals.items():
        if name in signal_map and value is not None:
            start, length, fmt = signal_map[name]
            packed = struct.pack(fmt, value)
            data[start:start+length] = packed
    
    return bytes(data)


def create_dbc_entry(slot_id: int, signal_map: Dict[str, Tuple[int, int, str]], 
                     cycle_time: int = 5) -> str:
    """
    Create a DBC-like entry for a FlexRay frame (for documentation purposes)
    
    Args:
        slot_id: FlexRay slot ID
        signal_map: Signal definitions
        cycle_time: Cycle time in milliseconds
    
    Returns:
        DBC-format string
    """
    lines = []
    lines.append(f"BO_ {slot_id} FlexRayFrame_{slot_id}: {max(s[0]+s[1] for s in signal_map.values())} Vector__XXX")
    
    for name, (start_byte, length, fmt) in signal_map.items():
        start_bit = start_byte * 8
        bit_length = length * 8
        lines.append(f" SG_ {name} : {start_bit}|{bit_length}@1+ (1,0) [0|0] \"\" Vector__XXX")
    
    return '\n'.join(lines)


def calculate_bus_utilization(num_static_slots: int, slot_duration_us: int, 
                             cycle_duration_us: int) -> float:
    """
    Calculate FlexRay bus utilization for static segment
    
    Args:
        num_static_slots: Number of static slots configured
        slot_duration_us: Duration of each slot in microseconds
        cycle_duration_us: Total cycle duration in microseconds
    
    Returns:
        Utilization as percentage (0-100)
    """
    static_segment_time = num_static_slots * slot_duration_us
    utilization = (static_segment_time / cycle_duration_us) * 100
    return min(utilization, 100.0)


def format_payload_hex(data: bytes, bytes_per_line: int = 16) -> str:
    """
    Format payload bytes as hex dump
    
    Args:
        data: Payload bytes
        bytes_per_line: Number of bytes per line
    
    Returns:
        Formatted hex string
    """
    lines = []
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i:i+bytes_per_line]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f'{i:04x}  {hex_str:<{bytes_per_line*3}}  {ascii_str}')
    return '\n'.join(lines)


def validate_cycle_timing(config: 'FlexRayBusConfig') -> List[str]:
    """
    Validate FlexRay cycle timing configuration
    
    Args:
        config: FlexRay bus configuration
    
    Returns:
        List of validation warnings/errors (empty if valid)
    
    Note:
        This assumes a default slot duration of 50us. For precise validation,
        the actual configured slot duration should be used.
    """
    issues = []
    
    # Default slot duration assumption (in microseconds)
    # This should ideally come from the actual configuration
    DEFAULT_SLOT_DURATION_US = 50
    
    # Check static segment fits in cycle
    static_time = config.static_slots * DEFAULT_SLOT_DURATION_US
    if static_time >= config.cycle_duration:
        issues.append(f"Static segment ({static_time}us) exceeds cycle duration ({config.cycle_duration}us)")
    
    # Check network idle time
    if config.network_idle_time < 1000:
        issues.append(f"Network idle time ({config.network_idle_time}us) is less than recommended 1000us")
    
    # Check total timing
    total_time = static_time + config.network_idle_time
    if total_time > config.cycle_duration:
        issues.append(f"Total segment time ({total_time}us) exceeds cycle duration")
    
    return issues


class FlexRayLogger:
    """Simple logger for FlexRay messages"""
    
    def __init__(self, filename: str):
        """Initialize logger"""
        self.filename = filename
        self.messages = []
    
    def log_message(self, slot_id: int, cycle: int, channel: int, payload: bytes, 
                   timestamp: float):
        """Log a message"""
        self.messages.append({
            'timestamp': timestamp,
            'slot_id': slot_id,
            'cycle': cycle,
            'channel': channel,
            'payload': payload.hex(),
            'length': len(payload)
        })
    
    def save(self):
        """Save logged messages to file"""
        with open(self.filename, 'w') as f:
            f.write("Timestamp,Slot,Cycle,Channel,Length,Payload\n")
            for msg in self.messages:
                f.write(f"{msg['timestamp']:.6f},{msg['slot_id']},{msg['cycle']},"
                       f"{msg['channel']},{msg['length']},{msg['payload']}\n")
    
    def get_statistics(self) -> Dict:
        """Get logging statistics"""
        if not self.messages:
            return {}
        
        slot_counts = {}
        for msg in self.messages:
            slot_counts[msg['slot_id']] = slot_counts.get(msg['slot_id'], 0) + 1
        
        return {
            'total_messages': len(self.messages),
            'unique_slots': len(slot_counts),
            'slot_distribution': slot_counts,
            'duration': self.messages[-1]['timestamp'] - self.messages[0]['timestamp']
        }
