# from https://github.com/mfurukawa/imu_sensor/tree/master/src/Python 
# March 31, 2025 by Masahiro Furukawa, furukawa.masahiro.ist@osaka-u.ac.jp
# September 03, 2020 by Yuto Nakayachi 


from __future__ import unicode_literals ,print_function
import serial 
from time import sleep 
import numpy as np 
import matplotlib.pyplot as plt
import io 
import csv
import time 
import datetime 
import struct 


# Variable to get real value 
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

# number of axis 
numVariable = 24 # 4ch * 6acc 

# Maximum time for measure
minuteLength = 25 

# sampling rate 
smplHz = 500 

# Variable to count number of sampling 
smpl_cnt = 0

# Variable to count number of fail
fail_cnt_byte = 0
fail_cnt_head = 0

# Array to store data
buf = [[0 for i in range(numVariable + 2)] for j in range(smplHz*60*minuteLength)] 

# Array to store real value 
buf_f = [[0 for i in range(numVariable + 2)] for j in range(smplHz*60*minuteLength)]

# define serial port 
ser = serial.Serial("COM3",921600,timeout=1) 


# Check serial connection 
if ser.is_open:
    print("Start Serial Connection") 
else:
    print("PORT ERROR") 
    ser.close() 
    exit() 

# Function to create csv file 
def writeCSV():
    global ser 
    global smpl_cnt 
    global buf 
    global buf_f 
    ser.write(b'r') 
    print("Start Create CSV File") 
    head = ["sample_cc","ms",
            # "ACC_X1","ACC_Y1","ACC_Z1","GYRO_X1","GYRO_Y1","GYRO_Z1",
            "ACC_X2","ACC_Y2","ACC_Z2","GYRO_X2","GYRO_Y2","GYRO_Z2",
            "ACC_X3","ACC_Y3","ACC_Z3","GYRO_X3","GYRO_Y3","GYRO_Z3"
            # ,"ACC_X4","ACC_Y4","ACC_Z4","GYRO_X4","GYRO_Y4","GYRO_Z4"
            ]
    dt_now = datetime.datetime.now() 
    year = dt_now.year 
    month = dt_now.month 
    day = dt_now.day 
    hour = dt_now.hour 
    minute = dt_now.minute 
    t = str(year)+str(month)+str(day)+str(hour)+str(minute)
    title_int = "acc_data"+str(t)+"_int"+".csv"
    title_float="acc_data"+str(t)+"_float"+".csv" 
    FILE_int = open(title_int,"w",newline="") 
    FILE_float = open(title_float,"w",newline="")    
    wi = csv.writer(FILE_int)
    wf = csv.writer(FILE_float) 
    wi.writerow(head)
    wf.writerow(head) 
    for i in range(smpl_cnt):
        wi.writerow(buf[i]) 
        wf.writerow(buf_f[i]) 
    FILE_int.close() 
    FILE_float.close() 
    print()
    print(title_int+" "+"created") 
    print(title_float+" "+"created")
    print()
    print("Done Create CSV File") 
       
