import os
import sys
import socket
import threading

import time
import io
from io import BytesIO

from pydub import AudioSegment
from pydub.playback import play


HOST = '114.70.22.237'
PORT = 5053

def write_to_fp(fp, input_wav):
    fp.write(input_wav)

def recv(client_sock):
    fp = BytesIO()

    id = 0
    seekInd = 0
    
    while True:
        #fp = open("./01.wav", 'ab')
        recv = client_sock.recv(1024)  

        if len(recv):
            if id == 0:
                print(recv)
            write_to_fp(fp, recv)

            #fp.close()
            lenRecv = len(recv)
            print(lenRecv)
            id += lenRecv

        if len(recv) > 1 and len(recv) < 1000:
            fp.seek(0)
            song = AudioSegment.from_wav(fp)
            print("PPPPPPPPPPPPPPPPPPPPlayyyyy")
            play(song)


#-------------이부분만 반복--------------#


client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))

thread1 = threading.Thread(target = recv, args=(client_socket, ))
thread1.start()