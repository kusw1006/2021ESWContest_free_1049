# Prepare_lang.sh 분석

> 작성자: 이찬현
>
> 작성일시: 21.08.28 21:27



## License

```shell
# Copyright 2012-2013  Johns Hopkins University (Author: Daniel Povey);
#                      Arnab Ghoshal
#                2014  Guoguo Chen
#                2015  Hainan Xu
#                2016  FAU Erlangen (Author: Axel Horndasch)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

# This script adds word-position-dependent phones and constructs a host of other
# derived files, that go in data/lang/.
```



## 요약

>prepare_dict를 통해 생성된 lexicon, lexiconp, silence, nonsilence, optional_silence, extra_questions를 이용하여 L.fst와 Lexicon fst를 만들기 위해 필요한 파일 생성 ``` L.fst, L_disambig.fst, oov.txt, phone dir / phones.txt words.txt topo, ngram-count```

```
이 스크립트는 다음과 같은 형식의 사전 lexicon.txt를 포함하는 소스 디렉토리가 주어지면 data/lang/과 같은 디렉토리를 표준 형식으로 준비합니다. 

또는 다음 형식의 lexiconp.txt라는 확률을 가진 사전: word pron-prob phone1 phone2 ... phoneN (0.0 < pron-prob <= 1.0); 
참고: lexiconp.txt가 있으면 lexicon.txt가 있어도 사용합니다.

그리고 또한 파일 silence_phones.txt, nonsilence_phones.txt, optional_silence.txt 및 extra_questions.txt 여기에서 silent_phone.txt 및 nonsilence_phone.txt는 각각 무음 및 무음이 아닌 전화의 목록입니다
(여기서 무음에는 다양한 종류의 소음, 웃음, 기침, 채워진 일시 정지 등이며 무음 전화에는 "실제" 전화가 포함됩니다.)

해당 파일의 각 줄에는 음소 목록이 있으며 각 줄의 전화는 동일한 "기본 음소"에 해당하는 것으로 가정합니다.
(즉, 동일한 기본 음소의 다른 스트레스 또는 톤 변형.)

"optional_silence.txt" 파일에는 사전에서 선택적 묵음에 사용되는 단일 Phone(일반적으로 SIL)만 포함되어 있습니다. 

extra_questions.txt가 비어 있을 수 있습니다.
일반적으로 Phone list으로 구성되며 각 목록의 모든 구성원은 동일한 강세 또는 어조로 구성됩니다.
Silence Phone list도 가능합니다. 이렇게 하면 자동으로 생성된 질문이 추가됩니다
(참고: 자동으로 생성된 질문은 전화기의 모든 강세/어조 버전을 동일하게 취급하므로 강세 또는 어조에 대해 "묻지 않음").
```



## Configure

```shell
#!/usr/bin/env bash

num_sil_states=5
num_nonsil_states=3
position_dependent_phones=true
# position_dependent_phones는 Position Dependent 음소 및 word_boundary.txt가 다른 Source에서 생성되었을때도 false입니다.
# 참고로 Position_dependent_phones는 _B, _E 와 같은 위치 음소들


share_silence_phones=false  # true로 되어있을경우, 모든 sil phone이 하나의 pdf로 통일됨
                            
sil_prob=0.5
unk_fst=        # make_unk_lm.sh에 의해 생성된 음소레벨 LM으로 알 수 없는 단어(<oov-dict-entry>)를 모델링하려면 이 플래그를 통해 텍스트 형식 FST를 제공합니다. <work-dir>/unk_fst.txt 여기서 <work-dir>은 make_unk_lm.sh의 두 번째 인수입니다.
                
phone_symbol_table=              # if set, use a specified phones.txt file.

extra_word_disambig_syms=        # if set, add disambiguation symbols from this file (one per line)
                                 # to phones/disambig.txt, phones/wdisambig.txt and words.txt

num_extra_phone_disambig_syms=1 # Standard one phone disambiguation symbol is used for optional silence.
                                # Increasing this number does not harm, but is only useful if you later
                                # want to introduce this labels to L_disambig.fst
```


## Option

