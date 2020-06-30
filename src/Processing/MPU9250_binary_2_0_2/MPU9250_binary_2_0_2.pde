// Masahiro Furukawa
// updated : May 28, 2020 sampled time [ms] bug fixed
// updated : Aug 29, 2018
// updated : Aug 7, 2018
//


//        printf("Gyro_scale=%u\n",imu[i]->set_gyro_scale(BITS_FS_250DPS));    //Set 500DPS scale range for gyros    //0706 wada 500to2000

//        printf("Acc_scale=%u\n",imu[i]->set_acc_scale(BITS_FS_2G));     


// https://os.mbed.com/compiler/#nav:/MPU-9250-Ch2_ACC_binary/MPU9250_SPI/MPU9250.h;
/* ---- Sensitivity --------------------------------------------------------- */

float MPU9250A_2g  =     0.000061035156; // 0.000061035156 g/LSB
float MPU9250A_4g  =     0.000122070312; // 0.000122070312 g/LSB
float MPU9250A_8g  =     0.000244140625; // 0.000244140625 g/LSB
float MPU9250A_16g =     0.000488281250; // 0.000488281250 g/LSB

float MPU9250G_250dps  = 0.007633587786; // 0.007633587786 dps/LSB
float MPU9250G_500dps  = 0.015267175572; // 0.015267175572 dps/LSB
float MPU9250G_1000dps = 0.030487804878; // 0.030487804878 dps/LSB
float MPU9250G_2000dps = 0.060975609756; // 0.060975609756 dps/LSB

float MPU9250M_4800uT  = 0.6;            // 0.6 uT/LSB

float MPU9250T_85degC  = 0.002995177763; // 0.002995177763 degC/LSB
float Magnetometer_Sensitivity_Scale_Factor = 0.15;

// this code require you to install Proessing Library named as follows:
// [1] "Minim"
// [2] "giCentre"
// [3] "controlp5"
//
// References:
// [1] http://www.d-improvement.jp/learning/processing/2010-b/10.html
//
// [2] https://www.gicentre.net/utils/chart
// [2] http://gicentre.org/utils/reference/
//
// [3] http://www.sojamo.de/libraries/controlP5/
// [3] http://aa-deb.hatenablog.com/entry/2016/11/04/230332


import processing.sound.*;
import processing.serial.*;
import java.io.*;

Serial myPort;      // The serial port

static int nCh = 4;
static int byteLength = 12 * 4  + 2;  // 4 timestamp 4ch \r\n
static int minuteLength = 25 ;
static int smplHz = 500 ;

static boolean isWin = false;//(System.getProperty("os.name").contains("Win"));

int p = 0;
byte[]   buf     = new byte[byteLength];
byte[]   inByte  = new byte[byteLength];
byte[][] inBytes = new byte[smplHz*60*minuteLength][byteLength + 4]; // with time stamp

boolean isRecording = false;
boolean isFull = false;

int lf=10; // ASCII linefeed
int startLines = 0;
int trialNo =1;
int time = 0;
int time0 = 0;
String filename;


int[][][] vals;

SqrOsc sqr;

void setup() 
{  
  inByte[0] = byte(0);

  vals = new int[width][4][3];

  //lights();
  //background(0);
  //size(640, 360, P3D);
  //// Change height of the camera with mouseY
  //camera(0.0, 130.0, -30.0, // eyeX, eyeY, eyeZ
  //       80.0, 0.0, 0.0, // centerX, centerY, centerZ
  //       0.0, 0.0, 1.0); // upX, upY, upZ

  size(1200, 480);


  // for mac
  try {

    myPort = new Serial(this, "/dev/tty.usbmodem14202", 921600);
    myPort.bufferUntil(lf);
  }
  catch(Exception e) {
    //e.printStackTrace();
    
    int idx = Serial.list().length - 1;
    String portName = Serial.list()[idx];
    myPort = new Serial(this, portName, 921600);
    myPort.bufferUntil(lf);
  }
  
  
  serialPurge();


  sqr = new SqrOsc(this);

  //Start the Sine Oscillator. There will be no sound in the beginning
  //unless the mouse enters the   
  sqr.play();
  sqr.freq(1600);
  sqr.amp(0.001);
  sqr.pan(0);


  println("ready");
}


void serialPurge()
{
  while (myPort.available() > 0) {
    myPort.read();
  }
  // serial buf pointer
  p = 0;
}

