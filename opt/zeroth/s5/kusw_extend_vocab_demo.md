## 원본

### data/lang

> 원본파일(L.fst, G.fst, lexicon, words 등등…)



### data/local/dict_nosp

> 원본 dict파일이 있는 경로



### data/local/lm

> 원본 arpa파일 (lm_tgsmall.arpa.gz)이 있는 경로





## 생성

### tree_dir

> exp/chain_rvb/tree_a

- AM 모델이 있는 곳



### lang_base

> data/lang_nosp_basevocab

- 원본 데이터의 L.fst, L_disambig.fst, phones.txt 등 prepare_lang의 결과물들 저장됨 (Stage 0)

  결과물로는 position sym이 있는 words.txt도 포함

- 원본 데이터(lm.arpa)로 생성한 G.fst가 저장됨



### lang_ext

> data/lang_nosp_extvocab

- new G.txt, G.fst 가 저장되는 폴더



### data/local/dict_nosp_basevocab

> data/local/dict_nosp의 dict관련 파일을 복사해서 넣은 곳

- 찐원본의 dict 파일들이 있는 곳

- nontermals.txt 생성

- 여기에 있는 파일들로 prepare_lang.sh 진행하여 $lang_base에 저장 (Stage 0)

  (lang_base=data/lang_nosp_basevocab)



### $tree_dir/extvocab_nosp_top

> exp/chain_rvb/tree_a 음향 모델이 있는 폴더 안의 extvocab_nosp_top 폴더

- nonterm을 추가한 새로운 HCLG.fst가 생성되는 위치 (Stage 2)



### $tree_dir/extvocab_nosp_lexicon

> 추가될 언어모델의 lexiconp 파일이 저장될 공간

- zeroth에 없는 unique한 lexicon이 생성됨 (Stage 3)
- New lexiconp.txt 생성



### $tree_dir/extvocab_nosp_part

> New HCLG 그래프가 저장되는 곳

- mkgraph를 통해 New HCLG.fst 생성됨



### $tree_dir/extvocab_nosp_combined

> 합쳐진 HCLG.fst가 생성되는 곳

- 합쳐진 HCLG.fst 생성



## 코드 전문

