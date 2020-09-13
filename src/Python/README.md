# imu_sensor/src/Python 

- September 14, 2020 - created / Yuto Nakayachi 

Yuto Nakayachi 

# read_acc_3_0_0.py 

mbedから送られてくるbinaryデータを受け取り、それをcsvファイルに落とすソースファイルです。

計測終了後、read_acc_3_0_0.pyと同階層に生データと実データの2つのCSVファイルが生成されます。

## Usage 
$ python read_acc_3_0_0.py

[以下実行結果]

Start Serial Connection 

ready? --> press s key 

[sキーを押す]

time: [計測にかかった時間が出る]

Start Create CSV File 

[生データのcsvファイルの名前].csv created

[実データのcsvファイルの名前].csv created

Done Create CSV File 

number of data: [計測したサンプル数が出る]

number of byte fail: [byte errorの回数が出る]

number of header fail: [heaedr errorの回数が出る]

END

## Note

binaryデータはread()関数により1Byteずつ受け取ります。

時間計測はmbedが各シーケンスごとに、前のシーケンスから経過した時間を出力する仕様です。(ex. 500Hzならば2msを返す)

print文でリアルタイムでのデータ出力(182~193行)を行うと、End byte set error(129行目の処理)とheader error(143行目)の処理が増加し、シーケンスの抜けが発生する(print文の処理がbinaryデータの受けとりに影響を与える)ため、printでのデータ出力はすべてコメントアウトしてあります。

計測時の時刻を作成するcsvファイルの名前としている(計測時刻が2020/09/14の15:10ならばacc_data20209141510.csvという名前のファイルができる)ため、同時刻に複数回計測を行うと、ファイルは上書きされ、最新のもののみが残ります。よって上書きされたくない場合は、作成したファイルの名前を変える、ファイルの保存場所をread_acc_3_0_0.pyとは別階層にするなどの処理が必要です。

# visualize_acc_3_0_0.py 

read_acc_3_0_0.pyが作ったcsvファイルを折れ線グラフに可視化するソースファイルです。

## Usage 

$ python visualize_acc_3_0_0.py [可視化したいcsvファイルの名前].csv



