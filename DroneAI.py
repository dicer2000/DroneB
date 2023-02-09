'''
DroneAI.py - An AI implementation with DroneB



(c)2022. Brett Huffman
v.02
---------------------------------------
'''
from libs.DroneBLib import DroneB
from libs.DroneBLib import exiting, current_frame
import cv2
import numpy as np


def main():


    db = DroneB()
    db.start(custom_loop = True)

    # Start the AI
    modelFile = "nn/res10_300x300_ssd_iter_140000.caffemodel"
    configFile = "nn/deploy.prototxt.txt"
    net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

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
            if db.command_queue_enable and loop_count % 30 == 0:

                h = image.shape[0]
                w = image.shape[1]

                blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 117.0, 123.0))

                net.setInput(blob)
                faces = net.forward()
                
                # If non found, start yawing left
                # looking for a face
                if faces.shape[2]:
                    db.AddNewQueueItem("yaw_left", 500)

                bFound = False
                for i in range(faces.shape[2]):
                    confidence = faces[0, 0, i, 2]
                    if confidence > 0.5:
                        box = faces[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (x, y, x1, y1) = box.astype("int")
                        bFound = True
                        break

                if not bFound:
                    db.AddNewQueueItem("yaw_left", 500)
                    continue
                else:
                    # Found a good face, zero in on it
                    cx = x1 - x
                    cy = y1 - y
                    cmx = h // 2
                    cmy = w // 2

                cv2.rectangle(image, (cx-1,cy-1), (cx+1, cy+1), (0, 0, 255), 2)
                cv2.rectangle(image, (cmx-1,cmy-1), (cmx+1, cmy+1), (255, 0, 0), 2)

                '''
                for i in range(faces.shape[2]):
                    confidence = faces[0, 0, i, 2]
                    if confidence > 0.5:
                        box = faces[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (x, y, x1, y1) = box.astype("int")
                        cv2.rectangle(image, (x, y), (x1, y1), (0, 0, 255), 2)

                '''

                # CV way of showing video
                cv2.imshow('Secondary View', image)
                _ = cv2.waitKey(1) & 0xFF

if __name__ == '__main__':
    main()
