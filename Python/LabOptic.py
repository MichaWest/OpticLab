
# from msilib import CreateRecord
# from pickle import NONE
import os
import sys
import platform
import tempfile
import re
import serial
import matplotlib.pyplot as plt
import json
import antaus.antaus as ant


file_path = "conf.json"

cur_dir = os.path.abspath(os.path.dirname(__file__))
ximc_dir = os.path.join(cur_dir, "ximc") 
ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
sys.path.append(ximc_package_dir)   
libdir = os.path.join(ximc_dir, "win64")
os.add_dll_directory(libdir)
try: 
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you changed the relative location of the test_Python.py and pyximc.py files. See developers' documentation for details.")
    exit()
except OSError as err:
    # print(err.errno, err.filename, err.strerror, err.winerror) # Allows you to display detailed information by mistake.
    if platform.system() == "Windows":
        if err.winerror == 193:   # The bit depth of one of the libraries bindy.dll, libximc.dll, xiwrapper.dll does not correspond to the operating system bit.
            print("Err: The bit depth of one of the libraries bindy.dll, libximc.dll, xiwrapper.dll does not correspond to the operating system bit.")
            # print(err)
        elif err.winerror == 126: # One of the library bindy.dll, libximc.dll, xiwrapper.dll files is missing.
            print("Err: One of the library bindy.dll, libximc.dll, xiwrapper.dll is missing.")
            print("It is also possible that one of the system libraries is missing. This problem is solved by installing the vcredist package from the ximc\\winXX folder.")
            # print(err)
        else:           # Other errors the value of which can be viewed in the code.
            print(err)
        print("Warning: If you are using the example as the basis for your module, make sure that the dependencies installed in the dependencies section of the example match your directory structure.")
        print("For correct work with the library you need: pyximc.py, bindy.dll, libximc.dll, xiwrapper.dll")
    else:
        print(err)
        print ("Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure that the architecture of the system and the interpreter is the same")
    exit()
print("Library libximc load")

def update_conf(object_name, name_of_data_change, new_value):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data_list = json.load(json_file)
    data_list[object_name][name_of_data_change] = new_value

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_list, json_file)


class Ximc:
    cord = ""       # cord.Position, cord.uPosition
    number = ""      # x - 0, z - 1, y - 2
    device_id = ""   # Значение необходимое для отправки команд устройству. Определяется в методе connect

    def get_position(self):
        if not  self.device_id is None: 
            print("\nRead position")
            cord = get_position_t()
            result = lib.get_position(self.device_id, byref(cord))
            print("Result: " + repr(result))
            if result == Result.Ok:
                print("Position: {0} steps, {1} microsteps".format(cord.Position, cord.uPosition))
            return cord.Position, cord.uPosition
        else:
            print("Device isn't connect")
    
    def __init__(self, i):
        self.number = i
        #self.cord = self.get_position()
 
    def get_dev_count(self, devenum):
        return lib.get_device_count(devenum)

    def connect(self):
        print("Hi")
        probe_flags = EnumerateFlags.ENUMERATE_PROBE + EnumerateFlags.ENUMERATE_NETWORK
        enum_hints = b"addr="
        devenum = lib.enumerate_devices(probe_flags, enum_hints)

        if len(sys.argv) > 1:
            open_name =  sys.argv[1]
        elif self.get_dev_count(devenum) > 0:
            open_name = lib.get_device_name(devenum, self.number)
        elif sys.version_info >= (3,0):
        # use URI for virtual device when there is new urllib python3 API
            tempdir = tempfile.gettempdir() + "/testdevice.bin"
            if os.altsep:
                tempdir = tempdir.replace(os.sep, os.altsep)
            # urlparse build wrong path if scheme is not file
            uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                    netloc=None, path=tempdir, params=None, query=None, fragment=None))
            open_name = re.sub(r'^file', 'xi-emu', uri).encode()
            print("The real controller is not found or busy with another app.")
            print("The virtual controller is opened to check the operation of the library.")
            print("If you want to open a real controller, connect it or close the application that uses it.")

        if not open_name:
            exit(1)

        if type(open_name) is str:
            open_name = open_name.encode()

        print("\nOpen device " + repr(open_name))

        self.device_id = lib.open_device(open_name)
        print("Device id: " + repr(self.device_id))

    def disconnect(self):
        if not self.device_id is None:
            print("\nClosing")
            lib.close_device(byref(cast(self.device_id, POINTER(c_int))))
            #lib.close_device(self.device_id, POINTER(c_int))
            self.device_id = None
            print("Done")
        else:
            print("Device isn't connect")

    def get_speed(self):
        if not self.device_id is None:
            print("\nGet speed")
            # Create move settings structure
            mvst  = move_settings_t()
            # Get current move settings from controller
            result = lib.get_move_settings(self.device_id, byref(mvst))
            # Print command return status. It will be 0 if all is OK
            print("Read command result: " + repr(result))   
            return mvst.Speed
        else:
            print("Device isn't connect")

    def set_speed(self, speed):
        if not  self.device_id is None:
            print("\nSet speed")
            # Create move settings structure
            mvst = move_settings_t()
            # Get current move settings from controller
            result = lib.get_move_settings(self.device_id, byref(mvst))
            # Print command return status. It will be 0 if all is OK
            print("Read command result: " + repr(result))
            print("The speed was equal to {0}. We will change it to {1}".format(mvst.Speed, speed))
            # Change current speed
            mvst.Speed = int(speed)
            # Write new move settings to controller
            result = lib.set_move_settings(self.device_id, byref(mvst))
            # Print command return status. It will be 0 if all is OK
            print("Write command result: " + repr(result)) 
        else:
            print("Device isn't connect")

    # distance [um]
    def move(self, distance, udistance):
        if not  self.device_id is None:
            print("\nGoing to {0} steps, {1} microsteps".format(distance, udistance))
            result = lib.command_move(self.device_id, distance, udistance)
            print("Result: " + repr(result))
        else:
            print("Device isn't connect")

    def info(self):
        if not  self.device_id is None:
            print("\nGet device info")
            x_device_information = device_information_t()
            result = lib.get_device_information(self.device_id, byref(x_device_information))
            print("Result: " + repr(result))
            if result == Result.Ok:
                print("Device information:")
                print(" Manufacturer: " +
                        repr(string_at(x_device_information.Manufacturer).decode()))
                print(" ManufacturerId: " +
                    repr(string_at(x_device_information.ManufacturerId).decode()))
                print(" ProductDescription: " +
                    repr(string_at(x_device_information.ProductDescription).decode()))
                print(" Major: " + repr(x_device_information.Major))
                print(" Minor: " + repr(x_device_information.Minor))
                print(" Release: " + repr(x_device_information.Release))
        else:
            print("Device isn't connect")

    def status(self):
        if not  self.device_id is None: 
            print("\nGet status")
            x_status = status_t()
            result = lib.get_status(self.device_id, byref(x_status))
            print("Result: " + repr(result))
            if result == Result.Ok:
                print("Status.Ipwr: " + repr(x_status.Ipwr))
                print("Status.Upwr: " + repr(x_status.Upwr))
                print("Status.Iusb: " + repr(x_status.Iusb))
                print("Status.Flags: " + repr(hex(x_status.Flags)))
        else:
            print("Device isn't connect")


