// Masahiro Furukawa
// July 2, 2020

using System;
using System.IO.Ports;
using System.Linq;
using System.Runtime.CompilerServices;

namespace read_test
{


    class Read_test
    {
        // Coefficient values to translate byte code to real value
        //
        // https://os.mbed.com/compiler/#nav:/MPU-9250-Ch2_ACC_binary/MPU9250_SPI/MPU9250.h
        // /* ---- Sensitivity --------------------------------------------------------- */

        const double MPU9250A_2g = 0.000061035156;       // 0.000061035156 g/LSB
        const double MPU9250A_4g = 0.000122070312;       // 0.000122070312 g/LSB
        const double MPU9250A_8g = 0.000244140625;       // 0.000244140625 g/LSB
        const double MPU9250A_16g = 0.000488281250;      // 0.000488281250 g/LSB

        const double MPU9250G_250dps = 0.007633587786;   // 0.007633587786 dps/LSB
        const double MPU9250G_500dps = 0.015267175572;   // 0.015267175572 dps/LSB
        const double MPU9250G_1000dps = 0.030487804878;  // 0.030487804878 dps/LSB
        const double MPU9250G_2000dps = 0.060975609756;  // 0.060975609756 dps/LSB

        const double MPU9250M_4800uT = 0.6;              // 0.6 uT/LSB

        const double MPU9250T_85degC = 0.002995177763;   // 0.002995177763 degC/LSB
        const double Magnetometer_Sensitivity_Scale_Factor = 0.15;

        static SerialPort serialPort1 = new SerialPort();

        Read_test()
        {
        }

        ~Read_test()
        {
            serialPort1.Close();
        }

        static void Main(string[] args)
        {
            string[] ports = SerialPort.GetPortNames();

            serialPort1.PortName = ports[ports.Count() - 1]; // select the last one
            serialPort1.BaudRate = 921600;
            serialPort1.Parity = Parity.None;
            serialPort1.DataBits = 8;
            serialPort1.StopBits = StopBits.One;
            serialPort1.Handshake = Handshake.None;

            serialPort1.Open();


            if (!serialPort1.IsOpen)
            {
                Console.WriteLine("Could not open COM Port");
                return;
            }

            serialPort1.Write("r"); // command to stop data stream for mbed
            serialPort1.Write("s"); // command to start data stream for mbed

            Int32 val = 0;
            Int32 state = 0;
            int p = 0;
            int count = 0;
            byte[] buf = new byte[51];

            while (true)
            {
                count = serialPort1.BytesToRead;

                while (count > 0)
                {
                    try
                    {
                        val = (byte)serialPort1.ReadByte();
                    }
                    catch
                    {
                        Console.WriteLine("catched exception.  count = {0}", count);
                    }
                    if (state == 0 && val == (byte)'\r')
                    {
                        val = (byte)serialPort1.ReadByte();

                        // waiting for '\n' and get ready
                        if (val == (byte)'\n')
                        {
                            state = 1;
                            p = 0;
                            continue;
                        }
                        else
                        {
                            Console.WriteLine("End byte set failure.");
                        }

                    }

                    // store val into list
                    if (state == 1)
                    {
                        // Make Little Endien for BitConverter from Big Endien
                        if (p % 2 == 0)
                            buf[p + 1] = (byte)val;
                        else
                            buf[p - 1] = (byte)val;
                        p++;

                        // ready to decode
                        if (p == 48)
                        {
                            p = 0;
                            state = 0;

                            short s = 0;
                            for (int i = 0; i < 3; i++) 
                            { 
                                s = BitConverter.ToInt16(buf, 2 * i);
                                Console.Write("{0,5:F} ", s * MPU9250A_4g);
                            }
                            for (int i = 0; i < 3; i++) { 
                                s = BitConverter.ToInt16(buf, 6 + 2 * i); 
                                Console.Write("{0,7:F} ", s * MPU9250G_500dps);
                            }
                            Console.WriteLine();
                        }

                    }
                }
            }


        }

    }
}
