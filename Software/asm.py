##############################################################################
# File name:    asm.py
# Project:      Robotic Surgery Software
# Part:         Arduino Stepper Motor (ASM)
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file works in conjuction with asm.ino. It provides
#               functions to control the Arduino Stepper Motor.
##############################################################################


# Modules
import serial
import time
import serial.tools.list_ports


class ASM:
    def __init__(self):
        self.ino_command_gnm    = 'GNM'     # Get Name
        self.ino_command_mov    = 'MOV'     # Move    
        self.ino_command_gpo    = 'GPO'     # Get Position
        self.ino_command_gdl    = 'GDL'     # Get Delay
        self.ino_command_sdl    = 'SDL'     # Set Delay
        self.ino_status_name    = 'NME'     # Name
        self.ino_status_err     = 'ERR'     # Error
        self.ino_status_ok      = 'COK'     # Command OK
        self.ino_status_done    = 'DNE'     # Done
        self.name               = 'Arduino'  
        self.err_no_serial      = 'no serial port is found!\n'
        self.err_not_found      = 'asm is not found!\n'
        self.status_ok          = 0
        self.baud_rate          = 9600      # [bps]
        self.time_out           = 0.5       # [s]
        self.sleep_time         = 2         # [s]
        self.ser                = None
        self.position           = 0         # [steps], it starts at 0 and is added on top with MOV
        self.delay              = 0
        

    def initialize(self):
        # checking the ports and returning the relevant result if a device is/is not found          
        ports = serial.tools.list_ports.comports()
        if (len(ports) == 0):
            return self.err_no_serial
        for port in ports:
            if self.name in port.description:
                self.ser = serial.Serial(port=port.device, baudrate=self.baud_rate, timeout=self.time_out)
                time.sleep(self.sleep_time)
                return self.status_ok
        return self.err_not_found

    def close(self):
        self.ser.close()

    def write(self, data):
        self.ser.write(data.encode('utf-8'))
        self.ser.write('\n'.encode('utf-8'))
        self.ser.flushOutput()  # clearing the output buffer

    def read(self):
        return self.ser.readline().decode('utf-8')

    def getname(self):
        self.write(self.ino_command_gnm)
        return self.read()

    def move(self, steps):
        self.write(self.ino_command_mov + str(steps))
        flag = 1
        while (flag):
            if (self.ino_status_done in self.read()):
                flag = 0
    
    def get_position(self):
        self.write(self.ino_command_gpo)
        self.position = self.read()
        return self.position

    def get_delay(self):
        self.write(self.ino_command_gdl)
        self.delay = int(self.read())
        return self.delay

    def set_delay(self, delay):
        self.write(self.ino_command_sdl + str(delay))
        flag = 1
        while (flag):
            if (self.ino_status_done in self.read()):
                flag = 0


if __name__ == '__main__':
    import os
    asm = ASM()
    status = asm.initialize()
    if status != asm.status_ok:
        print('asm initialization failed with status: ' + str(status))
        os._exit(0)
    else:
        print('asm has been initialized.')
    asm.set_delay(3)
    asm.move(-300)
    print(asm.get_position())
    asm.close()