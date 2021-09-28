# kaldi

> 각 파일의 설명 및 추가/삭제에 대한 주석은 github.com/kusw1006/studyZeroth 참고 (주소 변경 예정)



라즈베리파이를 이용하여 서버를 쉽게 이용할 수 있다.

라즈베리파이에 최적화된 UI



## run_kspon.sh

### AM학습

https://www.eleanorchodroff.com/tutorial/kaldi/training-overview.html 링크 참고



HMM/GMM

1. 오디오에서 음향특성 추출

   > 음성데이터의 MFCC(Mel Frequency Ceptral Coefficients)를 추출한다

2. MonoPhone 모델 학습

   > 이전/다음 음소에 대한 Context 정보를 포함하지 않는 음향

3. 음향모델에 맞게 오디오 정렬

   Viterbi 알고리즘을 이용해 1차적으로 정렬, 

4. Triphone 모델 학습

   > 좌우 컨텍스트에 따라 변형되는 음소의 형태를 고려하여 음소의 확률분포를 학습, 이때 음소를 잘게 쪼개서 모델의 수를 줄임

5. Triphone 모델 추가학습

   > 더 정교한 모델을 위해 추가 Train 알고리즘(delta-delta train, lda-mllt, sat, fmllr 등)을 이용하여 Triphone 모델 학습.

   - delta+delta-dalta train: MFCC 기능을 보완하기 위해 feature의 차이들로 이루어진 것들로 학습

   - lda-mllt: Linear Discriminant Analysis - Maximum Likelihood Linear Transform의 약자로써, 

   - **Delta+delta-delta 훈련** 은 MFCC 기능을 보완하기 위해 델타 및 이중 델타 기능 또는 동적 계수를 계산합니다. 델타 및 델타-델타 기능은 신호(기능)의 1차 및 2차 도함수에 대한 수치 추정치입니다. 따라서 계산은 일반적으로 더 큰 특징 벡터 창에서 수행됩니다. 두 개의 특징 벡터로 구성된 창이 작동할 수도 있지만 이는 매우 조잡한 근사치일 것입니다(델타 차이가 도함수의 매우 조잡한 근사치인 것과 유사함). 델타 기능은 원래 기능의 창에서 계산됩니다. 델타-델타는 델타-특징의 창에서 계산됩니다.

     **LDA-MLLT** 는 Linear Discriminant Analysis – Maximum Likelihood Linear Transform의 약자입니다. 선형 판별 분석은 특징 벡터를 사용하여 HMM 상태를 구축하지만 모든 데이터에 대해 특징 공간이 축소됩니다. Maximum Likelihood Linear Transform은 LDA에서 축소된 기능 공간을 가져와 각 스피커에 대해 고유한 변환을 유도합니다. 따라서 MLLT는 화자 간의 차이를 최소화하므로 화자 정규화를 향한 단계입니다.

     **SAT** 는 Speaker Adaptive Training의 약자입니다. SAT는 또한 특정 데이터 변환으로 각 특정 화자에 적응하여 화자 및 잡음 정규화를 수행합니다. 그 결과 화자 또는 녹음 환경과 반대로 모델이 음소로 인한 분산 추정에 매개변수를 사용할 수 있어 보다 균일하거나 표준화된 데이터가 생성됩니다.

     - **정렬 알고리즘**

     실제 정렬 알고리즘은 항상 동일합니다. 다른 스크립트는 다른 유형의 음향 모델 입력을 허용합니다.

     화자 독립 정렬은 소리와 같이 정렬 프로세스에서 화자별 정보를 제외합니다.

     **fMLLR** 은 Feature Space Maximum Likelihood Linear Regression을 나타냅니다. SAT 교육 후 음향 모델은 더 이상 원래 기능이 아닌 화자 정규화 기능에 대해 교육됩니다. 정렬을 위해 기본적으로 화자 ID를 추정하여(fMLLR 행렬의 역행렬을 사용하여) 특성에서 화자 ID를 제거한 다음, 역행렬에 특징 벡터를 곱하여 모델에서 제거해야 합니다. 이러한 유사 화자 독립 음향 모델은 정렬 프로세스에서 사용할 수 있습니다.

     **Delta+delta-delta training** computes delta and double-delta features, or dynamic coefficients, to supplement the MFCC features. Delta and delta-delta features are numerical estimates of the first and second order derivatives of the signal (features). As such, the computation is usually performed on a larger window of feature vectors. While a window of two feature vectors would probably work, it would be a very crude approximation (similar to how a delta-difference is a very crude approximation of the derivative). Delta features are computed on the window of the original features; the delta-delta are then computed on the window of the delta-features.

     **LDA-MLLT** stands for Linear Discriminant Analysis – Maximum Likelihood Linear Transform. The Linear Discriminant Analysis takes the feature vectors and builds HMM states, but with a reduced feature space for all data. The Maximum Likelihood Linear Transform takes the reduced feature space from the LDA and derives a unique transformation for each speaker. MLLT is therefore a step towards speaker normalization, as it minimizes differences among speakers.

     **SAT** stands for Speaker Adaptive Training. SAT also performs speaker and noise normalization by adapting to each specific speaker with a particular data transform. This results in more homogenous or standardized data, allowing the model to use its parameters on estimating variance due to the phoneme, as opposed to the speaker or recording environment.

     - **Alignment Algorithms**

     The actual alignment algorithm will always be the same; the different scripts accept different types of acoustic model input.

     Speaker independent alignment, as it sounds, will exclude speaker-specific information in the alignment process.

     **fMLLR** stands for Feature Space Maximum Likelihood Linear Regression. After SAT training, the acoustic model is no longer trained on the original features, but on speaker-normalized features. For alignment, we essentially have to remove the speaker identity from the features by estimating the speaker identity (with the inverse of the fMLLR matrix), then removing it from the model (by multiplying the inverse matrix with the feature vector). These quasi-speaker-independent acoustic models can then be used in the alignment process.

