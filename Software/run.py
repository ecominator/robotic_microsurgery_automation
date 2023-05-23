
##############################################################################
# File name:    run.py
# Project:      Robotic Surgery Software
# Part:         Running the software (gui)
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file is responsible for initializing all the
#               necessary modules and running the software.
##############################################################################


# Modules
from configuration import Configuration
from SmarAct import SmarAct
from pistage import PIStage
from asm import ASM
from gamepad import XInput
from pypylon import pylon
from gui import GUI
from PyQt5.QtWidgets import QApplication
import sys
import os


if __name__ == '__main__':
    config = Configuration()
    # initializing smaract
    smaract = SmarAct()
    status = smaract.initialize()
    if status != config.smaract_status_ok:
        print('smaract initialization failed with status: ' + str(status))
        os._exit(0)
    else:
        print('smaract has been initialized.')
     # initializing asm
    asm = ASM()
    status = asm.initialize()
    if status != asm.status_ok:
        print('asm initialization failed with status: ' + str(status))
        os._exit(0)
    else:
        print('asm has been initialized.')
    asm.set_delay(config.asm_delay_ms)
    # initializing pistage
    pistage = PIStage()
    status = pistage.initialize()
    if status != pistage.status_ok:
        print('pistage initialization failed with status: ' + str(status))
        os._exit(0)
    else:
        print('pistage has been initialized.')
    # initializing gamepad
    gamepad = XInput()
    # initializing camera
    tl = pylon.TlFactory.GetInstance()
    camera = pylon.InstantCamera()
    camera.Attach(tl.CreateFirstDevice())
    # running the gui
    app = QApplication([])
    screen = app.screens()[0]
    ppi = screen.physicalDotsPerInchX()
    gui = GUI(smaract=smaract, asm=asm, pistage=pistage, gamepad=gamepad, camera=camera, config=config, ppi=ppi)
    gui.show()
    sys.exit(app.exec_())
