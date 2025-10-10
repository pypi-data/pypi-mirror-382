import CV_Robot.opencv_api as cv_api
from typing import List
import numpy as np
import requests
import base64
import cv2

from CV_Robot import is_Robot, robot_URL, is_Server

net, classes, output_layers = cv_api.load_model()
camera = cv2.VideoCapture()
camera_active = False
is_video = False

class Objects:
    STOP_SIGN = 'STOP_SIGN'
    BIKE = 'BIKE'
    CAR = 'CAR'
    TRAFFIC_LIGHT = "TRAFFIC_LIGHT"
    FIRE_HYDRANT = "FIRE_HYDRANT"
    PERSON = "PERSON"
    TRUCK = "TRUCK"

    map = {"stop sign": STOP_SIGN,
         "bicycle": BIKE,
         "car": CAR,
         "traffic light": TRAFFIC_LIGHT,
         "fire hydrant": FIRE_HYDRANT,
         "person": PERSON,
         "truck": TRUCK}

class VisionObject:
    """
    VisionObject - holds information about a recognized object in an image
    All dimensions are normalized to 100 by 100

    Name: Object - type of object
    Size: float - in square pixels
    BBox: list[float] - x, y, width, height
    X: float - center x
    Y: float - center y
    """
    def __init__(self, box: List[float], conf: float, class_id: int):
        self.Name: Objects = Objects.map[classes[class_id]]
        self.Size: float = round(box[2] * box[3], 3)
        self.BBox = box #x, y, width, height
        self.Conf = round(conf, 3)
        self.X: float = box[0] + box[2] / 2
        self.Y: float = box[1] + box[3] / 2

        self._class_id: int = class_id
        self._class: str = classes[self._class_id]

    def __repr__(self):
        return f"VisionObject<{self.Name}> at ({int(round(self.X))}, {int(round(self.Y))})"

def activate_camera():
    """
    Activates the robot camera
    """
    global camera
    global camera_active
    global is_video
    if not is_Robot:
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera_active = True
    is_video = False

def get_camera_image(skip_frames = 5):
    """
    Retrieves current image from robot camera or video
    Returns none if the video is done or camera failed
    :param skip_frames: If playing a video, skip ahead this many frames at a time
    """
    global camera
    global camera_active
    if not camera_active:
        raise Exception("Camera is not active. Call vision.activate_camera() or vision.load_video()")
    if is_video:
        for i in range(0, skip_frames):
            camera.read()

    if is_Robot:
        #return np.array(json.loads(requests.get('http://' + robot_URL + '/get_camera_array').text)).astype(np.uint8)
        jpg_original = base64.b64decode(requests.get('http://' + robot_URL + '/get_camera_array_fast').text)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        image_buffer = cv2.imdecode(jpg_as_np, flags=1)
        return image_buffer

    _, img = camera.read()
    return img


def load_image(img_path):
    """
    Loads an image file
    :param img_path: File path to image
    """
    # image loading
    with open(img_path):
        pass #Make sure image exists
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    return img

def load_video(video_path):
    """
    Loads a video file to emulate camera
    :param video_path: File path to video
    """
    global camera
    global camera_active
    global is_video
    with open(video_path):
        pass #Make sure video exists
    camera = cv2.VideoCapture(video_path)
    camera_active = True
    is_video = True

def get_object_locations(image: cv_api.img_typ, thresh: float = 0.3):
    """
    Returns a list of VisionObjects which can be used to find object location and size
    :param image: Image object (from load_image)
    :param thresh: Threshold to identify object, default is 30% (0.3)
    """
    outputs = cv_api.detect_objects(image, net, output_layers)
    boxes, confs, class_ids = cv_api.get_box_dimensions(outputs, thresh=thresh)
    v_indexes = cv2.dnn.NMSBoxes(boxes, confs, thresh, thresh) #Filter by seperated boxes
    return [VisionObject(*item) for index, item in enumerate(zip(boxes, confs, class_ids))
            if classes[item[2]] in Objects.map.keys() and index in v_indexes]

def show_objects(image: cv_api.img_typ, thresh: float = 0.3, pause: bool = False):
    """
    Displays image with boxes around objects
    :param image: Image object (from load_image)
    :param thresh: Threshold to identify object, default is 30% (0.3)
    :param pause: Set to true to pause after showing image (only applies to local emulation)
    """
    cv_api.draw_labels(get_object_locations(image, thresh=thresh), image, pause=pause)

def find_objects(image: cv_api.img_typ, thresh: float = 0.3):
    """
    Runs machine learning model on image specified, returns list of identified objects
    :param image: Image object (from load_image)
    :param thresh: Threshold to identify object, default is 30% (0.3)
    """
    return list(set(obj.Name for obj in get_object_locations(image, thresh=thresh)))

def show_image(image: cv_api.img_typ, pause: bool = True):
    """
    Displays image
    :param image: Image to display
    :param pause: Set to true to pause after showing image (only applies to local emulation)
    """
    cv_api.show_image(image, pause=pause)

def save_image(image: cv_api.img_typ):
    """
    Saves image to file
    :param image: Image to save
    """
    if is_Robot or is_Server:
        with open('userscripts/s_img.lck', 'w+') as f:
            f.write("lck")
        cv2.imwrite("userscripts/saved_image.png", image)
        with open('userscripts/s_img.lck', 'w+') as f:
            f.write("")
    else:
        cv2.imwrite("saved_image.png", image)