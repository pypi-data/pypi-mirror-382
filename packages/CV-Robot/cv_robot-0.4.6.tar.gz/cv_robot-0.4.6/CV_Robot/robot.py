import requests
from time import sleep

try:
    # noinspection PyShadowingBuiltins
    from printlog import printlog as print
except ImportError:
    pass

from CV_Robot import is_Robot, robot_URL

def forward():
    """
    Moves robot forward at speed set by speed command.

    Runs emulated code if GPIO backend not found.
    """
    print("Driving forward...")
    if is_Robot:
        requests.get('http://' + robot_URL + '/forward')

def forward_straight():
    """
    Moves robot forward at speed set by speed command.
    Uses gyro correction to drive straight

    Runs emulated code if GPIO backend not found.
    """
    print("Driving forward (with gyro correction)...")
    if is_Robot:
        requests.get('http://' + robot_URL + '/forward_gyro')


def backward():
    """
    Moves robot backward at speed set by speed command.

    Runs emulated code if GPIO backend not found.
    """
    print("Driving backward...")
    if is_Robot:
        requests.get('http://' + robot_URL + '/backward')

def left():
    """
    Turns robot left at speed set by speed command.

    Runs emulated code if GPIO backend not found.
    """
    print("Turning left...")
    if is_Robot:
        requests.get('http://' + robot_URL + '/left')

def left_angle(x: int):
    """
    Turns robot left to a specified angle at speed set by speed command.
    Runs emulated code if GPIO backend not found.

    :param x: Angle to turn to (0 to 359)
    """
    print(f"Turning left {x} degrees...")
    if is_Robot:
        requests.get('http://' + robot_URL + '/left_angle?angle=' + str(x))

        while requests.get('http://' + robot_URL + '/done').text != "OK":
            sleep(1)


def right():
    """
    Turns robot right at speed set by speed command.

    Runs emulated code if GPIO backend not found.
    """
    print("Turning right...")
    if is_Robot:
        requests.get('http://' + robot_URL + '/right')


def right_angle(x: int):
    """
    Turns robot right to a specified angle at speed set by speed command.
    Runs emulated code if GPIO backend not found.

    :param x: Angle to turn to (0 to 359)
    """
    print(f"Turning right {x} degrees...")
    if is_Robot:
        requests.get('http://' + robot_URL + '/right_angle?angle=' + str(x))

        while requests.get('http://' + robot_URL + '/done').text != "OK":
            sleep(1)

def stop():
    """
    Sets speed of all motors to 0.

    Runs emulated code if GPIO backend not found.
    """
    print("Stopping robot...")
    if is_Robot:
        requests.get('http://' + robot_URL + '/stop')

def speed(val):
    """
    Sets driving speed to value specified
    """
    if is_Robot:
        requests.get('http://' + robot_URL + '/speed?val=' + str(val))