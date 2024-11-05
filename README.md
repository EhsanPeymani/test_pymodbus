# test_pymodbus

## Objective

To get to know modbus RTU and experiement building a client

## Setup
I am using Windows 11.

`python -m venv venv`

On Windows, activate it `venv\Scripts\activate`

Upgrade pip `python -m pip install --upgrade pip`

## Setup and Use of PyModbus Simulator
PyModbus built-in simulator simulates a Modbus device (server, slave).

Install `Com0Com` to have virtual com port
Make sure that 2 connected ports are installed on your system.

Optional: Install `PuTTY` to see messages on virtual ports

Build a json file to configure the simulator. 

```bash
usage: pymodbus.simulator [-h] [--modbus_server MODBUS_SERVER] [--modbus_device MODBUS_DEVICE] [--http_host HTTP_HOST] [--http_port HTTP_PORT] [--log {critical,error,warning,info,debug}] [--json_file JSON_FILE] [--log_file LOG_FILE]
                          [--custom_actions_module CUSTOM_ACTIONS_MODULE]

Modbus server with REST-API and web server

options:
  -h, --help            show this help message and exit
  --modbus_server MODBUS_SERVER
                        use <modbus_server> from server_list in json file
  --modbus_device MODBUS_DEVICE
                        use <modbus_device> from device_list in json file
  --http_host HTTP_HOST
                        use <http_host> as host to bind http listen
  --http_port HTTP_PORT
                        use <http_port> as port to bind http listen
  --log {critical,error,warning,info,debug}
                        set log level, default is info
  --json_file JSON_FILE
                        name of json file, default is "setup.json"
  --log_file LOG_FILE   name of server log file, default is "server.log"
  --custom_actions_module CUSTOM_ACTIONS_MODULE
                        python file with custom actions, default is none
```

Run it as 
```bash
pymodbus.simulator --modbus_server server_rtu --modbus_device device --json_file sim_setting.json
```

### Notes
Documentation is inaccurate, and the configuration for CO and DI shall follow these:

- Coils are binary (only 0 or 1, True or False)
- Use low addresses (starting from 0)
- Make sure addresses are in the "write" list if you want to write to them
- With "shared blocks": true, a coil at address 0 can be read as either:
  - Coil (Function Code 01)
  - Discrete Input (Function Code 02)
  - Same value will be returned by both

Still, I have a lot of problem with CO and DI. This is my discovery:
- The initial configuration value ({"addr": 1, "value": 1}) isn't being applied correctly
- However, the simulator is maintaining state between runs - values written to coils persist
- You can still write to coil 1 even when it's not in the "write" list. This suggests that the "write" list in the simulator might only be enforced for registers (uint16, uint32, etc.) and not for coils.

### isError() and isinstance(result, ExceptionResponse)
It returns True when response function code is greater than `0x80` (128 in decimal).

In Modbus protocol, when a function code is greater than 0x80 (128 in decimal), it indicates an exception response. 

When an error occurs, the slave device responds by:
- Taking the original function code
- Adding 0x80 to it to set the most significant bit

For example:
- Normal Read Holding Registers: 0x03
- Exception for Read Holding Registers: 0x83 (0x03 + 0x80)

Therefore, when `resp.isError() == True`, `isinstance(resp, ExceptionResponse) == True`

An exception response is sent by a slave device when it cannot fulfill a request. For example:
- Invalid function code
- Invalid register address
- Invalid data value
- Device failure

### client.connected vs client.is_socket_open()
`client.connected` is a property that indicates whether the client is currently in a connected state
It represents the overall connection status of the ModbusSerialClient
It's more about the logical connection state

`client.is_socket_open()` method specifically checks if the underlying serial port/socket is actually open and available for communication. It performs a physical check of the connection.
Returns True if the serial port is open and ready for communication, False otherwise
This is more of a hardware-level check.

The key difference is that `connected` is a status property tracking the intended/logical connection state, while `is_socket_open()` actively checks the physical connection status.
For robust error handling, it's good practice to check both since they could potentially be in different states.