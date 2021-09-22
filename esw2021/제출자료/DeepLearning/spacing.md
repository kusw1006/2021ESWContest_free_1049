# software 설계도

> 학습영역 - 띄어쓰기 보정 학습 구성도
>
> [설명 참조](https://jeongukjae.github.io/posts/korean-spacing-model/)
>
> [github](https://github.com/jeongukjae/korean-spacing-model)



- 모델 구조

<img src="https://jeongukjae.github.io/images/2020/09-23-korean-spacing-model/model.png" alt="img" style="zoom: 50%;" /> 

빠른 속도를 위해 CNN 구조를 선택. Embedding 후 Conv1D - MaxPool1D 결과물을 concat한 후 
Dense Layer을 두 번 통과. 



- input

(BatchSize,SequenceLength)의 int32 tensor



- output

(BatchSize, SequenceLength, 3)의 tensor



- 학습 방법

올바른 한국어 문장에 BOS, EOS 태그를 추가한 뒤 띄어쓰기를 랜덤하게 삭제/ 추가하고 그를 원래의 문장으로 복구하기 위한 label생성. 0.5의 확률로 공백 삭제, 0.15의 확률로 공백 추가



- label

0: 현재 상태 유지

1: 띄어쓰기 추가

2: 띄어쓰기 삭제



- vocab 구성

학습 코퍼스 내부의 문자 출현 빈도 상위 4996 + {padding, bos, eos, unk} : 총 5000개



- configure

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

