from pymodbus.client import ModbusSerialClient
from pymodbus.pdu import ExceptionResponse
import time


def test_coils(client):
    # Test reading individual coils
    print("\nReading individual coils:")
    coil_addresses = [0, 1]

    for addr in coil_addresses:
        print(f"\nReading coil at address {addr}:")
        try:
            result = client.read_discrete_inputs(addr, 1, slave=1)
            if isinstance(result, ExceptionResponse):
                print(f"Exception Code: {result.exception_code}")
                print(f"Exception Code: {result}")
                print(f"Exception Code: {result.isError()}")
            elif result.isError():
                print(f"Error: {result}")
            else:
                print(f"Value: {result.bits[0]}")
        except Exception as e:
            print(f"Exception: {str(e)}")
        time.sleep(0.1)

def main():
    client = ModbusSerialClient(
        port='COM10',
        baudrate=9600,
        parity='N',
        stopbits=1,
        bytesize=8,
        timeout=3,
    )

    if client.connect():
        print("Connected to COM10")
        test_coils(client)
        client.close()
    else:
        print("Failed to connect!")


if __name__ == "__main__":
    main()
