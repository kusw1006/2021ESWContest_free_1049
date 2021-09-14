# run_tdnn_1n.sh

> 코드 일부 수정 및 MODE 추가

```shell
#!/bin/bash

set -e -o pipefail

# First the options that are passed through to run_ivector_common.sh
# (some of which are also used in this script directly).
stage=0
nj=16
train_set=train_clean
num_data_reps=3        # number of reverberated copies of data to generate
speed_perturb=true
test_sets="test_200"
gmm=tri4b        # this is the source gmm-dir that we'll use for alignments; it
                 # should have alignments for the specified training data.
nnet3_affix=_rvb       # affix for exp dirs, e.g. it was _cleaned in tedlium.
mode=AM

# Options which are not passed through to run_ivector_common.sh
affix=1n_rvb  #affix for TDNN directory e.g. "1a" or "1b", in case we change the configuration.
common_egs_dir=

# LSTM/chain options
train_stage=-10
xent_regularize=0.1
max_param_change=2.0

# training chunk-options
get_egs_stage=-10
chunk_width=150,110,100

# training options
num_jobs_initial=1
num_jobs_final=2
num_epochs=4
minibatch_size=128
initial_effective_lrate=0.0015
final_effective_lrate=0.0002
remove_egs=true


#decode options
test_online_decoding=true  # if true, it will run the last decoding stage.

# End configuration section.
echo "$0 $@"  # Print the command line for logging


. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

trainTime=$(date +'%F-%H-%M')
echo "multi condition AM trained at" $trainTime

local/nnet3/multi_condition/run_ivector_common.sh --stage $stage  \
                                 --speed-perturb ${speed_perturb} \
                                 --num-data-reps ${num_data_reps} \
                                 --rvb-affix ${nnet3_affix}

if ! cuda-compiled; then
  cat <<EOF && exit 1
This script is intended to be used with GPUs but you have not compiled Kaldi with CUDA
If you want to use GPUs (and have them), go to src/, and configure and make on a machine
where "nvcc" is installed.
EOF
fi

if [ "$speed_perturb" == "true" ]; then
  train_set=${train_set}_sp
fi

gmm_dir=exp/${gmm}
clean_lat_dir=exp/${gmm}_${train_set}_lats
lat_dir=${clean_lat_dir}_rvb${num_data_reps}
dir=exp/chain_rvb/tdnn${affix}
train_data_dir=data/${train_set}_rvb${num_data_reps}_hires
train_ivector_dir=exp/nnet3_rvb/ivectors_${train_set}_rvb${num_data_reps}_hires
lores_train_data_dir=data/${train_set}

# note: you don't necessarily have to change the treedir name
# each time you do a new experiment-- only if you change the
# configuration in a way that affects the tree.
tree_dir=exp/chain_rvb/tree_a
# the 'lang' directory is created by this script.
# If you create such a directory with a non-standard topology
# you should probably name it differently.
lang=data/lang_chain

if [ -d exp/${gmm}_ali_${train_set} ]; then 
    ali_dir=exp/${gmm}_ali_${train_set}
else
    echo "$0: Using Alignment from GMM dir at ${gmm}..."
    ali_dir=${gmm_dir}
fi


for f in $train_data_dir/feats.scp $train_ivector_dir/ivector_online.scp \
    $lores_train_data_dir/feats.scp $gmm_dir/final.mdl \
    $ali_dir/ali.1.gz $gmm_dir/final.mdl; do
  [ ! -f $f ] && echo "$0: expected file $f to exist" && exit 1
done


if [ $stage -le 8 ]; then
  echo "$0: creating lang directory $lang with chain-type topology"
  # Create a version of the lang/ directory that has one state per phone in the
  # topo file. [note, it really has two states.. the first one is only repeated
  # once, the second one has zero or more repeats.]
  if [ -d $lang ]; then
    if [ $lang/L.fst -nt data/lang/L.fst ]; then
      echo "$0: $lang already exists, not overwriting it; continuing"
    else
      echo "$0: $lang already exists and seems to be older than data/lang..."
      echo " ... not sure what to do.  Exiting."
      exit 1;
    fi
  else
    cp -r data/lang $lang
    silphonelist=$(cat $lang/phones/silence.csl) || exit 1;
    nonsilphonelist=$(cat $lang/phones/nonsilence.csl) || exit 1;
    # Use our special topology... note that later on may have to tune this
    # topology.
    steps/nnet3/chain/gen_topo.py $nonsilphonelist $silphonelist > $lang/topo
  fi
fi

if [ $stage -le 9 ]; then
  # Get the alignments as lattices (gives the chain training more freedom).
  # use the same num-jobs as the alignments
  steps/align_fmllr_lats.sh --nj $nj --cmd "$train_cmd" ${lores_train_data_dir} \
    data/lang $gmm_dir $clean_lat_dir
  rm $clean_lat_dir/fsts.*.gz # save space
  # Create the lattices for the reverberated data

  # We use the lattices/alignments from the clean data for the reverberated data.
  mkdir -p $lat_dir/temp/
  lattice-copy "ark:gunzip -c $clean_lat_dir/lat.*.gz |" ark,scp:$lat_dir/temp/lats.ark,$lat_dir/temp/lats.scp

  # copy the lattices for the reverberated data
  rm -f $lat_dir/temp/combined_lats.scp
  touch $lat_dir/temp/combined_lats.scp
  # Here prefix "rev0-" represents the clean set, "rev1-" represents the reverberated set
  for i in `seq 0 $num_data_reps`; do
    cat $lat_dir/temp/lats.scp | sed -e "s/^/rev${i}-/" >> $lat_dir/temp/combined_lats.scp
  done
  sort -u $lat_dir/temp/combined_lats.scp > $lat_dir/temp/combined_lats_sorted.scp

  num_jobs=10
  split_scps=""
  for n in `seq $num_jobs`; do
      split_scps="$split_scps $lat_dir/temp/combined_lats_sorted.$n.scp"
  done
  utils/split_scp.pl $lat_dir/temp/combined_lats_sorted.scp $split_scps
  
  $train_cmd JOB=1:$num_jobs $lat_dir/temp/split_scp_copy.JOB.log \
      lattice-copy scp:$lat_dir/temp/combined_lats_sorted.JOB.scp "ark:|gzip -c >$lat_dir/lat.JOB.gz" \
      || exit 1;
  echo $num_jobs > $lat_dir/num_jobs

  #lattice-copy scp:$lat_dir/temp/combined_lats_sorted.scp "ark:|gzip -c >$lat_dir/lat.1.gz" || exit 1;
  #echo "1" > $lat_dir/num_jobs

  # copy other files from original lattice dir
  for f in cmvn_opts final.mdl splice_opts tree; do
    cp $clean_lat_dir/$f $lat_dir/$f
  done

fi

if [ $stage -le 10 ]; then
  # Build a tree using our new topology.  
   if [ -f $tree_dir/final.mdl ]; then
     echo "$0: $tree_dir/final.mdl already exists, refusing to overwrite it."
     exit 1;
  fi
  steps/nnet3/chain/build_tree.sh \
    --frame-subsampling-factor 3 \
    --context-opts "--context-width=2 --central-position=1" \
    --cmd "$train_cmd" 3500 ${lores_train_data_dir} \
    $lang $ali_dir $tree_dir
fi

if [ $stage -le 11 ]; then
  mkdir -p $dir
  echo "$0: creating neural net configs using the xconfig parser";
  num_targets=$(tree-info $tree_dir/tree |grep num-pdfs|awk '{print $2}')
  learning_rate_factor=$(echo "print 0.5/$xent_regularize" | python)
  opts="l2-regularize=0.002"
  linear_opts="orthonormal-constraint=1.0"
  output_opts="l2-regularize=0.0005 bottleneck-dim=256"

  mkdir -p $dir/configs

  cat <<EOF > $dir/configs/network.xconfig
  input dim=100 name=ivector
  input dim=40 name=input

  # please note that it is important to have input layer with the name=input
  # as the layer immediately preceding the fixed-affine-layer to enable
  # the use of short notation for the descriptor
  fixed-affine-layer name=lda input=Append(-1,0,1,ReplaceIndex(ivector, t, 0)) affine-transform-file=$dir/configs/lda.mat

  # the first splicing is moved before the lda layer, so no splicing here
  relu-batchnorm-layer name=tdnn1 $opts dim=1280
  linear-component name=tdnn2l dim=256 $linear_opts input=Append(-1,0)
  relu-batchnorm-layer name=tdnn2 $opts input=Append(0,1) dim=1280
  linear-component name=tdnn3l dim=256 $linear_opts
  relu-batchnorm-layer name=tdnn3 $opts dim=1280
  linear-component name=tdnn4l dim=256 $linear_opts input=Append(-1,0)
  relu-batchnorm-layer name=tdnn4 $opts input=Append(0,1) dim=1280
  linear-component name=tdnn5l dim=256 $linear_opts
  relu-batchnorm-layer name=tdnn5 $opts dim=1280 input=Append(tdnn5l, tdnn3l)
  linear-component name=tdnn6l dim=256 $linear_opts input=Append(-3,0)
  relu-batchnorm-layer name=tdnn6 $opts input=Append(0,3) dim=1280
  linear-component name=tdnn7l dim=256 $linear_opts input=Append(-3,0)
  relu-batchnorm-layer name=tdnn7 $opts input=Append(0,3,tdnn6l,tdnn4l,tdnn2l) dim=1280
  linear-component name=tdnn8l dim=256 $linear_opts input=Append(-3,0)
  relu-batchnorm-layer name=tdnn8 $opts input=Append(0,3) dim=1280
  linear-component name=tdnn9l dim=256 $linear_opts input=Append(-3,0)
  relu-batchnorm-layer name=tdnn9 $opts input=Append(0,3,tdnn8l,tdnn6l,tdnn4l) dim=1280
  linear-component name=tdnn10l dim=256 $linear_opts input=Append(-3,0)
  relu-batchnorm-layer name=tdnn10 $opts input=Append(0,3) dim=1280
  linear-component name=tdnn11l dim=256 $linear_opts input=Append(-3,0)
  relu-batchnorm-layer name=tdnn11 $opts input=Append(0,3,tdnn10l,tdnn8l,tdnn6l) dim=1280
  linear-component name=prefinal-l dim=256 $linear_opts

  relu-batchnorm-layer name=prefinal-chain input=prefinal-l $opts dim=1280
  output-layer name=output include-log-softmax=false dim=$num_targets $output_opts

  relu-batchnorm-layer name=prefinal-xent input=prefinal-l $opts dim=1280
  output-layer name=output-xent dim=$num_targets learning-rate-factor=$learning_rate_factor $output_opts
EOF
  steps/nnet3/xconfig_to_configs.py --xconfig-file $dir/configs/network.xconfig --config-dir $dir/configs/
fi

if [ $stage -le 12 ]; then
  hostInAtlas="ares hephaestus jupiter neptune"
  if [[ ! -z $(echo $hostInAtlas | grep -o $(hostname -f)) ]] && [ ! -d $dir/egs/storage ]; then
    utils/create_split_dir.pl /mnt/{ares,hephaestus,jupiter,neptune}/$USER/kaldi-data/zeroth-kaldi/s5/$dir/egs/storage \
      $dir/egs/storage
  fi

  steps/nnet3/chain/train.py --stage $train_stage \
    --cmd "$decode_cmd" \
    --feat.online-ivector-dir=$train_ivector_dir \
    --feat.cmvn-opts "--norm-means=false --norm-vars=false" \
    --chain.xent-regularize $xent_regularize \
    --chain.leaky-hmm-coefficient 0.1 \
    --chain.l2-regularize 0.0 \
    --chain.apply-deriv-weights false \
    --chain.lm-opts="--num-extra-lm-states=2000" \
    --trainer.max-param-change $max_param_change \
    --trainer.num-epochs $num_epochs \
    --trainer.frames-per-iter 1500000 \
    --trainer.optimization.num-jobs-initial $num_jobs_initial \
    --trainer.optimization.num-jobs-final $num_jobs_final \
    --trainer.optimization.initial-effective-lrate $initial_effective_lrate \
    --trainer.optimization.final-effective-lrate $final_effective_lrate \
    --trainer.num-chunk-per-minibatch $minibatch_size \
    --egs.stage $get_egs_stage \
    --egs.chunk-width $chunk_width \
    --egs.dir "$common_egs_dir" \
    --egs.opts "--frames-overlap-per-eg 0" \
    --cleanup.remove-egs $remove_egs \
    --use-gpu true \
    --feat-dir $train_data_dir \
    --tree-dir $tree_dir \
    --lat-dir $lat_dir \
    --dir $dir  || exit 1;
fi

if [ ! $MODE="AM" ]; then
    if [ $stage -le 13 ]; then
      # The reason we are using data/lang here, instead of $lang, is just to
      # emphasize that it's not actually important to give mkgraph.sh the
      # lang directory with the matched topology (since it gets the
      # topology file from the model).  So you could give it a different
      # lang directory, one that contained a wordlist and LM of your choice,
      # as long as phones.txt was compatible.

      utils/lang/check_phones_compatible.sh \
        data/lang_test_tgmed/phones.txt $lang/phones.txt
      utils/mkgraph.sh \
        --self-loop-scale 1.0 data/lang_test_tgmed \
        $tree_dir $tree_dir/graph_tgmed || exit 1;
    fi

    if $test_online_decoding && [ $stage -le 14 ]; then
      # note: if the features change (e.g. you add pitch features), you will have to
      # change the options of the following command line.
      steps/online/nnet3/prepare_online_decoding.sh \
        --mfcc-config conf/mfcc_hires.conf \
        $lang exp/nnet3_rvb/extractor ${dir} ${dir}_online

      rm $dir/.error 2>/dev/null || true

      for data in $test_sets; do
        (
          data_affix=$(echo $data | sed s/test_//)
          nspk=$(wc -l <data/${data}/spk2utt)
          # note: we just give it "data/${data}" as it only uses the wav.scp, the
          # feature type does not matter.
          for lmtype in tgmed; do
            steps/online/nnet3/decode.sh \
              --acwt 1.0 --post-decode-acwt 10.0 \
              --nj $nspk --cmd "$decode_cmd" \
              $tree_dir/graph_${lmtype} data/${data} ${dir}_online/decode_${lmtype}_test_${data_affix} || exit 1
          done
          steps/lmrescore_const_arpa.sh --cmd "$decode_cmd" \
            data/lang_test_{tgmed,fglarge} \
           data/${data} ${dir}_online/decode_{${lmtype},fglarge}_test_${data_affix} || exit 1
        ) || touch $dir/.error &
      done
      wait
      [ -f $dir/.error ] && echo "$0: there was a problem while decoding" && exit 1
    fi
fi

trainTimeF=$(date +'%F-%H-%M')
echo "multi condition AM trained finish at" $trainTimeF

exit 0;

```

