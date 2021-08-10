# Param

> - gmmdir = /exp/tri4b
> 
> - speed_perturb = false
> - trainset = train_clean
> - num_data_reps = 1
> - rvb_affix =_rvb
> - nj = 20
> 
> - maxThread=30



# 코드 분석

## Stage1: Speed Perturb

> - utils/perturb_data_dir_speed.sh: 속도 변형
>
> - utils/combine_data.sh: 폴더 병합
> - utils/validate_data_dir.sh
> - steps/make_mfcc.sh: mfcc 변환
> - steps/compute_cmvn_stats.sh: cmvn 평균, 표편계산
> - utils/fix_data_dir.sh
> - utils/copy_data_dir.sh: (일부) 데이터 복사 및 이동
> - utils/fix_data_dir.sh

```shell
# hostname중 hostInAtlas에 포함된 문자열이 있는 경우

hostInAtlas="ares hephaestus jupiter neptune"
      if [[ ! -z $(echo $hostInAtlas | grep -o $(hostname -f)) ]] && [ ! -d $mfccdir/storage ]; then
        mfcc=$(basename mfccdir) # in case was absolute pathname (unlikely), get basename.
        utils/create_split_dir.pl /mnt/{ares,hephaestus,jupiter,neptune}/$USER/kaldi-data/zeroth-kaldi-$(date +'%m_%d_%H_%M')/s5/$mfcc/storage \
          $mfccdir/storage
      fi
```

```shell
# trainset = train_clean = data/train_clean

for datadir in ${trainset} ; do
	  # 속도변형된 데이터 datadir_tmp에 저장
      utils/perturb_data_dir_speed.sh 0.9 data/${datadir} data/temp1
      utils/perturb_data_dir_speed.sh 1.1 data/${datadir} data/temp2
      utils/combine_data.sh data/${datadir}_tmp data/temp1 data/temp2
      utils/validate_data_dir.sh --no-feats data/${datadir}_tmp
      rm -r data/temp1 data/temp2
	
	  # 변형된 데이터를 가지고 mfcc 제작 및 cmvn 측정
      mfccdir=mfcc_perturbed      
      steps/make_mfcc.sh --cmd "$train_cmd" --nj $nj \
        data/${datadir}_tmp exp/make_mfcc/${datadir}_tmp $mfccdir || exit 1;
      steps/compute_cmvn_stats.sh data/${datadir}_tmp exp/make_mfcc/${datadir}_tmp $mfccdir || exit 1;
      utils/fix_data_dir.sh data/${datadir}_tmp

      utils/copy_data_dir.sh --spk-prefix sp1.0- --utt-prefix sp1.0- data/${datadir} data/temp0
      utils/combine_data.sh data/${datadir}_sp data/${datadir}_tmp data/temp0
      utils/fix_data_dir.sh data/${datadir}_sp
      rm -r data/temp0 data/${datadir}_tmp
```



## Stage2: Obtain the alignment of the perturbed data

> - steps/align_fmllr.sh: gmm을 이용한 alignment



## Stage3: Reverb Perturb

> - utils/split_data.sh [\--per-utt]<data-dir\><num-to-split\>
> - steps/data/reverberate_data_dir.py [options...] <in-data-dir\> <out-data-dir\>

```shell
  # RIR_NOISES 디렉토리가 없는 경우 데이터 다운로드
  
  if [ ! -d "RIRS_NOISES" ]; then
    # Download the package that includes the real RIRs, simulated RIRs, isotropic noises and point-source noises
    wget --no-check-certificate http://www.openslr.org/resources/28/rirs_noises.zip
    unzip rirs_noises.zip
  fi
```

