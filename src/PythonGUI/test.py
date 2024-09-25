import tkinter as tk
from tkinter import filedialog
import serial
import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

# COMポートのスキャン範囲を設定
START_COM_PORT = 2
END_COM_PORT = 8
BAUD_RATE = 921600  # ボーレートを921600に設定

class AccelerometerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Accelerometer Data Logger")
        
        # シリアルポートから読み込んだデータを保存するリスト
        self.data = {'x': [], 'y': [], 'z': [], 'time': []}
        self.is_running = True  # スレッド終了用フラグ

        # CSVファイル保存用の変数
        self.csv_file = None

        # チャネル状態を表示するラベル
        self.channel_status = {}
        for i in range(1, 5):
            label = tk.Label(self.root, text=f"CH {i}: Unknown", bg="gray")
            label.pack(side=tk.TOP, fill=tk.X)
            self.channel_status[i] = label

        # グラフの初期設定
        self.fig, self.ax = plt.subplots()
        self.line_x, = self.ax.plot([], [], label="X-axis")
        self.line_y, = self.ax.plot([], [], label="Y-axis")
        self.line_z, = self.ax.plot([], [], label="Z-axis")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-10, 10)
        self.ax.legend()

        # CanvasをTkinterウィンドウに埋め込む
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # CSV保存ボタン
        self.save_button = tk.Button(self.root, text="Save to CSV", command=self.save_to_csv)
        self.save_button.pack(side=tk.LEFT)

        # ウィンドウ終了イベントを設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # シリアルポートをスキャンして接続を確立
        self.serial_port = self.scan_serial_ports()
        if self.serial_port is None:
            print("No valid COM port found.")
            return
        
        # シリアルポートからデータを読み込むスレッドを開始
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.start()

        # アニメーションの設定
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=100)

    def save_to_csv(self):
        # ファイル保存ダイアログを開く
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time', 'X', 'Y', 'Z'])  # ヘッダーを書き込み
                for i in range(len(self.data['time'])):
                    writer.writerow([self.data['time'][i], self.data['x'][i], self.data['y'][i], self.data['z'][i]])

    def update_channel_status(self, channel, message):
        if "*** ERROR ***" in message:
            self.channel_status[channel].config(text=f"CH {channel}: Error", bg="red")
        else:
            self.channel_status[channel].config(text=f"CH {channel}: OK", bg="green")

    def scan_serial_ports(self):
        """COMポート2番から8番までスキャンし、有効なポートを見つける"""
        for port_number in range(START_COM_PORT, END_COM_PORT + 1):
            com_port = f"COM{port_number}"
            try:
                print(f"Trying {com_port}...")
                ser = serial.Serial(com_port, BAUD_RATE, timeout=1)
                
                # COMポートにブレーク信号を送信
                ser.send_break(duration=0.25)  # ブレーク信号を送信
                
                time.sleep(1)  # デバイスの応答を待つための遅延

                # メッセージを複数行読み込んで確認
                lines = []
                for _ in range(5):  # 複数行取得する
                    line = ser.readline().decode('utf-8').strip()
                    lines.append(line)
                    print(f"Received: {line}")

                # 正しいメッセージが含まれているか確認
                welcome_message = "\n".join(lines)
                if "KOMATSU Experiment" in welcome_message:
                    print(f"Valid COM port found: {com_port}")
                    return ser  # 有効なポートを開いた状態で返す
                else:
                    ser.close()  # 無効な場合はポートを閉じる
            except (serial.SerialException, UnicodeDecodeError):
                print(f"{com_port} is not valid.")
        return None

    def read_serial_data(self):
        channel = None  # 初期化しておく
        try:
            while self.is_running:  # フラグがTrueの間実行
                if self.serial_port.in_waiting > 0:  # データが存在する場合にのみ読み込む
                    line = self.serial_port.readline().decode('utf-8').strip()
                    
                    if line.startswith("CH"):
                        # チャネルを取得
                        try:
                            channel = int(line.split()[1])
                        except (IndexError, ValueError):
                            channel = None  # 何か問題があれば初期化

                    if channel and "WHOAMI" in line:
                        # チャネルごとのステータスを確認
                        sensor_status = []
                        for _ in range(3):  # エラーメッセージが3行続くと想定
                            status_line = self.serial_port.readline().decode('utf-8').strip()
                            sensor_status.append(status_line)

                        # チャネルのステータスを更新
                        status_message = "\n".join(sensor_status)
                        self.update_channel_status(channel, status_message)

                    if "Gyro_scale" in line and channel in [2, 4]:  # CH 2 と CH 4 のみ計測対象
                        # 有効なチャネルから加速度データを取得し、解析
                        try:
                            x, y, z = map(float, line.split()[1:4])
                            current_time = time.time() - time.time()
                            self.data['x'].append(x)
                            self.data['y'].append(y)
                            self.data['z'].append(z)
                            self.data['time'].append(current_time)

                            # データを一定数以上保持しないようにリミットを設定
                            if len(self.data['x']) > 100:
                                self.data['x'].pop(0)
                                self.data['y'].pop(0)
                                self.data['z'].pop(0)
                                self.data['time'].pop(0)
                        except ValueError:
                            continue

        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")

    def update_plot(self, frame):
        # グラフにリアルタイムデータをプロット
        self.line_x.set_data(range(len(self.data['x'])), self.data['x'])
        self.line_y.set_data(range(len(self.data['y'])), self.data['y'])
        self.line_z.set_data(range(len(self.data['z'])), self.data['z'])
        self.ax.set_xlim(0, max(100, len(self.data['x'])))
        self.canvas.draw()

    def on_closing(self):
        """×ボタンが押された時の処理"""
        print("Closing application...")
        self.is_running = False  # スレッドを停止するフラグを設定
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()  # シリアルポートを閉じる
        self.root.quit()  # Tkinterのメインループを停止
        self.root.destroy()  # ウィンドウを閉じる

# Tkinterのメインループ
root = tk.Tk()
app = AccelerometerGUI(root)
root.mainloop()
