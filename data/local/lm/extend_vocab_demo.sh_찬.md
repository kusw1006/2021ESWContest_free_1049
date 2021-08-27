```
이 스크립트는 문법 디코딩 프레임워크를 사용하여 둘 이상의 부분으로 구성된 그래프를 작성하는 방법을 보여줍니다.

'fstequivalent'를 사용하여 이 방법으로 구성된 그래프가 LM을 모두 단일 조각으로 가지고 있는 경우 생성하는 것과 동일하다는 것을 보여줍니다.

이것은 명령줄 도구를 사용하여 일반 FST로 확장합니다(--write-as-grammar=false).

실제로 결과가 클 수 있고 전체를 작성하는 데 너무 많은 시간이 걸릴 수 있기 때문에 그렇게 하고 싶지 않을 수 있습니다. 코드 자체를 사용하면 이러한 GrammarFst 개체를 가벼운 방식으로 구성하고 이를 사용하여 디코딩할 수 있습니다.
```



## 변수 선언 및 가져오기

```shell
. ./path.sh
. utils/parse_options.sh


tree_dir=exp/chain/tree_sp
lang_base=data/lang_nosp_basevocab
lang_ext=data/lang_nosp_extvocab
```



```shell
이 스크립트의 목적을 위해 테스트를 위한 bi-phone tree와 관련 전환 모델이 필요합니다.
왜냐하면 그래프 수준에서 테스트하기 때문입니다.
다시말해 컴파일된 HCLG 그래프의 동등성을 테스트하기 때문이며, 여기에는 디코딩이 포함되지 않습니다

silprobs를 지원하는 스크립트를 작성해야 하기 때문에 지금은 "no-silprobs" 사전 dir로 이 작업을 수행하고 있습니다.	***** silprob이 있는 버전도 있으니 그거 쓰면 됨

참고로 베이스라인에 대한 'lang' 디렉토리를 만드는 방법은 다음과 같습니다.
#utils/prepare_lang.sh data/local/dict_nosp \"<UNK>" data/local/lang_tmp_nosp data/lang_nosp
```



## Stage 0

```shell
cp -r data/local/dict_nosp data/local/dict_nosp_basevocab
echo "#nonterm:unk" > data/local/dict_nosp_basevocab/nonterminals.txt

utils/prepare_lang.sh data/local/dict_nosp_basevocab \
	"<UNK>" data/local/lang_tmp_nosp $lang_base
```

1. data/local/dict_nosp를 data/local/dict_nosp_basevocab로 복사

2. #nonterm:unk를 data/local/dict_nosp_basevocab/nonterminals.txt에 넣음

3. Prepare_lang.sh 사용

   - dict-src-dir = data/local/dict_nosp_basevocab 

   - oov-dict-entry = "<unk\>"

     > 두번째 인자는 spoken noise 혹은 oov에 대한 단어(해당 단어는 lexicon.txt에 있어야 하며, 음소는 silence_phones.txt에 있어야함)

   - tmp-dir = data/local/lang_tmp_nosp

   - lang-dir = data/lang_nosp_basevocab

   



## Stage 1

```
<UNK>는 arpa파일에서 합리적인 확률 (0.0)로 나타남
아마도 arpa 파일이 빌드된 어휘가 방대하지 않아 OOV가 많이 있었기 때문.

adjust_unk_arpa.pl을 사용하여 확률을 조정할 수 있지만 지금은 그대로 둡니다.

<UNK>는 arpa파일에 꽤 자주 등장함.

언어 모델에서 우리는 이것을 #nonterm:unk로 바꿨습니다. 이것은 나중에 새로운 단어의 사용자 정의 그래프로 확장될 것입니다.

우리는 G.fst의 출력 측에 #nonterm:unk를 원하지 않거나 디코딩된 출력에 나타날 것이므로 'fstrmsymbols' 명령을 사용하여 제거합니다.
```



```shell
nonterm_unk=$(grep '#nonterm:unk' $lang_base/words.txt | awk '{print $2}')

gunzip -c  data/local/lm/lm_tgsmall.arpa.gz | \
  sed 's/<UNK>/#nonterm:unk/g' | \
  arpa2fst --disambig-symbol=#0 \
           --read-symbol-table=$lang_base/words.txt - | \
           fstrmsymbols --remove-from-output=true "echo $nonterm_unk|" - $lang_base/G.fst
```

