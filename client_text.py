#라즈베리파이 클라이언트 개발
#실시간 수신 -> A{num}, 문장 끝 -> B{num}
#리스코어 수신 -> C{num}
#띄어쓰기 수신 -> D{num}

import socket
from _thread import *
import threading
from tkinter import *
from time import sleep
import pyaudio

chat_number = [0]
chat_cnt = 1
flag = 1
tag_flag = 0

def audio_receive(socket):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=10240, INPUT=True)
    while True:
        data = socket.recv(1024)
        if data:
            stream.write(data)
    socket.close()
    stream.stop_stream()
    stream.close()
    p.terminate()

def send(socket):
    global go_send, chat_cnt
    while True:
        if go_send:
            message = (message_input.get(1.0,"end")).rstrip()
            if message[0] != 'A' and message[0] != 'B' and message[0] != 'C' and message[0] != 'D' and message[0] != 'E' and message[0] != 'F':
                chat_log['state'] = 'normal'
                chat_log.insert("end",'손님' + '\n')
                chat_log.tag_add(str(chat_cnt) + 'C', str(chat_cnt) + ".0", str(chat_cnt) + ".end")
                chat_log.tag_config(str(chat_cnt) + 'C', foreground="black", font=("Arial", 8, "bold"),justify=RIGHT)
                chat_cnt = chat_cnt + 1
                chat_log.insert("end", message + '\n')
                chat_log['state'] = 'disabled'
                chat_log.see('end')
                chat_log.tag_add(str(chat_cnt) + 'C', str(chat_cnt) + ".0", str(chat_cnt) + ".end")
                chat_log.tag_config(str(chat_cnt) + 'C', foreground="green", font=("Arial", 14, "bold"),justify=RIGHT)
                chat_cnt = chat_cnt + 1
                #메세지 출력용
            elif message[0] == 'E':
                chat_log['state'] = 'normal'
                chat_log.insert("end",'[System] 통화가 시작됩니다.' + '\n')
                chat_log.tag_add(str(chat_cnt) + 'C', str(chat_cnt) + ".0", str(chat_cnt) + ".end")
                chat_log.tag_config(str(chat_cnt) + 'C', foreground="blue", font=("Arial", 10, "bold"),justify=CENTER)
                chat_cnt = chat_cnt + 1
                chat_log['state'] = 'disabled'
            elif message[0] == 'F':
                chat_log['state'] = 'normal'
                chat_log.insert("end",'[System] 이 통화는 청각장애인 분들의 원활한 통화를 위한 실시간 통역시스템이 작동하고 있습니다. 여유를 가지고 천천히 답변해주세요.' + '\n')
                chat_log.tag_add(str(chat_cnt) + 'C', str(chat_cnt) + ".0", str(chat_cnt) + ".end")
                chat_log.tag_config(str(chat_cnt) + 'C', foreground="blue", font=("Arial", 10, "bold"))
                chat_cnt = chat_cnt + 1
                chat_log['state'] = 'disabled'
            socket.send(message.encode())
            message_input.delete(1.0, "end")
            go_send = False
        else:
            if go_out:
                socket.close()
                exit()
            sleep(0.1)

