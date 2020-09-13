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
Timer           sp_time;
 
#define SampleFreq   500   // [Hz]
#define nCh            4   // number of ch
 
unsigned int counter = 0;
unsigned int usCycle = 1000000/SampleFreq ;
 
int errFlag = 0;
int past_time = 0;
int tmp_time = 0;
int res_time = 0;
 
//define the mpu9250 object
mpu9250_spi     *imu[nCh];
 
// define SPI object for imu objects
SPI             spi1(p5,  p6,  p7);
SPI             spi2(p11, p12, p13);
 
void init(void)
{
    pc.baud(921600); //921600 / 115200
 
    printf("\nrev Dec 17, 2019 for KOMATSU Experiment by Masahiro Furukawa\n\n");  
    
    imu[3] = new mpu9250_spi(spi2, p21);
    imu[2] = new mpu9250_spi(spi2, p23);
    imu[1] = new mpu9250_spi(spi1, p29);
    imu[0] = new mpu9250_spi(spi1, p30);
 
    for(int i=0; i<nCh; i++) {
 
        imu[0]->deselect();
        imu[1]->deselect();
        imu[2]->deselect();
        imu[3]->deselect();
        
        imu[i]->select();
 
        //INIT the mpu9250
        //if(imu[i]->init(1,BITS_DLPF_CFG_188HZ)) 
        //if(imu[i]->init(1,BITS_DLPF_CFG_5HZ))
        if(imu[i]->init(1,BITS_DLPF_CFG_256HZ_NOLPF2))
        { 
            printf("\nCH %d\n\nCouldn't initialize MPU9250 via SPI!", i+1);
            wait(90);
        }
        
        //output the I2C address to know if SPI is working, it should be 104
        printf("\nCH %d\nWHOAMI=0x%2x\n",i+1, imu[i]->whoami());         
               
        if(imu[i]->whoami() != 0x71) {
            printf(" *** ERROR *** acc and gyro sensor does not respond correctly!\n");
            errFlag |= 0x01<<(i*2);
        }
 
        printf("Gyro_scale=%u[DPS]\n",imu[i]->set_gyro_scale(BITS_FS_500DPS));    //Set 500DPS scale range for gyros    //0706 wada 500to2000
        wait_ms(20);
        
        printf("Acc_scale=%u[G]\n",imu[i]->set_acc_scale(BITS_FS_4G));          //Set 4G scale range for accs        //0706 wada 4to16
        wait_ms(20);
        sp_time.start();
        past_time=sp_time.read_ms();
        //printf("AK8963 WHIAM=0x%2x\n",imu[i]->AK8963_whoami());
        
        //if(imu[i]->AK8963_whoami() != 0x48) {
        //    printf(" *** ERROR *** magnetrometer does not respond correctly!\n");
        //    errFlag |= 0x02<<(i*2);
        //}
        
        //imu[i]->AK8963_calib_Magnetometer();
        //wait_ms(10);
    }
}
 
void eventFunc(void)
{
    // limitation on sending bytes at 921600bps - 92bits(under 100us/sample)
    // requirement : 1kHz sampling
    // = 921.5 bits/sample
    // = 115.1 bytes/sample
    // = 50 bytes/axis (2byte/axis)
    
    // 1 byte (Header)
    // 2 byte * 6 axes * 4 ch = 48 bytes/sample
    // 1 byte (Time value) 
 
    //for(int i=0; i<nCh; i++) {
        
        imu[0]->select();
        imu[1]->deselect();
        imu[2]->select();
        imu[3]->deselect();
        
        imu[0]->read_acc();
        imu[0]->read_rot();
                
        imu[2]->read_acc();
        imu[2]->read_rot();
        
        imu[0]->deselect();
        imu[1]->select();
        imu[2]->deselect();
        imu[3]->select();
        
        imu[1]->read_acc();
        imu[1]->read_rot();
        
        imu[3]->read_acc();
        imu[3]->read_rot();
    //}
    
    // set header 
    putc(42,stdout); // * 
    
    for(int i=0; i<nCh; i++) {
        for(int j=0; j<6; j++) putc(imu[i]->accelerometer_response[j], stdout);
        for(int j=0; j<6; j++) putc(imu[i]->gyroscope_response[j],     stdout);
        /*
        printf("%s,%s,%s,%s,%s,%s",imu[i]->accelerometer_response[0],imu[i]->accelerometer_response[1],imu[i]->accelerometer_response[2],
        imu[i]->accelerometer_response[3],imu[i]->accelerometer_response[4],imu[i]->accelerometer_response[5],
        imu[i]->gyroscope_response[0],imu[i]->gyroscope_response[1],imu[i]->gyroscope_response[2],imu[i]->gyroscope_response[3],imu[i]->gyroscope_response[4],
        imu[i]->gyroscope_response[5]);
        */
        //pc.printf("hello");
    }
    tmp_time = sp_time.read_ms();
    res_time = tmp_time - past_time;
    past_time = tmp_time;
    putc(res_time,stdout); //Time Value 
    putc(13, stdout);  //0x0d CR（復帰）
    putc(10, stdout);  //0x0a LF（改行）
//    printf("\r\n");
 
}
 
int main()
{
    // make instances and check sensors
    init();
    
    char c;
 
    while(1) {
        if(pc.readable()) {
            c = pc.getc();
 
            if(c == 'r') {
                ticker.detach();
            } else if(c == 's') {
                ticker.attach_us(eventFunc, 1000000.0f/SampleFreq);
            }
        }
    }
}