- nonterm_unk는 data/lang_nosp_basevocab/words.txt에서 "nonterm:unk"를 포함하는 line에서의 두번째 항목 ('#nonterm:unk')
- arpa파일에서 <UNK\>를 '#nonterm:unk'로 변경
- symbol table (Words.txt)를 이용하여 arpa파일을 fst로 변환
- fst_rm_symbols로 G.fst에서 $nonterm_unk 제거



## Stage 2

```
Graph의 top-level 부분 제작
```



```shell
utils/mkgraph.sh --self-loop-scale 1.0 $lang_base $tree_dir $tree_dir/extvocab_nosp_top
```

utils/mkgraph.sh (Create HCLG decoding grph)

- lang-dir : $lang_base
- model-dir : $tree_dir
- graphdir : $tree_dir/extvocab_nosp_top



## Stage 3

```
이 작업을 수행하기 위해 sequitur(G2P 도구)를 설치해야하고, 이를 위해 몇가지 작업을 수행해야 할 수도 있음

## 오랜 시간이 걸리는 작업이라 기본값은 Skip
```



```shell
if [ $stage -le 3 ] && $run_g2p; then
  dict=data/local/dict_nosp_basevocab
  steps/dict/train_g2p.sh --silence-phones $dict/silence_phones.txt $dict/lexicon.txt\
											$tree_dir/extvocab_nosp_g2p
fi
```

- OOV에 대한 발음 생성을 위한 g2p 모델 학습





## Stage 4

```
새로 생성된 어휘 항목만 포함하는 dict-dir로 data/local/dict_nosp_newvocab 생성(그러나 이전 설정과 동일한 전화 목록, 중요하지 않음)
```



```shell
mkdir -p $tree_dir/extvocab_nosp_lexicon

# 먼저 테스트 세트에서 어휘에 없는 단어 목록을 찾습니다. 물론 이것은 완전히 속임수입니다.
awk -v w=data/lang/words.txt 'BEGIN{while(getline <w) seen[$1] = $1} {for(n=2;n<=NF;n++) 							   if(!($n in seen)) oov[$n] = 1} \
							  END{ for(k in oov) print k;}' < data/dev_clean_2/text >\
                              $tree_dir/extvocab_nosp_lexicon/words


echo "$0: generating g2p entries for $(wc -l <$tree_dir/extvocab_nosp_lexicon/words) words"

if $run_g2p; then
  steps/dict/apply_g2p.sh $tree_dir/extvocab_nosp_lexicon/words \
  $tree_dir/extvocab_nosp_g2p  $tree_dir/extvocab_nosp_lexicon
else
  cat <<EOF >$tree_dir/extvocab_nosp_lexicon/lexicon.lex


HARDWIGG	0.962436	HH AA1 R D W IH1 G
SUDVESTR	0.162048	S AH1 D V EY1 S T R
SUDVESTR	0.133349	S AH1 D V EH1 S T R
SUDVESTR	0.114376	S AH1 D V EH1 S T ER0
VINOS	0.558345	V IY1 N OW0 Z
VINOS	0.068883	V AY1 N OW0 Z
VINOS	0.068431	V IY1 N OW0 S
DOMA	0.645714	D OW1 M AH0
DOMA	0.118255	D UW1 M AH0
DOMA	0.080682	D OW0 M AH0
GWYNPLAINE'S	0.983053	G W IH1 N P L EY1 N Z
SHIMERDA	0.610922	SH IH0 M EH1 R D AH0
SHIMERDA	0.175678	SH IY0 M EH1 R D AH0
SHIMERDA	0.069785	SH AY1 M ER1 D AH0
MYRDALS	0.479183	M IH1 R D AH0 L Z
MYRDALS	0.135225	M ER1 D AH0 L Z
MYRDALS	0.115478	M IH1 R D L Z
HEUCHERA	0.650042	HH OY1 K IH1 R AH0
HEUCHERA	0.119363	HH OY1 K EH1 R AH0
HEUCHERA	0.077907	HH OY1 K ER0 AH0
IMPARA	0.906222	IH0 M P AA1 R AH0
VERLOC'S	0.564847	V ER0 L AA1 K S
VERLOC'S	0.173540	V ER1 L AH0 K S
VERLOC'S	0.050543	V ER1 L AA1 K S
UNTRUSSING	0.998019	AH0 N T R AH1 S IH0 NG
DARFHULVA	0.317057	D AA2 F UH1 L V AH0
DARFHULVA	0.262882	D AA2 F HH UH1 L V AH0
DARFHULVA	0.064055	D AA2 F HH UW1 L V AH0
FINNACTA	0.594586	F IH1 N AH0 K T AH0
FINNACTA	0.232454	F IH1 N AE1 K T AH0
FINNACTA	0.044733	F IH1 N IH0 K T AH0
YOKUL	0.845279	Y OW1 K AH0 L
YOKUL	0.051082	Y OW2 K AH0 L
YOKUL	0.029435	Y OW0 K AH0 L
CONGAL	0.504228	K AA1 NG G AH0 L
CONGAL	0.151648	K AA2 NG G AH0 L
CONGAL	0.137837	K AH0 N JH AH0 L
DELECTASTI	0.632180	D IH0 L EH0 K T EY1 S T IY0
DELECTASTI	0.203808	D IH0 L EH1 K T EY1 S T IY0
DELECTASTI	0.066722	D IH0 L EH0 K T AE1 S T IY0
YUNDT	0.975077	Y AH1 N T
QUINCI	0.426115	K W IH1 N S IY0
QUINCI	0.369324	K W IH1 N CH IY0
QUINCI	0.064507	K W IY0 N CH IY0
BIRDIKINS	0.856979	B ER1 D IH0 K AH0 N Z
BIRDIKINS	0.045315	B ER1 D AH0 K AH0 N Z
SNEFFELS	0.928413	S N EH1 F AH0 L Z
FJORDUNGR	0.130629	F Y AO1 R D UW0 NG G R
FJORDUNGR	0.125082	F Y AO1 R D AH0 NG G R
FJORDUNGR	0.111035	F Y AO1 R D UH1 NG R
YULKA	0.540253	Y UW1 L K AH0
YULKA	0.295588	Y AH1 L K AH0
YULKA	0.076631	Y UH1 L K AH0
...
EOF
  fi

# extend_lang.sh needs it to have basename 'lexiconp.txt'.
mv $tree_dir/extvocab_nosp_lexicon/lexicon.lex $tree_dir/extvocab_nosp_lexicon/lexiconp.txt

[ -f data/lang_nosp_extvocab/G.fst ] && rm data/lang_nosp_extvocab/G.fst
utils/lang/extend_lang.sh  data/lang_nosp_basevocab $tree_dir/extvocab_nosp_lexicon/lexiconp.txt  data/lang_nosp_extvocab
```

