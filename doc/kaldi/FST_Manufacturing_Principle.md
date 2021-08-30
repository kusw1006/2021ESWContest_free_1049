## OpenFST Symbol Tables

> symbol(=string) to int and reverse mapping
>
> The symbolTable implements the mappings of labels to strings and reverse.
>
> SymbolTables are used to describe the alphabet of the input and output labels for arcs in a Finite State Transducer.



### words.txt

> An OpenFst symbol table

<eps\> 0

<!SIL\> 1

<UNK\> 2

a a 3

kinen kinen 4

…



### phones.txt

<eps\> 0

SIL 1

SIL_B 2

SIL_E 3







------

### fst 구조에서의 가중치

$$
가중치 =log_{10}{확률}
$$

따라서 가중치 0 = 확률 1





### n gram

> - (Legacy) Chain rule: I can play the piano라는 문장이 있을 때, piano의 등장 확률을 예측하기 위해선
>
>   "i, can, play, the, piano" 순서대로 나올 확률 / i, can, play, the 가 순서대로 나올 확률로 계산할 수 있음. 예외처리 어렵



> - (New) Markov Process: 미래사건이 오로지 현재의 상태에만 의존하는 Markov property를 가진 process
>
>   **함께 고려하는 단어의 수가 줄어 OOV 대응에 효과적**



- Unigram: 현재 단어만 고려

- Bigram: 앞의 한개의 단어만 고려

"i can play the piano" 에서 piano를 예측하기 위해선

> the가 나왔을때 piano가 나올확률 * play가 나왔을 때 the가 나올 확률 \* play가 나왔을 때 the가  나올 확률 … 로 계산

- Trigram: 앞의 두개의 단어만 고려

  

#### LM 제작

1. Train set에서 전체 단어를 통한 Vocabulary 구성
2. Vocab의 각 단어들에 대한 Co-occurence mat. 생성
   - Bigram) Vocab에 Hi, Hello, World … 가 있다면 Hello - Hello 횟수, Hello - World 횟수, World - World 횟수, Hello - Hi 횟수 … count
   - Unigram) 그냥 단어의 빈도만 계산
3. Co-occurence mat.을 Normalize하여 조건부 확률 계산



4. 예를들어 Trigram에서 Count가 0이 나오는 경우가 있다면 Hi, Hello, World 단어집에서 Hi - Hello - World가 나오는 경우가 0인 경우, 더 낮은 gram에서의 count를 찾는 기법을 **backoff**라 함. 하지만 이 경우 전체 확률이 1이 넘어갈 수 있으므로, 적절한 상수를 곱해줄 필요있음





### 예시

#### LM(Bigram) 예시

- 실행코드

```shell
cat lm.arpa | \
    grep -v '<s> <s>' | \	# 해당 하는 패턴이 없는 경우만 출력
    grep -v '</s> <s>' | \
    grep -v '</s> </s>' | \	# <s> </s> 패턴만 남겨줘
    arpa2fst - | \     (step 1)
    fstprint | \
    eps2disambig.pl |\ (step 2) 
    s2eps.pl | \       (step 3)
    fstcompile --isymbols=words.txt \
      --osymbols=words.txt  \
      --keep_isymbols=false --keep_osymbols=false | \
    fstrmepsilon > G.fst  (step 4)    
```

- word.txt

```
<eps> 0
</s> 1
<s> 2
Cay 3
K. 4
ache 5
#0 6
```



- arpa file

```
\data\
ngram 1=5
ngram 2=6
 
\1-grams:
-0.4259687 </s>
-99 <s> -0.30103
-0.60206 Cay -0.2730013
-0.60206 K. -0.2730013
-0.9030899 ache -0.09691
 
\2-grams:
-0.60206 <s> Cay
-0.30103 <s> K.
-0.1760913 Cay </s>
-0.4771213 K. Cay
-0.4771213 K. ache
-0.30103 ache </s>
 
\end\
```

- lexicon

```
ache  ey k
Cay  k ey #1	# 동음이의어
K.  k ey #2		# 동음이의어
# 동음이의어는 이후 add_lex_disambig.pl 스크립트에 의해 disambig symbol #1 #2 가 붙음


# 2개의 음소만 존재
```

- (step1) G.fst

![](../../../img/chanhyun1.png)

​		- 노드 3 - 노드 1 이 0.69315인건, <s\>의 back off probability인 
$$
-ln{10^{-0.31013}}
$$
​			의 값이기 때문



- (step2) eps2disambig.pl

  : 모든 eps 입력 레이블 (백오프 엣지에 사용되는 것)을 '#0' 기호로 변환



- (step3) s2eps.pl

  : '<s\>' '</s\>' 기호를 eps로 변환 (문장시작, 끝기호)



