import cv2
import numpy as np

# Import frame from source and resize
frame = cv2.imread('test2.jpg')
frame = cv2.resize(frame, (500, 500))

# Apply HSV filter for Green Bricks
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
lower_green = np.array([50, 70, 30])
upper_green = np.array([100, 255, 210])
mask = cv2.inRange(hsv, lower_green, upper_green)
res = cv2.bitwise_and(frame,frame, mask= mask)
# cv2.imshow('mask',mask)
# cv2.imshow('res',res)

# Apply Gaussian Blur with 5x5 kernel
blur = cv2.GaussianBlur(res, (5, 5), 0)
blur_grey = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
# cv2.imshow('blur_grey', blur_grey)

# Apply Sobel Operator
sobel_x = cv2.Sobel(blur_grey, cv2.CV_64F, 1, 0, ksize=5)
sobel_y = cv2.Sobel(blur_grey, cv2.CV_64F, 0, 1, ksize=5)
sobel_x_abs = cv2.convertScaleAbs(sobel_x)
sobel_y_abs = cv2.convertScaleAbs(sobel_y)
sobel = cv2.addWeighted(sobel_x_abs, 0.5, sobel_y_abs, 0.5, 0)
# cv2.imshow('sobel', sobel)

# Apply Canny Edge Detection
edges = cv2.Canny(sobel, 225, 300)
# cv2.imshow('canny', edges)

# Find contours
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

bricks = []
for contour in contours:
    if cv2.contourArea(contour) >= 10:
        perimeter = cv2.arcLength(contour, True)
        epsilon = 0.04 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        bricks.append(approx)

bricks = np.array(bricks)
cv2.drawContours(frame, bricks, -1, (0, 0, 0), 2)
print(bricks)
print("Number of Bricks Detected: " + str(len(bricks)))

cv2.imshow('Frame', frame)
cv2.waitKey(0)
'''
# Find and store brick coordinates and store in an array
i=0
bricks = []
for contour in contours:
    if cv2.contourArea(contour) >= 10:
        rect = cv2.minAreaRect(contour)
        bricks.append(rect)
        rect = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(frame, [rect], 0, (0,0,0), 2)
        i+=1
print(bricks)

'''