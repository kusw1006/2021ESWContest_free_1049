## zeroth/ s5/ data/ local/ lm/ run.sh

- setting

```sh
#!/bin/bash
# Build Korean n-gram based Language Model
#
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
# Apache 2.0
# 
# run ./extras/install_srilm.sh at $KALDI_ROOT/tools
# after download and locate archeived file named as srilm.taz

## 표준출력, 에러를 디스플레이하지 않음
exists(){
    command -v "$1" >/dev/null 2>&1
}

# check parallel installed
## parallel 없으면 설치 안내
if ! exists parallel; then
    echo "Please, install parallel"
    echo "-  sudo apt-get install parallel"
    exit 1
fi


## 아래의 sh들을 실행
. ./cmd.sh
. ./path.sh


## 말뭉치 리스트
corpusList=" \
    rawCorpus_subtitle_cineaste.tar.gz \
    rawCorpus_DramaMovieScripts.tar.gz \
    rawCorpus_Bobaedream.tar.gz \
    rawCorpus_Clien.tar.gz \
    rawCorpus_Chosun.tar.gz \
    rawCorpus_Joongang.tar.gz \
    rawCorpus_NamuWiki_n.tar.gz \
    rawCorpus_DAUM_INTERVIEW.tar.gz \
    rawCorpus_DAUM_RANKINGNEWS.tar.gz \
    rawCorpus_DAUM_RANKINGNEWS2.tar.gz \
    rawCorpus_JW_AWAKE.tar.gz \
    rawCorpus_SEJONG.tar.gz \
    rawCorpus_RECSCRIPT.tar.gz \
    rawCorpus_WIKI_AA.tar.gz \
    rawCorpus_WIKI_AB.tar.gz \
    rawCorpus_WIKI_AC.tar.gz \
    rawCorpus_WIKI_AD.tar.gz \
    rawCorpus_WIKI_AE.tar.gz \
    rawCorpus_WIKI_AF.tar.gz"

## normalize_cmd의 값을 cmd에
cmd=$normalize_cmd
srcdir=buildLM/_corpus_
scriptdir=buildLM/_scripts_


## parse_options.sh 실행/ 못하면 종료
## parse_options.sh : 명령줄 구문 분석?
. parse_options.sh || exit 1;



##set -e: 오류가 날 때까지
## %F: 년 월 일 // %H: 시  // %M: 분
set -e
date=$(date +'%F-%H-%M')
echo start at $date
```



- Download rowCorpus -> 실행안됨

```sh
# Download rawCorpus
#  raw text corpus is not open-source, plz use run_task.sh
#  
#echo "Now download raw corpus -------------------------------------------------"

## 말뭉치 리스트에 있는 말뭉치 만큼 반복
## corpus랑 srcdir읽어서 넘겨주면서 download_corpus.sh 실행
#for corpus in $corpusList; do
#    $scriptdir/download_corpus.sh $corpus $srcdir
#done
#
#echo 'Untar all ----------------------------------------------------------------'


## buildLM/_corpus_에서 tar.gz확장자 찾아서 확장자 다 버려서 tardir에 넣음
## tardir이 이미 있으면 corpus가 이미 untar되었다는 뜻
## 아니라면 corpus 압축해제해서 srcdir(buildLM/_corpus_)에 넣기

#for corpus in $(find $srcdir -name "*.tar.gz"); do
#    tardir=$(echo $corpus | sed -E 's/.tar.gz//g')
#    if [ -d $tardir ]; then
#        echo "  $corpus is already untar-ed"
#        continue
#    fi
#    tar -zxvf $corpus -C $srcdir
#done

## 실제로는 rawCorpus가 opensource가 아니라서 코드가 실행 안됨..
echo "Raw text corpus is not open-source, this code is not working"
echo "  plz use run_task.sh"
exit 1
```



- corpus 비슷한 길이로 쪼개기(split)

