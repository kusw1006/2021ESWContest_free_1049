#!/usr/bin/python3
from hangul_utils import join_jamos
import sys

# \uc790\uc74c-\ucd08\uc131/\uc885\uc131
cons = {'r':'\u3131', 'R':'\u3132', 's':'\u3134', 'S':'\u3134', 'e':'\u3137', 'E':'\u3138', 'f':'\u3139', 'F':'\u3139', 'a':'\u3141', 'A':'\u3141', 'q':'\u3142', 'Q':'\u3143', 't':'\u3145', 'T':'\u3146',
           'd':'\u3147', 'D':'\u3147', 'w':'\u3148', 'W':'\u3149', 'c':'\u314a', 'C':'\u314a', 'z':'\u314b', 'Z':'\u314b', 'x':'\u314c', 'X':'\u314c', 'V':'\u314d', 'v':'\u314d', 'G':'\u314e', 'g':'\u314e'}
# \ubaa8\uc74c-\uc911\uc131
vowels = {'k':'\u314f', 'K':'\u314f', 'o':'\u3150', 'i':'\u3151', 'O':'\u3152', 'j':'\u3153', 'J':'\u3153', 'p':'\u3154',
        'u':'\u3155', 'U':'\u3155', 'P':'\u3156', 'h':'\u3157', 'H':'\u3157', 'Hk':'\u3158', 'hK':'\u3158', 'HK':'\u3158', 'hk':'\u3158', 'ho':'\u3159', 'Ho':'\u3159', 'hO':'\u3159', 'HO':'\u3159', 
        'hl':'\u315a', 'Hl':'\u315a', 'hL':'\u315a', 'HL':'\u315a', 'y':'\u315b', 'Y':'\u315b', 'n':'\u315c', 'N':'\u315c','nj':'\u315d', 'Nj':'\u315d', 'nJ':'\u315d', 'NJ':'\u315d', 'np':'\u315e',
        'Np':'\u315e', 'nP':'\u315e', 'NP':'\u315e', 'nl':'\u315f', 'Nl':'\u315f', 'nL':'\u315f', 'NL':'\u315f', 'b':'\u3160', 'B':'\u3160', 'm':'\u3161', 'M':'\u3161', 'Ml':'\u3162', "mL":'\u3162', 
        'ML':'\u3162', 'ml':'\u3162', 'l':'\u3163', 'L':'l'}

# \uc790\uc74c-\uc885\uc131
cons_double = {'rt':'\u3133', 'sw':'\u3135', 'sg':'\u3136', 'fr':'\u313a', 'fa':'\u313b', 'fq':'\u313c', 'ft':'\u313d', 'fx':'\u313e', 'fv':'\u313f', 'fg':'\u3140', 'qt':'\u3144'}

def engkor(text):
    result = ''   # \uc601 > \ud55c \ubcc0\ud658 \uacb0\uacfc
    
    # 1. \ud574\ub2f9 \uae00\uc790\uac00 \uc790\uc74c\uc778\uc9c0 \ubaa8\uc74c\uc778\uc9c0 \ud655\uc778
    vc = '' 
    for t in text:
        if t in cons :
            vc+='c'
        elif t in vowels:
            vc+='v'
        else:
            vc+='!'
	
    # cvv \u2192 fVV / cv \u2192 fv / cc \u2192 dd 
    vc = vc.replace('cvv', 'fVV').replace('cv', 'fv').replace('cc', 'dd')
	
    
    # 2. \uc790\uc74c / \ubaa8\uc74c / \ub450\uae00\uc790 \uc790\uc74c \uc5d0\uc11c \uac80\uc0c9
    i = 0
    while i < len(text):
        v = vc[i]
        t = text[i]

        j = 1
        # \ud55c\uae00\uc77c \uacbd\uc6b0
        try:
            if v == 'f' or v == 'c':   # \ucd08\uc131(f) & \uc790\uc74c(c) = \uc790\uc74c
                result+=cons[t]

            elif v == 'V':   # \ub354\ube14 \ubaa8\uc74c
                result+=vowels[text[i:i+2]]
                j+=1

            elif v == 'v':   # \ubaa8\uc74c
                result+=vowels[t]

            elif v == 'd':   # \ub354\ube14 \uc790\uc74c
                result+=cons_double[text[i:i+2]]
                j+=1
            else:
                result+=t
                
        # \ud55c\uae00\uc774 \uc544\ub2d0 \uacbd\uc6b0
        except:
            if v in cons:
                result+=cons[t]
            elif v in vowels:
                result+=vowels[t]
            else:
                result+=t
        
        i += j


    return join_jamos(result)


try:
    # Linux & Mac \uc6a9 \ucf54\ub4dc
    import sys
    import tty
    import termios

    def getkey():
        """\ub2e8\uc77c\ud0a4 \ub204\ub974\ub294 \uac83\uc744 \ubc1b\uc544\uc634"""
        fd = sys.stdin.fileno()
        original_attributes = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, original_attributes)
        return ch
except:
    print("xxxx")


import os
sen = []
sens = ""
while True:
    try:
        txt = getkey()
        if(txt == ']'):
            sen.pop()
        elif(txt == '!'):
            break
        elif(txt == '\''):
            sen.clear()
            os.system('clear')
        else:
            sen.append(txt)
        sens = "".join(sen)
        print('(\uc885\ub8cc: !)', engkor(sens))
    except:
        print('\ud0a4 \uc785\ub825 \uc624\ub958')