```shell
echo "$0 $@"  # Print the command line for logging

. utils/parse_options.sh

if [ $# -ne 4 ]; then
  echo "Usage: utils/prepare_lang.sh <dict-src-dir> <oov-dict-entry> <tmp-dir> <lang-dir>"
  echo "e.g.: utils/prepare_lang.sh data/local/dict <SPOKEN_NOISE> data/local/lang data/lang"
  
  echo "<dict-src-dir>은 다음 파일을 꼭 포함하는 폴더여야함:"
  echo "extra_questions.txt  lexicon.txt nonsilence_phones.txt  optional_silence.txt  silence_phones.txt"
  
  echo "See http://kaldi-asr.org/doc/data_prep.html#data_prep_lang_creating for more info."
  
  echo "options: "
  echo "<dict-src-dir> may also, for the grammar-decoding case (see http://kaldi-asr.org/doc/grammar.html)"
  echo "contain a file nonterminals.txt containing symbols like #nonterm:contact_list, one per line."
  echo "     --num-sil-states <number of states>             # default: 5, #states in silence models."
  echo "     --num-nonsil-states <number of states>          # default: 3, #states in non-silence models."
  echo "     --position-dependent-phones (true|false)        # default: true; if true, use _B, _E, _S & _I"
  echo "                                                     # markers on phones to indicate word-internal positions. "
  echo "     --share-silence-phones (true|false)             # default: false; if true, share pdfs of "
  echo "                                                     # all silence phones. "
  echo "     --sil-prob <probability of silence>             # default: 0.5 [must have 0 <= silprob < 1]"
  echo "     --phone-symbol-table <filename>                 # default: \"\"; if not empty, use the provided "
  echo "                                                     # phones.txt as phone symbol table. This is useful "
  echo "                                                     # if you use a new dictionary for the existing setup."

  echo "     --unk-fst <text-fst>                            # default: none.  e.g. exp/make_unk_lm/unk_fst.txt."
  echo "                                                     # unknown 단어에 대한 모델을 만들 때 사용하는 옵션
  echo "                                                     # 음소 레벨 LM (rather than speical phone)에 사용
  echo "                                                     # train보다 test시에 훨씬 유용한 기능
  
  echo "     --extra-word-disambig-syms <filename>           # default: \"\"; if not empty, add disambiguation symbols"
  echo "                                                     # from this file (one per line) to phones/disambig.txt,"
  echo "                                                     # phones/wdisambig.txt and words.txt"
  exit 1;
fi

srcdir=$1
oov_word=$2
tmpdir=$3
dir=$4
```



## Main

### Lexicon

```shell
if [ -d $dir/phones ]; then
  rm -r $dir/phones
fi
mkdir -p $dir $tmpdir $dir/phones

# lexiconp_silprob.txt 파일이 존재하는 경우, silprob를 True로 설정
silprob=false
[ -f $srcdir/lexiconp_silprob.txt ] && silprob=true

# 예외 처리
[ -f path.sh ] && . ./path.sh

! utils/validate_dict_dir.pl $srcdir && \
  echo "*Error validating directory $srcdir*" && exit 1;

# lexicon 파일이 없는 경우, lexiconp 파일을 통해 lexicon 생성
if [[ ! -f $srcdir/lexicon.txt ]]; then
  echo "**Creating $srcdir/lexicon.txt from $srcdir/lexiconp.txt"
  perl -ape 's/(\S+\s+)\S+\s+(.+)/$1$2/;' < $srcdir/lexiconp.txt > $srcdir/lexicon.txt || exit 1;
fi

# lexiconp 파일이 없는 경우, $srcdir/lexicon 파일을 통해 lexiconp 파일 생성
if [[ ! -f $srcdir/lexiconp.txt ]]; then
  echo "**Creating $srcdir/lexiconp.txt from $srcdir/lexicon.txt"
  perl -ape 's/(\S+\s+)(.+)/${1}1.0\t$2/;' < $srcdir/lexicon.txt > $srcdir/lexiconp.txt || exit 1;
fi

#------------------#
# "<$srcdir>은 이미 다음 파일을 포함하고 있음
# "extra_questions.txt  lexicon.txt nonsilence_phones.txt  optional_silence.txt  silence_phones.txt"  
#------------------#
```





### 파일 검증

