'''
DBQueue - Demonstrates queuing items for
the drone to process

(c)2022. Brett Huffman
v.02
---------------------------------------
'''
from DroneBLib import DroneB, Queue_Item
from DroneBLib import exiting, current_frame
import cv2

def main():
    db = DroneB()
    db.start(custom_loop = True)


    # Fill command queue with items to process
    db.command_queue.append(Queue_Item(db.queue_items["takeoff"], 2000))
    db.command_queue.append(Queue_Item(db.queue_items["left"], 500))
    db.command_queue.append(Queue_Item(db.queue_items["forward"], 500))
    db.command_queue.append(Queue_Item(db.queue_items["right"], 500))
    db.command_queue.append(Queue_Item(db.queue_items["forward"], 500))
    db.command_queue.append(Queue_Item(db.queue_items["yaw_left"], 2000))
    db.command_queue.append(Queue_Item(db.queue_items["forward"], 500))
    db.command_queue.append(Queue_Item(db.queue_items["yaw_left"], 2000))
    db.command_queue.append(Queue_Item(db.queue_items["forward"], 500))

    # The start of this loop should be exactly as it's shown below. Any changes and it might not work
    # as expected. Use the CV image however you want to analyze drone video and call drone functions 
    # to move drone as desired.
    while exiting.get() == False: # Loop until exiting is signaled
        db.process_keyboard()  # Process keystrokes
        lcurrent_frame = current_frame.get() # Get video frame
        if lcurrent_frame != None:
            image = db.process_frame(lcurrent_frame) # Process


        db.process_command_queue() # Process the command queue

if __name__ == '__main__':
    main()