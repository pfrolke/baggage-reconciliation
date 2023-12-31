import pygame
import params
import tracking
import threading
import colour_picker
import cv2
import requests
import math


class Bag:
    def __init__(self, pos, size, bag_type, colour, visible=True):
        self.pos = pos
        self.size = size
        self.bag_type = bag_type
        self.colour = colour
        self.visible = visible
        self.missed_frames = 0
        self.detected_frames = 0


pygame.init()

cv2.namedWindow("BAG TRACKER 9000", cv2.WINDOW_NORMAL)

displayInfo = pygame.display.Info()
display_w, display_h = displayInfo.current_w, displayInfo.current_h
window_screen = pygame.display.set_mode(
    (display_w, display_h * 2 // 3), pygame.RESIZABLE
)
screen = pygame.Surface(params.DEFAULT_SCREEN_SIZE)
pygame.display.set_caption("LED SCREEN")

font = pygame.font.Font("freesansbold.ttf", params.FONT_SIZE)

BAG_TYPES = ["ALL", "TEMP", "PRIO", "ECO", "TRF"]
BAG_COLOR_PER_TYPE = {"TEMP": "gray", "PRIO": "red", "ECO": "green", "TRF": "blue"}

bag_type_idx = 0
bags = {}

annotated_frame = None
run = True


def scale_bag_size(bag: Bag) -> int:
    screen_center = params.DEFAULT_SCREEN_SIZE[0] / 2
    bag_center = bag.pos + bag.size / 2
    delta_x = abs(bag_center - screen_center)

    scaling_factor = (
        math.sqrt(params.DISTORTION_FACTOR**2 + delta_x**2)
        / params.DISTORTION_FACTOR
    )

    return int(bag.size * scaling_factor)


def loop():
    global run
    global bag_type_idx

    while run:
        # render annotated frame
        if annotated_frame is not None:
            cv2.imshow("BAG TRACKER 9000", annotated_frame)
            cv2.resizeWindow("BAG TRACKER 9000", display_w // 2, display_h // 4)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                run = False

        screen.fill(params.BACKGROUND_COLOR)

        sorted_bags = sorted(bags.values(), key=lambda bag: bag.size, reverse=True)

        for bag in sorted_bags:
            if bag.visible == True:
                # scaled_size = scale_bag_size(bag)
                if bag.pos + bag.size >= screen.get_width():
                    bag.size = screen.get_width() - bag.pos

                rect = pygame.Rect(bag.pos, 0, bag.size, screen.get_height())
                pygame.draw.rect(screen, bag.colour, rect)

                text = font.render(bag.bag_type, True, params.TEXT_COLOR)
                text_rect = text.get_rect()
                text_rect.center = (rect.x + (rect.w // 2), screen.get_height() // 2)
                screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # right mouse click
                    bag_type_idx = (bag_type_idx + 1) % len(BAG_TYPES)

        # scale screen to fit window
        window_screen.blit(
            pygame.transform.scale(screen, window_screen.get_rect().size), (0, 0)
        )
        pygame.display.flip()

    pygame.quit()
    cv2.destroyAllWindows()


def update_bags(xyxy, pred_bag_ids):
    def pred_has_bag(bag_id):
        return pred_bag_ids is not None and bag_id in pred_bag_ids

    for bag_id, bag in bags.items():
        if pred_has_bag(bag_id):
            # bag predicted
            bag.missed_frames = 0
            bag.detected_frames += 1

            # visible if type is selected
            if bag.detected_frames >= params.MINIMUM_DETECTED_FRAMES:
                bag.visible = (
                    BAG_TYPES[bag_type_idx] == "ALL"
                    or BAG_COLOR_PER_TYPE[BAG_TYPES[bag_type_idx]] == bag.colour
                )
            continue

        if (
            not pred_has_bag(bag_id)
            and bag.missed_frames <= params.ALLOWED_MISSED_FRAMES
        ):
            # estimate position
            bag.missed_frames += 1
            continue

        if not pred_has_bag(bag_id) and bags[bag_id].visible:
            # bag taken off belt
            bags[bag_id].visible = False
            requests.post(
                f"{params.HOST}:{params.SERVER_PORT}/bag",
                json={"bagId": int(bag_id), "action": "off-belt"},
            )

    if xyxy is None or pred_bag_ids is None:
        return

    for bag_id, (x1, y1, x2, y2) in zip(pred_bag_ids, xyxy):
        pos = int(x1)
        size = int(abs(x2 - x1))

        if bag_id in bags and bags[bag_id].bag_type != "TEMP":
            # update bag with predictions
            bags[bag_id].pos = pos
            bags[bag_id].size = size

        elif bag_id in bags and bags[bag_id].bag_type == "TEMP":
            peak_colour = colour_picker.colour_picker(
                annotated_frame[
                    int(y1) : int(min(y2, annotated_frame.shape[0])),
                    int(x1) : int(min(x2, annotated_frame.shape[1])),
                ]
            )
            
            bag_type = "TEMP"

            if peak_colour is not None:
                if peak_colour in params.YELLOW:
                    bag_type = "PRIO"
                elif peak_colour in params.BROWN:
                    bag_type = "ECO"
                else:
                    bag_type = "TRF"

            bags[bag_id].bag_type = bag_type
            bags[bag_id].colour = BAG_COLOR_PER_TYPE[bag_type]
            bags[bag_id].pos = pos
            bags[bag_id].size = size

            if bag_type != "TEMP":
                requests.post(
                    f"{params.HOST}:{params.SERVER_PORT}/bag",
                    json={
                        "bagId": int(bag_id),
                        "action": "on-belt",
                        "bag_type": bag_type,
                    },
                )

        else:
            peak_colour = colour_picker.colour_picker(
                annotated_frame[
                    int(y1) : int(min(y2, annotated_frame.shape[0])),
                    int(x1) : int(min(x2, annotated_frame.shape[1])),
                ]
            )

            bag_type = "TEMP"

            if peak_colour is not None:
                if peak_colour in params.YELLOW:
                    bag_type = "PRIO"
                elif peak_colour in params.BROWN:
                    bag_type = "ECO"
                else:
                    bag_type = "TRF"

            bag_color = BAG_COLOR_PER_TYPE[bag_type]
            bags[bag_id] = Bag(pos, size, bag_type, bag_color)

            if bag_type != "TEMP":
                requests.post(
                    f"{params.HOST}:{params.SERVER_PORT}/bag",
                    json={
                        "bagId": int(bag_id),
                        "action": "on-belt",
                        "bag_type": bag_type,
                    },
                )


def track():
    global annotated_frame

    # for annotated_frame, dets in tracking.process_video("videos/belt-test-video_rev.qt"):
    for annotated_frame, dets in tracking.process_cam():
        if not run:
            return

        update_bags(dets.xyxy, dets.tracker_id)


track_thread = threading.Thread(target=track)
track_thread.start()
loop()
track_thread.join()
