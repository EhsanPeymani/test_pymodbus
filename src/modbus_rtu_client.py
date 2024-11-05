import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Callable
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


class ModbusRtuClient:
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
        if self._client and self.connected:
            self._client.close()

    def _read_bits(
        self,
        function_name: str, 
        read_function: Callable, 
        address: int, 
        count: int = 1, 
        slave_number: int = 1, 
        no_response_expected: bool = False
    ) -> Optional[List[bool]]:
        """
        Generic method to read bits (coils or discrete inputs) from the Modbus server

        Args:
            function_name: Name of the function for logging
            read_function: Modbus client function to call
            address (int): Starting address
            count (int): Number of bits to read
            slave_number (int): Slave identifier
            no_response_expected (bool): The client will not expect a response to the request

        Returns:
            Optional[List[bool]]: List of bit values if successful, None if no response expected or on failure
        """
        # FIXIT slave_number shall come from pydantic to be between 1-247
        try:
            response = read_function(
                address=address,
                count=count,
                slave=slave_number,
                no_response_expected=no_response_expected
            )

            if no_response_expected:
                return None

            if not self._validate_response(response):
                raise ModbusException(f"Invalid master response: {response}")

            return response.bits[:count]

        except ModbusException as err:
            self._logger.error(f"Failed to read {function_name}: {err}")
            raise err

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
        if self._client is None:
            raise ModbusException("Modbus RTU client not initialized")
        
        return self._read_bits(
            function_name="coils",
            read_function=self._client.read_coils,
            address=address,
            count=count,
            slave_number=slave_number,
            no_response_expected=no_response_expected)

    def read_discrete_inputs(
        self, 
        address: int, 
        count: int = 1, 
        slave_number: int = 1,
        no_response_expected: bool = False
    ) -> Optional[List[bool]]:
        """
        Read discrete inputs from the Modbus server (code 0x02)

        Args:
            address (int): Starting address of discrete inputs
            count (int): Number of discrete inputs to read
            slave_number (int): Slave identifier
            no_response_expected (bool): The client will not expect a response to the request

        Returns:
            Optional[List[bool]]: List of discrete input values if successful, None if no response expected or on failure
        """
        if self._client is None:
            raise ModbusException("Modbus RTU client not initialized")
        
        return self._read_bits(
            function_name="discrete inputs",
            read_function=self._client.read_discrete_inputs,
            address=address,
            count=count,
            slave_number=slave_number,
            no_response_expected=no_response_expected
        )

    def __enter__(self):
        """Context manager entry"""
        if not self.connect():
            raise ModbusException("Failed to connect to Modbus device")
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
