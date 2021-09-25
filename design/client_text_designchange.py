#라즈베리파이 클라이언트 개발
#실시간 수신 -> A{num}, 문장 끝 -> B{num}
#리스코어 수신 -> C{num}
#띄어쓰기 수신 -> D{num}

import socket
from _thread import *
import threading
from tkinter import *
from time import sleep
from hangul_utils import join_jamos
import sys
import os
import subprocess
# import pyaudio

chat_number = [0] #각 index id에 맞춘 줄을 기억하기 위한 리스트
chat_cnt = 1 #줄 수를 count하는 변수
flag = 1 #A값에서 제일 처음 들어온 변수인지 체크하는 플래그
tag_flag = 0 #이전에 사용된 mark tag인지 확인하기 위한 플래그
pre_index_num = 0 #이전 index_num을 기억하는 용도

sen = []
sens = ""
stop_send = True
sft = False

chat_log = False
message_input = False
client_socket = False

# 자음-초성/종성
cons = {'r':'ㄱ', 'R':'ㄲ', 's':'ㄴ', 'S':'ㄴ', 'e':'ㄷ', 'E':'ㄸ', 'f':'ㄹ', 'F':'ㄹ', 'a':'ㅁ', 'A':'ㅁ', 'q':'ㅂ', 'Q':'ㅃ', 't':'ㅅ', 'T':'ㅆ',
           'd':'ㅇ', 'D':'ㅇ', 'w':'ㅈ', 'W':'ㅉ', 'c':'ㅊ', 'C':'ㅊ', 'z':'ㅋ', 'Z':'ㅋ', 'x':'ㅌ', 'X':'ㅌ', 'V':'ㅍ', 'v':'ㅍ', 'G':'ㅎ', 'g':'ㅎ'}
# 모음-중성
vowels = {'k':'ㅏ', 'K':'ㅏ', 'o':'ㅐ', 'i':'ㅑ', 'O':'ㅒ', 'j':'ㅓ', 'J':'ㅓ', 'p':'ㅔ',
        'u':'ㅕ', 'U':'ㅕ', 'P':'ㅖ', 'h':'ㅗ', 'H':'ㅗ', 'Hk':'ㅘ', 'hK':'ㅘ', 'HK':'ㅘ', 'hk':'ㅘ', 'ho':'ㅙ', 'Ho':'ㅙ', 'hO':'ㅙ', 'HO':'ㅙ', 
        'hl':'ㅚ', 'Hl':'ㅚ', 'hL':'ㅚ', 'HL':'ㅚ', 'y':'ㅛ', 'Y':'ㅛ', 'n':'ㅜ', 'N':'ㅜ','nj':'ㅝ', 'Nj':'ㅝ', 'nJ':'ㅝ', 'NJ':'ㅝ', 'np':'ㅞ',
        'Np':'ㅞ', 'nP':'ㅞ', 'NP':'ㅞ', 'nl':'ㅟ', 'Nl':'ㅟ', 'nL':'ㅟ', 'NL':'ㅟ', 'b':'ㅠ', 'B':'ㅠ', 'm':'ㅡ', 'M':'ㅡ', 'Ml':'ㅢ', "mL":'ㅢ', 
        'ML':'ㅢ', 'ml':'ㅢ', 'l':'ㅣ', 'L':'l'}

# 자음-종성
cons_double = {'rt':'ㄳ', 'sw':'ㄵ', 'sg':'ㄶ', 'fr':'ㄺ', 'fa':'ㄻ', 'fq':'ㄼ', 'ft':'ㄽ', 'fx':'ㄾ', 'fv':'ㄿ', 'fg':'ㅀ', 'qt':'ㅄ'}

