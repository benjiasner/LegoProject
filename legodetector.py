
import cv2
import numpy as np
import xlrd
import xlwt
from time import sleep
from picamera import PiCamera
from picamera.array import PiRGBArray

class LegoDetector:
    """
    This is a class for detecting legos using a Raspberry Pi Camera
    """

    def __init__(self, camera, reso, xlpath):
        """
        The constructor for the LegoDetector Class

        Parameters:
            camera (int): camera port,
            reso (tuple): camera resolution,
            xlpath (string): file path to colors Excel file
        """

        book = xlrd.open_workbook(str(xlpath), encoding_override="cp1252")
        self.sheet = book.sheet_by_index(0)

        self.bricks = []
        self.brick_contours = []

        self.identify = []

        self.camera = PiCamera(camera)
        self.camera.resolution = (reso)
        self.camera.start_preview()
        self.rawCapture = PiRGBArray(self.camera, size=reso)
        sleep(2)
        print("Camera initialized")

    def snap(self):
        """
        Capture a still image

        Returns:
            image: A file with all the image data
        """

        self.rawCapture.truncate(0)
        self.camera.capture(self.rawCapture, format="bgr")
        image = self.rawCapture.array
        return image

    def detection_pipeline(self, frame, brickID):
        """
        Run the image processing pipeline to detect bricks

        Parameters:
            frame (image): Input image frame,
            color (int): Color index as shown by the Excel file
        """

        # HSV Processing
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array(self.sheet.cell(brickID, 1))
        upper_green = np.array(self.sheet.cell(brickID, 2))
        mask = cv2.inRange(hsv, lower_green, upper_green)
        res = cv2.bitwise_and(frame,frame, mask=mask)

        # Gaussian Blur
        blur = cv2.GaussianBlur(res, (5, 5), 0)
        blur_grey = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

        # Sobel Operator
        sobel_x = cv2.Sobel(blur_grey, cv2.CV_64F, 1, 0, ksize=5)
        sobel_y = cv2.Sobel(blur_grey, cv2.CV_64F, 0, 1, ksize=5)
        sobel_x_abs = cv2.convertScaleAbs(sobel_x)
        sobel_y_abs = cv2.convertScaleAbs(sobel_y)
        sobel = cv2.addWeighted(sobel_x_abs, 0.5, sobel_y_abs, 0.5, 0)

        # Canny Edge Detection and Contour Detection
        edges = cv2.Canny(sobel, 225, 300)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Storing Contour Information if a Brick Matching the Properties of a Brick of 'brickID' is Found
        for contour in contours:
            if abs(self.sheet.cell(brickID, 3) - cv2.contourArea(contour)) <= 15:
                perimeter = cv2.arcLength(contour, True)
                if abs(self.sheet.cell(brickID, 4) - perimeter) <= 15:
                    epsilon = 0.04 * perimeter
                    approx = cv2.approxPolyDP(contour, epsilon, True)

                    x0, y0, w, h = cv2.boundingRect(contour)
                    centerpoint = (int(x0 + w/2), int(y0 + h/2))

                    self.bricks.append ([brickID, centerpoint, approx])
                    self.brick_contours.append(approx)

    def getMouseCoords(event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.identify.append((x, y))

    def identification_pipeline(self, frame):
        cv2.namedWindow('frame')
        cv2.setMouseCallback('frame',getMouseCoords)

        while True:
            cv2.imshow('frame',frame)
            if cv2.waitKey(20) & 0xFF == 27:
                break
        cv2.destroyAllWindows()

        inp = str(input('Would you like to save these coordinates? y/n'))
        if inp == 'y':
            pts = np.array(self.identify, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, (255, 255, 255))
            # TODO: Make this an ROI, get HSV, perimeter, and area of brick
            # TODO: Export information to spreadsheet
        else:
            self.identify = []

    def processBricks(self):
        """
        Once desired colors are tested, convert bricks and brick_contours into numpy arrays
        """

        self.bricks = np.array(self.bricks)
        self.brick_contours = np.array(self.brick_contours)
        return self.bricks

    def drawContours(self, frame):
        """
        Draw contours onto a frame

        Parameters:
            frame (image): Input image frame

        Returns:
            frame (image): Image frame with drawn contours
        """

        frame = cv2.drawContours(frame, self.brick_contours, -1, (0, 0, 0), 2)
        return frame

    def showContours(self, frame):
        """
        Displays desired frame on a GUI
        """

        cv2.imshow('Frame', frame)
        print("Number of Bricks: " + str(len(self.bricks)))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
