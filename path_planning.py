import pygame
from pygame.locals import *
import json
import math
import threading
import socket
import sys
import time
import numpy
import cv2 as cv
import cvzone
class Background (pygame.sprite.Sprite):
def __init__(self, image, location, scale):
pygame.sprite.Sprite.__init__(self)
self.image=pygame.image.load(image)
self.image=pygame.transform.rotozoom(self.image, 0, scale)
self.rect=self.image.get_rect()
self.rect.left, self.rect.top=location
def draw_grid(color, blocksize):
'''
Draw block grid for reference
'''
for x in range(WINDOW_WIDTH):
for y in range(WINDOW_HEIGHT):
rect=pygame.Rect((x*blocksize), (y*blocksize), blocksize, bloc
ksize)
pygame.draw.rect(screen, color, rect, 1)
pygame.display.update()
class button_class():
def __init__(self, x, y, text):
self.x=x
self.y=y
self.text=text
def draw_button(self):
global clicked
global path_wp
global index
global dir
global running
action=False
#colours for button and text
button_col = (240, 240, 240)
click_col = (0, 255, 0)
hover_col=(0, 240, 0)
text_col = (0, 0, 0)
width = 60
height = 30
# Set font
font=pygame.font.SysFont('Arial', 16)
# Get mouse position
pos=pygame.mouse.get_pos()
'''
Draw button
'''
# Rect() argument -->(left, top, width, height)
button=pygame.Rect(self.x, self.y, width, height)
button=pygame.draw.rect(screen, button_col, button)
# Check mouseover and clicked conditions
if button.collidepoint(pos):
if event.type==pygame.MOUSEBUTTONDOWN:
pygame.draw.rect(screen, click_col, button)
clicked=True
action=True
elif pygame.mouse.get_pressed()[0] == 0 and clicked == True:
clicked = False
else:
pygame.draw.rect(screen, hover_col, button)
else:
pygame.draw.rect(screen, button_col, button)
# Add text
text=font.render(self.text, True, text_col)
text_coord=(self.x + width/2),(self.y + height/2)
text_rect=text.get_rect(center=text_coord)
# Update screen
screen.blit(text, text_rect)
pygame.display.update()
return action
# ------------------Tello Initializing------------------
class Tello:
def __init__(self):
self._running = True
# Create a UDP socket
self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
self.sock.bind((host_ip, response_port)) # Bind for receiving
def terminate(self):
self._running = False
self.sock.close()
def recv(self):
""" Handler for Tello response message """
while self._running:
try:
msg,
= self.sock.recvfrom(1024) # Read 1024-
_
bytes from UDP socket
print("response: {}".format(msg.decode(encoding="utf-8")))
except Exception as err:
print(err)
def send(self, msg):
""" Handler for send message to Tello """
msg = msg.encode(encoding="utf-8")
self.sock.sendto(msg, (tello_ip, command_port))
print("message: {}".format(msg)) # Print message
def reset_the_path():
# Load background image
bground=Background('Capture.png',[80,0],1.0)
screen.blit(bground.image, bground.rect)
# Draw gridlines
draw_grid((255, 255, 255), 20)
# Draw the buttons
button_class.draw_button(turn_left)
button_class.draw_button(turn_right)
button_class.draw_button(go_straight)
button_class.draw_button(reset_path)
button_class.draw_button(path_complete)
def get_dist_btw_pos(pos0, pos1):
'''
Get distance between two mouse positions
'''
x=abs(pos0[0]-pos1[0])
y=abs(pos0[1]-pos1[1])
dist_px=math.hypot(x,y)
dist_cm=dist_px*MAP_SIZE_COEFF
return int(dist_cm), int(dist_px)
def get_angle_between_lines(pos0, pos1, posref):
'''
Get angle between two lines with respect to 'posref'
NOTE: using dot product
'''
ax=posref[0]-pos0[0]
ay=posref[1]-pos0[1]
bx=posref[0]-pos1[0]
by=posref[1]-pos1[1]
# Get dot product of pos0 and pos1
_dot=(ax*bx)+(ay*by)
# Get magnitude of pos0 and pos1
_magA=math.sqrt(ax**2 + ay**2)
_magB=math.sqrt(bx**2 + by**2)
# Get angle in radians and degrees
_rad=math.acos (_dot / (_magA*_magB))
angle=(_rad * 180)/math.pi # Angle in degrees
return int(angle)
def compute_waypoints(path_wp,dir):
global index
'''
Compute the waypoints (distances and angles)
'''
# Append first pos reference (dummy)
if index>0:
path_wp.insert(0, (path_wp[0][0], path_wp[0][1]-10))
path_dist_cm=[]
path_dist_px=[]
path_angle=[]
for index in range(len(path_wp)):
# Skip the first and second index
if index>1:
dist_cm, dist_px= get_dist_btw_pos(path_wp[index-
1],path_wp[index])
path_dist_cm.append(dist_cm)
path_dist_px.append(dist_px)
# Skip the first and last index
if index>0 and index<(len(path_wp)-1):
angle=get_angle_between_lines(path_wp[index-
1],path_wp[index+1],path_wp[index])
path_angle.append(angle)
# Print out the information
print('path_wp: {}', format(path_wp))
print('dist_cm: {}', format(path_dist_cm))
print('dist_px: {}', format(path_dist_px))
print('path_angle: {}', format(path_angle))
print('dir: {}', format(dir))
'''
Save waypoints into JSON file
'''
waypoints=[]
for index in range(len(path_dist_cm)):
waypoints.append({
'dist_cm': path_dist_cm[index],
'dist_px': path_dist_px[index],
'path_angle': path_angle[index],
'dir': dir[index]
})
# Save to JSON file
f=open('waypoints.json', 'w+')
if index>0:
path_wp.pop(0)
json.dump({
'wp': waypoints,
'coords': path_wp
}, f, indent=4)
f.close()
def follow_path():
global index
global t
# Checking if a path was chosen
if index>0:
# Opening JSON file
f = open('waypoints.json',)
# returns JSON object as a dictionary
path = json.load(f)
prev_dir="2"
try:
# Start tello command program
msg_command = "command"
t.send(msg_command)
msg_takeoff = "takeoff"
t.send(msg_takeoff)
time.sleep(5)
except:
t.terminate()
recvThread.join()
print('\n Unexpected error \n')
sys.exit
# Iterating through the json list
for i in path['wp']:
rot_x=i["path_angle"]
forward_x=i["dist_cm"]
try:
if i["dir"]=="2":
if i==0 or prev_dir=="2":
msg1 = "cw 0"
if prev_dir=="0":
msg1 = "cw " + str(180-rot_x)
if prev_dir=="1":
msg1 = "ccw " + str(180-rot_x)
if i["dir"]=="0":
msg1 = "ccw " + str(rot_x)
if i["dir"]=="1":
msg1 = "cw " + str(rot_x)
# Send data
t.send(msg1)
time.sleep(3)
prev_dir=i["dir"]
msg2 = "forward " + str(forward_x)
# Send data
t.send(msg2)
# detect objects here
time.sleep(8)
except KeyboardInterrupt:
t.terminate()
recvThread.join()
break
# Finish the path
t.terminate()
recvThread.join()
print("\nArrived to destination\n")
# Closing file
f.close()
else:
print('\nPlease choose a path that you need me to follow.\n')
def print_path():
global index
# global t
# Checking if a path was chosen
if index>0:
# Opening JSON file
f = open('waypoints.json',)
# returns JSON object as a dictionary
path = json.load(f)
prev_dir="2"
# Iterating through the json list
for i in path['wp']:
rot_x=i["path_angle"]
forward_x=i["dist_cm"]
try:
if i["dir"]=="2":
if i==0 or prev_dir=="2":
msg1 = "cw 0"
if prev_dir=="0":
msg1 = "cw " + str(180-rot_x)
if prev_dir=="1":
msg1 = "ccw " + str(180-rot_x)
if i["dir"]=="0":
msg1 = "ccw " + str(rot_x)
if i["dir"]=="1":
msg1 = "cw " + str(rot_x)
print(msg1)
time.sleep(3)
prev_dir=i["dir"]
msg2 = "forward " + str(forward_x)
print(msg2)
# detect objects here
time.sleep(8)
except KeyboardInterrupt:
break
print("\nArrived to destination\n")
# Closing file
f.close()
else:
print('\nPlease choose a path that you need me to follow.\n')
'''
how many pixels = actual distance in cm
453 px = 495 cm --> 495/453 = MAP_SIZE_COEFF
'''
MAP_SIZE_COEFF=1.1 # will be calbrated each time we load an image
pygame.init()
WINDOW_WIDTH=880
WINDOW_HEIGHT=530
screen=pygame.display.set_mode([WINDOW_WIDTH,WINDOW_HEIGHT])
screen.fill((255,255,255))
# Load background image
bground=Background('Capture.png',[80,0],1.0)
screen.blit(bground.image, bground.rect)
# Draw gridlines
draw_grid((255, 255, 255), 20)
# Define the buttons
turn_left=button_class(12, 2, 'Left')
turn_right=button_class(12, 42, 'Right')
go_straight=button_class(12, 82, 'Straight')
reset_path=button_class(12, 122, 'Reset')
path_complete=button_class(12, 162, 'Complete')
# Draw the buttons
button_class.draw_button(turn_left)
button_class.draw_button(turn_right)
button_class.draw_button(go_straight)
button_class.draw_button(reset_path)
button_class.draw_button(path_complete)
'''
Main capturing mouse program
'''
# Define global variables
clicked=False
path_wp=[]
dir=[]
index=0
running=True
while running:
for event in pygame.event.get():
if event.type==pygame.QUIT:
running=False
elif event.type==pygame.MOUSEBUTTONDOWN:
pos=pygame.mouse.get_pos()
# Check if a button was clicked
if pos[0]<80:
if button_class.draw_button(path_complete):
pygame.QUIT
running=False
if button_class.draw_button(reset_path):
reset_the_path()
path_wp=[]
dir=[]
index=0
# Take direction for rotation
if button_class.draw_button(turn_left):
dir.append('0')
if button_class.draw_button(turn_right):
dir.append('1')
if button_class.draw_button(go_straight):
dir.append('2')
else:
pos=pygame.mouse.get_pos()
print(pos)
path_wp.append(pos)
if index>0:
pygame.draw.line(screen,(255,0,0),path_wp[index-
1],pos,2)
index+=1
pygame.display.update()
# Generate waypoints
compute_waypoints(path_wp,dir)
# time.sleep(5)
'''
Start new thread to recieve Tello response messages
'''
# Tello constants
"""
@brief Tello IP address. Use local IP address since
host computer/device is a WiFi client to Tello.
"""
tello_ip = "192.168.10.1"
"""
Tello port to send command message.
"""
command_port = 8889
"""
@brief Host IP address. 0.0.0.0 referring to current
host/computer IP address.
"""
host_ip = "0.0.0.0"
"""
@brief UDP port to receive response msg from Tello.
Tello command response will send to this port.
"""
response_port = 9000
""" Welcome note """
print("\nTello Command Program\n")
# Tello Startup
t = Tello()
recvThread = threading.Thread(target=t.recv)
recvThread.start()
# Path following
follow_path()
print_path()