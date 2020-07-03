#from https://github.com/mfurukawa/imu_sensor/tree/master/src/Python 
#Yuto Nakayachi 
# July 01, 2020 


from __future__ import unicode_literals ,print_function
import serial 
from time import sleep 
import numpy as np 
import matplotlib.pyplot as plt
import io 
import csv 
import time 
import datetime 


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

numVariable = 24 # 4ch * 6acc 
minuteLength = 25 
smplHz = 500 
smpl_cnt = 0
xl = 500
yl=MPU9250A_4g*35000

buf = [[0 for i in range(numVariable + 2)] for j in range(smplHz*60*minuteLength)] 
buf_f = [[0 for i in range(numVariable + 2)] for j in range(smplHz*60*minuteLength)]

ser = serial.Serial("COM3",921600,timeout=1) 

if ser.is_open:
    print("start serial connection") 
else:
    print("PORT ERROR") 
    ser.close() 
    exit() 

def writeCSV():
    global ser 
    global smpl_cnt 
    global buf 
    global buf_f 
    ser.write(b'r') 
    print("start create csv file") 
    head = ["sample_cc","ms","ACC_X1","ACC_Y1","ACC_Z1","GYRO_X1","GYRO_Y1","GYRO_Z1","ACC_X2","ACC_Y2","ACC_Z2","GYRO_X2","GYRO_Y2","GYRO_Z2","ACC_X3","ACC_Y3","ACC_Z3","GYRO_X3","GYRO_Y3","GYRO_Z3","ACC_X4","ACC_Y4","ACC_Z4","GYRO_X4","GYRO_Y4","GYRO_Z4"]
    dt_now = datetime.datetime.now() 
    year = dt_now.year 
    month = dt_now.month 
    day = dt_now.day 
    hour = dt_now.hour 
    minute = dt_now.minute 
    t = str(year)+str(month)+str(day)+str(hour)+str(minute)
    title_int = "test"+str(t)+"_int"+".csv"
    FILE_int = open(title_int,"w",newline="") 
    title_float="test"+str(t)+"_float"+".csv" 
    FILE_float = open(title_float,"w",newline="")    
    wi = csv.writer(FILE_int)
    wi.writerow(head)
    wf = csv.writer(FILE_float) 
    wf.writerow(head) 
    for i in range(smpl_cnt):
        wi.writerow(buf[i]) 
        wf.writerow(buf_f[i]) 
    FILE_int.close() 
    FILE_float.close() 
    print("done create csv file") 
       
def readByte():
    global ser 
    global smpl_cnt 
    global buf 
    global buf_f  
    global xl 
    global yl 

    ser.write(b"r") 
    time.sleep(0.01)
    ser.write(b"s") 
    time.sleep(0.01) 

    while(1):
        res = ser.readline() 

        if len(res)==50:

            ################################################################
            #リアルタイムグラフ描写の部分(1/2)
            if smpl_cnt==0:
                fig,ax = plt.subplots(1,1) 
                ax.set_ylim((-yl,yl)) 
                x=np.arange(0,xl,1) 
                y = [] 
                for i in range(xl):
                    y.append(0) 
                lines, = ax.plot(x,y) 
                fig.show() 
            ##################################################################

            #add time stamp 
            if smpl_cnt==0:
                start_time = time.time() * 1000 
                tmp_time = start_time - start_time 
            else:
                now_time = time.time() * 1000 
                tmp_time = now_time - start_time 
            buf[smpl_cnt][1] = int(tmp_time) 
            buf_f[smpl_cnt][1] = int(tmp_time) 

            buf[smpl_cnt][0] = smpl_cnt
            buf_f[smpl_cnt][0] = smpl_cnt

            for i in range(0,48,2):
                res2 = res[i:i+2] 
                val = int.from_bytes(res2,'big',signed=True) 

                num = i%12 
                ch = i//12 
                buf[smpl_cnt][6*ch + num//2 + 2]=val 
                if (num//2)>=3:
                    buf_f[smpl_cnt][6*ch + num//2 + 2]=val * MPU9250G_500dps
                else:
                    buf_f[smpl_cnt][6*ch + num//2 + 2]=val * MPU9250A_4g


            print (
                "{:+.3f}".format(buf_f[smpl_cnt][2]) ,      "{:+.3f}".format(buf_f[smpl_cnt][3]) ,      "{:+.3f}".format(buf_f[smpl_cnt][4]) , 
                "{:+.3f}".format(buf_f[smpl_cnt][5]) ,  "{:+.3f}".format(buf_f[smpl_cnt][6]) ,  "{:+.3f}".format(buf_f[smpl_cnt][7]) ,'\t',
                
                "{:+.3f}".format(buf_f[smpl_cnt][8]) ,      "{:+.3f}".format(buf_f[smpl_cnt][9]) ,      "{:+.3f}".format(buf_f[smpl_cnt][10]) , 
                "{:+.3f}".format(buf_f[smpl_cnt][11]) ,  "{:+.3f}".format(buf_f[smpl_cnt][12]) ,  "{:+.3f}".format(buf_f[smpl_cnt][13]) , '\t',
                
                "{:+.3f}".format(buf_f[smpl_cnt][14]) ,      "{:+.3f}".format(buf_f[smpl_cnt][15]) ,      "{:+.3f}".format(buf_f[smpl_cnt][16]) , 
                "{:+.3f}".format(buf_f[smpl_cnt][17]) ,  "{:+.3f}".format(buf_f[smpl_cnt][18]) ,  "{:+.3f}".format(buf_f[smpl_cnt][19]) , '\t',
                
                "{:+.3f}".format(buf_f[smpl_cnt][20]) ,      "{:+.3f}".format(buf_f[smpl_cnt][21]) ,      "{:+.3f}".format(buf_f[smpl_cnt][22]) , 
                "{:+.3f}".format(buf_f[smpl_cnt][23]) ,  "{:+.3f}".format(buf_f[smpl_cnt][24]) ,  "{:+.3f}".format(buf_f[smpl_cnt][25]) ) 

            ########################################################
            #リアルタイムグラフ描写の部分(2/2)
            if smpl_cnt>=xl:
                x += 1 
                y=[]
                for i in range(x.min(),x.max()+1):
                    ax1 = buf_f[i][2]
                    y.append(ax1) 
                lines.set_data(x,y) 
                ax.set_xlim((x.min(),x.max())) 
                ax.set_ylim((-yl,yl)) 
            else:
                y=[]
                for i in range(x.min(),x.max()+1):
                    ax1 = buf_f[i][2] 
                    y.append(ax1) 
                lines.set_data(x,y)
                ax.set_xlim((x.min(),x.max())) 
                ax.set_ylim((-yl,yl)) 
            plt.pause(.001) 
            ########################################################

            smpl_cnt += 1
        else:
            continue 

        if smpl_cnt>2000:
            break 

print("ready? --> press s key") 
while(1):
    ready_s = input() 
    if ready_s == "s":
        break 
    if ready_s == "r":
        print("over") 
        ser.close()
        exit() 

readByte()

writeCSV() 

ser.close() 
print("number of data:",smpl_cnt) 
print("END")
