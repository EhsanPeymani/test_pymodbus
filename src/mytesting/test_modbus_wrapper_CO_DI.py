from modbus_rtu_client import ModbusRtuClient
from serial_config import SerialConfig
import time
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line: %(lineno)d'
)
logger = logging.getLogger(__name__)


def main():
    config = SerialConfig(port="COM10")
    modus_client = ModbusRtuClient(serial_config=config)
    
    with modus_client as client:
        coil_addresses = [0]

        for addr in coil_addresses:
            print(f"\nReading coil at address {addr}:")
            try:
                result = client.read_discrete_inputs(address=addr, count=2, slave_number=1)
                print(f"Value: {result if result is not None else "NONE"}")
            except Exception as e:
                print(f"Exception: {str(e)}")
            time.sleep(0.1)


if __name__ == "__main__":
    main()
