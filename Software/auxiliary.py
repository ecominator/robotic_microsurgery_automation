##############################################################################
# File name:    auxiliary.py
# Project:      Robotic Surgery Software
# Part:         Auxiliary functionalities
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file contains various functions used in the 
#               Robotic Surgery Software.
##############################################################################


# Modules
import computer_vision as vision
import numpy as np
import time


def smaract_is_valid_relative_movement(config, channel_index, absolute_position, relative_movement):
    '''
    checking the validity of the desired relative movement given to the smaract channels considering their workspace
    '''

    # x, y, and z channels
    if (channel_index in [config.smaract_channel_x, config.smaract_channel_y, config.smaract_channel_z]):
        if (absolute_position + relative_movement < config.smaract_linear_pos_min_safe):
            return False
        elif (absolute_position + relative_movement > config.smaract_linear_pos_max_safe):
            return False
    # alpha and beta channels
    elif (channel_index in [config.smaract_channel_alpha, config.smaract_channel_beta]):
        if (absolute_position + relative_movement < config.smaract_angular_pos_min_safe):
            return False
        elif (absolute_position + relative_movement > config.smaract_angular_pos_max_safe):
            return False
    # gamma channel
    elif (channel_index == config.smaract_channel_gamma):
        if (relative_movement < config.smaract_gamma_steps_min_safe):
            return False
        elif (relative_movement > config.smaract_gamma_steps_max_safe):
            return False
    return True


def pistage_is_valid_relative_movement(config, absolute_position, relative_movement):
    '''
    checking the validity of the desired relative movement given to the pistage axes considering their workspace
    '''

    if (absolute_position + relative_movement < config.pistage_pos_min_safe):
        return False
    elif (absolute_position + relative_movement > config.pistage_pos_max_safe):
        return False
    return True	


def smaract_is_valid_speed(config, channel_index, speed):
    '''
    checking the validity of the desired speed given to the smaract channels considering their limits
    '''

    # x, y, and z channels
    if (channel_index in [config.smaract_channel_x, config.smaract_channel_y, config.smaract_channel_z]):
        if (speed < config.smaract_linear_speed_min_safe):
            return False
        elif (speed > config.smaract_linear_speed_max_safe):
            return False
    # alpha and beta channels
    elif (channel_index in [config.smaract_channel_alpha, config.smaract_channel_beta]):
        if (speed < config.smaract_angular_speed_min_safe):
            return False
        elif (speed > config.smaract_angular_speed_max_safe):
            return False
    # gamma channel
    elif (channel_index == config.smaract_channel_gamma):
        if (speed < config.smaract_gamma_frequency_min_safe):
            return False
        elif (speed > config.smaract_gamma_frequency_max_safe):
            return False
    return True


def pistage_is_valid_speed(config, speed):
    '''
    checking the validity of the desired speed given to the pistage axes considering their limits
    '''

    if (speed < config.pistage_speed_min_safe):
        return False
    elif (speed > config.pistage_speed_max_safe):
        return False
    return True


def smaract_move_channel_to_position_sleep(smaract, channel_index, absolute_position, speed, sleep_multiplier):
    sleep_time = abs(absolute_position - smaract.get_channel_position(channel_index)) / speed
    smaract.move_channel_to_position(channel_index, absolute_position, speed)
    time.sleep(sleep_time * sleep_multiplier)


def smaract_move_channel_sleep(smaract, channel_index, relative_movement, speed, sleep_multiplier):
    sleep_time = abs(relative_movement) / speed
    smaract.move_channel(channel_index, relative_movement, speed)
    time.sleep(sleep_time * sleep_multiplier)


def pistage_move_axis_to_position_sleep(pistage, axis_index, absolute_position, speed, sleep_multiplier):
    sleep_time = abs(absolute_position - pistage.get_axis_position(axis_index)) / speed
    pistage.move_axis_to_position(axis_index, absolute_position, speed)
    time.sleep(sleep_time * sleep_multiplier)


def pistage_move_axis_sleep(pistage, axis_index, relative_movement, speed, sleep_multiplier):
    sleep_time = abs(relative_movement) / speed
    pistage.move_axis(axis_index, relative_movement, speed)
    time.sleep(sleep_time * sleep_multiplier)


def scissor_close(asm, config):
    asm.move(-config.asm_steps_base*config.sequence_cut_num)
        

def scissor_open(asm, config):
    asm.move(config.asm_steps_base*config.sequence_cut_num)


def clicked_position_is_valid(config, x, y):
    '''
    checking if the clicked position on the camera acquired image is valid
    '''

    if (x < 0) or (x > config.camera_width) or (y < 0) or (y > config.camera_height):
        return False
    return True


