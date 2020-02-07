
import xlwt
from time import sleep
from legodetector import LegoDetector

def main():
    camIndex = 0
    resolution = (1280, 720)  #ASSUMING PI CAM V2
    xl = "colors.xlsx"

    detector = LegoDetector(camIndex, resolution, xl)
    sleep(2)

    frame = detector.snap()
    """
    for None: #TODO: iterate through all colors in the excel file and run the detection pipeline
        detector.pipeline(frame, None)
        sleep(0.5)
    """
    detector.processBricks()
    frame = detector.drawContours(frame)
    detector.showContours(frame)