>run_openslr 분석
>
>- updateSegmentation.sh : segmention rule이 바뀌면 실행된다. morfessor installation check
>형태소를 찾아내서 문장에서 단어를 쪼개서 기입
>- prepare_dict.sh : dictionary를 만드는 작업이다. download_lm.sh에 있는 lexicon을 복사해온다.
>lexicon_raw_nosil에 넣어준다. phone lists와 clustering question을 준비한다. silence_phones와 nonsil_phones
>optional_silence, extra_question phone list를 만들어준다.
>- prepare_lang.sh : word-position-dependent phones를 덧붙이고 다른 파생된 host file들을 짜집기하여
>data/lang/에 넣어준다.
>- format_lms.sh : tgsmall에 대해 data를 formatting한다.
>- make_mfcc.sh : wav 파일에서 mel spectogram을 추출한다
>- compute_cmvn_stats.sh : 화자에 해당하는 cepstral 평균 및 분산 계산
>- train_mono.sh : MFCC와 delta-delta features를 활용하여 monophone training 진행, 하나의 phone으로만 진행
>- align_si.sh : training alignments를 delta를 활용해 계산한다.
>- train_deltas.sh : delta + delta-delta feature를 활용하여 triphone training 진행, 좌우 phone을 읽어
>3개의 phone에 대해서 학습 진행
>- align_si.sh : training alignments를 delta들을 활용해 계산한다.
>- train_lda_mllt.sh : train LDA+MLLT system을 진행한다. splicing -> LDA -> MLLT 진행
>- align_si.sh : training alignments를 tri2b model에서 진행
>- train_sat.sh : triphone training, LDA+MLLT+SAT system 진행
>- build_const_arpa_lm.sh : tglarge와 fglarge의 carpa를 제작한다.
>- align_fmllr.sh : 모든 train_clean에 대해 tri3b model를 활용하여 align한다.
>- train_sat.sh : 새로운 triphone training을 진행하는데 모든 sub_set에 대해서 진행된다. -> tri4b
>- mkgraph.sh : tri4b model을 활용해 decode를 진행한다. HCLG 제작
>- decode_fmllr.sh : graph_tgsmall에 대해 decode 진행
>- lmrescore_const_arpa.sh : (tgsmall, tglarge), (tgsmall, fglarge)에 대해 rescore 진행

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