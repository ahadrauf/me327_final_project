import serial
import struct
import time

arduino = serial.Serial(port='COM15', baudrate=115200, timeout=.1)


def write_read(x):
    # arduino.write(bytes(x, 'utf-8'))
    # arduino.write(struct.pack('>BBBBBB', 0, 1, 2, 3, 4, 5))
    data = x.split(" ")
    data = [int(d) for d in data]
    arduino.write(struct.pack('>BBBBBB', data[0], data[1], data[2], data[3], data[4], data[5]))
    time.sleep(0.05)
    data = arduino.readline()
    return data


while True:
    num = input("Enter a number: ")  # Taking input from user
    value = write_read(num)
    print(value)  # printing the value
