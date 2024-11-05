from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


def decode_registers(registers: list, data_type: str) -> any:
    """
    Decode registers using pymodbus payload decoder
    
    Args:
        registers (list): List of registers to decode
        data_type (str): Type of data to decode ('uint32', 'float32', 'string')
    
    Returns:
        decoded value based on data_type
    """
    decoder = BinaryPayloadDecoder.fromRegisters(
        registers,
        byteorder=Endian.BIG,
        wordorder=Endian.BIG
    )
    
    if data_type == 'uint32':
        return decoder.decode_32bit_uint()
    elif data_type == 'float32':
        return decoder.decode_32bit_float()
    elif data_type == 'string':
        return decoder.decode_string(len(registers) * 2).decode('ascii').strip()
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
