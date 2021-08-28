# extend_vocab_demo.sh

## setting

```sh
#!/usr/bin/env bash

# This script demonstrates how to use the grammar-decoding framework to build
# graphs made out of more than one part.  It demonstrates using `fstequivalent`
# that the graph constructed this way is equivalent to what you would create if
# you had the LM all as a single piece.  This uses the command line tools to
# expand to a regular FST (--write-as-grammar=false) In practice you might not
# want do to that, since the result might be large, and since writing the entire
# thing might take too much time.  The code itself allows you to construct these
# GrammarFst objects in lightweight way and decode using them.

# Unfortunately the filenames here are not very well through through.  I hope to
# rework this when I have time.

stage=0
run_g2p=false  # set this to true to run the g2p stuff, it's slow so
               # by default we fake it by providing what it previously output
set -e

. ./path.sh
. utils/parse_options.sh


tree_dir=exp/chain/tree_sp
lang_base=data/lang_nosp_basevocab
lang_ext=data/lang_nosp_extvocab

```



## stage <= 0

```sh
# For the purposes of this script we just need a biphone tree and associated
# transition-model for testing, because we're testing it at the graph level,
# i.e. testing equivalence of compiled HCLG graphs; there is no decoding
# involved here.

# We're doing this with the "no-silprobs" dictionary dir for now, as we
# need to write some scripts to support silprobs with this.

# For reference, here is how we could create the 'lang' dir for the
# baseline.
#utils/prepare_lang.sh data/local/dict_nosp \
#   "<UNK>" data/local/lang_tmp_nosp data/lang_nosp

if [ $stage -le 0 ]; then
  cp -r data/local/dict_nosp data/local/dict_nosp_basevocab
  echo "#nonterm:unk" > data/local/dict_nosp_basevocab/nonterminals.txt

  utils/prepare_lang.sh data/local/dict_nosp_basevocab \
       "<UNK>" data/local/lang_tmp_nosp $lang_base
fi
```

stage가 0보다 작거나 같다면

data/local/dict_nosp를 data/local/dict_nosp_basevocab로 복사

#nonterm:unk를 data/local/dict_nosp_basevocab/nonterminals.txt에 넣음



utils/prepare_lang.sh 

- dict-src-dir = data/local/dict_nosp_basevocab 
- oov-dict-entry = "< unk>" 
- tmp-dir = data/local/lang_tmp_nosp
- lang-dir = data/lang_nosp_basevocab





## stage <= 1

```sh
if [ $stage -le 1 ]; then
  # note: <UNK> does appear in that arpa file, with a reasonable probability
  # (0.0)...  presumably because the vocab that the arpa file was built with was
  # not vast, so there were plenty of OOVs.  It would be possible to adjust its
  # probability with adjust_unk_arpa.pl, but for now we just leave it as-is.
  # The <UNK> appears quite a few times in the ARPA.  In the language model we
  # replaced it with #nonterm:unk, which will later expand to our custom graph
  # of new words.

  # We don't want the #nonterm:unk on the output side of G.fst, or it would
  # appear in the decoded output, so we remove it using the 'fstrmsymbols' command.

  nonterm_unk=$(grep '#nonterm:unk' $lang_base/words.txt | awk '{print $2}')

  gunzip -c  data/local/lm/lm_tgsmall.arpa.gz | \
    sed 's/<UNK>/#nonterm:unk/g' | \
    arpa2fst --disambig-symbol=#0 \
             --read-symbol-table=$lang_base/words.txt - | \
    fstrmsymbols --remove-from-output=true "echo $nonterm_unk|" - $lang_base/G.fst
fi
```

UNK가 나오면 확률값 할당해놨었음(arpa 파일이 크지않아서 OOV가 많이 발생했기 때문)

UNK를 lm에서 #nonterm:unk로 대체하고 이는 나중에 새로운 단어의 custom graph로 확장됨



nonterm_unk = data/lang_nosp_basevocab/words.txt에서 #nonterm:unk를 포함하는 line의 두번째 요소



lm_tgsmall.arpa.gz 압축 해제(출력으로만. 원본파일 보존)하고 < UNK>  -> #nonterm:unk로 변경

words.txt를 symbol table로 이용하여 arpa파일을 fst로 변환



fstrmsymbols로 G.fst에서 $nonterm_unk 지움



## stage <= 2