def engkor(text):
    result = ''   # 영 > 한 변환 결과
    
    # 1. 해당 글자가 자음인지 모음인지 확인
    vc = '' 
    for t in text:
        if t in cons :
            vc+='c'
        elif t in vowels:
            vc+='v'
        else:
            vc+='!'
	
    # cvv → fVV / cv → fv / cc → dd 
    vc = vc.replace('cvv', 'fVV').replace('cv', 'fv').replace('cc', 'dd')
	
    
    # 2. 자음 / 모음 / 두글자 자음 에서 검색
    i = 0
    while i < len(text):
        v = vc[i]
        t = text[i]

        j = 1
        # 한글일 경우
        try:
            if v == 'f' or v == 'c':   # 초성(f) & 자음(c) = 자음
                result+=cons[t]

            elif v == 'V':   # 더블 모음
                result+=vowels[text[i:i+2]]
                j+=1

            elif v == 'v':   # 모음
                result+=vowels[t]

            elif v == 'd':   # 더블 자음
                result+=cons_double[text[i:i+2]]
                j+=1
            else:
                result+=t
                
        # 한글이 아닐 경우
        except:
            if v in cons:
                result+=cons[t]
            elif v in vowels:
                result+=vowels[t]
            else:
                result+=t
        
        i += j


    return join_jamos(result)
    

def send(socket):
    global go_send, chat_cnt, message_input, chat_log, sen
    while True:
        if go_send:
            message = (message_input.get(1.0,"end")).rstrip() #입력 된 메세지 읽어오기
            sen.clear()
            message_input['state'] = 'normal'
            message_input.delete("1.0","end")
            message_input['state'] = 'disabled'
            if message[0] != 'A' and message[0] != 'C' and message[0] != 'D' and message[0] != 'T' and message[0] != 'E' and message[0] != 'F':
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
            elif message[0] == 'F':
                chat_log['state'] = 'normal'
                chat_log.insert("end",'[System] 통화가 시작됩니다.' + '\n')
                chat_log.tag_add(str(chat_cnt) + 'C', str(chat_cnt) + ".0", str(chat_cnt) + ".end")
                chat_log.tag_config(str(chat_cnt) + 'C', foreground="blue", font=("Arial", 10, "bold"),justify=CENTER)
                chat_cnt = chat_cnt + 1
                chat_log['state'] = 'disabled'
                #통화 시작 알림
            elif message[0] == 'E':
                chat_log['state'] = 'normal'
                chat_log.insert("end",'[System] 이 통화는 청각장애인 분들의 원활한 통화를 위한 실시간 통역시스템이 작동하고 있습니다. 여유를 가지고 천천히 답변해주세요.' + '\n')
                chat_log.tag_add(str(chat_cnt) + 'C', str(chat_cnt) + ".0", str(chat_cnt) + ".end")
                chat_log.tag_config(str(chat_cnt) + 'C', foreground="blue", font=("Arial", 10, "bold"))
                chat_cnt = chat_cnt + 1
                chat_log['state'] = 'disabled'
                #시스템 알림
            socket.send(message.encode()) #서버로 텍스트 보내기
            message_input.delete(1.0, "end") #입력창 비우기
            go_send = False
        else:
            if go_out:
                socket.close()
                exit()
            sleep(0.1)
            
