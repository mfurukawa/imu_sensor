/**
 * Masahiro FURUKAWA - m.furukawa@ist.osaka-u.ac.jp
 *
 * Dec 26, 2017
 * Aug 29, 2018 
 * Dec 17, 2019 @ Digital Low Pass Filter 5Hz -> No LPF
                @ ACC range 2G -> 4G
                @ GYRO range 250 -> 500 Degree per second
                @ Deleted magnet sensor checking 
                @ Set Acc Data Rates, Enable Acc LPF , Bandwidth 218Hz
                @ Use DLPF set Gyroscope bandwidth 5Hz, temperature bandwidth 5Hz
 * Mar 31, 2025 @ Two Channels (Ch2, Ch3), 1kHz for WHC2025
 *
 * MPU9250 9DoF Sensor (Extended to Ch1 ~ Ch4)
 *
 **/

#include "mbed.h"
#include "MPU9250.h"

/* MPU9250 Library
 *
 *  https://developer.mbed.org/users/kylongmu/code/MPU9250_SPI_Test/file/5839d1b118bc/main.cpp
 *
 *   MOSI (Master Out Slave In)  p5
 *   MISO (Master In Slave Out   p6
 *   SCK  (Serial Clock)         p7
 *   ~CS  (Chip Select)          p8 -> p30
 */

// define serial objects
Serial          pc(USBTX, USBRX);

Ticker          ticker;
Timer           timer;

#define nCh     4   // number of ch

float     SampleFreq = 1000.0f;   // [Hz]
unsigned int counter = 0;
unsigned int usCycle = 1000000/SampleFreq ;

int errFlag = 0;

//define the mpu9250 object
mpu9250_spi     *imu[nCh];

// define SPI object for imu objects
SPI             spi1(p5,  p6,  p7);
SPI             spi2(p11, p12, p13);

void init(void)
{
    pc.baud(921600); //921600 / 115200

    imu[0] = new mpu9250_spi(spi1, p30); // Ch1 on PCB
    imu[1] = new mpu9250_spi(spi1, p29); // Ch2 on PCB *spi1*
    imu[2] = new mpu9250_spi(spi2, p23); // Ch3 on PCB *spi2*
    imu[3] = new mpu9250_spi(spi2, p21); // Ch4 on PCB

    for(int i=0; i<nCh; i++) {

        imu[0]->deselect();
        imu[1]->deselect(); // Ch2 on PCB *spi1*
        imu[2]->deselect(); // Ch3 on PCB *spi2*
        imu[3]->deselect();
        
        imu[i]->select();

        //INIT the mpu9250
        //if(imu[i]->init(1,BITS_DLPF_CFG_188HZ)) 
        //if(imu[i]->init(1,BITS_DLPF_CFG_5HZ))
        if(imu[i]->init(1,BITS_DLPF_CFG_256HZ_NOLPF2))
        { 
            printf("\nCH %d ----- Couldn't initialize", i+1);
            wait(10);
        }
        //output the I2C address to know if SPI is working, it should be 104
        printf("\nCH %d ----- WHOAMI = 0x%2x",i+1, imu[i]->whoami());         
               
        if(imu[i]->whoami() != 0x71) {
            printf(" *** ERROR *** Did not respond correctly!");
            errFlag |= 0x01<<(i*2);
        }else{
            printf(" Acc_scale = %u[G] ",   imu[i]->set_acc_scale(BITS_FS_16G));        wait_ms(10);
            printf(" Gyro_scale = %u[DPS]", imu[i]->set_gyro_scale(BITS_FS_2000DPS));   wait_ms(10);
            //printf("AK8963 WHIAM=0x%2x\n",imu[i]->AK8963_whoami());
            
            //if(imu[i]->AK8963_whoami() != 0x48) {
            //    printf(" *** ERROR *** magnetrometer does not respond correctly!\n");
            //    errFlag |= 0x02<<(i*2);
            //}
            
            //imu[i]->AK8963_calib_Magnetometer();
            //wait_ms(10);
        }
    }
    imu[0]->deselect();     
    imu[1]->select();                           // Ch2 on PCB *spi1*
    imu[2]->select();                           // Ch3 on PCB *spi2*
    imu[3]->deselect();
}

