import logging
import pymodbus
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Union
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.pdu.pdu import ModbusPDU


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

    def disconnect(self) -> None:
        """Close the Modbus RTU connection"""
        if self._client and self.connected:
            self._client.close()
            
    def read_coils(
        self, 
        address: int, 
        count: int = 1, 
        slave_number: int = 1,
        no_response_expected: bool = False
    ) -> Optional[List[bool]]:
        """
        Read coils from the Modbus server (code 0x01)
        
        Args:
            address (int): Starting address of coils
            count (int): Number of coils to read
            slave_number (int): Slave identifier
            no_response_expected (bool): The client will not expect a response to the request
            
        Returns:
            Optional[List[bool]]: List of coil values if successful, None if no response expected or on failure
        """
        # FIXIT slave_number shall come from pydantic to be between 1-247
        if not self.connected:
            self._logger.error("Cannot read coils: Client is not connected")
            return None
            
        try:
            if self._client is None:
                return None

            response = self._client.read_coils(
                address=address,
                count=count,
                slave=slave_number,
                no_response_expected=no_response_expected
            )

            if no_response_expected:
                return None

            if not self._validate_response(response):
                message = f"Invalid master response: {response}"
                raise ModbusException(message)
                
            return response.bits[:count]
            
        except ModbusException as err:
            self._logger.error(f"Failed to read coils: {err}")
            return None

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def _validate_response(self, response: ModbusPDU) -> bool:
        """
        Validate the Modbus response
        
        Args:
            response: Response from Modbus server
            
        Returns:
            bool: True if response is not a modbus exception, False otherwise
        """
        if response is None:
            # FIXIT I do not think it can None at any time
            self._logger.error("No response received from server")
            return False
        
        if isinstance(response, ExceptionResponse):
            return False
            
        return True