def send_message(event):
    global sen, sens, go_send, message_input, sft
    print(2)
    if sft:
        try:
            if stop_send:
                socket.close()
                exit()
            #txt = getkey()
            txt = event.keycode
            print(txt)
            if(txt == 22):
                sen.pop()
            elif(txt == 36):
                go_send = True
                sen.clear()
            elif(txt == 24):
                sen.append('Q')
            elif(txt == 25):
                sen.append('W')
            elif(txt == 26):
                sen.append('E')
            elif(txt == 27):
                sen.append('R')
            elif(txt == 28):
                sen.append('T')
            elif(txt == 29):
                sen.append('Y')
            elif(txt == 30):
                sen.append('U')
            elif(txt == 31):
                sen.append('I')
            elif(txt == 32):
                sen.append('O')
            elif(txt == 33):
                sen.append('P')
            elif(txt == 38):
                sen.append('A')
            elif(txt == 39):
                sen.append('S')
            elif(txt == 40):
                sen.append('D')
            elif(txt == 41):
                sen.append('F')
            elif(txt == 42):
                sen.append('G')
            elif(txt == 43):
                sen.append('H')
            elif(txt == 44):
                sen.append('J')
            elif(txt == 45):
                sen.append('K')
            elif(txt == 46):
                sen.append('L')
            elif(txt == 52):
                sen.append('Z')
            elif(txt == 53):
                sen.append('X')
            elif(txt == 54):
                sen.append('C')
            elif(txt == 55):
                sen.append('V')
            elif(txt == 56):
                sen.append('B')
            elif(txt == 57):
                sen.append('N')
            elif(txt == 58):
                sen.append('M')
            elif(txt == 65):
                sen.append(' ')
            else:
                sen.append('')
            sens = "".join(sen)
            message_input['state'] = 'normal'
            message_input.delete("1.0","end")
            message_input.insert("1.0",engkor(sens))
            message_input['state'] = 'disabled'
            print(1)
        except:
            print('키 입력 오류')
        sft = False
    else:
        try:
            if stop_send:
                socket.close()
                exit()
            #txt = getkey()
            txt = event.keycode
            print(txt)
            if(txt == 22):
                sen.pop()
            elif(txt == 36):
                go_send = True
            elif(txt == 24):
                sen.append('q')
            elif(txt == 25):
                sen.append('w')
            elif(txt == 26):
                sen.append('e')
            elif(txt == 27):
                sen.append('r')
            elif(txt == 28):
                sen.append('t')
            elif(txt == 29):
                sen.append('y')
            elif(txt == 30):
                sen.append('u')
            elif(txt == 31):
                sen.append('i')
            elif(txt == 32):
                sen.append('o')
            elif(txt == 33):
                sen.append('p')
            elif(txt == 38):
                sen.append('a')
            elif(txt == 39):
                sen.append('s')
            elif(txt == 40):
                sen.append('d')
            elif(txt == 41):
                sen.append('f')
            elif(txt == 42):
                sen.append('g')
            elif(txt == 43):
                sen.append('h')
            elif(txt == 44):
                sen.append('j')
            elif(txt == 45):
                sen.append('k')
            elif(txt == 46):
                sen.append('l')
            elif(txt == 52):
                sen.append('z')
            elif(txt == 53):
                sen.append('x')
            elif(txt == 54):
                sen.append('c')
            elif(txt == 55):
                sen.append('v')
            elif(txt == 56):
                sen.append('b')
            elif(txt == 57):
                sen.append('n')
            elif(txt == 58):
                sen.append('m')
            elif(txt == 65):
                sen.append(' ')
            elif(txt == 62):
                sft = True
            else:
                sen.append('')
            if sft == False:
                sens = "".join(sen)
                message_input['state'] = 'normal'
                message_input.delete("1.0","end")
                message_input.insert("1.0",engkor(sens))
                message_input['state'] = 'disabled'
            print(1)
        except:
            print('키 입력 오류')

