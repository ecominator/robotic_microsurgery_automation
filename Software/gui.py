##############################################################################
# File name:    gui.py
# Project:      Robotic Surgery Software
# Part:         GUI of the robotic surgery platform
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file contains the GUI of the robotic surgery platform
#               and is responsible for providing a user-friendly interface,
#               wrapping all the necessary elements together, and running 
#               multiple threads in parallel.   
##############################################################################


# Modules
import auxiliary as aux
import worker_threads as wt
import computer_vision as vision
import deep_network as dn
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton, QSpinBox, QMessageBox, QLineEdit, QTextEdit, QComboBox
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import Qt, pyqtSlot, QThreadPool
import pyqtgraph as pg
import os
import numpy as np
import time


class smaractSpinBox(QSpinBox):
    '''
    custom spin-box for smaract speed-multiplier
    '''

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setRange(self.config.smaract_speed_multiplier_indices[0], self.config.smaract_speed_multiplier_indices[-1])
        self.setSingleStep(1)

    def textFromValue(self, value):
        return str(self.config.smaract_speed_multiplier_values[value])
            

class PIStageSpinBox(QSpinBox):
    '''
    custom spin-box for pistage speed-multiplier
    '''

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setRange(self.config.pistage_speed_multiplier_indices[0], self.config.pistage_speed_multiplier_indices[-1])
        self.setSingleStep(1)

    def textFromValue(self, value):
        return str(self.config.pistage_speed_multiplier_values[value])


