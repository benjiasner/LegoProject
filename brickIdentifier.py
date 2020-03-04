from time import sleep
from legodetector import LegoDetector


def main():
    camIndex = 0
    resolution = (1280, 720)  # ASSUMING PI CAM V2
    xl = "colors.xlsx"

    detector = LegoDetector(camIndex, resolution, xl)
    sleep(2)

    frame = detector.snap()
    detector.identification_pipeline(frame)


if __name__ == '__main__':
    main()
