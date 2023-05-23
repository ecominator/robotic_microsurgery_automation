##############################################################################
# File name:    pistage.py
# Project:      Robotic Surgery Software
# Part:         PIStage positioning axes
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file handles the PIStage positioning axes and controls
#               their movements. 
##############################################################################


# Modules
from pipython import GCSDevice
from pipython import pitools
import time


class PIStage:
    def __init__(self):
        self.sleep_time         = 1     # [s]
        self.err_check          = True
        self.err_not_found      = 'pi device is not found!\n'
        self.status_ok          = 0
        self.device             = GCSDevice('C-884')
        self.referencing_status = None
        
    def initialize(self):
        self.device.errcheck = self.err_check
        time.sleep(self.sleep_time)
        devices = self.device.EnumerateUSB(mask='C-884')  
        time.sleep(self.sleep_time)
        if len(devices) == 0:
            return self.err_not_found
        self.device.ConnectUSB(devices[0])
        time.sleep(self.sleep_time)
        return self.status_ok
        
    def close(self):
        self.device.CloseConnection()

    def get_axis_position(self, axis):
        pos = self.device.qPOS(axis)
        return pos[axis]            # pos is an OrderedDict: OrderedDict([(axis, value)])

    def get_axis_velocity(self, axis):
        velocity = self.device.qVEL(axis)
        return velocity[axis]       # velocity is an OrderedDict: OrderedDict([(axis, value)])

    def set_axis_velocity(self, axis, velocity):
        self.device.VEL(axis, velocity)

    def get_axis_acceleration(self, axis):
        acceleration = self.device.qACC(axis)
        return acceleration[axis]   # acceleration is an OrderedDict: OrderedDict([(axis, value)])

    def set_axis_acceleration(self, axis, acceleration):
        self.device.ACC(axis, acceleration)

    def get_axis_deceleration(self, axis):
        deceleration = self.device.qDEC(axis)
        return deceleration[axis]   # deceleration is an OrderedDict: OrderedDict([(axis, value)])

    def set_axis_deceleration(self, axis, deceleration):
        self.device.DEC(axis, deceleration)

    def get_referencing_status(self):
        return self.referencing_status

    def set_referencing_status(self, status):
        self.referencing_status = status

    def is_axis_referenced(self, axis):
        referencing_status = self.device.qFRF()
        return referencing_status[str(axis)]

    def reference_axis(self, axis):
        self.device.SVO(axis, 1)
        self.device.FRF(axis)
        pitools.waitontarget(self.device, axis)
        referencing_status = self.device.qFRF()
        return referencing_status[str(axis)] 
    
    def move_axis(self, axis, movement, speed):
        self.set_axis_velocity(axis, speed)
        self.device.MVR(axis, movement)
        pitools.waitontarget(self.device, axis)

    def move_axis_to_position(self, axis, position, speed):
        self.set_axis_velocity(axis, speed)
        self.device.MOV(axis, position)
        pitools.waitontarget(self.device, axis)

    def stop(self):
        try:
            self.device.STP()
        except:
            return
        else:
            return
    
    def stop_axis(self, axis):
        try:
            self.device.HLT(axis)
        except:
            return
        else:
            return


if __name__ == '__main__':
    import os
    pistage = PIStage()
    status = pistage.initialize()
    if status != pistage.status_ok:
        print('pistage initialization failed with status: ' + str(status))
        os._exit(0)
    else:
        print('pistage has been initialized.')
    status = pistage.reference_axis(1)
    status = pistage.reference_axis(2)
    print(pistage.get_axis_position(1))
    pistage.move_axis(1, 10, 4)
    print(pistage.get_axis_position(1))
    pistage.device.MVR(1, 30)
    print(pistage.get_axis_position(1))
    try:
        pistage.device.STP()
        # pistage.device.HLT(1)
        # pistage.device.MVR(1, 0)
    except:
        print('failed')
        print(pistage.get_axis_position(1))
    else:
        print('succeeded')
    pistage.move_axis(1, -10, 4)
    print(pistage.get_axis_position(1))
    pistage.close()
