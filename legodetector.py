
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
        self.colorpx = ()

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
        res = cv2.bitwise_and(frame, frame, mask=mask)

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

                    self.bricks.append([brickID, centerpoint, approx])
                    self.brick_contours.append(approx)

    def getMouseCoords(event, x, y, flags, param):
        """
        Detect a mouse click when corner points of a new brick are being marked, then add these points to an array

        Parameters:
            event (cv2 event): Event type,
            x (int): X coordinate,
            y (int): Y coordinate,
            flags: Flags,
            param: Extra parameters
        """
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.identify.append((x, y))

    def getColorFromCoords(event, x, y, flags, param):
        """
        Detect a mouse click when the color of a new brick is being determined, then store this point into a tuple

        Parameters:
            event (cv2 event): Event type,
            x (int): X coordinate,
            y (int): Y coordinate,
            flags: Flags,
            param: Extra parameters
        """
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.colorpx = (x, y)

    def identification_pipeline(self, frame):
        """
        Run the image identification pipeline to catalogue new a brick

        Parameters:
            frame (image): Input image frame
        """
        # Create a new image window and assign the getMouseCoords mouse detector to it
        cv2.namedWindow('frame')
        cv2.setMouseCallback('frame', getMouseCoords)

        """
        Show the frame and allow the user to mark all corners of a brick:
            1. Go from one corner to the next adjacent corner
            2. Stop at the last corner before the first corner that was marked (DO NOT INCLUDE THE FIRST CORNER TWICE!)
            3. Press escape to exit
        """
        while True:
            cv2.imshow('frame', frame)
            if cv2.waitKey(20) & 0xFF == 27:
                break
        cv2.destroyAllWindows()

        inp = str(input('Would you like to save these coordinates? y/n'))
        if inp == 'y':
            # Convert corner points of brick to a contour and draw it to the frame
            cnt = np.array(self.identify).reshape((-1, 1, 2)).astype(np.int32)
            cv2.drawContours(frame, [cnt], 0, (0, 0, 0), 2)

            # Create a new image window and assign the getColorFromCoords mouse detector to it
            cv2.namedWindow('frame2')
            cv2.setMouseCallback('frame2', getColorFromCoords)
            print("Click a single point inside the brick to get color info")

            """
            Show the frame and allow the user to mark a single point inside the brick to determine color:
                1. Only click one point inside the brick
                2. Press escape to exit
            """
            while True:
                cv2.imshow('frame2', frame)
                if cv2.waitKey(20) & 0xFF == 27:
                    break
            cv2.destroyAllWindows()

            inp = str(input('Would you like to save this point? y/n'))
            if inp == 'y':
                # Get BGR color values of the selected pixel and convert to HSV
                b, g, r = frame[self.colorpx]
                color = np.uint8([[[b, g, r]]])
                color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

                """
                Determine all parameters of the brick:
                    1. brickID (int): Brick ID <- In the spreadsheet the brick ID's starts from 0, but self.sheet.nrows counts the number of rows which is brickID + 1,
                    2. lower (int[]): Lower HSV range value,
                    3. upper (int[]): Upper HSV range value,
                    4. area (int): Area of the brick,
                    5. perimeter (int): Perimeter of the brick
                """
                brickID = self.sheet.nrows
                lower = [color[0][0][0] - 10, color[0][0][1], color[0][0][2]]
                upper = [color[0][0][0] + 10, color[0][0][1], color[0][0][2]]
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt,True)

                # TODO: Figure out if this is the right way to write to the sheet (using xlrd-loaded sheet instead of xlwt?)
                # Write the new brick parameters into a new row in the spreadsheet
                self.sheet.write(brickID, 0, brickID)
                self.sheet.write(brickID, 1, lower)
                self.sheet.write(brickID, 2, upper)
                self.sheet.write(brickID, 3, area)
                self.sheet.write(brickID, 4, perimeter)

            else:
                self.colorpx = ()
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
