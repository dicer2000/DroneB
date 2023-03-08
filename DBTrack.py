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
    ResponseRadius = 240  # Pixels out to automatically move.  Otherwise don't move

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

            # Get image center
            h, w, c = image.shape
            img_center_x = w // 2
            img_center_y = h // 2
            qr_center_x = None
            qr_center_y = None

            loop_count += 1
            if loop_count % 10 == 0:

                # Look for QR - if read put text on screen
                str_code, points = read_qr_code(image=image)

                qr_lt = None
                qr_rt = None
                qr_rb = None
                qr_lb = None
                qr_center_x = None
                qr_center_y = None

                if(str_code and len(points) > 0):
                    # Get the square of the QR found
                    qr_lt = (int(points[0][0][0]), int(points[0][0][1]))
                    qr_rt = (int(points[0][1][0]), int(points[0][1][1]))
                    qr_rb = (int(points[0][2][0]), int(points[0][2][1]))
                    qr_lb = (int(points[0][3][0]), int(points[0][3][1]))
                    qr_center_x = qr_lt[0] + ((qr_rt[0] - qr_lt[0]) // 2)
                    qr_center_y = qr_lt[1] + (( qr_lb[1] - qr_lt[1]) // 2)
                    
                    # Draw text and surrounding box
                    cv2.putText(image, str_code, (2, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                    cv2.rectangle(image, qr_lt, qr_rb, (0, 255, 0), 3)

                    cv2.rectangle(image, (qr_center_x-2,qr_center_y-2), (qr_center_x+2,qr_center_y+2), (255, 255, 0), 3)
                    # QR Center - Aqua
                    cv2.circle(image, (qr_center_x, qr_center_y), 4, (255, 255, 0))
                    # Response area - Aqua
                    cv2.circle(image, (img_center_x, img_center_y), ResponseRadius, (0, 255, 255))
                    # Screen Center - Red
                    cv2.circle(image, (img_center_x, img_center_y), 4, (0, 255, 255))


                    ''' Determine how much to move
                    The CV2 Image layout is like this:
                    0/0---column--->
                    |
                    |
                    row
                    |
                    |
                    v

                    '''
                    # Are points within our Response Radius?
                    if loop_count % 30 == 0 and ResponseRadius ** 2 > abs(img_center_x-qr_center_x)**2 + abs(img_center_x-qr_center_x)**2:

                        # Do a little proportion here
                        # 40 pixels   =   diff
                        #  3 seconds      X
                        prop_x_to_move = int(10 * (img_center_x - qr_center_x)//30)
                        prop_y_to_move = int(10 * (img_center_y - qr_center_y)//30)

                        if db.command_queue_enable == True: #db.command_queue_active == True and 
                            if prop_x_to_move > 5:
                                print("*** Sent left", abs(prop_x_to_move))
                                db.AddNewQueueItem("left", abs(prop_x_to_move))
                            elif prop_x_to_move < -5:
                                print("*** Sent right", abs(prop_x_to_move))
                                db.AddNewQueueItem("right", abs(prop_x_to_move))

                            if prop_y_to_move > 5:
                                print("*** Sent up", abs(prop_x_to_move))
                                db.AddNewQueueItem("up", abs(prop_x_to_move))
                            elif prop_y_to_move < -5:
                                print("*** Sent down", abs(prop_x_to_move))
                                db.AddNewQueueItem("down", abs(prop_x_to_move))


                else:
                    continue

                # CV way of showing video
                cv2.imshow('Secondary View', image)
                _ = cv2.waitKey(1) & 0xFF


if __name__ == '__main__':
    main()