void serialEvent(Serial q) 
{    

  if (smplHz*60*minuteLength < startLines + 10)
  {
    writeFile();
    return;
  }
  // read buffer
  int byteCount = myPort.readBytes(buf); 

  // ignore initialization message
  if (byteCount > byteLength) return; // purge

  // ignore initialization message
  if (p + byteCount > byteLength) 
  {
    p = 0;
    return;
  } else {
    // concatenate several pieces of received data
    arrayCopy(buf, 0, inByte, p, byteCount);
    p = p + byteCount;
  }
  //print(byteCount + " ");


  if (isRecording && p == byteLength) 
  {
    // println("all 26 byte receieved");

    // reset serial buffer pointer  
    p = 0;

    // initial time stamp
    if (startLines == 0) time0 =  millis();

    // get time stamp
    time = millis() - time0;
    // the beginning 2 bytes are time stamp described in Milli Seconds 
    inBytes[startLines][0] = byte(time>>24 & 0xFF); // big endien
    inBytes[startLines][1] = byte(time>>16 & 0xFF); // big endien
    inBytes[startLines][2] = byte(time>>8  & 0xFF); // big endien
    inBytes[startLines][3] = byte(time     & 0xFF); // big endien

    // the next 6 bytes are acceleration of each two bytes in XYZ order. data type assumes int16 per each.
    // the next 6 bytes are gyro of each two bytes in XYZ order. data type assumes int16 per each. 
    // arrayCopy(src, srcPosition, dst, dstPosition, length)
    arrayCopy(inByte, 0, inBytes[startLines], 4, byteLength);


    // show state in console
    // comment out the below line!
    //println(startLines, time, byteCount);

    startLines++;
  }
}

