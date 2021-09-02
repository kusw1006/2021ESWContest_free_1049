#!/usr/bin/env bash


# top과 관련된 words.txt 등의 파일들은 data/lang에 있다고 생각하고 코드 시작

# 결국 top HCLG를 가져올때, 기존의 것을 이용하는것이 아닌 L.fst G.fst를 새롭게 nonterminal 토큰을 추가하여 제작한 뒤, HCLG로 만들어줘야함

stage=0
set -e

. ./path.sh
. utils/parse_options.sh

tree_dir=exp/chain_rvb/tree_a  # AM model이 있는 경로
lang_base=data/lang_nosp_basevocab
lang_ext=data/lang_nosp_extvocab

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
  gunzip -c  data/local/lm/lm_tgsmall.arpa.gz | \
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
    utils/prepare_lang.sh data/local/dict_nosp "<UNK>" data/local/lang_tmp_nosp data/lang_nosp

  fi


# 위의 코드 실행해봐
###################@@@@@@ exp/chain_rvb가 최종적인 AM exp/chain_rvb/tree_a

  # extend_lang.sh needs it to have basename 'lexiconp.txt'.
  mv $tree_dir/extvocab_nosp_lexicon/lexicon.lex $tree_dir/extvocab_nosp_lexicon/lexiconp.txt



  # 기존의 L.fst와 새로운 lexiconp를 가지고 extend_lang.sh 를 통해 새로운 L.fst 제작
  [ -f data/lang_nosp_extvocab/G.fst ] && rm data/lang_nosp_extvocab/G.fst
  utils/lang/extend_lang.sh  data/lang_nosp_basevocab $tree_dir/extvocab_nosp_lexicon/lexiconp.txt  data/lang_nosp_extvocab
fi