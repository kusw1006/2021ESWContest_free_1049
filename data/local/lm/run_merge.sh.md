## run_merge.sh

<br>

변경사항: 4-gram 을 위한 ngram -order 추가 (line 57, 58)

​				-order defalut : 3 (추측, 3-gram까진 자동으로 read)

- 변경 전(line 51~ 64)

```sh
echo 'Build a 4-gram mixed-LM --------------------------------------'
general_domain_lm=$genSrcDir/corpus.lm.fg.arpa.gz
task_domain_lm=$taskSrcDir/corpus.lm.fg.arpa.gz
test_corpus=$taskSrcDir/corpus.test
if [ "$use_best" = true ]; then
	echo 'find the best mixing weight'
	ngram -lm $general_domain_lm -ppl $test_corpus -debug 2 > $test_corpus.ppl.general_domain
	ngram -lm $task_domain_lm -ppl $test_corpus -debug 2 > $test_corpus.ppl.task_domain
	compute-best-mix $test_corpus.ppl.general_domain $test_corpus.ppl.task_domain > tmp
	lambda=$(cat tmp | grep best | awk '{print substr($6,2)}')
	
	lambda_fg=$lambda
	echo 'lamda 4-gram: '$lambda_fg 
fi
```

<br>

- 변경 후(line 51~64)

```sh
echo 'Build a 4-gram mixed-LM --------------------------------------'
general_domain_lm=$genSrcDir/corpus.lm.fg.arpa.gz
task_domain_lm=$taskSrcDir/corpus.lm.fg.arpa.gz
test_corpus=$taskSrcDir/corpus.test
if [ "$use_best" = true ]; then
	echo 'find the best mixing weight'
	ngram -lm $general_domain_lm -ppl $test_corpus -debug 2 -order 4 > $test_corpus.ppl.general_domain
	ngram -lm $task_domain_lm -ppl $test_corpus -debug 2 -order 4> $test_corpus.ppl.task_domain
	compute-best-mix $test_corpus.ppl.general_domain $test_corpus.ppl.task_domain > tmp
	lambda=$(cat tmp | grep best | awk '{print substr($6,2)}')
	
	lambda_fg=$lambda
	echo 'lamda 4-gram: '$lambda_fg 
fi
```