def normalize_image(img, range_min=0, range_max=255):
    img_temp = img.copy()
    return range_min + (img_temp-np.min(img_temp))/(np.max(img_temp)-np.min(img_temp))*(range_max-range_min)


def automation_extract_embryo_from_image(img, config):
    img_temp = img.copy()
    # blurring
    img_bl = vision.apply_blurring(img_temp, config.annotation_blurring_kernel_size, config.annotation_blurring_sigma_x)
    if config.automation_flag_save_image:
        vision.save_image(img_bl, str(config.automation_counter)+'_emb_bl', config.automation_directory)
    # thresholding
    img_th = vision.apply_in_range_threshold(img_bl, config.annotation_scissor_gray_level, config.annotation_embryo_gray_level_1)
    if config.automation_flag_save_image:
        vision.save_image(img_th, str(config.automation_counter)+'_emb_th', config.automation_directory)
    # seprating embryo from the background
    labels, areas = vision.find_connected_components(img_th)
    if len(areas) == 0:
        return None, None, False, config.annotation_err_no_areas
    elif np.max(areas) < config.annotation_area_value_min:
        return None, None, False, config.annotation_err_no_areas
    area_max_idx = np.argmax(areas)
    img_desired = np.zeros(labels.shape, dtype=np.uint8)
    img_desired[labels == area_max_idx + 1] = config.annotation_white_level
    if config.automation_flag_save_image:
        vision.save_image(img_desired, str(config.automation_counter)+'_emb', config.automation_directory)
    return img_desired, img_bl, True, None


def automation_extract_scissor_from_image(img, config):
    img_temp = img.copy()
    # blurring
    img_bl = vision.apply_blurring(img_temp, config.annotation_blurring_kernel_size, config.annotation_blurring_sigma_x)
    if config.automation_flag_save_image:
        vision.save_image(img_bl, str(config.automation_counter)+'_scs_bl', config.automation_directory)
    # thresholding
    img_th = vision.apply_in_range_threshold(img_bl, 0, config.annotation_scissor_gray_level)
    if config.automation_flag_save_image:
        vision.save_image(img_th, str(config.automation_counter)+'_scs_th', config.automation_directory)
    # seprating scissor from the background
    labels, areas = vision.find_connected_components(img_th)
    if len(areas) == 0:
        return None, None, False, config.annotation_err_no_areas
    elif np.max(areas) < config.annotation_area_value_min:
        return None, None, False, config.annotation_err_no_areas
    area_max_idx = np.argmax(areas)
    img_desired = np.zeros(labels.shape, dtype=np.uint8)
    img_desired[labels == area_max_idx + 1] = config.annotation_white_level
    if config.automation_flag_save_image:
        vision.save_image(img_desired, str(config.automation_counter)+'_scs', config.automation_directory)
    return img_desired, img_bl, True, None