$tree_dir/extvocab_nosp_lexicon 디렉토리 만듦

data/lang/words.txt에서 첫 번째 단어 추출해서 seen배열에 저장

data/dev_clean2/text 의 2~필드 끝 까지의 $n에서 seen에 없는 단어가 나온다면 oov[$n] = 1  

-> $tree_dir/extvocab_nosp_lexicon/words에 저장 -> line수 만큼의 단어에 대한 g2p 해야함



steps/dict/apply_g2p.sh : sequiter로 단어 -> lexicon

- word-list = $tree_dir/extvocab_nosp_lexicon/words
- g2p-model-dir = $tree_dir/extvocab_nosp_g2p
- output-dir = $tree_dir/extvocab_nosp_lexicon



## Stage 5

```
추가 단어에 대해 G.fst를 만듭니다. 그들 모두에게 동일한 확률을 할당하십시오. 단어는 모두 상태 1에서 2로 전환됩니다.
```



```shell
cat <<EOF > $lang_ext/G.txt
0    1    #nonterm_begin <eps>
2    3    #nonterm_end <eps>
3
EOF

lexicon=$tree_dir/extvocab_nosp_lexicon/lexiconp.txt
num_words=$(wc -l <$lexicon)
cost=$(perl -e "print log($num_words)");

awk -v cost=$cost '{print 1, 2, $1, $1, cost}' <$lexicon >>$lang_ext/G.txt
fstcompile --isymbols=$lang_ext/words.txt --osymbols=$lang_ext/words.txt <$lang_ext/G.txt 			| fstarcsort --sort_type=ilabel >$lang_ext/G.fst
```



## Stage 6

```
포함될 그래프의 일부를 만듭니다. 코드에서 이 작업을 수행하는 방법은 ./simple_demo.sh의 'compile-graph' 명령을 참조하세요.
```



```shell
utils/mkgraph.sh --self-loop-scale 1.0 $lang_ext $tree_dir $tree_dir/extvocab_nosp_part
```



## Stage 7

