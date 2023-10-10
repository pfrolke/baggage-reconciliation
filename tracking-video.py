import supervision as sv
from ultralytics import YOLO
from tqdm.autonotebook import tqdm
from trace_annotator import TraceAnnotator

yolo = YOLO('models/yolov8l.pt')

path = 'videos/remco-baggage.mov'

frame_gen = sv.get_video_frames_generator(path)
video_info = sv.VideoInfo.from_video_path(path)

tracker = sv.ByteTrack(track_buffer=500)
trace_annotator = TraceAnnotator(
    color=sv.ColorPalette.default(), trace_length=100)
box_annotator = sv.BoxAnnotator(color=sv.ColorPalette.default(), thickness=4)

with sv.VideoSink('videos/remco-baggage-pred.mp4', video_info) as sink:
    for frame in tqdm(frame_gen, total=video_info.total_frames):
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

        sink.write_frame(frame)
