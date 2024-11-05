from pymodbus.client import ModbusSerialClient
from modbus_rtu_client import ModbusRtuClient, SerialConfig
import time


def main():
    config = SerialConfig(port="COM10")
    modus_client = ModbusRtuClient(serial_config=config)
    
    with modus_client as client:
        coil_addresses = [0, 1, 20000]

        for addr in coil_addresses:
            print(f"\nReading coil at address {addr}:")
            try:
                result = client.read_discrete_inputs(address=addr, count=1, slave_number=1)
                print(f"Value: {result[0] if result is not None else "NONE"}")
            except Exception as e:
                print(f"Exception: {str(e)}")
            time.sleep(0.1)


if __name__ == "__main__":
    main()