class GUI(QMainWindow):
    def __init__(self, smaract, asm, pistage, gamepad, camera, config, ppi):
        super().__init__()
        self.smaract = smaract
        self.asm = asm
        self.pistage = pistage
        self.gamepad = gamepad
        self.camera = camera
        self.config = config
        self.ppi = ppi
        self.model = dn.load_model(self.config.dn_path, self.config.dn_image_size, self.config.dn_filters_num, 
                                   self.config.dn_kernel_size, self.config.dn_stride, self.config.dn_dropout,
                                   self.config.dn_flag_batch_norm)
        # loading the images
        self.image_black = QPixmap(self.config.gui_directory+'black.png')
        self.image_red_cross = QPixmap(self.config.gui_directory+'redCross.png')
        self.image_green_check = QPixmap(self.config.gui_directory+'greenCheck.png')
        self.image_microbs = QIcon(self.config.gui_directory+'MICROBS.png')
        # some gui constants
        # # font
        self.font_name = 'Segoe UI'
        self.font_size = 11
        self.font_size_setting = 10
        self.font_size_setting_title = 9
        # # button
        self.font_size_button = 11
        self.button_font = QFont(self.font_name, self.font_size_button, QFont.Bold)
        self.button_height  = int(2.2 * self.font_size_button)
        # # button middle
        self.font_size_button_middle = 9
        self.button_middle_font = QFont(self.font_name, self.font_size_button_middle, QFont.Bold)
        self.button_middle_height  = int(2.4 * self.font_size_button_middle)
        # # combo box
        self.font_size_combo_box = 9
        self.combo_box_font = QFont(self.font_name, self.font_size_combo_box)
        self.combo_box_height = int(2.5 * self.font_size_combo_box)
        # # color
        self.color_red = QColor(255, 0, 0)
        self.color_green = QColor(34, 139, 34)
        # # position label
        self.label_position_text_style = 'color: blue;'
        # creating the gui panels
        # # left panel
        self.layout_left = QVBoxLayout()
        self.create_smaract_referencing_layout()
        self.layout_left.addWidget(self.group_box_smaract_referencing)
        self.create_pistage_referencing_layout()
        self.layout_left.addWidget(self.group_box_pistage_referencing)
        self.create_control_left_layout()
        self.layout_left.addWidget(self.group_box_control)
        self.create_automation_layout()
        self.layout_left.addWidget(self.group_box_automation)
        self.create_position_layout()
        self.layout_left.addWidget(self.group_box_position)
        self.widget_left = QWidget()
        self.widget_left.setLayout(self.layout_left)
        self.widget_left.setFixedSize(int(self.ppi * 4.25), int(self.ppi * 7.8))
        # # middle panel (camera image, control button, and copyright label)
        self.layout_middle = QVBoxLayout()
        self.create_camera_image_view_layout()
        self.layout_middle.addWidget(self.camera_image_view)
        self.create_control_middle_layout()   
        self.layout_middle.addWidget(self.widget_control_middle)
        self.create_microbs_layout()
        self.layout_middle.addWidget(self.label_copy_right)
        self.widget_middle = QWidget()
        self.widget_middle.setLayout(self.layout_middle)
        self.widget_middle.setFixedSize(int(self.ppi * 6.5), int(self.ppi * 7.8))
        # # right panel (setting)
        self.create_setting_layout()
        self.group_box_setting.setFixedSize(int(self.ppi * 3.75), int(self.ppi * 7.8))
        # setting the central widget
        # # Since the GUI class inherits from QMainWindow, we need a central widget. This object will be the parent for the rest of the GUI components.
        # # organizing the created elements in the entire GUI (horizontal placement)
        self.layout_general = QHBoxLayout()
        self.layout_general.addWidget(self.widget_left)
        self.layout_general.addWidget(self.widget_middle)
        self.layout_general.addWidget(self.group_box_setting)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout_general)
        # # background settings of the gui window
        self.centralWidget.setAttribute(Qt.WA_StyledBackground, True)
        self.centralWidget.setStyleSheet('background-color: white;')
        # setting some properties of the gui window
        self.setWindowIcon(self.image_microbs)
        self.setWindowTitle(self.config.gui_window_title)
        self.gui_width = int(self.ppi * 14.75)
        self.gui_height = int(self.ppi * 8.0)
        self.setFixedSize(self.gui_width, self.gui_height)
        # multithreading
        self.thread_pool = QThreadPool()
        # running the gamepad thread
        self.worker_gamepad = wt.WorkerGamepad(self.smaract, self.asm, self.pistage, self.gamepad, self.config)
        self.worker_gamepad.signals.progress_gamepad_status.connect(self.update_gamepad_status)
        self.worker_gamepad.signals.progress_smaract_control_status.connect(self.update_smaract_control_status)
        self.worker_gamepad.signals.progress_pistage_control_status.connect(self.update_pistage_control_status)
        self.worker_gamepad.signals.progress_smaract_speed_multiplier.connect(self.update_smaract_speed_multiplier)
        self.worker_gamepad.signals.progress_pistage_speed_multiplier.connect(self.update_pistage_speed_multiplier)
        self.worker_gamepad.signals.progress_position.connect(self.update_position)
        self.worker_gamepad.signals.progress_text_edit.connect(self.update_text_edit)
        self.thread_pool.start(self.worker_gamepad)
    
    def closeEvent(self, event):
        '''
        Overriding the closeEvent method to close the GUI window and stop the multithreading
        '''

        close = QMessageBox.question(self, 'Exit', 'Are you sure you want to exit?', QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            self.asm.close()
            self.smaract.close()
            self.pistage.close()
            self.camera.StopGrabbing()
            self.camera.Close()
            self.thread_pool.waitForDone(self.config.gui_close_window_time_ms)
            self.thread_pool.clear()
            os._exit(0)
        else:
            event.ignore()

    def create_smaract_referencing_layout(self):
        '''
        creating the smaract referencing panel in the gui
        '''

        self.layout_smaract_referencing = QGridLayout()
        # creating the Referencing button 
        self.button_smaract_referencing = QPushButton('Reference')
        self.button_smaract_referencing.setFont(self.button_font)
        self.button_smaract_referencing.setFixedHeight(self.button_height)
        self.button_smaract_referencing.setStyleSheet('background-color: #228B22; color: white; text-align: center; padding-bottom: 3px;')      
        self.button_smaract_referencing.clicked.connect(self.action_button_smaract_referencing)
        # creating the Positioning button
        self.button_smaract_positioning = QPushButton('Position')
        self.button_smaract_positioning.setFont(self.button_font)
        self.button_smaract_positioning.setFixedHeight(self.button_height)
        self.button_smaract_positioning.setStyleSheet('background-color: #1899D6; color: white; text-align: center; padding-bottom: 3px;')
        self.button_smaract_positioning.clicked.connect(self.action_button_smaract_positioning)
        # creating the labels and icons for the x, y, z, alpha, beta, and gamma channels
        self.label_smaract_referencing_x = QLabel('x:')
        self.label_smaract_referencing_x.setFont(QFont(self.font_name, self.font_size))
        self.label_smaract_referencing_x_image = QLabel()
        self.label_smaract_referencing_x_image.setPixmap(self.image_black)
        self.label_smaract_referencing_x_image.resize(self.image_black.width(), self.image_black.height())
        self.label_smaract_referencing_y = QLabel('y:')
        self.label_smaract_referencing_y.setFont(QFont(self.font_name, self.font_size))
        self.label_smaract_referencing_y_image = QLabel()
        self.label_smaract_referencing_y_image.setPixmap(self.image_black)
        self.label_smaract_referencing_y_image.resize(self.image_black.width(), self.image_black.height())
        self.label_smaract_referencing_z = QLabel('z:')
        self.label_smaract_referencing_z.setFont(QFont(self.font_name, self.font_size))
        self.label_smaract_referencing_z_image = QLabel()
        self.label_smaract_referencing_z_image.setPixmap(self.image_black)
        self.label_smaract_referencing_z_image.resize(self.image_black.width(), self.image_black.height())
        self.label_smaract_referencing_alpha = QLabel('alpha:')
        self.label_smaract_referencing_alpha.setFont(QFont(self.font_name, self.font_size))
        self.label_smaract_referencing_alpha_image = QLabel()
        self.label_smaract_referencing_alpha_image.setPixmap(self.image_black)
        self.label_smaract_referencing_alpha_image.resize(self.image_black.width(), self.image_black.height())
        self.label_smaract_referencing_beta = QLabel('beta:')
        self.label_smaract_referencing_beta.setFont(QFont(self.font_name, self.font_size))
        self.label_smaract_referencing_beta_image = QLabel()
        self.label_smaract_referencing_beta_image.setPixmap(self.image_black)
        self.label_smaract_referencing_beta_image.resize(self.image_black.width(), self.image_black.height())
        self.label_smaract_referencing_status_title = QLabel('Status:')
        self.label_smaract_referencing_status_title.setFont(QFont(self.font_name, self.font_size, QFont.Bold))
        self.label_smaract_referencing_status_text = QLabel(self.config.smaract_referencing_default_text)
        self.label_smaract_referencing_status_text.setFont(QFont(self.font_name, self.font_size))
        self.label_smaract_referencing_status_image = QLabel()
        self.label_smaract_referencing_status_image.setPixmap(self.image_black)
        self.label_smaract_referencing_status_image.resize(self.image_black.width(), self.image_black.height())
        # positioning the widgets in the layout (widget name, row, column, rowspan, colspan)
        self.layout_smaract_referencing.addWidget(self.button_smaract_referencing, 0, 0, 1, 10)
        self.layout_smaract_referencing.addWidget(self.button_smaract_positioning, 1, 0, 1, 10)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_x, 2, 0, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_x_image, 2, 1, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_y, 2, 2, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_y_image, 2, 3, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_z, 2, 4, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_z_image, 2, 5, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_alpha, 2, 6, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_alpha_image, 2, 7, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_beta, 2, 8, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_beta_image, 2, 9, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_status_title, 3, 0, 1, 2)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_status_image, 3, 2, 1, 1)
        self.layout_smaract_referencing.addWidget(self.label_smaract_referencing_status_text, 3, 3, 1, 7)
        # grouping the above widgets
        self.group_box_smaract_referencing = QGroupBox('SmarAct Referencing')
        self.group_box_smaract_referencing.setLayout(self.layout_smaract_referencing)

    def action_button_smaract_referencing(self):
        '''
        this function is called when the user clicks the smaract 'Reference' button.
        it starts the smaract referencing worker thread which is responsible for referencing the smaract channels.
        '''

        self.worker_smaract_referencing = wt.WorkerSmarActReferencing(self.smaract, self.config)
        self.worker_smaract_referencing.signals.progress.connect(self.update_smaract_referencing_status)
        self.thread_pool.start(self.worker_smaract_referencing)
        self.button_smaract_referencing.setEnabled(False)   

    def action_button_smaract_positioning(self):
        '''
        this function is called when the user clicks the smaract 'Positioning' button.
        it starts the smaract positioning worker thread which is responsible for moving the smaract channels to the desired positions.
        '''

        self.worker_smaract_positioning = wt.WorkerSmarActPositioning(self.smaract, self.config)
        self.worker_smaract_positioning.signals.progress_position.connect(self.update_position)
        self.worker_smaract_positioning.signals.progress_control_status.connect(self.update_smaract_control_status)
        self.worker_smaract_positioning.signals.progress_button.connect(self.update_button_smaract_positioning)
        self.thread_pool.start(self.worker_smaract_positioning)
        self.button_smaract_positioning.setEnabled(False)
        
    def create_pistage_referencing_layout(self):
        '''
        creating the pistage referencing panel in the gui
        '''

        self.layout_pistage_referencing = QGridLayout()
        # creating the Referencing button
        self.button_pistage_referencing = QPushButton('Reference')
        self.button_pistage_referencing.setFont(self.button_font)
        self.button_pistage_referencing.setFixedHeight(self.button_height)
        self.button_pistage_referencing.setStyleSheet('background-color: #228B22; color: white; text-align: center; padding-bottom: 3px;')      
        self.button_pistage_referencing.clicked.connect(self.action_button_pistage_referencing)
        # creating the Positioning button
        self.button_pistage_positioning = QPushButton('Position')
        self.button_pistage_positioning.setFont(self.button_font)
        self.button_pistage_positioning.setFixedHeight(self.button_height)
        self.button_pistage_positioning.setStyleSheet('background-color: #1899D6; color: white; text-align: center; padding-bottom: 3px;')
        self.button_pistage_positioning.clicked.connect(self.action_button_pistage_positioning)
        # creating the labels and icons for L1 and L2 axes
        self.label_pistage_referencing_l1 = QLabel('linear 1:')
        self.label_pistage_referencing_l1.setFont(QFont(self.font_name, self.font_size))
        self.label_pistage_referencing_l1_image = QLabel()
        self.label_pistage_referencing_l1_image.setPixmap(self.image_black)
        self.label_pistage_referencing_l1_image.resize(self.image_black.width(), self.image_black.height())
        self.label_pistage_referencing_l2 = QLabel('linear 2:')
        self.label_pistage_referencing_l2.setFont(QFont(self.font_name, self.font_size))
        self.label_pistage_referencing_l2_image = QLabel()
        self.label_pistage_referencing_l2_image.setPixmap(self.image_black)
        self.label_pistage_referencing_l2_image.resize(self.image_black.width(), self.image_black.height())
        # indicating the status of referencing 
        self.label_pistage_referencing_status_title = QLabel('Status:')
        self.label_pistage_referencing_status_title.setFont(QFont(self.font_name, self.font_size, QFont.Bold))
        self.label_pistage_referencing_status_text = QLabel(self.config.pistage_referencing_default_text)
        self.label_pistage_referencing_status_text.setFont(QFont(self.font_name, self.font_size))
        self.label_pistage_referencing_status_image = QLabel()
        self.label_pistage_referencing_status_image.setPixmap(self.image_black)
        self.label_pistage_referencing_status_image.resize(self.image_black.width(), self.image_black.height())
        # positioning the widgets in the layout (widget name, row, column, rowspan, colspan)
        self.layout_pistage_referencing.addWidget(self.button_pistage_referencing, 0, 0, 1, 6)
        self.layout_pistage_referencing.addWidget(self.button_pistage_positioning, 1, 0, 1, 6)
        self.layout_pistage_referencing.addWidget(self.label_pistage_referencing_l1, 2, 0, 1, 1)
        self.layout_pistage_referencing.addWidget(self.label_pistage_referencing_l1_image, 2, 2, 1, 1)
        self.layout_pistage_referencing.addWidget(self.label_pistage_referencing_l2, 2, 3, 1, 1)
        self.layout_pistage_referencing.addWidget(self.label_pistage_referencing_l2_image, 2, 4, 1, 1)
        self.layout_pistage_referencing.addWidget(self.label_pistage_referencing_status_title, 3, 0, 1, 2)
        self.layout_pistage_referencing.addWidget(self.label_pistage_referencing_status_image, 3, 2, 1, 1)
        self.layout_pistage_referencing.addWidget(self.label_pistage_referencing_status_text, 3, 3, 1, 3)
        # grouping the above widgets
        self.group_box_pistage_referencing = QGroupBox('PIStage Referencing')
        self.group_box_pistage_referencing.setLayout(self.layout_pistage_referencing)

    def action_button_pistage_referencing(self):
        '''
        this function is called when the user clicks the PIStage 'Reference' button.
        it starts the PIStage referencing worker thread which is responsible for referencing the PIStage axes.
        '''

        self.worker_pistage_referencing = wt.WorkerPIStageReferencing(self.pistage, self.config)
        self.worker_pistage_referencing.signals.progress.connect(self.update_pistage_referencing_status)
        self.thread_pool.start(self.worker_pistage_referencing)
        self.button_pistage_referencing.setEnabled(False)

    def action_button_pistage_positioning(self):
        '''
        this function is called when the user clicks the PIStage 'Positioning' button.
        it starts the PIstage positioning worker thread which is responsible for moving the PIstage axes to the desired positions.
        '''

        self.worker_pistage_positioning = wt.WorkerPIStagePositioning(self.pistage, self.config)
        self.worker_pistage_positioning.signals.progress_position.connect(self.update_position)
        self.worker_pistage_positioning.signals.progress_control_status.connect(self.update_pistage_control_status)
        self.worker_pistage_positioning.signals.progress_button.connect(self.update_button_pistage_positioning)
        self.thread_pool.start(self.worker_pistage_positioning)
        self.button_pistage_positioning.setEnabled(False)

    def create_control_left_layout(self):
        '''
        creating the Control panel in the GUI
        '''

        self.layout_control_left = QGridLayout()
        # indicating the status of Gamepad connection
        self.label_gamepad_title = QLabel('Gamepad Status:')
        self.label_gamepad_title.setFont(QFont(self.font_name, self.font_size, QFont.Bold))
        self.label_gamepad_text = QLabel(self.config.gamepad_not_found_text)
        self.label_gamepad_text.setFont(QFont(self.font_name, self.font_size))
        self.label_gamepad_text.setStyleSheet('color: red;')
        # indicating the control status of smaract 
        self.label_smaract_control_status_title = QLabel('SmarAct Mode:')
        self.label_smaract_control_status_title.setFont(QFont(self.font_name, self.font_size))
        self.label_smaract_control_status_text = QLabel(self.config.gui_empty_text)
        self.label_smaract_control_status_text.setFont(QFont(self.font_name, self.font_size))
        self.label_smaract_control_status_text.setStyleSheet('color: red;')
        # indicating the active axis of pistage
        self.label_pistage_control_status_title = QLabel('PIStage Axis:')
        self.label_pistage_control_status_title.setFont(QFont(self.font_name, self.font_size))
        self.label_pistage_control_status_text = QLabel(self.config.gui_empty_text)
        self.label_pistage_control_status_text.setFont(QFont(self.font_name, self.font_size))
        self.label_pistage_control_status_text.setStyleSheet('color: red;')
        # indicating the smaract speed multiplier
        self.label_smaract_speed = QLabel('SmarAct speed:')
        self.label_smaract_speed.setFont(QFont(self.font_name, self.font_size))
        self.spinner_smaract_speed = smaractSpinBox(self.config)
        self.spinner_smaract_speed.setValue(self.config.smaract_speed_multiplier_index)
        # indicating the pistage speed multiplier
        self.label_pistage_speed = QLabel('PIStage speed:')
        self.label_pistage_speed.setFont(QFont(self.font_name, self.font_size))
        self.spinner_pistage_speed = PIStageSpinBox(self.config)
        self.spinner_pistage_speed.setValue(self.config.pistage_speed_multiplier_index)
        # positioning the widgets in the layout (widget name, row, column, rowspan, colspan)
        self.layout_control_left.addWidget(self.label_gamepad_title, 0, 0, 1, 3)
        self.layout_control_left.addWidget(self.label_gamepad_text, 0, 3, 1, 3)
        self.layout_control_left.addWidget(self.label_smaract_control_status_title, 1, 0, 1, 2)
        self.layout_control_left.addWidget(self.label_smaract_control_status_text, 1, 2, 1, 1)
        self.layout_control_left.addWidget(self.label_pistage_control_status_title, 1, 3, 1, 2)
        self.layout_control_left.addWidget(self.label_pistage_control_status_text, 1, 5, 1, 1)
        self.layout_control_left.addWidget(self.label_smaract_speed, 2, 0, 1, 2)
        self.layout_control_left.addWidget(self.spinner_smaract_speed, 2, 2, 1, 1)
        self.layout_control_left.addWidget(self.label_pistage_speed, 2, 3, 1, 2)
        self.layout_control_left.addWidget(self.spinner_pistage_speed, 2, 5, 1, 1)
        # grouping the above widgets
        self.group_box_control = QGroupBox('Control')
        self.group_box_control.setLayout(self.layout_control_left)
    
    def create_automation_layout(self):
        '''
        creating the Automation panel in the GUI
        '''

        self.layout_automation = QGridLayout()
        # indicating the clicked coordinates of the tool 
        self.label_tool_title = QLabel('Tool:')
        self.label_tool_title.setFont(QFont(self.font_name, self.font_size, QFont.Bold))
        self.label_tool_text = QLabel(self.config.coords_empty_text)
        self.label_tool_text.setFont(QFont(self.font_name, self.font_size))
        self.label_tool_text.setStyleSheet('color: red;')
        # indicating the clicked coordinates of the target
        self.label_target_title = QLabel('Target:')
        self.label_target_title.setFont(QFont(self.font_name, self.font_size, QFont.Bold))
        self.label_target_text = QLabel(self.config.coords_empty_text)
        self.label_target_text.setFont(QFont(self.font_name, self.font_size))
        self.label_target_text.setStyleSheet('color: red;')
        # creating the Initialize button
        self.button_initialize = QPushButton('Initialize')
        self.button_initialize.setFont(self.button_font)
        self.button_initialize.setFixedHeight(self.button_height)
        self.button_initialize.setStyleSheet('background-color: #228B22; color: white; text-align: center; padding-bottom: 3px;')   
        self.button_initialize.clicked.connect(self.action_button_initialize)
        # creating the Sequencing button
        self.button_sequence = QPushButton('Sequence')
        self.button_sequence.setFont(self.button_font)	
        self.button_sequence.setFixedHeight(self.button_height)
        self.button_sequence.setStyleSheet('background-color: #1899D6; color: white; text-align: center; padding-bottom: 3px;')
        self.button_sequence.clicked.connect(self.action_button_sequence)
        # positioning the widgets in the layout (widget name, row, column, rowspan, colspan)
        self.layout_automation.addWidget(self.label_tool_title, 0, 0, 1, 1)
        self.layout_automation.addWidget(self.label_tool_text, 0, 1, 1, 2)
        self.layout_automation.addWidget(self.label_target_title, 0, 3, 1, 1)
        self.layout_automation.addWidget(self.label_target_text, 0, 4, 1, 2)
        self.layout_automation.addWidget(self.button_initialize, 1, 0, 1, 3)
        self.layout_automation.addWidget(self.button_sequence, 1, 3, 1, 3)
        # grouping the above widgets
        self.group_box_automation = QGroupBox('Automation')
        self.group_box_automation.setLayout(self.layout_automation)

    def action_button_initialize(self):
        '''
        initialzing the smaract channels prior to the sequencing procedure
        this function is called when the user clicks the 'Initialize' button.
        '''

        self.worker_sequence_initialize = wt.WorkerSequenceInitialize(self.smaract, self.config)
        self.worker_sequence_initialize.signals.progress_position.connect(self.update_position)
        self.worker_sequence_initialize.signals.progress_button.connect(self.update_button_initialize)
        self.thread_pool.start(self.worker_sequence_initialize)
        self.button_initialize.setEnabled(False)

    def action_button_sequence(self):
        '''
        starting the sequencing procedure to cut the embryo
        this function is called when the user clicks the 'Sequence' button.
        '''

        self.worker_sequence_do = wt.WorkerSequenceDo(self.smaract, self.asm, self.config)
        self.worker_sequence_do.signals.progress_position.connect(self.update_position)
        self.worker_sequence_do.signals.progress_button.connect(self.update_button_sequence)
        self.thread_pool.start(self.worker_sequence_do)
        self.button_sequence.setEnabled(False)
    
    def create_position_layout(self):
        '''
        creating the Positions panel in the GUI
        '''

        self.layout_position = QGridLayout()
        # indicating the absolute position of smaract x channel 
        self.label_position_x_title = QLabel('X (mm):')
        self.label_position_x_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_x_text = QLabel(self.config.gui_empty_text)
        self.label_position_x_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_x_text.setStyleSheet('color: red;')
        # indicating the absolute position of smaract y channel 
        self.label_position_y_title = QLabel('Y (mm):')
        self.label_position_y_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_y_text = QLabel(self.config.gui_empty_text)
        self.label_position_y_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_y_text.setStyleSheet('color: red;')
        # indicating the absolute position of smaract z channel 
        self.label_position_z_title = QLabel('Z (mm):')
        self.label_position_z_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_z_text = QLabel(self.config.gui_empty_text)
        self.label_position_z_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_z_text.setStyleSheet('color: red;')
        # indicating the absolute position of smaract alpha channel 
        self.label_position_alpha_title = QLabel('Alpha (deg):')
        self.label_position_alpha_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_alpha_text = QLabel(self.config.gui_empty_text)
        self.label_position_alpha_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_alpha_text.setStyleSheet('color: red;')
        # indicating the absolute position of smaract beta channel 
        self.label_position_beta_title = QLabel('Beta (deg):')
        self.label_position_beta_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_beta_text = QLabel(self.config.gui_empty_text)
        self.label_position_beta_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_beta_text.setStyleSheet('color: red;')
        # indicating the position of smaract gamma channel 
        self.label_position_gamma_title = QLabel('Gamma (step):')
        self.label_position_gamma_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_gamma_text = QLabel(self.config.gui_empty_text)
        self.label_position_gamma_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_gamma_text.setStyleSheet('color: red;')
        # indicating the position of ASM
        self.label_position_asm_title = QLabel('ASM (step):')
        self.label_position_asm_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_asm_text = QLabel(self.config.gui_empty_text)
        self.label_position_asm_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_asm_text.setStyleSheet('color: red;')
        # indicating the absolute position of PIStage L1 Axis
        self.label_position_l1_title = QLabel('L1 (mm):')
        self.label_position_l1_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_l1_text = QLabel(self.config.gui_empty_text)
        self.label_position_l1_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_l1_text.setStyleSheet('color: red;')
        # indicating the absolute position of PIStage L2 Axis
        self.label_position_l2_title = QLabel('L2 (mm):')
        self.label_position_l2_title.setFont(QFont(self.font_name, self.font_size))
        self.label_position_l2_text = QLabel(self.config.gui_empty_text)
        self.label_position_l2_text.setFont(QFont(self.font_name, self.font_size))
        self.label_position_l2_text.setStyleSheet('color: red;')
        # Positioning the widgets in the layout (widget name, row, column, rowspan, colspan)
        self.layout_position.addWidget(self.label_position_x_title, 0, 0, 1, 1)
        self.layout_position.addWidget(self.label_position_x_text, 0, 1, 1, 3)
        self.layout_position.addWidget(self.label_position_y_title, 0, 4, 1, 1)
        self.layout_position.addWidget(self.label_position_y_text, 0, 5, 1, 3)
        self.layout_position.addWidget(self.label_position_z_title, 1, 0, 1, 1)
        self.layout_position.addWidget(self.label_position_z_text, 1, 1, 1, 3)
        self.layout_position.addWidget(self.label_position_alpha_title, 2, 0, 1, 1)
        self.layout_position.addWidget(self.label_position_alpha_text, 2, 1, 1, 3)
        self.layout_position.addWidget(self.label_position_beta_title, 2, 4, 1, 1)
        self.layout_position.addWidget(self.label_position_beta_text, 2, 5, 1, 3)
        self.layout_position.addWidget(self.label_position_gamma_title, 3, 0, 1, 1)
        self.layout_position.addWidget(self.label_position_gamma_text, 3, 1, 1, 3)
        self.layout_position.addWidget(self.label_position_asm_title, 4, 0, 1, 1)
        self.layout_position.addWidget(self.label_position_asm_text, 4, 1, 1, 3)
        self.layout_position.addWidget(self.label_position_l1_title, 5, 0, 1, 1)
        self.layout_position.addWidget(self.label_position_l1_text, 5, 1, 1, 3)
        self.layout_position.addWidget(self.label_position_l2_title, 5, 4, 1, 1)
        self.layout_position.addWidget(self.label_position_l2_text, 5, 5, 1, 3)
        # grouping the above widgets
        self.group_box_position = QGroupBox('Positions')
        self.group_box_position.setLayout(self.layout_position)

    def create_camera_image_view_layout(self):
        '''
        creating the camera image panel in the gui
        '''
  
        self.camera_image_view = pg.ImageView()
        self.camera_image_view.show()
        # creating a black image
        self.camera_image_view.setImage(np.zeros((self.config.camera_height, self.config.camera_width), dtype=np.uint8)) 
        # removing extra features of ImageView
        self.camera_image_view.ui.histogram.hide()
        self.camera_image_view.ui.roiBtn.hide()
        self.camera_image_view.ui.menuBtn.hide()
        self.camera_image_view.scene.sigMouseClicked.connect(self.on_click)

    def on_click(self, event):
        '''
        handling the clicks on the camera image
        the first click corresponds to the target location and the second click corresponds to the tool (smaract end-effector) location. 
        this clicking order is just a design choice and can be easily changed.
        '''

        mouse_point = self.camera_image_view.view.mapSceneToView(event._scenePos)
        self.config.coords_temp.append((int(mouse_point.x()), int(mouse_point.y())))
        if len(self.config.coords_temp) == 1:
            if not aux.clicked_position_is_valid(self.config, self.config.coords_temp[0][0], self.config.coords_temp[0][1]):
                self.update_text_edit(self.config.gui_err_clicked_pos_invalid, self.config.text_edit_mode_err)
                self.config.coords_temp = []
            else:
                self.config.coords_target.append((self.config.coords_temp[0][0], self.config.coords_temp[0][1]))
                self.label_target_text.setText('x: {:d}, y: {:d}'.format(int(self.config.coords_temp[0][0]), int(self.config.coords_temp[0][1])))
                self.label_target_text.setStyleSheet('color: blue;')
        elif len(self.config.coords_temp) == 2:
            if not aux.clicked_position_is_valid(self.config, self.config.coords_temp[1][0], self.config.coords_temp[1][1]):
                self.update_text_edit(self.config.gui_err_clicked_pos_invalid, self.config.text_edit_mode_err)
                self.config.coords_temp.pop()
            else:
                # preparing the movement of smaract channels to the target location
                y_movement = (self.config.coords_temp[1][1] - self.config.coords_temp[0][1]) * self.config.pixel_to_mili * self.config.mili_to_nano
                x_movement = (self.config.coords_temp[1][0] - self.config.coords_temp[0][0]) * self.config.pixel_to_mili * self.config.mili_to_nano
                speed = self.config.smaract_linear_speed_on_click
                if not aux.smaract_is_valid_relative_movement(self.config, self.config.smaract_channel_x, self.smaract.get_channel_position(self.config.smaract_channel_x), x_movement):
                    self.update_text_edit(self.config.smaract_err_x_not_reachable, self.config.text_edit_mode_err)
                    self.config.coords_temp.pop()
                elif not aux.smaract_is_valid_relative_movement(self.config, self.config.smaract_channel_y, self.smaract.get_channel_position(self.config.smaract_channel_y), y_movement):
                    self.update_text_edit(self.config.smaract_err_y_not_reachable, self.config.text_edit_mode_err)
                    self.config.coords_temp.pop()
                else:
                    if not aux.smaract_is_valid_speed(self.config, self.config.smaract_channel_x, speed):   # using channel x in the place of both x and y channels as they both have the same speed
                        self.update_text_edit(self.config.smaract_err_linear_speed_invalid, self.config.text_edit_mode_err)
                        self.config.coords_temp.pop()
                    else:
                        self.config.coords_tool.append((self.config.coords_temp[1][0], self.config.coords_temp[1][1]))
                        self.label_tool_text.setText('x: {:d}, y: {:d}'.format(int(self.config.coords_temp[1][0]), int(self.config.coords_temp[1][1])))
                        self.label_tool_text.setStyleSheet('color: green;')
                        self.smaract.move_channel(self.config.smaract_channel_x, x_movement, speed)
                        self.label_position_x_text.setText('{:.2f}'.format(self.smaract.get_channel_position(self.config.smaract_channel_x) / self.config.mili_to_nano))
                        self.label_position_x_text.setStyleSheet('color: blue;')
                        self.smaract.move_channel(self.config.smaract_channel_y, y_movement, speed)
                        self.label_position_y_text.setText('{:.2f}'.format(self.smaract.get_channel_position(self.config.smaract_channel_y) / self.config.mili_to_nano))
                        self.label_position_y_text.setStyleSheet('color: blue;')
                        self.config.coords_temp = []

    def create_control_middle_layout(self):
        '''
        creating the middle control panel in the gui
        '''

        self.layout_control_middle = QGridLayout()
        # creating the Start Camera button
        self.button_camera_start = QPushButton('Start Camera')
        self.button_camera_start.setFont(self.button_middle_font)	
        self.button_camera_start.setFixedHeight(self.button_middle_height)
        self.button_camera_start.setStyleSheet('background-color: #077b8a; color: white; text-align: center; padding-bottom: 3px;')
        self.button_camera_start.clicked.connect(self.action_button_camera_start)
        # creating the Stop Camera button
        self.button_camera_stop = QPushButton('Stop Camera')
        self.button_camera_stop.setFont(self.button_middle_font)
        self.button_camera_stop.setFixedHeight(self.button_middle_height)
        self.button_camera_stop.setStyleSheet('background-color: #d72631; color: white; text-align: center; padding-bottom: 3px;')
        self.button_camera_stop.setEnabled(False)
        self.button_camera_stop.clicked.connect(self.action_button_camera_stop)
        # creating the Save Image button
        self.button_camera_save = QPushButton('Save Image')
        self.button_camera_save.setFont(self.button_middle_font)
        self.button_camera_save.setFixedHeight(self.button_middle_height)
        self.button_camera_save.setStyleSheet('background-color: #9B59B6; color: white; text-align: center; padding-bottom: 3px;')
        self.button_camera_save.clicked.connect(self.action_button_camera_save)
        # creating the Annotate Embryo button
        self.button_annotate_embryo = QPushButton('Annotate Embryo')
        self.button_annotate_embryo.setFont(self.button_middle_font)
        self.button_annotate_embryo.setFixedHeight(self.button_middle_height)
        self.button_annotate_embryo.setStyleSheet('background-color: #E67E22; color: white; text-align: center; padding-bottom: 3px;')
        self.button_annotate_embryo.clicked.connect(self.action_button_annotate_embryo)
        # creating the Annotate Scissor button
        self.button_annotate_scissor = QPushButton('Annotate Scissor')
        self.button_annotate_scissor.setFont(self.button_middle_font)
        self.button_annotate_scissor.setFixedHeight(self.button_middle_height)
        self.button_annotate_scissor.setStyleSheet('background-color: #52BE80; color: white; text-align: center; padding-bottom: 3px;')
        self.button_annotate_scissor.clicked.connect(self.action_button_annotate_scissor)
        # creating the Clear Annotation button
        self.button_annotation_clear = QPushButton('Clear Annotation')
        self.button_annotation_clear.setFont(self.button_middle_font)
        self.button_annotation_clear.setFixedHeight(self.button_middle_height)
        self.button_annotation_clear.setStyleSheet('background-color: #34495E; color: white; text-align: center; padding-bottom: 3px;')
        self.button_annotation_clear.clicked.connect(self.action_button_annotation_clear)
        # creating the Automate button
        self.button_automation_start = QPushButton('Automate')
        self.button_automation_start.setFont(self.button_middle_font)
        self.button_automation_start.setFixedHeight(self.button_middle_height)
        self.button_automation_start.setStyleSheet('background-color: #c68642; color: white; text-align: center; padding-bottom: 3px;')  
        self.button_automation_start.clicked.connect(self.action_button_automation_start)
        # creating the Stop Automation button	
        self.button_automation_stop = QPushButton('Stop Automation')
        self.button_automation_stop.setFont(self.button_middle_font)
        self.button_automation_stop.setFixedHeight(self.button_middle_height)
        self.button_automation_stop.setStyleSheet('background-color: #A93226; color: white; text-align: center; padding-bottom: 3px;')
        self.button_automation_stop.clicked.connect(self.action_button_automation_stop)
        self.button_automation_stop.setEnabled(False)
        # creating the Reconnect button
        self.button_reconnection = QPushButton('Reconnect')
        self.button_reconnection.setFont(self.button_middle_font)
        self.button_reconnection.setFixedHeight(self.button_middle_height)
        self.button_reconnection.setStyleSheet('background-color: #fe8a71; color: white; text-align: center; padding-bottom: 3px;')
        self.button_reconnection.clicked.connect(self.action_button_reconnection)
        self.button_reconnection.setEnabled(False)
        # positioning the widgets in the layout (widget name, row, column, rowspan, colspan)
        self.layout_control_middle.addWidget(self.button_camera_start, 0, 0, 1, 1)
        self.layout_control_middle.addWidget(self.button_camera_stop, 0, 1, 1, 1)
        self.layout_control_middle.addWidget(self.button_camera_save, 0, 2, 1, 1)
        self.layout_control_middle.addWidget(self.button_annotate_embryo, 1, 0, 1, 1)
        self.layout_control_middle.addWidget(self.button_annotate_scissor, 1, 1, 1, 1)
        self.layout_control_middle.addWidget(self.button_annotation_clear, 1, 2, 1, 1)
        self.layout_control_middle.addWidget(self.button_automation_start, 2, 0, 1, 1)
        self.layout_control_middle.addWidget(self.button_automation_stop, 2, 1, 1, 1)
        self.layout_control_middle.addWidget(self.button_reconnection, 2, 2, 1, 1)
        # grouping the above widgets
        self.widget_control_middle = QWidget()
        self.widget_control_middle.setLayout(self.layout_control_middle)
    
    def action_button_camera_start(self):
        '''
        starting to acquire images with the camera
        this function is called when the user clicks the 'Start Camera' button.
        '''

        self.button_camera_start.setEnabled(False)
        self.config.camera_flag_off = False
        self.worker_camera = wt.WorkerCamera(self.camera, self.config)
        self.worker_camera.signals.progress.connect(self.update_camera_image_view)
        self.thread_pool.start(self.worker_camera)
        self.button_camera_stop.setEnabled(True)

    def action_button_camera_stop(self):
        '''
        stopping the camera
        this function is called when the user clicks the 'Stop Camera' button.
        '''

        self.button_camera_stop.setEnabled(False)
        self.config.camera_flag_off = True
        self.camera.StopGrabbing()
        self.camera.Close()
        self.config.annotation_embryo_points, self.config.annotation_scissor_points, self.config.annotation_points = [], [], []
        self.label_target_text.setText(self.config.coords_empty_text)
        self.label_target_text.setStyleSheet('color: red;')
        self.label_tool_text.setText(self.config.coords_empty_text)
        self.label_tool_text.setStyleSheet('color: red;')
        self.button_camera_start.setEnabled(True)

    def action_button_camera_save(self):
        '''
        this function is called when the user clicks the 'Save Image' button.
        '''

        if self.config.camera_flag_off:
            self.update_text_edit(self.config.camera_err_off, self.config.text_edit_mode_err)
            return
        self.button_camera_save.setEnabled(False)
        img = aux.normalize_image(self.config.camera_image)
        vision.save_image(img, str(self.config.save_counter), self.config.save_directory)
        self.config.save_counter = self.config.save_counter + 1
        self.button_camera_save.setEnabled(True)

    def action_button_annotate_embryo(self):
        '''
        annotating the acquired image with the coordinates of the desired keypoints of embryo
        this function is called when the user clicks the 'Annotate Embryo' button.
        '''

        if self.config.camera_flag_off:
            self.update_text_edit(self.config.camera_err_off, self.config.text_edit_mode_err)
            return
        # initializing
        self.button_annotate_embryo.setEnabled(False)
        if self.config.annotation_flag_stop_camera:
            self.camera.StopGrabbing()
            self.camera.AcquisitionStop.Execute()
            self.camera.TLParamsLocked = False
        # annotating
        flag, err = aux.annotate_embryo(self.config, self.model)
        if flag == False:
            # self.config.annotation_embryo_points, self.config.annotation_points = [], []
            self.config.annotation_points = list(set(self.config.annotation_points)-set(self.config.annotation_embryo_points))   
            self.config.annotation_embryo_points = []
            self.update_text_edit(err, self.config.text_edit_mode_err)
            if self.config.annotation_flag_stop_camera:
                self.camera.TLParamsLocked = True
                self.camera.AcquisitionStart.Execute()
                self.camera.StartGrabbing(1)
            self.config.annotation_embryo_counter = self.config.annotation_embryo_counter + 1
            self.button_annotate_embryo.setEnabled(True)
            return
        # reinitalizing
        if self.config.annotation_flag_stop_camera:
            self.camera.TLParamsLocked = True
            self.camera.AcquisitionStart.Execute()
            self.camera.StartGrabbing(1)
        self.config.annotation_embryo_counter = self.config.annotation_embryo_counter + 1
        self.button_annotate_embryo.setEnabled(True)

    def action_button_annotate_scissor(self):
        '''
        annotating the acquired image with the coordinates of the desired keypoint of scissor
        this function is called when the user clicks the 'Annotate Scissor' button.
        '''

        if self.config.camera_flag_off:
            self.update_text_edit(self.config.camera_err_off, self.config.text_edit_mode_err)
            return
        # initializing
        self.button_annotate_scissor.setEnabled(False)
        if self.config.annotation_flag_stop_camera:
            self.camera.StopGrabbing()
            self.camera.AcquisitionStop.Execute()
            self.camera.TLParamsLocked = False
        # annotating
        flag, err = aux.annotate_scissor(self.config)
        if flag == False:
            # self.config.annotation_scissor_points, self.config.annotation_points = [], []
            self.config.annotation_points = list(set(self.config.annotation_points)-set(self.config.annotation_scissor_points)) 
            self.config.annotation_scissor_points = []
            self.update_text_edit(err, self.config.text_edit_mode_err)
            if self.config.annotation_flag_stop_camera:
                self.camera.TLParamsLocked = True
                self.camera.AcquisitionStart.Execute()
                self.camera.StartGrabbing(1)
            self.config.annotation_scissor_counter = self.config.annotation_scissor_counter + 1
            self.button_annotate_scissor.setEnabled(True)
            return
        # reinitalizing
        if self.config.annotation_flag_stop_camera:
            self.camera.TLParamsLocked = True
            self.camera.AcquisitionStart.Execute()
            self.camera.StartGrabbing(1)
        self.config.annotation_scissor_counter = self.config.annotation_scissor_counter + 1
        self.button_annotate_scissor.setEnabled(True)

    def action_button_annotation_clear(self):
        '''
        this function is called when the user clicks the 'Clear Annotation' button.
        '''

        self.button_annotation_clear.setEnabled(False)
        self.config.annotation_embryo_points, self.config.annotation_scissor_points, self.config.annotation_points = [], [], []
        self.label_target_text.setText(self.config.coords_empty_text)
        self.label_target_text.setStyleSheet('color: red;')
        self.label_tool_text.setText(self.config.coords_empty_text)
        self.label_tool_text.setStyleSheet('color: red;')
        self.button_annotation_clear.setEnabled(True)

    def action_button_automation_start(self):
        '''
        this function is called when the user clicks the 'Automate' button.
        '''

        if self.config.camera_flag_off:
            self.update_text_edit(self.config.camera_err_off, self.config.text_edit_mode_err)
            return
        self.button_automation_start.setEnabled(False)
        self.config.automation_flag_stopped = False
        self.worker_automation = wt.WorkerAutomation(self.smaract, self.asm, self.pistage, self.camera, self.config, self.model)
        self.worker_automation.signals.progress_position.connect(self.update_position)
        self.worker_automation.signals.progress_text_edit.connect(self.update_text_edit)
        self.worker_automation.signals.progress_coord.connect(self.update_coord)
        self.worker_automation.signals.progress_button.connect(self.update_button_automation_start)
        self.thread_pool.start(self.worker_automation)
        self.button_automation_stop.setEnabled(True)
    
    def action_button_automation_stop(self):
        '''
        this function is called when the user clicks the 'Stop Automation' button.
        '''

        self.button_automation_stop.setEnabled(False)
        self.config.automation_flag_stopped = True
        aux.stop(self.smaract, self.pistage, self.asm, self.config)
        self.update_text_edit(self.config.automation_message_stopped, self.config.text_edit_mode_err)
        self.button_reconnection.setEnabled(True)

    def action_button_reconnection(self):
        '''
        this function is called when the user clicks the 'Reconnect' button.
        '''

        self.button_reconnection.setEnabled(False)
        self.config.automation_flag_stopped = False
        self.worker_reconnection = wt.WorkerReconnection(self.smaract, self.asm, self.config)
        self.worker_reconnection.signals.progress.connect(self.update_text_edit)
        self.thread_pool.start(self.worker_reconnection)
        self.button_automation_start.setEnabled(True)
        
    @pyqtSlot()
    def update_camera_image_view(self):
        '''
        this function is called when the camera has acquired a new image. it updates the image shown in the GUI.
        '''

        if len(self.config.annotation_points) == 0: # the image to be shown here is mono8 (grayscale)
            # the camera image is transposed to match the desired orientation.
            self.camera_image_view.setImage(np.transpose(self.config.camera_image))
            self.label_target_text.setText(self.config.coords_empty_text)
            self.label_target_text.setStyleSheet('color: red;')
            self.label_tool_text.setText(self.config.coords_empty_text)
            self.label_tool_text.setStyleSheet('color: red;')
        else:   # the image to be shown here is rgb
            img = aux.normalize_image(self.config.camera_image)
            img_drawn = vision.draw_points(np.float32(img), self.config.annotation_points, self.config.annotation_point_offset)
            # the camera image is transposed to match the desired orientation.
            img_drawn = np.transpose(img_drawn, (1, 0, 2))
            # converting bgr format (the opencv default) to rgb
            img_show = img_drawn.copy()
            img_show[:, :, 0] = img_drawn[:, :, 2]
            img_show[:, :, 2] = img_drawn[:, :, 0]
            self.camera_image_view.setImage(img_show)

    def create_microbs_layout(self):
        '''
        creating the MICROBS copyright panel in the gui
        '''	

        self.label_copy_right = QLabel(u'\u00a9' + ' MICROBS, EPFL, 2022-'+time.strftime('%Y', time.localtime()))
        self.label_copy_right.setAlignment(Qt.AlignCenter)
        self.label_copy_right.setStyleSheet('color: gray;')
        self.label_copy_right.setFont(QFont(self.font_name, self.font_size))

    def create_setting_layout(self):
        '''
        creating the setting panel in the gui
        '''

        self.layout_setting = QGridLayout()
        # creating the settings of camera
        self.label_camera_title = QLabel('Camera')
        self.label_camera_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_camera = QComboBox()
        self.combo_box_camera.setFont(self.combo_box_font)
        self.combo_box_camera.setFixedHeight(self.combo_box_height)
        self.combo_box_camera.addItems(['Width (px)', 'Height (px)'])
        self.combo_box_camera.setCurrentIndex(0)
        self.combo_box_camera.activated.connect(self.on_camera_combo_box)
        self.line_edit_camera = QLineEdit()
        self.line_edit_camera.setText(str(self.config.camera_width))
        self.line_edit_camera.returnPressed.connect(self.on_camera_line_edit)
        # creating the settings of smaract linear channels
        self.label_smaract_linear_title = QLabel('SmarAct Linear Channels')
        self.label_smaract_linear_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_smaract_linear = QComboBox()
        self.combo_box_smaract_linear.setFont(self.combo_box_font)
        self.combo_box_smaract_linear.setFixedHeight(self.combo_box_height)
        self.combo_box_smaract_linear.addItems(['Base Step (nm)', 'Positioning X and Y (nm)',
                                                'Positioning Z (nm)', 'Base Speed (nm/s)', 'Positioning Speed (nm/s)',
                                                'On-click Speed (nm/s)', 'Positioning Sleep Multiplier']) 
        self.combo_box_smaract_linear.setCurrentIndex(0)
        self.combo_box_smaract_linear.activated.connect(self.on_smaract_linear_combo_box)
        self.line_edit_smaract_linear = QLineEdit()
        self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_steps_base))
        self.line_edit_smaract_linear.returnPressed.connect(self.on_smaract_linear_line_edit)
        # creating the settings of smaract angular channels
        self.label_smaract_angular_title = QLabel('SmarAct Angular Channels')
        self.label_smaract_angular_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_smaract_angular = QComboBox()
        self.combo_box_smaract_angular.setFont(self.combo_box_font)
        self.combo_box_smaract_angular.setFixedHeight(self.combo_box_height)
        self.combo_box_smaract_angular.addItems(['Base Step (uDeg)', 'Positioning Alpha (uDeg)',
                                                 'Positioning Beta (uDeg)', 'Base Speed (uDeg/s)',
                                                 'Positioning Speed (uDeg/s)', 'Positioning Sleep Multiplier']) 
        self.combo_box_smaract_angular.setCurrentIndex(0)
        self.combo_box_smaract_angular.activated.connect(self.on_smaract_angular_combo_box)
        self.line_edit_smaract_angular = QLineEdit()
        self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_steps_base))
        self.line_edit_smaract_angular.returnPressed.connect(self.on_smaract_angular_line_edit)
        # creating the settings of smaract gamma channel
        self.label_smaract_gamma_title = QLabel('SmarAct Gamma channel')
        self.label_smaract_gamma_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_smaract_gamma = QComboBox()
        self.combo_box_smaract_gamma.setFont(self.combo_box_font)
        self.combo_box_smaract_gamma.setFixedHeight(self.combo_box_height)
        self.combo_box_smaract_gamma.addItems(['Base Step', 'Base Frequency (Hz)'])
        self.combo_box_smaract_gamma.setCurrentIndex(0)
        self.combo_box_smaract_gamma.activated.connect(self.on_smaract_gamma_combo_box)
        self.line_edit_smaract_gamma = QLineEdit()
        self.line_edit_smaract_gamma.setText(str(self.config.smaract_gamma_steps_base))
        self.line_edit_smaract_gamma.returnPressed.connect(self.on_smaract_gamma_line_edit)
        # creating the settings of pistage
        self.label_pistage_title = QLabel('PIStage')
        self.label_pistage_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_pistage = QComboBox()
        self.combo_box_pistage.setFont(self.combo_box_font)
        self.combo_box_pistage.setFixedHeight(self.combo_box_height)
        self.combo_box_pistage.addItems(['Base Step (mm)', 'Positioning L1 (mm)', 'Positioning L2 (mm)',
                                         'Base Speed (mm/s)', 'Positioning Speed (mm/s)', 'Positioning Sleep Multiplier'])
        self.combo_box_pistage.setCurrentIndex(0)
        self.combo_box_pistage.activated.connect(self.on_pistage_combo_box)
        self.line_edit_pistage = QLineEdit()
        self.line_edit_pistage.setText(str(self.config.pistage_steps_base))
        self.line_edit_pistage.returnPressed.connect(self.on_pistage_line_edit)
        # creating the settings of asm
        self.label_asm_title = QLabel('ASM')
        self.label_asm_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_asm = QComboBox()
        self.combo_box_asm.setFont(self.combo_box_font)
        self.combo_box_asm.setFixedHeight(self.combo_box_height)
        self.combo_box_asm.addItems(['Step', 'Delay (ms)'])
        self.combo_box_asm.setCurrentIndex(0)
        self.combo_box_asm.activated.connect(self.on_asm_combo_box)
        self.line_edit_asm = QLineEdit()
        self.line_edit_asm.setText(str(self.config.asm_steps_base))
        self.line_edit_asm.returnPressed.connect(self.on_asm_line_edit)
        # creating the settings of sequence
        self.label_sequence_title = QLabel('Sequencing')
        self.label_sequence_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_sequence = QComboBox()
        self.combo_box_sequence.setFont(self.combo_box_font)
        self.combo_box_sequence.setFixedHeight(self.combo_box_height)
        self.combo_box_sequence.addItems(['SmarAct Linear Speed (nm/s)', 'SmarAct Angular Speed (uDeg/s)',
                                          'Initial Alpha (uDeg)', 'Initial Beta (uDeg)', 'Initial Z (nm)',
                                          'ASM Sleep Time (s)', 'Sleep Multiplier (Initialize)', 'Sleep Multiplier (Sequence)',
                                          'Flag (Release Debris)'])
        self.combo_box_sequence.setCurrentIndex(0)
        self.combo_box_sequence.activated.connect(self.on_sequence_combo_box)
        self.line_edit_sequence = QLineEdit()
        self.line_edit_sequence.setText(str(self.config.sequence_linear_speed))
        self.line_edit_sequence.returnPressed.connect(self.on_sequence_line_edit)
        self.label_sequence_delta_z = QLabel('Delta Zs (um):')
        self.label_sequence_delta_z.setFont(QFont(self.font_name, self.font_size_setting))
        self.line_edit_sequence_delta_z = QLineEdit()
        self.line_edit_sequence_delta_z.setText(','.join(str(item) for item in self.config.sequence_delta_z))
        self.line_edit_sequence_delta_z.returnPressed.connect(self.on_sequence_delta_z_line_edit)
        self.label_sequence_delta_y = QLabel('Delta Ys (um):')
        self.label_sequence_delta_y.setFont(QFont(self.font_name, self.font_size_setting))
        self.line_edit_sequence_delta_y = QLineEdit()
        self.line_edit_sequence_delta_y.setText(','.join(str(item) for item in self.config.sequence_delta_y))
        self.line_edit_sequence_delta_y.returnPressed.connect(self.on_sequence_delta_y_line_edit)
        # creating the settings of genral annotation
        self.label_annotation_title = QLabel('General Annotation')
        self.label_annotation_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_annotation = QComboBox()
        self.combo_box_annotation.setFont(self.combo_box_font)
        self.combo_box_annotation.setFixedHeight(self.combo_box_height)
        self.combo_box_annotation.addItems(['Edge Level 1', 'Edge Level 2', 'Edge Aperture Size (px)', 'Edge L2 Gradient',
                                            'Closing Kernel Size (px)', 'Closing Iterations', 'Blurring Sigma X', 'Min Area (px)',
                                            'Flag (Save Image)', 'Flag (Stop Camera)'])
        self.combo_box_annotation.setCurrentIndex(0)
        self.combo_box_annotation.activated.connect(self.on_annotation_combo_box)
        self.line_edit_annotation = QLineEdit()
        self.line_edit_annotation.setText(str(self.config.annotation_edge_level_1))
        self.line_edit_annotation.returnPressed.connect(self.on_annotation_line_edit)
        # creating the settings of embryo annotation
        self.label_annotation_embryo_title = QLabel('Embryo Annotation')
        self.label_annotation_embryo_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_annotation_embryo = QComboBox()
        self.combo_box_annotation_embryo.setFont(self.combo_box_font)
        self.combo_box_annotation_embryo.setFixedHeight(self.combo_box_height)
        self.combo_box_annotation_embryo.addItems(['Gray Level 1', 'Gray Level 2', 'Crop Middle Offset (px)',
                                                   'Crop Offset (px)', 'Fill Offset (px)',
                                                   'Openning Kernel Size (px)', 'Openning Iterations',
                                                   'Circle Dp', 'Circle Param 1', 'Circle Param 2',
                                                   'Point Offset X (px)', 'Point Offset Y (px)',
                                                   'Flag (0:CV or 1:DN)'])
        self.combo_box_annotation_embryo.setCurrentIndex(0)
        self.combo_box_annotation_embryo.activated.connect(self.on_annotation_embryo_combo_box)
        self.line_edit_annotation_embryo = QLineEdit()
        self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_gray_level_1))
        self.line_edit_annotation_embryo.returnPressed.connect(self.on_annotation_embryo_line_edit)
        # creating the settings of scissor annotation
        self.label_annotation_scissor_title = QLabel('Scissor Annotation')
        self.label_annotation_scissor_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_annotation_scissor = QComboBox()
        self.combo_box_annotation_scissor.setFont(self.combo_box_font)
        self.combo_box_annotation_scissor.setFixedHeight(self.combo_box_height)
        self.combo_box_annotation_scissor.addItems(['Gray Level', 'Crop Offset (px)', 'Line Rho', 'Line Theta (deg)',
                                                    'Diagonal Offset (px)', 'Diagonal Vote', 'Diagonal Min Length (px)',
                                                    'Diagonal Max Gap (px)', 'Diagonal Min Slope (deg)', 'Diagonal Max Slope (deg)'])	
        self.combo_box_annotation_scissor.setCurrentIndex(0)
        self.combo_box_annotation_scissor.activated.connect(self.on_annotation_scissor_combo_box)
        self.line_edit_annotation_scissor = QLineEdit()
        self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_gray_level))
        self.line_edit_annotation_scissor.returnPressed.connect(self.on_annotation_scissor_line_edit)
        # creating the settings of automation
        self.label_automation_title = QLabel('Automation')
        self.label_automation_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_automation = QComboBox()
        self.combo_box_automation.setFont(self.combo_box_font)
        self.combo_box_automation.setFixedHeight(self.combo_box_height)
        self.combo_box_automation.addItems(['L1 Num', 'L2 Num', 'L1 Step (mm)', 'L2 Step (mm)', 
                                            'SmarAct Speed (nm/s)', 'PIStage Speed (mm/s)',
                                            'SmarAct Sleep Multiplier', 'PIStage Sleep Multiplier',
                                            'Flag (Save Image)', 'Flag (Release Debris)', 'Flag (0:CV or 1:DN)', 'Wait time (sec)'])	
        self.combo_box_automation.setCurrentIndex(0)
        self.combo_box_automation.activated.connect(self.on_automation_combo_box)
        self.line_edit_automation = QLineEdit()
        self.line_edit_automation.setText(str(self.config.automation_num_l1))
        self.line_edit_automation.returnPressed.connect(self.on_automation_line_edit)
        # creating the settings of deep network
        self.label_deep_network_title = QLabel('Deep Tube')
        self.label_deep_network_title.setFont(QFont(self.font_name, self.font_size_setting_title, QFont.Bold))
        self.combo_box_deep_network = QComboBox()
        self.combo_box_deep_network.setFont(self.combo_box_font)
        self.combo_box_deep_network.setFixedHeight(self.combo_box_height)
        self.combo_box_deep_network.addItems(['Somite Height (um)', 'Somite Target', 'Threshold (0-1)'])
        self.combo_box_deep_network.setCurrentIndex(0)
        self.combo_box_deep_network.activated.connect(self.on_deep_network_combo_box)
        self.line_edit_deep_network = QLineEdit()
        self.line_edit_deep_network.setText(str(self.config.dn_somite_height_um))
        self.line_edit_deep_network.returnPressed.connect(self.on_deep_network_line_edit)
        # creating the text edit
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont(self.font_name, self.font_size_setting))
        self.text_edit.setTextColor(self.color_red)
        self.text_edit.setText(self.config.gui_empty_text)

        # positionning the widgets in the layout (widget name, row, column, rowspan, colspan)
        # # camera settings
        self.layout_setting.addWidget(self.label_camera_title, 0, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_camera, 1, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_camera, 1, 3, 1, 1)
        # # smaract linear channels settings
        self.layout_setting.addWidget(self.label_smaract_linear_title, 2, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_smaract_linear, 3, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_smaract_linear, 3, 3, 1, 1)
        # # smaract angular channels settings
        self.layout_setting.addWidget(self.label_smaract_angular_title, 4, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_smaract_angular, 5, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_smaract_angular, 5, 3, 1, 1)
        # # smaract gamma channel settings
        self.layout_setting.addWidget(self.label_smaract_gamma_title, 6, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_smaract_gamma, 7, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_smaract_gamma, 7, 3, 1, 1)
        # # pistage settings
        self.layout_setting.addWidget(self.label_pistage_title, 8, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_pistage, 9, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_pistage, 9, 3, 1, 1)
        # # asm settings
        self.layout_setting.addWidget(self.label_asm_title, 10, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_asm, 11, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_asm, 11, 3, 1, 1)
        # # sequence settings
        self.layout_setting.addWidget(self.label_sequence_title, 12, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_sequence, 13, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_sequence, 13, 3, 1, 1)
        self.layout_setting.addWidget(self.label_sequence_delta_z, 14, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_sequence_delta_z, 14, 3, 1, 1)
        self.layout_setting.addWidget(self.label_sequence_delta_y, 15, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_sequence_delta_y, 15, 3, 1, 1)
        # # general annotation settings
        self.layout_setting.addWidget(self.label_annotation_title, 16, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_annotation, 17, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_annotation, 17, 3, 1, 1)
        # # embryo annotation settings
        self.layout_setting.addWidget(self.label_annotation_embryo_title, 18, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_annotation_embryo, 19, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_annotation_embryo, 19, 3, 1, 1)
        # # scissor annotation settings
        self.layout_setting.addWidget(self.label_annotation_scissor_title, 20, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_annotation_scissor, 21, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_annotation_scissor, 21, 3, 1, 1)
        # # automation settings
        self.layout_setting.addWidget(self.label_automation_title, 22, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_automation, 23, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_automation, 23, 3, 1, 1)
        # # deep network settings
        self.layout_setting.addWidget(self.label_deep_network_title, 24, 0, 1, 4)
        self.layout_setting.addWidget(self.combo_box_deep_network, 25, 0, 1, 3)
        self.layout_setting.addWidget(self.line_edit_deep_network, 25, 3, 1, 1)
        # # text edit
        self.layout_setting.addWidget(self.text_edit, 26, 0, 1, 4)

        # collecting above widgets under the same group and naming it
        self.group_box_setting = QGroupBox('Settings')
        self.group_box_setting.setLayout(self.layout_setting)

    def on_camera_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of camera in settings.
        '''

        if index == 0:      # width
            self.line_edit_camera.setText(str(self.config.camera_width))
        elif index == 1:    # height
            self.line_edit_camera.setText(str(self.config.camera_height))

    def on_camera_line_edit(self):
        '''
        this function is called when the user changes the line edit of camera in settings.
        '''

        index = self.combo_box_camera.currentIndex()
        if index == 0:  # width
            try:
                temp = int(self.line_edit_camera.text())
            except:
                self.line_edit_camera.setText(str(self.config.camera_width))
            else:
                if self.config.camera_flag_off:
                    self.update_text_edit(self.config.camera_err_off, self.config.text_edit_mode_err)
                    self.line_edit_camera.setText(str(self.config.camera_width))
                elif temp < self.camera.Width.GetMin():
                    self.config.camera_width = int(self.camera.Width.GetMin())
                    self.line_edit_camera.setText(str(self.config.camera_width))
                    self.update_text_edit(self.config.camera_err_width_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.camera.Width.GetMax():
                    self.config.camera_width = int(self.camera.Width.GetMax())
                    self.line_edit_camera.setText(str(self.config.camera_width))   
                    self.update_text_edit(self.config.camera_err_width_max_invalid, self.config.text_edit_mode_err)
                elif temp % self.camera.Width.GetInc() != 0:
                    self.config.camera_width = int(self.camera.Width.GetInc() * round(temp / self.camera.Width.GetInc()))
                    self.line_edit_camera.setText(str(self.config.camera_width))
                    self.update_text_edit(self.config.camera_err_width_increment_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.camera_width = temp
                    self.camera.StopGrabbing()
                    self.camera.AcquisitionStop.Execute()
                    self.camera.TLParamsLocked = False
                    self.camera.Width.SetValue(self.config.camera_width)
                    self.camera.TLParamsLocked = True
                    self.camera.AcquisitionStart.Execute()
                    self.camera.StartGrabbing(1)
        elif index == 1:    # height
            try:
                temp = int(self.line_edit_camera.text())
            except:
                self.line_edit_camera.setText(str(self.config.camera_height))
            else:
                if self.config.camera_flag_off:
                    self.update_text_edit(self.config.camera_err_off, self.config.text_edit_mode_err)
                    self.line_edit_camera.setText(str(self.config.camera_height))
                elif temp < self.camera.Height.GetMin():
                    self.config.camera_height = int(self.camera.Height.GetMin())
                    self.line_edit_camera.setText(str(self.config.camera_height))
                    self.update_text_edit(self.config.camera_err_height_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.camera.Height.GetMax():
                    self.config.camera_height = int(self.camera.Height.GetMax())
                    self.line_edit_camera.setText(str(self.config.camera_height))   
                    self.update_text_edit(self.config.camera_err_height_max_invalid, self.config.text_edit_mode_err)
                elif temp % self.camera.Height.GetInc() != 0:
                    self.config.camera_height = int(self.camera.Height.GetInc() * round(temp / self.camera.Height.GetInc()))
                    self.line_edit_camera.setText(str(self.config.camera_height))
                    self.update_text_edit(self.config.camera_err_height_increment_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.camera_height = temp
                    self.camera.StopGrabbing()
                    self.camera.AcquisitionStop.Execute()
                    self.camera.TLParamsLocked = False
                    self.camera.Height.SetValue(self.config.camera_height)
                    self.camera.TLParamsLocked = True
                    self.camera.AcquisitionStart.Execute()
                    self.camera.StartGrabbing(1)       

    def on_smaract_linear_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of smaract linear channels in settings.
        '''

        if index == 0:      # base steps
            self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_steps_base))
        elif index == 1:    # desired postions of x and y channels
            self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_pos_desired))
        elif index == 2:    # desired postion of z channel
            self.line_edit_smaract_linear.setText(str(self.config.smaract_z_pos_desired))    
        elif index == 3:    # base speed
            self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_base))  
        elif index == 4:    # positioning speed
            self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_positioning))  
        elif index == 5:    # on-click speed
            self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_on_click))  
        elif index == 6:    # positioning sleep multiplier
            self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_sleep_multiplier_positioning))
    
    def on_smaract_linear_line_edit(self):
        '''
        this function is called when the user changes the line edit of smaract linear channels in settings.
        '''

        index = self.combo_box_smaract_linear.currentIndex()
        if index == 0:      # base steps
            try:
                temp = int(self.line_edit_smaract_linear.text())
            except:
                self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_steps_base))
            else:
                if temp < self.config.smaract_linear_steps_min:
                    self.config.smaract_linear_steps_base = self.config.smaract_linear_steps_min
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_steps_base))
                    self.update_text_edit(self.config.smaract_err_linear_steps_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_linear_steps_max:
                    self.config.smaract_linear_steps_base = self.config.smaract_linear_steps_max
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_steps_base))
                    self.update_text_edit(self.config.smaract_err_linear_steps_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_linear_steps_base = temp
        elif index == 1:    # desired postions of x and y channels
            try:
                temp = int(self.line_edit_smaract_linear.text())
            except:
                self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_pos_desired))
            else:
                if temp < self.config.smaract_linear_pos_min_safe:
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_pos_desired))
                    self.update_text_edit(self.config.smaract_err_linear_pos_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_linear_pos_max_safe:
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_pos_desired))
                    self.update_text_edit(self.config.smaract_err_linear_pos_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_linear_pos_desired = temp
        elif index == 2:    # desired postion of z channel
            try:
                temp = int(self.line_edit_smaract_linear.text())
            except:
                self.line_edit_smaract_linear.setText(str(self.config.smaract_z_pos_desired))
            else:
                if temp < self.config.smaract_linear_pos_min_safe:
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_z_pos_desired))
                    self.update_text_edit(self.config.smaract_err_z_pos_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_linear_pos_max_safe:
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_z_pos_desired))
                    self.update_text_edit(self.config.smaract_err_z_pos_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_linear_z_desired = temp
        elif index == 3:    # base speed
            try:
                temp = int(self.line_edit_smaract_linear.text())
            except:
                self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_base))
            else:
                if temp < 0:
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_base))
                    self.update_text_edit(self.config.smaract_err_linear_speed_base_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_linear_speed_base = temp
        elif index == 4:    # positioning speed
            try:
                temp = int(self.line_edit_smaract_linear.text())
            except:
                self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_positioning))
            else:
                if temp < self.config.smaract_linear_speed_min_safe:
                    self.config.smaract_linear_speed_positioning = self.config.smaract_linear_speed_min_safe
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_positioning))
                    self.update_text_edit(self.config.smaract_err_linear_speed_positioning_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_linear_speed_max_safe:
                    self.config.smaract_linear_speed_positioning = self.config.smaract_linear_speed_max_safe
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_positioning))
                    self.update_text_edit(self.config.smaract_err_linear_speed_positioning_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_linear_speed_positioning = temp
        elif index == 5:    # on-click speed
            try:
                temp = int(self.line_edit_smaract_linear.text())
            except:
                self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_on_click))
            else:
                if temp < self.config.smaract_linear_speed_min_safe:
                    self.config.smaract_linear_speed_on_click = self.config.smaract_linear_speed_min_safe
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_on_click))
                    self.update_text_edit(self.config.smaract_err_linear_speed_on_click_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_linear_speed_max_safe:
                    self.config.smaract_linear_speed_on_click = self.config.smaract_linear_speed_max_safe
                    self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_speed_on_click))
                    self.update_text_edit(self.config.smaract_err_linear_speed_on_click_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_linear_speed_on_click = temp 
        elif index == 6:    # positioning sleep multiplier
            try:
                temp = float(self.line_edit_smaract_linear.text())
            except:
                self.line_edit_smaract_linear.setText(str(self.config.smaract_linear_sleep_multiplier_positioning))
            else:
                self.config.smaract_linear_sleep_multiplier_positioning = temp	

    def on_smaract_angular_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of smaract angular channels in settings.
        '''

        if index == 0:      # base steps
            self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_steps_base))
        elif index == 1:    # desired postion of alpha channel
            self.line_edit_smaract_angular.setText(str(self.config.smaract_alpha_pos_desired))
        elif index == 2:    # desired postion of beta channel
            self.line_edit_smaract_angular.setText(str(self.config.smaract_beta_pos_desired))    
        elif index == 3:    # base speed
            self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_speed_base))  
        elif index == 4:    # positioning speed
            self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_speed_positioning))  
        elif index == 5:    # positioning sleep multiplier
            self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_sleep_multiplier_positioning))
        
    def on_smaract_angular_line_edit(self):
        '''
        this function is called when the user changes the line edit of smaract angular channels in settings.
        '''

        index = self.combo_box_smaract_angular.currentIndex()
        if index == 0:      # base steps
            try:
                temp = int(self.line_edit_smaract_angular.text())
            except:
                self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_steps_base))
            else:
                if temp < self.config.smaract_angular_steps_min:
                    self.config.smaract_angular_steps_base = self.config.smaract_angular_steps_min
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_steps_base))
                    self.update_text_edit(self.config.smaract_err_angular_steps_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_angular_steps_max:
                    self.config.smaract_angular_steps_base = self.config.smaract_angular_steps_max
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_steps_base))
                    self.update_text_edit(self.config.smaract_err_angular_steps_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_angular_steps_base = temp
        elif index == 1:    # desired postion of alpha channel
            try:
                temp = int(self.line_edit_smaract_angular.text())
            except:
                self.line_edit_smaract_angular.setText(str(self.config.smaract_alpha_pos_desired))
            else:
                if temp < self.config.smaract_angular_pos_min_safe:
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_alpha_pos_desired))
                    self.update_text_edit(self.config.smaract_err_alpha_pos_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_angular_pos_max_safe:
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_alpha_pos_desired))
                    self.update_text_edit(self.config.smaract_err_alpha_pos_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_alpha_pos_desired = temp
        elif index == 2:    # desired postion of beta channel
            try:
                temp = int(self.line_edit_smaract_angular.text())
            except:
                self.line_edit_smaract_angular.setText(str(self.config.smaract_beta_pos_desired))
            else:
                if temp < self.config.smaract_angular_pos_min_safe:
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_beta_pos_desired))
                    self.update_text_edit(self.config.smaract_err_beta_pos_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_angular_pos_max_safe:
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_beta_pos_desired))
                    self.update_text_edit(self.config.smaract_err_beta_pos_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_beta_pos_desired = temp 
        elif index == 3:    # base speed
            try:
                temp = int(self.line_edit_smaract_angular.text())
            except:
                self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_speed_base))
            else:
                if temp < 0:
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_speed_base))
                    self.update_text_edit(self.config.smaract_err_angular_speed_base_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_angular_speed_base = temp
        elif index == 4:    # positioning speed
            try:
                temp = int(self.line_edit_smaract_angular.text())
            except:
                self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_speed_positioning))
            else:
                if temp < self.config.smaract_angular_speed_min_safe:
                    self.config.smaract_angular_speed_positioning = self.config.smaract_angular_speed_min_safe
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_speed_positioning))
                    self.update_text_edit(self.config.smaract_err_angular_speed_positioning_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_angular_speed_max_safe:
                    self.config.smaract_angular_speed_positioning = self.config.smaract_angular_speed_max_safe
                    self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_speed_positioning))
                    self.update_text_edit(self.config.smaract_err_angular_speed_positioning_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_angular_speed_positioning = temp
        elif index == 5:    # positioning sleep multiplier
            try:
                temp = float(self.line_edit_smaract_angular.text())
            except:
                self.line_edit_smaract_angular.setText(str(self.config.smaract_angular_sleep_multiplier_positioning))
            else:
                self.config.smaract_angular_sleep_multiplier_positioning = temp	

    def on_smaract_gamma_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of smaract gamma channel in settings.
        '''

        if index == 0:      # base steps
            self.line_edit_smaract_gamma.setText(str(self.config.smaract_gamma_steps_base))  
        elif index == 1:    # base frequeny
            self.line_edit_smaract_linear.setText(str(self.config.smaract_gamma_frequency_base))  
    
    def on_smaract_gamma_line_edit(self):
        '''
        this function is called when the user changes the line edit of smaract gamma channel in settings.
        '''

        index = self.combo_box_smaract_gamma.currentIndex()
        if index == 0:      # base steps
            try:
                temp = int(self.line_edit_smaract_gamma.text())
            except:
                self.line_edit_smaract_gamma.setText(str(self.config.smaract_gamma_steps_base))
            else:
                if temp < self.config.smaract_gamma_steps_min_safe:
                    self.config.smaract_gamma_steps_base = self.config.smaract_gamma_steps_min_safe
                    self.line_edit_smaract_gamma.setText(str(self.config.smaract_gamma_steps_base))
                    self.update_text_edit(self.config.smaract_err_gamma_steps_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.smaract_gamma_steps_max_safe:
                    self.config.smaract_gamma_steps_base = self.config.smaract_gamma_steps_max_safe
                    self.line_edit_smaract_gamma.setText(str(self.config.smaract_gamma_steps_base))
                    self.update_text_edit(self.config.smaract_err_gamma_steps_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_gamma_steps_base = temp
        elif index == 1:    # base frequeny
            try:
                temp = int(self.line_edit_smaract_gamma.text())
            except:
                self.line_edit_smaract_gamma.setText(str(self.config.smaract_gamma_frequency_base))
            else:
                if temp < 0:
                    self.line_edit_smaract_gamma.setText(str(self.config.smaract_gamma_frequency_base))
                    self.update_text_edit(self.config.smaract_err_gamma_frequency_base_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.smaract_gamma_frequency_base = temp
            
    def on_pistage_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of pistage in settings.
        '''

        if index == 0:      # base steps
            self.line_edit_pistage.setText(str(self.config.pistage_steps_base))
        elif index == 1:    # desired postion of l1 axis
            self.line_edit_pistage.setText(str(self.config.pistage_pos_l1_desired))
        elif index == 2:    # desired postion of l2 axis
            self.line_edit_pistage.setText(str(self.config.pistage_pos_l2_desired))    
        elif index == 3:    # base speed
            self.line_edit_pistage.setText(str(self.config.pistage_speed_base))  
        elif index == 4:    # positioning speed
            self.line_edit_pistage.setText(str(self.config.pistage_speed_positioning))  
        elif index == 5:    # positioning sleep multiplier
            self.line_edit_pistage.setText(str(self.config.pistage_sleep_multiplier_positioning))
    
    def on_pistage_line_edit(self):
        '''
        this function is called when the user changes the line edit of pistage in settings.
        '''

        index = self.combo_box_pistage.currentIndex()
        if index == 0:      # base steps
            try:
                temp = float(self.line_edit_pistage.text())
            except:
                self.line_edit_pistage.setText(str(self.config.pistage_steps_base))
            else:
                if temp < self.config.pistage_steps_min:
                    self.config.pistage_steps_base = self.config.pistage_steps_min
                    self.line_edit_pistage.setText(str(self.config.pistage_steps_base))
                    self.update_text_edit(self.config.pistage_err_steps_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.pistage_steps_max:
                    self.config.pistage_steps_base = self.config.pistage_steps_max
                    self.line_edit_pistage.setText(str(self.config.pistage_steps_base))
                    self.update_text_edit(self.config.pistage_err_steps_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.pistage_steps_base = temp
        elif index == 1:    # desired postion of l1 axis
            try:
                temp = float(self.line_edit_pistage.text())
            except:
                self.line_edit_pistage.setText(str(self.config.pistage_pos_l1_desired))
            else:
                if temp < self.config.pistage_pos_min_safe:
                    self.line_edit_pistage.setText(str(self.config.pistage_pos_l1_desired))
                    self.update_text_edit(self.config.pistage_err_pos_l1_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.pistage_pos_max_safe:
                    self.line_edit_pistage.setText(str(self.config.pistage_pos_l1_desired))
                    self.update_text_edit(self.config.pistage_err_pos_l1_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.pistage_pos_l1_desired = temp
        elif index == 2:    # desired postion of l2 axis
            try:
                temp = float(self.line_edit_pistage.text())
            except:
                self.line_edit_pistage.setText(str(self.config.pistage_pos_l2_desired))
            else:
                if temp < self.config.pistage_pos_min_safe:
                    self.line_edit_pistage.setText(str(self.config.pistage_pos_l2_desired))
                    self.update_text_edit(self.config.pistage_err_pos_l2_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.pistage_pos_max_safe:
                    self.line_edit_pistage.setText(str(self.config.pistage_pos_l2_desired))
                    self.update_text_edit(self.config.pistage_err_pos_l2_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.pistage_pos_l2_desired = temp   
        elif index == 3:    # base speed
            try:
                temp = float(self.line_edit_pistage.text())
            except:
                self.line_edit_pistage.setText(str(self.config.pistage_speed_base))
            else:
                if temp < 0:
                    self.line_edit_pistage.setText(str(self.config.pistage_speed_base))
                    self.update_text_edit(self.config.pistage_err_speed_base_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.pistage_speed_base = temp
        elif index == 4:    # positioning speed
            try:
                temp = float(self.line_edit_pistage.text())
            except:
                self.line_edit_pistage.setText(str(self.config.pistage_speed_positioning))
            else:
                if temp < self.config.pistage_speed_min_safe:
                    self.config.pistage_speed_positioning = self.config.pistage_speed_min_safe
                    self.line_edit_pistage.setText(str(self.config.pistage_speed_positioning))
                    self.update_text_edit(self.config.pistage_err_speed_positioning_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.pistage_speed_max_safe:
                    self.config.pistage_speed_positioning = self.config.pistage_speed_max_safe
                    self.line_edit_pistage.setText(str(self.config.pistage_speed_positioning))
                    self.update_text_edit(self.config.pistage_err_speed_positioning_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.pistage_speed_positioning = temp
        elif index == 5:    # positioning sleep multiplier
            try:
                temp = float(self.line_edit_pistage.text())
            except:
                self.line_edit_pistage.setText(str(self.config.pistage_sleep_multiplier_positioning))
            else:
                self.config.pistage_sleep_multiplier_positioning = temp

    def on_asm_combo_box(self, index):
        '''
        This function is called when the user changes the combo box of asm in settings.
        '''

        if index == 0:      # base steps
            self.line_edit_asm.setText(str(self.config.asm_steps_base))
        elif index == 1:    # delay between steps in ms
            self.line_edit_asm.setText(str(self.config.asm_delay_ms))

    def on_asm_line_edit(self):
        '''
        This function is called when the user changes the line edit of asm in settings.
        '''

        index = self.combo_box_asm.currentIndex()
        if index == 0:      # base steps
            try:
                temp = int(self.line_edit_asm.text())
            except:
                self.line_edit_asm.setText(str(self.config.asm_steps_base))
            else:
                if temp < self.config.asm_steps_min:
                    self.config.asm_steps_base = self.config.asm_steps_min
                    self.line_edit_asm.setText(str(self.config.asm_steps_base))
                    self.update_text_edit(self.config.asm_err_steps_min_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.asm_steps_max:
                    self.config.asm_steps_base = self.config.asm_steps_max
                    self.line_edit_asm.setText(str(self.config.asm_steps_base))
                    self.update_text_edit(self.config.asm_err_steps_max_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.asm_steps_base = temp
        elif index == 1:    # delay between steps in ms
            try:
                temp = int(self.line_edit_asm.text())
            except:
                self.line_edit_asm.setText(str(self.config.asm_delay_ms))
            else:
                self.config.asm_delay_ms = temp
                self.asm.set_delay(self.config.asm_delay_ms)

    def on_sequence_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of sequence in settings.
        '''

        if index == 0:      # smaract linear speed 
            self.line_edit_sequence.setText(str(self.config.sequence_linear_speed))
        elif index == 1:    # smaract angular speed
            self.line_edit_sequence.setText(str(self.config.sequence_angular_speed))
        elif index == 2:    # smaract inital alpha
            self.line_edit_sequence.setText(str(self.config.sequence_initial_alpha))    
        elif index == 3:    # smaract initial beta
            self.line_edit_sequence.setText(str(self.config.sequence_initial_beta))  
        elif index == 4:    # smaract initial z
            self.line_edit_sequence.setText(str(self.config.sequence_initial_z))  
        elif index == 5:    # asm sleep time
            self.line_edit_sequence.setText(str(self.config.sequence_asm_sleep_time_s))
        elif index == 6:    # sleep multiplier (initialize)
            self.line_edit_sequence.setText(str(self.config.sequence_sleep_multiplier_initialize))
        elif index == 7:    # sleep multiplier (sequence)
            self.line_edit_sequence.setText(str(self.config.sequence_sleep_multiplier_do))
        elif index == 8:    # flag of releasing debris
            self.line_edit_sequence.setText(str(self.config.sequence_flag_release_debris))

    def on_sequence_line_edit(self):
        '''
        this function is called when the user changes the line edit of sequence in settings.
        '''

        index = self.combo_box_sequence.currentIndex()
        if index == 0:      # smaract linear speed
            try:
                temp = int(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_linear_speed))
            else:
                self.config.sequence_linear_speed = temp
        elif index == 1:    # smaract angular speed
            try:
                temp = int(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_angular_speed))
            else:
                self.config.sequence_angular_speed = temp	
        elif index == 2:    # smaract inital alpha
            try:
                temp = int(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_initial_alpha))
            else:
                self.config.sequence_initial_alpha = temp
        elif index == 3:    # smaract initial beta
            try:
                temp = int(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_initial_beta))
            else:
                self.config.sequence_initial_beta = temp
        elif index == 4:    # smaract initial z
            try:
                temp = int(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_initial_z))
            else:
                self.config.sequence_initial_z = temp
        elif index == 5:    # asm sleep time
            try:
                temp = float(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_asm_sleep_time_s))
            else:
                self.config.sequence_asm_sleep_time_s = temp
        elif index == 6:    # sleep multiplier (initialize)
            try:
                temp = float(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_sleep_multiplier_initialize))
            else:
                self.config.sequence_sleep_multiplier_initialize = temp
        elif index == 7:    # sleep multiplier (sequence)
            try:
                temp = float(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_sleep_multiplier_do))
            else:
                self.config.sequence_sleep_multiplier_do = temp
        elif index == 8:    # flag of releasing debris
            try:
                temp = int(self.line_edit_sequence.text())
            except:
                self.line_edit_sequence.setText(str(self.config.sequence_flag_release_debris))
            else:
                self.config.sequence_flag_release_debris = temp

    def on_sequence_delta_z_line_edit(self):
        '''
        this function is called when the user changes the line edit of sequence delta z in settings.
        '''

        try:
            temp = self.line_edit_sequence_delta_z.text().split(',')
            temp = [int(i) for i in temp]
        except:
            self.line_edit_sequence_delta_z.setText(','.join(str(item) for item in self.config.sequence_delta_z))
        else:
            self.config.sequence_delta_z = temp

    def on_sequence_delta_y_line_edit(self):
        '''
        this function is called when the user changes the line edit of sequence delta y in settings.
        '''

        try:
            temp = self.line_edit_sequence_delta_y.text().split(',')
            temp = [int(i) for i in temp]
        except:
            self.line_edit_sequence_delta_y.setText(','.join(str(item) for item in self.config.sequence_delta_y))
        else:
            self.config.sequence_delta_y = temp

    def on_annotation_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of general annotation in settings.
        '''

        if index == 0:      # edge level 1 
            self.line_edit_annotation.setText(str(self.config.annotation_edge_level_1))
        elif index == 1:    # edge level 2
            self.line_edit_annotation.setText(str(self.config.annotation_edge_level_2))
        elif index == 2:    # edge aperture size
            self.line_edit_annotation.setText(str(self.config.annotation_edge_aperture_size))   
        elif index == 3:    # edge l2 gradient
            self.line_edit_annotation.setText(str(self.config.annotation_edge_l2_gradient))  
        elif index == 4:    # closing kernel size
            self.line_edit_annotation.setText(str(self.config.annotation_closing_kernel_size)) 
        elif index == 5:    # closing kernel iterations
            self.line_edit_annotation.setText(str(self.config.annotation_closing_iterations))
        elif index == 6:    # blurring sigma x
            self.line_edit_annotation.setText(str(self.config.annotation_blurring_sigma_x))
        elif index == 7:    # min area for connected components
            self.line_edit_annotation.setText(str(self.config.annotation_area_value_min))
        elif index == 8:    # flag of saving images
            self.line_edit_annotation.setText(str(self.config.annotation_flag_save_image))
        elif index == 9:    # flag of momentarily stopping the camera
            self.line_edit_annotation.setText(str(self.config.annotation_flag_stop_camera))

    def on_annotation_line_edit(self):
        '''
        this function is called when the user changes the line edit of general annotation in settings.
        '''

        index = self.combo_box_annotation.currentIndex()
        if index == 0:      # edge level 1 
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_edge_level_1))
            else:
                self.config.annotation_edge_level_1 = temp
        elif index == 1:    # edge level 2
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_edge_level_2))
            else:
                self.config.annotation_edge_level_2 = temp
        elif index == 2:    # edge aperture size
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_edge_aperture_size))
            else:
                self.config.annotation_edge_aperture_size = temp
        elif index == 3:    # edge l2 gradient
            try:
                temp = bool(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_edge_l2_gradient))
            else:
                self.config.annotation_edge_l2_gradient = temp
        elif index == 4:    # closing kernel size
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_closing_kernel_size))
            else:
                self.config.annotation_closing_kernel_size = temp
        elif index == 5:    # closing kernel iterations
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_closing_iterations))
            else:
                self.config.annotation_closing_iterations = temp
        elif index == 6:    # blurring sigma x
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_blurring_sigma_x))
            else:
                self.config.annotation_blurring_sigma_x = temp
                self.config.annotation_blurring_kernel_size = 6*self.config.annotation_blurring_sigma_x + 1
        elif index == 7:    # min area for connected components
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_area_value_min))
            else:
                self.config.annotation_area_value_min = temp
        elif index == 8:    # flag of saving images
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_flag_save_image))
            else:
                self.config.annotation_flag_save_image = temp
        elif index == 9:    # flag of momentarily stopping the camera
            try:
                temp = int(self.line_edit_annotation.text())
            except:
                self.line_edit_annotation.setText(str(self.config.annotation_flag_stop_camera))
            else:
                self.config.annotation_flag_stop_camera = temp

    def on_annotation_embryo_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of embryo annotation in settings.
        '''

        if index == 0:      # gray level 1 
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_gray_level_1))
        elif index == 1:    # gray level 2
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_gray_level_2))
        elif index == 2:    # crop middle offset
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_crop_middle_offset))    
        elif index == 3:    # crop offset
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_crop_offset))  
        elif index == 4:    # fill offset
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_fill_offset)) 
        elif index == 5:    # openning kernel size
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_openning_kernel_size))
        elif index == 6:    # openning kernel iterations
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_openning_iterations))
        elif index == 7:    # circle dp
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_circle_dp))
        elif index == 8:    # circle param 1
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_circle_param_1))
        elif index == 9:    # circle param 2
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_circle_param_2))
        elif index == 10:   # point offset x
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_point_offset_x))
        elif index == 11:   # point offset y
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_point_offset_y))
        elif index == 12:   # flag of computer vision or deep network
            self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_flag_cv_dn))

    def on_annotation_embryo_line_edit(self):
        '''
        this function is called when the user changes the line edit of embryo annotation in settings.
        '''

        index = self.combo_box_annotation_embryo.currentIndex()
        if index == 0:      # gray level 1
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_gray_level_1))
            else:
                self.config.annotation_embryo_gray_level_1 = temp
        elif index == 1:    # gray level 2
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_gray_level_2))
            else:
                self.config.annotation_embryo_gray_level_2 = temp
        elif index == 2:    # crop middle offset
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_crop_middle_offset))
            else:
                self.config.annotation_embryo_crop_middle_offset = temp
        elif index == 3:    # crop offset
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_crop_offset))
            else:
                self.config.annotation_embryo_crop_offset = temp
        elif index == 4:    # fill offset
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_fill_offset))
            else:
                self.config.annotation_embryo_fill_offset = temp
        elif index == 5:    # openning kernel size
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_openning_kernel_size))
            else:
                self.config.annotation_embryo_openning_kernel_size = temp
        elif index == 6:    # openning kernel iterations
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_openning_iterations))
            else:
                self.config.annotation_embryo_openning_iterations = temp
        elif index == 7:    # circle dp
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_circle_dp))
            else:
                self.config.annotation_embryo_circle_dp = temp
        elif index == 8:    # circle param 1
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_circle_param_1))	
            else:
                self.config.annotation_embryo_circle_param_1 = temp
        elif index == 9:    # circle param 2
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_circle_param_2))
            else:
                self.config.annotation_embryo_circle_param_2 = temp
        elif index == 10:   # point offset x
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_point_offset_x))
            else:
                self.config.annotation_embryo_point_offset_x = temp
        elif index == 11:   # point offset y
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_point_offset_y))
            else:
                self.config.annotation_embryo_point_offset_y = temp
        elif index == 12:   # flag of computer vision or deep network
            try:
                temp = int(self.line_edit_annotation_embryo.text())
            except:
                self.line_edit_annotation_embryo.setText(str(self.config.annotation_embryo_flag_cv_dn))
            else:
                self.config.annotation_embryo_flag_cv_dn = temp

    def on_annotation_scissor_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of scissor annotation in settings.
        '''

        if index == 0:      # gray level  
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_gray_level))
        elif index == 1:    # crop offset
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_crop_offset))
        elif index == 2:    # line rho
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_line_rho))    
        elif index == 3:    # line theta
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_line_theta))  
        elif index == 4:    # diagonal offset
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_offset)) 
        elif index == 5:    # diagonal vote
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_vote))
        elif index == 6:    # diagonal min length
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_length_min))
        elif index == 7:    # diagonal max gap
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_gap_max))
        elif index == 8:    # diagonal min slope
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_slope_min))
        elif index == 9:    # diagonal max slope
            self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_slope_max))
        
    def on_annotation_scissor_line_edit(self):
        '''
        this function is called when the user changes the line edit of scissor annotation in settings.
        '''

        index = self.combo_box_annotation_scissor.currentIndex()
        if index == 0:      # gray level  
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_gray_level))
            else:
                self.config.annotation_scissor_gray_level = temp
        elif index == 1:    # crop offset
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_crop_offset))
            else:
                self.config.annotation_scissor_crop_offset = temp
        elif index == 2:    # line rho
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_line_rho))
            else:
                self.config.annotation_scissor_line_rho = temp
        elif index == 3:    # line theta
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_line_theta))
            else:
                self.config.annotation_scissor_line_theta = temp
        elif index == 4:    # diagonal offset
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_offset))
            else:
                self.config.annotation_scissor_diagonal_line_offset = temp 
        elif index == 5:    # diagonal vote
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_vote))
            else:
                self.config.annotation_scissor_diagonal_line_vote = temp
        elif index == 6:    # diagonal min length
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_length_min))
            else:
                self.config.annotation_scissor_diagonal_line_length_min = temp
        elif index == 7:    # diagonal max gap
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_gap_max))
            else:
                self.config.annotation_scissor_diagonal_line_gap_max = temp
        elif index == 8:    # diagonal min slope
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_slope_min))
            else:
                self.config.annotation_scissor_diagonal_line_slope_min = temp
        elif index == 9:    # diagonal max slope
            try:
                temp = int(self.line_edit_annotation_scissor.text())
            except:
                self.line_edit_annotation_scissor.setText(str(self.config.annotation_scissor_diagonal_line_slope_max))
            else:
                self.config.annotation_scissor_diagonal_line_slope_max = temp

    def on_automation_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of automation in settings.
        '''

        if index == 0:      # l1 num
            self.line_edit_automation.setText(str(self.config.automation_num_l1))
        elif index == 1:    # l2 num
            self.line_edit_automation.setText(str(self.config.automation_num_l2))
        elif index == 2:    # l1 step
            self.line_edit_automation.setText(str(self.config.automation_step_l1))    
        elif index == 3:    # l2 step
            self.line_edit_automation.setText(str(self.config.automation_step_l2))  
        elif index == 4:    # smaract speed
            self.line_edit_automation.setText(str(self.config.automation_speed_smaract)) 
        elif index == 5:    # pistage
            self.line_edit_automation.setText(str(self.config.automation_speed_pistage))
        elif index == 6:    # smaract sleep multiplier
            self.line_edit_automation.setText(str(self.config.automation_sleep_multiplier_smaract))
        elif index == 7:    # pistage sleep multiplier
            self.line_edit_automation.setText(str(self.config.automation_sleep_multiplier_pistage))
        elif index == 8:    # flag of saving images
            self.line_edit_automation.setText(str(self.config.automation_flag_save_image))
        elif index == 9:    # flag of releasing debris
            self.line_edit_automation.setText(str(self.config.automation_flag_release_debris))
        elif index == 10:   # flag of computer vision or deep network
            self.line_edit_automation.setText(str(self.config.automation_flag_cv_dn))
        elif index == 11:   # waiting time for the development experiment
            self.line_edit_automation.setText(str(self.config.pistage_development_wait))
        
    def on_automation_line_edit(self):
        '''
        this function is called when the user changes the line edit of automation in settings.
        '''

        index = self.combo_box_automation.currentIndex()
        if index == 0:      # l1 num
            try:
                temp = int(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_num_l1))
            else:
                self.config.automation_num_l1 = temp
        elif index == 1:    # l2 num
            try:
                temp = int(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_num_l2))
            else:
                self.config.automation_num_l2 = temp
        elif index == 2:    # l1 step
            try:
                temp = float(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_step_l1))
            else:
                self.config.automation_step_l1 = temp    
        elif index == 3:    # l2 step
            try:
                temp = float(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_step_l2))
            else:
                self.config.automation_step_l2 = temp 
        elif index == 4:    # smaract speed
            try:
                temp = int(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_speed_smaract))
            else:
                self.config.automation_speed_smaract = temp 
        elif index == 5:    # pistage
            try:
                temp = float(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_speed_pistage))
            else:
                self.config.automation_speed_pistage = temp
        elif index == 6:    # smaract sleep multiplier
            try:
                temp = float(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_sleep_multiplier_smaract))
            else:
                self.config.automation_sleep_multiplier_smaract = temp
        elif index == 7:    # pistage sleep multiplier
            try:
                temp = float(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_sleep_multiplier_pistage))
            else:
                self.config.automation_sleep_multiplier_pistage = temp
        elif index == 8:    # flag of saving images
            try:
                temp = int(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_flag_save_image))
            else:
                self.config.automation_flag_save_image = temp
        elif index == 9:    # flag of releasing debris
            try:
                temp = int(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_flag_release_debris))
            else:
                self.config.automation_flag_release_debris = temp
        elif index == 10:   # flag of computer vision or deep network
            try:
                temp = int(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.automation_flag_cv_dn))
            else:
                self.config.automation_flag_cv_dn = temp
        elif index == 11:   # waiting time for the development experiment
            try:
                temp = int(self.line_edit_automation.text())
            except:
                self.line_edit_automation.setText(str(self.config.pistage_development_wait))
            else:
                self.config.pistage_development_wait = temp

    def on_deep_network_combo_box(self, index):
        '''
        this function is called when the user changes the combo box of deep network in settings.
        '''

        if index == 0:      # somite height
            self.line_edit_deep_network.setText(str(self.config.dn_somite_height_um))
        elif index == 1:    # somite target
            self.line_edit_deep_network.setText(str(self.config.dn_somite_target))
        elif index == 2:    # threshold
            self.line_edit_deep_network.setText(str(self.config.dn_threshold)) 

    def on_deep_network_line_edit(self):
        '''
        this function is called when the user changes the line edit of deep network in settings.
        '''

        index = self.combo_box_deep_network.currentIndex()
        if index == 0:      # somite height
            try:
                temp = int(self.line_edit_deep_network.text())
            except:
                self.line_edit_deep_network.setText(str(self.config.dn_somite_height_um))
            else:
                self.config.dn_somite_height_um = temp
                self.config.dn_somite_height_px = self.config.dn_somite_height_um * self.config.micro_to_mili * self.config.mili_to_pixel
        elif index == 1:    # somite target
            try:
                temp = int(self.line_edit_deep_network.text())
            except:
                self.line_edit_deep_network.setText(str(self.config.dn_somite_target))
            else:
                self.config.dn_somite_target = temp
        elif index == 2:    # threshold
            try:
                temp = float(self.line_edit_deep_network.text())
            except:
                self.line_edit_deep_network.setText(str(self.config.dn_threshold))
            else:
                if temp < self.config.dn_threshold_min:
                    self.line_edit_deep_network.setText(str(self.config.dn_threshold))
                    self.update_text_edit(self.config.dn_err_threshold_invalid, self.config.text_edit_mode_err)
                elif temp > self.config.dn_threshold_max:
                    self.line_edit_deep_network.setText(str(self.config.dn_threshold))
                    self.update_text_edit(self.config.dn_err_threshold_invalid, self.config.text_edit_mode_err)
                else:
                    self.config.dn_threshold = temp

    @pyqtSlot(int)
    def update_smaract_referencing_status(self, status):
        '''
        this function is called through the smaract referencing procedure. It updates the gui accordingly.
        '''

        if (status == self.config.smaract_referencing_x_failed):
            self.label_smaract_referencing_x_image.setPixmap(self.image_red_cross)
            self.label_smaract_referencing_status_text.setText(self.config.smaract_referencing_x_failed_text)
            self.label_smaract_referencing_status_text.setStyleSheet('color: red;')
            self.button_smaract_referencing.setEnabled(True)
        elif (status == self.config.smaract_referencing_x_done):
                self.label_smaract_referencing_x_image.setPixmap(self.image_green_check)
        elif (status == self.config.smaract_referencing_y_failed):
            self.label_smaract_referencing_y_image.setPixmap(self.image_red_cross)
            self.label_smaract_referencing_status_text.setText(self.config.smaract_referencing_y_failed_text)
            self.label_smaract_referencing_status_text.setStyleSheet('color: red;')
            self.button_smaract_referencing.setEnabled(True)
        elif (status == self.config.smaract_referencing_y_done):
            self.label_smaract_referencing_y_image.setPixmap(self.image_green_check)
        elif (status == self.config.smaract_referencing_z_failed):
            self.label_smaract_referencing_z_image.setPixmap(self.image_red_cross)
            self.label_smaract_referencing_status_text.setText(self.config.smaract_referencing_z_failed_text)
            self.label_smaract_referencing_status_text.setStyleSheet('color: red;')
            self.button_smaract_referencing.setEnabled(True)
        elif (status == self.config.smaract_referencing_z_done):
            self.label_smaract_referencing_z_image.setPixmap(self.image_green_check)
        elif (status == self.config.smaract_referencing_alpha_failed):
            self.label_smaract_referencing_alpha_image.setPixmap(self.image_red_cross)
            self.label_smaract_referencing_status_text.setText(self.config.smaract_referencing_alpha_failed_text)
            self.label_smaract_referencing_status_text.setStyleSheet('color: red;')
            self.button_smaract_referencing.setEnabled(True)
        elif (status == self.config.smaract_referencing_alpha_done):
            self.label_smaract_referencing_alpha_image.setPixmap(self.image_green_check)
        elif (status == self.config.smaract_referencing_beta_failed):
            self.label_smaract_referencing_beta_image.setPixmap(self.image_red_cross)
            self.label_smaract_referencing_status_text.setText(self.config.smaract_referencing_beta_failed_text)
            self.label_smaract_referencing_status_text.setStyleSheet('color: red;')
            self.button_smaract_referencing.setEnabled(True)
        elif (status == self.config.smaract_referencing_beta_done):
            self.label_smaract_referencing_beta_image.setPixmap(self.image_green_check)
        elif (status == self.config.smaract_referencing_done):
            self.label_smaract_referencing_x_image.setPixmap(self.image_green_check)
            self.label_smaract_referencing_y_image.setPixmap(self.image_green_check)
            self.label_smaract_referencing_z_image.setPixmap(self.image_green_check)
            self.label_smaract_referencing_alpha_image.setPixmap(self.image_green_check)
            self.label_smaract_referencing_beta_image.setPixmap(self.image_green_check)
            self.label_smaract_referencing_status_text.setText(self.config.smaract_referencing_done_text)
            self.label_smaract_referencing_status_text.setStyleSheet('color: green;')
            self.label_smaract_referencing_status_image.setPixmap(self.image_green_check)
            self.button_smaract_referencing.setEnabled(False)
    
    @pyqtSlot(int)
    def update_pistage_referencing_status(self, status):
        '''
        this function is called through the PI stage referencing procedure. It updates the gui accordingly.
        '''

        if (status == self.config.pistage_referencing_l1_failed):
            self.label_pistage_referencing_l1_image.setPixmap(self.image_red_cross)
            self.label_pistage_referencing_status_text.setText(self.config.pistage_referencing_l1_failed_text)
            self.label_pistage_referencing_status_text.setStyleSheet('color: red;')
            self.button_pistage_referencing.setEnabled(True)
        elif (status == self.config.pistage_referencing_l1_done):
                self.label_pistage_referencing_l1_image.setPixmap(self.image_green_check)
        elif (status == self.config.pistage_referencing_l2_failed):
            self.label_pistage_referencing_l2_image.setPixmap(self.image_red_cross)
            self.label_pistage_referencing_status_text.setText(self.config.pistage_referencing_l2_failed_text)
            self.label_pistage_referencing_status_text.setStyleSheet('color: red;')
            self.button_pistage_referencing.setEnabled(True)
        elif (status == self.config.pistage_referencing_l2_done):
            self.label_pistage_referencing_l2_image.setPixmap(self.image_green_check)
        elif (status == self.config.pistage_referencing_done):
            self.label_pistage_referencing_l1_image.setPixmap(self.image_green_check)
            self.label_pistage_referencing_l2_image.setPixmap(self.image_green_check)
            self.label_pistage_referencing_status_text.setText(self.config.pistage_referencing_done_text)
            self.label_pistage_referencing_status_text.setStyleSheet('color: green;')
            self.label_pistage_referencing_status_image.setPixmap(self.image_green_check)
            self.button_pistage_referencing.setEnabled(False)

    @pyqtSlot(int)
    def update_gamepad_status(self, status):
        '''
        this function is called to update gamepad status (connected or not found) in the gui.
        '''

        if status == self.config.gamepad_found:
            self.label_gamepad_text.setText(self.config.gamepad_found_text)
            self.label_gamepad_text.setStyleSheet('color: green;')
        elif status == self.config.gamepad_not_found:
            self.label_gamepad_text.setText(self.config.gamepad_not_found_text)
            self.label_gamepad_text.setStyleSheet('color: red;')

    @pyqtSlot(int)
    def update_smaract_control_status(self, status):
        '''
        this function is called to update smaract control status (Translation or Rotation) in the gui.
        '''

        if status == self.config.control_smaract_translation:
            self.label_smaract_control_status_text.setText(self.config.control_smaract_translation_str)
            self.label_smaract_control_status_text.setStyleSheet('color: blue;')
        elif status == self.config.control_smaract_rotation:
            self.label_smaract_control_status_text.setText(self.config.control_smaract_rotation_str)
            self.label_smaract_control_status_text.setStyleSheet('color: blue;')

    @pyqtSlot(int)
    def update_pistage_control_status(self, status):
        '''
        this function is called to update PIStage control status (L1 or L2) in the gui.
        '''

        if status == self.config.control_pistage_l1:
            self.label_pistage_control_status_text.setText(self.config.pistage_l1_str)
            self.label_pistage_control_status_text.setStyleSheet('color: blue;')
        elif status == self.config.control_pistage_l2:
            self.label_pistage_control_status_text.setText(self.config.pistage_l2_str)
            self.label_pistage_control_status_text.setStyleSheet('color: blue;')

    @pyqtSlot(int)
    def update_smaract_speed_multiplier(self, status):
        '''
        this function is called to update smaract speed multiplier in the gui.
        '''

        if status == self.config.smaract_speed_multiplier_increase:
            if (self.spinner_smaract_speed.value() < self.config.smaract_speed_multiplier_indices[-1]):
                self.config.smaract_speed_multiplier_index = self.config.smaract_speed_multiplier_index + 1
                self.config.smaract_speed_multiplier_value = self.config.smaract_speed_multiplier_values[self.config.smaract_speed_multiplier_index]
                self.spinner_smaract_speed.setValue(self.config.smaract_speed_multiplier_index)
        elif status == self.config.smaract_speed_multiplier_decrease:
            if (self.spinner_smaract_speed.value() > self.config.smaract_speed_multiplier_indices[0]):
                self.config.smaract_speed_multiplier_index = self.config.smaract_speed_multiplier_index - 1
                self.config.smaract_speed_multiplier_value = self.config.smaract_speed_multiplier_values[self.config.smaract_speed_multiplier_index]
                self.spinner_smaract_speed.setValue(self.config.smaract_speed_multiplier_index)

    @pyqtSlot(int)
    def update_pistage_speed_multiplier(self, status):
        '''
        this function is called to update PIStage speed multiplier in the gui.
        '''
        
        if status == self.config.pistage_speed_multiplier_increase:
            if (self.spinner_pistage_speed.value() < self.config.pistage_speed_multiplier_indices[-1]):
                self.config.pistage_speed_multiplier_index = self.config.pistage_speed_multiplier_index + 1
                self.config.pistage_speed_multiplier_value = self.config.pistage_speed_multiplier_values[self.config.pistage_speed_multiplier_index]
                self.spinner_pistage_speed.setValue(self.config.pistage_speed_multiplier_index)
        elif status == self.config.pistage_speed_multiplier_decrease:
            if (self.spinner_pistage_speed.value() > self.config.pistage_speed_multiplier_indices[0]):
                self.config.pistage_speed_multiplier_index = self.config.pistage_speed_multiplier_index - 1
                self.config.pistage_speed_multiplier_value = self.config.pistage_speed_multiplier_values[self.config.pistage_speed_multiplier_index]
                self.spinner_pistage_speed.setValue(self.config.pistage_speed_multiplier_index)

    @pyqtSlot(int, float)
    def update_position(self, code, value):
        '''
        this function is called to update the positions of components (smaract channels, pistage axes, and asm) in the gui.
        '''

        if code == self.config.id_smaract_channel_x:
            self.label_position_x_text.setText('{:.2f}'.format(float(value * self.config.nano_to_mili)))
            self.label_position_x_text.setStyleSheet(self.label_position_text_style)
        elif code == self.config.id_smaract_channel_y:
            self.label_position_y_text.setText('{:.2f}'.format(float(value * self.config.nano_to_mili)))
            self.label_position_y_text.setStyleSheet(self.label_position_text_style)
        elif code == self.config.id_smaract_channel_z:
            self.label_position_z_text.setText('{:.2f}'.format(float(value * self.config.nano_to_mili)))
            self.label_position_z_text.setStyleSheet(self.label_position_text_style)
        elif code == self.config.id_smaract_channel_alpha:
            self.label_position_alpha_text.setText('{:.2f}'.format(float(value / self.config.micro)))
            self.label_position_alpha_text.setStyleSheet(self.label_position_text_style)
        elif code == self.config.id_smaract_channel_beta:
            self.label_position_beta_text.setText('{:.2f}'.format(float(value / self.config.micro)))
            self.label_position_beta_text.setStyleSheet(self.label_position_text_style)
        elif code == self.config.id_smaract_channel_gamma:
            self.label_position_gamma_text.setText('{:d}'.format(int(value)))
            self.label_position_gamma_text.setStyleSheet(self.label_position_text_style)
        elif code == self.config.id_asm:
            self.label_position_asm_text.setText('{:d}'.format(int(value)))
            self.label_position_asm_text.setStyleSheet(self.label_position_text_style)
        elif code == self.config.id_pistage_l1:
            self.label_position_l1_text.setText('{:.2f}'.format(value))
            self.label_position_l1_text.setStyleSheet(self.label_position_text_style)
        elif code == self.config.id_pistage_l2:
            self.label_position_l2_text.setText('{:.2f}'.format(value))
            self.label_position_l2_text.setStyleSheet(self.label_position_text_style)

    @pyqtSlot(str, int)
    def update_text_edit(self, text, flag_mode):
        '''
        this function is called to show the possible info/err texts in the gui.
        '''

        time_stamp = time.strftime('%H_%M_%S: ', time.localtime())
        if flag_mode == self.config.text_edit_mode_info:
            self.text_edit.setTextColor(self.color_green)
        elif flag_mode == self.config.text_edit_mode_err:
            self.text_edit.setTextColor(self.color_red)
        self.text_edit.append(time_stamp+text)

    @pyqtSlot()
    def update_coord(self):
        '''
        this function is called when new annotation points are detected in automation. It updates the tool and trget coordinates shown in the gui.
        '''

        if len(self.config.coords_target) > 0:
            self.label_target_text.setText('x: {:d}, y: {:d}'.format(int(self.config.coords_target[-1][0]), int(self.config.coords_target[-1][1])))
            self.label_target_text.setStyleSheet('color: blue;')
        if len(self.config.coords_tool) > 0:
            self.label_tool_text.setText('x: {:d}, y: {:d}'.format(int(self.config.coords_tool[-1][0]), int(self.config.coords_tool[-1][1])))
            self.label_tool_text.setStyleSheet('color: green;')

    @pyqtSlot()
    def update_button_smaract_positioning(self):
        self.button_smaract_positioning.setEnabled(True)

    @pyqtSlot()
    def update_button_pistage_positioning(self):
        self.button_pistage_positioning.setEnabled(True)

    @pyqtSlot()
    def update_button_initialize(self):
        self.button_initialize.setEnabled(True)

    @pyqtSlot()
    def update_button_sequence(self):
        self.button_sequence.setEnabled(True)

    @pyqtSlot()
    def update_button_automation_start(self):
        self.button_automation_start.setEnabled(True)
