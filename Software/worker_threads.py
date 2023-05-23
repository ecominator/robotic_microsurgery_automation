##############################################################################
# File name:    worker_threads.py
# Project:      Robotic Surgery Software
# Part:         Threads
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file contains the worker threads that run in parallel
#               with the GUI thread.   
##############################################################################


# Modules
import auxiliary as aux
import computer_vision as vision
from pypylon import pylon
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot
import numpy as np
import cv2 as cv
import time


class WorkerSignalsCamera(QObject):
    '''
    defining the signals available from the camera worker thread
    '''

    progress = pyqtSignal()


class WorkerCamera(QRunnable):
    '''
    worker thread for camera
    '''

    def __init__(self, camera, config):
        super().__init__()
        self.camera = camera
        self.config = config
        # establishing the communication with the camera
        self.camera.Open()
        # setting the camera settings
        self.camera.MaxNumBuffer.SetValue(self.config.camera_buffer)
        self.camera.PixelFormat.SetValue(self.config.camera_pixel_format)
        self.camera.ExposureTime.SetValue(self.config.camera_exposure_time)
        self.camera.Width.SetValue(self.config.camera_width)
        self.camera.Height.SetValue(self.config.camera_height)
        self.camera.OffsetX.SetValue(self.config.camera_offset_x)
        self.camera.OffsetY.SetValue(self.config.camera_offset_y)
        self.camera.ReverseX.SetValue(self.config.camera_reverse_x)
        self.camera.ReverseY.SetValue(self.config.camera_reverse_y)
        self.signals = WorkerSignalsCamera()	
    
    @pyqtSlot()
    def run(self):
        '''
        this function is called when the camera thread is started.
        '''

        # When one StartGrabbing with a single integer argument, one tells Pylon the number of frames one want to acquire.
        # When the camera reaches that number of frames, it will stop acquiring new ones.
        self.camera.StartGrabbing(1)
        while True:
            if self.config.camera_flag_off:   
                return
            # retrieving the result using a timeout of CAMERA_TIMEOUT_MS
            # Specifying that if CAMERA_TIMEOUT_MS pass and there is no result, simply return. 
            # Another option would have been using TimeoutHandling_ThrowException.
            grab = self.camera.RetrieveResult(self.config.camera_timeout_ms, pylon.TimeoutHandling_Return) 
            # Checking that the grab actually worked by using the GrabSucceeded method. grab is True only when the RetrieveResult did not timeout.
            if grab and grab.GrabSucceeded():
                # We get the actual data (numpy array) using the GetArray method. 
                self.config.camera_image = grab.GetArray()
                grab.Release()
                self.signals.progress.emit()
            time.sleep(self.config.camera_sleep_time_s)


class WorkerSignalsSmarActReferencing(QObject):
    '''
    defining the signals available from the smaract referencing worker thread
    '''

    progress = pyqtSignal(int)


