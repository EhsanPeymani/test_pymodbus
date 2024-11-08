from ast import Call
import logging
from typing import Any, Optional, List, Callable
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.pdu.pdu import ModbusPDU
from pymodbus.constants import Endian
from decoder import DataType, DataDecoder
from serial_config import SerialConfig


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
    def config(self) -> SerialConfig:
        """
        Get current client configuration

        Returns:
            SerialConfig: Current serial configuration
        """
        return self._config

    @property
    def connected(self) -> bool:
        """
        Check if the client is currently connected

        Returns:
            bool: True if connected, False otherwise
        """
        return (
            self._client is not None
            and self._client.connected
            and self._client.is_socket_open()
        )

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
                retries=self._config.retries,
            )
            return self._client.connect()
        except Exception as err:
            self._logger.error(
                f"Failed to connect to serial port {self._config.port}: {err}"
            )
            return False

    def disconnect(self) -> bool:
        """
        Safely disconnect from the Modbus server

        Returns:
            bool: True if disconnection was successful
        """
        try:
            if self._client and self.connected:
                self._client.close()
                return True
            return False
        except Exception as err:
            self._logger.error(f"Error during disconnect: {err}")
            return False

    def read_coils(
        self,
        address: int,
        count: int = 1,
        slave_number: int = 1,
        no_response_expected: bool = False,
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
            read_function=self._client.read_coils,
            address=address,
            count=count,
            slave_number=slave_number,
            no_response_expected=no_response_expected,
        )

    def read_discrete_inputs(
        self,
        address: int,
        count: int = 1,
        slave_number: int = 1,
        no_response_expected: bool = False,
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

        print("here")

        return self._read_bits(
            read_function=self._client.read_discrete_inputs,
            address=address,
            count=count,
            slave_number=slave_number,
            no_response_expected=no_response_expected,
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

    def _read_bits(
        self,
        read_function: Callable,
        address: int,
        count: int = 1,
        slave_number: int = 1,
        no_response_expected: bool = False,
    ) -> Optional[List[bool]]:
        """
        Generic method to read bits (coils or discrete inputs) from the Modbus server

        Args:
            read_function: Modbus client function to call
            address (int): Starting address
            count (int): Number of bits to read
            slave_number (int): Slave identifier
            no_response_expected (bool): The client will not expect a response to the request

        Returns:
            Optional[List[bool]]: List of bit values if successful, None if no response expected or on failure
        """
        # FIXIT slave_number shall come from pydantic to be between 1-247
        print("here")
        try:
            response = read_function(
                address=address,
                count=count,
                slave=slave_number,
                no_response_expected=no_response_expected,
            )
            print(response)

            if no_response_expected:
                return None

            if not self._validate_response(response):
                raise ModbusException(f"Invalid master response: {response}")
            return response.bits[:count]

        except ModbusException as err:
            self._logger.error(f"Failed to read {read_function.__name__}: {err}")
            raise err

    def _read_registers(
        self,
        read_function: Callable,
        address: int,
        count: int = 1,
        slave_number: int = 1,
        no_response_expected: bool = False,
    ) -> Optional[List[int]]:
        """
        Generic method to read registers (holding or input) from the Modbus server

        Args:
            read_function: Modbus client function to call
            address (int): Starting address
            count (int): Number of registers to read
            slave_number (int): Slave identifier
            no_response_expected (bool): The client will not expect a response to the request

        Returns:
            Optional[List[int]]: List of register values if successful, None if no response expected or on failure
        """
        try:
            response = read_function(
                address=address,
                count=count,
                slave=slave_number,
                no_response_expected=no_response_expected,
            )

            if no_response_expected:
                return None

            if not self._validate_response(response):
                raise ModbusException(f"Invalid master response: {response}")

            return response.registers[:count]

        except ModbusException as err:
            self._logger.error(f"Failed to read {read_function.__name__}: {err}")
            raise err

    def read_holding_register(
        self,
        address: int,
        count: int = 1,
        slave_number: int = 1,
        no_response_expected: bool = False,
    ) -> Optional[List[int]]:
        """
        Read holding registers from the Modbus server (code 0x03)

        Args:
            address (int): Starting address of holding registers
            count (int): Number of registers to read
            slave_number (int): Slave identifier
            no_response_expected (bool): The client will not expect a response to the request

        Returns:
            Optional[List[int]]: List of register values if successful, None if no response expected or on failure
        """
        if self._client is None:
            raise ModbusException("Modbus RTU client not initialized")

        return self._read_registers(
            read_function=self._client.read_holding_registers,
            address=address,
            count=count,
            slave_number=slave_number,
            no_response_expected=no_response_expected,
        )

    def read_input_register(
        self,
        address: int,
        count: int = 1,
        slave_number: int = 1,
        no_response_expected: bool = False,
    ) -> Optional[List[int]]:
        """
        Read input registers from the Modbus server (code 0x04)

        Args:
            address (int): Starting address of input registers
            count (int): Number of registers to read
            slave_number (int): Slave identifier
            no_response_expected (bool): The client will not expect a response to the request

        Returns:
            Optional[List[int]]: List of register values if successful, None if no response expected or on failure
        """
        if self._client is None:
            raise ModbusException("Modbus RTU client not initialized")

        return self._read_registers(
            read_function=self._client.read_input_registers,
            address=address,
            count=count,
            slave_number=slave_number,
            no_response_expected=no_response_expected,
        )

    def _read_register_value(
        self,
        read_function: Callable,
        address: int,
        data_type: DataType,
        slave_number: int,
        string_length: int,
        byte_order: Endian,
        word_order: Endian,
    ) -> Any:
        """
        # TODO Shall be updated
        Base function to read values from Modbus holding registers.
        This include decoding of the device response.

        Args:
            address (int): Register address to read from
            data_type (DataType): Type of data to read (UINT16, INT16, UINT32, etc.)
            slave_number (int): Slave device number, defaults to 1
            string_length (int): Length of string in characters (only for STRING type)

        Returns:
            Any: Decoded register value

        Raises:
            ModbusException: If response is None
        """
        count = DataDecoder.get_register_count(
            data_type=data_type, string_length=string_length
        )

        response = read_function(
            address=address, count=count, slave_number=slave_number
        )

        if response is None:
            raise ModbusException(
                f"Response from device is None but {data_type.name} is expected"
            )

        return DataDecoder.decode_registers(
            response, data_type=data_type, byte_order=byte_order, word_order=word_order
        )

    def _read_hr_value(
        self,
        address: int,
        data_type: DataType,
        slave_number: int = 1,
        string_length: int = 0,
        byte_order: Endian = Endian.BIG,
        word_order: Endian = Endian.BIG,
    ) -> Any:
        """
        TODO Shall be updated
        Base function to read values from Modbus holding registers.
        This include decoding of the device response.

        Args:
            address (int): Register address to read from
            data_type (DataType): Type of data to read (UINT16, INT16, UINT32, etc.)
            slave_number (int): Slave device number, defaults to 1
            string_length (int): Length of string in characters (only for STRING type)

        Returns:
            Any: Decoded register value

        Raises:
            ModbusException: If response is None
        """
        if self._client is None:
            raise ModbusException("Modbus RTU client not initialized")

        return self._read_register_value(
            read_function=self.read_holding_register,
            address=address,
            data_type=data_type,
            slave_number=slave_number,
            string_length=string_length,
            byte_order=byte_order,
            word_order=word_order,
        )

    def _read_ir_value(
        self,
        address: int,
        data_type: DataType,
        slave_number: int = 1,
        string_length: int = 0,
        byte_order: Endian = Endian.BIG,
        word_order: Endian = Endian.BIG,
    ) -> Any:
        """
        TODO Shall be updated
        Base function to read values from Modbus input registers.
        This include decoding of the device response.

        Args:
            address (int): Register address to read from
            data_type (DataType): Type of data to read (UINT16, INT16, UINT32, etc.)
            slave_number (int): Slave device number, defaults to 1
            string_length (int): Length of string in characters (only for STRING type)

        Returns:
            Any: Decoded register value

        Raises:
            ModbusException: If response is None
        """
        if self._client is None:
            raise ModbusException("Modbus RTU client not initialized")

        return self._read_register_value(
            read_function=self.read_input_register,
            address=address,
            data_type=data_type,
            slave_number=slave_number,
            string_length=string_length,
            byte_order=byte_order,
            word_order=word_order,
        )

    def read_hr_uint16(self, address: int, slave_number: int = 1) -> int:
        return self._read_hr_value(address, DataType.UINT16, slave_number)

    def read_hr_int16(self, address: int, slave_number: int = 1) -> int:
        return self._read_hr_value(address, DataType.INT16, slave_number)

    def read_hr_uint32(self, address: int, slave_number: int = 1) -> int:
        return self._read_hr_value(address, DataType.UINT32, slave_number)

    def read_hr_int32(self, address: int, slave_number: int = 1) -> int:
        return self._read_hr_value(address, DataType.INT32, slave_number)

    def read_hr_uint64(self, address: int, slave_number: int = 1) -> int:
        return self._read_hr_value(address, DataType.UINT64, slave_number)

    def read_hr_int64(self, address: int, slave_number: int = 1) -> int:
        return self._read_hr_value(address, DataType.INT64, slave_number)

    def read_hr_float32(self, address: int, slave_number: int = 1) -> float:
        return self._read_hr_value(address, DataType.FLOAT32, slave_number)

    def read_hr_float64(self, address: int, slave_number: int = 1) -> float:
        return self._read_hr_value(address, DataType.FLOAT64, slave_number)

    def read_hr_string(
        self, address: int, string_length: int, slave_number: int = 1
    ) -> str:
        return self._read_hr_value(
            address=address,
            data_type=DataType.STRING,
            slave_number=slave_number,
            string_length=string_length,
        )

    def read_ir_uint16(self, address: int, slave_number: int = 1) -> int:
        return self._read_ir_value(address, DataType.UINT16, slave_number)

    def read_ir_int16(self, address: int, slave_number: int = 1) -> int:
        return self._read_ir_value(address, DataType.INT16, slave_number)

    def read_ir_uint32(self, address: int, slave_number: int = 1) -> int:
        return self._read_ir_value(address, DataType.UINT32, slave_number)

    def read_ir_int32(self, address: int, slave_number: int = 1) -> int:
        return self._read_ir_value(address, DataType.INT32, slave_number)

    def read_ir_uint64(self, address: int, slave_number: int = 1) -> int:
        return self._read_ir_value(address, DataType.UINT64, slave_number)

    def read_ir_int64(self, address: int, slave_number: int = 1) -> int:
        return self._read_ir_value(address, DataType.INT64, slave_number)

    def read_ir_float32(self, address: int, slave_number: int = 1) -> float:
        return self._read_ir_value(address, DataType.FLOAT32, slave_number)

    def read_ir_float64(self, address: int, slave_number: int = 1) -> float:
        return self._read_ir_value(address, DataType.FLOAT64, slave_number)

    def read_ir_string(
        self, address: int, string_length: int, slave_number: int = 1
    ) -> str:
        return self._read_ir_value(
            address=address,
            data_type=DataType.STRING,
            slave_number=slave_number,
            string_length=string_length,
        )
