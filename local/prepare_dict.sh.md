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

