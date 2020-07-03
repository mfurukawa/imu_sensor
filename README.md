# imu_sensor
Eagle PCB, mbed source code included.

- Juky  3, 2020 - added, Python, Unity, C# sample
- June 26, 2020 - created 

Masahiro Furukawa


# mbed Protocol 


# for 4Ch MPU-9250 Sensor Module 

mbed Source Code

[https://os.mbed.com/users/mfurukawa/code/MPU-9250-Ch4_ACC_binary/](https://os.mbed.com/users/mfurukawa/code/MPU-9250-Ch4_ACC_binary/)

see main.cpp

[https://os.mbed.com/users/mfurukawa/code/MPU-9250-Ch4_ACC_binary//file/818d64d37aeb/main.cpp/](https://os.mbed.com/users/mfurukawa/code/MPU-9250-Ch4_ACC_binary//file/818d64d37aeb/main.cpp/)


# How to check mbed response



1. Open terminal software.
2. Set baudrate as 921600bps.
3. Set linefeed as “LF” only.
4. Press reset button on mbed.
5. If you see some message, mbed works.
6. Press ‘s’ key and you will see the data stream
7. Press ‘r’ key and it will stop.


# Protocol for ver2.0.2

Byte order is **Big** Endian

for Acceleration  : 2 bytes = 16 bits describes 1 value


Higher Byte 

A<sub>x, i</sub> : acceleration on axis X of ch i

A<sub>y, i</sub> : acceleration on axis Y of ch i 

A<sub>z, i</sub> : acceleration on axis Y of ch i 


Lower Byte

a<sub>x, i</sub> : acceleration on axis X of ch i 

a<sub>y, i</sub> : acceleration on axis Y of ch i 

a<sub>z, i</sub> : acceleration on axis Z of ch i 

for Angular Velocity  : 2 bytes = 16 bits describes 1 value


Higher Byte

W<sub>x, i</sub> : angular velocity on axis X of ch i 

W<sub>y, i</sub> : angular velocity on axis Y of ch i 

W<sub>z, i</sub> : angular velocity on axis Z of ch i 


Lower Byte


w<sub>x, i</sub> : angular velocity on axis X of ch i

w<sub>y, i</sub> : angular velocity on axis Y of ch i

w<sub>z, i</sub> : angular velocity on axis Z of ch i

Byte Array (50 Bytes = 2 Byte * 3(xyz) *2(Acc, Gyro) * 4 (Ch) + 2(CR, LF) ) :


<table>
  <tr>
   <td>0
   </td>
   <td>1
   </td>
   <td>2
   </td>
   <td>3
   </td>
   <td>4
   </td>
   <td>5
   </td>
   <td>6
   </td>
   <td>7
   </td>
   <td>8
   </td>
   <td>9
   </td>
   <td>10
   </td>
   <td>11
   </td>
   <td>12
   </td>
   <td>13
   </td>
   <td>14
   </td>
   <td>15
   </td>
  </tr>
  <tr>
   <td>A<sub>x,1</sub> 
   </td>
   <td>a<sub>x,1</sub> 
   </td>
   <td>A<sub>y,1</sub> 
   </td>
   <td>a<sub>y,1</sub> 
   </td>
   <td>A<sub>z,1</sub> 
   </td>
   <td>a<sub>z,1</sub> 
   </td>
   <td>W<sub>x,1</sub> 
   </td>
   <td>w<sub>x,1</sub>
   </td>
   <td>W<sub>y,1</sub>
   </td>
   <td>w<sub>y,1</sub>
   </td>
   <td>W<sub>z,1</sub> 
   </td>
   <td>w<sub>z,1</sub> 
   </td>
   <td>A<sub>x,<em>2 </em></sub>
   </td>
   <td>a<sub>x,<em>2 </em></sub>
   </td>
   <td>A<sub>y,<em>2 </em></sub>
   </td>
   <td>a<sub>y,<em>2 </em></sub>
   </td>
  </tr>
  <tr>
   <td>A<sub>z,<em>2</em></sub>
   </td>
   <td>a<sub>z,<em>2</em></sub>
   </td>
   <td>W<sub>x,<em>2</em></sub>
   </td>
   <td>w<sub>x,<em>2</em></sub>
   </td>
   <td>W<sub>y,<em>2</em></sub>
   </td>
   <td>w<sub>y,<em>2</em></sub>
   </td>
   <td>W<sub>z,2</sub>
   </td>
   <td>w<sub>z,2</sub>
   </td>
   <td>A<sub>x,3</sub>
   </td>
   <td>a<sub>x,3</sub>
   </td>
   <td>A<sub>y,3</sub>
   </td>
   <td>a<sub>y,3</sub>
   </td>
   <td>A<sub>z,3</sub>
   </td>
   <td>a<sub>z,3</sub>
   </td>
   <td>W<sub>x,3</sub>
   </td>
   <td>w<sub>x,3</sub>
   </td>
  </tr>
  <tr>
   <td>W<sub>y,3</sub>
   </td>
   <td>w<sub>y,3</sub>
   </td>
   <td>W<sub>z,3</sub> 
   </td>
   <td>w<sub>z,3</sub>
   </td>
   <td>A<sub>x,<em>4</em></sub>
   </td>
   <td>a<sub>x,<em>4</em></sub>
   </td>
   <td>A<sub>y,<em>4</em></sub>
   </td>
   <td>a<sub>y,<em>4</em></sub>
   </td>
   <td>A<sub>z,4</sub> 
   </td>
   <td>a<sub>z,4</sub>
   </td>
   <td>W<sub>x,4</sub> 
   </td>
   <td>w<sub>x,4</sub>
   </td>
   <td>W<sub>y,4</sub>
   </td>
   <td>w<sub>y,4</sub>
   </td>
   <td>W<sub>z,4</sub>
   </td>
   <td>w<sub>z,4</sub> 
   </td>
  </tr>
  <tr>
   <td>CR
   </td>
   <td>LF
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
   <td>
   </td>
  </tr>
</table>


## MPU9250.h

16bits(= 2 Bytes) represents one value. Angular velocity represents in the same way. The address below shows data address in MPU-9250 IMU sensor.

> ```
> #define MPUREG_ACCEL_XOUT_H 0x3B
> #define MPUREG_ACCEL_XOUT_L 0x3C
> 
> #define MPUREG_ACCEL_YOUT_H 0x3D
> #define MPUREG_ACCEL_YOUT_L 0x3E
> 
> #define MPUREG_ACCEL_ZOUT_H 0x3F
> #define MPUREG_ACCEL_ZOUT_L 0x40
> 
> 
> #define MPUREG_GYRO_XOUT_H 0x43
> #define MPUREG_GYRO_XOUT_L 0x44
> 
> #define MPUREG_GYRO_YOUT_H 0x45
> #define MPUREG_GYRO_YOUT_L 0x46
> 
> #define MPUREG_GYRO_ZOUT_H 0x47
> #define MPUREG_GYRO_ZOUT_L 0x48
> ```

Thus six unsigned integer (8bit) variales represent three accelerations. Also six unsigned integer (8bit) variables represent three angular velocity. 


> ```
> uint8_t accelerometer_response[6]; 
> uint8_t gyroscope_response[6]; 
> ```


## MPU9250.cpp

> ```
> /*-----------------------------------------------------------------------------------------------
>                                 READ ACCELEROMETER
> usage: call this function to read accelerometer data. Axis represents selected axis:
> 0 -> X axis
> 1 -> Y axis
> > 2 -> Z axis
> 
> void mpu9250_spi::read_acc()
> {
>     //int16_t bit_data;
> //    float data;
> //    int i;
>     ReadRegs(MPUREG_ACCEL_XOUT_H,accelerometer_response,6);    
> //    for(i=0; i<3; i++) {
> //        bit_data=((int16_t)accelerometer_response[i*2]<<8)|accelerometer_response[i*2+1];
> //        data=(float)bit_data;
> //        accelerometer_data[i]=data/acc_divider;
> //        
> //    }
>     
> }
> ```


## main.cpp


> ```
> void eventFunc(void)
> {
>   ...
>     for(int i=0; i<nCh; i++) {
>         for(int j=0; j<6; j++) putc(imu[i]->accelerometer_response[j], stdout);
>         for(int j=0; j<6; j++) putc(imu[i]->gyroscope_response[j],     stdout);
>     }
>     putc(13, stdout);  //0x0d = 13(10) CR（復帰）
>     putc(10, stdout);  //0x0a = 10(10) LF（改行）
> }
> ```


# References

## How to read byte stream with Python

[https://qiita.com/keitasumiya/items/25a707c37a73bfd95bac](https://qiita.com/keitasumiya/items/25a707c37a73bfd95bac)
