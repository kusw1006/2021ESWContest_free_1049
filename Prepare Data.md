# Prepare Data



## Create files

### data/train

#### 1. text

> corpus에 있는 문장만 사용

```shell
utt_id WORD1 WORD2 WORD3 ...

ex) 
110236_20091006_82330_F_0001 I’M WORRIED ABOUT THAT
110236_20091006_82330_F_0002 AT LEAST NOW WE HAVE THE BENEFIT
110236_20091006_82330_F_0003 DID YOU EVER GO ON STRIKE
```



#### 2. segments

> 각 발언의 시작 및 종료시간 포함

```shell
utt_id file_id start_time end_time

ex)
110236_20091006_82330_F_001 110236_20091006_82330_F 0.0 3.44
110236_20091006_82330_F_002 110236_20091006_82330_F 4.60 8.54
110236_20091006_82330_F_003 110236_20091006_82330_F 9.45 12.05
110236_20091006_82330_F_004 110236_20091006_82330_F 13.29 16.13
```



#### 3. wav.scp

> 각 오디오 파일의 위치를 포함

```shell
fild_id path/file

ex)
110236_20091006_82330_F path/110236_20091006_82330_F.wav
111138_20091215_82636_F path/111138_20091215_82636_F.wav
111138_20091217_82636_F path/111138_20091217_82636_F.wav
```

이때, wav가 아닌 다른 형식인 경우 sox를 이용하여 변경 가능

```shell
# .sph 파일을 wav로 변환하는 경우
# 파이프(|) 뒤에 꼭 붙여줘야함
file_id path/sph2pipe -f wav -p -c 1 path/file |  
```

```shell
# sox를 이용하여 변경하는 경우
file_id path/sox audio.mp3 -t(ype) wav -r(ate) 8000 -c(hannel) 1 - remix 2|
```



#### 4. utt2spk

> 발화자는 단순히 다른 사람을 의미하는게 아닌, 억양 방 성별 등으로 구분가능

```shell
utt_id spkr

ex)
110236_20091006_82330_F_0001 110236
110236_20091006_82330_F_0002 110236
110236_20091006_82330_F_0003 110236
...
120958_20100126_97016_M_0284 120958
120958_20100126_97016_M_0285 120958
120958_20100126_97016_M_0286 120958
```



#### 5. spk2utt

> 발화자별 발화 매핑이 되어있는 파일
>
> 이미 utt2spk에 모든 정보가 있지만 format이 다르므로 다음 명령어를 통해 spk2utt 생성

```shell
utils/fix_data_dir.sh data/train

# 실행결과
spkr utt_id1 utt_id2 utt_id3
```



### data/local/lang

#### 1. lexicon.txt

> 작업 중인 언어의 발음 사전
>
> 각 단어를 한 줄에 대문자로 표시한 다음 음소 발음으로 나열해야함

```shell
WORD	W ER D
LEXICON	L EH K S IH K AH N
```

**음향모델에서 사용하는 음소와 동일해야하며, 침묵 또한 포함해야함**



#### 2. silence_phones.txt

> (SIL)(침묵) 및 'OOV'(어휘 없음)이 있음

```shell
# 제작방법
echo -e 'SIL'\\n'oov' > silence_phones.txt
```



#### 3. extra_questions.txt

> 음소가 단어의 시작부분인지 끝부분인지 등에 대한 질문이 있음



### data/lang

#### Prepare_lang.sh

> utils/prepare_lang.sh <dict-src-dir\><oov-dict-entry\><tmp-dir\><lang-dir\>
>
> - 두번째 인자는 spoken noise 혹은 oov에 대한 단어 해당 단어는 lexicon.txt에 있어야 하며, 음소는 silence_phones.txt에 있어야한다.



## Parallelization wrapper

