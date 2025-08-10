import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

lane_img = cv.imread("road.png")
copy_img = np.copy(lane_img)

def canny(image):
    gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    blur = cv.GaussianBlur(gray, (5,5), 0)
    canny = cv.Canny(blur, 100, 200)
    return canny

def region_of_interest(image):
    height = image.shape[0]
    width = image.shape[1]
    polygon = np.array([[(250,height), (1750, height), (1160, 475)]])
    mask = np.zeros_like(image)
    cv.fillPoly(mask, polygon, 255)
    masked_image = cv.bitwise_and(mask, image)
    return masked_image

def draw_lines(image, lines):
    line_img = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv.line(line_img, (x1, y1), (x2, y2), (255,0 , 0), 10)
    return line_img

def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1* 0.5)
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])

def average_slope_intercept(image, lines):
    right_fit = []
    left_fit = []
    
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]
        if slope < -0.5:
            left_fit.append((slope, intercept))
        elif slope > 0.5:
            right_fit.append((slope, intercept))
    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0) 
    left_line = make_coordinates(image, left_fit_average)
    right_line = make_coordinates(image, right_fit_average)
    return np.array([left_line, right_line])


""" canny_img = canny(copy_img)
cropped_img = region_of_interest(canny_img)
lane_lines = cv.HoughLinesP(cropped_img, 2, np.pi/180, 50, np.array([]) ,minLineLength= 100, maxLineGap =50)
averaged_lines = average_slope_intercept(copy_img, lane_lines)
line_image = draw_lines(copy_img, averaged_lines)
weighted_img = cv.addWeighted(copy_img, 0.8, line_image, 1, 1)
cv.imshow("Final Overlay", weighted_img)
cv.waitKey(0) """

cap = cv.VideoCapture("test_video.mp4")
while cap.isOpened():
    ret, frame = cap.read()
    canny_img = canny(frame)
    cropped_img = region_of_interest(canny_img)
    lane_lines = cv.HoughLinesP(cropped_img, 2, np.pi/180, 50, np.array([]) ,minLineLength= 100, maxLineGap =50)
    averaged_lines = average_slope_intercept(frame, lane_lines)
    line_image = draw_lines(frame, averaged_lines)
    weighted_img = cv.addWeighted(frame, 0.8, line_image, 1, 1)
    cv.imshow("Resultant Image", weighted_img)
    if cv.waitKey(1) & 0xFF == ord('\x1b'):  # Break on 'ESC' key
        break

cap.release()
cv.destroyAllWindows()
    