```shell
# 예외 처리
if [ ! -z "$unk_fst" ] && [ ! -f "$unk_fst" ]; then
  echo "$0: expected --unk-fst $unk_fst to exist as a file"
  exit 1
fi

# validation dir
if ! utils/validate_dict_dir.pl $srcdir >&/dev/null; then
  utils/validate_dict_dir.pl $srcdir  # show the output.
  echo "Validation failed (second time)"
  exit 1;
fi



# Phones.txt파일이 잇는 경우 sanity(온전성) 검사 수행
if [[ ! -z $phone_symbol_table ]]; then
  # Checks if we have position dependent phones
  n1=`cat $phone_symbol_table | grep -v -E "^#[0-9]+$" | cut -d' ' -f1 | sort -u | wc -l`
  n2=`cat $phone_symbol_table | grep -v -E "^#[0-9]+$" | cut -d' ' -f1 | sed 's/_[BIES]$//g' | sort -u | wc -l`
  $position_dependent_phones && [ $n1 -eq $n2 ] &&\
    echo "$0: Position dependent phones requested, but not in provided phone symbols" && exit 1;
  ! $position_dependent_phones && [ $n1 -ne $n2 ] &&\
      echo "$0: Position dependent phones not requested, but appear in the provided phones.txt" && exit 1;

  # Checks if the phone sets match.
  cat $srcdir/{,non}silence_phones.txt | awk -v f=$phone_symbol_table '
  BEGIN { while ((getline < f) > 0) { sub(/_[BEIS]$/, "", $1); phones[$1] = 1; }}
  { for (x = 1; x <= NF; ++x) { if (!($x in phones)) {
      print "Phone appears in the lexicon but not in the provided phones.txt: "$x; exit 1; }}}' || exit 1;
fi



# 추가적인 word-level disambig symbol이 있는 경우, 제공된 file의 모든 symbol이 유효한지 확인
if [ ! -z "$extra_word_disambig_syms" ]; then
  if ! utils/lang/validate_disambig_sym_file.pl --allow-numeric "false" $extra_word_disambig_syms; then
    echo "$0: Validation of disambiguation file \"$extra_word_disambig_syms\" failed."
    exit 1;
  fi
fi
```



### lexiconp 추가

> 음소 위치 마커(_B, _E …)를 추가한 lexiconp, lexiconp_silprob 생성