> - run.pl: 로컬 시스템에서 작업을 실행할 수 있습니다.
> - queue.pl: Sun Grid Engine을 이용하여 시스템에 작업을 할당할 수 있습니다.
> - slurm.pl: SLURM이라는 다른 그리드 엔진을 이용해 작업을 할당할 수 있습니다.
> - cmd.sh: Johns Hopkins CLSP 클러스터와 관련된 매개변수 사용
>
> 그리드 엔진이나 개인용 컴퓨터에서 작업하면 "run.pl"에 train_cmd와 decode_cmd 설정 가능



## MFCC

### Create files for conf

>MFCC 추출을 위한 매개변수가 포함된 파일

```shell
--use-energy=false

--sample-frequency=16000
```



### MFCC Extraction && CMVN 통계 계산

```shell
mfccdir=mfcc

steps/make_mfcc.sh --cmd "$train_cmd" --nj 16 data/train exp/make_mfcc/train/data $mfccdir
steps/compute_cmvn_stats.sh data/train exp/make_mfcc/data/train $mfccdir
```



## Phone training

### 모노폰 훈련 및 정렬

> Monophone은 적은양만으로도 합리적인 학습 가능
>
> 대체적으로 <location of Acoustic Data\> <location of lexicon\> <src-dir for model\> <dst-dir model\> 순으로 인자 입력

```shell
# 10000개의 데이터 준비
utils/subset_data_dir.sh --first data/train 10000 data/train_10k
```

```shell
# 데이터 훈련
steps/train_mono.sh --boost-silence 1.25 --nj 10 --cmd "$train_cmd" \
data/train_10k data/lang exp/mono_10k
```

```shell
# 모노폰 정렬
steps/align_si.sh --boost-silence 1.25 --nj 16 --cmd "$train_cmd" \
data/train data/lang exp/mono_10k exp/mono_ali || exit 1;
```



boost-silence가 학습의 표준 프로토콜로 사용됨

: 더 많은 데이터를 소비하게 하는 인자정도로 생각



### 트라이폰 훈련 및 정렬

> - HMM 상태
>
>   : 음소가 시작/중간/끝에 있는지에 따라 달라짐 따라서 하나의 음소에 최소한 세가지의 HMM상태를 요함
>
> - 가우시안 수

```shell
# 2000개의 HMM 상태 / 10000개의 가우시안 수로 delta 기반 트라이폰 훈련
steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" \
2000 10000 data/train data/lang exp/mono_ali exp/tri1 || exit 1;
```

```shell
# delta 기반 트라이폰 정렬
steps/align_si.sh --nj 24 --cmd "$train_cmd" \
data/train data/lang exp/tri1 exp/tri1_ali || exit 1;
```



```shell
# (delta + delta - delta) 구조 학습 
steps/train_deltas.sh --cmd "$train_cmd" \
2500 15000 data/train data/lang exp/tri1_ali exp/tri2a || exit 1;
```

```shell
# (delta + delta - delta) 구조 정렬
steps/align_si.sh  --nj 24 --cmd "$train_cmd" \
--use-graphs true data/train data/lang exp/tri2a exp/tri2a_ali  || exit 1;
```



```shell
# LDA-MLLT triphone 구조 학습
steps/train_lda_mllt.sh --cmd "$train_cmd" \
3500 20000 data/train data/lang exp/tri2a_ali exp/tri3a || exit 1;
```

```shell
# LDA-MLLT triphones 정렬 w/ FMLLR
steps/align_fmllr.sh --nj 32 --cmd "$train_cmd" \
data/train data/lang exp/tri3a exp/tri3a_ali || exit 1;
```



```shell
# SAT triphones 학습
steps/train_sat.sh  --cmd "$train_cmd" \
4200 40000 data/train data/lang exp/tri3a_ali exp/tri4a || exit 1;
```

```shell
# SAT triphones 정렬 w/ FMLLR
steps/align_fmllr.sh  --cmd "$train_cmd" \
data/train data/lang exp/tri4a exp/tri4a_ali || exit 1;
```



https://www.eleanorchodroff.com/tutorial/kaldi/training-acoustic-models.html
