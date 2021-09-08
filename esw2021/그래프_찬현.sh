scriptdir=./data/local/lm/buildLM/_scripts\_

srcdir=./data/local/lm/buildLM/_corpus\_



# ./data/local/lm/run.sh

## $scriptdir/buildlexicon.sh	$srcdir	$SegModelTxt

> 오약: Morphemes 모아서 FinalList(단어) 만들고 Lexicon 제작

### $scriptdir/genPronunciation.py

> $srcdir/finalList

### $scriptdir/genPhoneSeq.py

> $srcdir/finalList

### $scriptdir/genLexicon.py

> $srcdir/Lexicon



## $scriptdir/buildNGRAM.sh	$srcdir

> 요약: arpa파일 제작

### ngram-count -order $ngram -unk -map-unk "<UNK\>" -vocab $vocab -text $txt.train -lm $txt.lm.tg.arpa.gz -kndiscount -interpolate

> ngram count

### ngram -order 3 -lm $txt.lm.tg.arpa.gz -ppl $txt.test

> arpa파일 제작

### ngram -prune $prune_thresh_small -lm $txt.lm.tg.arpa.gz -write-lm $txt.lm.tgsmall.arpa.gz

> pruned된 arpa파일 제작











# s5/run_openslr.sh

## ./local/format_lms.sh --src-dir data/lang data/local/lm

### arpa2fst --disambig-symbol=#0 --read-symbol-table=$test/words.txt - $test/G.fst

> arpa파일을 이용해서 G.fst 제작

### utils/build_const_arpa_lm.sh data/local/lm/zeroth.lm.tg.arpa.gz data/lang data/lang_test_tglarge

> <arpa-lm-path> <old-lang-dir> <new-lang-dir>

#### arpa-to-const-arpa --bos-symbol=$bos --eos-symbol=$eos --unk-symbol=$unk "gunzip -c $arpa_lm | utils/map_arpa_lm.pl $new_lang/words.txt|" $new_lang/G.carpa

> const arpa 제작



