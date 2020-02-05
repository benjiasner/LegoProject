
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

    def __init__(self, camera, res):
        """
        The constructor for the LegoDetector Class

        Parameters:
            camera (int): camera port
            res (tuple): camera resolution
        """
        
        self.camera = PiCamera(camera)
        self.camera.resolution = (res)
        self.camera.start_preview()
        self.rawCapture = PiRGBArray(self.camera, size=res)
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

    def pipeline(self, frame):
        """
        Run the image processing pipeline to detect bricks

        Parameters:
            frame (image): Input image frame 
        """

        
