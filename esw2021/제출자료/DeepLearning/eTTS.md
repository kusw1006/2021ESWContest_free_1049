# 설명방법

> 다양한 모델을 사용해보고, 가장 좋고, 속도가 빠른 지금의 모델을 선택하기로함





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











## 전체구조

![](./ETTS3.png)



1. dynamic import로 우리의 모델을 불러놓은 뒤, config를 불러와 모델 생성

```python
# define E2E-TTS model
from argparse import Namespace
from os.path import join
from espnet.asr.asr_utils import get_model_conf
from espnet.asr.asr_utils import torch_load
from espnet.utils.dynamic_import import dynamic_import
idim, odim, train_args = get_model_conf(model_path)
model_class = dynamic_import(train_args.model_module)
model = model_class(idim, odim, train_args)
torch_load(model_path, model)
model = model.eval().to(device)
inference_args = Namespace(**{
    "threshold": 0.5,"minlenratio": 0.0, "maxlenratio": 10.0,
    # Only for Tacotron 2
    "use_attention_constraint": True, "backward_window": 1,"forward_window":3,
    # Only for fastspeech (lower than 1.0 is faster speech, higher than 1.0 is slower speech)
    "fastspeech_alpha": 1.0,
    })
```



2. parallel wave gan은 pretrained model 불러와서 이후에 생성된 mel spectrogram을 가지고 synthesis

``` python
import yaml
import parallel_wavegan.models
with open(vocoder_conf) as f:
    config = yaml.load(f, Loader=yaml.Loader)
vocoder_class = config.get("generator_type", "ParallelWaveGANGenerator")
vocoder = getattr(parallel_wavegan.models, vocoder_class)(**config["generator_params"])
vocoder.load_state_dict(torch.load(vocoder_path, map_location="cpu")["model"]["generator"])
vocoder.remove_weight_norm()
vocoder = vocoder.eval().to(device)
if config["generator_params"]["out_channels"] > 1:
    from parallel_wavegan.layers import PQMF
    pqmf = PQMF(config["generator_params"]["out_channels"]).to(device)
```



3. cmvn은 pre-trained된 값을 가져와 읽어들임

4. 이후에 emotion.scp를 통해 각 감정의 대표 벡터들이 있는 ark에 접근하여 해당 벡터들을 가져온뒤



5. 우리의 E2E-TTS 모델에 char과 inference_args = tacotron2의 인자 및 임베딩된 speakerid, speakerId+input_emotion 넣기
6.  cmvn에 모델의 mel spectrogram 적용, reshape 한뒤 가우시안 노이즈 추가하여 pqmf에 넣어 synthesis



```python
   	x = frontend(input_text)
    c, _, _ = model.inference(x, None, inference_args, spemb=spemb, stemb=stemb)
    xx_denorm = cmvn(c.cpu().numpy())
    c = torch.FloatTensor(scaler.transform(xx_denorm))
    c = pad_fn(c.unsqueeze(0).transpose(2, 1)).to(device)
    xx = (c,)
    if use_noise_input:
        z_size = (1, 1, (c.size(2) - sum(pad_fn.padding)) * config["hop_size"])
        z = torch.randn(z_size).to(device)
        xx = (z,) + xx
    if config["generator_params"]["out_channels"] == 1:
        y = vocoder(*xx).view(-1)
    else:
        y = pqmf.synthesis(vocoder(*xx)).view(-1)    
rtf = (time.time() - start) / (len(y) / config["sampling_rate"])
print(f"RTF = {rtf:5f}")

from IPython.display import display, Audio
display(Audio(y.view(-1).cpu().numpy(), rate=config["sampling_rate"]))
```





### E2E-TTS

> Transformer-Parallel WaveGAN 기반 E2E 한국어 음성합성

생성기는 non recursive한 Fastspeech2의 사용(Transformer에 기반을 두고있음) 및, 보코더는 Parallel WaveGAN을 사용 (임베디드 환경에서도 충분히 사용가능한 파라미터)

Tacotron2-GST로 사전에 학습한 모델에서 도출한 Emotion token weight와 어텐션 alignment을 이용하여 MSE를 계산하여 추론하는 transfer learning을 진해앟ㅁ Length Regulator는 음소 시퀀스 길이를 spectrogram 시퀀스 길이에 정합시켜, 이를 통해 합성시 음소의 지속시간을 정할 수 있도록 한다.

