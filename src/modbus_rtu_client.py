import logging
import pymodbus
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Union
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse


class BaudRate(Enum):
    BAUD_9600 = 9600
    BAUD_19200 = 19200
    BAUD_38400 = 38400
    BAUD_57600 = 57600
    BAUD_115200 = 115200


@dataclass
class SerialConfig:
    """Configuration data class for serial connection parameters

    Attributes:
        port: Serial port used for communication.
        baudrate: Bits per second - based on BaudRate
        bytesize: Number of bits per byte 7-8.
        parity: ‘E’ven, ‘O’dd or ‘N’one
        stopbits: Number of stop bits 0-2.
        timeout: Timeout for connecting and receiving data, in seconds.
        retries: Max number of retries per request.
    """
    port: str
    baudrate: int = BaudRate.BAUD_9600.value
    bytesize: int = 8
    parity: str = 'N'
    stopbits: int = 1
    timeout: float = 3
    retries: int = 3


class ModbusRTUClient:
    """
    A class to handle ModbusRTU client communications over serial connection.
    """

    def __init__(self, serial_config: SerialConfig):
        """
        Initialize ModbusRTU client with serial configuration
        """
        self._config = serial_config
        self._client = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def connect(self) -> bool:
        """
        Establish connection to Modbus RTU server

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self._client = ModbusSerialClient(
                framer=pymodbus.FramerType.RTU,
                port=self._config.port,
                baudrate=self._config.baudrate,
                bytesize=self._config.bytesize,
                parity=self._config.parity,
                stopbits=self._config.stopbits,
                timeout=self._config.timeout,
                retries=self._config.retries
            )
            return self._client.connect()
        except Exception as err:
            self._logger.error(f"Failed to connect to serial port {self._config.port}: {err}")
            return False
    
    @property
    def connected(self) -> bool:
        """
        Check if the client is currently connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        return (self._client is not None and
                self._client.connected and 
                self._client.is_socket_open())

    def disconnect(self) -> None:
        """Close the Modbus RTU connection"""
        if self._client and self._client.is_socket_open():
            self._client.close()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def _validate_response(self, response: Union[ExceptionResponse, None]) -> bool:
        """
        Validate the Modbus response
        
        Args:
            response: Response from Modbus server
            
        Returns:
            bool: True if response is valid, False otherwise
        """
        if response is None:
            self._logger.error("No response received from server")
            return False
        
        if isinstance(response, ExceptionResponse):
            self._logger.error(f"Received exception response: {response}")
            return False
            
        return True
