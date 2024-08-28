import serial
import matplotlib.pyplot as plt

class Pesa:
    number = None  # x - 0, y - 1, z - 2
    com_port = 'COM7'  # Порт подключения. Узнать его можно: Диспетчер устройств -> Контроллеры USB
    cord = None  # Собственная координата
    ximc = None  # Объект класса Ximc, на которой стоит пеза. Важно: pesa.number=ximc.number

    def __init__(self, i):
        self.number = i
        self.cord = 0
        self.ximc = None

    def connect(self):
        with serial.Serial(port=self.com_port, baudrate=19200, xonxoff=True) as ser:
            command = 'setk,' + str(self.number) + ',1\r'
            ser.write(command.encode())

            # step [um]

    def move(self, step):
        with serial.Serial(port=self.com_port, baudrate=19200, xonxoff=True) as ser:
            command = 'set,' + str(self.number) + ',' + str(step) + '\r'
            self.cord = 0
            self.cord = self.cord + step
            ser.write(command.encode())

    def disconnect(self):
        with serial.Serial(port=self.com_port, baudrate=19200, xonxoff=True) as ser:
            command = 'setk,' + str(self.number) + ',0\r'
            ser.write(command.encode())

    def get_self_position(self):
        return self.cord

    def get_absolute_position(self):
        return self.cord + self.ximc.get_position()