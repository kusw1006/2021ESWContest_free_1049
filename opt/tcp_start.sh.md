# tcp_start.sh

> 작성자: 김한비
>
> 경로: /opt/



> online2-tcp-nnet3-decode-faster로 tcp server 키는 거..(서버피시에서)
>
> 모델이랑 fst 등은 우리가 제작한 /home/dcl2003/esw어쩌구



> 이 코드는 server 키기만 함
>
> 실제 마이크 쓰거나 녹음파일 불러오려면 다른 bash에 실제사용 밑에 있는 코드 양식으로 입력해줘야함



> lat_wspecifier 추가

```sh
final_mdl=/home/dcl2003/esw2021/test/models/korean/zeroth/final.mdl
hclg_fst=/home/dcl2003/esw2021/test/models/korean/zeroth/HCLG.fst
words_txt=/home/dcl2003/esw2021/test/models/korean/zeroth/words.txt
online_conf=/home/dcl2003/esw2021/test/models/korean/zeroth/conf/online.conf

dir=/home/dcl2003/esw2021/src
lat_wspecifier="ark:|gzip -c >$dir/lat.1.gz"

/opt/kaldi/src/online2bin/online2-tcp-nnet3-decode-faster --samp-freq=16000 --frames-per-chunk=20 --extra-left-context-initial=0 \
    --frame-subsampling-factor=3 --config=$online_conf --min-active=200 --max-active=7000 \
    --beam=15.0 --lattice-beam=6.0 --acoustic-scale=1.0 --port-num=5051 $final_mdl $hclg_fst $words_txt "$lat_wspecifier"


# 실제 사용(라즈베리파이에서~)
# rec -r 16000 -e signed-integer -c 1 -b 16 -t raw  - | nc -n 114.70.22.237 5050
# sox /home/dcl2003/practice/16k.wav -t raw -c 1 -b 16 -r 16k -e s - | nc -n 114.70.22.237 5050
```



- sample rate(Hz)

8kHz: 디지털 전화

44.1kHz: 오디어 컴팩트 디스크

96 or 192kHz: 전문 오디오 시스템

> 칼디 학습 rate가 16000이라 그냥 16000으로 설정하는게 맞을듯



- data encoding

인코딩 방식.. 부호있는 정수(PCM&FLAC), 부동 소수점, ADPCM...



- channel

파일에 포함된 오디오 채널 수(주로 모노&스테레오)



- AUDIODRIVER: 오디오 드라이버 변경

ex) ALSA, OSS, SUNAU, AO

```sh
export AUDIODRIVER=ALSA
```



- AUDIODEV: 기본 오디오 장치 대체

```sh
export AUDIODEV=hw:0
sox... -t alsa

export AUDIODEV-/dev/dsp2
sox... -t oss
```



nc -N -> nc -n

-c 2 -> -c 1



