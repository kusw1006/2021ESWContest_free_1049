# run_ivector_common 통화 데이터 전처리 추가

## Code

  ```shell
  echo "$0: generating phone call noise"
  sed -i '2~2 s\$\sox -t wav - -t wav - highpass 100 | sox -t wav - -t wav - lowpass 1000 | sox -t wav - -t wav - dither -s |\g' data/${trainset}/wav.scp
  ```


## Meaning

  1. 통화 환경과 일치하는 음성 데이터 구축 및 학습
  2. sox pipeline을 구축하여 체계적 음성 데이터 전처리
  3. 유무선 통신 환경에서 사용되는 코덱 반영



## 유무선 통신 통화 코덱

  - 현재 상용화 된 코덱 : G.729a [picture G.729a]
  - 코덱 활용에는 유료화 문제가 있음
  - sox를 활용하여 최대한 코덱과 유사한 전처리 진행



## Analog to Digital Conversion

  - 표본화(Sampling), 양자화(Quantization), 부호화(Coding)과정 거침
  - 나이퀴스트 표준화 이론에 따라 샘플링 2배
  - decoding 과정에서 노이즈를 줄이기 위해 dither 과정을 거침



## 코드 해석

  1. wav sample rate이 16000Hz 이므로 기본 샘플링을 8000Hz로 설정
   - sox input.wav -r 8k output.wav
  2. sample rate 8000Hz -> 16000Hz
   - sox input.wav -r 16k output.wav
  3. 통화 코덱과 유사한 전처리를 위해 100-1000Hz bandpass filter 적용
   - sox input.wav output.wav lowpass 1000
   - sox input.wav output.wav highpass 100
  4. decoing 과정 노이즈 추가 효과 삽입
   - sox input.wav output.wav dither -s
  5. 1~4과정은 MFCC의 효율적인 특징 추출을 위해 짝수 데이터에 삽입

  6. 추가 gain에 따른 학습을 위해 8번째 데이터마다 gain 16db
   - sox input.wav output.wav gain 16







## 코드 전문

