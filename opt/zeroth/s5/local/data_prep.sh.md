# data_prep.sh

> 작성자: 이찬현
>
> 경로: s5/local/data_prep.sh



## 코드 전문

> 60번째 줄에 있는 wav.scp 형성 형식에서
>
> 8k downsampling 후 16k upsampling을 진행할 수 있도록 했으나, 오류로 인해 폐기
>
> **local/download_from_openslr.sh**을 수정하는것으로 대체

```shell
#!/bin/bash

# Copyright 2014  Vassil Panayotov
#           2014  Johns Hopkins University (author: Daniel Povey)
# Apache 2.0

# Modified by Lucas Jo 2017 (Altas Guide)
# Modified by Chanhyun Lee 2021 (Konkuk Univ.)

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <src-dir> <dst-dir>"
  echo "e.g.: $0 /export/a15/vpanayotov/data/LibriSpeech/dev-clean data/dev-clean"
  exit 1
fi

src=$1
dst=$2

# all utterances are FLAC compressed
if ! which flac >&/dev/null; then
   echo "Please install 'flac' on ALL worker nodes!"
   exit 1
fi

spk_file=$src/../AUDIO_INFO

mkdir -p $dst || exit 1;

[ ! -d $src ] && echo "$0: no such directory $src" && exit 1;
[ ! -f $spk_file ] && echo "$0: expected file $spk_file to exist" && exit 1;

wav_scp=$dst/wav.scp; [[ -f "$wav_scp" ]] && rm $wav_scp
trans=$dst/text; [[ -f "$trans" ]] && rm $trans
utt2spk=$dst/utt2spk; [[ -f "$utt2spk" ]] && rm $utt2spk
spk2gender=$dst/spk2gender; [[ -f $spk2gender ]] && rm $spk2gender
utt2dur=$dst/utt2dur; [[ -f "$utt2dur" ]] && rm $utt2dur

for scriptid_dir in $(find -L $src -mindepth 1 -maxdepth 1 -type d | sort); do
  scriptid=$(basename $scriptid_dir)
  #if ! [ $scriptid -eq $scriptid ]; then  # not integer.
  #  echo "$0: unexpected subdirectory name $scriptid"
  #  exit 1;
  #fi
  
  for reader_dir in $(find -L $scriptid_dir/ -mindepth 1 -maxdepth 1 -type d | sort); do
    reader=$(basename $reader_dir)
    #if ! [ "$reader" -eq "$reader" ]; then
    #  echo "$0: unexpected reader-subdirectory name $reader"
    #  exit 1;
    #fi

	reader_gender=$(egrep "^$reader\|" $spk_file | awk -F'|' '{gsub(/[ ]+/, ""); print tolower($3)}')
	if [ "$reader_gender" != 'm' ] && [ "$reader_gender" != 'f' ]; then
      echo "Unexpected gender: '$reader_gender'"
      exit 1;
    fi
	
	echo "  "$scriptid $reader $reader_gender

    find -L $reader_dir/ -iname "*.flac" | sort | xargs -I% basename % .flac | \
		awk -v "dir=$reader_dir" '{printf "%s flac -c -d -s %s/%s.flac |\n", $0, dir, $0}' >>$wav_scp|| exit 1
    
	reader_trans=$reader_dir/${reader}_${scriptid}.trans.txt
    [ ! -f  $reader_trans ] && echo "$0: expected file $reader_trans to exist" && exit 1
    cat $reader_trans >>$trans

    # NOTE: For now we are using per-chapter utt2spk. That is each chapter is considered
    #       to be a different speaker. This is done for simplicity and because we want
    #       e.g. the CMVN to be calculated per-chapter
    awk -v "reader=$reader" -v "scriptid=$scriptid" '{printf "%s %s_%s\n", $1, reader, scriptid}' \
      <$reader_trans >>$utt2spk || exit 1
    
	# reader -> gender map (again using per-chapter granularity)
    echo "${reader}_${scriptid} $reader_gender" >>$spk2gender  

  done
done

# sort 
cat $wav_scp    | sort > tmp
cp tmp $wav_scp
cat $trans      | sort > tmp
cp tmp $trans
cat $utt2spk    | sort > tmp
cp tmp $utt2spk
cat $spk2gender | sort > tmp
cp tmp $spk2gender
rm tmp


spk2utt=$dst/spk2utt
utils/utt2spk_to_spk2utt.pl <$utt2spk >$spk2utt || exit 1

ntrans=$(wc -l <$trans)
nutt2spk=$(wc -l <$utt2spk)
! [ "$ntrans" -eq "$nutt2spk" ] && \
  echo "Inconsistent #transcripts($ntrans) and #utt2spk($nutt2spk)" && exit 1;

utils/data/get_utt2dur.sh $dst 1>&2 || exit 1

#sed -i 's\$\ sox -t flac - -r 8k -t flac - | sox -t flac - -r 16k -t flac - |\g' $wav_scp

utils/validate_data_dir.sh --no-feats $dst || exit 1;

echo "$0: successfully prepared data in $dst"

exit 0

```