```shell
# reverberate_data를 통해 reverb 추가

$train_cmd JOB=1:$nj $logdir/reverberate.JOB.log \
      steps/data/reverberate_data_dir.py \
      "${rvb_opts[@]}" \
      --prefix "rev" \
      --foreground-snrs "20:10:15:5:0" \
      --background-snrs "20:10:15:5:0" \
      --speech-rvb-probability 1 \
      --pointsource-noise-addition-probability 1 \
      --isotropic-noise-addition-probability 1 \
      --num-replications ${num_data_reps} \
      --max-noises-per-minute 20 \
      --source-sampling-rate 16000 \
      --include-original-data true \
      data/${trainset}/split$nj/JOB data/${trainset}/split$nj/JOB_rvb${num_data_reps} \
      || exit 1
```

```shell
 
 # 이전에 호출한 reverberate_data_dir.py를 통해 생성된 옵션이 scp들이 저장된 디렉토리 병합
 for i in $(seq $nj); do
    dirs+=" data/${trainset}/split$nj/${i}_rvb${num_data_reps}"
  done
  mkdir -p data/${trainset}_rvb${num_data_reps}
  utils/combine_data.sh data/${trainset}_rvb${num_data_reps} $dirs
  utils/copy_data_dir.sh data/${trainset}_rvb${num_data_reps} \
  						 data/${trainset}_rvb${num_data_reps}_hires
  utils/data/perturb_data_dir_volume.sh data/${trainset}_rvb${num_data_reps}_hires 
```

> 생성된 scp는 s5/data/train_clean_sp_rvb1/wav.scp 확인



```shell
  # duration정보 가져와서 utt2dur파일 제작
  # utt2dur is same after reverberation process
  # this will helpfull to reduce time consuming get_egs.sh in nnet3 training
  from=data/${trainset}
  to=data/${trainset}_rvb${num_data_reps}_hires
  
  for i in `seq 1 $nj`; do
	  cat data/${trainset}/split$nj/$i/reco2dur
  done | sort -k1 > $from/reco2dur  
  
  if [ -f $to/utt2dur ] ; then
    rm $to/uttdur
  fi
  for i in `seq 0 ${num_data_reps}`; do
    cat $from/reco2dur | sed -e "s/^/rev${i}-/" >> $to/utt2dur  
  done
```

```shell
# 변형된 애들의 mfcc와 cmvn계산
  for datadir in ${trainset}_rvb${num_data_reps} ; do
    steps/make_mfcc.sh --nj $nj --mfcc-config conf/mfcc_hires.conf \
      --cmd "$train_cmd" data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;
    steps/compute_cmvn_stats.sh data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;
  done

  # 새로운 utt id들을 위해 ㄱ 정렬데이터 가져오기
  ali_dirs=
  
  for i in `seq 0 $num_data_reps`; do
    local/multi_condition/copy_ali_dir.sh --cmd "$decode_cmd" --utt-prefix "rev${i}-" \
    ${gmmdir}_ali_${trainset} ${gmmdir}_ali_${trainset}_temp_$i || exit 1;
    
    ali_dirs+=" ${gmmdir}_ali_${trainset}_temp_$i"
    cp ${gmmdir}_ali_${trainset}/phones.txt  ${gmmdir}_ali_${trainset}_temp_$i/ || exit 1;
  done
  
  steps/combine_ali_dirs.sh data/${trainset}_rvb${num_data_reps} ${gmmdir}_ali_${trainset}_rvb\
  $ali_dirs || exit 1;

  # We need to build a small system just because we need the LDA+MLLT transform
  # to train the diag-UBM on top of.  We align a subset of training data for
  # this purpose.
  utils/subset_data_dir.sh data/${trainset}_rvb${num_data_reps}_hires 100000 data/train_100k_hires
  utils/subset_data_dir.sh data/${trainset}_rvb${num_data_reps}_hires 30000 data/train_30k_hires
fi
```



- frame-shfit = t: 입력프레임을 t 이동 시킨 뒤, 출력 frame을 subsampling rate 만큼 이동 (3배)
- rspecifier/wspecifier -> [kaldi I/O 매커니즘](http://kaldi-asr.org/doc/io.html) 확인