class WorkerSmarActReferencing(QRunnable):
    '''
    worker thread for smaract referencing
    '''

    def __init__(self, smaract, config):
        super().__init__()
        self.smaract = smaract
        self.config = config
        self.signals = WorkerSignalsSmarActReferencing()

    @pyqtSlot()
    def run(self):
        '''
        this function is called when the smaract referencing thread is started.
        '''

        # Checking whether referencing has been already done or not
        if self.smaract.get_referencing_status() == self.config.smaract_referencing_done:
            self.signals.progress.emit(self.config.smaract_referencing_done)
            # getting the initial position
            self.config.pos_initial_x = self.smaract.get_channel_position(self.config.smaract_channel_x)
            self.config.pos_initial_y = self.smaract.get_channel_position(self.config.smaract_channel_y)
            self.config.pos_initial_z = self.smaract.get_channel_position(self.config.smaract_channel_z)
            return
        # referencing the channels
	    # # x
        status = self.smaract.is_channel_referenced(self.config.smaract_channel_x)
        if (status == self.config.smaract_referencing_x_not):
            status = self.smaract.reference_channel(self.config.smaract_channel_x)
            if (status != self.config.smaract_status_ok):
                self.smaract.set_referencing_status(self.config.smaract_referencing_x_failed)
                self.signals.progress.emit(self.config.smaract_referencing_x_failed)
                time.sleep(self.config.gui_sleep_time_s)
            else:
                self.smaract.set_referencing_status(self.config.smaract_referencing_x_done)
                self.signals.progress.emit(self.config.smaract_referencing_x_done)
                time.sleep(self.config.gui_sleep_time_s)
        elif (status != self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_x_failed)
            self.signals.progress.emit(self.config.smaract_referencing_x_failed)
            time.sleep(self.config.gui_sleep_time_s)
        elif (status == self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_x_done)
            self.signals.progress.emit(self.config.smaract_referencing_x_done)
            time.sleep(self.config.gui_sleep_time_s)
        # # y
        status = self.smaract.is_channel_referenced(self.config.smaract_channel_y)
        if (status == self.config.smaract_referencing_y_not):
            status = self.smaract.reference_channel(self.config.smaract_channel_y)
            if (status != self.config.smaract_status_ok):
                self.smaract.set_referencing_status(self.config.smaract_referencing_y_failed)
                self.signals.progress.emit(self.config.smaract_referencing_y_failed)
                time.sleep(self.config.gui_sleep_time_s)
            else:
                self.smaract.set_referencing_status(self.config.smaract_referencing_y_done)
                self.signals.progress.emit(self.config.smaract_referencing_y_done)
                time.sleep(self.config.gui_sleep_time_s)
        elif (status != self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_y_failed)
            self.signals.progress.emit(self.config.smaract_referencing_y_failed)
            time.sleep(self.config.gui_sleep_time_s)
        elif (status == self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_y_done)
            self.signals.progress.emit(self.config.smaract_referencing_y_done)
            time.sleep(self.config.gui_sleep_time_s)
        # # z
        status = self.smaract.is_channel_referenced(self.config.smaract_channel_z)
        if (status == self.config.smaract_referencing_z_not):
            status = self.smaract.reference_channel(self.config.smaract_channel_z)
            if (status != self.config.smaract_status_ok):
                self.smaract.set_referencing_status(self.config.smaract_referencing_z_failed)
                self.signals.progress.emit(self.config.smaract_referencing_z_failed)
                time.sleep(self.config.gui_sleep_time_s)
            else:
                self.smaract.set_referencing_status(self.config.smaract_referencing_z_done)
                self.signals.progress.emit(self.config.smaract_referencing_z_done)
                time.sleep(self.config.gui_sleep_time_s)
        elif (status != self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_z_failed)
            self.signals.progress.emit(self.config.smaract_referencing_z_failed)
            time.sleep(self.config.gui_sleep_time_s)
        elif (status == self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_z_done)
            self.signals.progress.emit(self.config.smaract_referencing_z_done)
            time.sleep(self.config.gui_sleep_time_s)
        # # alpha
        status = self.smaract.is_channel_referenced(self.config.smaract_channel_alpha)
        if (status == self.config.smaract_referencing_alpha_not):
            status = self.smaract.reference_channel(self.config.smaract_channel_alpha)
            if (status != self.config.smaract_status_ok):
                self.smaract.set_referencing_status(self.config.smaract_referencing_alpha_failed)
                self.signals.progress.emit(self.config.smaract_referencing_alpha_failed)
                time.sleep(self.config.gui_sleep_time_s)
            else:
                self.smaract.set_referencing_status(self.config.smaract_referencing_alpha_done)
                self.signals.progress.emit(self.config.smaract_referencing_alpha_done)
                time.sleep(self.config.gui_sleep_time_s)
        elif (status != self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_alpha_failed)
            self.signals.progress.emit(self.config.smaract_referencing_alpha_failed)
            time.sleep(self.config.gui_sleep_time_s)
        elif (status == self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_alpha_done)
            self.signals.progress.emit(self.config.smaract_referencing_alpha_done)
            time.sleep(self.config.gui_sleep_time_s)
        # # beta
        status = self.smaract.is_channel_referenced(self.config.smaract_channel_beta)
        if (status == self.config.smaract_referencing_beta_not):
            status = self.smaract.reference_channel(self.config.smaract_channel_beta)
            if (status != self.config.smaract_status_ok):
                self.smaract.set_referencing_status(self.config.smaract_referencing_beta_failed)
                self.signals.progress.emit(self.config.smaract_referencing_beta_failed)
                time.sleep(self.config.gui_sleep_time_s)
            else:
                self.smaract.set_referencing_status(self.config.smaract_referencing_beta_done)
                self.signals.progress.emit(self.config.smaract_referencing_beta_done)
                time.sleep(self.config.gui_sleep_time_s)
        elif (status != self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_beta_failed)
            self.signals.progress.emit(self.config.smaract_referencing_beta_failed)
            time.sleep(self.config.gui_sleep_time_s)
        elif (status == self.config.smaract_status_ok):
            self.smaract.set_referencing_status(self.config.smaract_referencing_beta_done)
            self.signals.progress.emit(self.config.smaract_referencing_beta_done)
            time.sleep(self.config.gui_sleep_time_s)
        # # done
        self.smaract.set_referencing_status(self.config.smaract_referencing_done)
        self.signals.progress.emit(self.config.smaract_referencing_done)
        time.sleep(self.config.gui_sleep_time_s)
        # getting the initial position
        self.config.pos_initial_x = self.smaract.get_channel_position(self.config.smaract_channel_x)
        self.config.pos_initial_y = self.smaract.get_channel_position(self.config.smaract_channel_y)
        self.config.pos_initial_z = self.smaract.get_channel_position(self.config.smaract_channel_z)


class WorkerSignalsSmarActPositioning(QObject):
    '''
    defining the signals available from the smaract positioning worker thread
    '''

    progress_position = pyqtSignal(int, float)
    progress_control_status = pyqtSignal(int)
    progress_button = pyqtSignal()


class WorkerSmarActPositioning(QRunnable):
    '''
    worker thread for smaract positioning
    '''

    def __init__(self, smaract, config):
        super().__init__()
        self.smaract = smaract
        self.config = config
        self.signals = WorkerSignalsSmarActPositioning()
        self.config.control_smaract_status = self.config.control_smaract_default

    @pyqtSlot()
    def run(self):
        '''
        this function is called when the smaract positioning thread is started.
        '''

        # channel x
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_x, self.config.smaract_linear_pos_desired, 
                                                   self.config.smaract_linear_speed_positioning, self.config.smaract_linear_sleep_multiplier_positioning)
        self.signals.progress_position.emit(self.config.id_smaract_channel_x, self.smaract.get_channel_position(self.config.smaract_channel_x))
        # channel y
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_y, self.config.smaract_linear_pos_desired,
                                                   self.config.smaract_linear_speed_positioning, self.config.smaract_linear_sleep_multiplier_positioning)
        self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
        # channel z
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_z, self.config.smaract_linear_pos_desired,
                                                   self.config.smaract_linear_speed_positioning, self.config.smaract_linear_sleep_multiplier_positioning)
        self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
        # channel alpha
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_alpha, self.config.smaract_alpha_pos_desired, 
                                                   self.config.smaract_angular_speed_positioning, self.config.smaract_angular_sleep_multiplier_positioning)
        self.signals.progress_position.emit(self.config.id_smaract_channel_alpha, self.smaract.get_channel_position(self.config.smaract_channel_alpha))
        # channel beta
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_beta, self.config.smaract_beta_pos_desired,
                                                   self.config.smaract_angular_speed_positioning, self.config.smaract_angular_sleep_multiplier_positioning)
        self.signals.progress_position.emit(self.config.id_smaract_channel_beta, self.smaract.get_channel_position(self.config.smaract_channel_beta))
        # getting the initial position
        self.config.pos_initial_x = self.smaract.get_channel_position(self.config.smaract_channel_x)
        self.config.pos_initial_y = self.smaract.get_channel_position(self.config.smaract_channel_y)
        self.config.pos_initial_z = self.smaract.get_channel_position(self.config.smaract_channel_z)
        # updating the control status
        self.config.control_smaract_status = self.config.control_smaract_translation
        self.signals.progress_control_status.emit(self.config.control_smaract_status)
        self.signals.progress_button.emit()


