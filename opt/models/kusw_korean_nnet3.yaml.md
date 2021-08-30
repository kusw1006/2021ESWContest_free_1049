# kusw_korean_nnet3.yaml

> 경로: /opt/models/
>
> 작성자: 김한비



> kaldi nnet3 sample을 참고하여 수치조정 + nnet-mode : 3 추가
>
> model~ivector-extraction-config 경로 수정(학습으로 만들어진 모델 경로)
>
> rescoring 사용 및 정확도 향상을 위해 additional function 주석 해제

```yaml
# You have to download TEDLIUM "online nnet2" models in order to use this sample
# Run download-tedlium-nnet2.sh in '/opt/models' to download them.
use-nnet2: True
decoder:
    # All the properties nested here correspond to the kaldinnet2onlinedecoder GStreamer plugin properties.
    # Use gst-inspect-1.0 ./libgstkaldionline2.so kaldinnet2onlinedecoder to discover the available properties
    nnet-mode : 3
    use-threaded-decoder:  true
    model : /home/dcl2003/esw2021/test/models/korean/zeroth/final.mdl
    word-syms : /home/dcl2003/esw2021/test/models/korean/zeroth/words.txt
    fst : /home/dcl2003/esw2021/test/models/korean/zeroth/HCLG.fst
    mfcc-config : /home/dcl2003/esw2021/test/models/korean/zeroth/conf/mfcc.conf
    ivector-extraction-config : /home/dcl2003/esw2021/test/models/korean/zeroth/conf/ivector_extractor.conf
    max-active: 7000
    beam: 15.0
    lattice-beam: 6.0
    acoustic-scale: 1.0
    do-endpointing : true
    endpoint-silence-phones : "1:2:3:4:5:6:7:8:9:10:11:12:13:14:15"
    traceback-period-in-secs: 0.25
    chunk-length-in-secs: 0.25
    num-nbest: 3

    #Additional functionality that you can play with:
    lm-fst:  /home/dcl2003/esw2021/test/models/korean/zeroth/G.fst
    big-lm-const-arpa: /home/dcl2003/esw2021/test/models/korean/zeroth/G.carpa
    phone-syms: /home/dcl2003/esw2021/test/models/korean/zeroth/phones.txt
    word-boundary-file: /home/dcl2003/esw2021/test/models/korean/zeroth/word_boundary.int
    #do-phone-alignment: true
out-dir: tmp

use-vad: False
silence-timeout: 10

# Just a sample post-processor that appends "." to the hypothesis
post-processor: perl -npe 'BEGIN {use IO::Handle; STDOUT->autoflush(1);} sleep(1); s/(.*)/\1./;'

#post-processor: (while read LINE; do echo $LINE; done)

# A sample full post processor that add a confidence score to 1-best hyp and deletes other n-best hyps
#full-post-processor: ./sample_full_post_processor.py

logging:
    version : 1
    disable_existing_loggers: False
    formatters:
        simpleFormater:
            format: '%(asctime)s - %(levelname)7s: %(name)10s: %(message)s'
            datefmt: '%Y-%m-%d %H:%M:%S'
    handlers:
        console:
            class: logging.StreamHandler
            formatter: simpleFormater
            level: DEBUG
    root:
        level: DEBUG
        handlers: [console]

```