void writeFile()
{      
  if (isRecording == false) return;

  isRecording = false;
  isFull = false;
  myPort.write('r');

  sqr.amp(1);      
  delay(250);
  sqr.amp(0.001);  
  delay(50);
  sqr.amp(1);      
  delay(250);
  sqr.amp(0.001);  
  delay(50);
  sqr.amp(1);      
  delay(250);
  sqr.amp(0.001);
  // serial buf pointer
  p = 0; 

  // set file name
  filename = nf(year(), 4) + nf(month(), 2) + nf(day(), 2) + nf(hour(), 2) + nf(minute(), 2) + "trial_" + nf(trialNo++);

  // binary data structure by Masahiro Furukawa Aug 29, 2018
  // ** big endien **

  //  -- time stamp (4 byte) --
  //  [TIME_STAMP_IN_MILLISECOND_H3]
  //  [TIME_STAMP_IN_MILLISECOND_H2]
  //  [TIME_STAMP_IN_MILLISECOND_H1]
  //  [TIME_STAMP_IN_MILLISECOND_H0]

  //  --  ch1 (12 byte) --
  //  [ACC_X_H]       
  //  [ACC_X_L]
  //  [ACC_Y_H]
  //  [ACC_Y_L]
  //  [ACC_Z_H]
  //  [ACC_Z_L]

  //  [GYR_X_H]
  //  [GYR_X_L]
  //  [GYR_Y_H]
  //  [GYR_Y_L]
  //  [GYR_Z_H]
  //  [GYR_Z_L]

  //  --  ch2 (12 byte) --
  //  [ACC_X_H]       
  //  [ACC_X_L]
  //  [ACC_Y_H]
  //  [ACC_Y_L]
  //  [ACC_Z_H]
  //  [ACC_Z_L]

  //  [GYR_X_H]
  //  [GYR_X_L]
  //  [GYR_Y_H]
  //  [GYR_Y_L]
  //  [GYR_Z_H]
  //  [GYR_Z_L]

  //  --  ch3 (12 byte) --
  //  [ACC_X_H]       
  //  [ACC_X_L]
  //  [ACC_Y_H]
  //  [ACC_Y_L]
  //  [ACC_Z_H]
  //  [ACC_Z_L]

  //  [GYR_X_H]
  //  [GYR_X_L]
  //  [GYR_Y_H]
  //  [GYR_Y_L]
  //  [GYR_Z_H]
  //  [GYR_Z_L]

  //  --  ch4 (12 byte) --
  //  [ACC_X_H]       
  //  [ACC_X_L]
  //  [ACC_Y_H]
  //  [ACC_Y_L]
  //  [ACC_Z_H]
  //  [ACC_Z_L]

  //  [GYR_X_H]
  //  [GYR_X_L]
  //  [GYR_Y_H]
  //  [GYR_Y_L]
  //  [GYR_Z_H]
  //  [GYR_Z_L]

  //  -- delimiter (2 byte) -- 
  //  [CR]
  //  [LF]

  try {

    // binary file

    OutputStream os = new FileOutputStream( savePath(filename + ".bin") );
    for (int i=0; i<startLines-1; i++) 
      os.write(inBytes[i]); 
    os.close();

    // csv file // int

    String title = "sample_count, ms, RAW_Acc X1, RAW_Acc Y1, RAW_Acc Z1, RAW_Gyro X1, RAW_Gyro Y1, RAW_Gyro Z1, RAW_Acc X2, RAW_Acc Y2, RAW_Acc Z2, RAW_Gyro X2, RAW_Gyro Y2, RAW_Gyro Z2";
    PrintWriter output;
    output = createWriter( savePath(filename + "_int.csv") );
    output.println(title);

    for (int i=0; i<startLines-1; i++) 
    {          
      // convert as "unsigned" integer
      int smplTime = int(inBytes[i][0]) * int(256^3)
        + int(inBytes[i][1]) * int(256^2)
        + int(inBytes[i][2]) * int(256)
        + int(inBytes[i][3]);

      output.print( i + "," + smplTime );

      int tmp;
      for (int ch=0; ch<nCh; ch++)
      {
        for (int j=0; j<6; j++)
        { 
          // convert Higher Byte as "signed" integer   : (int)inBytes[i][2*j+2]
          // convert Lower Byte as "unsigned" integer  : int(inBytes[i][2*j+3])
          //tmp[j] = (int)inBytes[i][2*j+2] * 256 + (int)inBytes[i][2*j+3];
          tmp = (int)inBytes[i][12*ch + 2*j+4] * 256 + int(inBytes[i][12*ch + 2*j+5]);
          output.print( "," + tmp );
        }
      }
      output.println();
    }
    output.flush(); 
    output.close();

    // csv file // float

    title = "sample_count, ms, RAW_Acc X1[G], RAW_Acc Y1[G], RAW_Acc Z1[G], RAW_Gyro X1[deg/s], RAW_Gyro Y1[deg/s], RAW_Gyro Z1[deg/s], RAW_Acc X2[G], RAW_Acc Y2[G], RAW_Acc Z2[G], RAW_Gyro X2[deg/s], RAW_Gyro Y2[deg/s], RAW_Gyro Z2[deg/s], RAW_Acc X3[G], RAW_Acc Y3[G], RAW_Acc Z3[G], RAW_Gyro X3[deg/s], RAW_Gyro Y3[deg/s], RAW_Gyro Z3[deg/s], RAW_Acc X4[G], RAW_Acc Y4[G], RAW_Acc Z4[G], RAW_Gyro X4[deg/s], RAW_Gyro Y4[deg/s], RAW_Gyro Z4[deg/s]";
    output = createWriter( savePath(filename + "_float.csv") );
    output.println(title);

    for (int i=0; i<startLines-1; i++) 
    {          
      // convert as "unsigned" integer
      int smplTime = int(inBytes[i][0]) * int(256^3) 
        + int(inBytes[i][1]) * int(256^2)
        + int(inBytes[i][2]) * int(256)
        + int(inBytes[i][3]);

      output.print( i + "," + smplTime );

      int tmp;
      for (int ch=0; ch<nCh; ch++)
      {
        for (int j=0; j<3; j++)
        { 
          // convert as "signed" integer
          // convert Higher Byte as "signed" integer   : (int)inBytes[i][2*j+2]
          // convert Lower Byte as "unsigned" integer  : int(inBytes[i][2*j+3])
          tmp = (int)inBytes[i][12*ch + 2*j + 4] * 256 + int(inBytes[i][12*ch + 2*j + 5]);
          //output.print( "," + (float)tmp * MPU9250A_2g );
          output.print( "," + (float)tmp * MPU9250A_4g );
        }
        for (int j=3; j<6; j++)
        { 
          // convert as "signed" integer
          // convert Higher Byte as "signed" integer   : (int)inBytes[i][2*j+2]
          // convert Lower Byte as "unsigned" integer  : int(inBytes[i][2*j+3])
          tmp = int(inBytes[i][12*ch + 2*j + 4]) * 256 + int(inBytes[i][12*ch + 2*j + 5]);
          //output.print( "," + (float)tmp * MPU9250G_250dps );
          output.print( "," + (float)tmp * MPU9250G_500dps );
        }
      }
      output.println();
    }
    output.flush(); 
    output.close();
  }
  catch(Exception e) {
    e.printStackTrace();
  }

  serialPurge();

  startLines = 0;
}