```shell
# 위치에 따른 음소(_B, _E) 옵션이 켜져있는 경우
# 단어 위치에 따라 마커(_B, _E, _S ...)를 추가하여

# $srcdir/lexiconp.txt 또는 $srcdir/lexiconp_silprob.txt를
# $tmpdir/lexiconp_lexiconp.txt 또는 $tmpdir/lexiconp_silprob.txt로 만듦

# silence에도 마커가 적용되며, lexiconp.txt에서부터 시작하여 이 작업을 수행하세요
if $position_dependent_phones; then

  if "$silprob"; then
    perl -ane '@A=split(" ",$_); $w = shift @A; $p = shift @A; $silword_p = shift @A;
              $wordsil_f = shift @A; $wordnonsil_f = shift @A; @A>0||die;
         if(@A==1) { print "$w $p $silword_p $wordsil_f $wordnonsil_f $A[0]_S\n"; }
         else { print "$w $p $silword_p $wordsil_f $wordnonsil_f $A[0]_B ";
         for($n=1;$n<@A-1;$n++) { print "$A[$n]_I "; } print "$A[$n]_E\n"; } ' \
                < $srcdir/lexiconp_silprob.txt > $tmpdir/lexiconp_silprob.txt
  else
    perl -ane '@A=split(" ",$_); $w = shift @A; $p = shift @A; @A>0||die;
         if(@A==1) { print "$w $p $A[0]_S\n"; } else { print "$w $p $A[0]_B ";
         for($n=1;$n<@A-1;$n++) { print "$A[$n]_I "; } print "$A[$n]_E\n"; } ' \
         < $srcdir/lexiconp.txt > $tmpdir/lexiconp.txt || exit 1;
  fi

  # $tmpdir/phone_map.txt 제작
  # (각 줄에) <original phone> <original phone의 버전 1> <버전 2> ...
  # 여기서 버전이란, 단어 내에서 phone의 위치에 따라 다르다.
  # 예를 들어:
  # AA AA_B AA_E AA_I AA_S

  # 이 phone map은 phone lists 전부를 word_position_depecdent 버전으로 phone lists를 확장해줌
  cat <(set -f; for x in `cat $srcdir/silence_phones.txt`; do for y in "" "" "_B" "_E" "_I" "_S"; do echo -n "$x$y "; done; echo; done) \
    <(set -f; for x in `cat $srcdir/nonsilence_phones.txt`; do for y in "" "_B" "_E" "_I" "_S"; do echo -n "$x$y "; done; echo; done) \
    > $tmpdir/phone_map.txt
else
  # lexiconp_silprob 파일이 있는 경우, silprob이 true가 되는데, 파일이 있다면 해당 파일에 대해 작업
  if "$silprob"; then
    cp $srcdir/lexiconp_silprob.txt $tmpdir/lexiconp_silprob.txt
  else
    cp $srcdir/lexiconp.txt $tmpdir/lexiconp.txt
  fi

  cat $srcdir/silence_phones.txt $srcdir/nonsilence_phones.txt | \
    awk '{for(n=1;n<=NF;n++) print $n; }' > $tmpdir/phones
  paste -d' ' $tmpdir/phones $tmpdir/phones > $tmpdir/phone_map.txt
fi



# Sets of phones for use in clustering, and making monophone systems.

# 모든 silence phone이 동일한 pdf를 공유하도록 하는 root file 작성
# [세 가지 별개의 상태가 transitions만 다를 것이다]

# 공유/비공유의 의미는 동일한 tree-root에 있는 3개의 HMM states를 공유한다는 것인가?
# models(phones)에서의 공유는 여러 phone을 한 줄의 root.txt에 작성하여 이루어 진다.
# (공유 / 비공유는 이것에 영향을 미치지 않음)

# not-shared, not-split의 의미는 3가지 state에 대해 별도의 tree-root가 있음을 의미하지만,
# tree를 분할하지 않아, stumps(그루터기)를 유지하므로
# 라인의 모든 phone이 동일한 model에 해당한다.
if $share_silence_phones; then

  cat $srcdir/silence_phones.txt | awk '{printf("%s ", $0); } END{printf("\n");}' | cat - $srcdir/nonsilence_phones.txt | \
    utils/apply_map.pl $tmpdir/phone_map.txt > $dir/phones/sets.txt
  cat $dir/phones/sets.txt | \
    awk '{if(NR==1) print "not-shared", "not-split", $0; else print "shared", "split", $0;}' > $dir/phones/roots.txt
else

다른 무음 전화에는 다른 GMM이 있습니다. [참고: 여기에서 모든 "공유 분할"은 모든 주에 대해 하나의 GMM이 있거나 주별로 분할할 수 있음을 의미합니다. 컨텍스트 독립적인 전화기이기 때문에 컨텍스트를 볼 수 없습니다.]
  # 서로 다른 silence phone은 서로 다른 GMMㅇ르 가진다.
  # (참고로, 여기에서의 모든 shared split )
  
  # different silence phones will have different GMMs.  [note: here, all "shared split" means
  # is that we may have one GMM for all the states, or we can split on states.  because they're
  # context-independent phones, they don't see the context.]
  cat $srcdir/{,non}silence_phones.txt | utils/apply_map.pl $tmpdir/phone_map.txt > $dir/phones/sets.txt
  cat $dir/phones/sets.txt | awk '{print "shared", "split", $0;}' > $dir/phones/roots.txt
fi

cat $srcdir/silence_phones.txt | utils/apply_map.pl $tmpdir/phone_map.txt | \
  awk '{for(n=1;n<=NF;n++) print $n;}' > $dir/phones/silence.txt
cat $srcdir/nonsilence_phones.txt | utils/apply_map.pl $tmpdir/phone_map.txt | \
  awk '{for(n=1;n<=NF;n++) print $n;}' > $dir/phones/nonsilence.txt
cp $srcdir/optional_silence.txt $dir/phones/optional_silence.txt
cp $dir/phones/silence.txt $dir/phones/context_indep.txt

# if extra_questions.txt is empty, it's OK.
cat $srcdir/extra_questions.txt 2>/dev/null | utils/apply_map.pl $tmpdir/phone_map.txt \
  >$dir/phones/extra_questions.txt

# Want extra questions about the word-start/word-end stuff. Make it separate for
# silence and non-silence. Probably doesn't matter, as silence will rarely
# be inside a word.
if $position_dependent_phones; then
  for suffix in _B _E _I _S; do
    (set -f; for x in `cat $srcdir/nonsilence_phones.txt`; do echo -n "$x$suffix "; done; echo) >>$dir/phones/extra_questions.txt
  done
  for suffix in "" _B _E _I _S; do
    (set -f; for x in `cat $srcdir/silence_phones.txt`; do echo -n "$x$suffix "; done; echo) >>$dir/phones/extra_questions.txt
  done
fi
```







