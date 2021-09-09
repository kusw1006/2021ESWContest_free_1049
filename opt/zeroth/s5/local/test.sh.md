# test.sh

> 경로: /opt/zeroth/s5/local
>
> 작성자: 김한비



> online2-nnet3-tcp-faster.cc에서 rescore을 하기위해 실행하는 sh파일
>
> online2-nnet3-wav-faster.cc의 rescore 부분을 참고하여 제작

```sh
#!/bin/bash
# for kaldi nnet3 decoding process check
# 
# Copyright  2017  Atlas Guide (Author : Lucas Jo)
# 
# Apache 2.0
#
#
. /opt/zeroth/s5/cmd.sh
. /opt/zeroth/s5/path.sh


dir=/home/dcl2003/esw2021/src
lat=$1

if [ ! -d $dir ]; then
    mkdir -p $dir
fi

LMWT=11.0
wip=0.0
rescore=true
if $rescore ; then
	echo "##### LM rescore ####"
	
	oldlm=/home/dcl2003/esw2021/test/models/korean/zeroth/G.fst
	newlm=/home/dcl2003/esw2021/test/models/korean/zeroth/G.carpa
	oldlmcommand="fstproject --project_output=true $oldlm |"

	symtab=/home/dcl2003/esw2021/test/models/korean/zeroth/words.txt
	lattice-lmrescore --lm-scale=-1.0 \
		"ark:gunzip -c $dir/lat.1.gz|" "$oldlmcommand" ark:- |\
		lattice-lmrescore-const-arpa --lm-scale=1.0 ark:- "$newlm" ark:- |\
		#lattice-scale --inv-acoustic-scale=$LMWT ark:- ark:- |\
		lattice-add-penalty --word-ins-penalty=$wip ark:- ark:- |\
		lattice-1best ark:- "ark:|gzip -c > $dir/lmre_lat.1.gz"

	# below is to show best-path decoding result in text
	echo $(lattice-copy "ark:gunzip -c $dir/lmre_lat.1.gz|" ark:- |\
		lattice-best-path --word-symbol-table=$symtab ark:- ark,t:-)
fi

```