```sh
#  split corpus into similar length around 1,000,000 line
echo 'Split corpus --------------------------------------------------------------'

## srcdir에서 확장자 안붙고 normedCorpus로 시작하지 않는 줄 찾아서 행의 개수 세기
numSplitedfiles=$(find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' -name "*.a*" | wc -l)


## 하나도 못찾으면 1,000,000줄씩 나누기
## 아니면 이미 나눠져있다..
if [ $numSplitedfiles -eq 0 ]; then
    find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' ! -name "*.a*" -type f |\
        parallel "split -l 1000000 {} {}'.'"
else
    echo '  It seems like already splited, if not plz remove *.a* files and run again'
fi


## 실제 파일은 splitedfiles에 넣기
## 만약 rowCorpus.$1없으면 splitfiles에서 rawCorpus로 복사
## srcdir/num_jobs에 job넣고 job++
splitedfiles=$(find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' -name "*.a*")
job=1
for file in $splitedfiles; do
    if [ -f $srcdir/rawCorpus.$job ]; then
        continue
    fi
    echo "  Copy $file into $srcdir/rawCorpus.$job"
    cp -rpf $file $srcdir/rawCorpus.$job
    echo $job > $srcdir/num_jobs
    job=$(( $job + 1 ))
done


## if -z: 문자열의 길이가 0인 경우
## hostInAtlas에서 hostname 찾기?
## 있으면 utils/create_split_dir.pl 실행: _corpus_에 storage 만들어서 기존 storage와 link
hostInAtlas="ares hephaestus jupiter neptune"
if [[ ! -z $(echo $hostInAtlas | grep -o $(hostname -f)) ]]; then
    echo "Found grid-engine environment ... preparing distributed computation"
    utils/create_split_dir.pl /mnt/{ares,hephaestus,jupiter,neptune}/$USER/lm_data/zeroth/s5/_corpus_/storage \
        $srcdir/storage
fi

```



- Normalization

```sh
echo 'Text normalization starts ---------------------------------------------------'

## logdir없으면 파일 만들기
nj=$(cat $srcdir/num_jobs)
logdir=$srcdir/log
if [ ! -d $logdir ]; then
    mkdir -p $logdir
fi


## srcdir/normedCorpus.1이 존재하지 않으면
## 1~nj까지 
## utils/create_data_link.pl : _corpus_/storage 꼭 존재해야함/ 기존 data와 link 해줌
## ex) egs/egs.3.4.ark -> storage/4/egs.3.4.ark 처럼 랜덤하게 숫자 정해서 link
## 특수문자 제거, 단위문자 전환, 숫자변환... 등 normalization해서 normedCorpus.n에 저장

if [ ! -e $srcdir/normedCorpus.1 ] ; then
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/normedCorpus.$n
    done
    $cmd JOB=1:$nj $logdir/rawCorpus.JOB.log \
        $scriptdir/normStep1.py $srcdir/rawCorpus.JOB \| \
        $scriptdir/normStep2.py \| \
        $scriptdir/normStep_tmp.py \| \
        $scriptdir/normStep4.py \| \
        $scriptdir/strip.py  \> $srcdir/normedCorpus.JOB || exit 1;
fi

```



- find uniq words 

```sh
echo 'Finding Uniq. words for morpheme analysis --------------------------------------'
## uniqWords.1 없으면 utils/create_data_link.pl에 uniqWords 넣어서 실행
## tr -s [space] \n : 띄어쓰기를 개행문자로 바꿈
## sort | uniq -c: 정렬하고 같은라인이 몇번나오는지 표시 ex) 1 orange \ 2 apple
## sort -k1 -n -r: 위에서 찾은 (몇번나오는지 표시된) 숫자를 기준으로 역순 정렬
if [ ! -e $srcdir/uniqWords.1 ] ; then
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/uniqWords.$n
    done
    $cmd JOB=1:$nj $logdir/normedCorpus.JOB.log \
        cat $srcdir/normedCorpus.JOB \| \
        tr -s \'[:space:]\' \'\\n\' \| sort \| uniq -c \| \
        sort -k1 -n -r \> $srcdir/uniqWords.JOB || exit 1;
fi
```



- uniqWordList statistics

```sh
echo "Accumulate statistics into: uniqWordList -----------------------------------------"

## uniqWordList가 없다면
## uniqWords들 sumStatUniqWords.py에 넣어서 결과값 uniqWordList에 넣기
## sumStatUniqWords.py: 단어 몇번나오는지.. -> 단어 많이 나오는 순으로 정렬

## awk.. uniqWordList에 대해서
## sum=0, cnt=0으로 시작해서 
## cnt+=1, 한번나온 단어들이 나올때마다 sum+=1
## 다 읽으면 sum/cnt 출력
## total uniq. word count: $cnt
## percentage= sum/cnt * 100 (uniqWordList에서 한번 카운트된 단어/uniqWordList 안의 모든 단어)

if [ ! -f $srcdir/uniqWordList ]; then
    cat $srcdir/uniqWords.* | \
        $scriptdir/sumStatUniqWords.py > $srcdir/uniqWordList
    stat=$(awk 'BEGIN{sum=0;cnt=0}{cnt+=1;if($2 == 1){sum+=1}}END{print sum"/"cnt}' $srcdir/uniqWordList)
    echo "  total uniq. word count: $(echo $stat | awk -F'/' '{print $2}')"
    percentage=$(echo "print('portion of freq.== 1 word: {:.2f} %'.format($stat*100))" | python3)
    echo "  $percentage"
fi
```