```
#configure

[
   
        "decoder_concat_after": false,
        "decoder_normalize_before": false,
        "dlayers": 6,
        "dunits": 1536,
        "duration_predictor_chans": 256,
        "duration_predictor_dropout_rate": 0.1,
        "duration_predictor_kernel_size": 3,
        "duration_predictor_layers": 2,
        
        "encoder_concat_after": false,
        "encoder_normalize_before": false,
        "epochs": 500,
        "eps": 1e-06,
        "eunits": 1536,
        "eval_interval_epochs": 1,
        "freeze_mods": null,
        "grad_clip": 1.0,
        "gru_unit": 128,
        "lr": 0.001,
        "model_module": "nets.e2e_tts_fastspeech_sgst2:FeedForwardTransformer",
        "ngpu": 1,
        "num_gst": 10,
        "num_heads": 4,
        "num_spk": 20,
        "opt": "noam",
        "patience": 0,
        "positionwise_conv_kernel_size": 3,
        "positionwise_layer_type": "conv1d",
        "postnet_dropout_rate": 0.5,
        "postnet_filts": 5,
        "postnet_layers": 5,
        "report_interval_iters": 100,
        "resume": null,
        "save_interval_epochs": 20,
        "spk_embed_dim": 128,
        "style_dim": 128,
]

```



18.5시간 13000개의 발화, sample rate = 22050, 16bit 양자화 데이터, 학습에 12950개 문장, 검증용으로 50개 사용하여 학습했을때 Fastspeech가 text2mel에서 가장 빨랐으며 대략 아래와 같은 성능이 나온다. 

ubuntu 16.04 / ram = 64gb / rtx2080ti 1개

![속도비교](./eTTS4.png)



![](./ETTS1.png)



음색+감정 음성합성기

https://github.com/emotiontts/emotiontts_open_db/tree/master/Codeset/realtimeMultiSpeakerMultiEmotionTTS



GST 출처: https://github.com/KinglittleQ/GST-Tacotron/blob/master/GST.py

---

### parallel waveGAN



보조(Auxiliary) feature == mel-spectrogram

![](./ETTS2.png)

#### 사용 이유

1.44M의 매개변수를 가지며, 단일 GPU 환경에서 실시간보다 28.68배 빠른 24kHz 음성 파형을 생성할 수 있는 모델을 선택하였다.

 Perceptual listening test results
verify that our proposed method achieves 4.16 mean opinion score
within a Transformer-based text-to-speech framework, 또한 성능또한 좋다



#### configure

```
#configure

allow_cache: true
batch_max_steps: 25600
batch_size: 6

discriminator_grad_norm: 1
discriminator_params:
  bias: true
  conv_channels: 64
  in_channels: 1
  kernel_size: 3
  layers: 10
  nonlinear_activation: LeakyReLU
  nonlinear_activation_params:
    negative_slope: 0.2
  out_channels: 1
  use_weight_norm: true
  
discriminator_scheduler_params:
  gamma: 0.5
  step_size: 200000
discriminator_train_start_steps: 100000
distributed: true
eval_interval_steps: 1000
fft_size: 1024

generator_grad_norm: 10
generator_optimizer_params:
  eps: 1.0e-06
  lr: 0.0001
  weight_decay: 0.0
generator_params:
  aux_channels: 80
  aux_context_window: 2
  dropout: 0.0
  gate_channels: 128
  in_channels: 1
  kernel_size: 3
  layers: 30
  out_channels: 1
  residual_channels: 64
  skip_channels: 64
  stacks: 3
  upsample_net: ConvInUpsampleNetwork
  upsample_params:
    upsample_scales:
    - 4
    - 4
    - 4
    - 4
  use_weight_norm: true
  
generator_scheduler_params:
  gamma: 0.5
  step_size: 200000
global_gain_scale: 1.0
hop_size: 256
lambda_adv: 4.0
log_interval_steps: 100
num_mels: 80
num_save_intermediate_results: 4
num_workers: 1
sampling_rate: 22050
```



#### 얘의 pretrained model을 이용

