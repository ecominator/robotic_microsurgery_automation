##############################################################################
# File name:    gamepad.py
# Project:      Robotic Surgery Software
# Part:         Gamepad as the human-machine interface (HMI)
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file manges the communication between the gamepad 
#               and the software. 
##############################################################################


# modules
import ctypes.wintypes
import ctypes, ctypes.util
import math


# loading the XInput DLL
xinput_dll_names = ('XInput1_4.dll', 'XInput9_1_0.dll', 'XInput1_3.dll', 'XInput1_2.dll', 'XInput1_1.dll')
libXInput = None
for name in xinput_dll_names:
    found = ctypes.util.find_library(name)
    if found:
        libXInput = ctypes.WinDLL(found)
        break
if not libXInput:
    raise IOError('XInput library was not found.')


# XInputGamepad class inherits from a Structure class. 
class XInputGamepad(ctypes.Structure):           
    _fields_ = [                                
        ('wButtons', ctypes.wintypes.WORD),
        ('bLeftTrigger', ctypes.wintypes.BYTE),
        ('bRightTrigger', ctypes.wintypes.BYTE),
        ('sThumbLX', ctypes.wintypes.SHORT),
        ('sThumbLY', ctypes.wintypes.SHORT),
        ('sThumbRX', ctypes.wintypes.SHORT),
        ('sThumbRY', ctypes.wintypes.SHORT)
    ]


# XInputState class represents the controller state
class XInputState(ctypes.Structure):                    
    _fields_ = [
        ('dwPacketNumber', ctypes.wintypes.DWORD),      # dwPacketNumber indicates that the state might have changed.
        ('Gamepad', XInputGamepad),
    ]


class XInput:
    def __init__(self):
        self.max_trigger_value = math.pow(2, 8)
        self.max_stick_value = math.pow(2, 15)
        self.gamepad_num = 0
        self.state = XInputState()
        self.previous_state = None
        self.gamepad = self.state.Gamepad

    def get_state(self):
        self.previous_state = self.state.dwPacketNumber
        result = libXInput.XInputGetState(ctypes.wintypes.WORD(self.gamepad_num), ctypes.pointer(self.state))
        return result

    def is_button_pressed(self, button):
        return bool(button & self.gamepad.wButtons)

    def get_axis_value(self, axis):
        return getattr(self.gamepad, axis)

    def get_trigger_value(self, trigger):
        # the returned value for triggers is in range of -128 to 127.
        # the 0xFF hexadecimal is 255 decimal. 
        return (self.get_axis_value(trigger) & 0xFF) / self.max_trigger_value

    def get_stick_value(self, thumb):
        return self.get_axis_value(thumb) / self.max_stick_value