```
add_lex_disambig.pl은 사전에 명확화 기호를 추가하고, 얼마나 많은 명확화 기호를 사용했는지 알려주고,

알려지지 않은 단어의 발음(--unk-fst가 제공된 경우)을 시퀀스 "#1 #2 #3으로 수정하는 역할을 합니다.

그리고 그 목적을 위해 disambig symbol를 예약합니다. 
#2는 나중에 실제 unk 모델로 교체됩니다. #1과 #3의 이유는 명확성과 FST를 간결하게 유지하기 위함입니다.

#1이 없으면 <unknown> 전환이 발생하는 각 시작 상태에 대해 unk-model FST의 다른 복사본 또는 최소한 일부 호가 있을 수 있습니다(끝마다 대신 더 컴팩트한 상태); 그리고 #3을 추가하면 선택적 침묵[모든 단어의 마지막 전화는 2개의 호를 얻음]으로 인해 잠재적으로 unk-model FST의 2개 사본을 갖는 것을 방지할 수 있습니다.
```

```shell
if [ ! -z "$unk_fst" ]; then # --unk-fst 옵션이 제공된 경우...
  if "$silprob"; then
    utils/lang/internal/modify_unk_pron.py $tmpdir/lexiconp_silprob.txt "$oov_word" || exit 1
  else
    utils/lang/internal/modify_unk_pron.py $tmpdir/lexiconp.txt "$oov_word" || exit 1
  fi
  unk_opt="--first-allowed-disambig 4"
else
  unk_opt=
fi

if "$silprob"; then
  ndisambig=$(utils/add_lex_disambig.pl $unk_opt --pron-probs --sil-probs $tmpdir/lexiconp_silprob.txt $tmpdir/lexiconp_silprob_disambig.txt)
else
  ndisambig=$(utils/add_lex_disambig.pl $unk_opt --pron-probs $tmpdir/lexiconp.txt $tmpdir/lexiconp_disambig.txt)
fi
ndisambig=$[$ndisambig+$num_extra_phone_disambig_syms]; # add (at least) one disambig symbol for silence in lexicon FST.
echo $ndisambig > $tmpdir/lex_ndisambig

# Format of lexiconp_disambig.txt:
# !SIL	1.0   SIL_S
# <SPOKEN_NOISE>	1.0   SPN_S #1
# <UNK>	1.0  SPN_S #2
# <NOISE>	1.0  NSN_S
# !EXCLAMATION-POINT	1.0  EH2_B K_I S_I K_I L_I AH0_I M_I EY1_I SH_I AH0_I N_I P_I OY2_I N_I T_E

( for n in `seq 0 $ndisambig`; do echo '#'$n; done ) >$dir/phones/disambig.txt

# In case there are extra word-level disambiguation symbols they also
# need to be added to the list of phone-level disambiguation symbols.
if [ ! -z "$extra_word_disambig_syms" ]; then
  # We expect a file containing valid word-level disambiguation symbols.
  cat $extra_word_disambig_syms | awk '{ print $1 }' >> $dir/phones/disambig.txt
fi

# Create phone symbol table.
if [[ ! -z $phone_symbol_table ]]; then
  start_symbol=`grep \#0 $phone_symbol_table | awk '{print $2}'`
  echo "<eps>" | cat - $dir/phones/{silence,nonsilence}.txt | awk -v f=$phone_symbol_table '
  BEGIN { while ((getline < f) > 0) { phones[$1] = $2; }} { print $1" "phones[$1]; }' | sort -k2 -g |\
    cat - <(cat $dir/phones/disambig.txt | awk -v x=$start_symbol '{n=x+NR-1; print $1, n;}') > $dir/phones.txt
