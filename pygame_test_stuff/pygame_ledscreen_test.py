import pygame
import random
import itertools 

def collision_check(active_box, boxes, SCREEN_WIDTH, SCREEN_HEIGHT):
    boxes_list_wo_colour = [box["Box"] for box in boxes]
    box_collision = len(boxes_list_wo_colour[active_box].collidelistall(boxes_list_wo_colour[0:active_box] + boxes_list_wo_colour[active_box+1:len(boxes_list_wo_colour)]))
    window_collision = (boxes_list_wo_colour[active_box].x < 0) + (boxes_list_wo_colour[active_box].x + boxes_list_wo_colour[active_box].width >= SCREEN_WIDTH) \
        + (boxes_list_wo_colour[active_box].y < 0) + (boxes_list_wo_colour[active_box].y + boxes_list_wo_colour[active_box].height >= SCREEN_HEIGHT)
    
    return ((box_collision + window_collision) > 0)

def generate_cubes(boxes_num):
    boxes = []
    dummy_boxes = []
    colours = [(0,0,255), (0,255,0), (255,0,0)]

    while len(boxes) != boxes_num:
      box = {}
      w = random.randint(65, 95)
      h = random.randint(65, 95)
      x = random.randint(0, SCREEN_WIDTH - w)
      y = random.randint(50, SCREEN_HEIGHT - h)
      box["Box"] = pygame.Rect(x, y, w, h)
      box["Colour"] = random.choice(colours)
      dummy_boxes.append(box)
      if collision_check(len(dummy_boxes) - 1, dummy_boxes, SCREEN_WIDTH, SCREEN_HEIGHT) == False:
          boxes.append(box)
      dummy_boxes = boxes.copy()
      
    return boxes

def generate_belt_with_screen(x_screen, y_screen, w_screen, h_screen, x_belt, y_belt, w_belt, h_belt):
    belts_with_screen = []
    belt_instance = {}
    screen_instance = {}
    
    belt_instance["Box"] = pygame.Rect(x_belt, y_belt, w_belt, h_belt)

    screen_instance["Box"] = pygame.Rect(x_screen, y_screen, w_screen, h_screen)
    
    belt_instance["Screen"] = screen_instance
    belts_with_screen.append(belt_instance)
    
    return belts_with_screen
      

pygame.init()

#game window
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600

background_colour = "dark gray"
belt_colour = "black"
screen_colour = (173, 216, 230)
text_colour = "white"

boxes_num = 1
boxes = generate_cubes(boxes_num)

belts_with_screen = generate_belt_with_screen(0, 0, SCREEN_WIDTH, 30, 0, 30, SCREEN_WIDTH, 120)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Drag Drop')

active_box = None
other_boxes = None

modes = [[(255,0,0), (0,255,0), (0,0,255)], [(255,0,0)], [(0,255,0)], [(0,0,255)]]
mode = 0

font = pygame.font.Font('freesansbold.ttf', 32)
colour_codes = {'(255, 0, 0)': "RED",
                '(0, 255, 0)': "GREEN",
                '(0, 0, 255)': "BLUE",
                '(173, 216, 230)': ""}
  
