# kusw_start.sh

> 제작: 이찬현, 김한비
>
> 설명: 서버 종료 후 서버 키기 (이후 sudo python /tmp/client.py ... 실행 필요)

```shell
#! /bin/bash
sh ./docker-kaldi-gstreamer-server/stop.sh
sh ./docker-kaldi-gstreamer-server/start.sh -y ./models/sample_english_nnet3.yaml
```

