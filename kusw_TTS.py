import os
import sys
import socket
import threading

import time
import io
from io import BytesIO

<<<<<<< HEAD


import base64

 

=======
>>>>>>> 0dcaccf001ac440cb00401213d080be47961cf90
from pydub import AudioSegment
from pydub.playback import play


HOST = '114.70.22.237'
PORT = 5053

def write_to_fp(fp, input_wav):
    fp.write(input_wav)

def recv(client_sock):
    fp = BytesIO()
<<<<<<< HEAD
    id = 0
=======

    id = 0
    seekInd = 0
    
>>>>>>> 0dcaccf001ac440cb00401213d080be47961cf90
    while True:
        #fp = open("./01.wav", 'ab')
        recv = client_sock.recv(1024)  

        if len(recv):
            if id == 0:
                print(recv)
            write_to_fp(fp, recv)

<<<<<<< HEAD
            print(len(recv),len(fp.read()))
            id += 1

        if len(recv) > 1 and len(recv) < 1024 and id > 8:       

            print("aaa",len(recv),len(fp.read()))

            print(fp.read())

            
=======
            #fp.close()
            lenRecv = len(recv)
            print(lenRecv)
            id += lenRecv
>>>>>>> 0dcaccf001ac440cb00401213d080be47961cf90

        if len(recv) > 1 and len(recv) < 1000:
            fp.seek(0)
            song = AudioSegment.from_wav(fp)
            print("PPPPPPPPPPPPPPPPPPPPlayyyyy")
            play(song)


#-------------이부분만 반복--------------#

<<<<<<< HEAD
import time

 

 

HOST = '114.70.22.237'

PORT = 5053

 

 
=======
>>>>>>> 0dcaccf001ac440cb00401213d080be47961cf90

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))

thread1 = threading.Thread(target = recv, args=(client_socket, ))
thread1.start()