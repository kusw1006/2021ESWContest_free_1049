## run_task.sh

> 소상공인 고객주문_sample





고객 질의응답 카페	-> cafe.txt(1981 lines)

고객 질의응답 음식점 -> baedal.txt(3079 lines)

total 							-> 5060 lines



training time: 1h 20m





## run_merge.sh

> 기존 zeroth LM + 소상공인 고객주문



|         | 변경전               | 변경후                          |
| ------- | -------------------- | ------------------------------- |
| 위치    | data/local/lm        | data/local/lm/buildLM/_ corpus_ |
| 파일명1 | zeroth.lm.fg.arpa.gz | corpus.lm.fg.arpa.gz            |
| 파일명2 | zeroth.lm.tg.arpa.gz | corpus.lm.tg.arpa.gz            |

