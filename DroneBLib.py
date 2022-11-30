'''
DroneBLib - Tello Drone Starter Library
(c)2022. Brett Huffman
v.01
---------------------------------------
Drone Controls
tab - lift off
WASD - Drone Forward, Left, Right, Back
Q/E - slow yaw
Arrow keys - ascend, descend, or yaw
H - toggle HUD
backspace - land
P - palm-land
Enter - take picture
R - toggle recording

Based on work from Hanyazou
https://github.com/hanyazou/TelloPy
---------------------------------------
'''
import time
import datetime
import os
import cv2
import tellopy
import av
import numpy
import pygame
import pygame.display
import pygame.key
import pygame.locals
import pygame.font
import copy
import threading #Python library that allows you to create multiple threads to run multiple functions at the same time

# Thread-safe global objects
class SafeFrame(object):
    def __init__(self, startval = None):
        self.lock = threading.Lock()
        self.value = startval
    def set(self, val):
        self.lock.acquire(True, 0.1)
        try:
            self.value = val
        finally:
            self.lock.release()
    def get(self):
        self.lock.acquire()
        try:
            return copy.deepcopy(self.value)
        finally:
            self.lock.release()
class SafeExiting(object):
    def __init__(self, startval = False):
        self.lock = threading.Lock()
        self.value = startval
    def set(self, exiting):
        with self.lock:
            self.value = exiting
    def get(self):
        with self.lock:
            return self.value

current_frame = SafeFrame()
exiting = SafeExiting(False)

class DroneB(object):
    """
    DroneB builds keyboard controls on top of TelloPy as well
    as generating images from the video stream and enabling opencv support
    """

    def frame_grab(self, db):
        """ Stores frames from video stream to global variable """
        global current_frame # global video image
        global exiting # global exit program signal
        for packet in db.container.demux((db.vid_stream,)):
            try:
                for frame in packet.decode():
                    current_frame.set(frame.to_image())
                if exiting.get() == True:
                    break
            except Exception as e:
                print("ERROR!!! {}".format(e))
        print("*** Exiting Frame Grab Thread ***")

    def start(self, custom_loop = False):
        """ Create controller and show the video feed."""
        global current_frame # allows the global variable defined above to be changed inside this function
        global exiting

        # Start everything
        self.init_drone()
        self.init_controls()
        self.init_window()

        threading.Thread(target=self.frame_grab, args=[self]).start() #Create a thread that runs the function frame_grab while main runs in the current thread
        
        if custom_loop == False:
            while exiting.get() == False:
                self.process_keyboard()  # Process keystrokes
                lcurrent_frame = current_frame.get()
                if lcurrent_frame != None:
                    image = self.process_frame(lcurrent_frame)

                # CV way of showing video
    #            cv2.imshow('tello', image)
    #            _ = cv2.waitKey(1) & 0xFF

    def __init__(self):
        self.prev_flight_data = None
        self.record = False
        self.tracking = False
        self.keydown = False
        self.date_fmt = '%Y-%m-%d_%H%M%S'
        self.speed = 50
        self.drone = tellopy.Tello()
        self.wid = None
        self.show_hud = True
        self.hud_font = None
        self.hud_color = (255,255,255)
        self.out_file = None
        self.out_stream = None
        self.out_stream_writer = None
        self.out_name = None
        self.start_time = time.time()

    def init_drone(self):
        """Connect, uneable streaming and subscribe to events"""

        self.drone.connect()
        self.drone.wait_for_connection(60.0)
        self.drone.start_video()
        # container for processing the packets into frames
        self.container = av.open(self.drone.get_video_stream())
        self.vid_stream = self.container.streams.video[0]
        # Subscribe for receiving data
        self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA, self.flight_data_handler)

    def init_window(self):
        pygame.init()
        pygame.display.init()
        pygame.display.set_mode((1280, 720))
        pygame.font.init()

        # Setup the HUD font
        self.hud_font = pygame.font.SysFont("freesansbold.ttf", 50)

        global wid
        if 'window' in pygame.display.get_wm_info():
            wid = pygame.display.get_wm_info()['window']
        print("Tello video WID:", wid)

    def init_controls(self):
        # Keyboard map - Key => Action
        # Action can be a string or method
        self.controls = {
            'w': 'forward',
            's': 'backward',
            'a': 'left',
            'd': 'right',
            'q': 'counter_clockwise',
            'e': 'clockwise',
            # arrow keys for fast turns and altitude adjustments
            'left': lambda drone, speed: drone.counter_clockwise(speed*2),
            'right': lambda drone, speed: drone.clockwise(speed*2),
            'up': lambda drone, speed: drone.up(speed),
            'down': lambda drone, speed: drone.down(speed),
            'tab': lambda drone, speed: drone.takeoff(),
            'backspace': lambda drone, speed: drone.land(),
            'h': self.toggle_hud,
            'p': self.palm_land,
    #        'r': toggle_recording,
    #        'z': toggle_zoom,
    #        'enter': take_picture,
    #        'return': take_picture,
        }

    def process_keyboard(self):
        time.sleep(0.01)  # Pygame seems to want a slight sleep
        for e in pygame.event.get():
            if e.type == pygame.locals.KEYDOWN:
                print('+' + pygame.key.name(e.key))
                keyname = pygame.key.name(e.key)
                if keyname == 'escape':
                    exiting.set(True)
                    self.drone.quit()
                    exit(0)
                if keyname in self.controls:
                    key_handler = self.controls[keyname]
                    if type(key_handler) == str:
                        getattr(self.drone, key_handler)(self.speed)
                    else:
                        key_handler(self.drone, self.speed)

            elif e.type == pygame.locals.KEYUP:
                print('-' + pygame.key.name(e.key))
                keyname = pygame.key.name(e.key)
                if keyname in self.controls:
                    key_handler = self.controls[keyname]
                    if type(key_handler) == str:
                        getattr(self.drone, key_handler)(0)
                    else:
                        key_handler(self.drone, 0)

    def process_frame(self, frame):
        """convert frame to cv2 image and show"""
        image = cv2.cvtColor(numpy.array(
            frame), cv2.COLOR_RGB2BGR)

        pg_image = pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "BGR")

        # Show video via Pygame window
        background = pygame.display.get_surface()
        # Get where to center video
        x = (background.get_width() - pg_image.get_width())/2
        y = (background.get_height() - pg_image.get_height())/2
        # Fast Blit it to the background & flip
        background.blit(pg_image, (x,y))

        # HUD Display
        x += 10 # minor aligning...
        y -= 30
        if self.show_hud == True:
            # Place text on screen
            for val1, val2, val in self.hud:
                txt_img = self.pretty_render(val, self.hud_font)
                y += 40
                background.blit(txt_img, (x,y))

        # Flip the background surface to the
        # Foreground and show
        pygame.display.flip()
