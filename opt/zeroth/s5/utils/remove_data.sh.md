# remove_data.sh

> 경로: zeroth/s5/utils/remove_data.sh



> run_task.sh(_corpus\_task\_)  & make_mfcc 등
>
> 부산물 한번에 지우기(파일이 없을 시 오류뜰 수 있음) -> 표준에러 리다이렉션 어디로할지..

```sh
rm -r /opt/zeroth/s5/mfcc* 2>/dev/null
rm -r /opt/zeroth/s5/data/la* > /dev/null 2>&1
rm -r /opt/zeroth/s5/data/t*
rm -r /opt/zeroth/s5/data/kspon
rm -r /opt/zeroth/s5/data/local/dict*
rm -r /opt/zeroth/s5/data/local/lang*
# rm -r /opt/zeroth/s5/speechDATA

#find /opt/zeroth/s5/data/local/lm/* ! -name 'zeroth.lm*' ! -name 'zeroth_*' ! -name 'AUDIO_INFO' -exec rm {} \;

# rm -r /opt/zeroth/s5/data/local/lm/buildLM/_corpus_task_/*.txt.*
# rm -r /opt/zeroth/s5/data/local/lm/buildLM/_corpus_task_/uniqWord*
# rm -r /opt/zeroth/s5/data/local/lm/buildLM/_corpus_task_/rawCorpus*
# rm -r /opt/zeroth/s5/data/local/lm/buildLM/_corpus_task_/normedCorpus*
# rm -r /opt/zeroth/s5/data/local/lm/buildLM/_corpus_task_/log
# rm -r /opt/zeroth/s5/data/local/lm/buildLM/_corpus_task_/morfessor.model.txt

find /opt/zeroth/s5/data/local/lm/buildLM/_corpus_task_/* ! -name '*arpa.gz*' ! -name '*.txt' -exec rm -r {} \;

rm -r /opt/zeroth/s5/exp/*
```