- Pruning uniqWordList

  > 가지치기 단계. med와 small model 생성 (3-gram에 대해서만 제작, 4-gram은 그냥 large 사용)

```sh
echo "Pruning uniqWordList for Morfessor training ------------------------------------"
coverage=0.98
srcFile=$srcdir/uniqWordList
inFile=$srcdir/uniqWordList.hangul
inFile2=$srcdir/uniqWordList.nonhangul
outFile=$srcdir/uniqWordList.hangul.pruned

## inFile이 정규파일이 아니라면
## 가-힣 0-9부분만 찾아서 awk로 넘김
## 전달받은 부분 길이나 단어카운트 수 봐서 바로 inFile에 넘겨주거나
## $0>uniqWordList.hangul.remained 하고 inFile에 넣음
## grep -v: select non matching line -> nonhangul에 넣음
## totalCnt에는 WordList.hangul에 들어있는 횟수들 총합해서 넣기

## awk// sum 더해가면서 sum/totalCnt가 0.98보다 작으면 단어 outFile에 넣음
## 0.98보다 커지면 $1>uniqWordList.hangul.pruned.remained 하고 outFile에 넣음
## 빈도수 높은순으로 98%만 뽑겠다는 의미
## outFile내의 행 개수 세서 final uniq. word for training 출력
if [ ! -f $inFile ]; then
    grep -E '[가-힣]+ [0-9]+' $srcFile |\
		awk -v file=$inFile '{if(length($1)<=10 || $2>5){print $0}else{print $0 > file".remained"}}' > $inFile  ##  
	grep -v -E '[가-힣]+ [0-9]+' $srcFile > $inFile2
    
	totalCnt=$(awk 'BEGIN{sum=0}{sum+=$2}END{print sum}' $inFile)
    echo '  pruned coverge:' $coverage
    echo '  total acc. count:' $totalCnt
    awk -v totalCnt="$totalCnt" -v coverage="$coverage" -v file=$outFile \
        'BEGIN{sum=0}{sum+=$2; if(sum/totalCnt <= coverage){print $1}else{print $1 > file".remained"}}' $inFile > $outFile
	echo "  final uniq. word for training: $(wc -l <$outFile)"
fi

```




- Morfessor model training

```sh
echo 'Morfessor model training  --------------------------------------------------'


## _corpus_/morfessor.model.pickled가 없다면
## --traindata-list -t $outFile : outFile을 input file로 넣음(split 되어있음)
## morfessor.model.txt -> 1.0 style model로 save /발음의 다양성을 위해
## morfessor.model.pickled -> binary model로 save
## morfessor.lexicon -> /-x: uniq.morpheme만 알면 안되기 때문에...?
## randsplit: 0.5 확률로 무작위 분할 
## skips: 건너뜀 -> training speed up
## nosplit-re: 뒤의 표현들로 감싸져있으면 분할 x

if [ ! -f $srcdir/morfessor.model.pickled ]; then
    morfessor --traindata-list \
        -t $outFile \
        -S $srcdir/morfessor.model.txt \
        -s $srcdir/morfessor.model.pickled \
        -x $srcdir/morfessor.lexicon \
        --randsplit 0.5 --skips \
		--progressbar \
        --nosplit-re '[0-9\[\]\(\){}a-zA-Z&.,\-]+'

	#morfessor --traindata-list \
    #    -t $outFile \
    #    -S $srcdir/morfessor.model.txt \
    #    -s $srcdir/morfessor.model.pickled \
    #    -x $srcdir/morfessor.lexicon \
	#	-a viterbi --viterbi-smoothing 20 \
	#	--randsplit 0.5 --skips \
	#	--progressbar \ 
    #    --nosplit-re '[0-9\[\]\(\){}a-zA-Z&.,\-]+'

fi

## _corpus_task_ 하위 morfessor.model.pickled가 _corpus_하위 morfessor.model.pickled보다
## 최근파일이면 segModel들 _corpus_task_걸로 변경
segModel=$srcdir/morfessor.model.pickled
segModelTxt=$srcdir/morfessor.model.txt
segModelLexicon=$srcdir/morfessor.lexicon
if [ -f buildLM/_corpus_task_/morfessor.model.pickled ] && 
	[ buildLM/_corpus_task_/morfessor.model.pickled -nt $srcdir/morfessor.model.pickled ]; then
	segModel=buildLM/_corpus_task_/morfessor.model.pickled
	segModelTxt=buildLM/_corpus_task_/morfessor.model.txt
	segModelLexicon=buildLM/_corpus_task_/morfessor.lexicon
	echo "  found more recently trained segment model: "
	echo "  1.  $segModel"
	echo "  2.  $segModelTxt"
	echo "  3.  $segModelLexicon"
	echo "  use this one"
fi
```



