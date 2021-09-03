# download_from_openslr.sh

> 작성자: 이찬현

> 2.5 단계를 통해 다운, 업샘플링 과정 추가

```shell
#!/bin/bash

# Copyright 2018 Lucas Jo (Atlas Guide)
# Apache 2.0
if [ $# -ne 1 ]; then
  echo "$0 usage: $0 <tar-dir>"
  exit 1
fi
tar_dir=$1

if [ ! -f zeroth_korean.tar.gz ]; then
	echo "1. Download opensource data from openslr"
	wget http://www.openslr.org/resources/40/zeroth_korean.tar.gz
else
	echo " zeroth_korean.tar.gz already exist"
fi

if [ ! -d $tar_dir ]; then
	echo "2. Untar data"
	mkdir -p $tar_dir
	tar -zxvf zeroth_korean.tar.gz -C $tar_dir
	
	echo "2.5. Down & Up sampling data"
	find -L $tar_dir -iname "*.flac" | awk -F . '{print "."$2}' | xargs -I{} sox -t flac {}.flac -r 8k -t flac {}.tflac
	find -L $tar_dir -iname "*.tflac" | awk -F . '{print "."$2}' | xargs -I{} sox -t flac {}.tflac -r 16k -t flac {}.flac
	find -L $tar_dir -iname "*.tflac" | xargs -I{} rm {}


	
	# files=$(find -L $tar_dir -iname "*.flac")
	# for file in $files; do
    # 	sox -t flac $file -r 8k -t flac - | sox -t flac - -r 16k -t flac $file
	# done


	echo "3. put LM fils into data/local/lm"
	mv speechDATA/zeroth* data/local/lm
fi

exit 0

```