class WorkerSignalsPIStageReferencing(QObject):
    ''' 
    defining the signals available from the pistage referencing worker thread
    '''

    progress = pyqtSignal(int)


class WorkerPIStageReferencing(QRunnable):
    '''
    worker thread for pistage referencing
    '''

    def __init__(self, pistage, config):
        super().__init__()
        self.pistage = pistage
        self.config = config
        self.signals = WorkerSignalsPIStageReferencing()

    @pyqtSlot()
    def run(self):
        '''
        this function is called when the pistage referencing thread is started.
        '''

        # Checking whether referencing has been already done or not
        if self.pistage.get_referencing_status() == self.config.pistage_referencing_done:
            self.signals.progress.emit(self.config.pistage_referencing_done)
            time.sleep(self.config.gui_sleep_time_s)
            return
        # referencing the axes
	    # # l1
        status = self.pistage.is_axis_referenced(self.config.pistage_l1)
        if (status == False):
            status = self.pistage.reference_axis(self.config.pistage_l1)
            if (status == False):
                self.pistage.set_referencing_status(self.config.pistage_referencing_l1_failed)
                self.signals.progress.emit(self.config.pistage_referencing_l1_failed)
                time.sleep(self.config.gui_sleep_time_s)
            else:
                self.pistage.set_referencing_status(self.config.pistage_referencing_l1_done)
                self.signals.progress.emit(self.config.pistage_referencing_l1_done)
                time.sleep(self.config.gui_sleep_time_s)
        else:
            self.pistage.set_referencing_status(self.config.pistage_referencing_l1_done)
            self.signals.progress.emit(self.config.pistage_referencing_l1_done)
            time.sleep(self.config.gui_sleep_time_s)
        # # l2
        status = self.pistage.is_axis_referenced(self.config.pistage_l2)
        if (status == False):
            status = self.pistage.reference_axis(self.config.pistage_l2)
            if (status == False):
                self.pistage.set_referencing_status(self.config.pistage_referencing_l2_failed)
                self.signals.progress.emit(self.config.pistage_referencing_l2_failed)
                time.sleep(self.config.gui_sleep_time_s)
            else:
                self.pistage.set_referencing_status(self.config.pistage_referencing_l2_done)
                self.signals.progress.emit(self.config.pistage_referencing_l2_done)
                time.sleep(self.config.gui_sleep_time_s)
        else:
            self.pistage.set_referencing_status(self.config.pistage_referencing_l2_done)
            self.signals.progress.emit(self.config.pistage_referencing_l2_done)
            time.sleep(self.config.gui_sleep_time_s)
        # # done
        self.pistage.set_referencing_status(self.config.pistage_referencing_done)
        self.signals.progress.emit(self.config.pistage_referencing_done)
        time.sleep(self.config.gui_sleep_time_s)


class WorkerSignalsPIStagePositioning(QObject):
    '''
    defining the signals available from the pistage positioning worker thread
    '''

    progress_position = pyqtSignal(int, float)
    progress_control_status = pyqtSignal(int)
    progress_button = pyqtSignal()


class WorkerPIStagePositioning(QRunnable):
    '''
    worker thread for pistage positioning
    '''

    def __init__(self, pistage, config):
        super().__init__()
        self.pistage = pistage
        self.config = config
        self.signals = WorkerSignalsPIStagePositioning()
        self.config.control_pistage_status = self.config.control_pistage_default

    @pyqtSlot()
    def run(self):
        '''
        this function is called when the pistage positioning thread is started.
        '''

        # axis l1
        aux.pistage_move_axis_to_position_sleep(self.pistage, self.config.pistage_l1, self.config.pistage_pos_l1_desired, 
                                                self.config.pistage_speed_positioning, self.config.pistage_sleep_multiplier_positioning)
        self.signals.progress_position.emit(self.config.id_pistage_l1, self.pistage.get_axis_position(self.config.pistage_l1))
        # axis l2
        aux.pistage_move_axis_to_position_sleep(self.pistage, self.config.pistage_l2, self.config.pistage_pos_l2_desired,
                                                self.config.pistage_speed_positioning, self.config.pistage_sleep_multiplier_positioning)
        self.signals.progress_position.emit(self.config.id_pistage_l2, self.pistage.get_axis_position(self.config.pistage_l2))
        # updating the control status
        self.config.control_pistage_status = self.config.control_pistage_l1
        self.signals.progress_control_status.emit(self.config.control_pistage_status)
        self.signals.progress_button.emit()


class WorkerSignalsGamepad(QObject):
    '''
    defining the signals available from the gamepad worker thread
    '''

    progress_gamepad_status = pyqtSignal(int)
    progress_smaract_control_status = pyqtSignal(int)
    progress_pistage_control_status = pyqtSignal(int)
    progress_smaract_speed_multiplier = pyqtSignal(int)
    progress_pistage_speed_multiplier = pyqtSignal(int)
    progress_position = pyqtSignal(int, float)
    progress_text_edit = pyqtSignal(str, int)