# Function to Measure 
def readByte():
    global ser 
    global smpl_cnt 
    global buf 
    global buf_f  
    global xl 
    global yl 
    global fail_cnt_byte 
    global fail_cnt_head 

    ser.write(b"r") 
    time.sleep(0.01)
    ser.write(b"s") 
    time.sleep(0.01) 

    state = 0
    store = []
    while(1):
        res = ser.read()

        if state == 0 and res == b'\x7f':  # DEL code (b'\x7f') as a start byte
            state = 1 
            store = []
        elif state == 1:
            store.append(res) 
                
            if len(store) == 50: # 2Channels * 6 axis * 2bytes per axis + 

                # check header 
                if store[0]==b'\x7f':
                    del store[0]
                else:
                    print("header error") 
                    #time.sleep(2)
                    fail_cnt_head += 1 
                    state = 0
                    store = []
                    continue 

        
                #add time stamp
                if smpl_cnt==0:
                    #start_time = int.from_bytes(res[-1],"big")
                    start_time = struct.unpack("b",store[-1])[0]
                    #start_time = store[-1]
                    #print(start_time)
                    tmp_time = 0
                else:
                    #now_time = int.from_bytes(res[-1],"big") 
                    add_time = struct.unpack("b",store[-1])[0]
                    #add_time = store[-1]
                    tmp_time += add_time
                buf[smpl_cnt][1] = tmp_time
                buf[smpl_cnt][0] = smpl_cnt
                buf_f[smpl_cnt][1] = tmp_time
                buf_f[smpl_cnt][0] = smpl_cnt

                # store data 
                for i in range(0,48,2):
                    res2 = store[i:i+2] 
                    tup = struct.unpack('>h', b''.join(res2)) 
                    val = tup[0]
                    num = i%12 
                    ch = i//12 
                    buf[smpl_cnt][6*ch + num//2 + 2]=val 
                    if (num//2)>=3:
                        buf_f[smpl_cnt][6*ch + num//2 + 2]=val * MPU9250G_500dps
                    else:
                        buf_f[smpl_cnt][6*ch + num//2 + 2]=val * MPU9250A_4g

                """           
                print (
                    "{:+.3f}".format(buf_f[smpl_cnt][2]) ,      "{:+.3f}".format(buf_f[smpl_cnt][3]) ,      "{:+.3f}".format(buf_f[smpl_cnt][4]) , 
                    "{:+.3f}".format(buf_f[smpl_cnt][5]) ,  "{:+.3f}".format(buf_f[smpl_cnt][6]) ,  "{:+.3f}".format(buf_f[smpl_cnt][7]) ,'\t',
                    
                    "{:+.3f}".format(buf_f[smpl_cnt][8]) ,      "{:+.3f}".format(buf_f[smpl_cnt][9]) ,      "{:+.3f}".format(buf_f[smpl_cnt][10]) , 
                    "{:+.3f}".format(buf_f[smpl_cnt][11]) ,  "{:+.3f}".format(buf_f[smpl_cnt][12]) ,  "{:+.3f}".format(buf_f[smpl_cnt][13]) , '\t',
                    
                    "{:+.3f}".format(buf_f[smpl_cnt][14]) ,      "{:+.3f}".format(buf_f[smpl_cnt][15]) ,      "{:+.3f}".format(buf_f[smpl_cnt][16]) , 
                    "{:+.3f}".format(buf_f[smpl_cnt][17]) ,  "{:+.3f}".format(buf_f[smpl_cnt][18]) ,  "{:+.3f}".format(buf_f[smpl_cnt][19]) , '\t',
                    
                    "{:+.3f}".format(buf_f[smpl_cnt][20]) ,      "{:+.3f}".format(buf_f[smpl_cnt][21]) ,      "{:+.3f}".format(buf_f[smpl_cnt][22]) , 
                    "{:+.3f}".format(buf_f[smpl_cnt][23]) ,  "{:+.3f}".format(buf_f[smpl_cnt][24]) ,  "{:+.3f}".format(buf_f[smpl_cnt][25]) ) 
                """
                
                smpl_cnt += 1
                store = []
                state = 0

            if smpl_cnt>=10000:
                break 

# Start
print("ready? --> press s key") 
while(1):
    ready_s = input() 
    if ready_s == "s":
        break 
    if ready_s == "r":
        print("over") 
        ser.close()
        exit() 

# Measure the start time 
p_time = time.time() 

# Function to measure 
readByte()

# Measure the end time 
e_time = time.time() 

# The time it took 
print("time: ",e_time - p_time) 

# Function to create csv file 
writeCSV() 

# close serial port 
ser.close() 

print("number of data: ",smpl_cnt) 
print("number of byte fail: ",fail_cnt_byte)
print("number of header fail: ",fail_cnt_head)
print("END")