def receive(socket):
    global chat_cnt, flag, tag_flag
    while True:
        try:
            data = socket.recv(1024)
            data = data.decode()
            if(len(data)==4 or len(data)==1): continue
            if data[0]=='A':
                print("A")
                index_num = int(data[data.find('{') + 1:data.find('}')])
                chat_log['state'] = 'normal'
                if flag == 1:
                    print("flag 1")
                    chat_log.insert(str(chat_cnt) + ".0",'점주' + '\n')
                    chat_log.tag_add(str(chat_cnt) + 'C', str(chat_cnt) + ".0", str(chat_cnt) + ".end")
                    chat_log.tag_config(str(chat_cnt) + 'C', foreground="black", font=("Arial", 8, "bold"))
                    chat_cnt = chat_cnt + 1
                    print(chat_cnt)
                    chat_number.append(chat_cnt)
                    chat_log.insert("end", str(data[data.find('}') + 1:]) + ' ')
                    if tag_flag == 0:
                        print("flag 1 tag_flag 0")
                        chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                        chat_log.tag_config(chat_number[index_num], foreground="red", font=("Arial", 14, "bold"))
                        tag_flag = 1
                    else:
                        print("flag 1 tag_flag 1")
                        chat_log.tag_delete(chat_number[index_num])
                        chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                        chat_log.tag_config(chat_number[index_num], foreground="red", font=("Arial", 14, "bold"))
                    flag = 0
                else :
                    chat_log.insert(str(chat_cnt) + ".end",str(data[data.find('}') + 1:]) + ' ')
                    if tag_flag == 0:
                        print("flag 0 tag_flag 0")
                        chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                        chat_log.tag_config(chat_number[index_num], foreground="red", font=("Arial", 14, "bold"))
                        tag_flag = 1
                    else:
                        print("flag 0 tag_flag 1")
                        chat_log.tag_delete(chat_number[index_num])
                        chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                        chat_log.tag_config(chat_number[index_num], foreground="red", font=("Arial", 14, "bold"))
                chat_log.see('end')
                chat_log['state'] = 'disabled'
            elif data[0]=='T' :
                print("T")
                flag = 1
                tag_flag = 0
                index_num = int(data[data.find('{') + 1:data.find('}')])
                chat_log['state'] = 'normal'
                chat_log.delete(str(chat_number[index_num])+".0",str(chat_number[index_num])+".end")
                chat_log.insert(str(chat_number[index_num])+".0",str(data[data.find('}') + 1:]))
                chat_log.tag_delete(chat_number[index_num])
                chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                chat_log.tag_config(chat_number[index_num], foreground="red", font=("Arial", 14, "bold"))
                chat_log.insert("end",'\n')
                chat_log.see('end')
                chat_cnt = chat_cnt + 1
                print(chat_cnt)
                chat_log['state'] = 'disabled'
            elif data[0]=='C' or data[0]=='D':
                if data[0]=='C': print('C')
                if data[0]=='D': print('D')
                index_num = int(data[data.find('{') + 1:data.find('}')])
                chat_log['state'] = 'normal'
                chat_log.delete(str(chat_number[index_num])+".0",str(chat_number[index_num])+".end")
                chat_log.insert(str(chat_number[index_num])+".0",str(data[data.find('}') + 1:]))
                chat_log.tag_delete(chat_number[index_num])
                chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                chat_log.tag_config(chat_number[index_num], foreground="red", font=("Arial", 14, "bold"))
                chat_log.see('end')
                chat_log['state'] = 'disabled'
        except ConnectionAbortedError as e:
            chat_log['state'] = 'normal'
            chat_log.insert("end", '\n[System] 통화가 종료됩니다.\n')
            chat_log['state'] = 'disabled'
            exit()

def login():
    # 서버의 ip주소 및 포트
    HOST = ip_entry.get(); PORT = int(port_entry.get())
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    #client_socket_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client_socket_audio.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #client_socket_audio.settimeout(10)
    #client_socket_audio.connect((HOST, PORT + 1))

    threading.Thread(target=send, args= (client_socket,)).start()
    threading.Thread(target=receive, args= (client_socket,)).start()
    #threading.Thread(target=audio_receive, args=(client_socket_audio,)).start()
    exit()

def try_login():
    global go_out, chat_cnt
    start_new_thread(login,())
    login_button['state'] = 'disabled'
    logout_button['state'] = 'active'
    ip_entry['state'] = 'readonly'
    port_entry['state'] = 'readonly'
    go_out = False

def try_logout():
    global go_out
    login_button['state'] = 'active'
    logout_button['state'] = 'disabled'
    ip_entry['state'] = 'normal'
    port_entry['state'] = 'normal'
    go_out = True

def set_go_send(event):
    global go_send
    go_send = True

go_out, go_send = False, False
c_root = Tk()
c_root.geometry('500x500')
c_root.title('Deep Listener Receiver')
c_root.resizable(False, False)

''' Top Menu '''
Label(c_root, text = 'Server IP : ').place(x=20, y=20)
Label(c_root, text = 'Port : ').place(x=250, y=20)
ip_entry = Entry(c_root, width=14); ip_entry.place(x=83, y=21)
ip_entry.insert(0,'114.70.22.237')
port_entry = Entry(c_root, width=5); port_entry.place(x = 290, y=21)
port_entry.insert(0,'5052')
login_button = Button(c_root,text='Log In', command=try_login); login_button.place(x=350, y=18)
logout_button = Button(c_root,text='Log Out',state = 'disabled', command = try_logout); logout_button.place(x=420, y=18)

''' Middle Menu '''
chat_frame = Frame(c_root)
scrollbar = Scrollbar(chat_frame) ; scrollbar.pack(side='right',fill='y')
chat_log = Text(chat_frame, width = 62, height = 24, state = 'disabled', yscrollcommand = scrollbar.set, padx = 6, pady = 6); chat_log.pack(side='left')#place(x=20, y=60)
scrollbar['command'] = chat_log.yview
#chat_log.image_create 이거 사용
chat_frame.place(x=20, y=60)
message_input = Text(c_root, width = 55, height = 4) ; message_input.place(x=20,y = 390)
send_button = Button(c_root, text = 'Send', command = lambda: set_go_send(None)); send_button.place(x=430, y=405)
message_input.bind("<Return>",set_go_send)

''' Bottom Menu '''
close_button = Button(c_root,text='Close',command=exit); close_button.place(x=200, y = 460)

c_root.mainloop()