class WorkerGamepad(QRunnable):
    '''
    Worker thread for gamepad
    '''

    def __init__(self, smaract, asm, pistage, gamepad, config):
        super().__init__()
        self.smaract = smaract
        self.asm = asm
        self.pistage = pistage
        self.gamepad = gamepad
        self.config = config
        self.signals = WorkerSignalsGamepad()
        self.axis_LX = self.gamepad.get_stick_value(self.config.gamepad_sticks['LS_X'])
        self.axis_LY = self.gamepad.get_stick_value(self.config.gamepad_sticks['LS_Y'])
        self.axis_RY = self.gamepad.get_stick_value(self.config.gamepad_sticks['RS_Y'])
        
    def run(self):
        '''
        this function is called when the gamepad thread is started.
        its role is to receive gamepad events (such as movement of axes) and translates them into desired commands (such as movement of smaract stages).
        '''

        while True:
            result = self.gamepad.get_state()
            if self.config.automation_flag_stopped:
                pass
            elif result == self.config.gamepad_not_found:
                self.signals.progress_gamepad_status.emit(self.config.gamepad_not_found)
            elif result == self.config.gamepad_found:
                self.signals.progress_gamepad_status.emit(self.config.gamepad_found)
                # LB button is responsible for changing the control mode of smaract (translation or rotation)
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['LB']):
                    if self.config.control_smaract_status == self.config.control_smaract_translation:
                        self.config.control_smaract_status = self.config.control_smaract_rotation
                    elif self.config.control_smaract_status == self.config.control_smaract_rotation:
                        self.config.control_smaract_status = self.config.control_smaract_translation
                    self.signals.progress_smaract_control_status.emit(self.config.control_smaract_status)
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # RB button is responsible for changing the control mode of pistage (L1 or L2)
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['RB']):
                    if self.config.control_pistage_status == self.config.control_pistage_l1:
                        self.config.control_pistage_status = self.config.control_pistage_l2
                    elif self.config.control_pistage_status == self.config.control_pistage_l2:
                        self.config.control_pistage_status = self.config.control_pistage_l1
                    self.signals.progress_pistage_control_status.emit(self.config.control_pistage_status)
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # A button is responsible for decreasing the pistage speed multiplier
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['A']):
                    self.signals.progress_pistage_speed_multiplier.emit(self.config.pistage_speed_multiplier_decrease)
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # Y button is responsible for increasing the pistage speed multiplier
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['Y']):
                    self.signals.progress_pistage_speed_multiplier.emit(self.config.pistage_speed_multiplier_increase)
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # B button is responsible for moving the smaract gamma channel counter-clockwise
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['B']):
                    gamma_movement = self.config.smaract_gamma_steps_base
                    gamma_frequency = self.config.smaract_speed_multiplier_value * self.config.smaract_gamma_frequency_base
                    if not aux.smaract_is_valid_speed(self.config, self.config.smaract_channel_gamma, gamma_frequency):
                        self.signals.progress_text_edit.emit(self.config.smaract_err_gamma_frequency_invalid, self.config.text_edit_mode_err)
                    else:
                        self.smaract.move_channel(self.config.smaract_channel_gamma, gamma_movement, gamma_frequency)
                        self.config.smaract_gamma_steps = self.config.smaract_gamma_steps + gamma_movement
                        self.signals.progress_position.emit(self.config.id_smaract_channel_gamma, self.config.smaract_gamma_steps)
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # X button is responsible for moving the smaract gamma channel clockwise
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['X']):
                    gamma_movement = -self.config.smaract_gamma_steps_base
                    gamma_frequency = self.config.smaract_speed_multiplier_value * self.config.smaract_gamma_frequency_base
                    if not aux.smaract_is_valid_speed(self.config, self.config.smaract_channel_gamma, gamma_frequency):
                        self.signals.progress_text_edit.emit(self.config.smaract_err_gamma_frequency_invalid, self.config.text_edit_mode_err)
                    else:
                        self.smaract.move_channel(self.config.smaract_channel_gamma, gamma_movement, gamma_frequency)
                        self.config.smaract_gamma_steps = self.config.smaract_gamma_steps + gamma_movement
                        self.signals.progress_position.emit(self.config.id_smaract_channel_gamma, self.config.smaract_gamma_steps)
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # Left in D-Pad is responsible for moving the Arduino stepper motor (ASM) clockwise
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['DPAD_LEFT']):
                    self.asm.move(-self.config.asm_steps_base)
                    self.signals.progress_position.emit(self.config.id_asm, float(self.asm.get_position()))
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # Right in D-Pad is responsible for moving the Arduino stepper motor (ASM) counter-clockwise
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['DPAD_RIGHT']):
                    self.asm.move(self.config.asm_steps_base)
                    self.signals.progress_position.emit(self.config.id_asm, float(self.asm.get_position()))
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # Up in D-Pad is responsible for  increasing the smaract speed multiplier
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['DPAD_UP']):
                    self.signals.progress_smaract_speed_multiplier.emit(self.config.smaract_speed_multiplier_increase)
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # Down in D-Pad is responsible for decreasing the smaract speed multiplier
                if self.gamepad.is_button_pressed(self.config.gamepad_buttons['DPAD_DOWN']):
                    self.signals.progress_smaract_speed_multiplier.emit(self.config.smaract_speed_multiplier_decrease)
                    time.sleep(self.config.gamepad_polling_time_button_s)
                # Left stick X (horizontal) is responsible for moving the smaract channels x (in translation mode) and alpha (in rotation mode)
                lsx = self.gamepad.get_stick_value(self.config.gamepad_sticks['LS_X'])
                if abs(lsx - self.axis_LX) > self.config.gamepad_sensitivity: 
                    self.axis_LX = lsx
                    if abs(lsx) <= self.config.gamepad_threshold:   # ignoring the gamepad command if it is less than the higher threshold
                        # smaract channel x
                        if self.config.control_smaract_status == self.config.control_smaract_translation:
                            self.smaract.stop_channel(self.config.smaract_channel_x)
                            self.signals.progress_position.emit(self.config.id_smaract_channel_x, self.smaract.get_channel_position(self.config.smaract_channel_x))
                        # smaract channel alpha
                        elif self.config.control_smaract_status == self.config.control_smaract_rotation:
                            self.smaract.stop_channel(self.config.smaract_channel_alpha)
                            self.signals.progress_position.emit(self.config.id_smaract_channel_alpha, self.smaract.get_channel_position(self.config.smaract_channel_alpha))
                    else:  
                        # smaract channel x
                        if self.config.control_smaract_status == self.config.control_smaract_translation:
                            x_movement = -lsx * self.config.smaract_linear_steps_base
                            x_speed = self.config.smaract_speed_multiplier_value * self.config.smaract_linear_speed_base
                            if not aux.smaract_is_valid_speed(self.config, self.config.smaract_channel_x, x_speed):
                                self.signals.progress_text_edit.emit(self.config.smaract_err_linear_speed_invalid, self.config.text_edit_mode_err)
                            else:
                                if self.smaract.get_channel_position(self.config.smaract_channel_x) >= self.config.smaract_linear_pos_gamepad_high_limit and x_movement > 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_x)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_x, self.smaract.get_channel_position(self.config.smaract_channel_x))
                                elif self.smaract.get_channel_position(self.config.smaract_channel_x) <= self.config.smaract_linear_pos_gamepad_low_limit and x_movement < 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_x)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_x, self.smaract.get_channel_position(self.config.smaract_channel_x))
                                else:
                                    self.smaract.move_channel(self.config.smaract_channel_x, x_movement, x_speed)
                        # smaract channel alpha	
                        elif self.config.control_smaract_status == self.config.control_smaract_rotation:
                            alpha_movement = lsx * self.config.smaract_angular_steps_base
                            alpha_speed = self.config.smaract_speed_multiplier_value * self.config.smaract_angular_speed_base
                            if not aux.smaract_is_valid_speed(self.config, self.config.smaract_channel_alpha, alpha_speed):
                                self.signals.progress_text_edit.emit(self.config.smaract_err_angular_speed_invalid, self.config.text_edit_mode_err)
                            else:
                                if self.smaract.get_channel_position(self.config.smaract_channel_alpha) >= self.config.smaract_alpha_pos_gamepad_high_limit and alpha_movement > 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_alpha)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_alpha, self.smaract.get_channel_position(self.config.smaract_channel_alpha))
                                elif self.smaract.get_channel_position(self.config.smaract_channel_alpha) <= self.config.smaract_alpha_pos_gamepad_low_limit and alpha_movement < 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_alpha)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_alpha, self.smaract.get_channel_position(self.config.smaract_channel_alpha))
                                else:
                                    self.smaract.move_channel(self.config.smaract_channel_alpha, alpha_movement, alpha_speed)
                # Left stick Y (vertical) is responsible for moving the smaract channels y (in translation mode) and beta (in rotation mode)
                lsy = self.gamepad.get_stick_value(self.config.gamepad_sticks['LS_Y'])
                if abs(lsy - self.axis_LY) > self.config.gamepad_sensitivity: 
                    self.axis_LY = lsy
                    if abs(lsy) <= self.config.gamepad_threshold:   # ignoring the gamepad command if it is less than the higher threshold
                        # smaract channel y
                        if self.config.control_smaract_status == self.config.control_smaract_translation:
                            self.smaract.stop_channel(self.config.smaract_channel_y)
                            self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
                        # smaract channel beta	
                        elif self.config.control_smaract_status == self.config.control_smaract_rotation:
                            self.smaract.stop_channel(self.config.smaract_channel_beta)
                            self.signals.progress_position.emit(self.config.id_smaract_channel_beta, self.smaract.get_channel_position(self.config.smaract_channel_beta))
                    else:
                        # smaract channel y
                        if self.config.control_smaract_status == self.config.control_smaract_translation:
                            y_movement = lsy * self.config.smaract_linear_steps_base
                            y_speed = self.config.smaract_speed_multiplier_value * self.config.smaract_linear_speed_base
                            if not aux.smaract_is_valid_speed(self.config, self.config.smaract_channel_y, y_speed):
                                self.signals.progress_text_edit.emit(self.config.smaract_err_linear_speed_invalid, self.config.text_edit_mode_err)
                            else:
                                if self.smaract.get_channel_position(self.config.smaract_channel_y) >= self.config.smaract_linear_pos_gamepad_high_limit and y_movement > 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_y)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
                                elif self.smaract.get_channel_position(self.config.smaract_channel_y) <= self.config.smaract_linear_pos_gamepad_low_limit and y_movement < 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_y)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
                                else:
                                    self.smaract.move_channel(self.config.smaract_channel_y, y_movement, y_speed)
                        # smaract channel beta
                        elif self.config.control_smaract_status == self.config.control_smaract_rotation:
                            beta_movement = lsy * self.config.smaract_angular_steps_base
                            beta_speed = self.config.smaract_speed_multiplier_value * self.config.smaract_angular_speed_base
                            if not aux.smaract_is_valid_speed(self.config, self.config.smaract_channel_beta, beta_speed):
                                self.signals.progress_text_edit.emit(self.config.smaract_err_angular_speed_invalid, self.config.text_edit_mode_err)
                            else:
                                if self.smaract.get_channel_position(self.config.smaract_channel_beta) >= self.config.smaract_beta_pos_gamepad_high_limit and beta_movement > 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_beta)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_beta, self.smaract.get_channel_position(self.config.smaract_channel_beta))
                                elif self.smaract.get_channel_position(self.config.smaract_channel_beta) <= self.config.smaract_beta_pos_gamepad_low_limit and beta_movement < 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_beta)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_beta, self.smaract.get_channel_position(self.config.smaract_channel_beta))
                                else:
                                    self.smaract.move_channel(self.config.smaract_channel_beta, beta_movement, beta_speed)
                # Right stick Y (vertical) is responsible for moving the smaract channels z (in translation mode)
                rsy = self.gamepad.get_stick_value(self.config.gamepad_sticks['RS_Y'])
                if abs(rsy - self.axis_RY) > self.config.gamepad_sensitivity: 
                    self.axis_RY = rsy
                    if abs(rsy) <= self.config.gamepad_threshold:     # ignoring the gamepad command if it is less than the higher threshold
                        # smaract channel z
                        if self.config.control_smaract_status == self.config.control_smaract_translation:
                            self.smaract.stop_channel(self.config.smaract_channel_z)
                            self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
                    else:
                        # smaract channel z
                        if self.config.control_smaract_status == self.config.control_smaract_translation:
                            z_movement = -rsy * self.config.smaract_linear_steps_base
                            z_speed = self.config.smaract_speed_multiplier_value * self.config.smaract_linear_speed_base
                            if not aux.smaract_is_valid_speed(self.config, self.config.smaract_channel_z, z_speed):
                                self.signals.progress_text_edit.emit(self.config.smaract_err_linear_speed_invalid, self.config.text_edit_mode_err)
                            else:
                                if self.smaract.get_channel_position(self.config.smaract_channel_z) >= self.config.smaract_linear_pos_gamepad_high_limit and z_movement > 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_z)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
                                elif self.smaract.get_channel_position(self.config.smaract_channel_z) <= self.config.smaract_linear_pos_gamepad_low_limit and z_movement < 0:
                                    self.smaract.stop_channel(self.config.smaract_channel_z)
                                    self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
                                else:
                                    self.smaract.move_channel(self.config.smaract_channel_z, z_movement, z_speed)
                # Right stick X (horizontal) is responsible for moving the pistage axes L1 (in L1 mode) and L2 (in L2 mode)
                rsx = self.gamepad.get_stick_value(self.config.gamepad_sticks['RS_X'])
                if abs(rsx) > self.config.gamepad_threshold:
                    # pistage axis L1
                    if self.config.control_pistage_status == self.config.control_pistage_l1:
                        l1_movement = -rsx * self.config.pistage_steps_base
                        l1_speed = self.config.pistage_speed_multiplier_value * self.config.pistage_speed_base
                        if not aux.pistage_is_valid_relative_movement(self.config, self.pistage.get_axis_position(self.config.pistage_l1), l1_movement):
                            self.signals.progress_text_edit.emit(self.config.pistage_err_l1_not_reachable, self.config.text_edit_mode_err)
                        else:
                            if not aux.pistage_is_valid_speed(self.config, l1_speed):
                                self.signals.progress_text_edit.emit(self.config.pistage_err_speed_invalid, self.config.text_edit_mode_err)
                            else:
                                self.pistage.move_axis(self.config.pistage_l1, l1_movement, l1_speed)
                                self.signals.progress_position.emit(self.config.id_pistage_l1, self.pistage.get_axis_position(self.config.pistage_l1))
                    # pistage axis L2
                    elif self.config.control_pistage_status == self.config.control_pistage_l2:
                        l2_movement = -rsx * self.config.pistage_steps_base
                        l2_speed = self.config.pistage_speed_multiplier_value * self.config.pistage_speed_base
                        if not aux.pistage_is_valid_relative_movement(self.config, self.pistage.get_axis_position(self.config.pistage_l2), l2_movement):
                            self.signals.progress_text_edit.emit(self.config.pistage_err_l2_not_reachable, self.config.text_edit_mode_err)
                        else:
                            if not aux.pistage_is_valid_speed(self.config, l2_speed):
                                self.signals.progress_text_edit.emit(self.config.pistage_err_speed_invalid, self.config.text_edit_mode_err)
                            else:
                                self.pistage.move_axis(self.config.pistage_l2, l2_movement, l2_speed)
                                self.signals.progress_position.emit(self.config.id_pistage_l2, self.pistage.get_axis_position(self.config.pistage_l2))
            time.sleep(self.config.gamepad_polling_time_s)