run = True
while run:

  screen.fill(background_colour)
  
  for belt in belts_with_screen:
    pygame.draw.rect(screen, belt_colour, belt["Box"])
    pygame.draw.rect(screen, screen_colour, belt["Screen"]["Box"])
    
    colour_memory = belt["Screen"]["Box"].w*[None]
    boxes_to_draw = []
    
    for box in boxes:
        box_points_y = list(range(int(box["Box"].y), int(box["Box"].y + box["Box"].h)))
        belt_points_y = [j for j in range(belt["Box"].y, belt["Box"].y + belt["Box"].h)]
        
        if (box["Colour"] in modes[mode] and any(box_point in belt_points_y for box_point in box_points_y)):
            screen_seg = pygame.Rect(box["Box"].x, belt["Screen"]["Box"].y, box["Box"].w, belt["Screen"]["Box"].h)
            screen_seg_points_x = [j for j in range(screen_seg.x, screen_seg.x + screen_seg.w)]
            colour_memory[(screen_seg_points_x[0]):(screen_seg_points_x[-1])] = len(screen_seg_points_x)*[box["Colour"]]
            if (mode != 0 and box["Colour"] in modes[mode]):
                box_instance = {}
                box_instance["Box"] = screen_seg
                box_instance["Colour"] = box["Colour"]
                boxes_to_draw.append(box_instance)
                
    if (mode == 0):
        segmented_colour_memory = [list(j) for i, j in itertools.groupby(colour_memory)]
        encountered_points_num = 0
        boxes_to_draw = []
        
        for i in range(len(segmented_colour_memory)):
            
            if (segmented_colour_memory[i][0] == None):
                if (i == 0):
                    box_instance = {}
                    box_instance["Box"] = pygame.Rect(encountered_points_num, belt["Screen"]["Box"].y, len(segmented_colour_memory[i]), belt["Screen"]["Box"].h)
                    
                    if (i == len(segmented_colour_memory) - 1):
                        box_instance["Colour"] = screen_colour
                        boxes_to_draw.append(box_instance)
                        encountered_points_num += len(segmented_colour_memory[i])
                        
                    else:
                        segmented_colour_memory[i+1] = (len(segmented_colour_memory[i]))*[segmented_colour_memory[i+1][0]] + segmented_colour_memory[i+1]
                        
                        
                else:
                    
                    if (i != len(segmented_colour_memory) - 1):
                        boxes_to_draw[-1]["Box"] = pygame.Rect(boxes_to_draw[-1]["Box"].x, belt["Screen"]["Box"].y, boxes_to_draw[-1]["Box"].w + (len(segmented_colour_memory[i])//2), belt["Screen"]["Box"].h)
                        segmented_colour_memory[i+1] = (len(segmented_colour_memory[i]) - len(segmented_colour_memory[i])//2)*[segmented_colour_memory[i+1][0]] + segmented_colour_memory[i+1]
                        encountered_points_num += (len(segmented_colour_memory[i]) - len(segmented_colour_memory[i])//2)
                        
                    else:
                        boxes_to_draw[-1]["Box"] = pygame.Rect(boxes_to_draw[-1]["Box"].x, belt["Screen"]["Box"].y, boxes_to_draw[-1]["Box"].w + (len(segmented_colour_memory[i])), belt["Screen"]["Box"].h)
                        
            elif (segmented_colour_memory[i][0] != None):
                box_instance = {}
                box_instance["Box"] = pygame.Rect(encountered_points_num, belt["Screen"]["Box"].y, len(segmented_colour_memory[i]), belt["Screen"]["Box"].h)
                box_instance["Colour"] = segmented_colour_memory[i][0]
                boxes_to_draw.append(box_instance)
                encountered_points_num += len(segmented_colour_memory[i])
                
        boxes_to_draw_colours = [boxes_to_draw[i]["Colour"] for i in range(len(boxes_to_draw))]
        segmented_boxes_to_draw_colours = [list(j) for i, j in itertools.groupby(boxes_to_draw_colours)]
        encountered_points_num = 0
        final_boxes_to_draw = []
        
        for i in range(len(segmented_boxes_to_draw_colours)):
            box_instance = {}
            total_width = sum([boxes_to_draw[j]["Box"].w for j in range(encountered_points_num, encountered_points_num + len(segmented_boxes_to_draw_colours[i]))])
            box_instance["Box"] = pygame.Rect(boxes_to_draw[encountered_points_num]["Box"].x, belt["Screen"]["Box"].y, total_width, belt["Screen"]["Box"].h)
            box_instance["Colour"] = segmented_boxes_to_draw_colours[i][0]
            final_boxes_to_draw.append(box_instance)
            encountered_points_num += len(segmented_boxes_to_draw_colours[i])
        
        boxes_to_draw = final_boxes_to_draw
            
            
    for box in boxes_to_draw:
        pygame.draw.rect(screen, box["Colour"], box["Box"])
        text = font.render(colour_codes[str(box["Colour"])], True, text_colour)
        textRect = text.get_rect()
        textRect.center = (box["Box"].x + (box["Box"].w//2), belt["Screen"]["Box"].y + (belt["Screen"]["Box"].h//2))
        screen.blit(text, textRect)
            
  for box in boxes:
    pygame.draw.rect(screen, box["Colour"], box["Box"])

  for event in pygame.event.get():
      
    if event.type == pygame.MOUSEBUTTONDOWN:
        
      if event.button == 1: #left mouse click
        for num, box in enumerate(boxes):
          if box["Box"].collidepoint(event.pos):
            active_box = num
            
      if event.button == 2: #middle mouse click
          boxes = []
          boxes_num = 0
            
      if event.button == 3: #right mouse click
        mode += 1
        if mode >= len(modes):
            mode = 0
        
      if event.button == 4: #Scroll up
        boxes_num += 1
        boxes = generate_cubes(boxes_num)
        
      if event.button == 5 and boxes_num > 0: #Scroll down
        boxes_num -= 1
        boxes = generate_cubes(boxes_num)

    if event.type == pygame.MOUSEBUTTONUP:
      if event.button == 1:
        active_box = None

    if event.type == pygame.MOUSEMOTION:
        if active_box != None and len(boxes) > 0:
            boxes[active_box]["Box"].move_ip(event.rel)
            if collision_check(active_box, boxes, SCREEN_WIDTH, SCREEN_HEIGHT) == False:
                last_known_x = boxes[active_box]["Box"].x
                last_known_y = boxes[active_box]["Box"].y
            else:
                boxes[active_box]["Box"].x = last_known_x
                boxes[active_box]["Box"].y = last_known_y
            
    if event.type == pygame.QUIT:
      run = False

  pygame.display.flip()

pygame.quit()