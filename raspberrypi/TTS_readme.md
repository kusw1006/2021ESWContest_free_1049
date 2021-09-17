# TTS
## 최종

Python Library gTTS(Google Text-to-Speech)


### 사전작업
```
$ pip install gTTS
$ pip install pydub
$ pip install simpleaudio
```
simpleaudio의 경우 pip3로 다운받는 등의 오류해결 과정 거침

예시)
```
$ sudo -H pip3 install --upgrade --ignore-installed pip setuptools
$ pip3 install simpleaudio
```

### 코드
` $ python tts_gtts.py`

**비고**

1. 한국어 입력 및 이용을 위해 type을 `str` -> `utf-8` 로 변환  
    ex) `word=word_str.decode('utf-8')`

2. python2.x 환경에서 문자열을 input으로 받아올 수 없기 때문에
`raw_input(" ")`으로 대체

3. 프로그램 시작 전 음성 안내를 위한 코드부분 추가
4. `q`를 누르면 대화가 종료될 수 있도록 함.


### 실행
```
$ cd TTS
$ python tts_gtts.py
```

+) 통화 내에서도 잘 작동하는 것을 확인함.


