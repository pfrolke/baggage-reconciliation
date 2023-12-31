import numpy as np
import itertools

LARGE_MODEL = "models/yolov8l.pt"
NANO_MODEL = "models/yolov8n.pt"
MODEL = LARGE_MODEL
TRACKING_BUFFER = 200
USE_GPU = True
BOX_THICKNESS = 4
YOLO_ALLOWLIST = (24, 26, 28)

DEFAULT_SCREEN_SIZE = (1920, 1080)
BACKGROUND_COLOR = "black"
TEXT_COLOR = "black"
FONT_SIZE = 32
ALLOWED_MISSED_FRAMES = 10
MINIMUM_DETECTED_FRAMES = 20

DISTORTION_FACTOR = 90

BROWN_LOWER = np.array([0, 0, 0])
BROWN_UPPER = np.array([30, 255, 255])
BROWN = list(itertools.product(list(range(BROWN_LOWER[0], BROWN_UPPER[0])), 
                                list(range(BROWN_LOWER[1], BROWN_UPPER[1])), 
                                list(range(BROWN_LOWER[2], BROWN_UPPER[2]))))

YELLOW_LOWER = np.array([31, 100, 100])
YELLOW_UPPER = np.array([60, 255, 255])
YELLOW = list(itertools.product(list(range(YELLOW_LOWER[0], YELLOW_UPPER[0])), 
                                list(range(YELLOW_LOWER[1], YELLOW_UPPER[1])), 
                                list(range(YELLOW_LOWER[2], YELLOW_UPPER[2]))))

SERVER_PORT = 6969
HOST = "http://localhost"

SEGREGATION = {"one": ["PRIO"], "two": ["TRF", "ECO"]}
