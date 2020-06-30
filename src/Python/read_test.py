# Masahiro Furukawa
# June 30, 2020


# https://os.mbed.com/compiler/#nav:/MPU-9250-Ch2_ACC_binary/MPU9250_SPI/MPU9250.h
# /* ---- Sensitivity --------------------------------------------------------- */

MPU9250A_2g  =     0.000061035156 # 0.000061035156 g/LSB
MPU9250A_4g  =     0.000122070312 # 0.000122070312 g/LSB
MPU9250A_8g  =     0.000244140625 # 0.000244140625 g/LSB
MPU9250A_16g =     0.000488281250 # 0.000488281250 g/LSB

MPU9250G_250dps  = 0.007633587786 # 0.007633587786 dps/LSB
MPU9250G_500dps  = 0.015267175572 # 0.015267175572 dps/LSB
MPU9250G_1000dps = 0.030487804878 # 0.030487804878 dps/LSB
MPU9250G_2000dps = 0.060975609756 # 0.060975609756 dps/LSB

MPU9250M_4800uT  = 0.6            # 0.6 uT/LSB

MPU9250T_85degC  = 0.002995177763 # 0.002995177763 degC/LSB
Magnetometer_Sensitivity_Scale_Factor = 0.15


import serial
import time
from struct import *

# ser = serial.Serial('/dev/ttyUSB0', 921600)  
ser = serial.Serial('COM4', 921600,  timeout=1)  

state = 0
buf = []

# definition of data frame
class ACC_GYRO:
    def __int__(self):
        self.ax = 0
        self.ay = 0
        self.az = 0
        self.wx = 0
        self.wy = 0
        self.wz = 0


# instantiate data frames
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
        
        # ready to decode
        if len(buf) == 48:

            # decode 48 bytes
            (ch[0].ax, ch[0].ay, ch[0].az, ch[0].wx, ch[0].wy, ch[0].wz,
             ch[1].ax, ch[1].ay, ch[1].az, ch[1].wx, ch[1].wy, ch[1].wz,
             ch[2].ax, ch[2].ay, ch[2].az, ch[2].wx, ch[2].wy, ch[2].wz,
             ch[3].ax, ch[3].ay, ch[3].az, ch[3].wx, ch[3].wy, ch[3].wz )= unpack('hhhhhhhhhhhhhhhhhhhhhhhh', b''.join(buf)) 
            
            # # show integer
            # print (
            #     ch[0].ax, ch[0].ay, ch[0].az, ch[0].wx, ch[0].wy, ch[0].wz,
            #     ch[1].ax, ch[1].ay, ch[1].az, ch[1].wx, ch[1].wy, ch[1].wz,
            #     ch[2].ax, ch[2].ay, ch[2].az, ch[2].wx, ch[2].wy, ch[2].wz,
            #     ch[3].ax, ch[3].ay, ch[3].az, ch[3].wx, ch[3].wy, ch[3].wz ) 
            
            # real value
            # print (
            #     ch[0].ax * MPU9250A_4g, ch[0].ay * MPU9250A_4g, ch[0].az * MPU9250A_4g, ch[0].wx * MPU9250G_500dps, ch[0].wy * MPU9250G_500dps, ch[0].wz * MPU9250G_500dps,
            #     ch[1].ax * MPU9250A_4g, ch[1].ay * MPU9250A_4g, ch[1].az * MPU9250A_4g, ch[1].wx * MPU9250G_500dps, ch[1].wy * MPU9250G_500dps, ch[1].wz * MPU9250G_500dps,
            #     ch[2].ax * MPU9250A_4g, ch[2].ay * MPU9250A_4g, ch[2].az * MPU9250A_4g, ch[2].wx * MPU9250G_500dps, ch[2].wy * MPU9250G_500dps, ch[2].wz * MPU9250G_500dps,
            #     ch[3].ax * MPU9250A_4g, ch[3].ay * MPU9250A_4g, ch[3].az * MPU9250A_4g, ch[3].wx * MPU9250G_500dps, ch[3].wy * MPU9250G_500dps, ch[3].wz * MPU9250G_500dps ) 
            
            # real value
            print (
                "{:+.3f}".format(ch[0].ax * MPU9250A_4g) ,      "{:+.3f}".format(ch[0].ay * MPU9250A_4g) ,      "{:+.3f}".format(ch[0].az * MPU9250A_4g) , 
                "{:+.3f}".format(ch[0].wx * MPU9250G_500dps) ,  "{:+.3f}".format(ch[0].wy * MPU9250G_500dps) ,  "{:+.3f}".format(ch[0].wz * MPU9250G_500dps) ,'\t',
                
                "{:+.3f}".format(ch[1].ax * MPU9250A_4g) ,      "{:+.3f}".format(ch[1].ay * MPU9250A_4g) ,      "{:+.3f}".format(ch[1].az * MPU9250A_4g) , 
                "{:+.3f}".format(ch[1].wx * MPU9250G_500dps) ,  "{:+.3f}".format(ch[1].wy * MPU9250G_500dps) ,  "{:+.3f}".format(ch[1].wz * MPU9250G_500dps) , '\t',
                
                "{:+.3f}".format(ch[2].ax * MPU9250A_4g) ,      "{:+.3f}".format(ch[2].ay * MPU9250A_4g) ,      "{:+.3f}".format(ch[2].az * MPU9250A_4g) , 
                "{:+.3f}".format(ch[2].wx * MPU9250G_500dps) ,  "{:+.3f}".format(ch[2].wy * MPU9250G_500dps) ,  "{:+.3f}".format(ch[2].wz * MPU9250G_500dps) , '\t',
                
                "{:+.3f}".format(ch[3].ax * MPU9250A_4g) ,      "{:+.3f}".format(ch[3].ay * MPU9250A_4g) ,      "{:+.3f}".format(ch[3].az * MPU9250A_4g) , 
                "{:+.3f}".format(ch[3].wx * MPU9250G_500dps) ,  "{:+.3f}".format(ch[3].wy * MPU9250G_500dps) ,  "{:+.3f}".format(ch[3].wz * MPU9250G_500dps) ) 
            

            # print(unpack('hhhhhhhhhhhhhhhhhhhhhhhh', b''.join(buf)) )
            
            buf = []
            state = 0            

ser.close()      