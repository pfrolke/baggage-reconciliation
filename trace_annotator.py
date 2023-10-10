from typing import List, Optional, Union
import cv2
import numpy as np

from supervision.detection.core import Detections
from supervision.draw.color import Color, ColorPalette
from supervision.geometry.core import Position


class Trace:
    def __init__(
        self,
        max_size: Optional[int] = None,
        start_frame_id: int = 0,
        anchor: Position = Position.CENTER,
    ) -> None:
        self.current_frame_id = start_frame_id
        self.max_size = max_size
        self.anchor = anchor

        self.frame_id = np.array([], dtype=int)
        self.xy = np.empty((0, 2), dtype=np.float32)
        self.tracker_id = np.array([], dtype=int)

    def put(self, detections: Detections) -> None:
        frame_id = np.full(len(detections), self.current_frame_id, dtype=int)
        self.frame_id = np.concatenate([self.frame_id, frame_id])
        self.xy = np.concatenate(
            [self.xy, detections.get_anchor_coordinates(self.anchor)]
        )
        self.tracker_id = np.concatenate(
            [self.tracker_id, detections.tracker_id])

        unique_frame_id = np.unique(self.frame_id)

        if 0 < self.max_size < len(unique_frame_id):
            max_allowed_frame_id = self.current_frame_id - self.max_size + 1
            filtering_mask = self.frame_id >= max_allowed_frame_id
            self.frame_id = self.frame_id[filtering_mask]
            self.xy = self.xy[filtering_mask]
            self.tracker_id = self.tracker_id[filtering_mask]

        self.current_frame_id += 1

    def get(self, tracker_id: int) -> np.ndarray:
        return self.xy[self.tracker_id == tracker_id]


class TraceAnnotator:
    """
    A class for drawing trace paths on an image based on detection coordinates.

    Attributes:
        color (Union[Color, ColorPalette]): The color to draw the trace, can be
            a single color or a color palette.
        position (Optional[Position]): The position of the trace. Defaults to `CENTER`.
        trace_length (int): The maximum length of the trace in terms of historical
            points. Defaults to `30`.
        thickness (int): The thickness of the trace lines. Defaults to `2`.

    """

    def __init__(
        self,
        color: Union[Color, ColorPalette] = ColorPalette.default(),
        position: Optional[Position] = Position.CENTER,
        trace_length: int = 30,
        thickness: int = 2,
    ):
        self.color: Union[Color, ColorPalette] = color
        self.position = position
        self.trace = Trace(max_size=trace_length)
        self.thickness = thickness

    def annotate(self, scene: np.ndarray, detections: Detections) -> np.ndarray:
        """
        Draws trace paths on the frame based on the detection coordinates provided.

        Args:
            scene (np.ndarray): The image on which the traces will be drawn.
            detections (Detections): The detections which include coordinates for
                which the traces will be drawn.

        Returns:
            np.ndarray: The image with the trace paths drawn on it.

        Example:
            ```python
            >>> import supervision as sv

            >>> image = ...
            >>> detections = sv.Detections(...)

            >>> trace_annotator = sv.TraceAnnotator()
            >>> annotated_frame = trace_annotator.annotate(
            ...     scene=image.copy(),
            ...     detections=detections
            ... )
            ```
        """
        self.trace.put(detections)

        for i, (xyxy, mask, confidence, class_id, tracker_id) in enumerate(detections):
            class_id = detections.class_id[i] if class_id is not None else None
            idx = class_id if class_id is not None else i
            color = (
                self.color.by_idx(idx)
                if isinstance(self.color, ColorPalette)
                else self.color
            )

            xy = self.trace.get(tracker_id=tracker_id)
            if len(xy) > 1:
                scene = cv2.polylines(
                    scene,
                    [xy.astype(np.int32)],
                    False,
                    color=color.as_bgr(),
                    thickness=self.thickness,
                )
        return scene