class WorkerSignalsSequenceInitialize(QObject):
    '''
    defining the signals available from the sequence-initialize worker thread
    '''

    progress_position = pyqtSignal(int, float)
    progress_button = pyqtSignal()


class WorkerSequenceInitialize(QRunnable):
    '''
    worker thread for sequence-initialize
    '''

    def __init__(self, smaract, config):
        super().__init__()
        self.smaract = smaract
        self.config = config
        self.signals = WorkerSignalsSequenceInitialize()

    @pyqtSlot()
    def run(self):
        '''
        this function is called when the sequence-initialize thread is started.
        '''

        # channel alpha
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_alpha, self.config.sequence_initial_alpha,
                                                   self.config.sequence_angular_speed, self.config.sequence_sleep_multiplier_initialize)
        self.signals.progress_position.emit(self.config.id_smaract_channel_alpha, self.smaract.get_channel_position(self.config.smaract_channel_alpha))
        # channel beta
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_beta, self.config.sequence_initial_beta,
                                                   self.config.sequence_angular_speed, self.config.sequence_sleep_multiplier_initialize)
        self.signals.progress_position.emit(self.config.id_smaract_channel_beta, self.smaract.get_channel_position(self.config.smaract_channel_beta))
        # channel z
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_z, self.config.sequence_initial_z,
                                                   self.config.sequence_linear_speed, self.config.sequence_sleep_multiplier_initialize)
        self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
        # getting the initial position
        self.config.pos_initial_x = self.smaract.get_channel_position(self.config.smaract_channel_x)
        self.config.pos_initial_y = self.smaract.get_channel_position(self.config.smaract_channel_y)
        self.config.pos_initial_z = self.smaract.get_channel_position(self.config.smaract_channel_z)
        self.signals.progress_button.emit()


