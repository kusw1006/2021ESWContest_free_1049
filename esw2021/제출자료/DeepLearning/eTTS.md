TTS 모델은 

어떤 모델 어떤 모델 어떤 모델을 사용했으며



학습을 위해선 어떤것을

뭐를위해선 어떤것을 해야한다

spnet v.0.6.0 기준



## installation

### 사용환경

ESPNET 0.7.0

pytorch 19.0

cuda 11.1

cudnn 8.0.5

pip install jamo

vga: rtx 3080

#@@@ pip를 싹다 python3 -m pip로 변경

```shell


pip install jamo

pip install -q torchtext==0.6 parallel_wavegan PyYaml unidecode ConfigArgparse torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html

git clone -q https://github.com/kan-bayashi/espnet.git #-b fix_import

cd espnet && git fetch && git checkout -b v.0.7.0 4ad3247c850bb6696e4e2c3f7633c0153463dded
```



```shell
# Download pre trained model

import os
if not os.path.exists("downloads/ptFastSpeech"):
    !./espnet/utils/download_from_google_drive.sh \
       https://drive.google.com/open?id=14JKGJ5lfM6ATaavDAlJyCGA81BAden9x downloads/ptFastSpeech tar.gz

# set path
trans_type = "char"
dict_path = "downloads/ptFastSpeech/data/lang_1char/EMO_char_train_no_dev_units.txt"
model_path = "downloads/ptFastSpeech/exp/EMO_char_train_no_dev_pytorch_train_fastspeech.sgst2.spkid/results/model.loss.best"
cmvn_path = "downloads/ptFastSpeech/data/EMO_char_train_no_dev/cmvn.ark"

print("Sucessfully finished download.")
```

```shell
# download pretrained model
import os
if not os.path.exists("downloads/ptParallelWavegan"):
    !./espnet/utils/download_from_google_drive.sh \
        https://drive.google.com/open?id=1GVVG9lw6Aq2a-C6au7KCMtp186GtsXrk downloads/ptParallelWavegan tar.gz

# set path
vocoder_path = "downloads/ptParallelWavegan/checkpoint-255000steps.pkl"
vocoder_conf = "downloads/ptParallelWavegan/config.yml"
vocoder_stat =  "downloads/ptParallelWavegan/stats.h5"

print("Sucessfully finished download.")

# add path
import sys
sys.path.append("espnet")
sys.path.append("downloads/ptFastSpeech")
```



```shell
# kaldi 설치

git clone https://github.com/kaldi-asr/kaldi
cd kaldi/tools
make -j <NUM-CPU>
sudo ./extras/install_mkl.sh
# 문제가 발생한다면 https://github.com/kusw1006/studyZeroth/tree/main/opt/kaldi/src 참고
cd ../src
./configure
make -j clean depend; make -j <NUM-CPU>
cd ../..
```



## Model

1. speaker model

   : 화자의 id를 onehot으로 추가하여 관련된 파형이 생기게

2. emotion model

   : multi-head attention을 이용하여 reference mel-spectrogram과 감정벡터를 엮어, 특정 감정에 대한 관련도가 제일 높은 mel-spectrogram을 파악하고 해당 정보를 embedding하여 이후 fastspeech의 attention에 text정보와 함께 삽입

3. fast speech & parallel waveGAN

   : 음소, 음소 길이, 기본주파수 등







1. text to mel-spectrogram을 진행하는 Transformer train

2. Transformer를 이용한 mel-spectrogram synthesis
   - Transformer에서 positional encoding을 더할 때 layer norm적용

3. Parallel WaveGAN을 이용한 waveform 합성

입력은 char 단위



### GST(global state toke) Tacotron

> Emotion token layer에서 Multihead attention을 이용하였음

![](./ETTS1.png)



GST기반 감정분석

https://www.jask.or.kr/articles/xml/d9vK/

**여기의 결과 이용하기 (과 동기들에게 평가를 요청하여 비교를 하였다)**



### Parallel Wave GAN

![](./ETTS2.png)

보조(Auxiliary) feature == mel-spectrogram





#### 사용 이유

1.44M의 매개변수를 가지며, 단일 GPU 환경에서 실시간보다 28.68배 빠른 24kHz 음성 파형을 생성할 수 있는 모델을 선택하였다.

 Perceptual listening test results
verify that our proposed method achieves 4.16 mean opinion score
within a Transformer-based text-to-speech framework, 또한 성능또한 좋다



#### 특징

Wavenet은 multi-resolution short-time Fourier transform(STFT)와 adversarial(적대적) 손실 함수의 조합을 최적화하여 non recursive Wavenet 모델만 학습하여, 훈련 프로세스가 매우 간단하다

Teacher - student의 프레임워크가 없이도 간단하게 교육할 수 있으므로, 교육 및 추론시간을 획기적으로 줄임

WaveNet의 목표는 teacher - student 프레임워크의 2개의 파이프라인을 축소시키는데에 있으며, 다시말해 우리의 목적은 distillation process없이 parallel wavenet을 돌리는것





### Transformer 기반 Parallel WaveGAN TTS





#### 학습 방법

```
cd egs/<DB>/tts1 # 해당 ㄱ
./run.sh
```





#### 얘의 pretrained model을 이용

https://github.com/emotiontts/emotiontts_open_db/tree/master/Codeset/Transformer-ParallelWaveGAN-based-Korean-TTS-master





### Ref

- [ESPnet github](https://github.com/espnet/espnet)
- [Parallel WaveGAN github](https://github.com/kan-bayashi/ParallelWaveGAN)
- [Transformer TTS paper](https://arxiv.org/pdf/1809.08895.pdf)
- [MultiSpeech paper](https://arxiv.org/pdf/2006.04664.pdf)
- [Parallel WaveGAN paper](https://arxiv.org/pdf/1910.11480.pdf)



Parallel Wave GAN

https://github.com/kan-bayashi/ParallelWaveGAN







음색+감정 음성합성기

https://github.com/emotiontts/emotiontts_open_db/tree/master/Codeset/realtimeMultiSpeakerMultiEmotionTTS