- Morpheme segmentation

```sh
echo 'Morpheme segmentation -----------------------------------------------------'

# The Morfessor should be installed in the all Grid machines
## normedCorpus.seg.1이 없다면
## n=1~nj 에 대해
## create_data_link.pl <-normedCorpus.seg.$n
## morfessor -l $segModel: binary model로 불러오기
## --output-format '{analysis}': 기존 띄어쓰기 위치를 알 수 있는 기호 사용 강제
## normedCorpus.n -> input corpus file to analyze

if [ ! -f $srcdir/normedCorpus.seg.1 ]; then
    for n in $(seq $nj); do
        # the next command does nothing unless _corpus_/storage/ exists, see
        # utils/create_data_link.pl for more info.
        utils/create_data_link.pl $srcdir/normedCorpus.seg.$n
    done
	
    $cmd JOB=1:$nj $logdir/normedCorpus.seg.JOB.log \
		morfessor -l $segModel \
		--output-format \'{analysis} \' -T $srcdir/normedCorpus.JOB \
		-o $srcdir/normedCorpus.seg.JOB --output-newlines \
		--nosplit-re "'[0-9\[\]\(\){}a-zA-Z&.,\-]+'"
fi

```



- Extract uniq Morphemes

```sh
echo 'Extract uniq Morphemes ----------------------------------------------------------'
# nonHangulList from general domain (freq. > 10)  + morphemes from Morfessor

## morphemes가 없다면
## uniqWordList.nonhangul에서 A-Z로 시작하는 라인들을 uniqWordList.nonhangul.alphabet에 넣음
## A-Z로 시작하지 않는것들은 morphemes.etc에 넣음

## -lexicon-
## 나무숲 n a m u s u b2
## n->morphems.hangul
## 한글/영어/기타등등에 대한 morphemes를 정렬하고
## 겹치는 것 제외해서 morphemes에 넣음



if [ ! -f $srcdir/morphemes ]; then

	cat $srcdir/uniqWordList.nonhangul | grep -E "^[A-Z]+ " > $srcdir/uniqWordList.nonhangul.alphabet
	cat $srcdir/uniqWordList.nonhangul | grep -v -E "^[A-Z]+ " | awk '{print $1}' > $srcdir/morphemes.etc

	coverage=0.98
	totalCnt=$(awk 'BEGIN{sum=0}{sum+=$2}END{print sum}' $srcdir/uniqWordList.nonhangul.alphabet)
    awk -v totalCnt="$totalCnt" -v coverage="$coverage" \
        'BEGIN{sum=0}{sum+=$2; if(sum/totalCnt <= coverage){print $1}}' $srcdir/uniqWordList.nonhangul.alphabet \
		> $srcdir/morphemes.alphabet


	cat $segModelLexicon | awk '{print $2}' > $srcdir/morphemes.hangul
	cat $srcdir/morphemes.hangul $srcdir/morphemes.alphabet $srcdir/morphemes.etc |\
		sort | uniq > $srcdir/morphemes
	
	echo '  morphemes hangul: '$(wc -l <$srcdir/morphemes.hangul)
	echo '  morphemes alphabet: '$(wc -l <$srcdir/morphemes.alphabet)
	echo '  morphemes etc: '$(wc -l <$srcdir/morphemes.etc)
	echo '  total morphemes: '$(wc -l <$srcdir/morphemes) 
	echo '  check morphemes longer than 10 characters'
	awk 'BEGIN{sum=0;total=0}{if(length($1)>10){print $0;sum+=1}total+=1}END{print(sum" "total)}' \
		$srcdir/morphemes
fi
```



- build lexicon

