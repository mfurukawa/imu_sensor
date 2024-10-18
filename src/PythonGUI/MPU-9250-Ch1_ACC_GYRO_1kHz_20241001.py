import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import serial
import csv
import struct  # バイト列の解析に使用
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import numpy as np

# COMポートのスキャン範囲を設定
START_COM_PORT = 2
END_COM_PORT = 8
BAUD_RATE = 921600  # ボーレートを921600に設定
DATA_LENGTH = 100000

# データのスケーリング用
ACC_SCALE = 32768.0 / 16.0 # 例: 加速度のスケーリングファクター
GYRO_SCALE = 131.0 / 8.0   # 例: ジャイロのスケーリングファクター

class AccelerometerGUI:
    
    # スケール変更時のイベントハンドラ
    def update_acc_scale(self, event):
        self.stop_measurement()
        self.clear_data()
        selected_scale = event.widget.get()
        global ACC_SCALE
        if selected_scale == 'Acc scale 2G':
            ACC_SCALE = 32768.0 / 2.0
            cmd = b'0'        
            self.ax_acc.set_ylim(-3, 3)
        elif selected_scale == 'Acc scale 4G':
            ACC_SCALE = 32768.0 / 4.0
            cmd = b'1'
            self.ax_acc.set_ylim(-6, 6)
        elif selected_scale == 'Acc scale 8G':
            ACC_SCALE = 32768.0 / 8.0
            cmd = b'2'
            self.ax_acc.set_ylim(-10, 10)
        elif selected_scale == 'Acc scale 16G':
            ACC_SCALE = 32768.0 / 16.0
            cmd = b'3'
            self.ax_acc.set_ylim(-20, 20)
        else:
            ACC_SCALE = 32768.0 / 16.0  # デフォルト値
            cmd = b'3'        
            self.ax_acc.set_ylim(-20, 20)
        
        """ACC SCALE設定のために 'A' を送信"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(b'A')
            self.serial_port.write(cmd)
            print(f"Acceleration scale set to: {selected_scale}")
        return
    
    # スケール変更時のイベントハンドラ
    def update_gyro_scale(self, event):
        self.stop_measurement()
        self.clear_data()
        selected_scale = event.widget.get()
        global GYRO_SCALE
        if selected_scale == 'Gyro scale 250DPS':
            GYRO_SCALE = 131.0 
            cmd = b'0'
            self.ax_gyro.set_ylim(-300, 300)
        elif selected_scale == 'Gyro scale 500DPS':
            GYRO_SCALE = 131.0 / 2.0
            cmd = b'1'
            self.ax_gyro.set_ylim(-600, 600)
        elif selected_scale == 'Gyro scale 1000DPS':
            GYRO_SCALE = 131.0 / 4.0
            cmd = b'2'
            self.ax_gyro.set_ylim(-1100, 1100)
        elif selected_scale == 'Gyro scale 2000DPS':
            GYRO_SCALE = 131.0 / 8.0
            cmd = b'3'
            self.ax_gyro.set_ylim(-2200, 2200)
        else:
            GYRO_SCALE = 131.0 / 8.0   # デフォルト値
            cmd = b'3'
            self.ax_gyro.set_ylim(-2200, 2200)

        """GYRO SCALE 設定のために 'G' を送信"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(b'G')
            self.serial_port.write(cmd)
            print(f"Gyroscope scale set to: {selected_scale}")
        return
    
    def __init__(self, root):
        self.root = root
        self.root.title("Accelerometer & Gyroscope Data Logger")

        # get key event
        self.root.bind("<KeyPress>", self.key_event)     

        self.clear_data()
        self.is_running = True  # スレッド終了用フラグ

        # CSVファイル保存用の変数
        self.csv_file = None

        # チャネル状態を表示するラベル
        self.channel_status = {}
        frame_tool_bar = tk.Frame(self.root, borderwidth = 0)
        for i in range(1, 5):
            label = tk.Label(frame_tool_bar, text=f"  CH {i}: Unknown  ", bg="gray", height = 0, font=("MSゴシック", "10", "bold"))
            label.pack(side=tk.LEFT)
            self.channel_status[i] = label
            
        label = tk.Label(frame_tool_bar, text=f"  Recorded Length :       0  ", bg="gray", font=("MSゴシック", "10", "bold"))
        label.pack(side=tk.LEFT)
        self.channel_status[5] = label

        # Acc/Gryo Setup
        # 設定項目をつくる
        
        # 項目1
        style = ttk.Style()
        style.configure("TCombobox", font=("MSゴシック", "14", "bold"), padding=2)

        self.items1 = ttk.Combobox(frame_tool_bar, state='readonly', width=20, style="TCombobox")
        self.items1['values'] = ('Acc scale 2G', 'Acc scale 4G', 'Acc scale 8G', 'Acc scale 16G')
        self.items1.current(1)  # デフォルト値を設定
        self.items1.pack(side=tk.LEFT)
        
        # 項目2
        self.items2 = ttk.Combobox(frame_tool_bar, state='readonly', width=20)
        self.items2['values'] = ('Gyro scale 250DPS', 'Gyro scale 500DPS', 'Gyro scale 1000DPS', 'Gyro scale 2000DPS')
        self.items2.current(1)  # デフォルト値を設定
        self.items2.pack(side=tk.LEFT)        
        frame_tool_bar.pack(fill=tk.X)
        
        # スケール変更時のイベントハンドラを設定
        self.items1.bind("<<ComboboxSelected>>", self.update_acc_scale)
        self.items2.bind("<<ComboboxSelected>>", self.update_gyro_scale)

        # グラフの初期設定
        #self.fig, (self.ax_acc, self.ax_gyro) = plt.subplots(2, 1, figsize=(10, 8))
        # In your __init__ method, add another axis for the FFT
        self.fig, (self.ax_acc, self.ax_gyro, self.ax_fft) = plt.subplots(3, 1, figsize=(8, 8))

        # 加速度グラフ
        self.line_x_acc, = self.ax_acc.plot([], [], label="X-acc", color='r')
        self.line_y_acc, = self.ax_acc.plot([], [], label="Y-acc", color='g')
        self.line_z_acc, = self.ax_acc.plot([], [], label="Z-acc", color='b')
        self.ax_acc.set_xlim(0, 500)
        self.ax_acc.set_ylim(-20, 20)
        self.ax_acc.set_xlabel("Time [s]")  # X-axis label for accelerometer data
        self.ax_acc.set_ylabel("Acceleration [G]")
        self.ax_acc.set_title("Acceleration")
        self.ax_acc.legend(loc='upper right')

        # ジャイログラフ
        self.line_x_gyro, = self.ax_gyro.plot([], [], label="X-gyro", color='r')
        self.line_y_gyro, = self.ax_gyro.plot([], [], label="Y-gyro", color='g')
        self.line_z_gyro, = self.ax_gyro.plot([], [], label="Z-gyro", color='b')
        self.ax_gyro.set_xlim(0, 500)
        self.ax_gyro.set_ylim(-2200, 2200)
        self.ax_gyro.set_ylabel("Gyro [Degree per second]")
        self.ax_gyro.set_xlabel("Time [s]")  # X-axis label for gyroscope data
        self.ax_gyro.set_title("Gyroscope")
        self.ax_gyro.legend(loc='upper right')

        # Add a line for the FFT plot with thinner line width
        self.line_x_fft, = self.ax_fft.plot([], [], label="FFT of X-acc", color='r', linewidth=0.5)
        self.line_y_fft, = self.ax_fft.plot([], [], label="FFT of Y-acc", color='g', linewidth=0.5)
        self.line_z_fft, = self.ax_fft.plot([], [], label="FFT of Z-acc", color='b', linewidth=0.5)
        self.ax_fft.set_xscale('log')
        self.ax_fft.set_xlim(1, 500)  # Frequency range, you can adjust this based on your data
        self.ax_fft.set_ylim(0, 20)   # Magnitude range, adjust accordingly
        self.ax_fft.set_xlabel("Frequency [Hz]")
        self.ax_fft.set_ylabel("Magnitude")
        self.ax_fft.set_title("Real-Time FFT of X-Acceleration")
        self.ax_fft.legend(loc='upper left')

        # CanvasをTkinterウィンドウに埋め込む
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Draw the canvas and adjust layout
        self.canvas.draw()
        plt.subplots_adjust(hspace=0.5)  # Automatically adjust layout

        # CSV保存ボタン
        self.save_button = tk.Button(self.root, text="  Save to CSV [S]  ", font=("MSゴシック", "10", "bold"), command=self.save_to_csv)
        self.save_button.pack(side=tk.LEFT)

        # データ計測開始・停止ボタン
        self.start_button = tk.Button(self.root, text="  Start Measurement [s]  ", font=("MSゴシック", "10", "bold"), command=self.start_measurement)
        self.start_button.pack(side=tk.LEFT)
        self.stop_button = tk.Button(self.root, text="  Stop Measurement [r] ", font=("MSゴシック", "10", "bold"), command=self.stop_measurement)
        self.stop_button.pack(side=tk.LEFT)

        # クリアボタン
        self.save_button = tk.Button(self.root, text="  Clear Data [c]  ", font=("MSゴシック", "10", "bold"), command=self.stop_and_clear)
        self.save_button.pack(side=tk.LEFT)

        # ウィンドウ終了イベントを設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Active Port
        self.active_port = 999

        # シリアルポートをスキャンして接続を確立
        self.serial_port = self.scan_serial_ports()
        if self.serial_port is None:
            # again
            self.serial_port = self.scan_serial_ports()            
            if self.serial_port is None:
                print("No valid COM port found.")
                return
        
        # デフォルトのスケールを設定
        self.items1.set("Acc scale 16G")
        self.items1.event_generate("<<ComboboxSelected>>")
        self.items2.set("Gyro scale 2000DPS")
        self.items2.event_generate("<<ComboboxSelected>>")

        # シリアルポートからデータを読み込むスレッドを開始
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.start()

        # アニメーションの設定 (グラフの描画は間引いて行う)
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=16.6)
      
             
    # シリアルポートから読み込んだデータを保存するリスト
    def clear_data(self):
        self.data = {'x_acc': [], 'y_acc': [], 'z_acc': [],
                    'x_gyro': [], 'y_gyro': [], 'z_gyro': [], 'time': []}

    def stop_and_clear(self):
        self.stop_measurement()
        self.clear_data()

    # Key Event Handler
    def key_event(self, e):
        key = e.keysym
        
        if key == "c":
            self.stop_measurement()
            self.clear_data()
        
        if key == "s":
            self.start_measurement()
        
        if key == "r":
            self.stop_measurement()

        if key == "S":
            self.stop_measurement()
            self.save_to_csv()

        if key == "Escape" or key == "q":
            self.stop_measurement()
            self.on_closing()


    def save_to_csv(self):
        # ファイル保存ダイアログを開く
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time[ms]', 'X-Acc[G]', 'Y-Acc[G]', 'Z-Acc[G]', 'X-Gyro', 'Y-Gyro', 'Z-Gyro'])  # ヘッダーを書き込み
                for i in range(len(self.data['time'])):
                    writer.writerow([self.data['time'][i], 
                                     self.data['x_acc'][i]/ ACC_SCALE, 
                                     self.data['y_acc'][i]/ ACC_SCALE, 
                                     self.data['z_acc'][i]/ ACC_SCALE,
                                     self.data['x_gyro'][i]/ GYRO_SCALE, 
                                     self.data['y_gyro'][i]/ GYRO_SCALE, 
                                     self.data['z_gyro'][i]/ GYRO_SCALE])

    def start_measurement(self):
        """データ計測開始のために 's' を送信"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(b's')
            print("Measurement started.")

    def stop_measurement(self):
        """データ計測停止のために 'r' を送信"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(b'r')
            print("Measurement stopped.")

    def update_channel_status(self, channel, message):
        """チャネルのエラーステータスを更新"""
        if "*** ERROR ***" in message:
            self.channel_status[channel].config(text=f"  CH {channel}: Error  ", bg="Salmon")
        else:
            self.channel_status[channel].config(text=f"    CH {channel}: OK   ", bg="light green")

    def scan_serial_ports(self):
        """COMポート2番から8番までスキャンし、有効なポートを見つける"""
        for port_number in range(START_COM_PORT, END_COM_PORT + 1):
            com_port = f"COM{port_number}"
            try:
                print(f"Trying {com_port}...", end='')
                ser = serial.Serial(com_port, BAUD_RATE, timeout=1)

                # COMポートにブレーク信号を送信
                ser.send_break(duration=0.1)  # ブレーク信号を送信
                time.sleep(.1)  # デバイスの応答を待つための遅延

                # メッセージを複数行読み込んで確認
                lines = []
                for _ in range(4):  # 複数行取得する
                    line = ser.readline().decode('utf-8').strip()
                    lines.append(line)
                    # print(f"Received: {line}")

                # 正しいメッセージが含まれているか確認
                welcome_message = "\n".join(lines)
                if "KOMATSU Experiment" in welcome_message:
                    print(f"Valid COM port found: {com_port}")

                    # チャネルごとのメッセージ処理
                    channel_status = {}
                    for ch in range(1, 5):  # CH 1 から CH 4 まで処理
                        line = ser.readline().decode('utf-8').strip()
                        if line.startswith(f"CH {ch}"):
                            # CH n が始まったら、次の数行を処理
                            whoami_line = ser.readline().decode('utf-8').strip()
                            if "WHOAMI" in whoami_line:
                                whoami_value = whoami_line.split('=')[-1].strip()
                                
                                # WHOAMI値が0x00ならエラーとみなす
                                if whoami_value == "0x71":
                                    channel_status[ch] = "OK"
                                    print(f"CH {ch} : OK.     WHOAMI = {whoami_value}")
                                    self.active_port = ch
                                else:
                                    channel_status[ch] = "*** ERROR ***"
                                    print(f"CH {ch} : error.  WHOAMI = {whoami_value}")
                                    ser.readline().decode('utf-8').strip()  # 読み飛ばし
                                
                                # 残りのメッセージ（エラーまたはセンサー情報）を処理
                                sensor_status = []
                                for _ in range(3):  # 次の3行を読む
                                    status_line = ser.readline().decode('utf-8').strip()
                                    sensor_status.append(status_line)
                                    print(status_line)
                                
                                # エラーメッセージが含まれていればエラーと判断
                                if any("*** ERROR ***" in line for line in sensor_status):
                                    channel_status[ch] = "*** ERROR *** acc and gyro sensor does not respond correctly!"
                                
                                # ステータスをGUIに反映
                                self.update_channel_status(ch, channel_status[ch])
                                    
                    #ser.write(b's')  # 's' を送信してデータ送信を開始
                    return ser  # 有効なポートを開いた状態で返す
                else:
                    ser.close()  # 無効な場合はポートを閉じる

            except (serial.SerialException, UnicodeDecodeError):
                print(f"{com_port} is not valid.")
        return None

    def read_serial_data(self):
        try:
            while self.is_running:
                header = self.serial_port.read(1)
                if(len(header) == 0):
                    continue
                if ord(header) != 127:  # ASCII code of DEL
                    print('/', end='')  # 読み落としがあるか確認
                    continue                
                else:
                    # for ch in range(1, 5):  # CH 1 から CH 4 まで処理
                    #     if ch == self.active_port:

                    # データを順次読み取る
                    acc_data = self.serial_port.read(6)
                    x_acc, y_acc, z_acc = struct.unpack('>hhh', acc_data)  # ビッグエンディアンでデコード

                    gyro_data = self.serial_port.read(6)
                    x_gyro, y_gyro, z_gyro = struct.unpack('>hhh', gyro_data)
                                    
                        # else:
                        #     # データを順次読み取る
                        #     acc_data = self.serial_port.read(6)
                        #     gyro_data = self.serial_port.read(6)

                    # タイムスタンプを読み取る
                    time_data = self.serial_port.read(3)
                    milliseconds = int.from_bytes(time_data, byteorder='big', signed=False)

                    if 'x_acc' in locals():
                        # データを保存
                        self.data['x_acc'].append(x_acc)
                        self.data['y_acc'].append(y_acc)
                        self.data['z_acc'].append(z_acc)
                        self.data['x_gyro'].append(x_gyro)
                        self.data['y_gyro'].append(y_gyro)
                        self.data['z_gyro'].append(z_gyro)
                        self.data['time'].append(milliseconds)

                        # データを一定数以上保持しないようにリミットを設定
                        if len(self.data['x_acc']) > DATA_LENGTH:
                            self.stop_measurement()
                
        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")



    def update_plot(self, frame):
        min_len = len(self.data['time'])  # Use the length of the time data for synchronization
        start_index = max(0, min_len - 500)  # Show the last 500 samples, adjust as necessary

        if min_len > 0:
            # Get the time range for the x-axis (in real time)
            x_range = np.array(self.data['time'][start_index:min_len]) / 1000  # Convert to seconds

            # Prepare accelerometer and gyroscope data
            acc_data = [(self.data['x_acc'], self.line_x_acc), 
                        (self.data['y_acc'], self.line_y_acc), 
                        (self.data['z_acc'], self.line_z_acc)]
            gyro_data = [(self.data['x_gyro'], self.line_x_gyro), 
                        (self.data['y_gyro'], self.line_y_gyro), 
                        (self.data['z_gyro'], self.line_z_gyro)]

            # Update accelerometer and gyroscope lines
            for data, line in acc_data:
                line.set_data(x_range, np.array(data[start_index:min_len]) / ACC_SCALE)
            for data, line in gyro_data:
                line.set_data(x_range, np.array(data[start_index:min_len]) / GYRO_SCALE)

            # Perform FFT on the accelerometer data
            if len(self.data['x_acc']) >= 1024:
                for axis, line_fft in zip(['x_acc', 'y_acc', 'z_acc'], [self.line_x_fft, self.line_y_fft, self.line_z_fft]):
                    signal = np.array(self.data[axis][-1024:])  # Get the last 1024 samples
                    fft_result = np.fft.fft(signal)  # Perform FFT
                    freqs = np.fft.fftfreq(len(fft_result), d=(x_range[1] - x_range[0]))  # Compute frequency bins
                    line_fft.set_data(freqs[:512], np.log(np.abs(fft_result[:512])))  # Plot only the positive frequencies

            # Keep a fixed time window for the x-axis
            end_time = x_range[-1]
            start_time = max(end_time - 0.5, x_range[0])  # Show the last 500 milliseconds, adjust as necessary
            self.ax_acc.set_xlim(start_time, end_time)
            self.ax_gyro.set_xlim(start_time, end_time)

            # Add x-axis labels
            self.channel_status[5].config(text=f"  Recorded Length :  {min_len} ", fg="white", bg="black", font=("MSゴシック", "10", "bold"))


    def on_closing(self):
        """×ボタンが押された時の処理"""
        print("Closing thread...")
        self.is_running = False  # スレッドを停止するフラグを設定
        time.sleep(0.2)          # スレッドが停止するのを待つ
        print("Closing COM port...")
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()  # シリアルポートを閉じる
            time.sleep(0.1)          # スレッドが停止するのを待つ
        print("Closing application...")
        self.root.quit()  # Tkinterのメインループを停止
        self.root.destroy()  # ウィンドウを閉じる

        
    
# Tkinterのメインループ
root = tk.Tk()
app = AccelerometerGUI(root)
root.mainloop()
