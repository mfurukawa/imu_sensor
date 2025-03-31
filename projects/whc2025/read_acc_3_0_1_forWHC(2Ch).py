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
import msvcrt


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
numVariable = 12 # 2ch * 6acc 

# Maximum time for measure
minuteLength = 5 

# sampling rate 
smplHz = 1000 

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
ser = serial.Serial("COM3", 921600, timeout=1) 


# Check serial connection 
if ser.is_open:
    print("Serial Connection OK")
    print("Serial Port: ",ser.name)
    print("Baudrate: ",ser.baudrate) 
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
    t = str(year) + f"{month:02}" + f"{day:02}" + "_" + f"{hour:02}" + f"{minute:02}"
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
    global ser, smpl_cnt, buf, buf_f
    global fail_cnt_byte, fail_cnt_head

    ser.write(b"r")
    time.sleep(0.01)
    ser.write(b"s")
    time.sleep(0.01)

    state = 0
    store = []
    tmp_time = 0

    while True:
            
        if msvcrt.kbhit():
            if( msvcrt.getwch() == "q"):
                print("over") 
                ser.write(b"r")
                time.sleep(0.04)
                break
            
        res = ser.read()

        if state == 0 and res == b'\x7f':
            state = 1
            store = []
            res = 0
            print("state = 1")

        elif state == 1 and res == b'\x7f':
            fail_cnt_byte += 1
            state = 0
            store = []
            print("fail_cnt_byte += 1   " + str(fail_cnt_byte))

        else:

            store.append(res)

            if len(store) == 51:  # ← 52バイトに変更

                # タイムスタンプ（3byte Big Endian）
                timestamp_bytes = b''.join(store[-3:])
                add_time = int.from_bytes(timestamp_bytes, byteorder='big')
                if smpl_cnt == 0:
                    tmp_time = 0
                else:
                    tmp_time = add_time

                buf[smpl_cnt][0] = smpl_cnt
                buf[smpl_cnt][1] = tmp_time
                buf_f[smpl_cnt][0] = smpl_cnt
                buf_f[smpl_cnt][1] = tmp_time

                # センサデータ24バイト（12個のshort整数）
                for i in range(0, 24, 2):
                    val = struct.unpack('>h', b''.join(store[i:i+2]))[0]
                    idx = i // 2
                    buf[smpl_cnt][idx + 2] = val
                    if idx % 6 >= 3:  # 角速度
                        buf_f[smpl_cnt][idx + 2] = val * MPU9250G_500dps
                    else:  # 加速度
                        buf_f[smpl_cnt][idx + 2] = val * MPU9250A_4g

                smpl_cnt += 1
                store = []
                state = 0

                print("state = 0")
                if smpl_cnt >= 1000:
                    break


# Start
print("press [s] key to start") 
print("press [q] key to quit (stop while measure)")
print("ready? --> ")

while(1):
    if msvcrt.kbhit():
        ready_s = msvcrt.getwch()
    else:
        ready_s = ""
    if ready_s == "s":
        break 
    if ready_s == "q":
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