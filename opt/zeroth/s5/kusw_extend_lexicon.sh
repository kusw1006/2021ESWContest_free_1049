#!/usr/bin/env bash

# Copyright 2017 Lucas Jo (Atlas Guide)
# Copyright 2021 Chanhyun Lee (Konkuk Univ.)
# Apache 2.0

resegment="False"

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

lm_dir="data/local/lm"
script_dir=$lm_dir/buildLM/_scripts_

dst=${1%/}

corpus_path="data/local/lm/buildLM/_corpus_task_/"
corpus_name="ksponcorpus.txt"
txt=${corpus_path}${corpus_name}
rectTxt=$dst/rect_corpus

if [ "$#" -ne 1 ]; then
    echo " Usage: $0 <dst>"
    echo "    ex: $0 /opt/zeroth/s5/test/"
    echo "notice: decode를 적절한 문자형식으로 바꿔줘야함 (Generally, cp949)"
    exit 1
fi

if [ ! -f $script_dir/cmudict-0.7b.txt ]; then
	echo $0: No such cmudict dictionary file.
	exit 1
fi


if [ ! -f $rectTxt ]; then
    startTime=$(date +'%F-%H-%M')
    echo $0: "1차 분류 시작" $startTime

    # 사용하는 txt파일에 따라서 decode("utf-8")을 적절히 변경해 줄 것. 일반적으로는 cp949
    gen_enc() {
        echo -en "$1" | perl -MEncode -ne '$_=encode("utf-8", decode("utf-8", $_));
            s:\r::g; # remove LF
            print "$_\n";'
    }

    export -f gen_enc

    iter=0
    old_iter=0
    files_info=()
    if [ -s $txt ]; then
        ( cat $txt | parallel gen_enc {} > $rectTxt.tmp ) &
        iter=$[iter+1]
    fi

    if [ $old_iter -ne $iter -a $[iter%12] -eq 0 ]; then
        echo -n .
        wait $(jobs -p)
    fi
    old_iter=$iter
    echo
    wait $(jobs -p)

    echo -n "$0: Run Corpus rectifier"
    echo -n .

    perl -F'\t' -ane '#next if ($F[0] =~ m:u/:); # Skip the inaudiable(or unclear) utterance of sentence
            $F[0] =~ s:(\d+)\s*/\s*(\d+):\2 분에 \1:g; #Chagne division mark
            $F[0] =~ s:\.+:.:g; # remove multi-dots
            $F[0] =~ s:([a-zA-Z])\.([a-zA-Z])\.:\1\2:g; # e.g., D.C.
            $F[0] =~ s:u/::g; # Unclear utterance of sentence mark
            $F[0] =~ s:o/::g; # Noise mark of utterance
            $F[0] =~ s:[lbn]/::g; # Breath, laugh, BG noise mark
            $F[0] =~ s:([가-힣]+?)/:\1:g; # Replace a interjection(filler words)
            $F[0] =~ s:\+::g; # Utterance repetation mark
            $F[0] =~ s:\Q*\E::g; # Unclear words utterance mark
            $F[0] =~ s:[\?\#\!,]::g; # Some other symbols
            $F[0] =~ s:([^\d])\.([^\d]):\1\2:g; # Remove dot with non-numbers
            $F[0] =~ s:([\d])\.([^\d ]):\1\2:g; # Remove dot with non-numbers
            $F[0] =~ s:([^\d ])\.([\d]):\1\2:g; # Remove dot with non-numbers
            #$F[0] =~ s:\((.+?)\)/\((.+?)\)s:\1:g; #representation (it needs too much exception)
            $F[0] =~ s:\((.+?)\)/\((.+?)\):\2:g; #representation
            $F[0] =~ s:([\w가-힣])-([\w가-힣]):\1 \2:g; #remove hyphen mark used to join words
            $F[0] =~ s:/::g; # remove some slash
            $F[0] =~ s:^[\s\.]+::g; # trim left
            $F[0] =~ s:[\s\.]+$::g; # trim right
            $F[0] =~ s: +: :g; # remove multi-spaces
            print "$F[0]\n";' $rectTxt.tmp >> $rectTxt.tmp2 || exit 1
    echo

    echo $0: Sorting Corpus
    env LC_ALL=C sort -u $rectTxt.tmp2 > $rectTxt

    rm -f $rectTxt.tmp*
    
    finishTime=$(date +'%F-%H-%M')
    echo $0: "1차 분류 완료" $finishTime
fi


if [ $resegment == "True" ]; then
    startTime=$(date +'%F-%H-%M')
    echo $0: "Re-segment transcripts" $startTime

    if ! exists morfessor; then
        echo "Morfessor is not installed, so install it"
        wd=`pwd`
        cd $KALDI_ROOT/tools
        ./extras/install_morfessor.sh
        cd $wd
        . ./path.sh
    fi

    trans=$rectTxt
    if [ ! -f $trans ]; then
        echo "$rectTxt is not found"
        exit 1
    fi

    cat $trans |\
        sed -E 's/\s+/ /g; s/^\s//g; s/\s$//g' |\
        morfessor -l $lm_dir/zeroth_morfessor.seg -T - -o - \
        --output-format '{analysis} ' --output-newlines \
        --nosplit-re '[0-9\[\]\(\){}a-zA-Z&.,\-]+'

    finishTime=$(date +'%F-%H-%M')
    echo $0: "Re-segment transcripts" $finishTime
fi

startTime=$(date +'%F-%H-%M')
echo $0: "2차 분류 시작" $startTime

if [ ! -f $rectTxt ]; then
	echo $0: No such file: $rectTxt
	exit 1
fi

echo "$0: Segmenting word class"
cat $rectTxt |\
	perl -Mutf8 -CS -pe 's/(?<=[가-힣])([^ 가-힣])/ \1/g; s/(?<=[^ 가-힣])([가-힣])/ \1/g;
			     s/(?<=[a-zA-Z])([^ a-zA-Z])/ \1/g; s/(?<=[^ a-zA-Z])([a-zA-Z])/ \1/g;
			     s/(?<=[0-9])([^0-9])/ \1/g; s/(?<=[^0-9])([0-9])/ \1/g' >\
		$rectTxt.tmp

echo "$0: Generating unique word from AM text"
parallel -a $rectTxt.tmp --pipepart --block=11M tr -s '[:space:]' '\\n' \| env LC_ALL=C sort -u | env LC_ALL=C sort -u > $dst/uniqWords.txt

grep -P '[가-힣]+_?' $dst/uniqWords.txt  | env LC_ALL=C sort -u > $dst/uniqWords.hangul
grep -v -P '[가-힣]+_?' $dst/uniqWords.txt | env LC_ALL=C sort -u > $dst/uniqWords.nonhangul
cat $dst/uniqWords.nonhangul | grep -E "^[A-Z]+_? " > $dst/uniqWords.nonhangul.alphabet
cat $dst/uniqWords.nonhangul | grep -v -E "^[A-Z]+_? " | awk '{print $1}' > $dst/uniqWords.nonhangul.etc
cat $dst/uniqWords.nonhangul.{alphabet,etc} | env LC_ALL=C sort -u > $dst/uniqWords.nonhangul.sorted

echo "$0: Generating pronunciation for non-hangul morphemes"
env LC_ALL=en_US.UTF-8 $script_dir/genPronunciation_cmu.py $dst/uniqWords.nonhangul.sorted > $dst/tmp
env LC_ALL=en_US.UTF-8 $script_dir/genPronunciation.py $dst/tmp > $dst/tmp2

awk -F'\t' '{if(NF>1){print $0}}' $dst/tmp2 > $dst/uniqWords.nonhangul.sorted.pron
awk -F'\t' '{if(NF<2){print $0}}' $dst/tmp2 > $dst/noPronList
noPronCount=$(wc -l <$dst/noPronList)
if [ $noPronCount -ne 0 ]; then
        echo $0: There exist morphemes without pronunciation, plz check noPronList: $noPronCount
        head $dst/noPronList
        echo "... (omitted) ..."
        rm -f $dst/noPronList
        exit 1
fi

echo $0: Generating pronunciation
cat $dst/uniqWords.nonhangul.sorted.pron $dst/uniqWords.hangul > $dst/finalList

# genPhoneSeq.py에서 finalList를 가지고 dic.pronun생성
env LC_ALL=en_US.UTF-8 $script_dir/genPhoneSeq.py $dst/finalList

echo $0: Extracting uniq lexicon
env LC_ALL=en_US.UTF-8 $script_dir/genLexicon.py dic.pronun | perl -pe 's/^\s+$//g' > $dst/extra_lexicon.tmp
utils/filter_scp.pl --exclude $lm_dir/zeroth_lexicon $dst/extra_lexicon.tmp > $dst/extra_lexicon
mv -f dic.pronun $dst/dic.pronun

[ ! -s $dst/noPronList ] && rm -f $dst/noPronList
[ ! -s $dst/extra_lexicon ] && rm -f $dst/extra_lexicon

#rm -f $rectTxt.tmp* $dst/tmp* $dst/*.tmp* $dst/uniqWords.* $dst/{dic.pronun,finalList,pronoun.dict}

finishTime=$(date +'%F-%H-%M')
echo $0: "2차 분류 완료" $finishTime

exit 0