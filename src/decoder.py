from typing import List, Any
from enum import Enum, auto
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pydantic import BaseModel, Field, NonNegativeInt, model_validator


class DataType(Enum):
    "All possible Modbus datatypes"
    BOOL = auto()
    UINT16 = auto()
    UINT32 = auto()
    UINT64 = auto()
    INT16 = auto()
    INT32 = auto()
    INT64 = auto()
    FLOAT32 = auto()
    FLOAT64 = auto()
    STRING = auto()


class RegisterCountParams(BaseModel):
    """Pydantic model for validating get_register_count parameters"""
    data_type: DataType = Field(..., frozen=True, validate_default=True)
    string_length: NonNegativeInt = Field(default=0, description="Length of string in characters (only for STRING type)")

    @model_validator(mode='after')
    def validate_string_params(self):
        """Validate string_length based on data_type"""
        if self.data_type == DataType.STRING and self.string_length == 0:
            raise ValueError("string_length must be provided for STRING data type")
        return self


class DataDecoder:
    """Helper class for decoding Modbus register values"""
    
    @staticmethod
    def get_register_count(data_type: DataType, string_length: int = 0) -> int:
        """
        Get number of registers needed for the data type
        
        Args:
            data_type (DataType): Type of data to decode
            string_length (int): Length of string in characters (only for STRING type)
            
        Returns:
            int: Number of registers needed
        """
        parmeters = RegisterCountParams(data_type=data_type, string_length=string_length)
        
        if parmeters.data_type == DataType.BOOL:
            return 1
        
        if parmeters.data_type in {DataType.UINT16, DataType.INT16}:
            return 1
        
        if parmeters.data_type in {DataType.UINT32, DataType.INT32, DataType.FLOAT32}:
            return 2
        
        if parmeters.data_type in {DataType.UINT64, DataType.INT64, DataType.FLOAT64}:
            return 4
        
        if parmeters.data_type == DataType.STRING:
            # 2 chars per register which is 2 bytes
            return (string_length + 1) // 2
        
        raise ValueError(f"Unsupported data type, got {parmeters.data_type}")
    
    @staticmethod
    def decode_registers(
        registers: List,
        data_type: DataType,
        byte_order: Endian = Endian.BIG,
        word_order: Endian = Endian.BIG
    ) -> Any:
        try:
            print(registers)
            decoder = BinaryPayloadDecoder.fromRegisters(
                registers,
                byteorder=byte_order,
                wordorder=word_order
            )
            
            if data_type == DataType.UINT16:
                return decoder.decode_16bit_uint()
            
            if data_type == DataType.INT16:
                return decoder.decode_16bit_int()
            
            if data_type == DataType.UINT32:
                return decoder.decode_32bit_uint()
            
            if data_type == DataType.INT32:
                return decoder.decode_32bit_int()
            
            if data_type == DataType.UINT64:
                return decoder.decode_64bit_uint()
            
            if data_type == DataType.INT64:
                return decoder.decode_64bit_int()
            
            if data_type == DataType.FLOAT32:
                return decoder.decode_32bit_float()
            
            if data_type == DataType.FLOAT64:
                return decoder.decode_64bit_float()
            
            if data_type == DataType.STRING:
                # Decode string and strip any padding
                return decoder.decode_string(len(registers) * 2).decode('ascii').strip()
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
        except Exception as e:
            raise ValueError(f"Error decoding {data_type}: {str(e)}")
