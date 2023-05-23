##############################################################################
# File name:    computer_vision.py
# Project:      Robotic Surgery Software
# Part:         Computer vision methods for automatic annotation
# Author:       Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
#               erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
# Version:      22.0
# Description:  This file containts the computer vision methods enabling
#               the automatic annotation of the zebrafish embroys' images.
##############################################################################


# Modules
import cv2 as cv
import numpy as np
import time


def resize_image_by_percentage(img, scale_percent):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    return cv.resize(src=img, dsize=(width, height), interpolation=cv.INTER_LINEAR)


def resize_image_by_size(img, width, height):
    return cv.resize(src=img, dsize=(width, height), interpolation=cv.INTER_LINEAR)


def count_gray_levels(img):
    unique, counts = np.unique(img, return_counts=True)
    return int(np.max(unique))


def crop_image_old(img_test, img_original, offset):
    coords = cv.findNonZero(img_test)
    x, y, w, h = cv.boundingRect(coords)
    return img_test[y-offset:y+h+offset, x-offset:x+w+offset], img_original[y-offset:y+h+offset, x-offset:x+w+offset],\
           x-offset, y-offset


def crop_image(img_test, img_original, offset):
    coords = cv.findNonZero(img_test)
    x, y, w, h = cv.boundingRect(coords)
    h_img, w_img = img_test.shape
    y_lower = y-offset
    y_upper = y+h+offset
    x_lower = x-offset
    x_upper = x+w+offset
    if(y_lower<0):
        y_lower = 0
    if(y_upper>h_img):
        y_upper = h_img
    if(x_lower<0):
        x_lower = 0
    if(x_upper>w_img):
        x_upper = w_img
    return img_test[y_lower:y_upper, x_lower:x_upper], img_original[y_lower:y_upper, x_lower:x_upper],\
           x_lower, y_lower


def crop_image_with_black_offset(img_test, img_original, offset):
    coords = cv.findNonZero(img_test)
    x, y, w, h = cv.boundingRect(coords)
    h_img, w_img = img_test.shape
    y_lower = y-offset
    y_upper = y+h+offset
    x_lower = x-offset
    x_upper = x+w+offset
    img_test_temp = np.copy(img_test)
    img_original_temp = np.copy(img_original)
    if(y_lower<0):
        img_test_temp = np.vstack((np.zeros((abs(y_lower), w_img), dtype=np.uint8), img_test_temp))
        img_original_temp = np.vstack((np.zeros((abs(y_lower), w_img), dtype=np.uint8), img_original_temp))
        y_upper = y_upper + abs(y_lower)
        y_lower = 0
    if(y_upper>h_img):
        img_test_temp = np.vstack((img_test_temp, np.zeros((y_upper-h_img, w_img), dtype=np.uint8)))
        img_original_temp = np.vstack((img_original_temp, np.zeros((y_upper-h_img, w_img), dtype=np.uint8)))
    if(x_lower<0):
        img_test_temp = np.hstack((np.zeros((h_img, abs(x_lower)), dtype=np.uint8), img_test_temp))
        img_original_temp = np.hstack((np.zeros((h_img, abs(x_lower)), dtype=np.uint8), img_original_temp))
        x_upper = x_upper + abs(x_lower)
        x_lower = 0
    if(x_upper>w_img):
        img_test_temp = np.hstack((img_test_temp, np.zeros((h_img, x_upper-w_img), dtype=np.uint8)))
        img_original_temp = np.hstack((img_original_temp, np.zeros((h_img, x_upper-w_img), dtype=np.uint8)))
    return img_test_temp[y_lower:y_upper, x_lower:x_upper], img_original_temp[y_lower:y_upper, x_lower:x_upper],\
           x_lower, y_lower


def crop_image_with_fixed_size(img_test, img_original, size):
    coords = cv.findNonZero(img_test)
    x, y, w, h = cv.boundingRect(coords)
    diff_x = (size-w)//2
    diff_y = (size-h)//2
    y_lower = y-diff_y
    y_upper = y+h+diff_y
    if (y_upper-y_lower) < size:
        y_lower = y_lower+(y_upper-y_lower-size)
    else:
        y_upper = y_upper-(y_upper-y_lower-size)
    x_lower = x-diff_x
    x_upper = x+w+diff_x
    if x_upper-x_lower < size:
        x_lower = x_lower+(x_upper-x_lower-size)
    else:
        x_upper = x_upper-(x_upper-x_lower-size)
    return img_test[y_lower:y_upper, x_lower:x_upper], img_original[y_lower:y_upper, x_lower:x_upper]