else
  echo "<eps>" | cat - $dir/phones/{silence,nonsilence,disambig}.txt | \
    awk '{n=NR-1; print $1, n;}' > $dir/phones.txt
fi

# Create a file that describes the word-boundary information for
# each phone.  5 categories.
if $position_dependent_phones; then
  cat $dir/phones/{silence,nonsilence}.txt | \
    awk '/_I$/{print $1, "internal"; next;} /_B$/{print $1, "begin"; next; }
         /_S$/{print $1, "singleton"; next;} /_E$/{print $1, "end"; next; }
         {print $1, "nonword";} ' > $dir/phones/word_boundary.txt
else
  # word_boundary.txt might have been generated by another source
  [ -f $srcdir/word_boundary.txt ] && cp $srcdir/word_boundary.txt $dir/phones/word_boundary.txt
fi

# Create word symbol table.
# <s> and </s> are only needed due to the need to rescore lattices with
# ConstArpaLm format language model. They do not normally appear in G.fst or
# L.fst.

if "$silprob"; then
  # remove the silprob
  cat $tmpdir/lexiconp_silprob.txt |\
    awk '{
      for(i=1; i<=NF; i++) {
        if(i!=3 && i!=4 && i!=5) printf("%s\t", $i); if(i==NF) print "";
      }
    }' > $tmpdir/lexiconp.txt
fi

cat $tmpdir/lexiconp.txt | awk '{print $1}' | sort | uniq  | awk '
  BEGIN {
    print "<eps> 0";
  }
  {
    if ($1 == "<s>") {
      print "<s> is in the vocabulary!" | "cat 1>&2"
      exit 1;
    }
    if ($1 == "</s>") {
      print "</s> is in the vocabulary!" | "cat 1>&2"
      exit 1;
    }
    printf("%s %d\n", $1, NR);
  }
  END {
    printf("#0 %d\n", NR+1);
    printf("<s> %d\n", NR+2);
    printf("</s> %d\n", NR+3);
  }' > $dir/words.txt || exit 1;

# In case there are extra word-level disambiguation symbols they also
# need to be added to words.txt
if [ ! -z "$extra_word_disambig_syms" ]; then
  # Since words.txt already exists, we need to extract the current word count.
  word_count=`tail -n 1 $dir/words.txt | awk '{ print $2 }'`

  # We expect a file containing valid word-level disambiguation symbols.
  # The list of symbols is attached to the current words.txt (including
  # a numeric identifier for each symbol).
  cat $extra_word_disambig_syms | \
    awk -v WC=$word_count '{ printf("%s %d\n", $1, ++WC); }' >> $dir/words.txt || exit 1;
fi

# format of $dir/words.txt:
#<eps> 0
#a 1
#aa 2
#aarvark 3
#...

silphone=`cat $srcdir/optional_silence.txt` || exit 1;
[ -z "$silphone" ] && \
  ( echo "You have no optional-silence phone; it is required in the current scripts"
    echo "but you may use the option --sil-prob 0.0 to stop it being used." ) && \
   exit 1;

# create $dir/phones/align_lexicon.{txt,int}.
# This is the method we use for lattice word alignment if we are not
# using word-position-dependent phones.

# First remove pron-probs from the lexicon.
perl -ape 's/(\S+\s+)\S+\s+(.+)/$1$2/;' <$tmpdir/lexiconp.txt >$tmpdir/align_lexicon.txt

# Note: here, $silphone will have no suffix e.g. _S because it occurs as optional-silence,
# and is not part of a word.
[ ! -z "$silphone" ] && echo "<eps> $silphone" >> $tmpdir/align_lexicon.txt

cat $tmpdir/align_lexicon.txt | \
  perl -ane '@A = split; print $A[0], " ", join(" ", @A), "\n";' | sort | uniq > $dir/phones/align_lexicon.txt
