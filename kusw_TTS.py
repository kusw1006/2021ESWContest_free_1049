'''
sudo apt-get install ffmpeg
python3 -m pip install pydub 
python3로 실행해야함
'''
import os
import sys
import socket
import threading

import io
from io import BytesIO

from pydub import AudioSegment
from pydub.playback import play
 

def write_to_fp(fp, input_wav):
    fp.write(input_wav)


def recv(client_sock):
    fp = BytesIO()

    while True:
        recv = client_sock.recv(1024)  

        if len(recv):
            write_to_fp(fp, recv)
            print(len(recv),len(fp.read()))

        if fp.read and len(recv)==1:       
            print("aaa",len(recv),len(fp.read()))
            print(fp.read())

            fp.seek(0)

            #print(fp.read())

            song = AudioSegment.from_file(fp, format="wav")
            play(song)
 

#-------------이부분만 반복--------------#
import time


HOST = '114.70.22.237'
PORT = 5052

 
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))

thread1 = threading.Thread(target = recv, args=(client_socket, ))
thread1.start()