def fill_image(img, offset, color):
    img_f = img.copy()
    h, w = img_f.shape
    mask = np.zeros((h+offset, w+offset), np.uint8)
    # flood-filling the image from (0, 0) pixel
    cv.floodFill(image=img_f, mask=mask, seedPoint=(0, 0), newVal=color)
    # inverting the floodfilled image
    img_f_inv = cv.bitwise_not(src=img_f)
    # combining the two images to get the foreground
    return img | img_f_inv


def calculate_centroid(img):
    img_moments = cv.moments(img)
    if img_moments["m00"] == 0:
        return None, None
    centroid_x = int(img_moments["m10"] / img_moments["m00"])
    centroid_y = int(img_moments["m01"] / img_moments["m00"])
    return centroid_x, centroid_y


def detect_circles(img, dp, param1, param2, offset):
    img_temp = cv.cvtColor(img.copy(), cv.COLOR_GRAY2RGB)
    h, w = img_temp.shape[:2]
    circles = cv.HoughCircles(image=img.copy(), method=cv.HOUGH_GRADIENT, dp=dp, minDist=int(0.5*w/2), 
                              param1=param1, param2=param2, minRadius=int(0.9*w/2), maxRadius=int(w/2))
    if circles is not None:
        # converting the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv.circle(img=img_temp, center=(x, y), radius=r, color=(0, 0, 255), thickness=2)
            cv.rectangle(img=img_temp, pt1=(x-offset, y-offset), pt2=(x+offset, y+offset),
                         color=(0, 0, 255), thickness=-1)
        center_x = int(np.mean(circles[:, 0]))
        center_y = int(np.mean(circles[:, 1]))
        return img_temp, center_x, center_y
    else:
        return None, None, None


def detect_lines(img, rho, theta, threshold, min_line_length, max_line_gap, slope_min, slope_max):
    img_temp = cv.cvtColor(img.copy(), cv.COLOR_GRAY2RGB)
    lines = cv.HoughLinesP(image=img.copy(), rho=rho, theta=theta*np.pi/180, threshold=threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)
    points = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if slope_min <= 180*np.arctan2(abs(y2-y1), abs(x2-x1))/np.pi <= slope_max:
                points = [x1, y1, x2, y2]
                cv.line(img=img_temp, pt1=(x1, y1), pt2=(x2, y2), color=(0, 0, 255), thickness=3)
                return img_temp, points
    return None, None


def save_image(img, name, path):
    time_stamp = time.strftime('%Y_%m_%d_%H_%M_%S_', time.localtime())
    cv.imwrite(path + time_stamp + name + '.png', img)


def apply_closing(img, kernel_size, iterations):
    kernel = cv.getStructuringElement(shape=cv.MORPH_ELLIPSE, ksize=(kernel_size, kernel_size))
    return cv.morphologyEx(src=img.copy(), op=cv.MORPH_CLOSE, kernel=kernel, iterations=iterations)


def apply_opening(img, kernel_size, iterations):
    kernel = cv.getStructuringElement(shape=cv.MORPH_ELLIPSE, ksize=(kernel_size, kernel_size))
    return cv.morphologyEx(src=img.copy(), op=cv.MORPH_OPEN, kernel=kernel, iterations=iterations)


def detect_edges(img, threshold_1, threshold_2, aperture_size, l2_gradient=True):
    return cv.Canny(image=img.copy(), threshold1=threshold_1, threshold2=threshold_2, apertureSize=aperture_size, L2gradient=l2_gradient)


def apply_in_range_threshold(img, lower_bound, upper_bound):
    return cv.inRange(src=img.copy(), lowerb=lower_bound, upperb=upper_bound)


def apply_blurring(img, kernel_size, sigma_x):
    return cv.GaussianBlur(src=img.copy(), ksize=(kernel_size, kernel_size), sigmaX=sigma_x)
    

def find_connected_components(img):
    n_labels, labels, stats, centroids = cv.connectedComponentsWithStats(image=img.copy(), connectivity=8, ltype=cv.CV_32S)
    areas = stats[1:, cv.CC_STAT_AREA]
    return labels, areas


def draw_points(img, points, offset):
    img_drawn = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    for point in points:
        cv.rectangle(img=img_drawn, pt1=(point[0]-offset, point[1]-offset), 
                     pt2=(point[0]+offset, point[1]+offset), color=point[2], thickness=-1)  # -1 means that the rectangle will be filled
    return img_drawn
    