```



### nonterminal 처리

```shell
# 아마 nonterminals.txt에는 nonterm 심볼이 들어가있을거임
if [ -f $srcdir/nonterminals.txt ]; then
  utils/lang/grammar/augment_phones_txt.py $dir/phones.txt $srcdir/nonterminals.txt $dir/phones.txt
  utils/lang/grammar/augment_words_txt.py $dir/words.txt $srcdir/nonterminals.txt $dir/words.txt
  cp $srcdir/nonterminals.txt $dir/phones/nonterminals.txt
  utils/sym2int.pl $dir/phones.txt <$dir/phones/nonterminals.txt >$dir/phones/nonterminals.int

  for w in "#nonterm_begin" "#nonterm_end" $(cat $srcdir/nonterminals.txt); do
    echo $w $w  # These are words without pronunciations, so leave those prons
                # empty.
  done >> $dir/phones/align_lexicon.txt
  nonterm_phones_offset=$(grep '#nonterm_bos' <$dir/phones.txt | awk '{print $2}')
  echo $nonterm_phones_offset > $dir/phones/nonterm_phones_offset.int
  echo '#nonterm_bos' > $dir/phones/nonterm_phones_offset.txt  # temporary.

  if [ -f $dir/phones/word_boundary.txt ]; then
    # word-position-dependent system.  Only include the optional-silence phone,
    # and phones that can end a word, plus the special symbol #nonterm_bos, in the
    # left-context phones.
    awk '{if ($2 == "end" || $2 == "singleton") print $1; }' <$dir/phones/word_boundary.txt | \
        cat - $dir/phones/optional_silence.txt $dir/phones/nonterm_phones_offset.txt > $dir/phones/left_context_phones.txt
  else
    cat $dir/phones/{silence,nonsilence}.txt $dir/phones/nonterm_phones_offset.txt > $dir/phones/left_context_phones.txt
  fi
  utils/sym2int.pl $dir/phones.txt <$dir/phones/left_context_phones.txt >$dir/phones/left_context_phones.int

  # we need to write utils/lang/make_lexicon_fst_silprob.py before this can work.
  grammar_opts="--left-context-phones=$dir/phones/left_context_phones.txt --nonterminals=$srcdir/nonterminals.txt"
else
  grammar_opts=
fi

# create phones/align_lexicon.int from phones/align_lexicon.txt
cat $dir/phones/align_lexicon.txt | utils/sym2int.pl -f 3- $dir/phones.txt | \
  utils/sym2int.pl -f 1-2 $dir/words.txt > $dir/phones/align_lexicon.int

# Create the basic L.fst without disambiguation symbols, for use
# in training.

if $silprob; then
  # Add silence probabilities (models the prob. of silence before and after each
  # word).  On some setups this helps a bit.  See utils/dict_dir_add_pronprobs.sh
  # and where it's called in the example scripts (run.sh).
  utils/lang/make_lexicon_fst_silprob.py $grammar_opts --sil-phone=$silphone \
         $tmpdir/lexiconp_silprob.txt $srcdir/silprob.txt | \
     fstcompile --isymbols=$dir/phones.txt --osymbols=$dir/words.txt \
       --keep_isymbols=false --keep_osymbols=false |   \
     fstarcsort --sort_type=olabel > $dir/L.fst || exit 1;
else
  utils/lang/make_lexicon_fst.py $grammar_opts --sil-prob=$sil_prob --sil-phone=$silphone \
            $tmpdir/lexiconp.txt | \
    fstcompile --isymbols=$dir/phones.txt --osymbols=$dir/words.txt \
      --keep_isymbols=false --keep_osymbols=false | \
    fstarcsort --sort_type=olabel > $dir/L.fst || exit 1;
fi

# The file oov.txt contains a word that we will map any OOVs to during
# training.
echo "$oov_word" > $dir/oov.txt || exit 1;
cat $dir/oov.txt | utils/sym2int.pl $dir/words.txt >$dir/oov.int || exit 1;
# integer version of oov symbol, used in some scripts.


# the file wdisambig.txt contains a (line-by-line) list of the text-form of the
# disambiguation symbols that are used in the grammar and passed through by the
# lexicon.  At this stage it's hardcoded as '#0', but we're laying the groundwork
# for more generality (which probably would be added by another script).
# wdisambig_words.int contains the corresponding list interpreted by the
# symbol table words.txt, and wdisambig_phones.int contains the corresponding
# list interpreted by the symbol table phones.txt.
echo '#0' >$dir/phones/wdisambig.txt

