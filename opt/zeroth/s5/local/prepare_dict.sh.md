## prepare_dict.sh

> AI-Hub kspon speech related scripts



변경사항: 24~27 line 추가 (if ~ fi)

- 변경 전 (line 22~26)

```sh
if [[ ! -s "$lexicon_raw_nosil" ]]; then
	cp $lm_dir/zeroth_lexicon $lexicon_raw_nosil || exit 1
fi

silence_phones=$dst_dir/silence_phones.txt
```



- 변경 후 (line 22~~30)

```sh
if [[ ! -s "$lexicon_raw_nosil" ]]; then
	cp $lm_dir/zeroth_lexicon $lexicon_raw_nosil || exit 1
	if [ -s $lm_dir/extra_lexicon ]; then
		env LC_ALL=C sort -u $lexicon_raw_nosil $lm_dir/extra_lexicon > $lexicon_raw_nosil.tmp
		mv -f $lexicon_raw_nosil.tmp $lexicon_raw_nosil
	fi
fi

silence_phones=$dst_dir/silence_phones.txt
```


# prepare_dict.sh

> 작성자: 이찬현



> utils/prepare_dict.sh <lm-dir\> <dst-dir\>
>
> ex) /data/local/lm  data/local/dict_nosp



> <lm-dir\>: lm돌리며 생성된 lexicon file이 있는 경로
>
> <dict_nosp\>: silence_phones / optional_silence / nonsilence_phones / extra_questions / lexicon 생성됨
>
> 다운받은 lexicon 파일을 사용하여 변형함



```shell
#!/bin/bash

# Copyright 2014 Vassil Panayotov
# Apache 2.0

# Modified by Lucas Jo 2017 (Altas Guide)
# Prepare dictionary

if [ $# -ne 2 ]; then
	echo "Usage: $0 <lm-dir> <dst-dir>"
	echo "e.g.: /data/local/lm data/local/dict_nosp"
	exit 1
fi
lm_dir=$1
dst_dir=$2

mkdir -p $dst_dir || exit 1;

# this file is  a copy of the lexicon we obtained from download_lm.sh process
lexicon_raw_nosil=$dst_dir/lexicon_raw_nosil.txt

if [[ ! -s "$lexicon_raw_nosil" ]]; then
	cp $lm_dir/zeroth_lexicon $lexicon_raw_nosil || exit 1
	if [ -s $lm_dir/extra_lexicon ]; then
		env LC_ALL=C sort -u $lexicon_raw_nosil $lm_dir/extra_lexicon > $lexicon_raw_nosil.tmp
		mv -f $lexicon_raw_nosil.tmp $lexicon_raw_nosil
	fi
fi

silence_phones=$dst_dir/silence_phones.txt
optional_silence=$dst_dir/optional_silence.txt
nonsil_phones=$dst_dir/nonsilence_phones.txt
extra_questions=$dst_dir/extra_questions.txt

echo "Preparing phone lists and clustering questions"
(echo SIL; echo SPN;) > $silence_phones
#( echo SIL; echo BRH; echo CGH; echo NSN ; echo SMK; echo UM; echo UHH ) > $silence_phones
echo SIL > $optional_silence
# nonsilence phones; on each line is a list of phones that correspond
# really to the same base phone.
awk '{for (i=2; i<=NF; ++i) { print $i; gsub(/[0-9]/, "", $i); print $i}}' $lexicon_raw_nosil |\
	sort -u |\
	perl -e 'while(<>){
chop; m:^([^\d]+)(\d*)$: || die "Bad phone $_";
$phones_of{$1} .= "$_ "; }
foreach $list (values %phones_of) {print $list . "\n"; } ' \
	> $nonsil_phones || exit 1;
# A few extra questions that will be added to those obtained by
# automatically clustering
# the "real" phones.  These ask about stress; there's also one for
# silence.
cat $silence_phones| awk '{printf("%s ", $1);} END{printf "\n";}' > $extra_questions || exit 1;
cat $nonsil_phones | perl -e 'while(<>){ foreach $p (split(" ", $_)){
	$p =~ m:^([^\d]+)(\d*)$: || die "Bad phone $_"; $q{$2} .= "$p "; } } foreach $l (values %q) {print "$l\n";}' \
		>> $extra_questions || exit 1;

echo "$(wc -l <$silence_phones) silence phones saved to: $silence_phones"
echo "$(wc -l <$optional_silence) optional silence saved to: $optional_silence"
echo "$(wc -l <$nonsil_phones) non-silence phones saved to: $nonsil_phones"
echo "$(wc -l <$extra_questions) extra triphone	clustering-related questions saved to: $extra_questions"

#(echo '!SIL SIL'; echo '[BREATH] BRH'; echo '[NOISE] NSN'; echo '[COUGH] CGH';
# echo '[SMACK] SMK'; echo '[UM] UM'; echo '[UH] UHH'
#  echo '<UNK> NSN' ) | \
(echo '!SIL SIL'; echo '<SPOKEN_NOISE> SPN'; echo '<UNK> SPN'; ) |\
cat - $lexicon_raw_nosil | sort | uniq >$dst_dir/lexicon.txt
echo "Lexicon text file saved as: $dst_dir/lexicon.txt"
exit 0

```