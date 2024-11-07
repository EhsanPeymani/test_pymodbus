from enum import Enum
from typing import Annotated, Literal
from pydantic import BaseModel, Field, field_validator


class BaudRate(Enum):
    BAUD_9600 = 9600
    BAUD_19200 = 19200
    BAUD_38400 = 38400
    BAUD_57600 = 57600
    BAUD_115200 = 115200


class SerialConfig(BaseModel):
    """Configuration class for serial connection parameters

    Attributes:
        port: Serial port used for communication
        baudrate: Bits per second - must be a valid BaudRate value
        bytesize: Number of bits per byte 7-8
        parity: ‘E’ven, ‘O’dd or ‘N’one (Use E, N or O)
        stopbits: Number of stop bits (1 or 2)
        timeout: Timeout for connecting and receiving data, in seconds, must be positive
        retries: Max number of retries per request, must be positive
    """

    port: Annotated[
        str, Field(description="Serial port path (e.g., /dev/ttyUSB0 or COM1)")
    ]

    baudrate: Annotated[
        int,
        Field(
            default=BaudRate.BAUD_9600.value,
            description="Communication speed in bits per second",
        ),
    ]

    bytesize: Annotated[
        Literal[7, 8], Field(default=8, description="Number of bits per byte")
    ]

    parity: Annotated[
        Literal["E", "O", "N"],
        Field(default="N", description="Parity checking mode: Even, Odd, or None"),
    ]

    stopbits: Annotated[
        Literal[1, 2], Field(default=1, description="Number of stop bits")
    ]

    timeout: Annotated[
        float, Field(default=3.0, gt=0, description="Timeout duration in seconds")
    ]

    retries: Annotated[
        int, Field(default=3, gt=0, description="Maximum number of retry attempts")
    ]

    model_config = {"frozen": True}

    @field_validator("baudrate")
    @classmethod
    def validate_baudrate(cls, v: int) -> int:
        valid_baudrates = {rate.value for rate in BaudRate}
        if v not in valid_baudrates:
            raise ValueError(f"Baudrate must be one of {valid_baudrates}")
        return v
