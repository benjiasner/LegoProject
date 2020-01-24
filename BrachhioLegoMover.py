#    need a getstate which outputs the original state
#   define an array
#    include inputs
#functions write new serials out and update python states, the originals are contained
#motor 1 up 1 degrees
# if correct write serial out and update the states
#declare integers for the 6 motors:
#sends instructions to the serial port to move

# corresponds to L and base counterclockwise

    #increment the getState array of motors by 1 degree
    # array.getState() =+ or something
import os
import serial
import time

class BrachhioLegoMover:
    ser = serial.Serial('/dev/tty.usbserial-14310' ,9600)
    def getState():
        global initDegBase = 90 # degrees
        global initDegShoulder = 45
        global initDegElbow = 180
        global initDegWristVertical = 180
        global initDegWristRotate = 90
        global initDegGripper = 10

# corresponds to A and shoulder down
    def degree_shoulder_up():
        getState()
        ser.write(bytes("A", encoding='utf-8'))
        initDegShoulder += 1

    def degree_shoulder_down():
        getState()
        ser.write(bytes("B", encoding='utf-8'))
        initDegShoulder -= 1

    def degree_elbow_up():
        getState()
        ser.write(bytes("C", encoding='utf-8'))
        initDegElbow += 1

    def degree_elbow_down():
        getState()
        ser.write(bytes("D", encoding='utf-8'))
        initDegElbow -= 1

    def degree_wrist_up():
        getState()
        ser.write(bytes("E", encoding='utf-8'))
        initDegWristVertical += 1

    def degree_wrist_down():
        getState()
        ser.write(bytes("F", encoding='utf-8'))
        initDegWristVertical -= 1

    def degree_wrist_clockwise():
        getState()
        ser.write(bytes("G", encoding='utf-8'))
        initDegWristRotate += 1

    def degree_wrist_counterclockwise():
        getState()
        ser.write(bytes("H", encoding='utf-8'))
        initDegWristRotate -= 1

    def degree_gripper_open():
        getState()
        ser.write(bytes("I", encoding='utf-8'))
        initDegGripper += 1

    def degree_gripper_closed():
        getState()
        ser.write(bytes("J", encoding='utf-8'))
        initDegGripper -= 1

    def degree_base_clockwise():
        getState()
        ser.write(bytes("K", encoding='utf-8'))
        initDegBase += 1

    def degree_base_counterclock():
        getState()
        ser.write(bytes("L", encoding='utf-8'))
        initDegBase -= 1

#message input into terminal that is parsed into utf-8 and sent to arduino
    def moveBracchio(message): #not sure if you need this argument, but probably
        message = input("What Command? \n ")
    #taking in commands, using functions
        if (message == "shoulder up"):
            degree_shoulder_up()
        if (message == "shoulder down"):
            degree_shoulder_down()
        if (message == "elbow down"):
            degree_elbow_up()
        if (message == "wrist up"):
            degree_wrist_up()
        if (message == "wrist down"):
            degree_wrist_down()
        if (message == "wrist clockwise"):
            degree_wrist_clockwise()
        if (message == "wrist counterclockwise"):
            degree_wrist_counterclockwise()
        if (message == "gripper open"):
            degree_gripper_open()
        if (message == "gripper closed"):
            degree_gripper_closed()
        if (message == "base clockwise"):
            degree_base_clockwise()
        if (message == "base counterclockwise"):
            degree_base_counterclock()
