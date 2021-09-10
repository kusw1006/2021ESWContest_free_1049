# Raspberry pi
## Audio Connect
---
### 9/7 
phone -> raspberry pi  
> : bluetooth 이용  
>  
>> **개선점**  
>> bluetooth 연결이 안 될 때가 있음 *꽤나 자주  
>> --> bluetooth 동글을 이용해보기  
>> 미디어 오디오는 잘 넘어가나 통화 오디오는 넘어가지 않음  
>> 내부 설정이 필요한지, 라즈베리 자체의 hw 문제인지 확인 필요  
>> --> 동글 이용시 쌍방 연결 + 통화 연결이 가능할지도 (기대중)  
>> --> Zoom 등의 웹 회의를 이용해도 통화는 넘어가지 않음

raspberry pi -> phone
> : soundCard와 3.5 AV Jack 포트 이용  
> 미디어 출력 잘 됨  
> 통화 연결 시에도 라즈베리파이의 소리가 잘 넘어오는 것을 확인  
> (외부 소리 x)
>> **개선점**  
>> 블루투스로 쌍방향 통신이 가능한지 확인(추가적)  

<br/>
+) Test용 녹음 명령어  

녹음:  
`$ arecord --format=S16_LE --duration={원하는sec} --rate=16000 --file-type={TYPE} {FILENAME}.{TYPE}`  
재생:  
`$ aplay --format=S16_LE --rate=16000 {FILENAME}.{TYPE}`

<br/>

## 추가적 문제점
---
- 가끔 SD 카드 인식 불량으로 화면이 안 들어오는 경우가 있음  
이건 라즈베리파이 고유의 문제로 모든 데이터셋이 정리되고 나면
새로운 SD카드를 사용해서 아예 안 빼는 조건으로 연결하던지 해야 될듯  
혹은 usb 포트 등을 이용하던지 혹은 이외의 포트 등을 이용하던지  
<br/>
- **rec 명령어를 통한 서버에서 음성 받아오기가 안 됨**  
`$ sudo apt-get install sox`  
오류 시 별도의 라이브러리 추가 설치  
ex) [error] sox FAIL formats: no handler for file extention 'mp3'  
`$ sudo apt-get install libsox-fmt-mp3`
 ---------------FAIL
<br/>
- phone->raspberrypi 녹음 시 통신 문제 발생  
예를 들어 어떤 부분만 2배속

<br/>


## Google API
---
### STT
#### 기본설정
> `$ export GOOGLE_APPLICATION_CREDENTIALS='/경로/key이름.json`  
> : 단축어 gst  
> `$ gcloud auth activate-service-account --key-file="/경로/key이름.json"`  
> : 단축어 ______  
> `$ sudo chmod 777 'key이름.json'`  
> `$ gcloud init`

실행  
`stt/test1.py`

휴대폰의 소리가 잘 넘어오는 것을 확인함.  
google SDK 파일 설치 필요 (새로운 sd card 사용 시)

<br/>

### TTS
#### 기본설정
> `$ export GOOGLE_APPLICATION_CREDENTIALS='/경로/key이름.json`  
> : 단축어 gst  
> `$ gcloud auth activate-service-account --key-file="/경로/key이름.json"`  
> : 단축어 gclauthtts  
> `$ sudo chmod 777 'key이름.json'`  
> `$ gcloud init`  

실행  
`tts/youngqnew.py`  
--> 실시간으로 받아오는 건 가능, 저장 말고 재생하도록 파일 수정  
--> 영어 버리고 한국어만 해서 모든 걸 다 한국어로 하도록 하기

### 9/8

**블루투스연결 오류**  

동글 이용 과정에서 기존 Onboard 블루투스를 Disalbe함  
다시 Enable하려 했으나 삭제됨. 작동 x  
+) `$bluetoothctl` 도 먹히지 않음

동글을 lsusb를 통해서는 인식이 가능하나 hciconfig등의 bluetooth 인식 명령어에서는 인식이 되지 않음

동글이 5.0 이어서인지, 윈도우 기준 동글이라서인지 모르겠음

동글은 actto 제품이나 Linux환경에서 쓰려면 mpow의 드라이버를 이용함.

<br/>

**TTS**  

실시간 문자열 인식에서 문자열 리스트로 만들지 못했음  
문자열은 받아오나 이걸 영어인지 한국어인지 구분을 못 해서
그냥 영어로 받아왔었음.

그래서 영어는 버리고 기본을 한국어로 해서 코드 수정함.
(업로드 필요)

완료 파일을 저장하는 부분을 실시간으로 송출할 수 있게 코드수정 필요



9/10

`$pulseaudio`  
켜져있다면 `$pulseaudio --kill` 후 다시 키기 `$pulseaudio --start`

`$pactl load-module module-bluetooth-discover`  
`$bluetoothctl`  
만약 `scan on` 에서 안 뜨면 `remove ______________` 한 후 다시 `scan on`

<br/>

**bluetooth 연결 시**  
phone->rasppi bluetooth로 통신 가능  
즉 통화 시 상대의 목소리가 라즈베리에 들어감.

하지만 다시 raspi -> phone 의 소리가 건너가지 않음

의심: 블루투스 스피커로 rasp는 보내고 있는데 phone에서 이를 무시하는 경우

> 사운드카드 연결 또는 블루투스 둘 중 하나만 폰에서 인식 가능



**9/10 최종**

라즈베리파이는 블루투스와 잭 모두 동시에 가능함.  
하지만 동시에 같은 폰에서는 쌍방향은 불가능함.(둘 중 하나만 가능)  
그래서 다른 기기에 잭을 연결하고, 폰에서 블루투스로 넘겼을 때 기기에서 소리가 들림  
폰에서 블루투스 마이크 소리를 받아야 하는데 그게 일단은 불가능함.
<br/>  
**SoundWire**  
`$./SoundWireServer`    
진행 시 라베파->폰 소리 가능(잭 연결 없이)
<br/>
<br/>
> 추가적으로 폰->라베파도 이걸로 가능한지, 그리고 블루투스 연결 환경 또는 통화 환경에서도 가능한지 검토가 필요함.