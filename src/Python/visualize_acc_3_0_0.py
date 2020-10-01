#Acceleration and angular acceleration visualization program
# July 7, 2020 
# Yuto Nakayachi 

import sys 
import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 


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



yl=MPU9250A_4g * 35000
yr=MPU9250G_500dps * 35000


args = sys.argv 
title = args[1] 

data = pd.read_csv(title,encoding="UTF-8")
xdata = data["ms"] 
print(xdata.head())
data=data.drop(data.columns[[0,1]],axis=1)
print(data.head())

data1 = data.drop(data.columns[[6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]],axis=1) #CH1
data2 = data.drop(data.columns[[0,1,2,3,4,5,12,13,14,15,16,17,18,19,20,21,22,23]],axis=1) #CH2
data3 = data.drop(data.columns[[0,1,2,3,4,5,6,7,8,9,10,11,18,19,20,21,22,23]],axis=1) #CH3
data4 = data.drop(data.columns[[0,1,2,3,4,5, 6,7,8,9,10,11, 12,13,14,15,16,17]],axis=1) #CH4 
print(data1.head())
print(data2.head()) 
print(data3.head())  
print(data4.head()) 

#CH1 
fig1,(axeL1,axeR1) = plt.subplots(ncols=2) 
# ms -> s 
xdata = xdata / 1000

axeL1.plot(xdata,data1["ACC_X1"],label="ACC_X") 
axeL1.plot(xdata,data1["ACC_Y1"],label="ACC_Y")
axeL1.plot(xdata,data1["ACC_Z1"],label="ACC_Z")
axeR1.plot(xdata,data1["GYRO_X1"],label="GYRO_X")
axeR1.plot(xdata,data1["GYRO_Y1"],label="GYRO_Y")
axeR1.plot(xdata,data1["GYRO_Z1"],label="GYRO_Z")
axeL1.set_title("CH1 ACC")
axeR1.set_title("CH1 GYRO") 
axeL1.set_xlabel("s")
axeR1.set_xlabel("s")  
axeL1.set_ylabel("Value(G)") 
axeR1.set_ylabel("Value(dps)") 
axeL1.set_ylim(-yl,yl)
axeR1.set_ylim(-yr,yr) 
axeL1.legend() 
axeR1.legend()

#CH2
fig2,(axeL2,axeR2) = plt.subplots(ncols=2) 

axeL2.plot(xdata,data2["ACC_X2"],label="ACC_X") 
axeL2.plot(xdata,data2["ACC_Y2"],label="ACC_Y")
axeL2.plot(xdata,data2["ACC_Z2"],label="ACC_Z")
axeR2.plot(xdata,data2["GYRO_X2"],label="GYRO_X")
axeR2.plot(xdata,data2["GYRO_Y2"],label="GYRO_Y")
axeR2.plot(xdata,data2["GYRO_Z2"],label="GYRO_Z")
axeL2.set_title("CH2 ACC")
axeR2.set_title("CH2 GYRO") 
axeL2.set_xlabel("s")
axeR2.set_xlabel("s")  
axeL2.set_ylabel("Value(G)") 
axeR2.set_ylabel("Value(dps)") 
axeL2.set_ylim(-yl,yl)
axeR2.set_ylim(-yr,yr) 
axeL2.legend() 
axeR2.legend()

#CH3 
fig3,(axeL3,axeR3) = plt.subplots(ncols=2) 

axeL3.plot(xdata,data3["ACC_X3"],label="ACC_X") 
axeL3.plot(xdata,data3["ACC_Y3"],label="ACC_Y")
axeL3.plot(xdata,data3["ACC_Z3"],label="ACC_Z")
axeR3.plot(xdata,data3["GYRO_X3"],label="GYRO_X")
axeR3.plot(xdata,data3["GYRO_Y3"],label="GYRO_Y")
axeR3.plot(xdata,data3["GYRO_Z3"],label="GYRO_Z")
axeL3.set_title("CH3 ACC")
axeR3.set_title("CH3 GYRO") 
axeL3.set_xlabel("s")
axeR3.set_xlabel("s")  
axeL3.set_ylabel("Value(G)") 
axeR3.set_ylabel("Value(dps)") 
axeL3.set_ylim(-yl,yl)
axeR3.set_ylim(-yr,yr) 
axeL3.legend() 
axeR3.legend()

#CH4
fig4,(axeL4,axeR4) = plt.subplots(ncols=2) 

axeL4.plot(xdata,data4["ACC_X4"],label="ACC_X") 
axeL4.plot(xdata,data4["ACC_Y4"],label="ACC_Y")
axeL4.plot(xdata,data4["ACC_Z4"],label="ACC_Z")
axeR4.plot(xdata,data4["GYRO_X4"],label="GYRO_X")
axeR4.plot(xdata,data4["GYRO_Y4"],label="GYRO_Y")
axeR4.plot(xdata,data4["GYRO_Z4"],label="GYRO_Z")
axeL4.set_title("CH4 ACC")
axeR4.set_title("CH4 GYRO") 
axeL4.set_xlabel("s")
axeR4.set_xlabel("s")  
axeL4.set_ylabel("Value(G)") 
axeR4.set_ylabel("Value(dps)") 
axeL4.set_ylim(-yl,yl)
axeR4.set_ylim(-yr,yr) 
axeL4.legend() 
axeR4.legend()

plt.show()