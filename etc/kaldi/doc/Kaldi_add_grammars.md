# Kaldi add grammars

> 작성자: 이찬현
>
> 작성일시: 21.08.27 18:11



```
단어 추가를 위한 기능

작은 G.fst를 만든 뒤 (필요한 경우, disambig symbol을 이용하여 결정할 수 있는지 확인) HCLG.fst를 구성하여 동적으로 기존의 HCLG와 연결해야하는 경우 유용

기본적으로 왼쪽 bi-phone 모델에서만 작동
기존 모델이 왼쪽 bi-phone context를 사용하므로 성능 손실이 없음
```



## FST text 구조

```
<현재노드>	<다음노드>	<입력>	<출력>
0	1	M	Mars
1	2	a	<eps>
2	3	r	<eps>
3	4	s	<eps>
4
```





## Openfst - Replace()

> 기존 fst의 arc를 다른 fst로 recursive하게 바꾸는 도구

```shell
#Usage:
#fstreplace root.fst rootlabel [rule1.fst label1 ...] [out.fst]

#Example:
(echo 0  1  0  5; echo 1 0) | fstcompile > top.fst	# 기존
(echo 0  1  0  6; echo 1 0) | fstcompile > x.fst	# 새로운
fstreplace top.fst 1000 x.fst 5 | fstprint
0	1	0	0
1	2	0	6
2	3	0	0
3
```

이러한 도구는 G.fst에 다른 FST로 대체되는 기호가 있어야한다는 점에서 유사하지만

음성 Context를 처리해야하는 업무가 필요하므로 **Replace()를 사용할 수 없음**

또한 Kaldi에선 Root FST에 특별히 할당된 기호가 없으므로 FST로 대체할 수 없음



## Framwork 개요

연락처 목록 Senario를 이용하여 예시를 들자면

1. #nonterm:contact_list를 넣어서

2. 작은 LM을 만들어 (거의 대부분의 단어는 기존 모델에 없었던거겠지?)

3. graph compile

4. Big graph와 Small graph 모두 HCLG로 fully compile

5. decode 시 GrammarFst가 병합할 수 있도록 Special ilabels를 입력해줘야함

   > ilabel_info은 Context fst를 제작할 때 사용한 바 있음
   >
   > 열방향 index는 Triphone_id 이며 행방향 값들은 CI Phone으로 구성됨

   > 대부분의 ilabel들은 trainsition-dis와 관련되어있지만, 'Special ilabel'은 엄청나게 큰 수 (천만)가 들어잇음 



- GrammarFst의 StateId는 32bit integers형 2개 즉, 64bit로 구성되어있다.

  > 상위비트는, fst instance이고 하위비트는 fst instance의 상태 이다.



## Symbol Table & Special Symbol

> Symbol Table인 words.txt, phones.txt에 특정 Special Symbol을 추가함
>
> Special symbol은 사용자정의 NonTerminal 기호도 포함됨

- words.txt

```shell
tail words.txt 
ZZZ 8431 
#0 8432 
#nonterm_begin 8434 
#nonterm_end 8435 
#nonterm:foo 8437	# 사용자 정의 non terminal 기호 
#nonterm:bar 8438	# 사용자 정의 non terminal 기호
```

- phones.txt

```shell
tail phones.txt 
Z_S 243 
#0 244 
#1 245 
#2 246 
#nonterm_bos 247 
#nonterm_begin 248 
#nonterm_end 249 
#nonterm_reenter 250 
#nonterm:foo 251 
#nonterm:bar 252
```

하지만 사용자가 이 기호를 직접 추가할 필요는 없음

**validate된 dict directory에 'nonterminal.txt'를 생성하면, utils/prepare_lang.sh에 의해 자동으로 생성됨**



words.txt의 비단말 기호는 script 수준(L.fst 생성)에서만 작동하며, C++에서는 사용되지 않으며 phones.txt만 C++에서 사용됨

따라서 words.txt에는 따로 제약이 없으나, phones.txt에는 자약이 따름 내부 기호의 순서가 순서대로 있어야 하고, 사용자 정의 nonterminal이 바로 뒤에 와야하며 아래와 같은 것들이 있어야 함



일부 binary의 -nonterm-phones-offset 옵션에선, 비터미널 기호를 찾을 위치를 알려주는 옵션이 켜져있으므로, Phones.txt의 #nonterm_bos 심볼의 정수 id와 동일해야함. 위에서는 -nonterm-phones-offset=247



## G.fst

https://kaldi-asr.org/doc/grammar.html