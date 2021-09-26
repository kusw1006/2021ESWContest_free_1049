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
    while True:
        #fp = open("./01.wav", 'ab')
        
        recv_wav = client_sock.recv(1024)  
        if len(recv_wav):
            # if id == 0:
            # print(recv_wav)
            write_to_fp(fp, recv_wav)
            print(len(recv_wav),len(fp.read()))
            print("asdf")
            if len(recv_wav) > 1 and len(recv_wav) < 1024:
                fp.seek(0)
                song = AudioSegment.from_wav(fp)
                print("PPPPPPPPPPPPPPPPPPPPlayyyyy")
                play(song)

                print("aaa",len(recv_wav),len(fp.read()))
        
         
            

            # print(fp.read())
        
            

        # if len(recv_wav) > 1 and len(recv_wav) < 1000:
        #     fp.seek(0)
        #     song = AudioSegment.from_wav(fp)
        #     print("PPPPPPPPPPPPPPPPPPPPlayyyyy")
        #     play(song)

        # if str(recv_wav).find("END"):
        #     print("end")
            # print(str(recv_wav))

#-------------이부분만 반복--------------#


client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))

thread1 = threading.Thread(target = recv, args=(client_socket, ))
thread1.start()
