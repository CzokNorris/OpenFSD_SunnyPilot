"""
FlexRay Protocol Definitions and Constants

This module defines the FlexRay communication protocol parameters and constants
used for experimental Panda support with FlexRay-enabled vehicles.

FlexRay is a deterministic, fault-tolerant communication system for automotive
applications with high data rates (up to 10 Mbit/s).
"""

# FlexRay Protocol Version
FLEXRAY_VERSION = "3.0.1"

# FlexRay Timing Parameters (in microseconds)
class FlexRayTiming:
    """FlexRay timing parameters for bus configuration"""
    
    # Cycle timing
    GDCYCLE = 5000  # Duration of communication cycle (5ms default)
    GD_STATIC_SLOT = 50  # Duration of static slot (50us)
    GD_MINISLOT = 5  # Duration of minislot (5us)
    GD_NIT = 1000  # Duration of Network Idle Time (1ms)
    
    # Symbol timing
    GD_TSS_TRANSMITTER = 3  # Transmitter start sequence
    GD_CAS_RX = 11  # Collision avoidance symbol RX
    
    # Sample points
    GD_SAMPLE_CLOCK_PERIOD = 0.0125  # 12.5ns for 80MHz


# FlexRay Frame Parameters
class FlexRayFrame:
    """FlexRay frame structure parameters"""
    
    # Frame lengths (in bytes)
    MAX_PAYLOAD_LENGTH = 254  # Maximum payload in bytes
    HEADER_LENGTH = 5  # Frame header length
    TRAILER_LENGTH = 3  # Frame trailer (CRC)
    
    # Slot IDs
    MIN_SLOT_ID = 1
    MAX_SLOT_ID = 2047
    
    # Channel identifiers
    CHANNEL_A = 0x01
    CHANNEL_B = 0x02
    CHANNEL_AB = 0x03  # Both channels


# FlexRay Bus Configuration
class FlexRayBusConfig:
    """Default FlexRay bus configuration parameters"""
    
    def __init__(self):
        self.baudrate = 10_000_000  # 10 Mbit/s
        self.static_slots = 64  # Number of static slots
        self.dynamic_slots = 128  # Number of dynamic slots
        self.payload_length = 32  # Default payload length in 16-bit words
        
        # Cluster parameters
        self.cycle_duration = 5000  # microseconds
        self.network_idle_time = 1000  # microseconds
        
        # Channel assignment
        self.channel = FlexRayFrame.CHANNEL_AB
        
        # Wakeup parameters
        self.wakeup_symbol_rx_low = 18
        self.wakeup_symbol_rx_window = 76
        
    def to_dict(self):
        """Convert configuration to dictionary"""
        return {
            'baudrate': self.baudrate,
            'static_slots': self.static_slots,
            'dynamic_slots': self.dynamic_slots,
            'payload_length': self.payload_length,
            'cycle_duration': self.cycle_duration,
            'network_idle_time': self.network_idle_time,
            'channel': self.channel,
            'wakeup_symbol_rx_low': self.wakeup_symbol_rx_low,
            'wakeup_symbol_rx_window': self.wakeup_symbol_rx_window,
        }


# FlexRay State Machine States
class FlexRayState:
    """FlexRay Communication Controller states"""
    
    DEFAULT_CONFIG = 0x00
    READY = 0x01
    NORMAL_ACTIVE = 0x02
    NORMAL_PASSIVE = 0x03
    HALT = 0x04
    MONITOR_MODE = 0x05
    CONFIG = 0x0F
    WAKEUP = 0x10
    STARTUP = 0x11


# FlexRay Error Types
class FlexRayError:
    """FlexRay error definitions"""
    
    # Syntax errors
    SYNTAX_ERROR = 0x01
    CONTENT_ERROR = 0x02
    SLOT_BOUNDARY_VIOLATION = 0x03
    
    # Protocol errors  
    CYCLE_START_ERROR = 0x10
    SLOT_START_ERROR = 0x11
    
    # Communication errors
    CHANNEL_A_ERROR = 0x20
    CHANNEL_B_ERROR = 0x21
    MISSING_RATE_CORRECTION = 0x30
    MISSING_OFFSET_CORRECTION = 0x31


# FlexRay Commands
class FlexRayCommand:
    """Command codes for FlexRay controller"""
    
    CONFIG = 0x01
    READY = 0x02
    WAKEUP = 0x03
    RUN = 0x04
    ALL_SLOTS = 0x05
    HALT = 0x06
    FREEZE = 0x07
    SEND_MTS = 0x08
    ALLOW_COLDSTART = 0x09
    RESET_STATUS_INDICATORS = 0x0A
    MONITOR_MODE = 0x0B
    CLEAR_RAMS = 0x0C


# FlexRay Message Flags
class FlexRayFlags:
    """Flags for FlexRay message transmission"""
    
    STARTUP_FRAME = 0x01
    SYNC_FRAME = 0x02
    NULL_FRAME = 0x04
    PAYLOAD_PREAMBLE = 0x08
    
    # Channel flags
    TRANSMIT_ON_A = 0x10
    TRANSMIT_ON_B = 0x20
    TRANSMIT_ON_BOTH = 0x30


def calculate_frame_crc(header: bytes, payload: bytes) -> int:
    """
    Calculate FlexRay frame CRC
    
    Args:
        header: Frame header bytes
        payload: Frame payload bytes
        
    Returns:
        24-bit CRC value
    """
    # FlexRay uses CRC-24 polynomial: 0x5D6DCB
    CRC_POLYNOMIAL = 0x5D6DCB
    crc = 0xFEDCBA  # Initial value
    
    # Process header
    for byte in header:
        crc ^= (byte << 16)
        for _ in range(8):
            if crc & 0x800000:
                crc = ((crc << 1) ^ CRC_POLYNOMIAL) & 0xFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFF
    
    # Process payload
    for byte in payload:
        crc ^= (byte << 16)
        for _ in range(8):
            if crc & 0x800000:
                crc = ((crc << 1) ^ CRC_POLYNOMIAL) & 0xFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFF
    
    return crc


def format_frame_id(slot_id: int, cycle_count: int = 0) -> str:
    """
    Format FlexRay frame identifier
    
    Args:
        slot_id: Slot ID (1-2047)
        cycle_count: Cycle counter (0-63)
        
    Returns:
        Formatted frame ID string
    """
    if not (FlexRayFrame.MIN_SLOT_ID <= slot_id <= FlexRayFrame.MAX_SLOT_ID):
        raise ValueError(f"Slot ID must be between {FlexRayFrame.MIN_SLOT_ID} and {FlexRayFrame.MAX_SLOT_ID}")
    
    return f"FR_{slot_id:04d}_C{cycle_count:02d}"