```shell
offset=$(grep nonterm_bos $lang_ext/phones.txt | awk '{print $2}')
nonterm_unk=$(grep nonterm:unk $lang_ext/phones.txt | awk '{print $2}')

mkdir -p $tree_dir/extvocab_nosp_combined
[ -d $tree_dir/extvocab_nosp_combined/phones ] && rm -r $tree_dir/extvocab_nosp_combined/phones


# 디코딩 스크립트는 words.txt 및phones/를 예상하고 적절한 값을 가질 extvocab_part 그래프 디렉토리에서 복사합니다.
cp -r $tree_dir/extvocab_nosp_part/{words.txt,phones.txt,phones/}\
	$tree_dir/extvocab_nosp_combined

# 다음은 --write-as-grammar=false로 인해 일반 디코더에서 디코딩할 수 있는 FST로 컴파일됩니다.
make-grammar-fst --write-as-grammar=false --nonterm-phones-offset=$offset\
	$tree_dir/extvocab_nosp_top/HCLG.fst \
	$nonterm_unk $tree_dir/extvocab_nosp_part/HCLG.fst \
	$tree_dir/extvocab_nosp_combined/HCLG.fst
	
# 다음은 그것을 컴파일하고 GrammarFst로 씁니다. 크기는 176M이고 HCLG.fst의 경우 182M입니다. 물론 다른 예에서는 차이가 더 클 수 있습니다.
make-grammar-fst --write-as-grammar=true --nonterm-phones-offset=$offset\
	$tree_dir/extvocab_nosp_top/HCLG.fst \
	$nonterm_unk $tree_dir/extvocab_nosp_part/HCLG.fst\
	$tree_dir/extvocab_nosp_combined/HCLG.gra
```



## Stage 8

```shell
이제 실제로 테스트 데이터를 디코딩합니다.
참고로 현재(작성 당시) 체인 TDNN 시스템 local/chain/run_tdnn.sh에서 테스트 데이터를 디코딩하는 데 사용된 명령(그 단계에서 실행하여 알아낸 대로)은 다음과 같습니다. 

steps/nnet3/decode.sh --acwt 1.0 --post-decode-acwt 10.0 --frames-per-chunk 140\
	--nj 38 --cmd "queue.pl --mem 4G --num-threads 4" --online -ivector-dir \
    exp/nnet3/ivectors_dev_clean_2_hires \ exp/chain/tree_sp/graph_tgsmall \
    data/dev_clean_2_hires exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2
```



```shell
# $treedir/extvocab_nosp_combined에 있는 그래프로 교체합니다.
steps/nnet3/decode.sh --acwt 1.0 --post-decode-acwt 10.0 --frames-per-chunk 140 --nj 38 \
    --cmd "queue.pl --mem 4G --num-threads 4" --online-ivector-dir \
    exp/nnet3/ivectors_dev_clean_2_hires \
    exp/chain/tree_sp/extvocab_nosp_combined data/dev_clean_2_hires \
    exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2_ev_nosp_comb
    
 #  s5: grep WER exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2_ev_nosp_comb/wer_* | utils/best_wer.sh
 # %WER 11.79 [ 2375 / 20138, 195 ins, 343 del, 1837 sub ] exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2_ev_nosp_comb/wer_12_0.0


# 참고 아래 기준선과 비교하여 기준선은 문법 디코딩이 (아직) 지원하지 않는 묵음 확률을 사용했기 때문에 100% 비교할 수 없습니다...

# s5: grep WER exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2/wer_* | utils/best_wer.sh
# %WER 12.01 [ 2418 / 20138, 244 ins, 307 del, 1867 sub ] exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2/wer_13_0.0
```



## Stage 9

```shell
steps/nnet3/decode_grammar.sh --acwt 1.0 --post-decode-acwt 10.0 --frames-per-chunk 140 --nj 38 \
    --cmd "queue.pl --mem 4G --num-threads 4" --online-ivector-dir exp/nnet3/ivectors_dev_clean_2_hires \
    exp/chain/tree_sp/extvocab_nosp_combined data/dev_clean_2_hires exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2_ev_nosp_comb_gra

  #  The WER when decoding with the grammar FST directly is exactly the same:
  # s5:  grep WER exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2_ev_nosp_comb_gra/wer_* | utils/best_wer.sh
  # %WER 11.79 [ 2375 / 20138, 195 ins, 343 del, 1837 sub ] exp/chain/tdnn1h_sp/decode_tgsmall_dev_clean_2_ev_nosp_comb_gra/wer_12_0.0
```

