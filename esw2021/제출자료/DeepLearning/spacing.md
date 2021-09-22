# software 설계도

> 학습영역 - 띄어쓰기 보정 학습 구성도
>
> [설명 참조](https://jeongukjae.github.io/posts/korean-spacing-model/)
>
> [github](https://github.com/jeongukjae/korean-spacing-model)



## Dataset

> 경어체보다는 구어체와 배달관련 용어를 많이 쓰기 때문에 해당 domain에 맞는 corpus를 이용하였다.

- 국립국어원 모두의 말뭉치: 일상대화말뭉치 2020, 구어 말뭉치

- AIHub: 소상공인 고객 주문 질의 텍스트(2020), 한국어대화(2018), 민원 콜센터(2020)

약 25,000,000개의 문장으로 구성되어있으며 22,500,000 (Train set) / 2,500,000 (Test set)으로 이루어져있다.





# Model

- 모델 구조

<img src="https://jeongukjae.github.io/images/2020/09-23-korean-spacing-model/model.png" alt="img" style="zoom: 50%;" /> 

Bi-LSTM구조를 CNN으로 교체하면 정확도와 빠른 성능을 얻을 수 있다는 점([Strubell et al., 2017](https://arxiv.org/abs/1702.02098)) 에서 착안하여 

빠른 속도를 위해 CNN 구조를 선택. Embedding 후 Conv1D - MaxPool1D (그림은 3개지만 2~10 조절) 결과물을 concat한 후 
Dense Layer 2번 통과. 



- input 

int32 tensor: (BatchSize,SequenceLength)



- output

float32 tensor: (BatchSize, SequenceLength, 3)



- 학습 방법

```
1. Index Character: Dataset 상위 4996개의 음소를 빈도 순으로 저장하여 매핑
2. Vocab 제작: Index Character에 padding, bos, eos, unk 4개의 인덱스도 추가
3. 띄어쓰기가 잘 되어있는 한국어 문장에 BOS, EOS 태그를 추가한 뒤 띄어쓰기를 랜덤하게 삭제/ 추가하고 그를 원래의 문장으로 복구하기 위한 label생성. 0.5의 확률로 공백 삭제, 0.15의 확률로 공백 추가
4. Character Indexing 후 model 통과
```



```shell
python train.py \
    --train-file train-text-file-path \
    --dev-file dev-text-file-path \
    --training-config ./resources/config.json \
    --char-file ./resources/char-4996
```



- label

0: 현재 상태 유지

1: 띄어쓰기 추가

2: 띄어쓰기 삭제



- 학습 시 사용한 configure

sequence length: 128

Optimizer : Adam Optimizer

train_batch_size: 64,

val_batch_size: 1024,

epochs: 30,

learning_rate: 0.01,

vocab_size: 5000,

hidden_size: 48,

conv_activation: "relu",

dense_activation: "relu",

conv_kernel_and_filter_sizes: [[2, 8], [3, 8], [4, 8], [5, 16], [6, 16], [7, 16], [8, 16], [9, 16], [10, 16]],

dropout_rate: 0.1



# 결과

공백을 다 제거한 경우 0.9442

모든 문장에 공백을 추가한 경우 0.9539

한 문장당 추론에 0.088ms 소요



## Reference

- Jeong Ukjae 블로그 - CNN Spacing
- GitHub: [haven-jeon/KoSpacing](https://github.com/haven-jeon/KoSpacing) - CNN - BatchNorm - FFN - GRU - FFN 구조 (무거움)
- GitHub: [pingpong-ai/chatspace](https://github.com/pingpong-ai/chatspace) - CNN - BatchNorm - FFN - BiLSTM - LayerNorm - FFN
- Emma Strubell, Patrick Verga, David Belanger, and Andrew McCallum. 2017. Fast and accurate entity recognition with iterated dilated convolutions. [arXiv:1702.02098.](https://arxiv.org/abs/1702.02098)
- Xinyu Wang el al., 2020. AIN: Fast and Accurate Sequence Labeling with Approximate Inference Network. [arXiv:2009.08229.](https://arxiv.org/abs/2009.08229)

