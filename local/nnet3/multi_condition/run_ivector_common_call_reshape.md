# run_ivector_common 통화 데이터 전처리 추가

## Code

  ```shell
  echo "$0: generating phone call noise"
  sed -i '2~2 s\$\sox -t wav - -r 8k -t wav - | sox -t wav - -r 16k -t wav - | sox -t wav - -t wav - highpass 100 | sox -t wav - -t wav - lowpass 1000 | sox -t wav - -t wav - dither -s |\g' data/${trainset}/wav.scp
  sed -i '2~8 s\$\sox -t wav - -t wav - gain 16 |\g' data/${trainset}/wav.scp
  ```


## Meaning

  1. 통화 환경과 일치하는 음성 데이터 구축 및 학습
  2. sox pipeline을 구축하여 체계적 음성 데이터 전처리
  3. 유무선 통신 환경에서 사용되는 코덱 반영



## 유무선 통신 통화 코덱

  - 현재 상용화 된 코덱 : G.729a [picture G.729a]
  - 코덱 활용에는 유료화 문제가 있음
  - sox를 활용하여 최대한 코덱과 유사한 전처리 진행



## Analog to Digital Conversion

  - 표본화(Sampling), 양자화(Quantization), 부호화(Coding)과정 거침
  - 나이퀴스트 표준화 이론에 따라 샘플링 2배
  - decoding 과정에서 노이즈를 줄이기 위해 dither 과정을 거침



## 코드 해석

  1. wav sample rate이 16000Hz 이므로 기본 샘플링을 8000Hz로 설정
   - sox input.wav -r 8k output.wav
  2. sample rate 8000Hz -> 16000Hz
   - sox input.wav -r 16k output.wav
  3. 통화 코덱과 유사한 전처리를 위해 100-1000Hz bandpass filter 적용
   - sox input.wav output.wav lowpass 1000
   - sox input.wav output.wav highpass 100
  4. decoing 과정 노이즈 추가 효과 삽입
   - sox input.wav output.wav dither -s
  5. 1~4과정은 MFCC의 효율적인 특징 추출을 위해 짝수 데이터에 삽입

  6. 추가 gain에 따른 학습을 위해 8번째 데이터마다 gain 16db
   - sox input.wav output.wav gain 16