import pygame
import random

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
      w = random.randint(35, 65)
      h = random.randint(35, 65)
      x = random.randint(0, SCREEN_WIDTH - w)
      y = random.randint(50, SCREEN_HEIGHT - h)
      box["Box"] = pygame.Rect(x, y, w, h)
      box["Colour"] = random.choice(colours)
      dummy_boxes.append(box)
      if collision_check(len(dummy_boxes) - 1, dummy_boxes, SCREEN_WIDTH, SCREEN_HEIGHT) == False:
          boxes.append(box)
      dummy_boxes = boxes.copy()
      
    return boxes

def generate_belt_with_LEDstrips(x_strip, y_strip, w_strip, h_strip, x_belt, y_belt, w_belt, h_belt):
    belts_with_LEDstrip = []
    belt_instance = {}
    LEDstrip_instance = {}
    
    belt_instance["Box"] = pygame.Rect(x_belt, y_belt, w_belt, h_belt)
    
    LEDstrip_instance["Box"] = pygame.Rect(x_strip, y_strip, w_strip, h_strip)
    LEDstrip_instance["Circles set"] = [[(i*h_strip+h_strip//2), (y_strip+h_strip//2), (h_strip//2)] for i in range(0, (w_strip//h_strip+1))]
    LEDstrip_instance["Circle colours"] = len(LEDstrip_instance["Circles set"])*[(255, 255, 255)]
    
    belt_instance["LEDstrip"] = LEDstrip_instance
    belts_with_LEDstrip.append(belt_instance)
    
    return belts_with_LEDstrip
      

pygame.init()

#game window
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

background_colour = "black"
belt_colour = "dark gray"
LED_colour = "light gray"
LEDstrip_colour = "white"

boxes_num = 1
boxes = generate_cubes(boxes_num)

belts_with_LEDstrip = generate_belt_with_LEDstrips(0, 0, SCREEN_WIDTH, 20, 0, 20, SCREEN_WIDTH, 130)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Drag Drop')

active_box = None
other_boxes = None

modes = [[(255,0,0), (0,255,0), (0,0,255)], [(255,0,0)], [(0,255,0)], [(0,0,255)]]
mode = 0
  
run = True
while run:

  screen.fill(background_colour)
  
  for belt in belts_with_LEDstrip:
    pygame.draw.rect(screen, belt_colour, belt["Box"])
    pygame.draw.rect(screen, LEDstrip_colour, belt["LEDstrip"]["Box"])
    
    light_colour_memory = len(belt["LEDstrip"]["Circles set"])*[LED_colour]
    light_distance_memory = len(belt["LEDstrip"]["Circles set"])*[SCREEN_HEIGHT]
    
    for i in range(len(belt["LEDstrip"]["Circles set"])):
        for box in boxes:
            box_points_y = list(range(int(box["Box"].y), int(box["Box"].y + box["Box"].h)))
            belt_points = [j for j in range(belt["Box"].y, belt["Box"].y + belt["Box"].h)]
            
            if (box["Colour"] in modes[mode] and any(box_point in belt_points for box_point in box_points_y)):
                box_points_x = list(range(int(box["Box"].x), int(box["Box"].x + box["Box"].w)))
                circle_points = [j for j in range(belt["LEDstrip"]["Circles set"][i][0], belt["LEDstrip"]["Circles set"][i][0] + 2*belt["LEDstrip"]["Circles set"][i][2])]
                
                if (any(box_point in circle_points for box_point in box_points_x)):
                    if (light_distance_memory[i] > box["Box"].y):
                        light_colour_memory[i] = box["Colour"]
                        light_distance_memory[i] = box["Box"].y
                
    for i in range(len(light_colour_memory)):
        if light_colour_memory[i] != None:
            belt["LEDstrip"]["Circle colours"][i] = light_colour_memory[i]
            pygame.draw.circle(screen, belt["LEDstrip"]["Circle colours"][i], belt["LEDstrip"]["Circles set"][i][0:2],belt["LEDstrip"]["Circles set"][i][2])
        else:
            pygame.draw.circle(screen, LED_colour, belt["LEDstrip"]["Circles set"][i][0:2],belt["LEDstrip"]["Circles set"][i][2])
            
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