https://github.com/emotiontts/emotiontts_open_db/tree/master/Codeset/Transformer-ParallelWaveGAN-based-Korean-TTS-master







#### 특징

Wavenet은 multi-resolution short-time Fourier transform(STFT)와 adversarial(적대적) 손실 함수의 조합을 최적화하여 non recursive Wavenet 모델만 학습하여, 훈련 프로세스가 매우 간단하다

```
# 우리가 Parallel Wave Net을 사용하는 이유
보코더 기술의 대표적인 방식에는 WaveNet과
WaveRNN 등이 있다. WaveNet은 이전 샘플을 이용하
여 현재 샘플의 확률분포를 예측하는 자기회귀 방식을
적용하여[7], 합성할 때 음성 샘플의 예측을 순차적으로
처리하므로 시간이 매우 오래 걸린다[8]. WaveRNN은
순환 신경망 계층 하나와 전연결 신경망 두 개 계층이
연결된 이중 소프트맥스 층으로 구성되어 있다[9], 이
방식은 긴 음성 시퀀스를 여러 개의 작은 시퀀스로 나
누는 Subscale 방식을 적용하여 한 번에 16개의 샘플을
생성할 수 있어, WaveNet 방식과 비교하여 합성 시간
이 빠르나 이 방식 역시 실시간 처리가 되지 않는다고
보고되어 있다[8].
이러한 방식들은 현재의 음성 샘플을 예측하기 위하
여 이전의 샘플을 이용하는 자기회귀 방식을 적용한다.
이와 같이 음성신호를 병렬로 생성하지 않고 직렬로 예
측하는 연산 특성은 GPU의 병렬 가속 연산 기능을 활
용하지 못하여 합성 시간이 오래 걸리는 단점을 갖는
다. 따라서 합성음의 품질이 우수하더라도 실시간 처리
가 요구되는 환경에서 사용하기 어렵다.
자기회귀 방식으로 음성 샘플을 생성하는 방식과 달
리, 비-자기회귀(Non-autoregressive) 방식은 이전에
생성된 샘플에 의존하지 않고 병렬로 음성 샘플을 생성
할 수 있어 음성 합성 처리 속도를 개선할 수 있다. 최
근에 비-자기회귀 방식을 적용한 TTS 기술이 제안되
고 있다.


★★★★★
실시간 처리는 자율 주행차, 로봇 등 임베디드 환경
에서 필수적인 요소이다. 본 논문의 실시간 처리 여부
는 컴퓨터 환경에서 시뮬레이션을 하여 얻은 결과이다.
향후에, 본 논문에서 제시한 TTS 시스템을 임베디드
환경에 구현하는 방식과 성능 검증에 대해 연구를 진행
할 계획이다.
```



#### 결과

MOS

|           | 동기1 | 동기2 | 동기3 | 동기4 | 동기5 | …    |      | 평균 |
| --------- | ----- | ----- | ----- | ----- | ----- | ---- | ---- | ---- |
| Neutral   | 4     | 3     | 3     | 5     | 4     |      |      |      |
| Anger     |       |       |       |       |       |      |      |      |
| Sadness   |       |       |       |       |       |      |      |      |
| Happiness |       |       |       |       |       |      |      |      |

|           | TPR(true positive rate) | TNR(true negative rate) | Accuracy |
| --------- | ----------------------- | ----------------------- | -------- |
| neutral   |                         |                         |          |
| anger     |                         |                         |          |
| sadness   |                         |                         |          |
| happiness |                         |                         |          |



### Ref

- [ESPnet github](https://github.com/espnet/espnet)
- [Parallel WaveGAN github](https://github.com/kan-bayashi/ParallelWaveGAN)
- [Transformer TTS paper](https://arxiv.org/pdf/1809.08895.pdf)
- [MultiSpeech paper](https://arxiv.org/pdf/2006.04664.pdf)
- [Parallel WaveGAN paper](https://arxiv.org/pdf/1910.11480.pdf)



Parallel Wave GAN

https://github.com/kan-bayashi/ParallelWaveGAN













# temp



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

  

### Tacotron2 GST(global state toke)

> Emotion token layer에서 Multihead attention을 이용하였음





GST기반 감정분석

https://www.jask.or.kr/articles/xml/d9vK/



