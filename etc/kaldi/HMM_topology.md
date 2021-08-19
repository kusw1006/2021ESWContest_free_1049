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

> - 하나의 TopologyEntry가 있으며
> - 8개의 음소를 다룸, 8개의 음소는 모두 동일한 Topology를 공유
> - 3개의 방출상태 존재 (연관된 Pdfs가 있고, 특징 벡터를 방출하는 상태)
> - 각각 자체 루프와 다음 상태로의 전환 존재
> - 마지막 상태는 비방출 상태이며, 최종 확률 1을 가짐
>   - 마지막 상태로의 '전이' 확률을 HMM의 '최종확률'로 취급할 수 있음