# Team Deep Listener

## 팀원

| 이름   | 전공           | 메일               |
| ------ | -------------- | ------------------ |
| 이찬현 | 건국대학교 전기전자공학부 | ech97@konkuk.ac.kr |
| 안진혁 | 건국대학교 전기전자공학부 | hijin99@konkuk.ac.kr |
| 김한비 | 건국대학교 전기전자공학부 | khb200718@konkuk.ac.kr   |
| 신지혜 | 건국대학교 전기전자공학부 | long0404@konkuk.ac.kr    |



## github Tree





## 구조

![](./graph_AM_수정.png)
![](./graph_LM.png)



## 서버 구성도

![서버 구성도]



## 딥러닝 클라이언트 구조

![딥러닝들]

### E2E Text To Speech Model

#### 1. Text2Mel

##### 1-1. Tacotron2

> https://github.com/NVIDIA/tacotron2의 Model 사용

![](./imgs/TACOTRON2.png)

> Text2Mel을 진행해주는 Seq2Seq모델의 구조를 기반으로 하는 Neural Network이다. 문자 임베딩을 Mel-Spectrogram에 맵핑하는 반복적인 구조로 이루어져있으며, Encoder와 
> Decoder를 연결하는 Location-Sensitive Attention이 있다. 이때 Decoder에서 AutoRegressive 
> RNN을 포함하는데 이와 같은 이유로, 추론 속도가 떨어지는 특징을 가진다.



##### 1-2. GST

![](./imgs/GST.png)

> 다양한 길이의 오디오 입력의 운율을 Reference Encoder(참조 인코더)를 통해 고정된 길이의 
> 벡터로 변환한다. 이후 학습 과정에서 Tacotron 인코더단의 출력과 concatenate하여 Tacotron 
> 모델의 Attention의 입력으로 사용하여 목표 문장의 Style을 Embedding을 한다. 이후의 Style Embedding Vector는 Text2Mel 모델을 사용할 때 임베딩 된 Character와 함께 
> add 또는 concatenate하여 Style에 맞는 Mel-spectrogram을 제작하는데 사용된다.



##### 1-3. FastSpeech

![fastSpeech]

> FastSpeech 모델은 Text2Mel 작업을 위한 Neural Network이며, 같은 작업을 하는 Tacotron2
> 는 Regressive한 구조를 가지는데 비해 FastSpeech는 Non-autoRegressive한 구조를 가져 훨씬 
> 더 빠른 inference가 가능해 해당 모델을 사용하기로 하였다. 전체 구조는 위의 그림과 같으며, Tacotron2-GST를 통해 학습하였던 Style Vector를 가져와 
> Character Embedding Vector와 add연산을 진행하여 추론에 사용한다.



### KADLI Speech To Text



### Korean Spacing Model



### KoBERT Sentimental Classification

> https://github.com/SKTBrain/KoBERT의 PreTrained BERT 사용

![](./imgs/kobert.png)





## Requirement

ESPnet

Kaldi 



### Computing Power

> 



## TODOS

- server, client 고급화
- raspberryPi/src/client_text.py 코드 최적화
- Large HCLG graph 제작
