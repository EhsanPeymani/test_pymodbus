from modbus_rtu_client import ModbusRtuClient, SerialConfig
from decoder import decode_registers
import time
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    config = SerialConfig(port="COM10")
    modus_client = ModbusRtuClient(serial_config=config)
    
    # result = modus_client.read_discrete_inputs(address=1, count=1, slave_number=1)
    
    with modus_client as client:
        logger.info("Connected to Modbus RTU server")
        
        # resp = modus_client._client.report_slave_id(slave=20)
        # print(resp)
        
        # Read uint16 at address 3
        hr_value = client.read_holding_registers(address=3, count=1)
        logger.info(f"HR[3] = {hr_value}")

        hr_uint32 = client.read_holding_registers(address=4, count=2)
        if hr_uint32:
            logger.info(f"HR (uint32) = {hr_uint32}")
            value = decode_registers(hr_uint32, data_type="uint32")
            logger.info(f"value={value}")
        
        hr_float = client.read_holding_registers(address=6, count=2)
        if hr_float:
            logger.info(f"HR (float32) = {hr_float}")
            value = decode_registers(hr_float, data_type="float32")
            logger.info(f"value={value}")    
        
        hr_string = client.read_holding_registers(address=16, count=5)
        if hr_string:
            logger.info(f"HR (string) = {hr_string}")
            value = decode_registers(hr_string, data_type="string")
            logger.info(f"value={value}")    
        


if __name__ == "__main__":
    main()