class WorkerSignalsSequenceDo(QObject):
    '''
    defining the signals available from the sequence-do worker thread
    '''

    progress_position = pyqtSignal(int, float)
    progress_button = pyqtSignal()


class WorkerSequenceDo(QRunnable):
    '''
    worker thread for sequence-do
    '''

    def __init__(self, smaract, asm, config):
        super().__init__()
        self.smaract = smaract
        self.asm = asm
        self.config = config
        self.signals = WorkerSignalsSequenceDo()

    @pyqtSlot()
    def run(self):
        '''
        this function is called when the sequence-do thread is started.
        '''

        # setting asm delay
        self.asm.set_delay(self.config.asm_delay_ms)
        for i in range(len(self.config.sequence_delta_z)):
            # moving for delta z
            aux.smaract_move_channel_sleep(self.smaract, self.config.smaract_channel_z, self.config.sequence_delta_z[i]*self.config.micro_to_nano,
                                           self.config.sequence_linear_speed, self.config.sequence_sleep_multiplier_do)
            self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
            # moving for delta y
            aux.smaract_move_channel_sleep(self.smaract, self.config.smaract_channel_y, self.config.sequence_delta_y[i]*self.config.micro_to_nano,
                                           self.config.sequence_linear_speed, self.config.sequence_sleep_multiplier_do)
            self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
            # cutting
            aux.scissor_close(self.asm, self.config)
            self.signals.progress_position.emit(self.config.id_asm, float(self.asm.get_position()))
            # opening
            aux.scissor_open(self.asm, self.config)
            self.signals.progress_position.emit(self.config.id_asm, float(self.asm.get_position()))
        # moving to initial z (to avoid the scissor jump)
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_z, self.config.pos_initial_z,
                                                   self.config.sequence_linear_speed, self.config.sequence_sleep_multiplier_do)
        self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
        # moving to initial x (to avoid the scissor jump)
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_x, self.config.pos_initial_x,
                                                   self.config.sequence_linear_speed, self.config.sequence_sleep_multiplier_do)
        self.signals.progress_position.emit(self.config.id_smaract_channel_x, self.smaract.get_channel_position(self.config.smaract_channel_x))
        # moving to initial y (to avoid the scissor jump)
        aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_y, self.config.pos_initial_y,
                                                   self.config.sequence_linear_speed, self.config.sequence_sleep_multiplier_do)
        self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
        if self.config.sequence_flag_release_debris:
            aux.scissor_close(self.asm, self.config)
            aux.scissor_open(self.asm, self.config)
        # done
        img = aux.normalize_image(self.config.camera_image)
        vision.save_image(img, str(self.config.save_counter)+'_done', self.config.save_directory)
        self.config.annotation_embryo_points, self.config.annotation_scissor_points, self.config.annotation_points = [], [], []
        self.signals.progress_button.emit()


