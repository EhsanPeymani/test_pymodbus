from pymodbus.client import ModbusSerialClient
from pymodbus.pdu import ExceptionResponse
import time


def test_coils(client):
    # Test reading individual coils
    print("\nReading individual coils:")
    coil_addresses = [0, 1, 2]

    for addr in coil_addresses:
        print(f"\nReading coil at address {addr}:")
        try:
            result = client.read_discrete_inputs(addr, 1, slave=1)
            if isinstance(result, ExceptionResponse):
                print(f"Exception Code: {result.exception_code}")
            elif result.isError():
                print(f"Error: {result}")
            else:
                print(f"Value: {result.bits[0]}")
        except Exception as e:
            print(f"Exception: {str(e)}")
        time.sleep(0.1)

    # Test reading multiple coils at once
    print("\nReading multiple coils (addresses 0-2):")
    try:
        result = client.read_coils(0, 3, slave=1)
        if isinstance(result, ExceptionResponse):
            print(f"Exception Code: {result.exception_code}")
        elif result.isError():
            print(f"Error: {result}")
        else:
            print(f"Values: {result.bits[0:3]}")
    except Exception as e:
        print(f"Exception: {str(e)}")

    # Test writing to coils
    print("\nWriting to coils:")
    test_writes = [
        (0, True),  # Turn OFF coil 0
        (1, False),   # Turn ON coil 1
        (2, True)    # Turn ON coil 2
    ]

    for addr, value in test_writes:
        print(f"\nWriting {value} to coil {addr}:")
        try:
            write_result = client.write_coil(addr, value, slave=1)
            if isinstance(write_result, ExceptionResponse):
                print(f"Write Exception Code: {write_result.exception_code}")
            elif write_result.isError():
                print(f"Write Error: {write_result}")
            else:
                print("Write successful!")

                # Read back the value
                time.sleep(0.1)
                read_result = client.read_coils(addr, 1, slave=1)
                if not read_result.isError():
                    print(f"Read back value: {read_result.bits[0]}")

        except Exception as e:
            print(f"Write Exception: {str(e)}")
        time.sleep(0.1)

    # # Test writing multiple coils at once
    # print("\nWriting multiple coils at once (addresses 0-2):")
    # try:
    #     values = [True, False, True]  # Values for coils 0, 1, and 2
    #     write_result = client.write_coils(0, values, slave=1)
    #     if isinstance(write_result, ExceptionResponse):
    #         print(f"Write Exception Code: {write_result.exception_code}")
    #     elif write_result.isError():
    #         print(f"Write Error: {write_result}")
    #     else:
    #         print("Multiple write successful!")

    #         # Read back all values
    #         time.sleep(0.1)
    #         read_result = client.read_coils(0, 3, slave=1)
    #         if not read_result.isError():
    #             print(f"Read back values: {read_result.bits}")

    # except Exception as e:
    #     print(f"Multiple Write Exception: {str(e)}")


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
