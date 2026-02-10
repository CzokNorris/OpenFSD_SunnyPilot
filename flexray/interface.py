"""
FlexRay Panda Interface

This module provides an interface for communicating with FlexRay-enabled Panda devices.
It handles the low-level communication protocol and provides a high-level API for
sending and receiving FlexRay frames.
"""

import struct
import time
from typing import Optional, List, Tuple, Callable
from dataclasses import dataclass
from .protocol import (
    FlexRayBusConfig,
    FlexRayFrame,
    FlexRayState,
    FlexRayCommand,
    FlexRayFlags,
    calculate_frame_crc,
)


@dataclass
class FlexRayMessage:
    """Represents a FlexRay message"""
    slot_id: int
    cycle_count: int
    channel: int
    payload: bytes
    flags: int = 0
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def to_bytes(self) -> bytes:
        """Convert message to bytes for transmission"""
        # Build header
        header = struct.pack('>HBB', 
            self.slot_id,
            self.cycle_count,
            (self.channel << 4) | (self.flags & 0x0F)
        )
        
        # Add payload length
        header += struct.pack('>H', len(self.payload))
        
        # Calculate CRC
        crc = calculate_frame_crc(header, self.payload)
        
        # Build complete frame with 24-bit CRC
        # Pack CRC as 3 separate bytes (24 bits)
        crc_bytes = struct.pack('>BBB', (crc >> 16) & 0xFF, (crc >> 8) & 0xFF, crc & 0xFF)
        frame = header + self.payload + crc_bytes
        return frame
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'FlexRayMessage':
        """Parse message from bytes"""
        if len(data) < 8:
            raise ValueError("Frame too short")
        
        # Parse header
        slot_id, cycle_count, chan_flags, payload_len = struct.unpack('>HBBH', data[:6])
        channel = (chan_flags >> 4) & 0x03
        flags = chan_flags & 0x0F
        
        # Extract payload
        payload = data[6:6+payload_len]
        
        return cls(
            slot_id=slot_id,
            cycle_count=cycle_count,
            channel=channel,
            payload=payload,
            flags=flags,
            timestamp=time.time()
        )


class FlexRayPanda:
    """
    FlexRay Panda Interface
    
    This class provides an interface to communicate with a FlexRay-enabled Panda device.
    Note: This is experimental and requires custom Panda hardware with FlexRay support.
    """
    
    def __init__(self, config: Optional[FlexRayBusConfig] = None):
        """
        Initialize FlexRay Panda interface
        
        Args:
            config: FlexRay bus configuration. If None, uses default configuration.
        """
        self.config = config or FlexRayBusConfig()
        self.state = FlexRayState.DEFAULT_CONFIG
        self._message_callbacks: List[Callable[[FlexRayMessage], None]] = []
        self._running = False
        
    def configure(self, config: FlexRayBusConfig) -> bool:
        """
        Configure the FlexRay controller
        
        Args:
            config: FlexRay bus configuration
            
        Returns:
            True if configuration successful
        """
        if self.state != FlexRayState.DEFAULT_CONFIG:
            return False
        
        self.config = config
        
        # TODO: Send configuration to actual hardware
        # This is a placeholder for experimental hardware interface
        print(f"Configuring FlexRay with parameters: {config.to_dict()}")
        
        self.state = FlexRayState.READY
        return True
    
    def start(self) -> bool:
        """
        Start FlexRay communication
        
        Returns:
            True if started successfully
        """
        if self.state != FlexRayState.READY:
            return False
        
        # TODO: Send start command to hardware
        print("Starting FlexRay communication")
        
        self.state = FlexRayState.NORMAL_ACTIVE
        self._running = True
        return True
    
    def stop(self) -> bool:
        """
        Stop FlexRay communication
        
        Returns:
            True if stopped successfully
        """
        if self.state != FlexRayState.NORMAL_ACTIVE:
            return False
        
        # TODO: Send stop command to hardware
        print("Stopping FlexRay communication")
        
        self.state = FlexRayState.HALT
        self._running = False
        return True
    
    def send_message(self, message: FlexRayMessage) -> bool:
        """
        Send a FlexRay message
        
        Args:
            message: FlexRay message to send
            
        Returns:
            True if message sent successfully
        """
        if self.state != FlexRayState.NORMAL_ACTIVE:
            print(f"Cannot send message in state {self.state}")
            return False
        
        # Validate message
        if not (FlexRayFrame.MIN_SLOT_ID <= message.slot_id <= FlexRayFrame.MAX_SLOT_ID):
            raise ValueError(f"Invalid slot ID: {message.slot_id}")
        
        if len(message.payload) > FlexRayFrame.MAX_PAYLOAD_LENGTH:
            raise ValueError(f"Payload too large: {len(message.payload)} bytes")
        
        # Convert to bytes and send
        frame_bytes = message.to_bytes()
        
        # TODO: Send to actual hardware
        print(f"Sending FlexRay message: Slot={message.slot_id}, Cycle={message.cycle_count}, "
              f"Channel={message.channel}, Length={len(message.payload)}")
        
        return True
    
    def receive_messages(self, timeout: float = 1.0) -> List[FlexRayMessage]:
        """
        Receive FlexRay messages
        
        Args:
            timeout: Receive timeout in seconds
            
        Returns:
            List of received messages
        """
        if self.state != FlexRayState.NORMAL_ACTIVE:
            return []
        
        messages = []
        
        # TODO: Receive from actual hardware
        # This is a placeholder for experimental hardware interface
        
        return messages
    
    def register_callback(self, callback: Callable[[FlexRayMessage], None]):
        """
        Register a callback for received messages
        
        Args:
            callback: Function to call when message received
        """
        self._message_callbacks.append(callback)
    
    def get_state(self) -> int:
        """Get current controller state"""
        return self.state
    
    def get_statistics(self) -> dict:
        """
        Get FlexRay communication statistics
        
        Returns:
            Dictionary with statistics
        """
        # TODO: Get from actual hardware
        return {
            'state': self.state,
            'cycle_count': 0,
            'tx_frames': 0,
            'rx_frames': 0,
            'errors': 0,
            'channel_a_active': True,
            'channel_b_active': True,
        }
    
    def reset(self) -> bool:
        """
        Reset the FlexRay controller
        
        Returns:
            True if reset successful
        """
        # TODO: Send reset command to hardware
        print("Resetting FlexRay controller")
        
        self.state = FlexRayState.DEFAULT_CONFIG
        self._running = False
        return True


class FlexRaySimulator:
    """
    FlexRay bus simulator for testing without hardware
    
    This can be used for development and testing of FlexRay applications
    without actual FlexRay hardware.
    """
    
    def __init__(self, config: Optional[FlexRayBusConfig] = None):
        """Initialize simulator"""
        self.config = config or FlexRayBusConfig()
        self.messages: List[FlexRayMessage] = []
        self.cycle_count = 0
        self.running = False
    
    def start(self):
        """Start simulation"""
        self.running = True
        self.cycle_count = 0
        print("FlexRay simulator started")
    
    def stop(self):
        """Stop simulation"""
        self.running = False
        print("FlexRay simulator stopped")
    
    def send_message(self, message: FlexRayMessage):
        """Add message to simulation"""
        self.messages.append(message)
    
    def get_messages(self) -> List[FlexRayMessage]:
        """Get all messages"""
        return self.messages.copy()
    
    def advance_cycle(self):
        """Advance to next communication cycle"""
        if self.running:
            self.cycle_count = (self.cycle_count + 1) % 64