# In case there are extra word-level disambiguation symbols they need
# to be added to the existing word-level disambiguation symbols file.
if [ ! -z "$extra_word_disambig_syms" ]; then
  # We expect a file containing valid word-level disambiguation symbols.
  # The regular expression for awk is just a paranoia filter (e.g. for empty lines).
  cat $extra_word_disambig_syms | awk '{ print $1 }' >> $dir/phones/wdisambig.txt
fi

utils/sym2int.pl $dir/phones.txt <$dir/phones/wdisambig.txt >$dir/phones/wdisambig_phones.int
utils/sym2int.pl $dir/words.txt <$dir/phones/wdisambig.txt >$dir/phones/wdisambig_words.int

# Create these lists of phones in colon-separated integer list form too,
# for purposes of being given to programs as command-line options.
for f in silence nonsilence optional_silence disambig context_indep; do
  utils/sym2int.pl $dir/phones.txt <$dir/phones/$f.txt >$dir/phones/$f.int
  utils/sym2int.pl $dir/phones.txt <$dir/phones/$f.txt | \
   awk '{printf(":%d", $1);} END{printf "\n"}' | sed s/:// > $dir/phones/$f.csl || exit 1;
done

for x in sets extra_questions; do
  utils/sym2int.pl $dir/phones.txt <$dir/phones/$x.txt > $dir/phones/$x.int || exit 1;
done

utils/sym2int.pl -f 3- $dir/phones.txt <$dir/phones/roots.txt \
   > $dir/phones/roots.int || exit 1;

if [ -f $dir/phones/word_boundary.txt ]; then
  utils/sym2int.pl -f 1 $dir/phones.txt <$dir/phones/word_boundary.txt \
    > $dir/phones/word_boundary.int || exit 1;
fi

silphonelist=`cat $dir/phones/silence.csl`
nonsilphonelist=`cat $dir/phones/nonsilence.csl`

# Note: it's OK, after generating the 'lang' directory, to overwrite the topo file
# with another one of your choice if the 'topo' file you want can't be generated by
# utils/gen_topo.pl.  We do this in the 'chain' recipes.  Of course, the 'topo' file
# should cover all the phones.  Try running utils/validate_lang.pl to check that
# everything is OK after modifying the topo file.
utils/gen_topo.pl $num_nonsil_states $num_sil_states $nonsilphonelist $silphonelist >$dir/topo


# Create the lexicon FST with disambiguation symbols, and put it in lang_test.
# There is an extra step where we create a loop to "pass through" the
# disambiguation symbols from G.fst.

if $silprob; then
  utils/lang/make_lexicon_fst_silprob.py $grammar_opts \
     --sil-phone=$silphone --sil-disambig='#'$ndisambig \
     $tmpdir/lexiconp_silprob_disambig.txt $srcdir/silprob.txt | \
     fstcompile --isymbols=$dir/phones.txt --osymbols=$dir/words.txt \
       --keep_isymbols=false --keep_osymbols=false |   \
     fstaddselfloops  $dir/phones/wdisambig_phones.int $dir/phones/wdisambig_words.int | \
     fstarcsort --sort_type=olabel > $dir/L_disambig.fst || exit 1;
else
  utils/lang/make_lexicon_fst.py $grammar_opts \
       --sil-prob=$sil_prob --sil-phone=$silphone --sil-disambig='#'$ndisambig \
         $tmpdir/lexiconp_disambig.txt | \
     fstcompile --isymbols=$dir/phones.txt --osymbols=$dir/words.txt \
       --keep_isymbols=false --keep_osymbols=false |   \
     fstaddselfloops  $dir/phones/wdisambig_phones.int $dir/phones/wdisambig_words.int | \
     fstarcsort --sort_type=olabel > $dir/L_disambig.fst || exit 1;
fi


if [ ! -z "$unk_fst" ]; then
  utils/lang/internal/apply_unk_lm.sh $unk_fst $dir || exit 1

  if ! $position_dependent_phones; then
    echo "$0: warning: you are using the --unk-lm option and setting --position-dependent-phones false."
    echo " ... this will make it impossible to properly work out the word boundaries after"
    echo " ... decoding; quite a few scripts will not work as a result, and many scoring scripts"
    echo " ... will die."
    sleep 4
  fi
fi

echo "$(basename $0): validating output directory"
! utils/validate_lang.pl $dir && echo "$(basename $0): error validating output" &&  exit 1;

exit 0;
```