void eventFunc(void)
{
    // limitation on sending bytes at 921600bps - 92bits(under 100us/sample)
    // requirement : 1kHz sampling
    // = 921.5 bits/sample
    // = 115.1 bytes/sample
    // = 50 bytes/axis (2byte/axis)
    
    // 2 byte * 6 axes * 2 ch = 24 bytes/sample

    // imu[0]->select();       imu[1]->deselect();
    // imu[2]->select();       imu[3]->deselect();
    
    // imu[0]->read_acc();    imu[0]->read_rot();            
    // imu[2]->read_acc();    imu[2]->read_rot();
    
    // imu[0]->deselect();    imu[1]->select();
    // imu[2]->deselect();    imu[3]->select();
    
    // imu[1]->read_acc();    imu[1]->read_rot();    
    // imu[3]->read_acc();    imu[3]->read_rot();
    
    imu[1]->read_acc();    imu[1]->read_rot();  // Ch2 on PCB *spi1*
    imu[2]->read_acc();    imu[2]->read_rot();  // Ch3 on PCB *spi2*

    // set header 
    putc(127, stdout); // DEL in ascii 
    putc(127, stdout); // DEL in ascii 

    // Ch2(imu[1]) on PCB *spi1*
    // Ch3(imu[2]) on PCB *spi2*
    for(int i=1; i<=2; i++) {
        // 2 byte * 6 axes * 2 ch = 24 bytes/sample
        for(int j=0; j<6; j++) putc(imu[i]->accelerometer_response[j], stdout);
        for(int j=0; j<6; j++) putc(imu[i]->gyroscope_response[j],     stdout);
    }
        
    // send time stamp // 4バイト（ビッグエンディアン）で送信
    //putc((counter >> 24) & 0xFF, stdout); // 最上位バイト
    putc((counter >> 16) & 0xFF, stdout); // 2番目のバイト
    putc((counter >> 8) & 0xFF, stdout);  // 3番目のバイト
    putc(counter & 0xFF, stdout);         // 最下位バイト

    counter++;
}

void set_acc_scale_all(int val){ 
    for(int i=0; i<nCh; i++) {
        imu[0]->deselect();
        imu[1]->deselect();
        imu[2]->deselect();
        imu[3]->deselect();
    
        imu[i]->select();
        imu[i]->set_acc_scale(val);
        wait_ms(2);
    }
}
void set_gyro_scale_all(int val){ 
    for(int i=0; i<nCh; i++) {
        imu[0]->deselect();
        imu[1]->deselect();
        imu[2]->deselect();
        imu[3]->deselect();
    
        imu[i]->select();
        imu[i]->set_gyro_scale(val);
        wait_ms(2);
    }
}
void set_LPF_all(int val){ 
    for(int i=0; i<nCh; i++) {
        imu[0]->deselect();
        imu[1]->deselect();
        imu[2]->deselect();
        imu[3]->deselect();
    
        imu[i]->select();
        imu[i]->init(1, val);  
        wait_ms(2);
    }
}

int main()
{
    // make instances and check sensors
    init();    

    char c;

    while(1) {
        if(pc.readable()) {
            c = pc.getc();

            switch(c){
                
                // reset
                case 'r':
                    ticker.detach();
                    break;
                
                // start sampling
                case 's': 
                    counter = 0;
                    ticker.attach_us(eventFunc, 1000000.0f/SampleFreq);
                    break;

                // set ACC range
                case 'A':
                    ticker.detach();        
                    c = pc.getc();  // read second byte
                    if('0' == c)  set_acc_scale_all(BITS_FS_2G);  
                    if('1' == c)  set_acc_scale_all(BITS_FS_4G);
                    if('2' == c)  set_acc_scale_all(BITS_FS_8G);
                    if('3' == c)  set_acc_scale_all(BITS_FS_16G); 
                    break;

                // set GYRO range
                case 'G':
                    ticker.detach();        
                    c = pc.getc();  // read second byte
                    if('0' == c)  set_gyro_scale_all(BITS_FS_250DPS);  
                    if('1' == c)  set_gyro_scale_all(BITS_FS_500DPS);
                    if('2' == c)  set_gyro_scale_all(BITS_FS_1000DPS);
                    if('3' == c)  set_gyro_scale_all(BITS_FS_2000DPS); 
                    break;

                // set LPF cutoff frequecy
                case 'L':
                    ticker.detach();        
                    c = pc.getc();  // read second byte
                    if('0' == c)  set_LPF_all(BITS_DLPF_CFG_256HZ_NOLPF2);  
                    if('1' == c)  set_LPF_all(BITS_DLPF_CFG_188HZ);
                    if('2' == c)  set_LPF_all(BITS_DLPF_CFG_98HZ);
                    if('3' == c)  set_LPF_all(BITS_DLPF_CFG_42HZ); 
                    if('4' == c)  set_LPF_all(BITS_DLPF_CFG_20HZ);  
                    if('5' == c)  set_LPF_all(BITS_DLPF_CFG_10HZ);
                    if('6' == c)  set_LPF_all(BITS_DLPF_CFG_5HZ);
                    if('7' == c)  set_LPF_all(BITS_DLPF_CFG_2100HZ_NOLPF); 
                    break;

            }
        }
    }
}
