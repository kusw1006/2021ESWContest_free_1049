# allStart.sh

> 경로: /opt
>
> 작성자: 김한비



> tcp 한번에 세팅하기

```sh
#!/bin/bash 

tcp=$(ps aux | grep tcp | awk '{ print $2 }' | head -1 )
kill -9 $tcp
space=$(ps aux | grep run_sentence | awk '{ print $2 }' | head -1 )
kill -9 $space
tts=$(ps aux | grep run_tts | awk '{ print $2 }' | head -1 )
kill -9 $tts

final_mdl=/home/dcl2003/esw2021/test4/models/korean/zeroth/final.mdl
hclg_fst=/home/dcl2003/esw2021/test4/models/korean/zeroth/HCLG.fst
words_txt=/home/dcl2003/esw2021/test4/models/korean/zeroth/words.txt
online_conf=/home/dcl2003/esw2021/test4/models/korean/zeroth/conf/online.conf

dir=/home/dcl2003/esw2021/src
# post_decode_acwt=10.0
# lat_wspecifier="ark:|lattice-scale --acoustic-scale=$post_decode_acwt ark:- ark:- | gzip -c >$dir/lat.1.gz"

lat_wspecifier="ark:|gzip -c >$dir/lat.1.gz"

/opt/kaldi/src/online2bin/online2-tcp-nnet3-decode-faster --samp-freq=16000 --frames-per-chunk=20 --extra-left-context-initial=0 \
    --frame-subsampling-factor=3 --config=$online_conf --min-active=200 --max-active=7000 \
    --beam=15.0 --lattice-beam=6.0 --acoustic-scale=1.0 --port-num=5052 $final_mdl $hclg_fst $words_txt "$lat_wspecifier" &

sleep 5

char_file=/home/dcl2003/spacing/korean-spacing-model/resources/chars-4996
model_file=/home/dcl2003/spacing/korean-spacing-model/models/checkpoint-12.ckpt
training_config=/home/dcl2003/spacing/korean-spacing-model/resources/config.json 

cd /home/dcl2003/spacing/korean-spacing-model && python3 ./run_sentences.py --char-file $char_file --model-file $model_file --training-config $training_config &

sleep 7

cd /home/dcl2003/TTS && python3 ./run_tts.py &

# 실제 사용(라즈베리파이에서~)
# rec -r 16000 -e signed-integer -c 1 -b 16 -t raw  - | nc -n 114.70.22.237 5050
# sox /home/dcl2003/practice/16k.wav -t raw -c 1 -b 16 -r 16k -e s - | nc -n 114.70.22.237 5050



# SIGHUP, SIGINT SIGTERM 시그널이 발생하면 cleanup 함수 실행 


# trap "cleanup; exit" SIGHUP SIGINT SIGTERM 

# function cleanup() { 
#     echo "SIGNAL input" 
#     tcp=$(ps aux | grep tcp | awk '{ print $2 }' | head -1 )
#     kill -9 $tcp
#     space=$(ps aux | grep run_sentence | awk '{ print $2 }' | head -1 )
#     kill -9 $space
#     tts=$(ps aux | grep run_tts | awk '{ print $2 }' | head -1 )
#     kill -9 $tts
# }

# 터미널 용
# tcp=$(ps aux | grep tcp | awk '{ print $2 }' | head -1 )
# sudo kill -9 $tcp
# space=$(ps aux | grep run_sentence | awk '{ print $2 }' | head -1 )
# sudo kill -9 $space
# tts=$(ps aux | grep run_tts | awk '{ print $2 }' | head -1 )
# sudo kill -9 $tts

```

백그라운드로 실행 -> ctrl + c로 종료 불가 -> 시작할 때 마다 ps aux에서 찾아서 kill하고 시작

종속성 문제를 해결하기 위해 해당 폴더로 이동 후 실행