```sh
if [ $stage -le 2 ]; then
  # make the top-level part of the graph.
  utils/mkgraph.sh --self-loop-scale 1.0 $lang_base $tree_dir $tree_dir/extvocab_nosp_top
fi
```

utils/mkgraph.sh

- lang-dir : $lang_base
- model-dir : $tree_dir
- graphdir : $tree_dir/extvocab_nosp_top



## stage <= 3

```sh
if [ $stage -le 3 ] && $run_g2p; then
  # you may have to do some stuff manually to install sequitur, to get this to work.
  dict=data/local/dict_nosp_basevocab
  steps/dict/train_g2p.sh --silence-phones $dict/silence_phones.txt $dict/lexicon.txt  $tree_dir/extvocab_nosp_g2p
fi
```

defalut는 건너뜀....



## stage <= 4

새로운 단어로만 만들어진 dict_nosp_newvocab 생성

```sh
if [ $stage -le 4 ]; then
  # Create data/local/dict_nosp_newvocab as a dict-dir containing just the
  # newly created vocabulary entries (but the same phone list as our old setup, not
  # that it matters)

  mkdir -p $tree_dir/extvocab_nosp_lexicon

  # First find a list of words in the test set that are out of vocabulary.
  # Of course this is totally cheating.
  awk -v w=data/lang/words.txt 'BEGIN{while(getline <w) seen[$1] = $1} {for(n=2;n<=NF;n++) if(!($n in seen)) oov[$n] = 1}
                                END{ for(k in oov) print k;}' < data/dev_clean_2/text > $tree_dir/extvocab_nosp_lexicon/words
  echo "$0: generating g2p entries for $(wc -l <$tree_dir/extvocab_nosp_lexicon/words) words"

  if $run_g2p; then
    steps/dict/apply_g2p.sh $tree_dir/extvocab_nosp_lexicon/words $tree_dir/extvocab_nosp_g2p  $tree_dir/extvocab_nosp_lexicon
  else
    cat <<EOF >$tree_dir/extvocab_nosp_lexicon/lexicon.lex
...
FIBI	0.619154	F IH1 B IY0
FIBI	0.163168	F IY1 B IY0
FIBI	0.083443	F AY1 B IY0
IROLG	0.823123	IH0 R OW1 L G
IROLG	0.053196	IH0 R OW1 L JH
IROLG	0.021038	IH0 R OW1 L JH IY1
BALVASTRO	0.251546	B AA0 L V AA1 S T R OW0
BALVASTRO	0.213351	B AE0 L V AE1 S T R OW0
BALVASTRO	0.133005	B AA0 L V AE1 S T R OW0
BOOLOOROO	0.676757	B UW1 L UW1 R UW0
BOOLOOROO	0.173653	B UW1 L UH2 R UW0
BOOLOOROO	0.086501	B UW1 L UH0 R UW0
...

EOF
  fi

  # extend_lang.sh needs it to have basename 'lexiconp.txt'.
  mv $tree_dir/extvocab_nosp_lexicon/lexicon.lex $tree_dir/extvocab_nosp_lexicon/lexiconp.txt

  [ -f data/lang_nosp_extvocab/G.fst ] && rm data/lang_nosp_extvocab/G.fst
  utils/lang/extend_lang.sh  data/lang_nosp_basevocab $tree_dir/extvocab_nosp_lexicon/lexiconp.txt  data/lang_nosp_extvocab
fi

```

$tree_dir/extvocab_nosp_lexicon 디렉토리 만듦

data/lang/words.txt에서 첫 번째 단어 추출해서 seen배열에 저장

data/dev_clean2/text 의 2~필드끝 까지의 $n에서 seen에 없는 단어가 나온다면 oov[$n] = 1  

-> $tree_dir/extvocab_nosp_lexicon/words에 저장 -> line수 만큼의 단어에 대한 g2p 해야함



steps/dict/apply_g2p.sh : sequitur로 단어 -> lexicon

- word-list = $tree_dir/extvocab_nosp_lexicon/words
- g2p-model-dir = $tree_dir/extvocab_nosp_g2p
- output-dir = $tree_dir/extvocab_nosp_lexicon



data/lang_nosp_extvocab/G.fst 있으면 지움



utils/lang/extend_lang.sh : (lexicon에 있는 음소로 이루어진) 단어 추가

- old-lang-dir = data/lang_nosp_basevocab
- lexicon = $tree_dir/extvocab_nosp_lexicon/lexiconp.txt
- new-lang-dir = data/lang_nosp_extvocab

