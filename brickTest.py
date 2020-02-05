# TODO: Figure out why angles are weird
import cv2
import math
import numpy as np

# Import frame from source and resize
frame = cv2.imread('test.jpg')
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

# Find coordinates, center points of bricks
# vertices is used only for drawing the outline of the bricks on a GUI
bricks = []
vertices = []
cPts = []
for contour in contours:
    if cv2.contourArea(contour) >= 10:
        perimeter = cv2.arcLength(contour, True)
        epsilon = 0.04 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        x0, y0, w, h = cv2.boundingRect(contour)
        centerpoint = (int(x0 + w/2), int(y0 + h/2))

        bricks.append ([approx, centerpoint, perimeter])
        vertices.append(approx)

cv2.drawContours(frame, vertices, -1, (0, 0, 0), 2)

bricks = np.array(bricks)

print(bricks)
print("Number of Bricks Detected: " + str(len(bricks)))

cv2.imshow('Frame', frame)
cv2.waitKey(0)
