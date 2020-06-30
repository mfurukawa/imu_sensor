# Masahiro Furukawa
# June 30, 2020

import serial
import time
from struct import *

# ser = serial.Serial('/dev/ttyUSB0', 921600)  
ser = serial.Serial('COM4', 921600,  timeout=1)  

state = 0
buf = []

class ACC_GYRO:
    def __int__(self):
        self.ax = 0
        self.ay = 0
        self.az = 0
        self.wx = 0
        self.wy = 0
        self.wz = 0


# data frame    
ch = []
ch.append( ACC_GYRO() )
ch.append( ACC_GYRO() )
ch.append( ACC_GYRO() )
ch.append( ACC_GYRO() )

# command char 'r' means to stop streaming
ser.write(b'r')
time.sleep(0.01)

# command char 's' means to start streaming
ser.write(b's')
time.sleep(0.01)

while 1:

    val = ser.read()
    
    # waiting for '\r'
    if state == 0 and val == b'\r':        
        val = ser.read()
        
        # waiting for '\n' and get ready
        if val == b'\n':
            state = 1
            buf = []
            next
        else:
            print('End byte set failure.')

    # store val into list
    if state == 1:
        buf.append(val)
        
        # decode 48 bytes
        if len(buf) == 48:
            (ch[0].ax, ch[0].ay, ch[0].az, ch[0].wx, ch[0].wy, ch[0].wz,
             ch[1].ax, ch[1].ay, ch[1].az, ch[1].wx, ch[1].wy, ch[1].wz,
             ch[2].ax, ch[2].ay, ch[2].az, ch[2].wx, ch[2].wy, ch[2].wz,
             ch[3].ax, ch[3].ay, ch[3].az, ch[3].wx, ch[3].wy, ch[3].wz )= unpack('hhhhhhhhhhhhhhhhhhhhhhhh', b''.join(buf)) 
            
            print (ch[0].ax, ch[0].ay, ch[0].az, ch[0].wx, ch[0].wy, ch[0].wz,
             ch[1].ax, ch[1].ay, ch[1].az, ch[1].wx, ch[1].wy, ch[1].wz,
             ch[2].ax, ch[2].ay, ch[2].az, ch[2].wx, ch[2].wy, ch[2].wz,
             ch[3].ax, ch[3].ay, ch[3].az, ch[3].wx, ch[3].wy, ch[3].wz ) 
            

            # print(unpack('hhhhhhhhhhhhhhhhhhhhhhhh', b''.join(buf)) )
            
            buf = []
            state = 0            

ser.close()      