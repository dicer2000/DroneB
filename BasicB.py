'''
BasicB - The most basic use of the Tello 
Drone Starter Library.  No looping is
required, just instantiate an DroneB object,
call the start() method, and go

(c)2022. Brett Huffman
v.01
---------------------------------------
'''
from DroneBLib import DroneB

def main():
    db = DroneB()
    db.start()


if __name__ == '__main__':
    main()