def automation_annotate_embryo(img_cam, config, model):
    # extracting embryo from the image
    img_th, img_bl, flag, err = automation_extract_embryo_from_image(img_cam, config)
    if flag == False:
        return flag, err
    if config.automation_flag_cv_dn:     # deep network
        # processing the image to be fed to the deep network
        img_th_cr, img_cr, x_cropped, y_cropped = vision.crop_image(img_th, img_cam, config.annotation_embryo_crop_offset)
        h_emb, w_emb = img_cr.shape
        img_rs = vision.resize_image_by_size(img_cr, config.dn_image_size, config.dn_image_size)
        img_in_arr = np.zeros((1, config.dn_image_size, config.dn_image_size, 1), dtype=np.float32)
        img_in_arr[0, :, :, 0] = np.float32(img_rs) / config.dn_white_level
        img_out_arr = model.predict(img_in_arr, verbose=0)
        # processing the output of the deep network
        img_out = img_out_arr[0, :, :, 0]
        img_out_rs = vision.resize_image_by_size(img_out, w_emb, h_emb)
        if config.automation_flag_save_image:
            vision.save_image(img_out_rs*config.dn_white_level, str(config.automation_counter)+'_dn_out', config.automation_directory)
        img_out_th = np.zeros(img_out_rs.shape)
        img_out_th[img_out_rs > config.dn_threshold] = config.dn_white_level_normalized
        if config.automation_flag_save_image:
            vision.save_image(img_out_th*config.dn_white_level, str(config.automation_counter)+'_dn_th', config.automation_directory)
        # computing the annotation coordinates
        ids = np.argwhere(img_out_th == config.dn_white_level_normalized)
        if ids.size == 0:
            return False, config.dn_err_empty
        top = ids[:, 0].min()
        bottom = ids[:, 0].max()
        y_arr = np.arange(bottom, top, -int(config.dn_somite_height_px))
        x_arr = np.zeros(y_arr.shape, dtype=int)
        for i in range(len(y_arr)):
            y = y_arr[i]
            id_closest = np.abs(ids[:, 0] - y).argmin()
            y_closest = ids[id_closest, 0]
            x_arr[i] = int(np.mean(ids[ids[:, 0]==y_closest][:, 1]))
        if config.automation_flag_save_image:
            temp_points = [(int(x), int(y), (0, 0, 255)) for x, y in zip(x_arr, y_arr)]
            img_drawn = vision.draw_points(np.float32(img_out_th*config.dn_white_level), temp_points, config.annotation_point_offset)
            vision.save_image(img_drawn, str(config.automation_counter)+'_dn_th_ann', config.automation_directory)
        # converting the coordinates to match the dimensions of the full image
        x_arr = x_arr + x_cropped
        y_arr = y_arr + y_cropped
        # processing the annotation points
        config.annotation_embryo_points = [(int(x), int(y), (0, 0, 255)) for x, y in zip(x_arr, y_arr)] 
        # # config.annotation_points = list(set(config.annotation_embryo_points).union(set(config.annotation_points)))  
        config.annotation_points = config.annotation_points + config.annotation_embryo_points
        return True, None
    else:   # computer vision   
        # cropping
        img_th_cr, img_bl_cr, x_cropped, y_cropped = vision.crop_image(img_th, img_bl, config.annotation_embryo_crop_offset)
        h_full, w_full = img_th_cr.shape
        if config.automation_flag_save_image:
            vision.save_image(img_th_cr, str(config.automation_counter)+'_emb_th_cr', config.automation_directory)
            vision.save_image(img_bl_cr, str(config.automation_counter)+'_emb_bl_cr', config.automation_directory)
        # filling
        img_fl = vision.fill_image(img_th_cr, config.annotation_embryo_fill_offset, config.annotation_white_level)
        if config.automation_flag_save_image:
            vision.save_image(img_fl, str(config.automation_counter)+'_emb_fl', config.automation_directory)
        # closing
        img_cl = vision.apply_closing(img_fl, config.annotation_closing_kernel_size, config.annotation_closing_iterations)
        if config.automation_flag_save_image:
            vision.save_image(img_cl, str(config.automation_counter)+'_emb_cl', config.automation_directory)
        # calculating the centroid of the full embryo
        x_full_centroid, y_full_centroid = vision.calculate_centroid(img_cl)
        if (x_full_centroid, y_full_centroid) == (None, None):
            return False, config.annotation_err_no_centroid
        # detecting the edges
        img_ed = vision.detect_edges(img_cl, config.annotation_edge_level_1, config.annotation_edge_level_2, config.annotation_edge_aperture_size, config.annotation_edge_l2_gradient)
        if config.automation_flag_save_image:
            vision.save_image(img_ed, str(config.automation_counter)+'_emb_ed', config.automation_directory)
        # detecting the circles
        img_crc, x_circle, y_circle = vision.detect_circles(img_ed, config.annotation_embryo_circle_dp,
                                                            config.annotation_embryo_circle_param_1, config.annotation_embryo_circle_param_2, offset=config.annotation_point_offset)
        if (x_circle, y_circle) == (None, None):
            return False, config.annotation_embryo_err_no_circle
        if config.automation_flag_save_image:
            vision.save_image(img_crc, str(config.automation_counter)+'_emb_crc', config.automation_directory)
        # cropping the middle part of the image
        img_mid = img_bl_cr[:, x_circle-config.annotation_embryo_crop_middle_offset:x_circle+config.annotation_embryo_crop_middle_offset]
        if config.automation_flag_save_image:
            vision.save_image(img_mid, str(config.automation_counter)+'_emb_mid', config.automation_directory)
        h_mid, w_mid = img_mid.shape
        # thresholding
        img_mid_th = vision.apply_in_range_threshold(img_mid, 0, config.annotation_embryo_gray_level_2)
        if config.automation_flag_save_image:
            vision.save_image(img_mid_th, str(config.automation_counter)+'_emb_mid_th', config.automation_directory)
        # processing the lower half of the image 
        img_low = img_mid_th[h_mid//2:, :]
        if config.automation_flag_save_image:
            vision.save_image(img_low, str(config.automation_counter)+'_emb_low', config.automation_directory)
        img_low_op = vision.apply_opening(img_low, config.annotation_embryo_openning_kernel_size, config.annotation_embryo_openning_iterations)
        if config.automation_flag_save_image:
            vision.save_image(img_low_op, str(config.automation_counter)+'_emb_low_op', config.automation_directory)
        x_low_centroid, y_low_centroid = vision.calculate_centroid(img_low_op)
        if (x_low_centroid, y_low_centroid) == (None, None):
            return False, config.annotation_err_no_centroid
        x_low_centroid = x_low_centroid + x_circle - config.annotation_embryo_crop_middle_offset
        y_low_centroid = y_low_centroid + h_mid//2
        # processing the upper half of the image
        img_up = img_cl[:h_mid//3, :]
        if config.automation_flag_save_image:
            vision.save_image(img_up, str(config.automation_counter)+'_emb_up', config.automation_directory)
        img_up_op = vision.apply_opening(img_up, config.annotation_embryo_openning_kernel_size, config.annotation_embryo_openning_iterations)
        if config.automation_flag_save_image:
            vision.save_image(img_up_op, str(config.automation_counter)+'_emb_up_op', config.automation_directory)
        x_up_centroid, y_up_centroid = vision.calculate_centroid(img_up_op)
        if (x_up_centroid, y_up_centroid) == (None, None):
            return False, config.annotation_err_no_centroid
        # converting the coordinates to match the dimensions of the full image
        x_low_centroid = x_low_centroid + x_cropped
        x_up_centroid = x_up_centroid + x_cropped
        y_low_centroid = y_low_centroid + y_cropped
        y_up_centroid = y_up_centroid + y_cropped
        # processing the annotation points
        config.annotation_embryo_points = [(x_low_centroid, y_low_centroid, (255, 255, 0)), 
                                           (x_up_centroid, y_up_centroid, (0, 255, 0)), 
                                           ((x_low_centroid+x_up_centroid)//2, y_low_centroid, (0, 0, 255)), 
                                           (x_low_centroid+config.annotation_embryo_point_offset_x, y_low_centroid+config.annotation_embryo_point_offset_y, (255, 0, 0))
                                          ]
        # # config.annotation_points = list(set(config.annotation_embryo_points).union(set(config.annotation_points)))  
        config.annotation_points = config.annotation_points + config.annotation_embryo_points
        return True, None


def automation_annotate_scissor(img_cam, config):
    # extracting scissor from the image
    img_th, img_bl, flag, err = extract_scissor_from_image(img_cam, config)
    if flag == False:
        return flag, err
    # cropping
    img_th_cr, img_bl_cr, x_cropped, y_cropped = vision.crop_image(img_th, img_bl, config.annotation_scissor_crop_offset)
    h_full, w_full = img_th_cr.shape
    if config.automation_flag_save_image:
        vision.save_image(img_th_cr, str(config.automation_counter)+'_scs_th_cr', config.automation_directory)
        vision.save_image(img_bl_cr, str(config.automation_counter)+'_scs_bl_cr', config.automation_directory)
    # closing
    img_cl = vision.apply_closing(img_th_cr, config.annotation_closing_kernel_size, config.annotation_closing_iterations)
    if config.automation_flag_save_image:
        vision.save_image(img_cl, str(config.automation_counter)+'_scs_cl', config.automation_directory)
    # calculating the centroid of the full scissor
    x_full_centroid, y_full_centroid = vision.calculate_centroid(img_cl)
    if (x_full_centroid, y_full_centroid) == (None, None):
        return False, config.annotation_err_no_centroid
    # detecting the edges
    img_ed = vision.detect_edges(img_cl, config.annotation_edge_level_1, config.annotation_edge_level_2, config.annotation_edge_aperture_size, config.annotation_edge_l2_gradient)
    if config.automation_flag_save_image:
        vision.save_image(img_ed, str(config.automation_counter)+'_scs_ed', config.automation_directory)
    # dividing the scissor into two parts (left and right)
    img_left = img_ed[:, :x_full_centroid]
    img_right = img_ed[:, x_full_centroid:]
    # detecting lines in the left part
    img_left_ann, points_left = vision.detect_lines(img_left, config.annotation_scissor_line_rho, config.annotation_scissor_line_theta,
                                                    config.annotation_scissor_diagonal_line_vote, config.annotation_scissor_diagonal_line_length_min,
                                                    config.annotation_scissor_diagonal_line_gap_max, config.annotation_scissor_diagonal_line_slope_min,
                                                    config.annotation_scissor_diagonal_line_slope_max)
    if points_left == None:
        return False, config.annotation_scissor_err_no_line
    if config.automation_flag_save_image:
        vision.save_image(img_left_ann, str(config.automation_counter)+'_scs_left_ann', config.automation_directory)
    # detecting lines in the right part
    img_right_ann, points_right = vision.detect_lines(img_right, config.annotation_scissor_line_rho, config.annotation_scissor_line_theta,
                                                      config.annotation_scissor_diagonal_line_vote, config.annotation_scissor_diagonal_line_length_min,   
                                                      config.annotation_scissor_diagonal_line_gap_max, config.annotation_scissor_diagonal_line_slope_min,
                                                      config.annotation_scissor_diagonal_line_slope_max)
    if points_right == None:
        return False, config.annotation_scissor_err_no_line
    if config.automation_flag_save_image:
        vision.save_image(img_right_ann, str(config.automation_counter)+'_scs_right_ann', config.automation_directory)
    # converting the coordinates to match the dimensions of the full image
    x1 = points_left[0] + config.annotation_scissor_diagonal_line_offset + x_cropped
    x2 = points_left[2] + config.annotation_scissor_diagonal_line_offset + x_cropped
    y1 = points_left[1] + y_cropped
    y2 = points_left[3] + y_cropped
    x3 = points_right[0] - config.annotation_scissor_diagonal_line_offset + x_full_centroid + x_cropped
    x4 = points_right[2] - config.annotation_scissor_diagonal_line_offset + x_full_centroid + x_cropped
    y3 = points_right[1] + y_cropped
    y4 = points_right[3] + y_cropped
    # calculating the intersection point
    x_intersection = int(((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)))
    y_intersection = int(((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)))
    if x_intersection < 0 or x_intersection > img_th.shape[1] or y_intersection < 0 or y_intersection > img_th.shape[0]:
        return False, config.annotation_scissor_err_no_intersection
    # processing the annotation points
    config.annotation_scissor_points = [(x_intersection, y_intersection, (0, 255, 255))]
    # # config.annotation_points = list(set(config.annotation_scissor_points).union(set(config.annotation_points)))
    config.annotation_points = config.annotation_points + config.annotation_scissor_points
    return True, None


def extract_embryo_from_image(img, config):
    img_temp = img.copy()
    # blurring
    img_bl = vision.apply_blurring(img_temp, config.annotation_blurring_kernel_size, config.annotation_blurring_sigma_x)
    if config.annotation_flag_save_image:
        vision.save_image(img_bl, str(config.annotation_embryo_counter)+'_bl', config.annotation_embryo_directory)
    # thresholding
    img_th = vision.apply_in_range_threshold(img_bl, config.annotation_scissor_gray_level, config.annotation_embryo_gray_level_1)
    if config.annotation_flag_save_image:
        vision.save_image(img_th, str(config.annotation_embryo_counter)+'_th', config.annotation_embryo_directory)
    # seprating embryo from the background
    labels, areas = vision.find_connected_components(img_th)
    if len(areas) == 0:
        return None, None, False, config.annotation_err_no_areas
    elif np.max(areas) < config.annotation_area_value_min:
        return None, None, False, config.annotation_err_no_areas
    area_max_idx = np.argmax(areas)
    img_desired = np.zeros(labels.shape, dtype=np.uint8)
    img_desired[labels == area_max_idx + 1] = config.annotation_white_level
    if config.annotation_flag_save_image:
        vision.save_image(img_desired, str(config.annotation_embryo_counter)+'_ex', config.annotation_embryo_directory)
    return img_desired, img_bl, True, None


def extract_scissor_from_image(img, config):
    img_temp = img.copy()
    # blurring
    img_bl = vision.apply_blurring(img_temp, config.annotation_blurring_kernel_size, config.annotation_blurring_sigma_x)
    if config.annotation_flag_save_image:
        vision.save_image(img_bl, str(config.annotation_scissor_counter)+'_bl', config.annotation_scissor_directory)
    # thresholding
    img_th = vision.apply_in_range_threshold(img_bl, 0, config.annotation_scissor_gray_level)
    if config.annotation_flag_save_image:
        vision.save_image(img_th, str(config.annotation_scissor_counter)+'_th', config.annotation_scissor_directory)
    # seprating scissor from the background
    labels, areas = vision.find_connected_components(img_th)
    if len(areas) == 0:
        return None, None, False, config.annotation_err_no_areas
    elif np.max(areas) < config.annotation_area_value_min:
        return None, None, False, config.annotation_err_no_areas
    area_max_idx = np.argmax(areas)
    img_desired = np.zeros(labels.shape, dtype=np.uint8)
    img_desired[labels == area_max_idx + 1] = config.annotation_white_level
    if config.annotation_flag_save_image:
        vision.save_image(img_desired, str(config.annotation_scissor_counter)+'_ex', config.annotation_scissor_directory)
    return img_desired, img_bl, True, None


def annotate_embryo(config, model):
    # taking the current image of the camera
    img_cam = normalize_image(config.camera_image)
    vision.save_image(img_cam, str(config.annotation_embryo_counter), config.annotation_embryo_directory)
    # extracting embryo from the image
    img_th, img_bl, flag, err = extract_embryo_from_image(img_cam, config)
    if flag == False:
        return flag, err
    if config.annotation_embryo_flag_cv_dn:     # deep network
        # processing the image to be fed to the deep network
        img_th_cr, img_cr, x_cropped, y_cropped = vision.crop_image(img_th, img_cam, config.annotation_embryo_crop_offset)
        h_emb, w_emb = img_cr.shape
        img_rs = vision.resize_image_by_size(img_cr, config.dn_image_size, config.dn_image_size)
        img_in_arr = np.zeros((1, config.dn_image_size, config.dn_image_size, 1), dtype=np.float32)
        img_in_arr[0, :, :, 0] = np.float32(img_rs) / config.dn_white_level
        img_out_arr = model.predict(img_in_arr, verbose=0)
        # processing the output of the deep network
        img_out = img_out_arr[0, :, :, 0]
        img_out_rs = vision.resize_image_by_size(img_out, w_emb, h_emb)
        if config.annotation_flag_save_image:
            vision.save_image(img_out_rs*config.dn_white_level, str(config.annotation_embryo_counter)+'_dn_out', config.annotation_embryo_directory)
        img_out_th = np.zeros(img_out_rs.shape)
        img_out_th[img_out_rs > config.dn_threshold] = config.dn_white_level_normalized
        if config.annotation_flag_save_image:
            vision.save_image(img_out_th*config.dn_white_level, str(config.annotation_embryo_counter)+'_dn_th', config.annotation_embryo_directory)
        # computing the annotation coordinates
        ids = np.argwhere(img_out_th == config.dn_white_level_normalized)
        if ids.size == 0:
            return False, config.dn_err_empty
        top = ids[:, 0].min()
        bottom = ids[:, 0].max()
        y_arr = np.arange(bottom, top, -int(config.dn_somite_height_px))
        x_arr = np.zeros(y_arr.shape, dtype=int)
        for i in range(len(y_arr)):
            y = y_arr[i]
            id_closest = np.abs(ids[:, 0] - y).argmin()
            y_closest = ids[id_closest, 0]
            x_arr[i] = int(np.mean(ids[ids[:, 0]==y_closest][:, 1]))
        if config.annotation_flag_save_image:
            temp_points = [(int(x), int(y), (0, 0, 255)) for x, y in zip(x_arr, y_arr)]
            img_drawn = vision.draw_points(np.float32(img_out_th*config.dn_white_level), temp_points, config.annotation_point_offset)
            vision.save_image(img_drawn, str(config.annotation_embryo_counter)+'_dn_th_ann', config.annotation_embryo_directory)
        # converting the coordinates to match the dimensions of the full image
        x_arr = x_arr + x_cropped
        y_arr = y_arr + y_cropped
        # processing the annotation points
        config.annotation_embryo_points = [(int(x), int(y), (0, 0, 255)) for x, y in zip(x_arr, y_arr)]   
        # # config.annotation_points = list(set(config.annotation_embryo_points).union(set(config.annotation_points)))  
        config.annotation_points = config.annotation_points + config.annotation_embryo_points
        # saving the annotated image with the points drawn on it
        img_drawn = vision.draw_points(np.float32(img_cam), config.annotation_embryo_points, config.annotation_point_offset)
        vision.save_image(img_drawn, str(config.annotation_embryo_counter)+'_dn_ann', config.annotation_embryo_directory)
        return True, None
    else:   	# computer vision
        # cropping
        img_th_cr, img_bl_cr, x_cropped, y_cropped = vision.crop_image(img_th, img_bl, config.annotation_embryo_crop_offset)
        h_full, w_full = img_th_cr.shape
        if config.annotation_flag_save_image:
            vision.save_image(img_th_cr, str(config.annotation_embryo_counter)+'_th_cr', config.annotation_embryo_directory)
            vision.save_image(img_bl_cr, str(config.annotation_embryo_counter)+'_bl_cr', config.annotation_embryo_directory)
        # filling
        img_fl = vision.fill_image(img_th_cr, config.annotation_embryo_fill_offset, config.annotation_white_level)
        if config.annotation_flag_save_image:
            vision.save_image(img_fl, str(config.annotation_embryo_counter)+'_fl', config.annotation_embryo_directory)
        # closing
        img_cl = vision.apply_closing(img_fl, config.annotation_closing_kernel_size, config.annotation_closing_iterations)
        if config.annotation_flag_save_image:
            vision.save_image(img_cl, str(config.annotation_embryo_counter)+'_cl', config.annotation_embryo_directory)
        # calculating the centroid of the full embryo
        x_full_centroid, y_full_centroid = vision.calculate_centroid(img_cl)
        if (x_full_centroid, y_full_centroid) == (None, None):
            return False, config.annotation_err_no_centroid
        # detecting the edges
        img_ed = vision.detect_edges(img_cl, config.annotation_edge_level_1, config.annotation_edge_level_2, config.annotation_edge_aperture_size, config.annotation_edge_l2_gradient)
        if config.annotation_flag_save_image:
            vision.save_image(img_ed, str(config.annotation_embryo_counter)+'_ed', config.annotation_embryo_directory)
        # detecting the circles
        img_crc, x_circle, y_circle = vision.detect_circles(img_ed, config.annotation_embryo_circle_dp,
                                                            config.annotation_embryo_circle_param_1, config.annotation_embryo_circle_param_2, offset=config.annotation_point_offset)
        if (x_circle, y_circle) == (None, None):
            return False, config.annotation_embryo_err_no_circle
        if config.annotation_flag_save_image:
            vision.save_image(img_crc, str(config.annotation_embryo_counter)+'_crc', config.annotation_embryo_directory)
        # cropping the middle part of the image
        img_mid = img_bl_cr[:, x_circle-config.annotation_embryo_crop_middle_offset:x_circle+config.annotation_embryo_crop_middle_offset]
        if config.annotation_flag_save_image:
            vision.save_image(img_mid, str(config.annotation_embryo_counter)+'_mid', config.annotation_embryo_directory)
        h_mid, w_mid = img_mid.shape
        # thresholding
        img_mid_th = vision.apply_in_range_threshold(img_mid, 0, config.annotation_embryo_gray_level_2)
        if config.annotation_flag_save_image:
            vision.save_image(img_mid_th, str(config.annotation_embryo_counter)+'_mid_th', config.annotation_embryo_directory)
        # processing the lower half of the image 
        img_low = img_mid_th[h_mid//2:, :]
        if config.annotation_flag_save_image:
            vision.save_image(img_low, str(config.annotation_embryo_counter)+'_low', config.annotation_embryo_directory)
        img_low_op = vision.apply_opening(img_low, config.annotation_embryo_openning_kernel_size, config.annotation_embryo_openning_iterations)
        if config.annotation_flag_save_image:
            vision.save_image(img_low_op, str(config.annotation_embryo_counter)+'_low_op', config.annotation_embryo_directory)
        x_low_centroid, y_low_centroid = vision.calculate_centroid(img_low_op)
        if (x_low_centroid, y_low_centroid) == (None, None):
            return False, config.annotation_err_no_centroid
        x_low_centroid = x_low_centroid + x_circle - config.annotation_embryo_crop_middle_offset
        y_low_centroid = y_low_centroid + h_mid//2
        # processing the upper half of the image
        img_up = img_cl[:h_mid//3, :]
        if config.annotation_flag_save_image:
            vision.save_image(img_up, str(config.annotation_embryo_counter)+'_up', config.annotation_embryo_directory)
        img_up_op = vision.apply_opening(img_up, config.annotation_embryo_openning_kernel_size, config.annotation_embryo_openning_iterations)
        if config.annotation_flag_save_image:
            vision.save_image(img_up_op, str(config.annotation_embryo_counter)+'_up_op', config.annotation_embryo_directory)
        x_up_centroid, y_up_centroid = vision.calculate_centroid(img_up_op)
        if (x_up_centroid, y_up_centroid) == (None, None):
            return False, config.annotation_err_no_centroid
        # converting the coordinates to match the dimensions of the full image
        x_low_centroid = x_low_centroid + x_cropped
        x_up_centroid = x_up_centroid + x_cropped
        y_low_centroid = y_low_centroid + y_cropped
        y_up_centroid = y_up_centroid + y_cropped
        # processing the annotation points
        config.annotation_embryo_points = [(x_low_centroid, y_low_centroid, (255, 255, 0)), 
                                           (x_up_centroid, y_up_centroid, (0, 255, 0)),
                                           ((x_low_centroid+x_up_centroid)//2, y_low_centroid, (0, 0, 255)), 
                                           (x_low_centroid+config.annotation_embryo_point_offset_x, y_low_centroid+config.annotation_embryo_point_offset_y, (255, 0, 0))
                                          ]
        # # config.annotation_points = list(set(config.annotation_embryo_points).union(set(config.annotation_points)))  
        config.annotation_points = config.annotation_points + config.annotation_embryo_points
        # saving the annotated image with the points drawn on it
        img_drawn = vision.draw_points(np.float32(img_cam), config.annotation_embryo_points, config.annotation_point_offset)
        vision.save_image(img_drawn, str(config.annotation_embryo_counter)+'_ann', config.annotation_embryo_directory)
        return True, None


def annotate_scissor(config):
    # taking the current image of the camera
    img_cam = normalize_image(config.camera_image)
    vision.save_image(img_cam, str(config.annotation_scissor_counter), config.annotation_scissor_directory)
    # extracting scissor from the image
    img_th, img_bl, flag, err = extract_scissor_from_image(img_cam, config)
    if flag == False:
        return flag, err
    # cropping
    img_th_cr, img_bl_cr, x_cropped, y_cropped = vision.crop_image(img_th, img_bl, config.annotation_scissor_crop_offset)
    h_full, w_full = img_th_cr.shape
    if config.annotation_flag_save_image:
        vision.save_image(img_th_cr, str(config.annotation_scissor_counter)+'_th_cr', config.annotation_scissor_directory)
        vision.save_image(img_bl_cr, str(config.annotation_scissor_counter)+'_bl_cr', config.annotation_scissor_directory)
    # closing
    img_cl = vision.apply_closing(img_th_cr, config.annotation_closing_kernel_size, config.annotation_closing_iterations)
    if config.annotation_flag_save_image:
        vision.save_image(img_cl, str(config.annotation_scissor_counter)+'_cl', config.annotation_scissor_directory)
    # calculating the centroid of the full scissor
    x_full_centroid, y_full_centroid = vision.calculate_centroid(img_cl)
    if (x_full_centroid, y_full_centroid) == (None, None):
        return False, config.annotation_err_no_centroid
    # detecting the edges
    img_ed = vision.detect_edges(img_cl, config.annotation_edge_level_1, config.annotation_edge_level_2, config.annotation_edge_aperture_size, config.annotation_edge_l2_gradient)
    if config.annotation_flag_save_image:
        vision.save_image(img_ed, str(config.annotation_scissor_counter)+'_ed', config.annotation_scissor_directory)
    # dividing the scissor into two parts (left and right)
    img_left = img_ed[:, :x_full_centroid]
    img_right = img_ed[:, x_full_centroid:]
    # detecting lines in the left part
    img_left_ann, points_left = vision.detect_lines(img_left, config.annotation_scissor_line_rho, config.annotation_scissor_line_theta,
                                                    config.annotation_scissor_diagonal_line_vote, config.annotation_scissor_diagonal_line_length_min,
                                                    config.annotation_scissor_diagonal_line_gap_max, config.annotation_scissor_diagonal_line_slope_min,
                                                    config.annotation_scissor_diagonal_line_slope_max)
    if points_left == None:
        return False, config.annotation_scissor_err_no_line
    if config.annotation_flag_save_image:
        vision.save_image(img_left_ann, str(config.annotation_scissor_counter)+'_left_ann', config.annotation_scissor_directory)
    # detecting lines in the right part
    img_right_ann, points_right = vision.detect_lines(img_right, config.annotation_scissor_line_rho, config.annotation_scissor_line_theta,
                                                      config.annotation_scissor_diagonal_line_vote, config.annotation_scissor_diagonal_line_length_min,   
                                                      config.annotation_scissor_diagonal_line_gap_max, config.annotation_scissor_diagonal_line_slope_min,
                                                      config.annotation_scissor_diagonal_line_slope_max)
    if points_right == None:
        return False, config.annotation_scissor_err_no_line
    if config.annotation_flag_save_image:
        vision.save_image(img_right_ann, str(config.annotation_scissor_counter)+'_right_ann', config.annotation_scissor_directory)
    # converting the coordinates to match the dimensions of the full image
    x1 = points_left[0] + config.annotation_scissor_diagonal_line_offset + x_cropped
    x2 = points_left[2] + config.annotation_scissor_diagonal_line_offset + x_cropped
    y1 = points_left[1] + y_cropped
    y2 = points_left[3] + y_cropped
    x3 = points_right[0] - config.annotation_scissor_diagonal_line_offset + x_full_centroid + x_cropped
    x4 = points_right[2] - config.annotation_scissor_diagonal_line_offset + x_full_centroid + x_cropped
    y3 = points_right[1] + y_cropped
    y4 = points_right[3] + y_cropped
    # calculating the intersection point
    x_intersection = int(((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)))
    y_intersection = int(((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)))
    if x_intersection < 0 or x_intersection > img_th.shape[1] or y_intersection < 0 or y_intersection > img_th.shape[0]:
        return False, config.annotation_scissor_err_no_intersection
    # processing the annotation points
    config.annotation_scissor_points = [(x_intersection, y_intersection, (0, 255, 255))]
    # # config.annotation_points = list(set(config.annotation_scissor_points).union(set(config.annotation_points)))
    config.annotation_points = config.annotation_points + config.annotation_scissor_points
    # saving the annotated image with the points drawn on it
    img_drawn = vision.draw_points(np.float32(img_cam), config.annotation_scissor_points, config.annotation_point_offset)
    vision.save_image(img_drawn, str(config.annotation_scissor_counter)+'_ann', config.annotation_scissor_directory)
    return True, None


def stop(smaract, pistage, asm, config):
    smaract.stop_channel(config.smaract_channel_x)
    smaract.stop_channel(config.smaract_channel_y)	
    smaract.stop_channel(config.smaract_channel_z)
    smaract.stop_channel(config.smaract_channel_alpha)
    smaract.stop_channel(config.smaract_channel_beta)
    smaract.stop_channel(config.smaract_channel_gamma)
    smaract.close()
    pistage.stop()
    asm.close()
