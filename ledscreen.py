import pygame
import params
import random
import tracking
import threading
import cv2


class Bag:
    def __init__(self, pos, size, bag_type, colour, visible=True):
        self.pos = pos
        self.size = size
        self.bag_type = bag_type
        self.colour = colour
        self.visible = visible


pygame.init()

window_screen = pygame.display.set_mode(
    params.DEFAULT_SCREEN_SIZE, pygame.RESIZABLE)
screen = window_screen.copy()
pygame.display.set_caption('LED SCREEN')

font = pygame.font.Font('freesansbold.ttf', params.FONT_SIZE)

BAG_TYPES = ['PRIO', 'ECO', 'TRF']
BAG_COLOR_PER_TYPE = {
    'PRIO': 'red',
    'ECO': 'green',
    'TRF': 'blue'
}
bags = {}

annotated_frame = None
run = True


def loop():
    global run
    while run:
        # render annotated frame
        if annotated_frame is not None:
            cv2.imshow('BAG TRACKER 9000', annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                run = False

        screen.fill(params.BACKGROUND_COLOR)

        for bag in bags.values():
            if not bag.visible:
                continue

            rect = pygame.Rect(bag.pos, 0, bag.size, screen.get_height())
            pygame.draw.rect(screen, bag.colour, rect)

            text = font.render(bag.bag_type, True, params.TEXT_COLOR)
            text_rect = text.get_rect()
            text_rect.center = (rect.x + (rect.w // 2),
                                screen.get_height() // 2)
            screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # scale screen to fit window
        window_screen.blit(pygame.transform.scale(
            screen, window_screen.get_rect().size), (0, 0))
        pygame.display.flip()

    pygame.quit()
    cv2.destroyAllWindows()


def update_bags(xyxy, bag_ids):
    for bag_id in bags:
        bags[bag_id].visible = bag_id in bag_ids

    for bag_id, (x1, y1, x2, y2) in zip(bag_ids, xyxy):
        pos = int(x1)
        size = int(abs(x2 - x1))

        if bag_id in bags:
            bags[bag_id].pos = pos
            bags[bag_id].size = size
        else:
            bag_type = random.choice(BAG_TYPES)
            bag_color = BAG_COLOR_PER_TYPE[bag_type]
            bags[bag_id] = Bag(pos, size, bag_type, bag_color)


def track():
    global annotated_frame

    # for annotated_frame, dets in tracking.process_video('videos/baggage-video.mp4'):
    for annotated_frame, dets in tracking.process_cam():

        if dets.xyxy is None or dets.tracker_id is None:
            continue

        if not run:
            return

        update_bags(dets.xyxy, dets.tracker_id)


track_thread = threading.Thread(target=track)
track_thread.start()
loop()
track_thread.join()
