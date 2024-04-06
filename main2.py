# Example file showing a basic pygame "game loop"
import pygame
import json
from math import sin, cos, pi
import os


file_name = "Vintage Race Car.obj.txt"

def degrees(angle):
    return (pi*angle)/180


def draw_pixel(screen, pos):
    pygame.draw.rect(screen, "black", pygame.Rect(pos[0], pos[1], 1, 1))


def draw_vertical_line(screen, xcor, point1_ycor, point2_ycor):
    if point2_ycor > point1_ycor:
        for y in range(int(point1_ycor), int(point2_ycor)):
            pos = (xcor, y)
            draw_pixel(screen, pos)
    else:
        for y in range(int(point2_ycor), int(point1_ycor)):
            pos = (xcor, y)
            draw_pixel(screen, pos)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((720, 720))
origin = (360, 360)
clock = pygame.time.Clock()
running = True

data_ready = {
  "vertices": {
    },
  "lines": {
  }
}

# Loading 3D model data
with open(file_name) as model_3d:
    data = model_3d.readlines()

vertex_count = 0
for i in range(0, len(data)):
    vertex_parsed = False
    if data[i][0] == 'v' and data[i][1] == " ":
        vertex_count += 1
        vertex_parsed = data[i].replace('v',"")
        vertex_parsed = vertex_parsed.split(" ")
        for element in vertex_parsed:
            if element == '':
                vertex_parsed.remove(element)
        #vertex_parsed.remove("")
        vertex_parsed[2] = vertex_parsed[2].replace("\n", "")
    if vertex_parsed:
        vertex_parsed[0] = float(vertex_parsed[0])
        vertex_parsed[1] = float(vertex_parsed[1])
        vertex_parsed[2] = float(vertex_parsed[2])
        data_ready["vertices"][str(vertex_count)] = vertex_parsed

camera_azimuth = 0.0
camera_orbit = 0.0
zoom_factor = 5.0
handling_camera = False

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                camera_orbit += 5
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                camera_orbit -= 5
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and camera_azimuth < 90:
                camera_azimuth += 5
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN and camera_azimuth > -90:
                camera_azimuth -= 5
        if event.type == pygame.MOUSEWHEEL and event.y == 1:
            zoom_factor *= 0.9
        if event.type == pygame.MOUSEWHEEL and event.y == -1:
            zoom_factor *= 1.1

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handling_camera = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            handling_camera = False

        if handling_camera and event.type == pygame.MOUSEMOTION:
            mouse_movement = pygame.mouse.get_rel()
            camera_orbit += mouse_movement[0]
            camera_azimuth += mouse_movement[1]

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # RENDER YOUR GAME HERE
    positions_2d = []

    for vertex in data_ready["vertices"]:
        x3d = data_ready["vertices"][vertex][0]
        y3d = data_ready["vertices"][vertex][1] - 6
        z3d = data_ready["vertices"][vertex][2]

        x2d = origin[0] + (x3d*cos(degrees(camera_orbit)) + z3d*sin(degrees(camera_orbit)))*zoom_factor
        y2d = origin[1] - (x3d*sin(degrees(camera_orbit))*sin(degrees(camera_azimuth)) + y3d*cos(degrees(camera_azimuth)) - z3d*cos(degrees(camera_orbit))*sin(degrees(camera_azimuth)))*zoom_factor
        positions_2d.append((x2d, y2d))

        pygame.draw.circle(screen, "black", (x2d, y2d), 2)

    for line in data_ready["lines"]:
        points_to_join = data_ready["lines"][line]
        point1_xcor = positions_2d[points_to_join[0] - 1][0]
        point1_ycor = positions_2d[points_to_join[0] - 1][1]
        point2_xcor = positions_2d[points_to_join[1] - 1][0]
        point2_ycor = positions_2d[points_to_join[1] - 1][1]

#        print(f"""{positions_2d}
#({point1_xcor},{point1_ycor}), ({point2_xcor}, {point2_ycor})""")

        try:
            m = (point2_ycor-point1_ycor)/(point2_xcor-point1_xcor)
        except ZeroDivisionError:
            m = "infinite"

        if type(m) == float and point2_xcor > point1_xcor:# and -1 <= m <= 1
            for x in range(int(point1_xcor), int(point2_xcor)):
                pos = (x, (x - point1_xcor)*m + point1_ycor)
                draw_pixel(screen, pos)
        if type(m) == float and point1_xcor > point2_xcor:# and -1 <= m <= 1
            for x in range(int(point2_xcor), int(point1_xcor)):
                pos = (x, (x - point1_xcor)*m + point1_ycor)
                draw_pixel(screen, pos)
        #if type(m) == float and -1 <= m <= 1 and point2_ycor > point1_ycor:
         #   for y in range(int(point1_ycor), int(point2_ycor)):
          #      pos = ((y - point1_ycor)/m, y)
        if m == "infinite":
            draw_vertical_line(screen, point1_xcor, point1_ycor, point2_ycor)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