```shell
#!/usr/bin/env bash

# Copyright  2021 Konkuk Univ. (Chanhyun Lee)
# Apache 2.0

# top과 관련된 words.txt 등의 파일들은 data/lang에 있다고 생각하고 코드 시작
# 결국 top HCLG를 가져올때, 기존의 것을 이용하는것이 아닌 L.fst G.fst를 새롭게 nonterminal 토큰을 추가하여 제작한 뒤, HCLG로 만들어줘야함

stage=0
set -e

. ./path.sh
. utils/parse_options.sh

tree_dir=exp/chain_rvb/tree_a  # AM model이 있는 경로
lang_base=data/lang_nosp_basevocab
lang_ext=data/lang_nosp_extvocab


# prefix 변수 정하기 (default = zeroth)
# tgmed small 크기를 정하는 변수 정하기
# 파일(lexicon, rvb, tgsmall.ARPA) 있는지 체크하는 메세지 추가하기
# 경로에 다른 파일이 있는 경우 강제로 쓰게하는 모드 추가


if [ $stage -le 0 ]; then
    cp -r data/local/dict_nosp data/local/dict_nosp_basevocab
    echo "#nonterm:unk" > data/local/dict_nosp_basevocab/nonterminals.txt

    # prepare_lang.sh <dict-src-dir> <oov-dict-entry> <tmp-dir> <lang-dir>
    # <dict-src-dir>: extra_questions.txt / lexicon.txt / nonsilence_phones.txt / optional_silence.txt / silence_phones.txt 가 있는 폴더
    # <oov-dict-entry>: oov를 처리할 토큰
    # <lang-dir>: L.fst / L_disambig.fst / oov.txt / phones.txt / words.txt / topo / ngram-count 이 생길 폴더
    utils/prepare_lang.sh data/local/dict_nosp_basevocab "<UNK>" data/local/lang_tmp_nosp $lang_base
fi

if [ $stage -le 1 ]; then
  nonterm_unk=$(grep '#nonterm:unk' $lang_base/words.txt | awk '{print $2}')

  #@ LM 경로 설정
  # $lang_base에 G.fst 생성
    gunzip -c  data/local/lm/zeroth.lm.tgmed.arpa.gz | \
     sed 's/<UNK>/#nonterm:unk/g' | \
     arpa2fst --disambig-symbol=#0 \
              --read-symbol-table=$lang_base/words.txt - | \
     fstrmsymbols --remove-from-output=true "echo $nonterm_unk|" - $lang_base/G.fst
fi


if [ $stage -le 2 ]; then
  # top HCLG 생성
  # <lang_base>: L.fst, G.fst가 있는 경로
  # <tree_dir>: AM모델이 있는 곳
  # <tree_dir/extvocab_nosp_top>: HCLG.fst 가 저장될 폴더
    utils/mkgraph.sh --self-loop-scale 1.0 $lang_base $tree_dir $tree_dir/extvocab_nosp_top
fi

if [ $stage -le 3 ]; then

  # # AM 모델이 있는 폴더에 ./extvocab_nosp_lexicon 폴더 생성
  # mkdir -p $tree_dir/extvocab_nosp_lexicon

  # 기존 words.txt에 없는 단어를 추출하여
  # $tree_dir/extvocab_nosp_lexicon/words에 저장
    awk -v w=data/lang/words.txt 'BEGIN{while(getline <w) seen[$1] = $1} {for(n=2;n<=NF;n++) if(!($n in seen)) oov[$n] = 1}
                                    END{ for(k in oov) print k;}' < data/train_30k_hires/text > $tree_dir/extvocab_nosp_lexicon/words

    if $run_g2p; then
        echo "$0: generating g2p entries for $(wc -l <$tree_dir/extvocab_nosp_lexicon/words) words"
        steps/dict/apply_g2p.sh $tree_dir/extvocab_nosp_lexicon/words $tree_dir/extvocab_nosp_g2p  $tree_dir/extvocab_nosp_lexicon
    else


    # data/local/lm/run_task.sh를 실행하면 생기는 lexicon 파일
    if [ ! -f data/local/lm/buildLM/_corpus_task_/lexicon ]; then
        echo "Please build new Lexicon at data/local/lm/buildLM/_corpus_task_/lexicon"
        exit 1;
    fi
    
    # new lexicon에서 zeroth_lexicon에 없는 단어만 추가
    echo "**Creating Exclusive New Lexicon from data/local/lm/zeroth_lexicon data/local/lm/buildLM/_corpus_task_/morfessor.model.txt to $lang_ext/lexicon.txt"
    utils/filter_scp.pl --exclude data/local/lm/zeroth_lexicon data/local/lm/buildLM/_corpus_task_/lexicon > $tree_dir/extvocab_nosp_lexicon/lexicon.txt
    
    echo "**Creating $tree_dir/extvocab_nosp_lexicon/lexiconp.txt from $tree_dir/extvocab_nosp_lexicon/lexicon.txt"
    perl -ape 's/(\S+\s+)(.+)/${1}1.0\t$2/;' < $tree_dir/extvocab_nosp_lexicon/lexicon.txt > $tree_dir/extvocab_nosp_lexicon/lexiconp.txt
  
  fi

  # 기존의 L.fst와 새로운 lexiconp를 가지고 extend_lang.sh 를 통해 새로운 L.fst, words 제작
    [ -f $lang_ext/G.fst ] && rm $lang_ext/G.fst
    utils/lang/extend_lang.sh  data/lang_nosp_basevocab $tree_dir/extvocab_nosp_lexicon/lexiconp.txt $lang_ext
fi


if [ $stage -le 4 ]; then
  # 추가 단어에 대해 G.fst를 만듦
  # 모두에게 동일한 확률을 할당하며, 단어는 모두 상태 1에서 2로 전환됨
  cat <<EOF > $lang_ext/G.txt
0    1    #nonterm_begin <eps>
2    3    #nonterm_end <eps>
3
EOF
    lexicon=$tree_dir/extvocab_nosp_lexicon/lexiconp.txt
    num_words=$(wc -l <$lexicon)
    cost=$(perl -e "print log($num_words)");
    awk -v cost=$cost '{print 1, 2, $1, $1, cost}' <$lexicon >>$lang_ext/G.txt
    fstcompile --isymbols=$lang_ext/words.txt --osymbols=$lang_ext/words.txt <$lang_ext/G.txt | \
    fstarcsort --sort_type=ilabel >$lang_ext/G.fst
fi


if [ $stage -le 5 ]; then
  # tree_dir로 되어있는 부분을 우리가 기존에 가지고있는 AM 위치로 엮어줘야함 (exp/chain_rvb/tree_a)
    utils/mkgraph.sh --self-loop-scale 1.0 $lang_ext $tree_dir $tree_dir/extvocab_nosp_part
fi

if [ $stage -le 6 ]; then
    offset=$(grep nonterm_bos $lang_ext/phones.txt | awk '{print $2}')
    nonterm_unk=$(grep nonterm:unk $lang_ext/phones.txt | awk '{print $2}')

    mkdir -p $tree_dir/extvocab_nosp_combined
    [ -d $tree_dir/extvocab_nosp_combined/phones ] && rm -r $tree_dir/extvocab_nosp_combined/phones
  
  # 디코딩 스크립트는 words.txt 및phones/를 예상하고 적절한 값을 가질 extvocab_part 그래프 디렉토리에서 복사합니다.
    cp -r $tree_dir/extvocab_nosp_part/{words.txt,phones.txt,phones/} $tree_dir/extvocab_nosp_combined

  # 다음은 --write-as-grammar=false로 인해 일반 디코더에서 디코딩할 수 있는 FST로 컴파일됩니다.
    make-grammar-fst --write-as-grammar=false --nonterm-phones-offset=$offset\
    	$tree_dir/extvocab_nosp_top/HCLG.fst \
    	$nonterm_unk $tree_dir/extvocab_nosp_part/HCLG.fst \
    	$tree_dir/extvocab_nosp_combined/HCLG.fst
fi
```

