# Detection constants
whT = 320
confthreshold =0.5
nmsthreshold= 0.2
# LOAD MODEL
# Coco Names
classesFile = "coco.names"
classNames = []
with open(classesFile, 'rt') as f:
classNames = f.read().rstrip('\n').split('\n')
# print(classNames)
# Model Files
modelConfiguration = "yolov3.cfg"
modelWeights = "yolov3.weights"
net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
# Tello constants
tello_ip = "192.168.10.1"
command_port = 8889
host_ip = "0.0.0.0"
response_port = 9000
# Speed accumulated during the period of avoidance
speed_l_r = 0
# Set counter for number of speed data saved
n = 0
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
def read_frame(vcap, whT):
ret, frame = vcap.read()
blob = cv.dnn.blobFromImage(frame, 1/255, (whT, whT), [0, 0, 0], 1
, crop=False)
net.setInput(blob)
layersNames = net.getLayerNames()
outputNames = [(layersNames[i[0] - 1]) for i in net.getUnconnected
OutLayers()]
outputs = net.forward(outputNames)
return ret, frame, outputs
# ------------------Detection and Avoidance Algorithm------------------
def detect_obstacles(outputs, frame):
hT, wT, cT = frame.shape
bbox = []
classIds = []
confs = []
obstacle_center = []
obstacle_area = []
obstacle_distance = []
for output in outputs:
for det in output:
scores = det[5:]
classId = numpy.argmax(scores)
confidence = scores[classId]
if confidence > confthreshold:
w,h = int(det[2]*wT) , int(det[3]*hT)
x,y = int((det[0]*wT)-w/2) , int((det[1]*hT)-h/2)
cx = x + w/2
cy = y + h/2
area = w*h
# Calculate the distance between the obstacle and the came
ra based on its class
if classId == 0:
# At 50cm, the size of box bounding person is 400
distance = -0.5*(w - 400) + 50 # distance in cm
# Continue the conditions for other obstacles
elif (classId == 14) or (classId == 68):
distance = -0.5*(w - 900) + 50
elif (classId == 26) or (classId == 30) or (classId == 83)
:
distance = -0.5*(w - 150) + 50
elif (classId == 43) or (classId == 63) or (classId == 85)
or (classId == 76):
distance = -0.5*(w - 50) + 50
elif (classId == 67):
distance = -0.5*(w - 1000) + 50
else:
# Set greater than the collision distance because won'
t be testing the code on other obstacles
distance = 300
bbox.append([x,y,w,h])
classIds.append(classId)
confs.append(float(confidence))
obstacle_area.append(area)
obstacle_center.append([cx, cy])
obstacle_distance.append(distance)
if len(classIds) != 0:
i = obstacle_distance.index(min(obstacle_distance))
detect_collision(obstacle_center[i][0], obstacle_cente
r[i][1], obstacle_distance[i])
else:
back_to_path()
indices = cv.dnn.NMSBoxes(bbox, confs, confthreshold, nmsthreshold)
# Visualize obstacles
for i in indices:
i = i[0]
box = bbox[i]
x, y, w, h = box[0], box[1], box[2], box[3]
# print(x,y,w,h)
cvzone.cornerRect(frame, box)
cv.putText(frame,f'{classNames[classIds[i]].upper()} {int(confs[i]
*100)}%',
(x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
"""
Defining a collision detection technique based on estimating the distance
between the drone (its camera)
and the obstacle facing it, and decide a threshold.
Collision distance: 1.5 m
We estimate this distance based on the size of the object appearing on the
camera
and its common size in real life
Width for common objects:
1 person w = 40 cm
15 bench w = 90 cm
27 backpack w = 15 cm
31 handbag w = 15 cm
44 bottle w = 5 cm
62 chair w = 40 cm
64 potted plant w = 5 cm
68 window w = 100 cm
69 desk w = 90 cm
77 cell phone w = 5 cm
84 book w = 15 cm
86 vase w = 5 cm
ClassId = nb - 1
"""
def detect_collision(cx, cy, distance):
collision_distance = 150
# Check for approaching obstacles
if distance <= collision_distance:
avoid_collision(vcap, cx, cy)
if distance > collision_distance:
avoid_collision(vcap, 0, 0)
back_to_path()
def get_object_quadrant(vcap, cx, cy):
if vcap.isOpened():
width = int(vcap.get(3))
height = int(vcap.get(4))
if (cx <= width/2) and (cy <= height/2):
quadrant = 'TOP_LEFT'
if (cx > width/2) and (cy < height/2):
quadrant = 'TOP_RIGHT'
if (cx <= width/2) and (cy >= height/2):
quadrant = 'BOTTOM_LEFT'
if (cx > width/2) and (cy > height/2):
quadrant = 'BOTTOM_RIGHT'
error = cx - width/2
return quadrant, error
def avoid_collision(vcap, cx, cy):
global n
global speed_l_r
# Controller constants
pid = [0.4, 0, 0]
#Set bias for controller
P = 0
# Check for collision threat
if (cx != 0) and (cy !=0):
quadrant, error = get_object_quadrant(vcap, cx, cy)
# Calculate input
u = pid[0]*error + P
# Get avoidance direction
if (quadrant == 'TOP_LEFT') or (quadrant == 'BOTTOM_LEFT'): # erro
r < 0
move_dir = 'right'
# print(quadrant)
# print(move_dir)
u = u*(-(numpy.sign(error)))
if (quadrant == 'TOP_RIGHY') or (quadrant == 'BOTTOM_RIGHT'): # er
ror > 0
move_dir = 'left'
# print(quadrant)
# print(move_dir)
u = u*((numpy.sign(error)))
u = int(numpy.clip(u, -50, 50))
if (cx == 0) and (cy ==0):
u = 0
# Send results to tello
msg_rc = "rc " + str(u) + " 0 0 0"
t.send(msg_rc)
# print("Avoiding... ")
# print(msg_rc)
speed_l_r = speed_l_r + u
n = n + 1
def back_to_path():
# Controller constants
pid = [0.4, 0, 0]
#Set bias for controller
P = 0
ur = speed_l_r/n
u = ur*(-1)
u = int(numpy.clip(u, -50, 50))
# Send results to tello
msg_rc = "rc " + str(u) + " 0 0 0"
t.send(msg_rc)
# print("Returning... ")
# print(msg_rc)
# n = 0
# speed_l_r = 0