# kaldi

> 각 파일의 설명 및 추가/삭제에 대한 주석은 github.com/kusw1006/studyZeroth 참고 (주소 변경 예정)





## run_kspon.sh

### AM학습

#### 학습 파라미터

- clean

  | 학습종류               | maximum pdf | maximum gaussian |
  | ---------------------- | ----------- | ---------------- |
  | delta train            | 2000        | 10000            |
  | lda + mllt train       | 2500        | 15000            |
  | triphone train         | 4200        | 40000            |
  | lda + mllt + SAT train | 4200        | 40000            |

  - LDA(linear discriminant Analysis)
  - MLLT (maxixum likelihood linear transform)
  - fMLLR (feature space maximum likelihood linear regression)

- multicondition

  CHAIN 모델에 대한 학습 후 작성 필요

  snrs 배열 수정 (30:20:15:5:0)

  reverberate 3 iter

  maxspeaker 2

  1dConv + batch norm + relu NN 사용

  

#### 사용한 데이터

>  aihub ksponspeech 1000시간 발화데이터를 학습하다 대회 제출 기간을 고려하여 300시간 데이터로 축소하여 학습을 진행하였다.



#### multicondition

G.729에 맞춰 script에 sox 파이프라인 작성 (파형 비교 사진) @@ **진혁이가 제작한 파일 참고**

전화선 데이터에 맞춰 기존 16kHz로 학습을 진행하는 kaldi asr(automatic sound recognition) system에 맞게 8kHz를 학습할 수 있도록 변형하였다.

> 또한 음식점 환경에 특화된 RIR를 추가하였고, 증폭이 많이되는 유선전화 특성 상 clipping이 많이 발생할 수 있어 음성 데이터셋을 해당 환경에 맞게 변형 한 뒤 multicondition에 대한 학습도 진행하였다.

#### 기술적 어려움

> 지나치게 데이터를 변형할 경우 음소에 대한 파형의 특징을 잡기 어려워져 HMM-GMM을 통한 음소-파형 alignment 학습이 어려울 수 있기 때문에 적절한 양을 조절하는데 어려움을 겪었고, 최대한 음소학습시 파형 변형이 크지않도록 multi condition 학습의 위치를 조절하는데에 어려움을 겪었다.

> 또한 RAM 및 오랜 시간이 걸리는 작업 (최소 3주 이상 소모)



### LM학습

#### 말뭉치

> base domain에 사용된 말뭉치의
>
> 단어수, 문장수는 ~~고@@ **8/24 일지 와 한비가 작성한 파일 참고**
>
> 출처는 ~~다@@
>
> 또한 구어체가 많이 등장하는 배달관련 말뭉치를 얻기 위해 selenium을 이용한 가게리뷰, 배달리뷰의 web scrapping도 진행하여 최대한 부족한 배달관련 말뭉치를 채웠다.



#### Carpa

4-gram arpa file을 가지고 fst형태로 만들어 음성인식에 사용하게 되면, 용량 및 path 탐색에 오랜 비용이 들기때문에,

const-arpa형식으로 제작하여 Grammar fst를 rescore해서 사용할 수 있도록 하였다. (G.fst 수십기가)



#### arpa

위의 이유로 arpa 파일은 prune하여 불필요한(확률이 낮은) 문장관계를 최대한 제거하고 제작하였다.

4-gram 기준 0.00000001 (NGRAM 어쩌구 파일에 있는 수치 확인@@)로 설정하여 prune을 진행한 뒤, HCLG 그래프로 제작하여 수십배 빠른 decoding을 진행할 수 있도록 하였다.





### HCLG제작

다양한 모델을 만들어 학습을 진행하였으며

또한 AM을 전화선 상황에 맞게 변형하였을때와 변형하지않았을때의 인식률의 차이가 어느정도인지 짤로 보여주기**@@@ (간단한 문장 캡쳐)**



3-gram small(prune:0.0000003)로 구성된 LM / 3-gram medium(0.0000001)으로 구성된 LM

4-gram small(prune:0.00000008)과 4-gram medium (prune:0.00000001)로 구성된 LM

또한 추후 설명할 extend vocabulary를 적용한 main LM과 task domain에 맞는 LM 등 다양한 LM을 이용하였으며

또한 AM 구성 시 다양한 음향 환경 추가 및 데이터셋을 변경하며 제작하여, 수많은 HCLG.fst를 제작하였고,

속도면에서는 큰 차이가 없어, 음식점관련 환경에서 인식률이 가장 좋은 모델을 선택하여 사용하게되었다.



#### 결과

Kaldi WER 측정 Tool을 이용한 결과는 다음과 같다.

WER(word error rate): 11%(clean) ~ 16%(noisy)



## 글자 확장

신조어 및 새로운 배달메뉴가 계속해서 나오므로, 음성 인식 domain의 확장은 필수적이고, 신속해야한다.



### run_task.sh

> task domain의 arpa를 제작한 뒤 srilm tool을 이용하여 interpolation하여, domain에 특화하여 LM을 구축 할 수 있으나,
>
> 한번 interpolation이 진행되면, 최적화 및 bias가 걸려 다른 domain의 arpa와 더 이상 interpolation을 진행할 수 없게 된다.

### extend vocab demo

>interpolation의 단점을 해결하기 위해, top L.fst, G.fst가 nonterminal하게 동작할 수 있도록 unknown 단어에 대해 기존 <UNK\> 심볼 대신 #nonterm:unk 심볼을 추가하여 해당 부분에 task domain G.fst를 결합할 수 있도록 전처리 한 뒤에 제작한 top HCLG.fst을 가지고 각 task domain에 맞는 새로운 단어들로 L.fst, G.fst를 제작한 뒤, HCLG.fst로 묶고, make-grammar-fst Kaldi binary 파일을 이용하여 main HCLG.fst와 new HCLG.fst를 빠르게 결합하여, domain에 맞게 떼었다 붙였다 할 수 있는 기술을 개발하였다.

이때 L.fst는 따로 g2p를 이용하여 발음을 생성하지 않고, (설명한대로) 해당 table에 맞게 발음을 변형한 뒤(with gen_pronounciation.py) data driven 방식으로 형태소를 분석하는 morfessor tool을 이용하여 형태소를 분석하여 기존의 단어집과 비교하여 새로운 단어가 있을 때 해당 단어에 대해 새로운 Lexicon을 만들고 결합할 수 있도록 shell script로 제작해놓았다.