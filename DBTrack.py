'''
DBTrack.py - Track blue squares with queues.  Once
user presses 'C', the drone will automatically
track a blue square (use blue tape on the wall to demo).

(c)2022. Brett Huffman
v.02
---------------------------------------
'''
from libs.DroneBLib import DroneB
from libs.DroneBLib import exiting, current_frame
import cv2
import numpy as np
import imutils
from libs.QR import read_qr_code
from math import floor

def main():

    db = DroneB()
    db.start(custom_loop = True)

    loop_count = 0
    # The start of this loop should be exactly as it's shown below. Any changes and it might not work
    # as expected. Use the CV image however you want to analyze drone video and call drone functions 
    # to move drone as desired.
    while exiting.get() == False: # Loop until exiting is signaled
        db.process_keyboard()  # Process keystrokes
        # Once the command queue is enabled, process them
        # one-by-one until it's empty
        db.process_command_queue() # Process the command queue
        lcurrent_frame = current_frame.get() # Get video frame
        if lcurrent_frame != None:
            image = db.process_frame(lcurrent_frame) # Process
            # Change nothing above here!  Use image however you 
            # want to analyze drone position, movement, etc.
            # image is a CV2 image.

            loop_count += 1
            if loop_count % 5 == 0:

                # Look for QR - if read put text on screen
                str_code, points = read_qr_code(image=image)

                start = None
                end = None
                
                if(str_code and len(points) > 0):
                    # Be sure to get the floor of these points
                    start = (int(points[0][0][0]), int(points[0][0][1]))
                    end = (int(points[0][2][0]), int(points[0][2][1]))

                    # Draw text and surrounding box
                    cv2.putText(image, str_code, (2, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                    cv2.rectangle(image, start, end, (0, 255, 0), 3)
                    
                else:
                    continue

                ''' Determine how much to move
                The axes are shown below (assuming a frame width and height of 600x400):
                +Y                 (0,200)

                Y  (-300, 0)        (0,0)               (300,0)

                -Y                 (0,-200)
                -X                    X                    +X
                
                if  abs(extBot[0] - extTop[0]) > 40 and abs(extBot[1] - extTop[1]) > 40:
                    # Get image midpoint and calculate diff
                    height, width, channels = frame.shape
                    image_mid = (width // 2, height // 2)
                    obj_mid = (extTop[0] + (extBot[0] - extTop[0])//2, extTop[1] + (extBot[1] - extTop[1])//2)

                    # Draw them on the image
                    cv2.circle(image, image_mid, 4, (255, 255, 255))
                    cv2.circle(image, obj_mid, 4, (255, 0, 255))

                    # Do a little proportion here
                    # 40 pixels   =   diff
                    #  3 seconds      X
                    prop_x_to_move = int(10 * (image_mid[0] - obj_mid[0])//40)
                    prop_y_to_move = int(10 * (image_mid[1] - obj_mid[1])//40)

                    if db.command_queue_active == True and db.command_queue_enable == True:
                        if prop_x_to_move > 5:
                            print("Sent left", abs(prop_x_to_move))
                            db.AddNewQueueItem("left", abs(prop_x_to_move))
                        elif prop_x_to_move < -5:
                            print("Sent right", abs(prop_x_to_move))
                            db.AddNewQueueItem("right", abs(prop_x_to_move))

                        if prop_y_to_move > 5:
                            print("Sent up", abs(prop_x_to_move))
                            db.AddNewQueueItem("up", abs(prop_x_to_move))
                        elif prop_y_to_move < -5:
                            print("Sent down", abs(prop_x_to_move))
                            db.AddNewQueueItem("down", abs(prop_x_to_move))
'''
                # CV way of showing video
                cv2.imshow('Secondary View', image)
                _ = cv2.waitKey(1) & 0xFF


if __name__ == '__main__':
    main()
