> 작성자: 이찬현
>
> 작성일시: 21.08.18 21:47

# Kaldi Data Preparation

> 직접제작

## Data/train

```shell
ls data/train
cmvn.scp feats.scp reco2file_and_channel segments spk2utt text utt2spk wav.scp
```

utt2spk, text, wav.scp 필수로 생성, segment는 가능하면 생성, 나머지는 자동 생성 스크립트 존재



### text

```shell
head -3 data/train/text

<utt-id1> HI UM YEAH I'D LIKE TO TALK ABOUT HOW YOU DRESS FOR WORK AND
<utt-id2> UM-HUM
<utt-id3> AND IS
```



### utt2spk, spk2utt

utt2spk, spk2utt의 정렬 순서는 동일해야하므로, 보통은 utt의 접두사를 spk앞에 붙임

```shell
utt 형식
sw02001-A_000098-001156

spk 형식
2001-A	// '_' 보다는 '-'가 ASCII값이 낮음
```

- spk-id를 utt-id로 대체가능

- 화자 ID를 개개인별로 나눌 필요 없음



### wav.scp

```shell
<recording-id> <extended-filename>
```

이때, segment 정보가 없다면 recording-id => uttrance-id



### segment

```shell
<utt-id> <recording-id> <segment-begin> <segment-end>
```

```shell
head -3 data/train/segments
sw02001-A_000098-001156 sw02001-A 0.98 11.56
```



### reco2file_and_channel

NIST의 "sclite" 도구로 채점 (오류율 측정)시에만 사용

```
<recording-id> <filename> <recording-side (A or B)>
```

```shell
head -3 data/train/reco2file_and_channel
sw02001-A sw02001 A
sw02001-B sw02001 B
sw02005-A sw02005 A
```

---

> 자동 제작

### feats.scp

```shell
<utt-id> <extended-filename-of-features>
```

```shell
head -3 data/train/feats.scp

sw02001-A_000098-001156 /home/dpovey/kaldi-trunk/egs/swbd/s5/mfcc/raw_mfcc_train.1.ark:24
sw02001-A_001980-002131 /home/dpovey/kaldi-trunk/egs/swbd/s5/mfcc/raw_mfcc_train.1.ark:54975
sw02001-A_002736-002893 /home/dpovey/kaldi-trunk/egs/swbd/s5/mfcc/raw_mfcc_train.1.ark:62762
```

MFCC를 가리킴. 이때 kaldi 형식 Matrix가 있는 아카이브 파일을 여는데

행렬의 차원은 13(10ms 간격)이며,

sw02001-A_000098-001156/home/dpovey/kaldi-trunk/egs/swbd/s5/mfcc/raw_mfcc_train.1.ark:24

아카이브 파일에서 fseek의 위치를 24 이동하고 데이터를 읽음



```shell
# feats.scp 생성
steps/make_mfcc.sh --nj 20 --cmd "$train_cmd" data/train exp/make_mfcc/train $mfccdir
```



### cmvn.scp

speaker로 부터 인덱싱된 cepstral 평균, 분산 통계가 있음. 차원은 2x14

```shell
<spk-id> <filename>

head -3 data/train/cmvn.scp

2001-A /home/dpovey/kaldi-trunk/egs/swbd/s5/mfcc/cmvn_train.ark:7
2001-B /home/dpovey/kaldi-trunk/egs/swbd/s5/mfcc/cmvn_train.ark:253
2005-A /home/dpovey/kaldi-trunk/egs/swbd/s5/mfcc/cmvn_train.ark:499
```



```shell
# cmvn.scp 생성
steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train $mfccdir
```

----

## data/lang

```shell
ls data/lang
G.fst L.fst  L_disambig.fst  oov.int	oov.txt  phones  phones.txt  topo  words.txt
```



### data/lang/phones

> txt, int, csl 세 가지 형태로 제작되어있으며
>
> **utils/prepare_lang.sh**를 통해 보다 쉬운 입력으로 세가지 파일 작성가능

```shell
ls data/lang/phones
context_indep.csl  disambig.txt         nonsilence.txt        roots.txt    silence.txt
context_indep.int  extra_questions.int  optional_silence.csl  sets.int     word_boundary.int
context_indep.txt  extra_questions.txt  optional_silence.int  sets.txt     word_boundary.txt
disambig.csl       nonsilence.csl       optional_silence.txt  silence.csl
```

- .txt는 단어들을 openfst 형식에 맞게 텍스트로 제작

  ```
  head -3 data/lang/phones/context_indep.txt
  SIL
  SIL_B
  SIL_E
  ```

- .int는 단어들을 숫자로 매핑

- .csl은 쉼표가 아닌 콜론으로 구분도니 목록을 나타냄



#### disambig

: 동음이의 기호 목록이 포함되어있음



#### context_indep

: 묵음에 대한 단어 존재

SIL(단어의 묵음), SIL_S(묵음자체가 단어), SIL_B …



#### optional_silence

: 단어 사이의 묵음 SIL 존재