def receive(socket):
    global chat_cnt, flag, tag_flag, pre_index_num, chat_log
    while True:
        try:
            data = socket.recv(1024) #서버로부터 텍스트 받아오기
            data = data.decode() #디코드
            if(len(data)==1): continue #비어있을 경우 continue
            if data[0]=='A': #A로 들어오는 경우
                print("A")
                index_num = int(data[data.find('{') + 1:data.find('}')]) #index id 추출
                if(pre_index_num != index_num): #만약 index id에 변화가 있다면 플래그 변수 초기화
                    flag = 1
                    tag_flag = 0
                    pre_index_num = index_num
                print(index_num)
                chat_log['state'] = 'normal'
                if flag == 1: #처음 들어온 A 값이라면
                    print("flag 1")
                    chat_log.insert(str(chat_cnt) + ".0",'점주' + '\n')
                    chat_log.tag_add(str(chat_cnt) + 'C', str(chat_cnt) + ".0", str(chat_cnt) + ".end")
                    chat_log.tag_config(str(chat_cnt) + 'C', foreground="seashell", font=("Arial", 8, "bold"))
                    chat_cnt = chat_cnt + 1 #점주라는 이름 띄우기
                    print(chat_cnt)
                    chat_number.append(chat_cnt) #index id에 맞는 줄 저장
                    chat_log.insert("end",'\n') #줄 띄워주기
                    chat_log.see('end')
                    chat_cnt = chat_cnt + 1
                    chat_log.insert(str(chat_number[index_num]) + ".end", str(data[data.find('}') + 1:]) + ' ') #텍스트 입력
                    if tag_flag == 0: #이전에 tag된 적이 없다면
                        print("flag 1 tag_flag 0")
                        chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                        chat_log.tag_config(chat_number[index_num], font=("Arial", 14, "bold"))
                        chat_log['fg']='#fdfcc0'
                        tag_flag = 1
                    else: #이전에 tag된 적이 있다면
                        print("flag 1 tag_flag 1")
                        chat_log.tag_delete(chat_number[index_num])
                        chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                        chat_log.tag_config(chat_number[index_num], font=("Arial", 14, "bold"))
                        chat_log['fg']='#fdfcc0'
                    flag = 0
                else :
                    chat_log.insert(str(chat_number[index_num]) + ".end",str(data[data.find('}') + 1:]) + ' ')
                    if tag_flag == 0:#이전에 tag된 적이 없다면
                        print("flag 0 tag_flag 0")
                        chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                        chat_log.tag_config(chat_number[index_num], font=("Arial", 14, "bold"))
                        chat_log['fg']='#fdfcc0'
                        tag_flag = 1
                    else:#이전에 tag된 적이 있다면
                        print("flag 0 tag_flag 1")
                        chat_log.tag_delete(chat_number[index_num])
                        chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                        chat_log.tag_config(chat_number[index_num], font=("Arial", 14, "bold"))
                        chat_log['fg']='#fdfcc0'
                chat_log.see('end')
                chat_log['state'] = 'disabled'
            elif data[0]=='C' or data[0]=='D' or data[0]=='T': #만약 rescore, decode, space 문장이 들어올 경우 문장 덮어쓰기
                if data[0]=='C': print('C')
                if data[0]=='D': print('D')
                if data[0]=='T': print('T')
                index_num = int(data[data.find('{') + 1:data.find('}')])
                print(index_num)
                chat_log['state'] = 'normal'
                chat_log.delete(str(chat_number[index_num])+".0",str(chat_number[index_num])+".end")
                chat_log.insert(str(chat_number[index_num])+".0",str(data[data.find('}') + 1:]))
                chat_log.tag_delete(chat_number[index_num])
                chat_log.tag_add(chat_number[index_num], str(chat_number[index_num]) + ".0", str(chat_number[index_num]) + ".end")
                chat_log.tag_config(chat_number[index_num], font=("Arial", 14, "bold"))
                chat_log['fg']='#fdfcc0'
                chat_log.see('end')
                chat_log['state'] = 'disabled'
        except ConnectionAbortedError as e: #예외 발생시 통화 종료
            chat_log['state'] = 'normal'
            chat_log.insert("end", '\n[System] 통화가 종료됩니다.\n')
            chat_log['state'] = 'disabled'
            exit()

def login():
    # 서버의 ip주소 및 포트
    global client_socket
    HOST = '114.70.22.237'; PORT = int('5052')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    subprocess.run(["./start_rec.sh"], shell=True)
    threading.Thread(target=send, args= (client_socket,)).start()
    threading.Thread(target=receive, args= (client_socket,)).start()
    #threading.Thread(target=send_message, args= (client_socket,)).start()
    exit()

def try_login():
    global go_out, chat_cnt
    start_new_thread(login,())
    #login_button['state'] = 'disabled'
    #logout_button['state'] = 'active'
    #ip_entry['state'] = 'readonly'
    #port_entry['state'] = 'readonly'
    go_out = False
    

def try_logout():
    global go_out
    #login_button['state'] = 'active'
    #logout_button['state'] = 'disabled'
    #ip_entry['state'] = 'normal'
    #port_entry['state'] = 'normal'
    go_out = True

def set_go_send(event):
    global go_send
    go_send = True