class Pesa:
    number = None #x - 0, y - 1, z - 2
    com_port = 'COM7'  # Порт подключения. Узнать его можно: Диспетчер устройств -> Контроллеры USB
    cord = None   # Собственная координата
    ximc = None   # Объект класса Ximc, на которой стоит пеза. Важно: pesa.number=ximc.number

    def __init__(self, i):
        self.number = i
        self.cord = 0
        self.ximc = None

    def connect(self):
        with serial.Serial(port=self.com_port, baudrate=19200, xonxoff=True) as ser:
            command = 'setk,'+str(self.number)+',1\r'
            ser.write(command.encode()) 
            
    # step [um]
    def move(self, step):
        with serial.Serial(port=self.com_port, baudrate=19200, xonxoff=True) as ser:
            command = 'set,'+str(self.number)+','+str(step)+'\r'
            cord = 0
            cord = cord + step
            ser.write(command.encode())

    def disconnect(self):
        with serial.Serial(port=self.com_port, baudrate=19200, xonxoff=True) as ser:
            command = 'setk,'+str(self.number)+',0\r'
            ser.write(command.encode()) 

    def get_self_position(self):
        return self.cord

    def get_absolute_position(self):
        return self.cord+self.ximc.get_position()


class Antaus:
    power = 1
    freq_time = 1
    base_divider = 1
    name = 'Antaus'

    def schutter_open(self):
        ant.CONTROL(['SHUTTER', 1])

    def schutter_close(self):
        ant.CONTROL(['SHUTTER', 0])

    def set_power_trim(self, power):
        self.power = power
        ant.CONTROL(['POWER_TRIM', power])
        update_conf(self.name, 'power', power)
   
    def set_freq_time(self, freq_time):
        self.freq_time = freq_time
        ant.CONTROL(['OUT_DIVIDER', freq_time])
        update_conf(self.name, 'out_divider', freq_time)

    def get_power_trim(self):
        return self.power

    def get_freq_time(self):
        return self.freq_time

    def get_base_divider(self):
        return self.base_divider

    def set_base_divider(self, base_divider):
        self.base_divider = base_divider
        ant.CONTROL(['BASE_DIVIDER', base_divider])
        update_conf(self.name, 'base_divider', base_divider)