```shell
#!/bin/bash

# this script contains some common (shared) parts of the run_nnet*.sh scripts.
. cmd.sh


stage=0
gmmdir=exp/tri4b
speed_perturb=false
trainset=train_clean

# ★노이즈 입힌 데이터 몇종류 만들건지 설정 
num_data_reps=3
rvb_affix=_rvb
nj=20
maxThread=30  # the max number of schedullable thread on your machine 

set -e
. cmd.sh
. ./path.sh
. ./utils/parse_options.sh


if [ "$speed_perturb" == "true" ]; then
  if [ $stage -le 1 ]; then
    #Although the nnet will be trained by high resolution data, we still have to perturbe the normal data to get the alignment
    # _sp stands for speed-perturbed

    for datadir in ${trainset} ; do
      utils/perturb_data_dir_speed.sh 0.9 data/${datadir} data/temp1
      utils/perturb_data_dir_speed.sh 1.1 data/${datadir} data/temp2
      utils/combine_data.sh data/${datadir}_tmp data/temp1 data/temp2
      utils/validate_data_dir.sh --no-feats data/${datadir}_tmp
      rm -r data/temp1 data/temp2

      mfccdir=mfcc_perturbed
      hostInAtlas="ares hephaestus jupiter neptune"
      if [[ ! -z $(echo $hostInAtlas | grep -o $(hostname -f)) ]] && [ ! -d $mfccdir/storage ]; then
        mfcc=$(basename mfccdir) # in case was absolute pathname (unlikely), get basename.
        utils/create_split_dir.pl /mnt/{ares,hephaestus,jupiter,neptune}/$USER/kaldi-data/zeroth-kaldi-$(date +'%m_%d_%H_%M')/s5/$mfcc/storage \
          $mfccdir/storage
      fi
      steps/make_mfcc.sh --cmd "$train_cmd" --nj $nj \
        data/${datadir}_tmp exp/make_mfcc/${datadir}_tmp $mfccdir || exit 1;
      steps/compute_cmvn_stats.sh data/${datadir}_tmp exp/make_mfcc/${datadir}_tmp $mfccdir || exit 1;
      utils/fix_data_dir.sh data/${datadir}_tmp

      utils/copy_data_dir.sh --spk-prefix sp1.0- --utt-prefix sp1.0- data/${datadir} data/temp0
      utils/combine_data.sh data/${datadir}_sp data/${datadir}_tmp data/temp0
      utils/fix_data_dir.sh data/${datadir}_sp
      rm -r data/temp0 data/${datadir}_tmp
    done
  fi

  if [ $stage -le 2 ]; then
    #obtain the alignment of the perturbed data
    steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" \
      data/${trainset}_sp data/lang_nosp ${gmmdir} ${gmmdir}_ali_${trainset}_sp || exit 1
  fi
  trainset=${trainset}_sp
fi

if [ $stage -le 3 ]; then
  
  # Added by An, Lee
  echo "$0: generating phone call noise"
  sed -i '2~2 s\$\sox -t wav - -r 8k -t wav - | sox -t wav - -r 16k -t wav - | sox -t wav - -t wav - highpass 100 | sox -t wav - -t wav - lowpass 1000 | sox -t wav - -t wav - dither -s |\g' data/${trainset}/wav.scp
  sed -i '2~8 s\$\sox -t wav - -t wav - gain 16 |\g' data/${trainset}/wav.scp

  
  echo "$0: creating reverberated MFCC features"

  mfccdir=mfcc_rvb
  # Create high-resolution MFCC features (with 40 cepstra instead of 13).
  # this shows how you can split across multiple file-systems.  we'll split the
  # MFCC dir across multiple locations.  You might want to be careful here, if you
  # have multiple copies of Kaldi checked out and run the same recipe, not to let
  # them overwrite each other.
  hostInAtlas="ares hephaestus jupiter neptune"
  if [[ ! -z $(echo $hostInAtlas | grep -o $(hostname -f)) ]] && [ ! -d $mfccdir/storage ]; then
    mfcc=$(basename mfccdir) # in case was absolute pathname (unlikely), get basename.
    utils/create_split_dir.pl /mnt/{ares,hephaestus,jupiter,neptune}/$USER/kaldi-data/zeroth-kaldi-$(date +'%m_%d_%H_%M')/s5/$mfcc/storage \
      $mfccdir/storage
  fi

  if [ ! -d "RIRS_NOISES" ]; then
    # Download the package that includes the real RIRs, simulated RIRs, isotropic noises and point-source noises
    wget --no-check-certificate http://www.openslr.org/resources/28/rirs_noises.zip
    unzip rirs_noises.zip
  fi

  rvb_opts=()
  rvb_opts+=(--rir-set-parameters "0.5, RIRS_NOISES/simulated_rirs/smallroom/rir_list")
  rvb_opts+=(--rir-set-parameters "0.5, RIRS_NOISES/simulated_rirs/mediumroom/rir_list")
  rvb_opts+=(--noise-set-parameters RIRS_NOISES/pointsource_noises/noise_list)


  ### applied GridEngine for speed-up
  logdir=data/${trainset}/log
  mkdir -p $logdir
  

  utils/split_data.sh data/$trainset $nj

  $train_cmd JOB=1:$nj $logdir/reverberate.JOB.log \
      steps/data/reverberate_data_dir.py \
      "${rvb_opts[@]}" \
      --prefix "rev" \
      --foreground-snrs "30:20:15:5:0" \
      --background-snrs "30:20:15:5:0" \
      --speech-rvb-probability 1 \
      --pointsource-noise-addition-probability 1 \
      --isotropic-noise-addition-probability 1 \
      --num-replications ${num_data_reps} \
      --max-noises-per-minute 20 \
      --source-sampling-rate 16000 \
      --include-original-data true \
      data/${trainset}/split$nj/JOB data/${trainset}/split$nj/JOB_rvb${num_data_reps} \
      || exit 1

  dirs=
  for i in $(seq $nj); do
    dirs+=" data/${trainset}/split$nj/${i}_rvb${num_data_reps}"
  done
  mkdir -p data/${trainset}_rvb${num_data_reps}
  utils/combine_data.sh data/${trainset}_rvb${num_data_reps} $dirs
  ###

  utils/copy_data_dir.sh data/${trainset}_rvb${num_data_reps} data/${trainset}_rvb${num_data_reps}_hires
  utils/data/perturb_data_dir_volume.sh data/${trainset}_rvb${num_data_reps}_hires

  ###
  # commented by Lucas Jo 2017.10.31
  #
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
  ###


  for datadir in ${trainset}_rvb${num_data_reps} ; do
    steps/make_mfcc.sh --nj $nj --mfcc-config conf/mfcc_hires.conf \
      --cmd "$train_cmd" data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;
    steps/compute_cmvn_stats.sh data/${datadir}_hires exp/make_hires/$datadir $mfccdir || exit 1;
  done

  # copy the alignments for the newly created utterance ids
  ali_dirs=
  for i in `seq 0 $num_data_reps`; do
    local/multi_condition/copy_ali_dir.sh --cmd "$decode_cmd" --utt-prefix "rev${i}-" ${gmmdir}_ali_${trainset} ${gmmdir}_ali_${trainset}_temp_$i || exit 1;
    ali_dirs+=" ${gmmdir}_ali_${trainset}_temp_$i"
    cp ${gmmdir}_ali_${trainset}/phones.txt  ${gmmdir}_ali_${trainset}_temp_$i/ || exit 1;
  done
  steps/combine_ali_dirs.sh data/${trainset}_rvb${num_data_reps} ${gmmdir}_ali_${trainset}_rvb $ali_dirs || exit 1;

  # We need to build a small system just because we need the LDA+MLLT transform
  # to train the diag-UBM on top of.  We align a subset of training data for
  # this purpose.
  utils/subset_data_dir.sh data/${trainset}_rvb${num_data_reps}_hires 100000 data/train_100k_hires
  utils/subset_data_dir.sh data/${trainset}_rvb${num_data_reps}_hires 30000 data/train_30k_hires
fi


if [ $stage -le 4 ]; then
  # Train a small system just for its LDA+MLLT transform.  We use --num-iters 13
  # because after we get the transform (12th iter is the last), any further
  # training is pointless.

  mkdir exp -p exp/nnet3${rvb_affix}

  steps/train_lda_mllt.sh --cmd "$train_cmd" --num-iters 13 \
    --realign-iters "" \
    --splice-opts "--left-context=3 --right-context=3" \
    3000 10000 data/train_100k_hires data/lang_nosp \
    ${gmmdir}_ali_${trainset}_rvb exp/nnet3${rvb_affix}/tri2b
fi


if [ $stage -le 5 ]; then
  # To train a diagonal UBM we don't need very much data, so use a small subset
  # (actually, it's not that small: still around 100 hours).
  steps/online/nnet2/train_diag_ubm.sh --cmd "$train_cmd" --nj $nj --num_threads $maxThread --num-frames 700000 \
    data/train_30k_hires 512 exp/nnet3${rvb_affix}/tri2b exp/nnet3${rvb_affix}/diag_ubm
fi

if [ $stage -le 6 ]; then
  # iVector extractors can in general be sensitive to the amount of data, but
  # this one has a fairly small dim (defaults to 100) so we don't use all of it,
  # we use just the 3k subset (about one fifth of the data, or 200 hours).
  steps/online/nnet2/train_ivector_extractor.sh --cmd "$train_cmd" --nj 10 \
    data/${trainset}_rvb${num_data_reps}_hires exp/nnet3${rvb_affix}/diag_ubm exp/nnet3${rvb_affix}/extractor || exit 1;
fi

if [ $stage -le 7 ]; then
  ivectordir=exp/nnet3${rvb_affix}/ivectors_${trainset}_rvb${num_data_reps}_hires

  # We extract iVectors on all the train data, which will be what we train the
  # system on.  With --utts-per-spk-max 2, the script.  pairs the utterances
  # into twos, and treats each of these pairs as one speaker.  Note that these
  # are extracted 'online'.

  # having a larger number of speakers is helpful for generalization, and to
  # handle per-utterance decoding well (iVector starts at zero).
  utils/data/modify_speaker_info.sh --utts-per-spk-max 2 \
    data/${trainset}_rvb${num_data_reps}_hires data/${trainset}_rvb${num_data_reps}_hires_max2
  
  steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj $nj \
    data/${trainset}_rvb${num_data_reps}_hires_max2 exp/nnet3${rvb_affix}/extractor $ivectordir || exit 1;
fi


exit 0;

```

