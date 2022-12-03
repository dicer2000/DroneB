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

def main():

    # Start up Neural Network
    net = cv2.dnn.readNetFromCaffe('./nn/DenseNet_121.prototxt.txt', './nn/DenseNet_121.caffemodel')


    db = DroneB()
    db.start(custom_loop = True)



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
            if loop_count % 30 == 0:

                # Analyze video with NN
                # DenseNet121 image size: 224x224
#                imgSqr = resize_image(image, (224,224))
                rows, cols, channels = image.shape

                net.setInput(cv2.dnn.blobFromImage(image, size=(cols, rows), swapRB=True, crop=False))
 
                # Runs a forward pass to compute the net output
                networkOutput = net.forward()
 
                # Loop on the outputs
                for detection in networkOutput[0,0]:
                    if len(detection) < 6:
                        continue
                    score = float(detection[2])
                    if score > 0.2:
                    
                        left = detection[3] * cols
                        top = detection[4] * rows
                        right = detection[5] * cols
                        bottom = detection[6] * rows
                
                        #draw a red rectangle around detected objects
                        cv2.rectangle(image, (int(left), int(top)), (int(right), int(bottom)), (0, 0, 255), thickness=2)
 

                # CV way of showing video
                cv2.imshow('Secondary View', image)
                _ = cv2.waitKey(1) & 0xFF

def resize_image(img, size=(28,28)):

    h, w = img.shape[:2]
    c = img.shape[2] if len(img.shape)>2 else 1

    if h == w: 
        return cv2.resize(img, size, cv2.INTER_AREA)

    dif = h if h > w else w

    interpolation = cv2.INTER_AREA if dif > (size[0]+size[1])//2 else cv2.INTER_CUBIC

    x_pos = (dif - w)//2
    y_pos = (dif - h)//2

    if len(img.shape) == 2:
        mask = np.zeros((dif, dif), dtype=img.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w] = img[:h, :w]
    else:
        mask = np.zeros((dif, dif, c), dtype=img.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w, :] = img[:h, :w, :]

    return cv2.resize(mask, size, interpolation)

def _resize2SquareKeepingAspectRation(img, size, interpolation):
    h, w = img.shape[:2]
    c = None if len(img.shape) < 3 else img.shape[2]
    if h == w: return cv2.resize(img, (size, size), interpolation)
    if h > w: dif = h
    else:     dif = w
    x_pos = int((dif - w)/2.)
    y_pos = int((dif - h)/2.)
    if c is None:
        mask = np.zeros((dif, dif), dtype=img.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w] = img[:h, :w]
    else:
        mask = np.zeros((dif, dif, c), dtype=img.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w, :] = img[:h, :w, :]
    return cv2.resize(mask, (size, size), interpolation)

if __name__ == '__main__':
    main()
