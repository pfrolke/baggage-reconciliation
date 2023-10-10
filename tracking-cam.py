import supervision as sv
from ultralytics import YOLO
import cv2
from trace_annotator import TraceAnnotator
import cv2
import time
import torch
import params

# load model
device = "mps" if params.USE_GPU and torch.backends.mps.is_available() else "cpu"
device = "cuda" if params.USE_GPU and torch.cuda.is_available() else device
print(device)

yolo = YOLO(params.MODEL).to(device)

# setup tracker & annotator
tracker = sv.ByteTrack(track_buffer=params.TRACKING_BUFFER)
trace_annotator = TraceAnnotator(
    color=sv.ColorPalette.default(), trace_length=params.TRACKING_BUFFER)
box_annotator = sv.BoxAnnotator(color=sv.ColorPalette.default(), thickness=4)

frames = 0
curTime = time.time_ns()
displaying = False

# setup capture
cap = cv2.VideoCapture(0)

ret, img = cap.read()
video_info = sv.VideoInfo(img.shape[1], img.shape[0], 30)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # fps
    dTime = time.time_ns()
    if dTime - curTime > 1e9:
        curTime = dTime
        print(frames, 'fps')
        frames = 0
    frames += 1

    # object detection & tracking
    yolo_result = yolo(frame, verbose=False, classes=(24, 26, 28))[0]

    dets = sv.Detections.from_ultralytics(yolo_result)
    dets = tracker.update_with_detections(dets)

    # annotate frame
    labels = [str(d[4]) for d in dets]
    dets.class_id = dets.tracker_id

    try:  # sometimes fails for no reason
        box_annotator.annotate(frame, dets, labels)
        trace_annotator.annotate(frame, dets)
    except:
        pass

    # show frame
    cv2.imshow('BAG TRACKER 9000', frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
