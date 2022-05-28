import serial
import struct


def generate_arduino(com_port: str, baudrate: int = 115200, timeout: float = 0.1) -> serial.Serial:
    return serial.Serial(port=com_port, baudrate=baudrate, timeout=timeout)


def write_three_numbers(arduino: serial.Serial, num1: int, num2: int, num3: int) -> None:
    arduino.write(struct.pack('>BBB', num1, num2, num3))
