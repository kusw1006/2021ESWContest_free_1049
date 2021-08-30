## run_task.sh

> 소상공인 고객주문_sample

<br>

<br>

고객 질의응답 카페	-> cafe.txt(1981 lines)

고객 질의응답 음식점 -> baedal.txt(3079 lines)

total 							-> 5060 lines

<br>

training time: 1h 20m

<br>

<br>

## run_merge.sh

> 기존 zeroth LM + 소상공인 고객주문

<br>

|         | 변경전               | 변경후                          |
| ------- | -------------------- | ------------------------------- |
| 위치    | data/local/lm        | data/local/lm/buildLM/_ corpus_ |
| 파일명1 | zeroth.lm.fg.arpa.gz | corpus.lm.fg.arpa.gz            |
| 파일명2 | zeroth.lm.tg.arpa.gz | corpus.lm.tg.arpa.gz            |



- zeroth 제공

zeroth.lm.fg.arpa.gz 4.2G

zeroth.lm.tg.arpa.gz 2.7G

zeroth.lm.tgmed.arpa.gz 64M

zeroth.lm.tgsmall.arpa.gz 25M



- 소상공인 corpus

corpus.lm.fg.arpa.gz 2.3M

corpus.lm.tg.arpa.gz 2.3M

corpus.lm.tgmed.arpa.gz 2.3M

corpus.lm.tgsmall.arpa.gz 2.3M



- merge

mixed.lm.fg.arpa.gz 2.6G

mixed.lm.tg.arpa.gz 2.7G

mixed.lm.tgmed.arpa.gz 6.3M

mixed.lm.tgsmall.arpa.gz 4.3M

