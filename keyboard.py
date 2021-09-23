from hangul_utils import join_jamos
import sys

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


try:
    # Windows용 코드
    import msvcrt

    def getkey():
        """단일키 누르는 것을 받아옴"""
        return msvcrt.getch()

except ImportError:
    # Linux & Mac 용 코드
    import sys
    import tty
    import termios

    def getkey():
        """단일키 누르는 것을 받아옴"""
        fd = sys.stdin.fileno()
        original_attributes = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, original_attributes)
        return ch
import os
sen = []
while True:
    #os.system('clear')
    txt = getkey()
    if(txt == b'\x08'):
        sen.pop()
    elif(txt == b'\x21'):
        break
    else:
        sen.append(txt.decode('utf-8'))
    sens = "".join(sen)
    print('(종료: !)', engkor(sens))
