# -*- coding: UTF-8 -*-
import os
from glob import glob
from io import BytesIO

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


def tts(word_str, toSlow=True):
    word=word_str.decode('utf-8')
    tts = gTTS(text=word, lang="ko", slow=toSlow)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    # simpleaudio가 있어야 작동한다.
    song = AudioSegment.from_file(fp, format="mp3")
    play(song)

    # ffcache 파일이 생성돼서 glob wild card로 전부 삭제
    fileList = glob("./ffcache*")
    for filePath in fileList:
        os.remove(filePath)
        
        
if __name__ == "__main__":
    start_voice= "이 통화는 청각장애인분들을 위한 실시간 음성 시스템이 지원되는 통화입니다. 여유를 가지고 말씀해 주시면 감사하겠습니다."
    tts(start_voice, toSlow=False)
    while True:        
        mention=raw_input("input: ")
        if mention == 'q':
            print("대화를 종료합니다.")
            break
        else :
            tts(mention, toSlow=False)# 안녕 빠르게 발음
    
        #tts(mention, toSlow=True)  # 안녕 느리게 발음

