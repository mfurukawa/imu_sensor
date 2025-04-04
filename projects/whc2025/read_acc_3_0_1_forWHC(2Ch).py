# from https://github.com/mfurukawa/imu_sensor/tree/master/src/Python 
AUTHOR  = "Masahiro Furukawa"
DATE    = "March 31, 2025"
EMAIL   = "furukawa.masahiro.ist@osaka-u.ac.jp"
MESSAGE = "IMU sensor MPU9250 (3-axis accelerometer, gyroscope) Logger"
# September 03, 2020 by Yuto Nakayachi 

DESCRIPTION1 = "This program is for reading data from the IMU sensor MPU9250 (3-axis accelerometer, gyroscope, and magnetometer)"
DESCRIPTION2 = "and saving the data to a CSV file."

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
minuteLength = 1 

# sampling rate 
smplHz = 1000 

# Maximum number of sampling
maxSmpl = smplHz*60*minuteLength

# Variable to count number of sampling 
smpl_cnt = 0

# Variable to count number of fail
fail_cnt_byte = 0
fail_cnt_head = 0

# Array to store data
buf = [[0 for i in range(numVariable + 2)] for j in range(maxSmpl)] 

# Array to store real value 
buf_f = [[0 for i in range(numVariable + 2)] for j in range(maxSmpl)]

# define serial port 
ser = serial.Serial("COM3", 921600, timeout=1) 

# Display copyright information
print("-" * 60)
print(f"{MESSAGE}")
print("-" * 60)
print(f"{DATE}")
print(f"{AUTHOR}")
print(f"{EMAIL}")
print()

print(f"{DESCRIPTION1}")
print(f"{DESCRIPTION2}")
print("-" * 60)

# Check serial connection 
if ser.is_open:
    print("\nSerial Connection OK")
    print("Serial Port: ",ser.name)
    print("Baudrate: ",ser.baudrate)

    # Send break code to microcontroller
    ser.send_break(duration=0.25)  # Send a break signal for 250ms
    sleep(0.5)  # Wait for the microcontroller to reset or respond
    
    # ブレークコード送信時(mbedのリセット時)に受信したデータを読み取る
    data = ser.read(ser.in_waiting)  # read all data currently in the input buffer
    
    # ブレークコード送信時に返信があれば表示させる。センサーの接続確認のためには必要
    if data:
        print("Received data on connection:")
        print(data.decode('ascii', errors='replace'))  # display received bytes as ASCII
    else:
        print("No data received on connection.")

    # バッファをクリアする
    ser.flushInput()  # clear input buffer
    ser.flushOutput()  # clear output buffer
    print("\nBuffer Clear")

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
    second = dt_now.second 
    t = str(year) + f"{month:02}" + f"{day:02}" + "_" + f"{hour:02}" + f"{minute:02}" + f"{second:02}"
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

        # キー待ち受け
        if msvcrt.kbhit():
            if msvcrt.getwch() == "q":
                print("Stopped by user.")
                ser.write(b"r")
                time.sleep(0.04)
                break

        res = ser.read()
        # 受信したバイトを表示
        # print(f"{res.hex()} ", end="")

        if res == b'':  # タイムアウト時
            print("Timeout: No data received")
            continue
        
        if state == 0:
            if res == b'\x7f': # ヘッダはDELが2つ連続するが1つ目のDELを見つけた
                state = 1
                continue
        
        if state == 1:
            if res != b'\x7f': # ヘッダはDELが2つ連続するはずだがしない
                # 異常：ヘッダの条件を満たさなかった
                fail_cnt_byte += 1
                state = 0
                # print("Header error")
                continue

            else:
                state = 2
                # print("found header") 
                # 直後の行を実行するので continue しない！

        if state == 2:
            store = ser.read(27) # ← ヘッダを除いて残り27バイト受信でOK

            # 受信した全てのバイトを表示
            # print(" ".join(f"{byte:02x}" for byte in store))
            
            # 受信したバイト数を表示
            # print(f"Received {len(store)} bytes")

            try:
                # タイムスタンプ（末尾3バイト）
                timestamp_bytes = b''.join(bytes([b]) for b in store[-3:])

                # タイムスタンプのバイト列を表示
                # print("TIMESTAMP " + " ".join(f"{byte:02x}" for byte in timestamp_bytes))
            
                # タイムスタンプを整数に変換
                timestamp = int.from_bytes(timestamp_bytes, byteorder='big')
                print(f"Timestamp: {timestamp}")

                if smpl_cnt < len(buf):

                    # サンプル数を格納
                    buf[smpl_cnt][0] = smpl_cnt
                    buf_f[smpl_cnt][0] = smpl_cnt

                    # タイムスタンプを格納
                    buf[smpl_cnt][1] = timestamp
                    buf_f[smpl_cnt][1] = timestamp

                    for i in range(0, 24, 2):
                        # 2バイトずつ読み取る(16bit分解能、ビッグエンディアン)
                        val = struct.unpack('>h', bytes(store[i:i+2]))[0]

                        idx = i // 2
                        buf[smpl_cnt][idx + 2] = val
                        
                        # 実数値保持用
                        if idx % 6 >= 3:
                            buf_f[smpl_cnt][idx + 2] = val * MPU9250G_2000dps
                        else:
                            buf_f[smpl_cnt][idx + 2] = val * MPU9250A_16g

                    # 取得データ数をインクリメント
                    smpl_cnt += 1

                    # print("Data parsed successfully")
                else:
                    print("Buffer full. Skipping.")

            except Exception as e:
                print(f"\nData parse error at {smpl_cnt}: {e}")
                fail_cnt_head += 1
            finally:
                store = []
                state = 0
                

            if smpl_cnt >= maxSmpl:
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
print(f"\ntime: {e_time - p_time:.2f} [s]\n") 

# Function to create csv file 
writeCSV() 

# close serial port 
ser.close() 

print("number of data: ",smpl_cnt) 
print("number of byte fail: ",fail_cnt_byte)
print("number of header fail: ",fail_cnt_head)
print("END")