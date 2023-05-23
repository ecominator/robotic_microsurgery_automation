##############################################################################
# File name:    configuration.py
# Project:      Robotic Surgery Software
# Part:         Configuration of the robotic surgery platform
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file contains the settings which are used to 
#               confiugre the components and various functions of the 
#               robotic platform.
##############################################################################


class Configuration:
    def __init__(self):
        # smaract constants and variables
        # # channels
        self.smaract_channel_x                                          = 0
        self.smaract_channel_y                                          = 1
        self.smaract_channel_z                                          = 2
        self.smaract_channel_alpha                                      = 3
        self.smaract_channel_beta                                       = 4
        self.smaract_channel_gamma                                      = 5
        # # referencing
        self.smaract_referencing_default                                = 0
        self.smaract_referencing_x_done                                 = 1
        self.smaract_referencing_x_failed                               = 2
        self.smaract_referencing_x_not                                  = 3
        self.smaract_referencing_y_done                                 = 4
        self.smaract_referencing_y_failed                               = 5
        self.smaract_referencing_y_not                                  = 6
        self.smaract_referencing_z_done                                 = 7
        self.smaract_referencing_z_failed                               = 8
        self.smaract_referencing_z_not                                  = 9
        self.smaract_referencing_alpha_done                             = 10
        self.smaract_referencing_alpha_failed                           = 11
        self.smaract_referencing_alpha_not                              = 12
        self.smaract_referencing_beta_done                              = 13
        self.smaract_referencing_beta_failed                            = 14
        self.smaract_referencing_beta_not                               = 15
        self.smaract_referencing_done                                   = 16
        self.smaract_referencing_x_failed_text                          = 'referencing smaract (x) has been failed!'
        self.smaract_referencing_y_failed_text                          = 'referencing smaract (y) has been failed!'
        self.smaract_referencing_z_failed_text                          = 'referencing smaract (z) has been failed!'
        self.smaract_referencing_alpha_failed_text                      = 'referencing smaract (alpha) has been failed!'
        self.smaract_referencing_beta_failed_text                       = 'referencing smaract (beta) has been failed!'
        self.smaract_referencing_done_text                              = 'referencing has been done.'
        self.smaract_referencing_default_text                           = 'not referenced yet.'
        # # speed multiplier
        self.smaract_speed_multiplier_indices                           = [0, 1, 2, 3]
        self.smaract_speed_multiplier_values                            = [1, 5, 10, 15]
        self.smaract_speed_multiplier_index                             = self.smaract_speed_multiplier_indices[2]
        self.smaract_speed_multiplier_value                             = self.smaract_speed_multiplier_values[self.smaract_speed_multiplier_index]
        self.smaract_speed_multiplier_increase                          = 1
        self.smaract_speed_multiplier_decrease                          = -1
        # # linear channels: steps and position
        self.smaract_linear_steps_base	                                = 2000000       # nm = 2mm  
        self.smaract_linear_steps_min                                   = 500000        # nm = 0.5mm 
        self.smaract_linear_steps_max                                   = 20000000      # nm = 20mm 
        self.smaract_linear_pos_min_safe                                = 100000	    # nm = 0.1mm (used for checking the movement in on_click), min is 0mm
        self.smaract_linear_pos_max_safe                                = 39900000	    # nm = 39.9mm (used for checking the movement in on_click), max is 40mm
        self.smaract_linear_pos_desired                                 = 20000000		# nm = 20mm (used in positioning)
        self.smaract_z_pos_desired                                      = 17000000		# nm = 17mm (used in positioning)
        self.smaract_linear_pos_gamepad_low_limit                       = 3000000		# nm = 3mm (used for limiting the movement of channels with gamepad)
        self.smaract_linear_pos_gamepad_high_limit                      = 37000000		# nm = 37mm (used for limiting the movement of channels with gamepad)
        # # linear channels: speed
        self.smaract_linear_speed_base                                  = 1000000       # nm/s = 1mm/s
        self.smaract_linear_speed_min_safe                              = 500000        # nm/s = 0.5mm/s (used for checking the speed in on_click and with gamepad), min is 0mm/s
        self.smaract_linear_speed_max_safe                              = 20000000      # nm/s = 20mm/s (used for checking the speed in on_click and with gamepad), max is 100mm/s (smaract Doc - page 81) 
        self.smaract_linear_speed_positioning                           = 5000000		# nm/s = 5mm/s (used in positioning)
        self.smaract_linear_speed_on_click                              = 500000		# nm/s = 0.5mm/s (used in on_click)
        # # linear channels: sleep multiplier
        self.smaract_linear_sleep_multiplier_positioning                = 1.5
        # # angular channels: steps and position
        self.smaract_angular_steps_base                                 = 10000000      # uDeg = 10deg
        self.smaract_angular_steps_min                                  = 1000000       # uDeg = 1deg 
        self.smaract_angular_steps_max                                  = 50000000      # uDeg = 50deg 
        self.smaract_angular_pos_min_safe                               = 0	            # uDeg = 0deg, min is -359.999999deg (smaract Doc - page 68)
        self.smaract_angular_pos_max_safe                               = 60000000	    # uDeg = 60deg, max is 359.999999deg (smaract Doc - page 68) 
        self.smaract_alpha_pos_desired                                  = -5000000      # uDeg = -5deg (used in positioning)
        self.smaract_beta_pos_desired                                   = 53000000		# uDeg = 53deg (used in positioning)
        self.smaract_alpha_pos_gamepad_low_limit                        = -30000000	    # uDeg = -30deg (used for limiting the movement of channels with gamepad)
        self.smaract_alpha_pos_gamepad_high_limit                       = 30000000	    # uDeg = 30deg (used for limiting the movement of channels with gamepad)
        self.smaract_beta_pos_gamepad_low_limit                         = 0     	    # uDeg = 0deg (used for limiting the movement of channels with gamepad)
        self.smaract_beta_pos_gamepad_high_limit                        = 53000000	    # uDeg = 54deg (used for limiting the movement of channels with gamepad)
        # # angular channels: speed
        self.smaract_angular_speed_base                                 = 2000000       # uDeg/s = 2deg/s
        self.smaract_angular_speed_min_safe                             = 1000000       # uDeg/s = 1deg/s (used for checking the speed when using the gamepad). min is 0deg/s
        self.smaract_angular_speed_max_safe                             = 50000000      # uDeg/s = 50deg/s (used for checking the speed when using the gamepad), max is 100deg/s (smaract Doc - page 81)
        self.smaract_angular_speed_positioning                          = 5000000	    # uDeg/S = 5deg/s (used in positioning)
        # # angular channels: sleep multiplier
        self.smaract_angular_sleep_multiplier_positioning               = 1.5
        # # gamma channel: steps
        self.smaract_gamma_steps                                        = 0             # absolute position (aritficially) of the gamma channel 
        self.smaract_gamma_steps_base                                   = 500
        self.smaract_gamma_steps_min_safe                               = 0             # min is -30000 corresponding to unbound (smaract Doc - page 91) 
        self.smaract_gamma_steps_max_safe                               = 29900         # max is 30000 corresponding to unbound (smaract Doc - page 91)
        # # gamma channel: frequency
        self.smaract_gamma_frequency_base                               = 1000		    # Hz = 1kHz
        self.smaract_gamma_frequency_min_safe                           = 250           # Hz = 250Hz (used for checking the frequency when using the gamepad), min is 0Hz
        self.smaract_gamma_frequency_max_safe                           = 18000         # Hz = 18kHz (used for checking the frequency when using the gamepad), max is 18.5kHz (smaract Doc - page 91)
        # # others
        self.smaract_status_ok                                          = 0             # equivalent of SA_OK in SmarAct module
        self.smaract_err_x_not_reachable                                = 'smaract channel (x) target position is out of reach!'
        self.smaract_err_y_not_reachable                                = 'smaract channel (y) target position is out of reach!'
        self.smaract_err_z_not_reachable                                = 'smaract channel (z) target position is out of reach!'
        self.smaract_err_alpha_not_reachable                            = 'smaract channel (alpha) target position is out of reach!'
        self.smaract_err_beta_not_reachable                             = 'smaract channel (beta) target position is out of reach!'
        self.smaract_err_gamma_steps_invalid                            = 'smaract channel gamma movement is invalid!'
        self.smaract_err_linear_speed_invalid                           = 'smaract channel (x or y or z) speed is invalid!'
        self.smaract_err_angular_speed_invalid                          = 'smaract channel (alpha or beta) speed is invalid!'
        self.smaract_err_gamma_frequency_invalid                        = 'smaract channel gamma frequency is invalid!'
        self.smaract_err_linear_steps_min_invalid                       = 'the entered smaract linear step was invalid and is resetted to the valid minimum!'
        self.smaract_err_linear_steps_max_invalid                       = 'the entered smaract linear step was invalid and is resetted to the valid maximum!'
        self.smaract_err_angular_steps_min_invalid                      = 'the entered smaract angular step was invalid and is resetted to the valid minimum!'
        self.smaract_err_angular_steps_max_invalid                      = 'the entered smaract angular step was invalid and is resetted to the valid maximum!'
        self.smaract_err_gamma_steps_min_invalid                        = 'the entered smaract gamma step was invalid and is resetted to the valid minimum!'
        self.smaract_err_gamma_steps_max_invalid                        = 'the entered smaract gamma step was invalid and is resetted to the valid maximum!'
        self.smaract_err_linear_speed_base_invalid                      = 'the entered smaract linear speed base was invalid and is resetted!'
        self.smaract_err_angular_speed_base_invalid                     = 'the entered smaract angular speed base was invalid and is resetted!'
        self.smaract_err_gamma_frequency_base_invalid                   = 'the entered smaract gamma frequency base was invalid and is resetted!'
        self.smaract_err_linear_speed_positioning_min_invalid           = 'the entered smaract linear speed for positioning was invalid and is resetted to the valid minimum!'
        self.smaract_err_linear_speed_positioning_max_invalid           = 'the entered smaract linear speed for positioning was invalid and is resetted to the valid maximum!'
        self.smaract_err_angular_speed_positioning_min_invalid          = 'the entered smaract angular speed for positioning was invalid and is resetted to the valid minimum!'
        self.smaract_err_angular_speed_positioning_max_invalid          = 'the entered smaract angular speed for positioning was invalid and is resetted to the valid maximum!'
        self.smaract_err_linear_speed_on_click_min_invalid              = 'the entered smaract linear speed for onClick was invalid and is resetted to the valid minimum!'
        self.smaract_err_linear_speed_on_click_max_invalid              = 'the entered smaract linear speed for onClick was invalid and is resetted to the valid maximum!'
        self.smaract_err_linear_pos_invalid                             = 'the entered smaract desired position of x and y channel was invalid and is resetted!'
        self.smaract_err_z_pos_invalid                                  = 'the entered smaract desired position of z channel was invalid and is resetted!'
        self.smaract_err_alpha_pos_invalid                              = 'the entered smaract desired position of alpha channel was invalid and is resetted!'
        self.smaract_err_beta_pos_invalid                               = 'the entered smaract desired position of beta channel was invalid and is resetted!'

        # asm constants and variables
        # # steps
        self.asm_steps_base                                             = 100   
        self.asm_steps_min                                              = 10    
        self.asm_steps_max                                              = 1000  
        self.asm_delay_ms                                               = 3
        # # errors
        self.asm_err_steps_min_invalid                                  = 'the entered asm step was invalid and is resetted to the valid minimum!'
        self.asm_err_steps_max_invalid                                  = 'the entered asm step was invalid and is resetted to the valid maximum!'

        # pistage constants and variables
        # # axes
        self.pistage_l1                                                 = 1
        self.pistage_l1_str                                             = 'L1'
        self.pistage_l2                                                 = 2
        self.pistage_l2_str                                             = 'L2'
        # # referencing
        self.pistage_referencing_default                                = 0
        self.pistage_referencing_l1_done                                = 1
        self.pistage_referencing_l1_failed                              = 2
        self.pistage_referencing_l2_done                                = 3
        self.pistage_referencing_l2_failed                              = 4
        self.pistage_referencing_done                                   = 5
        self.pistage_referencing_l1_failed_text                         = 'referencing (l1) has been failed!'
        self.pistage_referencing_l2_failed_text                         = 'referencing (l2) has been failed!'
        self.pistage_referencing_done_text                              = 'referencing has been done.'
        self.pistage_referencing_default_text                           = 'not referenced yet.'
        # # speed multiplier
        self.pistage_speed_multiplier_indices                           = [0, 1, 2, 3, 4]
        self.pistage_speed_multiplier_values                            = [1, 2, 3, 4, 5]
        self.pistage_speed_multiplier_index                             = self.pistage_speed_multiplier_indices[0]
        self.pistage_speed_multiplier_value                             = self.pistage_speed_multiplier_values[self.pistage_speed_multiplier_index]
        self.pistage_speed_multiplier_increase                          = 1
        self.pistage_speed_multiplier_decrease                          = -1
        # # steps and position
        self.pistage_steps_base                                         = 0.1       # mm
        self.pistage_steps_min                                          = 0.0       # mm 
        self.pistage_steps_max                                          = 5.0       # mm 
        self.pistage_pos_min_safe                                       = 0.1       # mm (used for checking the movement when using the gamepad), min is 0mm
        self.pistage_pos_max_safe                                       = 99.9      # mm (used for checking the movement when using the gamepad), max is 100mm
        self.pistage_pos_l1_desired                                     = 31.00     # mm (used in positioning)
        self.pistage_pos_l2_desired                                     = 7.00      # mm (used in positioning)
        # # speed
        self.pistage_speed_base                                         = 4         # mm/s   
        self.pistage_speed_min_safe                                     = 0         # mm/s (used for checking the speed when using the gamepad), min is 0mm/s
        self.pistage_speed_max_safe                                     = 20        # mm/s (used for checking the speed when using the gamepad), max is 20mm/s
        self.pistage_speed_positioning                                  = 2         # mm/s (used in positioning)
        # # sleep multiplier
        self.pistage_sleep_multiplier_positioning                       = 0.2  
        self.pistage_development_wait                                   = 0         # sec.     #30*60
        # # errors
        self.pistage_err_l1_not_reachable                               = 'pistage (l1) target position is out of reach!'
        self.pistage_err_l2_not_reachable                               = 'pistage (l2) target position is out of reach!'
        self.pistage_err_speed_invalid                                  = 'pistage (l1 or l2) speed is invalid!'
        self.pistage_err_steps_min_invalid                              = 'the entered pistage step was invalid and is resetted to the valid minimum!'
        self.pistage_err_steps_max_invalid                              = 'the entered pistage step was invalid and is resetted to the valid maximum!'
        self.pistage_err_speed_base_invalid                             = 'the entered pistage speed based was invalid and is resetted!'
        self.pistage_err_speed_positioning_min_invalid                  = 'the entered pistage speed for positioning was invalid and is resetted to the valid minimum!'
        self.pistage_err_speed_positioning_max_invalid                  = 'the entered pistage speed for positioning was invalid and is resetted to the valid maximum!'
        self.pistage_pos_l1_invalid                                     = 'the entered pistage desired position of l1 was invalid and is resetted!'
        self.pistage_pos_l2_invalid                                     = 'the entered pistage desired position of l2 was invalid and is resetted!'

        # camera constants and variables
        self.camera_image                                               = 0
        self.camera_buffer                                              = 10
        self.camera_pixel_format                                        = 'Mono8'
        self.camera_exposure_time                                       = 1000  # us = 1ms
        self.camera_width                                               = 1200  # px
        self.camera_height                                              = 1200  # px
        self.camera_offset_x                                            = 0     # px
        self.camera_offset_y                                            = 0     # px
        self.camera_reverse_x                                           = False
        self.camera_reverse_y                                           = False
        self.camera_sleep_time_s                                        = 0.1
        self.camera_timeout_ms                                          = 100
        self.camera_err_width_min_invalid                               = 'the entered camera width was invalid and is resetted to the valid minimum!'
        self.camera_err_width_max_invalid                               = 'the entered camera width was invalid and is resetted to the valid maximum!'
        self.camera_err_width_increment_invalid                         = 'the entered camera width was invalid because the valid width increment is 4!'
        self.camera_err_height_min_invalid                              = 'the entered camera height was invalid and is resetted to the valid minimum!'
        self.camera_err_height_max_invalid                              = 'the entered camera height was invalid and is resetted to the valid maximum!'
        self.camera_err_height_increment_invalid                        = 'the entered camera height was invalid because the valid height increment is 2!'
        self.camera_flag_off                                            = True
        self.camera_err_off                                             = 'camera is off!'
        
        # gamepad constants and variables
        self.gamepad_not_found                                          = 1167
        self.gamepad_not_found_text                                     = 'not found!'
        self.gamepad_found                                              = 0
        self.gamepad_found_text                                         = 'Connected.'
        self.gamepad_buttons = {'DPAD_UP': 0x0001, 'DPAD_DOWN': 0x0002, 'DPAD_LEFT': 0x0004, 'DPAD_RIGHT': 0x0008,
                                'START': 0x0010, 'BACK': 0x0020,
                                'LB': 0x0100, 'RB': 0x0200,
                                'A': 0x1000, 'B': 0x2000, 'X': 0x4000, 'Y': 0x8000
                               }
        self.gamepad_triggers = {'LT': 'bLeftTrigger', 'RT': 'bRightTrigger'}
        self.gamepad_sticks = {'LS_X': 'sThumbLX', 'LS_Y': 'sThumbLY', 'RS_X': 'sThumbRX', 'RS_Y': 'sThumbRY'}
        self.gamepad_axes = {**self.gamepad_triggers, **self.gamepad_sticks}    # merging triggers and sticks
        # # threshold for the gamepad axes such that if the abs(value of axis) is less than this threshold, the command will be ignored.  
        self.gamepad_threshold                                          = 0.6
        # # threshold for the gamepad axes such that if the change in the value of axis is less than this threshold, the command will be ignored.
        self.gamepad_sensitivity                                        = 0.2
        self.gamepad_polling_time_s                                     = 0.05
        self.gamepad_polling_time_button_s                              = 0.15

        # control constants and variables
        self.control_smaract_translation                                = 0
        self.control_smaract_translation_str                            = 'Translation'
        self.control_smaract_rotation                                   = 1
        self.control_smaract_rotation_str                               = 'Rotation'
        self.control_smaract_default                                    = -1
        self.control_smaract_status                                     = self.control_smaract_default
        self.control_pistage_l1                                         = 1
        self.control_pistage_l2                                         = 2
        self.control_pistage_default                                    = -1
        self.control_pistage_status                                     = self.control_pistage_default

        # id constants and variables
        self.id_smaract_channel_x                                       = 0
        self.id_smaract_channel_y                                       = 1
        self.id_smaract_channel_z                                       = 2
        self.id_smaract_channel_alpha                                   = 3
        self.id_smaract_channel_beta                                    = 4
        self.id_smaract_channel_gamma                                   = 5  
        self.id_asm                                                     = 6
        self.id_pistage_l1                                              = 7
        self.id_pistage_l2                                              = 8
        
        # sequence constants and variables
        self.sequence_linear_speed                                  	= 800000    	    # nm/s = 0.8mm/s
        self.sequence_angular_speed                                     = 8000000    	    # uDeg/s = 8deg/s
        self.sequence_initial_alpha                                     = 839192            # uDeg = 0.839192deg
        self.sequence_initial_beta                                      = 44000000          # uDeg = 44deg (used to be 53deg)
        self.sequence_initial_z                                         = 8100000           # nm = 8.10mm (used to be 18.650mm)
        self.sequence_delta_z                                           = [420, 50]         # um 
        self.sequence_delta_y                                           = [0, 120]          # um
        self.sequence_cut_num                                           = 3
        self.sequence_asm_sleep_time_s                                  = 0.5
        self.sequence_sleep_multiplier_initialize                       = 1.1
        self.sequence_sleep_multiplier_do                               = 1.5
        self.sequence_flag_release_debris                               = 0
        
        # annotation (computer vision) constants and variables
        self.annotation_points                                          = []
        self.annotation_point_offset                                    = 5     # px
        self.annotation_white_level                                     = 255
        self.annotation_edge_level_1                                    = self.annotation_white_level//2
        self.annotation_edge_level_2                                    = self.annotation_white_level
        self.annotation_edge_aperture_size                              = 3    # px
        self.annotation_edge_l2_gradient                                = True
        self.annotation_closing_kernel_size                             = 7    # px
        self.annotation_closing_iterations                              = 3
        self.annotation_blurring_sigma_x                                = 1
        self.annotation_blurring_kernel_size                            = 6*self.annotation_blurring_sigma_x + 1
        self.annotation_area_value_min                                  = 20000 # px
        self.annotation_flag_save_image                                 = 0
        self.annotation_flag_stop_camera                                = 0
        self.annotation_directory                                       = './images_annotated/'
        self.annotation_err_no_areas                                    = 'no areas are found!'
        self.annotation_err_no_centroid                                 = 'no centroids are found!'
        # # embryo
        self.annotation_embryo_points                                   = []
        self.annotation_embryo_counter                                  = 1   
        self.annotation_embryo_gray_level_1                             = 180
        self.annotation_embryo_gray_level_2                             = 120
        self.annotation_embryo_crop_middle_offset                       = 80    # px
        self.annotation_embryo_crop_offset                              = 10    # px
        self.annotation_embryo_fill_offset                              = 2     # px
        self.annotation_embryo_openning_kernel_size                     = 7     # px
        self.annotation_embryo_openning_iterations                      = 3
        self.annotation_embryo_circle_dp                                = 5
        self.annotation_embryo_circle_param_1                           = 255
        self.annotation_embryo_circle_param_2                           = 220
        self.annotation_embryo_point_offset_x                           = 0     # px
        self.annotation_embryo_point_offset_y                           = 0     # px, -100
        self.annotation_embryo_flag_cv_dn                               = 0     # 0: cv (computer vision), 1: dn (deep network)
        self.annotation_embryo_err_no_circle                            = 'no circle is detected!'
        self.annotation_embryo_directory                                = self.annotation_directory + 'emb_'
        # # scissor
        self.annotation_scissor_points                                  = []
        self.annotation_scissor_counter                                 = 1
        self.annotation_scissor_gray_level                              = 40
        self.annotation_scissor_crop_offset                             = 0     # px
        self.annotation_scissor_line_rho                                = 1
        self.annotation_scissor_line_theta                              = 1     # [deg]
        self.annotation_scissor_diagonal_line_offset                    = 20    # px
        self.annotation_scissor_diagonal_line_vote                      = 60
        self.annotation_scissor_diagonal_line_length_min                = 120   # px
        self.annotation_scissor_diagonal_line_gap_max                   = 50    # px
        self.annotation_scissor_diagonal_line_slope_min                 = 60    # [deg]
        self.annotation_scissor_diagonal_line_slope_max                 = 80    # [deg]
        self.annotation_scissor_err_no_line                             = 'no line is detected!'
        self.annotation_scissor_err_no_intersection                     = 'intersection is not in the field of view!'
        self.annotation_scissor_directory                               = self.annotation_directory + 'scs_'

        # automation constants and variables
        self.automation_counter                                         = 1
        self.automation_directory                                       = './images_automation/'
        self.automation_num_l1                                          = 6         # number of embryos in the pistage l1 direction
        self.automation_num_l2                                          = 6         # number of embryos in the pistage l2 direction
        self.automation_step_l1                                         = 2.00      # mm, spacing between embryos in the pistage l1 direction
        self.automation_step_l2                                         = 2.00      # mm, spacing between embryos in the pistage l2 direction
        self.automation_speed_smaract                                   = 800000    # nm/s = 0.8mm/s
        self.automation_speed_pistage                                   = 0.8       # mm/s
        self.automation_flag_save_image                                 = 0
        self.automation_flag_release_debris                             = 0
        self.automation_flag_cv_dn                                      = 0         # 0: cv (computer vision), 1: dn (deep network)
        self.automation_message_done                                    = 'automation is done.'
        self.automation_message_stopped                                 = 'automation is stopped! you have to reconnect in order to move any component!'
        self.automation_message_next                                    = 'going to embryo '
        self.automation_message_annotating                              = 'annotating embryo '
        self.automation_message_sequence                                = 'dissecting embryo '
        self.automation_sleep_multiplier_pistage                        = 0.2
        self.automation_sleep_multiplier_smaract                        = 1.5
        self.automation_flag_stopped                                    = False
        
        # positioning variables to store the initial position of smaract channels prior to perform the cutting sequence
        self.pos_initial_x                                              = 0
        self.pos_initial_y                                              = 0
        self.pos_initial_z                                              = 0

        # coords constants and variables
        self.coords_temp                                                = []
        self.coords_target                                              = []
        self.coords_tool                                                = []
        self.coords_empty_text                                          = 'no coordinates!'

        # gui constants and variables
        self.gui_empty_text                                             = '-'
        self.gui_sleep_time_s                                           = 0.3
        self.gui_close_thread_time_s                                    = 1.0
        self.gui_close_window_time_ms                                   = 500
        self.gui_err_clicked_pos_invalid                                = 'clicked position is out of range!'
        self.gui_directory                                              = './images_gui/'
        self.gui_window_title                                           = 'Robotic Surgery Software'

        # reconnection constants and variables
        self.reconnection_message_done_smaract                          = 'smaract has been reconnected.'
        self.reconnection_message_done_asm                              = 'asm has been reconnected.'
        self.reconnection_message_failed_smaract                        = 'smaract reconnection failed with status: '
        self.reconnection_message_failed_asm                            = 'asm reconnection failed with status: '

        # general constants and variables
        self.mili_to_nano                                               = 1000000
        self.nano_to_mili                                               = 1/self.mili_to_nano
        self.micro_to_nano                                              = 1000
        self.nano_to_micro                                              = 1/self.micro_to_nano
        self.mili_to_micro                                              = 1000
        self.micro_to_mili                                              = 1/self.mili_to_micro
        self.micro                                                      = 1000000
        self.pixel_to_mili                                              = 1/690    # 104px/mm for 0.63x, 660/684/690px/mm for 4x, found by imageJ calibration
        self.mili_to_pixel                                              = 1/self.pixel_to_mili
        self.save_counter                                               = 1
        self.save_directory                                             = './images_saved/'
        self.flag_save_images_annotation                                = False
        self.text_edit_mode_err                                         = 0
        self.text_edit_mode_info                                        = 1
        self.color_red                                                  = (0, 0, 255)   # bgr
        self.color_blue                                                 = (255, 0, 0)   # bgr
        self.color_green                                                = (0, 255, 0)   # bgr
        self.color_cyan                                                 = (255, 255, 0) # bgr
        self.color_yellow                                               = (0, 255, 255) # bgr
        
        # deep network constants and variables
        self.dn_path                                                    = './deep_networks/deep_tube.h5'
        self.dn_image_size                                              = 240   # px
        self.dn_filters_num                                             = 16
        self.dn_kernel_size                                             = 3
        self.dn_stride                                                  = 2
        self.dn_dropout                                                 = 0.5
        self.dn_flag_batch_norm                                         = True
        self.dn_threshold                                               = 0.5
        self.dn_somite_height_um                                        = 50    # um
        self.dn_somite_height_px                                        = self.dn_somite_height_um * self.micro_to_mili * self.mili_to_pixel
        self.dn_somite_target                                           = 5  
        self.dn_white_level                                             = 255
        self.dn_white_level_normalized                                  = 1
        self.dn_threshold_min                                           = 0
        self.dn_threshold_max                                           = 1
        self.dn_err_threshold_invalid                                   = 'the entered threshold for deep network was invalid and is set to the previous valid value!'
        self.dn_err_empty                                               = 'the thresholded output image of the deep network is empty!'
