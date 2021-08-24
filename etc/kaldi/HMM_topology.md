> 작성자: 이찬현
>
> 일시: 21.08.18 15:00

# HMM topology

> Kaldi에서의 HMM Topology 표현 방법

```xml
 <Topology>
 <TopologyEntry>
 <ForPhones> 1 2 3 4 5 6 7 8 </ForPhones>
 <State> 0 <PdfClass> 0
 <Transition> 0 0.5
 <Transition> 1 0.5
 </State>
 <State> 1 <PdfClass> 1
 <Transition> 1 0.5
 <Transition> 2 0.5
 </State>
 <State> 2 <PdfClass> 2
 <Transition> 2 0.5
 <Transition> 3 0.5
 </State>
 <State> 3
 </State>
 </TopologyEntry>
 </Topology>
```

> - 하나의 TopologyEntry가 [있으며](https://www.jask.or.kr/articles/xml/v9ka/)
> - 8개의 음소를 다룸, 8개의 음소는 모두 동일한 Topology를 공유
> - 3개의 방출상태 존재 (연관된 Pdfs가 있고, 특징 벡터를 방출하는 상태)
> - 각각 자체 루프와 다음 상태로의 전환 존재
> - 마지막 상태는 비방출 상태이며, 최종 확률 1을 가짐
>   - 마지막 상태로의 '전이' 확률을 HMM의 '최종확률'로 [취급할](https://www.jask.or.kr/articles/xml/v9ka/) 수 있음

## PDF class

> 확률 분포 함수의 인덱스로 사용되며, 일반적인 경우 HMM state와 동일한 인덱스를 가짐
>
> 하지만 동일한 phonetic context를 가진것들은 같은 pdf를 공유하며, 공유를 강제하기 위해 pdf class를 사용할 수도 있다.

- 어떤 HMM 상태에 대해 pdf class = -1(kNoPdf)인 경우 방출하지 않는 상태라는 것





## TransitionModel의 정수 식별자 특징

> 1로 시작하는 배열을 기피하고는 있지만, openfst에서의 0이 special symbol (epsilon)이기 때문에 몇몇개는 1로 시작함

- phone (one-based): this type of identifier is used throughout the toolkit; it can be converted to a phone name via an OpenFst symbol table. Not necessarily contiguous (the toolkit allows "skips" in the phone indices).
- hmm-state (zero-based): this is an index into something of type [HmmTopology::TopologyEntry](https://kaldi-asr.org/doc/classkaldi_1_1HmmTopology.html#aba67ff7bf4a95d8b1b33f1f41b385a74). In the normal case, it is one of {0, 1, 2}.
- pdf, or pdf-id (zero-based): this is the index of the p.d.f., as originally allocated by the decision-tree clustering; (see [PDF identifiers](https://kaldi-asr.org/doc/tree_externals.html#pdf_id)). There would normally be several thousand pdf-ids in a system.
- transition-state, or trans_state (one-based): this is an index that is defined by the [TransitionModel](https://kaldi-asr.org/doc/classkaldi_1_1TransitionModel.html) itself. Each possible triple of (phone, hmm-state, pdf) maps to a unique transition-state. Think of it is the finest granularity of HMM-state for which transitions are separately estimated.
- transition-index, or trans_index (zero-based): this is an index into the "transitions" array of type [HmmTopology::HmmState](https://kaldi-asr.org/doc/structkaldi_1_1HmmTopology_1_1HmmState.html). It numbers the transitions out of a particular transition-state.
- transition-id, or trans_id (one-based): each of these corresponds to a unique transition probability in the transition model. There is a mapping from (transition-state, transition-index) to transition-id, and vice versa.



## Transition model의 학습

- 각 feature vector에 transition-id 부여
- train 과정에서 transition-id를 본 횟수를 accumulate
- Transition()::Update() does the ML update for each transition-state



## Alignments in kaldi

> Sequnce of trasition-ids를 가지고 하는데, 얘의 길이는 정렬에 해당하는 utt의 길이와 동일하다.
>
>  
>
> transition-ids sequence는 일반적으로 입력 레이블