``` sh
echo "Starts to build lexicon ----------------------------------------------------------"

##lexicon이 없다면
## buildLexicon.sh에 srcdir과 segModelTxt넣고 실행
## buildLexicon.sh: morphemes 모아서 finalList(단어)만들고 
## 					genPhoneSeq.py를 통해 발음사전 만듦 -> lexicon


if [ ! -f $srcdir/lexicon ]; then
(
	$scriptdir/buildLexicon.sh $srcdir $segModelTxt
)&
fi


## n-gram language model 없으면 buildNGRAM.sh에 srcdir 넣고 실행
## buildNGRAM.sh: corpus섞고 train, test set을 split함
##				train, test corpus 병합하고 LM만듦
## 				perplexity(예측도) test하고 pruned LM 생성


echo "Starts to build n-gram language model ---------------------------------------------"
if [ ! -f $srcdir/corpus.lm.fg.arpa.gz ]; then
(
	$scriptdir/buildNGRAM.sh $srcdir
)&
fi
wait


## LM 최신화
echo "Copy LM files to top --------------------------------------------------------------"
echo "  $segModel"
cp -rpf $segModel zeroth_morfessor.seg
cp -rpf $srcdir/lexicon zeroth_lexicon
cp -rpf $srcdir/corpus.lm.fg.arpa.gz zeroth.lm.fg.arpa.gz
cp -rpf $srcdir/corpus.lm.tg.arpa.gz zeroth.lm.tg.arpa.gz
cp -rpf $srcdir/corpus.lm.tgmed.arpa.gz zeroth.lm.tgmed.arpa.gz
cp -rpf $srcdir/corpus.lm.tgsmall.arpa.gz zeroth.lm.tgsmall.arpa.gz

date=$(date +'%F-%H-%M')
echo ends at $date
```





### morfessor

[morfessor 공식 홈페이지](https://morfessor.readthedocs.io/en/latest/cmdtools.html#)


 - Loading existing model

   - **-l <file> :  load binary model**

   - -L <file> :  load Morfessor 1.0 style text model


 - Loading data

   - **-t <file>, --traingdata <file> : input corpus file for training(split data)**
   - **--traindata-list : interpret all training files as list files instead of corpus files**                                      (one compound per line)
   - -T <file>, --testdata <file> : input corpus file to analyze

 

 - Training model options

   - -m <mode>, --mode <mode>
   
     - none : Do initialize of train a model/ just loading a model for new data
     - init: create new model and load input data/ does not train the model
     - batch: loads an existing model(already initialized)&run Batch training
     - init+batch: create a new model, load input data, run Batch training
  - online: create a new model, read and train the model .. Online training
     - online+batch: first with Online training->retrain using Batch training

   - -a <algorithm>, --algorithm <algorithm>
   
     - recursive
     - viterbi: Local Viterbi training
   
   - -d <type>, --dampening <type>
   
     - none: token based training
  - log: x-> log(x) // log-token based training
     - ones: Treat all compounds as if they only occured once (type based training)
   
   - -f <list> , --forcesplit <list>
   
  - no force -> -f ""
     - to split -> -f " '-' "
   
   - -F <float>, --finish-threshold <float>

     - default: 0.005

   - -r <seed>, --randseed <seed>
   
     - seed for random number generator
   
   - **-R <float>, --randsplit <float>**
   
  - initialize new words by random splitting using the given split probability
     - default - no splitting

   - **--skips: use random skips for frequently seen conpounds to speed up training**

   - --batch-minfreq <int> : compound frequency threshold for batch training(default 1)

   - --max-epochs <int>: hard maximum of epochs in training
   
   - **--nosplit-re <regexp>**
   
     : expression matches the two surrounding characters  -> do not allow splitting (default none)
   
   - --online-epochint<int>: epoch interval for online training(defalut 10000)
   
   - --viterbi-smoothing <float>: additive smoothing parameter for Viterbi training
   
   - --viterbi-maxlen <int>: maximum construction length in Viterbi training (default 30)

   

   - Saving model

     - **-s <file> : save Binary model**
   - **-S <file> : save Morfessor 1.0 style text model**
  - --save-reduced: save Reduced Binary model



- morfessor-segment

   - morfessor-segment [arguments] testcorpus-file [testcorpus-file] ....

  - -l <file> // -L <file>



- morfessor-evaluate

  - morfessor-evaluate [arguments] <goldstandard> <model> [<model> ....]



- Positional arguments

  - <goldstandard> : gold standard file in standard annotation format

  - <model>: model files to segment(binary of 1.0 style)



- Optional arguments

  --num-samples / --sample-size / --format-string / --format-template...



- Data format command line options

  - --encoding <encoding> : encoding of input and output files

  - --lowercase: lowercase input data

  - **--traindata-list: input file for batch training are lists(one compound per line)**

  - **--output-format <format>**

    - **{analysis} = constructions of the compound**
     - {compound}= compound string

   - **--output-newlines: for each newline in input, print newline in output file**

 

 - Universal command line options

  - **--progressbar: force the progressbr to be displayed**