- (step4) 

  : eps를 제거하고 해석





#### Lexicon 예시

- 실행코드

```shell
make_lexicon_fst.pl lexicon_disambig.txt 0.5 sil '#'$ndisambig | \
   fstcompile --isymbols=lexgraphs/phones_disambig.txt \
    --osymbols=lmgraphs/words.txt \
    --keep_isymbols=false --keep_osymbols=false |\
   fstaddselfloops  $phone_disambig_symbol $word_disambig_symbol | \
   fstarcsort --sort_type=olabel \
   > lexgraphs/L_disambig.fst
```

make_lexicon_fst.pl 4가지의 파라미터를 받음

​	1. disambig symbol이 있는 사전 파일

	2. optional silence(단어 사이의 묵음)의 확률 0.5
	3. silence phone을 나타내는데 사용하는 symbol
	4. slience를 표현하는 disambig symbol



- make_lexicon_fst.pl

  : 문장의 시작부분과 lexicon 단어 뒤에 Optional Silence (disambig symbol #3 사용) 추가

  (Optional Silence는 단어와 단어사이 존재)



- L.fst

![](../../../img/chanhyun2.png)



#### L * G composition

- 실행코드

```shell
fsttablecompose L_disambig.fst G.fst |\
  fstdeterminizestar --use-log=true | \
  fstminimizeencoded  > LG.fst
```



- L*G composition (Mini, det.)

![](../../../img/chanhyun3.png)

> #0 자체 루프는 L과 G를 병합할 때, G에서의 Special symbol을 처리하기 위해 만들어 놓은 경로



#### C.fst

> ilabel_info 라는 kaldi의 data structure을 이용하여 지정되는 triphone-id를 입력으로 넣음

- ilabel_info

  - 열의 'index'는 triphone의 id

  - 행의 값들은 context independent phone의 id가 들어있음

    C.I.Phone을 이용하여 특정 Triphone에 대한 Context 구축

  

  ``` 
  ex1) id가 10인 triphone a/b/c가 있다면
  ilabel_info의 11번째 항목(index alignment)은 'a' 'b' 'c'와 같은 C.I Phone이 들어있음
  ```

  

  ```
  ex2) 'sil' '<eps>'와 같은 phone은 kaldi에서 설명한 대로 빈 배열로 표시하며
  	 - '#-1'과 같은 symbol은 '0'이 하나 들어간 배열로 표현
  	 	(0번노드(시작노드)의 나가는 Arc에서 입력기호로 사용됨)
  	 	
  	 - '$'은 최종상태의 입력호에 대한 출력기호로 사용
  ```

- I/O

  - input (C.D. Phone): <eps\>/sil/ey (중심단어 sil 왼쪽이 <eps\> 오른쪽이 ey)

  - output(C.I. Phone): ey

    출력기호는 입력기호에 비해 (N-P-1) 위치만큼 앞에 나타나게 됨 (결합의 용이성을 위해)

    > 하지만, 이렇게 되면 Triphone에 (N-P-1) 또는 1이 있는 대부분의 Triphone에서 flush할 입력기호가 있을 때, 출력기호가 부족함
    >
    > **따라서, 발화의 끝 또는 막다른 길에서 '$' 기호를 사용해 줌**

  - '$'는 C가 LG로 composition될때 소모되어야함

    LG.fst의 출력층에 $:<eps\> self-loop를 추가하여 이를 소모

![](../../../img/chanhyun4.png)





#### CLG.fst

> 병합 시 optim.을 위해 동일한 HMM모델 (같은 PDF id)에 해당하는 모든 Triphone을 임의로 선택도니 하나의 멤버의 Triphone id에 매핑하여 사용



```
ex1) 'sil'은 CI이고, 모두가 동일한 HMM모델로 구성되기에 Triphone context에서의 모든 'sil'이 하나의 'sil' triphone id에 매핑됨
```



```
ex2) <eps>/ey/<eps>와 ey/ey/<eps>는 동일한 PDF_id (동일한 HMM 모델)을 사용하기에 같은 triphone id에 매핑함
```





![](../../../img/chanhyun5.png)





#### H.fst

> C.D. phones가 Transition-id에 매핑됨
>
> Transition-id는 CD Phone을 고유하게 식별하는데 사용되고,
>
> PDF_id는 CD Phone내의 노드 및 Arc를 식별함



![](../../../img/chanhyun6.png)



- Transition-id 표현 방법

  ```
  k_1_739_1
  Transition_id는 State 1 (두번째 State)와 관련되어 있으며
  PDF ID가 739인 음소 'K' (context에 따라 id는 달라질 수도 있음),
  또한 현재 State (=1)에서 넘어가는 State가 1
  즉, self-loop를 나타내는 Transition-id
  ```

  
