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

# COMポートのスキャン範囲を設定
START_COM_PORT = 2
END_COM_PORT = 8
BAUD_RATE = 921600  # ボーレートを921600に設定
DATA_LENGTH = 100000

# データのスケーリング用
ACC_SCALE = 16384.0 / 2.0 # 例: 加速度のスケーリングファクター
GYRO_SCALE = 131.0 / 2.0  # 例: ジャイロのスケーリングファクター

class AccelerometerGUI:
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
        frame_tool_bar = tk.Frame(self.root, borderwidth = 10)
        for i in range(1, 5):
            label = tk.Label(frame_tool_bar, text=f"  CH {i}: Unknown  ", bg="gray", height = 2, font=("MSゴシック", "12", "bold"))
            label.pack(side=tk.LEFT)
            self.channel_status[i] = label
            
        label = tk.Label(frame_tool_bar, text=f"  Recorded Length :       0  ", bg="gray", font=("MSゴシック", "16", "bold"))
        label.pack(side=tk.LEFT)
        self.channel_status[5] = label
        frame_tool_bar.pack(fill = tk.X)

        # Acc/Gryo Setup
        # 項目をつくる
        frame_scale = tk.Frame(self.root, borderwidth=10)
        
        # 項目1
        items1 = ttk.Combobox(frame_scale, state='readonly', width=20, font=("MSゴシック", "14", "bold"))
        items1['values'] = ('Acc scale 2G', 'Acc scale 4G', 'Acc scale 8G', 'Acc scale 16G')
        items1.current(0)  # デフォルト値を設定
        items1.pack(side=tk.LEFT)
        
        # 項目2
        items2 = ttk.Combobox(frame_scale, state='readonly', width=20, font=("MSゴシック", "14", "bold"))
        items2['values'] = ('Gyro scale 250DPS', 'Gyro scale 500DPS', 'Gyro scale 1000DPS', 'Gyro scale 2000DPS')
        items2.current(0)  # デフォルト値を設定
        items2.pack(side=tk.LEFT)
        
        frame_scale.pack(fill=tk.X)
        
        # スケール変更時のイベントハンドラを設定
        items1.bind("<<ComboboxSelected>>", self.update_acc_scale)
        items2.bind("<<ComboboxSelected>>", self.update_gyro_scale)



    #     case BITS_FS_2G:
    #         acc_divider=16384;
    #     break;
    #     case BITS_FS_4G:
    #         acc_divider=8192;
    #     break;
    #     case BITS_FS_8G:
    #         acc_divider=4096;
    #     break;
    #     case BITS_FS_16G:
    #         acc_divider=2048;
    #     break;   
   
    # }    switch (scale){
    #     case BITS_FS_250DPS:
    #         gyro_divider=131;
    #     break;
    #     case BITS_FS_500DPS:
    #         gyro_divider=65.5;
    #     break;
    #     case BITS_FS_1000DPS:
    #         gyro_divider=32.8;
    #     break;
    #     case BITS_FS_2000DPS:
    #         gyro_divider=16.4;
    #     break;   
    # }
    # temp_scale=WriteReg(MPUREG_GYRO_CONFIG|READ_FLAG, 0x00);
    # switch (temp_scale){
    #     case BITS_FS_250DPS:
    #         temp_scale=250;
    #     break;
    #     case BITS_FS_500DPS:
    #         temp_scale=500;
    #     break;
    #     case BITS_FS_1000DPS:
    #         temp_scale=1000;
    #     break;
    #     case BITS_FS_2000DPS:
    #         temp_scale=2000;
    #     break;   
    # }
        # グラフの初期設定
        self.fig, (self.ax_acc, self.ax_gyro) = plt.subplots(2, 1, figsize=(10, 8))

        # 加速度グラフ
        self.line_x_acc, = self.ax_acc.plot([], [], label="X-acc", color='r')
        self.line_y_acc, = self.ax_acc.plot([], [], label="Y-acc", color='g')
        self.line_z_acc, = self.ax_acc.plot([], [], label="Z-acc", color='b')
        self.ax_acc.set_xlim(0, 500)
        self.ax_acc.set_ylim(-5, 5)
        self.ax_acc.set_ylabel("Acceleration [G]")
        self.ax_acc.set_title("Acceleration")
        self.ax_acc.legend()

        # ジャイログラフ
        self.line_x_gyro, = self.ax_gyro.plot([], [], label="X-gyro", color='r')
        self.line_y_gyro, = self.ax_gyro.plot([], [], label="Y-gyro", color='g')
        self.line_z_gyro, = self.ax_gyro.plot([], [], label="Z-gyro", color='b')
        self.ax_gyro.set_xlim(0, 500)
        self.ax_gyro.set_ylim(-500, 500)
        self.ax_gyro.set_ylabel("Gyro [rps]")
        self.ax_gyro.set_xlabel("Time [sample]")
        self.ax_gyro.set_title("Gyroscope")
        self.ax_gyro.legend()

        # CanvasをTkinterウィンドウに埋め込む
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # CSV保存ボタン
        self.save_button = tk.Button(self.root, text="  Save to CSV [S]  ", font=("MSゴシック", "14", "bold"), command=self.save_to_csv)
        self.save_button.pack(side=tk.LEFT)

        # データ計測開始・停止ボタン
        self.start_button = tk.Button(self.root, text="  Start Measurement [s]  ", font=("MSゴシック", "14", "bold"), command=self.start_measurement)
        self.start_button.pack(side=tk.LEFT)
        self.stop_button = tk.Button(self.root, text="  Stop Measurement [r] ", font=("MSゴシック", "14", "bold"), command=self.stop_measurement)
        self.stop_button.pack(side=tk.LEFT)

        # クリアボタン
        self.save_button = tk.Button(self.root, text="  Clear Data [c]  ", font=("MSゴシック", "14", "bold"), command=self.stop_and_clear)
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
        
        # シリアルポートからデータを読み込むスレッドを開始
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.start()

        # アニメーションの設定 (グラフの描画は間引いて行う)
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=5)

        # Realtime Clock
        self.milliseconds_start = int(time.time() * 1000)
      
    # スケール変更時のイベントハンドラ
    def update_acc_scale(self, event):
        return
    
    # スケール変更時のイベントハンドラ
    def update_gyro_scale(self, event):
        return
             
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
        if key == "Escape":
            self.stop_measurement()
            self.on_closing()


    def save_to_csv(self):
        # ファイル保存ダイアログを開く
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time[ms]', 'X-Acc', 'Y-Acc', 'Z-Acc', 'X-Gyro', 'Y-Gyro', 'Z-Gyro'])  # ヘッダーを書き込み
                for i in range(len(self.data['time'])):
                    writer.writerow([self.data['time'][i], self.data['x_acc'][i], self.data['y_acc'][i], self.data['z_acc'][i],
                                     self.data['x_gyro'][i], self.data['y_gyro'][i], self.data['z_gyro'][i]])

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
                print(f"Trying {com_port}...")
                ser = serial.Serial(com_port, BAUD_RATE, timeout=1)

                # COMポートにブレーク信号を送信
                ser.send_break(duration=0.20)  # ブレーク信号を送信
                time.sleep(.1)  # デバイスの応答を待つための遅延

                # メッセージを複数行読み込んで確認
                lines = []
                for _ in range(4):  # 複数行取得する
                    line = ser.readline().decode('utf-8').strip()
                    lines.append(line)
                    print(f"Received: {line}")
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
                                    
                    ser.write(b's')  # 's' を送信してデータ送信を開始
                    self.milliseconds_start = int(time.time() * 1000)
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
                
                # ヘッダーチェック ('*' で始まるか)
                if header == b'*':

                    for ch in range(1, 5):  # CH 1 から CH 4 まで処理
                        if ch == self.active_port:
                            # データを順次読み取る
                            acc_data = self.serial_port.read(6)
                            x_acc, y_acc, z_acc = struct.unpack('>hhh', acc_data)  # ビッグエンディアンでデコード
                            x_acc = x_acc / ACC_SCALE  # スケーリング
                            y_acc = y_acc / ACC_SCALE
                            z_acc = z_acc / ACC_SCALE

                            gyro_data = self.serial_port.read(6)
                            x_gyro, y_gyro, z_gyro = struct.unpack('>hhh', gyro_data)
                            x_gyro = x_gyro / GYRO_SCALE  # スケーリング
                            y_gyro = y_gyro / GYRO_SCALE
                            z_gyro = z_gyro / GYRO_SCALE
                        else:
                            # データを順次読み取る
                            acc_data = self.serial_port.read(6)
                            gyro_data = self.serial_port.read(6)

                    # タイムスタンプを読み取る
                    time_data = self.serial_port.read(1)
                    timestamp = struct.unpack('>B', time_data)[0]  # 1バイトのタイムスタンプ
                    milliseconds = int(time.time() * 1000)
                    

                    # CR (0x0d) と LF (0x0a) を読み飛ばす
                    self.serial_port.read(2)

                    # データを保存
                    self.data['x_acc'].append(x_acc)
                    self.data['y_acc'].append(y_acc)
                    self.data['z_acc'].append(z_acc)
                    self.data['x_gyro'].append(x_gyro)
                    self.data['y_gyro'].append(y_gyro)
                    self.data['z_gyro'].append(z_gyro)
                    self.data['time'].append((milliseconds - self.milliseconds_start)/1000.0)

                    # データを一定数以上保持しないようにリミットを設定
                    if len(self.data['x_acc']) > DATA_LENGTH:
                        self.data['x_acc'].pop(0)
                        self.data['y_acc'].pop(0)
                        self.data['z_acc'].pop(0)
                        self.data['x_gyro'].pop(0)
                        self.data['y_gyro'].pop(0)
                        self.data['z_gyro'].pop(0)
                        self.data['time'].pop(0)
                
                #読み落としがあるか確認        
                #else:
                    #print('/')

        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")

    def update_plot(self, frame):
        # データ長をそろえるために、最小長のリストに基づいてデータを切り詰める
        min_len = min(len(self.data['x_acc']), len(self.data['y_acc']), len(self.data['z_acc']), len(self.data['x_gyro']))
        x_range = range(min_len)

        # 加速度グラフのデータ設定
        self.line_x_acc.set_data(x_range, self.data['x_acc'][:min_len])
        self.line_y_acc.set_data(x_range, self.data['y_acc'][:min_len])
        self.line_z_acc.set_data(x_range, self.data['z_acc'][:min_len])

        # ジャイログラフのデータ設定
        self.line_x_gyro.set_data(x_range, self.data['x_gyro'][:min_len])
        self.line_y_gyro.set_data(x_range, self.data['y_gyro'][:min_len])
        self.line_z_gyro.set_data(x_range, self.data['z_gyro'][:min_len])

        # プロットのX軸範囲を更新
        self.ax_acc.set_xlim(max(100, min_len) - 100, max(100, min_len))
        self.ax_gyro.set_xlim(max(100, min_len) - 100, max(100, min_len))

        # レコード長を表示
        self.channel_status[5].config(text=f"  Recorded Length :  {min_len} ", bg="gray", font=("MSゴシック", "16", "bold"))
        # print(min_len)

        # キャンバスの更新
        self.canvas.draw()

    def on_closing(self):
        """×ボタンが押された時の処理"""
        print("Closing thread...")
        self.is_running = False  # スレッドを停止するフラグを設定
        time.sleep(0.7)          # スレッドが停止するのを待つ
        print("Closing COM port...")
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()  # シリアルポートを閉じる
            time.sleep(0.2)          # スレッドが停止するのを待つ
        print("Closing application...")
        self.root.quit()  # Tkinterのメインループを停止
        self.root.destroy()  # ウィンドウを閉じる

        
    
# Tkinterのメインループ
root = tk.Tk()
app = AccelerometerGUI(root)
root.mainloop()
