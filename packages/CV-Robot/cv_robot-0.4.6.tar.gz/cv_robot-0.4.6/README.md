# Computer Vision Robot

![Python Version Badge](https://img.shields.io/pypi/pyversions/CV_Robot)
![License Badge](https://img.shields.io/github/license/RobertJN64/CV_Robot)

Library for computer vision code in Google Colab and Raspberry Pi.
Uses Yolo v3 with OpenCV.

## Config:

Place the following files in the same directory as your script to configure.
 - CONFIG_CV_SERVER.py - runs in server mode
 - CONFIG_CV_ROBOT.py - runs in server mode on robot
 - CONFIG_CV_LIVE_IMG.py - replaces server preview with matplotlib window

By default, the code will not use cameras (great for Google Colab!)

## Example:
```python
#Imports
from CV_Robot import robot
from CV_Robot import vision
from time import sleep

#Example - find objects in an image
img = vision.load_image("sample_images/sample_005.png")
vision.show_image(img)
vision.show_objects(img, pause=True)
print(vision.find_objects(img))

#Example - drive forward until a STOP_SIGN is found
robot.forward()
vision.activate_camera()
while True:
    img = vision.get_camera_image()
    if img is None: #This is good practice - it will stop the loop if the video ends / the camera fails
        break
    vision.show_objects(img)
    if vision.Objects.STOP_SIGN in vision.find_objects(img):
        break
    sleep(0.1)
robot.stop()
```

## Data Sources
https://github.com/nandinib1999/object-detection-yolo-opencv

```commandline
#Download some sample videos + images for testing
wget https://github.com/nandinib1999/object-detection-yolo-opencv/raw/master/videos/pedestrians.mp4
wget https://github.com/nandinib1999/object-detection-yolo-opencv/raw/master/videos/car_on_road.mp4
wget -O sample_images.zip https://github.com/RobertJN64/CV_Robot/raw/master/Examples/Samples/100samples.zip
unzip sample_images.zip -d sample_images
```