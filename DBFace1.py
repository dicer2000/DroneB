'''
DBFace1.py

(c)2022. Brett Huffman
v.02
---------------------------------------
'''
from DroneBLib import DroneB
from DroneBLib import exiting, current_frame
import cv2
import numpy as np
import imutils

ilowH = 0
ihighH = 179
ilowS = 0
ihighS = 255
ilowV = 0
ihighV = 255

def main():


    db = DroneB()
    db.start(custom_loop = True)

    # Setup some special keyboard handlers
    db.controls["u"] = h_up
    # Set range for green color and 
    # define mask
    color_lower = np.array([110,50,50], np.uint8) #(255, 255, 130) #BGR
    color_upper = np.array([130,255,255], np.uint8) #(131, 67, 18)  #BGR
    kernel = np.ones((5, 5), "uint8")

    loop_count = 0
    # The start of this loop should be exactly as it's shown below. Any changes and it might not work
    # as expected. Use the CV image however you want to analyze drone video and call drone functions 
    # to move drone as desired.
    while exiting.get() == False: # Loop until exiting is signaled
        db.process_keyboard()  # Process keystrokes
        lcurrent_frame = current_frame.get() # Get video frame
        if lcurrent_frame != None:
            image = db.process_frame(lcurrent_frame) # Process
            # Change nothing above here!  Use image however you 
            # want to analyze drone position, movement, etc.
            # image is a CV2 image.

            # Here is an example to show a secondary CV2
            # window.  loop_count keeps it updating only
            # once per 30 frames (which is a good idea
            # for efficiency sake.)
            loop_count += 1
            if loop_count % 5 == 0:

                # Analyze video cv2 color detection
#                hsvFrame = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#                green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)
#                green_mask = cv2.dilate(green_mask, kernal)
#                res_green = cv2.bitwise_and(image, image,
#                                            mask = green_mask)

#                blurred = cv2.GaussianBlur(image, (11, 11), 0)
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                mask = cv2.inRange(hsv, color_lower, color_upper)
#                mask = cv2.erode(mask, None, iterations=2)
#                mask = cv2.dilate(mask, None, iterations=2)

#                res = cv2.bitwise_and(image, image, mask = mask)

                # Convert to BGR Gray
                mask2 = cv2.cvtColor(hsv.copy(), cv2.COLOR_BGR2GRAY)

                # reduce the noise
#                opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                contours, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#                contours = imutils.grab_contours(contours)
                contours = contours[0]
                # Get dimensions of everything
                x = 10000
                y = 10000
                w = 0
                y = 0
                for contour in contours:
                    x,y,w,h = cv2.boundingRect(contour)
#                    if w>5 and h>10:
                    cv2.rectangle(image,(x,y),(x+w,y+h),(155,155,0),1)

#                    c = max(cnts, key=cv2.contourArea)

#                    extLeft = tuple(c[c[:, :, 0].argmin()][0])
#                    extRight = tuple(c[c[:, :, 0].argmax()][0])
#                    extTop = tuple(c[c[:, :, 1].argmin()][0])
#                    extBot = tuple(c[c[:, :, 1].argmax()][0])

#                    cv2.rectangle(mask, extTop, extBot, (0, 255, 0), 3)

                cv2.putText(image, str(ilowH), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                # CV way of showing video
                cv2.imshow('Secondary View', image)
                _ = cv2.waitKey(1) & 0xFF

def h_up(drone, speed):
    global ilowH
    if ilowH < 180:
        ilowH += 1

def h_down(drone, speed):
    global ihighH
    if ihighH > -1:
        ihighH -= 1

if __name__ == '__main__':
    main()