class WorkerSignalsAutomation(QObject):
    '''
    defining the signals available from the developing embryo experiment worker thread
    '''

    progress_position = pyqtSignal(int, float)
    progress_text_edit = pyqtSignal(str, int)
    progress_coord = pyqtSignal()
    progress_button = pyqtSignal()

class WorkerAutomation(QRunnable):
    '''
    worker thread for developing embryo experiment
    '''

    def __init__(self, smaract, asm, pistage, camera, config, model):
        super().__init__()
        self.smaract = smaract
        self.asm = asm
        self.pistage = pistage
        self.camera = camera
        self.config = config
        self.model = model
        self.signals = WorkerSignalsAutomation()
        #self.worker_camera = WorkerCamera(self.camera, self.config)

    def go_to_next_embryo(self, l1, l2):
        if self.config.automation_flag_stopped:
            return
        if l1 == self.config.automation_num_l1 - 1:
            if l2 == self.config.automation_num_l2 - 1:
                l1_movement = 0
                l2_movement = 0
            else:
                l1_movement = 0
                # wait until the next somite forms
                if self.config.pistage_development_wait != 0:
                    self.camera.StopGrabbing()
                    time.sleep(self.config.pistage_development_wait)
                    self.camera.StartGrabbing(1)
                    l2_movement = self.config.automation_step_l2
                else:
                    l2_movement = self.config.automation_step_l2
        else:
            if l2%2 == 0:
                l1_movement = -self.config.automation_step_l1
            else:
                l1_movement = self.config.automation_step_l1
            l2_movement = 0
        if l2*self.config.automation_num_l1+l1+2 <= self.config.automation_num_l1*self.config.automation_num_l2:
            self.signals.progress_text_edit.emit(self.config.automation_message_next+str(l2*self.config.automation_num_l1+l1+2), self.config.text_edit_mode_info)
        # axis L1
        aux.pistage_move_axis_sleep(self.pistage, self.config.pistage_l1, l1_movement, self.config.automation_speed_pistage, self.config.automation_sleep_multiplier_pistage)
        self.signals.progress_position.emit(self.config.id_pistage_l1, self.pistage.get_axis_position(self.config.pistage_l1))
        # axis L2
        aux.pistage_move_axis_sleep(self.pistage, self.config.pistage_l2, l2_movement, self.config.automation_speed_pistage, self.config.automation_sleep_multiplier_pistage)
        self.signals.progress_position.emit(self.config.id_pistage_l2, self.pistage.get_axis_position(self.config.pistage_l2))

    @pyqtSlot()
    def run(self):
        '''
        this function is called when the automation thread is started.
        '''

        # setting asm delay
        self.asm.set_delay(self.config.asm_delay_ms)
        for l2 in range(self.config.automation_num_l2):
            for l1 in range(self.config.automation_num_l1):
                if self.config.automation_flag_stopped:
                    return
                # annotating
                self.signals.progress_text_edit.emit(self.config.automation_message_annotating+str(l2*self.config.automation_num_l1+l1+1), self.config.text_edit_mode_info)
                # # taking the current image of the camera
                img = aux.normalize_image(self.config.camera_image)
                vision.save_image(img, str(self.config.automation_counter), self.config.automation_directory)
                # # annotating embryo
                flag, err = aux.automation_annotate_embryo(img, self.config, self.model)
                if flag == False:
                    self.config.annotation_embryo_points, self.config.annotation_scissor_points, self.config.annotation_points = [], [], []
                    self.signals.progress_text_edit.emit(err, self.config.text_edit_mode_err)
                    if self.config.automation_flag_stopped:
                        return 
                    self.go_to_next_embryo(l1, l2)
                    self.config.automation_counter = self.config.automation_counter + 1
                    continue
                # # annotating scissor
                flag, err = aux.automation_annotate_scissor(img, self.config)
                if flag == False:
                    self.config.annotation_embryo_points, self.config.annotation_scissor_points, self.config.annotation_points = [], [], []
                    self.signals.progress_text_edit.emit(err, self.config.text_edit_mode_err)
                    if self.config.automation_flag_stopped:
                        return 
                    self.go_to_next_embryo(l1, l2)
                    self.config.automation_counter = self.config.automation_counter + 1
                    continue
                img_drawn = vision.draw_points(np.float32(img), self.config.annotation_points, self.config.annotation_point_offset)
                vision.save_image(img_drawn, str(self.config.automation_counter)+'_ann', self.config.automation_directory)
                # updating the coordinates
                if self.config.automation_flag_cv_dn:
                    self.config.coords_target.append((self.config.annotation_embryo_points[self.config.dn_somite_target-1][0],
                                                      self.config.annotation_embryo_points[self.config.dn_somite_target-1][1]))
                else:
                    self.config.coords_target.append((self.config.annotation_embryo_points[-1][0], self.config.annotation_embryo_points[-1][1]))
                self.config.coords_tool.append((self.config.annotation_scissor_points[-1][0], self.config.annotation_scissor_points[-1][1]))
                self.signals.progress_coord.emit()
                # getting the initial position
                self.config.pos_initial_x = self.smaract.get_channel_position(self.config.smaract_channel_x)
                self.config.pos_initial_y = self.smaract.get_channel_position(self.config.smaract_channel_y)
                self.config.pos_initial_z = self.smaract.get_channel_position(self.config.smaract_channel_z)
                # moving the scissor to the embryo keypoint
                self.signals.progress_text_edit.emit(self.config.automation_message_sequence+str(l2*self.config.automation_num_l1+l1+1), self.config.text_edit_mode_info)
                x_movement = -(self.config.coords_target[-1][0] -  self.config.coords_tool[-1][0]) * self.config.pixel_to_mili * self.config.mili_to_nano
                aux.smaract_move_channel_sleep(self.smaract, self.config.smaract_channel_x, x_movement, 
                                               self.config.automation_speed_smaract, self.config.automation_sleep_multiplier_smaract)
                self.signals.progress_position.emit(self.config.id_smaract_channel_x, self.smaract.get_channel_position(self.config.smaract_channel_x))
                y_movement = -(self.config.coords_target[-1][1] -  self.config.coords_tool[-1][1]) * self.config.pixel_to_mili * self.config.mili_to_nano 
                aux.smaract_move_channel_sleep(self.smaract, self.config.smaract_channel_y, y_movement,
                                               self.config.automation_speed_smaract, self.config.automation_sleep_multiplier_smaract)
                self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
                # performing the cutting sequence
                for i in range(len(self.config.sequence_delta_z)):
                    if self.config.automation_flag_stopped:
                        return
                    # # moving for delta z
                    aux.smaract_move_channel_sleep(self.smaract, self.config.smaract_channel_z, self.config.sequence_delta_z[i]*self.config.micro_to_nano,
                                                   self.config.automation_speed_smaract, self.config.automation_sleep_multiplier_smaract)
                    self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
                    # # moving for delta y
                    aux.smaract_move_channel_sleep(self.smaract, self.config.smaract_channel_y, self.config.sequence_delta_y[i]*self.config.micro_to_nano,
                                                   self.config.automation_speed_smaract, self.config.automation_sleep_multiplier_smaract)
                    self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
                    # # cutting
                    aux.scissor_close(self.asm, self.config)
                    self.signals.progress_position.emit(self.config.id_asm, float(self.asm.get_position()))
                    # # opening
                    aux.scissor_open(self.asm, self.config)
                    self.signals.progress_position.emit(self.config.id_asm, float(self.asm.get_position()))
                # # moving to initial z (to avoid the scissor jump)
                aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_z, self.config.pos_initial_z,
                                                           self.config.automation_speed_smaract, self.config.automation_sleep_multiplier_smaract)
                self.signals.progress_position.emit(self.config.id_smaract_channel_z, self.smaract.get_channel_position(self.config.smaract_channel_z))
                # # moving to initial x (to avoid the scissor jump)
                aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_x, self.config.pos_initial_x,
                                                           self.config.automation_speed_smaract, self.config.automation_sleep_multiplier_smaract)
                self.signals.progress_position.emit(self.config.id_smaract_channel_x, self.smaract.get_channel_position(self.config.smaract_channel_x))
                # # moving to initial y (to avoid the scissor jump)
                aux.smaract_move_channel_to_position_sleep(self.smaract, self.config.smaract_channel_y, self.config.pos_initial_y,
                                                           self.config.automation_speed_smaract, self.config.automation_sleep_multiplier_smaract)
                self.signals.progress_position.emit(self.config.id_smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y))
                if self.config.automation_flag_release_debris:
                    if self.config.automation_flag_stopped:
                        return
                    aux.scissor_close(self.asm, self.config)
                    aux.scissor_open(self.asm, self.config)
                # going to the next embryo
                img = aux.normalize_image(self.config.camera_image)
                vision.save_image(img, str(self.config.automation_counter)+'_done', self.config.automation_directory)
                self.config.automation_counter = self.config.automation_counter + 1
                self.config.annotation_embryo_points, self.config.annotation_scissor_points, self.config.annotation_points = [], [], []
                if self.config.automation_flag_stopped:
                    return 
                self.go_to_next_embryo(l1, l2)
        # Done
        self.signals.progress_text_edit.emit(self.config.automation_message_done, self.config.text_edit_mode_info)
        self.signals.progress_button.emit()