#        image = self.write_hud(image)
#        if self.record:
#            self.record_vid(frame)
        return image

    def pretty_render(self, text, font, gfcolor=pygame.Color('dodgerblue'), ocolor=(255, 255, 255), opx=2):
        '''Renders text with a nice background'''
        textsurface = font.render(text, True, gfcolor).convert_alpha()
        w = textsurface.get_width() + 2 * opx
        h = font.get_height()

        osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()

        osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

        for dx, dy in ((-2,-2),(2,2),(-2,2),(2,-2)):
            surf.blit(osurf, (dx + opx, dy + opx))

        surf.blit(textsurface, (opx, opx))
        return surf

    def cvimage_to_pygame(self, image):
        """Convert cvimage into a pygame image"""
        image_rgb = cv2.CreateMat(image.height, image.width, cv2.CV_8UC3)
        cv2.CvtColor(image, image_rgb, cv2.CV_BGR2RGB)
        return pygame.image.frombuffer(image.tostring(), cv2.GetSize(image_rgb), "RGB")

    # ALT:0|SPD:0|BAT:12|WIFI:0|CAM:0|MODE:6
    hud = [
        ['ALT', 'ALT {0}', ''],
        ['SPD', 'SPD {0}', ''],
        ['BAT', 'BAT {0}%', ''],
        ['WIFI', 'NET {0}%', '']
    ]

    def flight_data_handler(self, event, sender, data):
        '''Receives data from drone and formats for HUD'''
        strData = str(data).replace(" ", "")
        hud_items = dict(x.split(":") for x in str(strData).split("|"))
        i = 0
        for item_val, fmt_str, val3 in (self.hud):
            val = hud_items[item_val]
            if val == None:
                self.hud[i][2] = fmt_str.format("N/A")
            else:
                self.hud[i][2] = fmt_str.format(val)
            i += 1

    ####################################
    # Functions Available for core functions
    def get_exiting(self):
        global exiting
        return exiting.get()

    def take_picture(self, drone, speed):
        if speed == 0:
            return
        drone.take_picture()

    def palm_land(self, drone, speed):
        if speed == 0:
            return
        drone.palm_land()

    def toggle_hud(self, drone, speed):
        if speed == 0:
            return
        self.show_hud = not self.show_hud
