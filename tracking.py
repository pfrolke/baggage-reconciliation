import supervision as sv
from ultralytics import YOLO
import cv2
import time
import torch
import params
from tqdm import tqdm

# load model
device = "mps" if params.USE_GPU and torch.backends.mps.is_available() else "cpu"
device = "cuda" if params.USE_GPU and torch.cuda.is_available() else device
print(device)

yolo = YOLO(params.MODEL).to(device)

# setup tracker & annotator
tracker = sv.ByteTrack(track_buffer=params.TRACKING_BUFFER)
trace_annotator = sv.TraceAnnotator(
    color=sv.ColorPalette.default(), trace_length=params.TRACKING_BUFFER
)
box_annotator = sv.BoxAnnotator(
    color=sv.ColorPalette.default(), thickness=params.BOX_THICKNESS
)


def process_frame(frame):
    # object detection & tracking - block list
    yolo_result = yolo(
        frame, verbose=False, classes=params.YOLO_ALLOWLIST, agnostic_nms=True
    )[0]

    # # object detection & tracking - only suitcases and bags
    # yolo_result = yolo(frame, verbose=False, classes=(24, 26, 28))[0]

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

    return frame, dets


def process_cam():
    frames = 0
    curTime = time.time_ns()

    cap = cv2.VideoCapture(0)
    while True:
        # fps
        dTime = time.time_ns()
        if dTime - curTime > 1e9:
            curTime = dTime
            print(frames, "fps")
            frames = 0
        frames += 1

        ret, frame = cap.read()

        if not ret:
            break

        frame, dets = process_frame(frame)

        yield frame, dets

    cap.release()


def process_video(path):
    frame_gen = sv.get_video_frames_generator(path)
    video_info = sv.VideoInfo.from_video_path(path)

    with sv.VideoSink(f"{path}-pred.mp4", video_info) as sink:
        for frame in tqdm(frame_gen, total=video_info.total_frames):
            frame, dets = process_frame(frame)
            sink.write_frame(frame)

            yield frame, dets


if __name__ == "__main__":
    # for annotated_frame, dets in process_video('videos/test_video.mov'):
    for annotated_frame, dets in process_cam():
        cv2.imshow("BAG TRACKER 9000", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