def createNewWindow():
    global message_input, chat_log, cllient_socket, stop_send
    root_x = app.winfo_rootx()
    root_y = app.winfo_rooty()
    c_root = Toplevel(app)
    c_root.geometry("%dx%d+%d+%d" % (1280,720,0,0))
    #c_root.wm_attributes("-topmost",1)
    c_root.title('실시간 통화 동시 통역 채팅 프로그램')
    c_root.resizable(False, False)
    chat_frame = Frame(c_root)
    wall_chat = PhotoImage(file = "chat.png")
    wall_label_chat = Label(c_root, image = wall_chat)
    wall_label_chat.place(x=0,y=0)
    
    photo = PhotoImage(file = "Home_resize.png")
    btn = Button(c_root, image = photo, command=c_root.destroy, background="midnight blue")
    btn.place(x=70,y=260)
    
    photo_menu = PhotoImage(file = "menu_resize.png")
    btn_menu = Button(c_root, image = photo_menu, background="midnight blue")
    btn_menu.place(x=70,y=320)
    
    scrollbar = Scrollbar(chat_frame) ; scrollbar.pack(side='right',fill='y')
    chat_log = Text(c_root, width = 115 , height = 22, state = 'disabled', yscrollcommand = scrollbar.set, padx = 6, pady = 6); chat_log.pack(side='left'); chat_log.place(x=250, y=70)
    chat_log['bg']='#0f1c33'
    scrollbar['command'] = chat_log.yview
    chat_frame.place(x=80, y=60)
    
    message_input = Text(c_root, width = 68, height = 5, font=("나눔 고딕", 15, "bold")) ; message_input.place(x=374,y = 530)
    message_input['fg']='#d0d9e8'
    message_input['bg']='#0f1c33'
    stop_send = False
    c_root.bind('<KeyPress>',send_message)
    #send_button = Button(c_root, text = 'Send', command = lambda: set_go_send(None)); send_button.place(x=430, y=405)
    #message_input.bind("<Return>",send_message)
    #close_button = Button(c_root,text='Close',command=exit); close_button.place(x=230, y = 660)
    c_root.mainloop()
    stop_send = True

def callback(event):
    email = (email_input.get(1.0,"end")).rstrip()
    password = (password_input.get(1.0,"end")).rstrip()
    if(email == "vvs@konkuk.ac.kr" and password == "1234"):
        try_login()
        createNewWindow()

go_out, go_send = False, False
app = Tk()
app.geometry("%dx%d+%d+%d" % (1280,720,0,0))
wall = PhotoImage(file = "base_image.png")
wall_label = Label(app, image = wall)
wall_label.place(x=0,y=0)
app.resizable(False, False)
app.title('Login')
email_input = Text(app, width = 30, height = 2, font=("나눔 고딕", 13, "bold")) ; email_input.place(x=465,y = 355)
email_input['fg']='#d0d9e8'
email_input['bg']='#0f1c33'
password_input = Text(app, width = 30, height = 2, font=("나눔 고딕", 13, "bold")) ; password_input.place(x=465,y = 440)
password_input['fg']='#d0d9e8'
password_input['bg']='#0f1c33'
app.bind('<Return>', callback)
loginphoto = PhotoImage(file = 'login_resize.png')
button = Button(app, image = loginphoto ,command=createNewWindow, background="midnight blue"); button.place(x=580, y=506)



#c_root = Tk()
#c_root.geometry('500x500')
#c_root.title('실시간 통화 동시 통역 채팅 프로그램')
#c_root.resizable(False, False)

''' Top Menu '''
#Label(c_root, text = 'Server IP : ').place(x=20, y=20)
#Label(c_root, text = 'Port : ').place(x=250, y=20)
#ip_entry = Entry(c_root, width=14); ip_entry.place(x=83, y=21)
#ip_entry.insert(0,'114.70.22.237')
#port_entry = Entry(c_root, width=5); port_entry.place(x = 290, y=21)
#port_entry.insert(0,'5052')
#login_button = Button(app,text='Log In', command=try_login); login_button.place(x=350, y=18)
#logout_button = Button(app,text='Log Out',state = 'disabled', command = try_logout); logout_button.place(x=420, y=18)

''' Middle Menu '''
#chat_frame = Frame(c_root)
#scrollbar = Scrollbar(chat_frame) ; scrollbar.pack(side='right',fill='y')
#chat_log = Text(chat_frame, width = 55 , height = 18, state = 'disabled', yscrollcommand = scrollbar.set, padx = 6, pady = 6); chat_log.pack(side='left')#place(x=20, y=60)
#scrollbar['command'] = chat_log.yview
#chat_log.image_create 이거 사용
#chat_frame.place(x=20, y=60)
#message_input = Text(c_root, width = 45, height = 4) ; message_input.place(x=20,y = 390)
#send_button = Button(c_root, text = 'Send', command = lambda: set_go_send(None)); send_button.place(x=430, y=405)
#message_input.bind("<Return>",set_go_send)

''' Bottom Menu '''
#close_button = Button(c_root,text='Close',command=exit); close_button.place(x=200, y = 460)

app.mainloop()