class WorkerSignalsReconnection(QObject):
    '''
    defining the signals available from the reconnection worker thread
    '''

    progress = pyqtSignal(str, int)


class WorkerReconnection(QRunnable):
    '''
    worker thread for reconnection
    '''

    def __init__(self, smaract, asm, config):
        super().__init__()
        self.smaract = smaract
        self.asm = asm
        self.config = config
        self.signals = WorkerSignalsReconnection()

    @pyqtSlot()
    def run(self):
        '''
        this function is called when the reconnection thread is started.
        '''

        status = self.smaract.initialize()
        time.sleep(self.config.gui_sleep_time_s)
        if status != self.config.smaract_status_ok:
            self.signals.progress.emit(self.config.reconnection_message_failed_smaract+str(status)+'!', self.config.text_edit_mode_err)
            return
        else:
            self.signals.progress.emit(self.config.reconnection_message_done_smaract, self.config.text_edit_mode_info)
        status = self.asm.initialize()
        time.sleep(self.config.gui_sleep_time_s)
        if status != self.asm.status_ok:
            self.signals.progress.emit(self.config.reconnection_message_failed_asm+str(status)+'!', self.config.text_edit_mode_err)
            return
        else:
            self.signals.progress.emit(self.config.reconnection_message_done_asm, self.config.text_edit_mode_info)
            self.asm.set_delay(self.config.asm_delay_ms)
