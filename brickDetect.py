
from time import sleep
from legodetector import LegoDetector

if __name__ == '__main__':
    main()

def main():
    camIndex = 0
    resolution = (1280, 720)  #ASSUMING PI CAM V2
    xl = "colors.xlsx"

    detector = LegoDetector(camIndex, resolution, xl)
    sleep(2)

    frame = detector.snap()

    for brickID in range(0, detector.sheet.nrows):
        detector.detection_pipeline(frame, brickID)
        sleep(0.5)

    bricks = detector.processBricks()
    frame = detector.drawContours(frame)
    detector.showContours(frame)
