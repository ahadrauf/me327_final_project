import serial
import struct
from enum import Enum


class DriveMode(Enum):
    Directional = 1
    Adirectional = 2
    Cycle = 3
    Off = 4


def generate_arduino(com_port: str, baudrate: int = 115200, timeout: float = 0.1) -> serial.Serial:
    return serial.Serial(port=com_port, baudrate=baudrate, timeout=timeout)


def write_three_numbers(arduino: serial.Serial, num1: int, num2: int, num3: int) -> None:
    arduino.write(struct.pack('>BBB', num1, num2, num3))


def write_four_numbers(arduino: serial.Serial, num1: int, num2: int, num3: int, num4: int) -> None:
    arduino.write(struct.pack('>BBBB', num1, num2, num3, num4))


if __name__ == "__main__":
    arduino = generate_arduino("COM10")
    # write_four_numbers(arduino, DriveMode.Cycle.value, 0, 0, int(0.8*255))
    write_four_numbers(arduino, DriveMode.Off.value, 0, 0, 0)

