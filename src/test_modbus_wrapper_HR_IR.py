from modbus_rtu_client import ModbusRtuClient, SerialConfig
from decoder import DataDecoder, DataType
import time
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    config = SerialConfig(port="COM9")
    modus_client = ModbusRtuClient(serial_config=config)
    
    # result = modus_client.read_discrete_inputs(address=1, count=1, slave_number=1)
    
    with modus_client as client:
        logger.info("Connected to Modbus RTU server")
        
        # resp = modus_client._client.report_slave_id(slave=20)
        # print(resp)
        
        # Read uint16 at address 3
        hr_value = client.read_holding_register(address=3, count=1)
        logger.info(f"HR[3] = {hr_value}")

        hr_uint32 = client.read_holding_register(address=4, count=2)
        if hr_uint32:
            logger.info(f"HR (uint32) = {hr_uint32}")
            value = DataDecoder.decode_registers(hr_uint32, data_type=DataType.UINT32)
            logger.info(f"value={value}")
            
        hr_uint32 = client.read_hr_uint32(address=4, slave_number=1)
        logger.info(f"Using client.read_uint32: value={hr_uint32}")
        
        hr_float = client.read_holding_register(address=6, count=2)
        if hr_float:
            logger.info(f"HR (float32) = {hr_float}")
            value = DataDecoder.decode_registers(hr_float, data_type=DataType.FLOAT32)
            logger.info(f"value={value}")    
        
        hr_string = client.read_holding_register(address=16, count=5)
        if hr_string:
            logger.info(f"HR (string) = {hr_string}")
            value = DataDecoder.decode_registers(hr_string, data_type=DataType.STRING)
            logger.info(f"value={value}")    
        


if __name__ == "__main__":
    main()