void keyPressed() 
{
  if ( key == 's' ) 
  {
    if (isRecording ) 
    {
      writeFile();
    } else {

      sqr.amp(1);          
      delay(250);
      sqr.amp(0.001);      
      delay(50);
      sqr.amp(1);          
      delay(50);
      sqr.amp(0.001);      
      delay(50);
      sqr.amp(1);          
      delay(50);
      sqr.amp(0.001);

      serialPurge();

      println("now recording");
      isRecording = true;

      myPort.write('s');

      // serial buf pointer
      p = 0; 

      startLines = 0;
    }
  }
}

void stop()
{
  serialPurge();

  super.stop();
}

void draw() 
{
  String stat, msg;

  if (isRecording)
  {
    stat = "Now Recording";
    msg = "Hit 's' to stop & save";
    //background(200, 0, 0);
    background(0, 0, 0);
    noStroke();

    for (int i = width/2+1; i < width; i++) { 
      for (int ch = 0; ch < 4; ch++) { 
        for (int xyz = 0; xyz < 3; xyz++) { 
          vals[i-1][ch][xyz] = vals[i][ch][xyz];
        }
      }
    } 


    int acc;
    for (int ch=0; ch<4; ch++) {
      for (int xyz=0; xyz<3; xyz++) {
        acc=(int)inByte[12*ch + 2*xyz] * 256 + int(inByte[12*ch + 2*xyz + 1]);
        // Add the new values to the end of the array 
        vals[width-1][ch][xyz] = int((float)acc*MPU9250A_4g*height/16);
      }
    }    




    strokeWeight(1);
    for (int ch=0; ch<4; ch++) {
      int h = height/4*(ch+1) - height/8;
      int hn = h - height/16;
      int hp = h + height/16;
      stroke(128);
      line(width/2, hn, width, hn);
      line(width/2, hp, width, hp);
      for (int i=width/2+1; i<width; i++) {
        stroke(255, 0, 0);
        line(i, h+vals[i-1][ch][0], i, h+vals[i][ch][0]);
        stroke(0, 255, 0);
        line(i, h+vals[i-1][ch][1], i, h+vals[i][ch][1]);
        stroke(0, 128, 255);
        line(i, h+vals[i-1][ch][2], i, h+vals[i][ch][2]);
      }
      stroke(255);
      line(width/2, h, width, h); // base
    }

    noFill();
    stroke(128);
  } else
  {
    stat = "Ready";
    msg="Hit 's' to start";
    background(0, 200, 0);
    noFill();
    stroke(128);
  }  

  textAlign(CENTER, CENTER);  
  fill(255);

  textSize(100); 
  text(stat, 600, 40);
  textSize(30); 
  text(msg, 600, 110);

  // show current received data
  textSize(70); 

  //text(new String(inByte), 150, 85);
  text(String.format("ACC  %+06d %+06d %+06d ", (int)inByte[0] * 256 + int(inByte[1]), (int)inByte[2] * 256 + int(inByte[3]), (int)inByte[4] * 256 + int(inByte[5])  ), 600, 160);  
  text(String.format("GYRO %+06d %+06d %+06d ", (int)inByte[6] * 256 + int(inByte[7]), (int)inByte[8] * 256 + int(inByte[9]), (int)inByte[10]* 256 + int(inByte[11]) ), 600, 220);  

  textSize(30); 
  text(String.format("ACC Hex   %02x %02x / %02x %02x / %02x %02x", inByte[0], inByte[1], inByte[2], inByte[3], inByte[4], inByte[5]), 600, 300);  
  text(String.format("GYRO Hex  %02x %02x / %02x %02x / %02x %02x", inByte[6], inByte[7], inByte[8], inByte[9], inByte[10], inByte[11]), 600, 330);

  textSize(70); 

  if (isRecording ) 
  {
    text(String.format("Remain[min]  %2d / %2d", (minuteLength * smplHz * 60 - startLines) / smplHz / 60, minuteLength  ), 600, 400);
  } else {
    text(String.format("Wrote  %s", filename), 600, 400);
  }
}
