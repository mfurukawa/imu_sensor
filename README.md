# imu_sensor
Eagle PCB, mbed source code included.
June 26, 2020
Masahiro Furukawa

mbed Protocol 
for 4Ch MPU-9250 Sensor Module 

mbed Source Code
https://os.mbed.com/users/mfurukawa/code/MPU-9250-Ch4_ACC_binary/

see main.cpp
https://os.mbed.com/users/mfurukawa/code/MPU-9250-Ch4_ACC_binary//file/818d64d37aeb/main.cpp/
How to check mbed response
Open terminal software.
Set baudrate as 921600bps.
Set linefeed as “LF” only.
Press reset button on mbed.
If you see some message, mbed works.
Press ‘s’ key and you will see the data stream
Press ‘r’ key and it will stop.
Protocol for ver2.0.2
Byte order is Big Endian.

for Acceleration  : 2 bytes = 16 bits describes 1 value

Higher Byte 
Ax, i : acceleration on axis X of ch i 
Ay, i : acceleration on axis Y of ch i 
Az, i : acceleration on axis Z of ch i 

Lower Byte
ax, i : acceleration on axis X of ch i 
ay, i : acceleration on axis Y of ch i 
az, i : acceleration on axis Z of ch i 

for Angular Velocity  : 2 bytes = 16 bits describes 1 value

Higher Byte
Wx, i : angular velocity on axis X of ch i 
Wy, i : angular velocity on axis Y of ch i 
Wz, i : angular velocity on axis Z of ch i 

Lower Byte
wx, i : angular velocity on axis X of ch i 
wy, i : angular velocity on axis Y of ch i 
wz, i : angular velocity on axis Z of ch i 

Byte Array (50 Bytes = 2 Byte * 3(xyz) *2(Acc, Gyro) * 4 (Ch) + 2(CR, LF) ) :

0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
Ax,1 
ax,1 
Ay,1 
ay,1 
Az,1 
az,1 
Wx,1 
wx,1
Wy,1
wy,1
Wz,1 
wz,1 
Ax,2 
ax,2 
Ay,2 
ay,2 
Az,2
az,2
Wx,2
wx,2
Wy,2
wy,2
Wz,2
wz,2
Ax,3
ax,3
Ay,3
ay,3
Az,3
az,3
Wx,3
wx,3
Wy,3
wy,3
Wz,3 
wz,3
Ax,4
ax,4
Ay,4
ay,4
Az,4 
az,4
Wx,4 
wx,4
Wy,4
wy,4
Wz,4
wz,4 
CR
LF





























MPU9250.h
符号なし整数8bit が加速度用に6つ(2つ(H, L)で1つの軸を表現)
uint8_t accelerometer_response[6]; //追加
uint8_t gyroscope_response[6]; //追加

MPU9250.h
加速度は2つ(H, L)のByteで1つの軸を表現している．つまり16bit(=2Byte)で1つの値を表現している．角速度の情報も同じ表現形式である．
#define MPUREG_ACCEL_XOUT_H 0x3B
#define MPUREG_ACCEL_XOUT_L 0x3C

#define MPUREG_ACCEL_YOUT_H 0x3D
#define MPUREG_ACCEL_YOUT_L 0x3E

#define MPUREG_ACCEL_ZOUT_H 0x3F
#define MPUREG_ACCEL_ZOUT_L 0x40


#define MPUREG_GYRO_XOUT_H 0x43
#define MPUREG_GYRO_XOUT_L 0x44

#define MPUREG_GYRO_YOUT_H 0x45
#define MPUREG_GYRO_YOUT_L 0x46

#define MPUREG_GYRO_ZOUT_H 0x47
#define MPUREG_GYRO_ZOUT_L 0x48

MPU9250.cpp
/*-----------------------------------------------------------------------------------------------
                                READ ACCELEROMETER
usage: call this function to read accelerometer data. Axis represents selected axis:
0 -> X axis
1 -> Y axis
2 -> Z axis
-----------------------------------------------------------------------------------------------*/

void mpu9250_spi::read_acc()
{
    //int16_t bit_data;
//    float data;
//    int i;
    ReadRegs(MPUREG_ACCEL_XOUT_H,accelerometer_response,6);    
//    for(i=0; i<3; i++) {
//        bit_data=((int16_t)accelerometer_response[i*2]<<8)|accelerometer_response[i*2+1];
//        data=(float)bit_data;
//        accelerometer_data[i]=data/acc_divider;
//        
//    }
    
}


main.cpp
void eventFunc(void)
{
  ...
    for(int i=0; i<nCh; i++) {
        for(int j=0; j<6; j++) putc(imu[i]->accelerometer_response[j], stdout);
        for(int j=0; j<6; j++) putc(imu[i]->gyroscope_response[j],     stdout);
    }
    putc(13, stdout);  //0x0d = 13(10) CR（復帰）
    putc(10, stdout);  //0x0a = 10(10) LF（改行）
}

How to read byte stream with Python
https://qiita.com/keitasumiya/items/25a707c37a73bfd95bac

