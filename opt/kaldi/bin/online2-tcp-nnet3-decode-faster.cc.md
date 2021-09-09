# online2-tcp-nnet3-decode-faster.cc

> 경로: /opt/kaldi/src/online2bin/
>
> 작성자: 김한비
> 코드제작: 이찬현, 김한비

<br>

> tcp 서버를 이용한 디코딩(multi-threading을 통해 resocre기능 추가)

<br>

## 변경사항

<br>

```c++
#include <fcntl.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include <resolv.h>
#include <pthread.h>

//------------Add------------//
#define MAX_SEN 100

std::string* rescoreStr[MAX_SEN];
char flag[MAX_SEN] = {0, };
int id = 0;

typedef struct _threadPack{
  int id;
  fst::SymbolTable* _word_syms;
}threadPack;
//---------------------------//
```

multi-threading을 위한 헤더 파일 추가 

외부 함수에서 rescore된 문장을 main문으로 가져가기 위해 rescoreStr을 전역변수로 선언

flag는 각 문장마다 rescore 됐는지 확인하는 용도(client 화면에 출력하고 다시 0으로 바뀜)

id는 문장마다 rescore을 하기위한 식별자

pthread로 실행시킬 함수에 인자를 하나밖에 전달하지 못하기 때문에 넘겨줘야하는 인자들을 구조체로 선언

(_word\_syms는 thread 함수(rescoring)에서 FInd 기능을 쓰기 위해)

<br>

```c++
//------------Add------------//
char *rescoreBuf[MAX_SEN];

void* rescoring(void* _Package) {
  int rescoreId;
  
  threadPack* rescorePack = (threadPack *)_Package;
  rescoreId = rescorePack->id;
  fst::SymbolTable word_syms = *(fst::SymbolTable *) rescorePack->_word_syms;

  // kaldi::CompactLattice* lat2 = (kaldi::CompactLattice*)lat1;
  // kaldi::CompactLattice lat3 = *lat2;
  // FILE* stream=popen("/opt/zeroth/s5/local/kusw_resore.sh --option","r"); //s5에서 할까?
  // char rescoreBuf[1280] = {0, };

  rescoreBuf[rescoreId] = (char*)calloc(1280, sizeof(char));
  rescoreStr[rescoreId] = new std::string();


  FILE* stream=popen("/opt/zeroth/s5/local/test.sh | grep 000","r");
  fgets(rescoreBuf[rescoreId], 1280, stream);
  
  
  int num[250];
  char tok[] = " ";
  char *token;
  token = strtok(rescoreBuf[rescoreId], tok);
  int i;

  for(i = 0; token = strtok(NULL, tok); i++){
    num[i]=atoi(token);
  }

  std::vector<int32> words(num, num + i);

  rescoreStr[rescoreId]->append("\t\t\t\t\t\t\t\t");
  rescoreStr[rescoreId]->append(std::to_string(rescoreId));
  rescoreStr[rescoreId]->append(": ");
  for (int j = 0; j < i; j++) {
    std::string s = word_syms.Find(words[j]);
    if (s.empty()) {
      KALDI_WARN << "Word-id " << words[j] << " not in symbol table.";
      // msg << "<#" << std::to_string(j) << "> ";
    } else {
      // msg << s << " ";
      // KALDI_LOG << s;
      rescoreStr[rescoreId]->append(s);
      rescoreStr[rescoreId]->append(" ");
      //msg << s;
    }
  }
  KALDI_LOG << *rescoreStr[rescoreId] << "##";

  free(rescoreBuf[rescoreId]);
  flag[rescoreId] = 1;

  return 0;
}
//---------------------------//
```

<br>

rescore된 문장을 임시 저장하기 위한 rescoreBuf 선언

void* rescoring(void* _Package) = pthread에서 실행시키는 함수(병렬적으로 동작하는)

호출될 때 threadPack* 형식을 void*로 형변환된 채로 받음 -> 다시 threadPack\*으로 typecasting

id와 _word_syms를 각각 rescoreId, word_syms로 받아옴

<br>

/opt/zeroth/s5/local/test.sh 파일을 실행시켜 출력결과 중 000이 들어간 문장만 받아서 rescoreBuf에 저장

이 때 rescoreBuf에는 rescore된 문장이 아니라 각 단어들의 라벨이 들어가있음

띄어쓰기 기준으로 끊어서 라벨에 해당하는 단어를 찾아 s에 넣어줌

s가 비어있지 않다면(symbol table에서 단어를 찾았다면) rescoreStr에 append해줌

동적할당 free해주고 해당 id의 flag를 1로 바꿔줌 -> main에서 출력할 수 있게

<br>

rescoreBuf = 라벨 형태(000 1012 30 2203 44213)

rescoreStr = 문장 단어 형태(000 나 는 오늘 집)

<br>

```c++
	//-------------Add-----------//
    threadPack Package;
    //---------------------------//
 	if (po.NumArgs() != 4) {
      po.PrintUsage();
      return 1;
    }

    //-------------Add-----------//
    std::string clat_wspecifier;
    
    std::string nnet3_rxfilename = po.GetArg(1),
        fst_rxfilename = po.GetArg(2),
        word_syms_filename = po.GetArg(3);
        clat_wspecifier = po.GetArg(4);
    
    // for multithreading
    pthread_t thread_id[MAX_SEN];
    //---------------------------//
```

<br>

기존 입력에 wspecifier를 추가하기 위해 po.NumArgs() 값 수정,

clat_wspecifier = po.GetArg(4)

thread_id = pthread 식별자

<br>

```c++
            //-------------Add-----------//
            CompactLatticeWriter clat_writer(clat_wspecifier);
            clat_writer.Write("000", lat);
            //---------------------------//

			// 사이에 다른 코드 있음 //

            //-------------Add-----------//
            if (msg.length()!=0)
            {

              Package.id = id;
              Package._word_syms = word_syms;
              
              
              //pthread_create(&thread_id[id], NULL, rescoring, (void *)word_syms);
              pthread_create(&thread_id[id], NULL, rescoring, (void *)&Package);
              pthread_detach(thread_id[id]);
              KALDI_LOG<<"@@@@@@@@@@@@@@@@@"<< id <<"@@@@@@@@@@@@@@@@@";
              
              
              //CompactLattice *latt = &lat;
              
              
              // int status;
              // status = pthread_kill(thread_id[0],0);
              // if ( status == ESRCH ) // 존재하지 않는 쓰레드 아이디일때, 다시 살리면 된다.
              // {   
              // }
              // else if ( status == EINVAL ) // 잘못된 시그널을 전달했을 경우.
              // { 
              // } 
              // else // 현재 쓰레드는 생존해 있다.
              // {
              //   pthread_create(&thread_id[1], NULL, rescoring2, (void *)word_syms);
              //   pthread_detach(thread_id[1]);
              // } 9.9 700 139 1800 700 8300 8900 89Gb

              for(int idx=0; idx<MAX_SEN; idx++) {
                if(flag[idx]==1) {
                  server.WriteLn("\n");
                  server.WriteLn(*rescoreStr[idx]);
                  server.WriteLn("\n");

                  flag[idx]=0;
                  delete rescoreStr[idx];
                }
              }


              server.WriteLn((std::to_string(id) + ": " + msg));

              id = (id + 1) % 100;
            }
            //---------------------------//
```

clat_writer 선언(clat_wspecifier에 clat 적어줌) 000은 utt값 임의로 지정

msg.length()!=0  -> 아무 소리도 전달받지 않을경우 thread낭비를 방지하고자

<br>

pthread_create(&thread식별자, thread 속성, 실행시킬 함수, 전달시킬 인자): pthread 생성, 함수 실행

pthread_detach(thread식별자): pthread 분리(종료에 대한 종속성 x)

<br>

flag가 1인(rescore 된) 인덱스를 찾아서 해당 문장 server.WriteLn

출력후 flag는 0으로 변경, rescoreStr delete

<br>

rescore 문장 말고 raw문장 출력(인터페이스를 위해 순서를 이처럼 정함)

100문장 이상 말했을 때를 대비해 id는 100으로 나눈 나머지로 지정, id++

<br>

<br>

## 지나온 error...

1. client에게서도 실시간으로 음성을 받아와야하고, 이에 대한 rescoring도 실시간으로 처리되어야함.
   -> multi-threading을 이용해 병렬적으로 처리하자

2. Endpoint, sending message라는 로그가 뜰 때마다 완성된 문장이 뜨는 것을 확인하여 이 때 msg를 받아와서 rescoring을 해야겠다 생각함

3. 처음에는 rescore를 위한 thread를 하나만 만들었음.
   pthread_create(&thread[id], NULL, rescoring, NULL);

4. main위에서 rescoring 함수를 선언하고 main문 아래에서 구현함 -> 참조할 수 없는 어쩌구..

   -> main문 위에서 전부 구현함

5. rescoring함수에서 sh파일을 불러올 수 있다면? 
   online2-nnet3-wav-faster.cc에서 사용한 sh파일을 이용해 rescore을 진행할 수 있을 것임 -> popen 이용

6. FILE* stream = popen("/opt/zeroth/s5/local/test.sh"); -> sh파일 실행 결과가 stream에 저장됨

7. sh파일에 인자를 넣어줄 수 있을까.. 되긴 됨. 
   그래서 처음에는 인자를 전달해주려 했으나 wav의 rescoring을 분석한 결과 utt,clat가 쓰여진 
   [사용자지정경로]/wspecifier를 이용하여 rescoring을 진행함을 알게됨.
   그러면 tcp의 utt, clat도 wspecifier에 저장시키고 그걸 sh에서 직접 불러서 rescoring하자

   -> 000,clat를 write한 wspecifier 생성

8. fgets(rescoreBuf[id],1280,stream);을 통해 rescoreBuf에 rescore결과를 저장함

   -> rescoring함수 내에서 server.WriteLn(rescoreBuf[id]); 실행

   -> server가 이 scope 내에서 선언되지 않았다 하면서 안됨..

9. server를 rescoring 함수 인자로 받아서 실행시킴 -> 계속 종료됨. 차라리 결과를 main으로 보내서 write하자

10. rescoreBuf를 밖에 선언하고 main문에서 받아서 출력시킴 -> 결과가 라벨이었음

11. symbol table에서 라벨에 해당하는 단어를 찾아야함 -> Find 함수 이용했으나 마찬가지로 scope 문제 발생
    -> symbol table 인자로 받아와서 Find함수 이용하여 resocreStr 생성

12. main 문에서 rescoreStr를 server.writeLn 시킴 -> 1차 성공

13. 그러나 첫 문장이 rescore되는 중에 다음 문장이 들어가면 두 문장이 모두 rescoring될 때까지 출력되지 않음

    -> 이전 문장이 rescore 완료되지 않았을 경우에 대비해 thread를 여러개 만들자

14. thread_id[1]을 추가로 만들고 thread_id[0]이 사용중이면 thread[1]에 가게 설정

    -> 그냥 rescore이 두 번 되는 꼴이 됨

15. 차라리 매 문장마다 새로운 thread에 넣자
    MAX_SEN을 100으로 정하고 thread_id[MAX_SEN] : 100개의 thread가 만들어질 수 있음

    id=0부터 시작해서 문장을 받을 때마다 +1시키면서 각자 id에 맞는 thread와 rescoreBuf, rescoreStr를 사용

16. rescoreBuf와 rescoreStr는 각각 자료형에 맞는 형태로 동적할당하고, 사용완료되면 해제시킴

17. 첫문장 까지는 괜찮으나 다음 문장이 들어가면 서버가 강제 종료됨 -> id문제라고 추측

    현재 id는 전역변수로 설정이 되어있고 문장이 들어갈 때마다 1씩 증가함
    즉, rescoring함수내에서 코드가 차례로 실행되다가 중간에 id가 증가할 때 문제가 발생

19. 그렇다면 id도 함께 인자로 넣어주자. -> 구조체로 id와 symbol table 전달

20. 구조체에서 받아온 id와 symbol table을 다른 변수에 저장해놓고 쓰면 중간에 바뀔 걱정 없음

21. 이제 강제 종료되지는 않으나 출력이 이상함
      flag를 공유하고 있었음 -> 어느 문장이 rescore되어 flag가 1이 되었는지 알 수 없음

22. flag[id]로 id마다 각자의 flag를 설정할 수 있게 함

   \+이전 문장들이 뒤늦게 rescore될 경우를 생각하여 현재 id까지 flag를 모두 검사하여 출력하게 함

23. 100문장이 넘어갈 때에 대비해 id를 100으로 나눈 나머지로 설정(이전에 사라진 거 다시 쓸수있게)

24. 20번 처럼 flag를 검사할 경우 101번째 문장이 들어갔을 때 99번째 문장이 rescore된다면 발견되지 않음

   -> for문을 MAX_SEN 전체를 도는 것으로 수정

<br>

※ 과제: 마지막 문장의 rescore이 출력 되지 않음

<br>

## 코드 전문

```c++
// online2bin/online2-tcp-nnet3-decode-faster.cc

// Copyright 2014  Johns Hopkins University (author: Daniel Povey)
//           2016  Api.ai (Author: Ilya Platonov)
//           2018  Polish-Japanese Academy of Information Technology (Author: Danijel Korzinek)

// See ../../COPYING for clarification regarding multiple authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
// WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
// MERCHANTABLITY OR NON-INFRINGEMENT.
// See the Apache 2 License for the specific language governing permissions and
// limitations under the License.

#include "feat/wave-reader.h"
#include "online2/online-nnet3-decoding.h"
#include "online2/online-nnet2-feature-pipeline.h"
#include "online2/onlinebin-util.h"
#include "online2/online-timing.h"
#include "online2/online-endpoint.h"
#include "fstext/fstext-lib.h"
#include "lat/lattice-functions.h"
#include "util/kaldi-thread.h"
#include "nnet3/nnet-utils.h"

#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <poll.h>
#include <signal.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string>

#include <fcntl.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include <resolv.h>
#include <pthread.h>

//------------Add------------//
#define MAX_SEN 100

std::string* rescoreStr[MAX_SEN];
char flag[MAX_SEN] = {0, };
int id = 0;

typedef struct _threadPack{
  int id;
  fst::SymbolTable* _word_syms;
}threadPack;
//---------------------------//


namespace kaldi {

class TcpServer {
 public:
  explicit TcpServer(int read_timeout);
  ~TcpServer();

  bool Listen(int32 port);  // start listening on a given port
  int32 Accept();  // accept a client and return its descriptor

  bool ReadChunk(size_t len); // get more data and return false if end-of-stream

  Vector<BaseFloat> GetChunk(); // get the data read by above method

  bool Write(const std::string &msg); // write to accepted client
  bool WriteLn(const std::string &msg, const std::string &eol = "\n"); // write line to accepted client

  void Disconnect();
  

 private:
  struct ::sockaddr_in h_addr_;
  int32 server_desc_, client_desc_;
  int16 *samp_buf_;
  size_t buf_len_, has_read_;
  pollfd client_set_[1];
  int read_timeout_;
};


std::string LatticeToString(const Lattice &lat, const fst::SymbolTable &word_syms) {
  LatticeWeight weight;
  std::vector<int32> alignment;
  std::vector<int32> words;
  GetLinearSymbolSequence(lat, &alignment, &words, &weight);

  std::ostringstream msg;
  for (size_t i = 0; i < words.size(); i++) {
    std::string s = word_syms.Find(words[i]);
    if (s.empty()) {
      KALDI_WARN << "Word-id " << words[i] << " not in symbol table.";
      msg << "<#" << std::to_string(i) << "> ";
    } else
      msg << s << " ";
      //msg << s;
  }
  return msg.str();
}

std::string GetTimeString(int32 t_beg, int32 t_end, BaseFloat time_unit) {
  char buffer[100];
  double t_beg2 = t_beg * time_unit;
  double t_end2 = t_end * time_unit;
  snprintf(buffer, 100, "%.2f %.2f", t_beg2, t_end2);
  return std::string(buffer);
}

int32 GetLatticeTimeSpan(const Lattice& lat) {
  std::vector<int32> times;
  LatticeStateTimes(lat, &times);
  return times.back();
}

std::string LatticeToString(const CompactLattice &clat, const fst::SymbolTable &word_syms) {
  if (clat.NumStates() == 0) {
    KALDI_WARN << "Empty lattice.";
    return "";
  }
  CompactLattice best_path_clat;
  CompactLatticeShortestPath(clat, &best_path_clat);

  Lattice best_path_lat;
  ConvertLattice(best_path_clat, &best_path_lat);
  return LatticeToString(best_path_lat, word_syms);
}
}

//------------Add------------//
char *rescoreBuf[MAX_SEN];

void* rescoring(void* _Package) {
  int rescoreId;
  
  threadPack* rescorePack = (threadPack *)_Package;
  rescoreId = rescorePack->id;
  fst::SymbolTable word_syms = *(fst::SymbolTable *) rescorePack->_word_syms;

  // kaldi::CompactLattice* lat2 = (kaldi::CompactLattice*)lat1;
  // kaldi::CompactLattice lat3 = *lat2;
  // FILE* stream=popen("/opt/zeroth/s5/local/kusw_resore.sh --option","r"); //s5에서 할까?
  // char rescoreBuf[1280] = {0, };

  rescoreBuf[rescoreId] = (char*)calloc(1280, sizeof(char));
  rescoreStr[rescoreId] = new std::string();


  FILE* stream=popen("/opt/zeroth/s5/local/test.sh | grep 000","r");
  fgets(rescoreBuf[rescoreId], 1280, stream);
  
  
  int num[250];
  char tok[] = " ";
  char *token;
  token = strtok(rescoreBuf[rescoreId], tok);
  int i;

  for(i = 0; token = strtok(NULL, tok); i++){
    num[i]=atoi(token);
  }

  std::vector<int32> words(num, num + i);

  rescoreStr[rescoreId]->append("\t\t\t\t\t\t\t\t");
  rescoreStr[rescoreId]->append(std::to_string(rescoreId));
  rescoreStr[rescoreId]->append(": ");
  for (int j = 0; j < i; j++) {
    std::string s = word_syms.Find(words[j]);
    if (s.empty()) {
      KALDI_WARN << "Word-id " << words[j] << " not in symbol table.";
      // msg << "<#" << std::to_string(j) << "> ";
    } else {
      // msg << s << " ";
      // KALDI_LOG << s;
      rescoreStr[rescoreId]->append(s);
      rescoreStr[rescoreId]->append(" ");
      //msg << s;
    }
  }
  KALDI_LOG << *rescoreStr[rescoreId] << "##";

  free(rescoreBuf[rescoreId]);
  flag[rescoreId] = 1;

  return 0;
}
//---------------------------//





int main(int argc, char *argv[]) {
  try {
    using namespace kaldi;
    using namespace fst;

    typedef kaldi::int32 int32;
    typedef kaldi::int64 int64;

    const char *usage =
        "Reads in audio from a network socket and performs online\n"
        "decoding with neural nets (nnet3 setup), with iVector-based\n"
        "speaker adaptation and endpointing.\n"
        "Note: some configuration values and inputs are set via config\n"
        "files whose filenames are passed as options\n"
        "\n"
        "Usage: online2-tcp-nnet3-decode-faster [options] <nnet3-in> "
        "<fst-in> <word-symbol-table>\n";

    ParseOptions po(usage);


    // feature_opts includes configuration for the iVector adaptation,
    // as well as the basic features.
    OnlineNnet2FeaturePipelineConfig feature_opts;
    nnet3::NnetSimpleLoopedComputationOptions decodable_opts;
    LatticeFasterDecoderConfig decoder_opts;
    OnlineEndpointConfig endpoint_opts;

    BaseFloat chunk_length_secs = 0.18;
    BaseFloat output_period = 1;
    BaseFloat samp_freq = 16000.0;
    int port_num = 5050;
    int read_timeout = 3;
    bool produce_time = false;

    //-------------Add-----------//
    threadPack Package;
    //---------------------------//


    po.Register("samp-freq", &samp_freq,
                "Sampling frequency of the input signal (coded as 16-bit slinear).");
    po.Register("chunk-length", &chunk_length_secs,
                "Length of chunk size in seconds, that we process.");
    po.Register("output-period", &output_period,
                "How often in seconds, do we check for changes in output.");
    po.Register("num-threads-startup", &g_num_threads,
                "Number of threads used when initializing iVector extractor.");
    po.Register("read-timeout", &read_timeout,
                "Number of seconds of timeout for TCP audio data to appear on the stream. Use -1 for blocking.");
    po.Register("port-num", &port_num,
                "Port number the server will listen on.");
    po.Register("produce-time", &produce_time,
                "Prepend begin/end times between endpoints (e.g. '5.46 6.81 <text_output>', in seconds)");

    feature_opts.Register(&po);
    decodable_opts.Register(&po);
    decoder_opts.Register(&po);
    endpoint_opts.Register(&po);

    po.Read(argc, argv);

    if (po.NumArgs() != 4) {
      po.PrintUsage();
      return 1;
    }

    //-------------Add-----------//
    std::string clat_wspecifier;
    
    std::string nnet3_rxfilename = po.GetArg(1),
        fst_rxfilename = po.GetArg(2),
        word_syms_filename = po.GetArg(3);
        clat_wspecifier = po.GetArg(4);
    
    // for multithreading
    pthread_t thread_id[MAX_SEN];
    //---------------------------//
    
    OnlineNnet2FeaturePipelineInfo feature_info(feature_opts);
    BaseFloat frame_shift = feature_info.FrameShiftInSeconds();
    int32 frame_subsampling = decodable_opts.frame_subsampling_factor;

    KALDI_VLOG(1) << "Loading AM...";

    TransitionModel trans_model;
    nnet3::AmNnetSimple am_nnet;
    {
      bool binary;
      Input ki(nnet3_rxfilename, &binary);
      trans_model.Read(ki.Stream(), binary);
      am_nnet.Read(ki.Stream(), binary);
      SetBatchnormTestMode(true, &(am_nnet.GetNnet()));
      SetDropoutTestMode(true, &(am_nnet.GetNnet()));
      nnet3::CollapseModel(nnet3::CollapseModelConfig(), &(am_nnet.GetNnet()));
    }

    // this object contains precomputed stuff that is used by all decodable
    // objects.  It takes a pointer to am_nnet because if it has iVectors it has
    // to modify the nnet to accept iVectors at intervals.
    nnet3::DecodableNnetSimpleLoopedInfo decodable_info(decodable_opts,
                                                        &am_nnet);

    KALDI_VLOG(1) << "Loading FST...";

    fst::Fst<fst::StdArc> *decode_fst = ReadFstKaldiGeneric(fst_rxfilename);

    fst::SymbolTable *word_syms = NULL;
    if (!word_syms_filename.empty())
      if (!(word_syms = fst::SymbolTable::ReadText(word_syms_filename)))
        KALDI_ERR << "Could not read symbol table from file "
                  << word_syms_filename;

    signal(SIGPIPE, SIG_IGN); // ignore SIGPIPE to avoid crashing when socket forcefully disconnected

    TcpServer server(read_timeout);

    server.Listen(port_num);


    while (true) {

      server.Accept();

      int32 samp_count = 0;// this is used for output refresh rate
      size_t chunk_len = static_cast<size_t>(chunk_length_secs * samp_freq);
      int32 check_period = static_cast<int32>(samp_freq * output_period);
      int32 check_count = check_period;

      int32 frame_offset = 0;

      bool eos = false;

      OnlineNnet2FeaturePipeline feature_pipeline(feature_info);
      SingleUtteranceNnet3Decoder decoder(decoder_opts, trans_model,
                                          decodable_info,
                                          *decode_fst, &feature_pipeline);

      while (!eos) {

        decoder.InitDecoding(frame_offset);
        OnlineSilenceWeighting silence_weighting(
            trans_model,
            feature_info.silence_weighting_config,
            decodable_opts.frame_subsampling_factor);
        std::vector<std::pair<int32, BaseFloat>> delta_weights;

        while (true) {
          eos = !server.ReadChunk(chunk_len);
          
          if (eos) {
            feature_pipeline.InputFinished();

            if (silence_weighting.Active() &&
                feature_pipeline.IvectorFeature() != NULL) {
              silence_weighting.ComputeCurrentTraceback(decoder.Decoder());
              silence_weighting.GetDeltaWeights(feature_pipeline.NumFramesReady(),
                                                frame_offset * decodable_opts.frame_subsampling_factor,
                                                &delta_weights);
              feature_pipeline.UpdateFrameWeights(delta_weights);
            }

            decoder.AdvanceDecoding();
            decoder.FinalizeDecoding();
            frame_offset += decoder.NumFramesDecoded();
            if (decoder.NumFramesDecoded() > 0) {
              CompactLattice lat;
              decoder.GetLattice(true, &lat);
              std::string msg = LatticeToString(lat, *word_syms);

              // get time-span from previous endpoint to end of audio,
              if (produce_time) {
                int32 t_beg = frame_offset - decoder.NumFramesDecoded();
                int32 t_end = frame_offset;
                msg = GetTimeString(t_beg, t_end, frame_shift * frame_subsampling) + " " + msg;
              }

              KALDI_VLOG(1) << "EndOfAudio, sending message: " << msg;
              server.WriteLn(msg);
            } else
              server.Write("\n");
            server.Disconnect();
            break;
          }

          Vector<BaseFloat> wave_part = server.GetChunk();
          feature_pipeline.AcceptWaveform(samp_freq, wave_part);
          samp_count += chunk_len;

          if (silence_weighting.Active() &&
              feature_pipeline.IvectorFeature() != NULL) {
            silence_weighting.ComputeCurrentTraceback(decoder.Decoder());
            silence_weighting.GetDeltaWeights(feature_pipeline.NumFramesReady(),
                                              frame_offset * decodable_opts.frame_subsampling_factor,
                                              &delta_weights);
            feature_pipeline.UpdateFrameWeights(delta_weights);
          }

          decoder.AdvanceDecoding();

          if (samp_count > check_count) {
            if (decoder.NumFramesDecoded() > 0) {
              Lattice lat;
              decoder.GetBestPath(false, &lat);
              TopSort(&lat); // for LatticeStateTimes(),
              std::string msg = LatticeToString(lat, *word_syms);

              // get time-span after previous endpoint,
              if (produce_time) {
                int32 t_beg = frame_offset;
                int32 t_end = frame_offset + GetLatticeTimeSpan(lat);
                msg = GetTimeString(t_beg, t_end, frame_shift * frame_subsampling) + " " + msg;
              }

              KALDI_VLOG(1) << "Temporary transcript: " << msg;
              server.WriteLn(msg, "\r");

              // CompactLattice clat;
              // ConvertLattice(lat, &clat);
              // CompactLatticeWriter clat_writer(clat_wspecifier);
              // clat_writer.Write(msg,clat);

            }
            check_count += check_period;
          }

          if (decoder.EndpointDetected(endpoint_opts)) {
            decoder.FinalizeDecoding();
            frame_offset += decoder.NumFramesDecoded();
            CompactLattice lat;
            decoder.GetLattice(true, &lat);
            std::string msg = LatticeToString(lat, *word_syms);
            
            //-------------Add-----------//
            CompactLatticeWriter clat_writer(clat_wspecifier);
            clat_writer.Write("000", lat);
            //---------------------------//


            // get time-span between endpoints,
            if (produce_time) {
              int32 t_beg = frame_offset - decoder.NumFramesDecoded();
              int32 t_end = frame_offset;
              msg = GetTimeString(t_beg, t_end, frame_shift * frame_subsampling) + " " + msg;
            }

            KALDI_VLOG(1) << "Endpoint, sending message: " << msg;

            //-------------Add-----------//
            if (msg.length()!=0)
            {

              Package.id = id;
              Package._word_syms = word_syms;
              
              
              //pthread_create(&thread_id[id], NULL, rescoring, (void *)word_syms);
              pthread_create(&thread_id[id], NULL, rescoring, (void *)&Package);
              pthread_detach(thread_id[id]);
              KALDI_LOG<<"@@@@@@@@@@@@@@@@@"<< id <<"@@@@@@@@@@@@@@@@@";
              
              
              //CompactLattice *latt = &lat;
              
              
              // int status;
              // status = pthread_kill(thread_id[0],0);
              // if ( status == ESRCH ) // 존재하지 않는 쓰레드 아이디일때, 다시 살리면 된다.
              // {   
              // }
              // else if ( status == EINVAL ) // 잘못된 시그널을 전달했을 경우.
              // { 
              // } 
              // else // 현재 쓰레드는 생존해 있다.
              // {
              //   pthread_create(&thread_id[1], NULL, rescoring2, (void *)word_syms);
              //   pthread_detach(thread_id[1]);
              // } 9.9 700 139 1800 700 8300 8900 89Gb

              for(int idx=0; idx<=id; idx++) {
                if(flag[idx]==1) {
                  server.WriteLn("\n");
                  server.WriteLn(*rescoreStr[idx]);
                  server.WriteLn("\n");

                  flag[idx]=0;
                  delete rescoreStr[idx];
                }
              }


              server.WriteLn((std::to_string(id) + ": " + msg));

              id = (id + 1) % 100;
            }
            //---------------------------//
            // 애로사항부터 해서 어떻게 코딩한거고 목적이 어떻게 되는지 markdown에 서술
            break; // while (true)
          }
        }
        
      }
    }
  } catch (const std::exception &e) {
    std::cerr << e.what();
    return -1;
  }
} // main()


namespace kaldi {
TcpServer::TcpServer(int read_timeout) {
  server_desc_ = -1;
  client_desc_ = -1;
  samp_buf_ = NULL;
  buf_len_ = 0;
  read_timeout_ = 1000 * read_timeout;
}

bool TcpServer::Listen(int32 port) {
  h_addr_.sin_addr.s_addr = INADDR_ANY;
  h_addr_.sin_port = htons(port);
  h_addr_.sin_family = AF_INET;

  server_desc_ = socket(AF_INET, SOCK_STREAM, 0);

  if (server_desc_ == -1) {
    KALDI_ERR << "Cannot create TCP socket!";
    return false;
  }

  int32 flag = 1;
  int32 len = sizeof(int32);
  if (setsockopt(server_desc_, SOL_SOCKET, SO_REUSEADDR, &flag, len) == -1) {
    KALDI_ERR << "Cannot set socket options!";
    return false;
  }

  if (bind(server_desc_, (struct sockaddr *) &h_addr_, sizeof(h_addr_)) == -1) {
    KALDI_ERR << "Cannot bind to port: " << port << " (is it taken?)";
    return false;
  }

  if (listen(server_desc_, 1) == -1) {
    KALDI_ERR << "Cannot listen on port!";
    return false;
  }

  KALDI_LOG << "TcpServer: Listening on port: " << port;

  return true;

}

TcpServer::~TcpServer() {
  Disconnect();
  if (server_desc_ != -1)
    close(server_desc_);
  delete[] samp_buf_;
}

int32 TcpServer::Accept() {
  KALDI_LOG << "Waiting for client...";

  socklen_t len;

  len = sizeof(struct sockaddr);
  client_desc_ = accept(server_desc_, (struct sockaddr *) &h_addr_, &len);

  struct sockaddr_storage addr;
  char ipstr[20];

  len = sizeof addr;
  getpeername(client_desc_, (struct sockaddr *) &addr, &len);

  struct sockaddr_in *s = (struct sockaddr_in *) &addr;
  inet_ntop(AF_INET, &s->sin_addr, ipstr, sizeof ipstr);

  client_set_[0].fd = client_desc_;
  client_set_[0].events = POLLIN;

  KALDI_LOG << "Accepted connection from: " << ipstr;

  return client_desc_;
}

bool TcpServer::ReadChunk(size_t len) {
  if (buf_len_ != len) {
    buf_len_ = len;
    delete[] samp_buf_;
    samp_buf_ = new int16[len];
  }

  ssize_t ret;
  int poll_ret;
  char *samp_buf_p = reinterpret_cast<char *>(samp_buf_);
  size_t to_read = len * sizeof(int16);
  has_read_ = 0;
  while (to_read > 0) {
    poll_ret = poll(client_set_, 1, read_timeout_);
    if (poll_ret == 0) {
      KALDI_WARN << "Socket timeout! Disconnecting..." << "(has_read_ = " << has_read_ << ")";
      break;
    }
    if (poll_ret < 0) {
      KALDI_WARN << "Socket error! Disconnecting...";
      break;
    }
    ret = read(client_desc_, static_cast<void *>(samp_buf_p + has_read_), to_read);
    if (ret <= 0) {
      KALDI_WARN << "Stream over...";
      break;
    }
    to_read -= ret;
    has_read_ += ret;
  }
  has_read_ /= sizeof(int16);

  return has_read_ > 0;
}

Vector<BaseFloat> TcpServer::GetChunk() {
  Vector<BaseFloat> buf;

  buf.Resize(static_cast<MatrixIndexT>(has_read_));

  for (int i = 0; i < has_read_; i++)
    buf(i) = static_cast<BaseFloat>(samp_buf_[i]);

  return buf;
}

bool TcpServer::Write(const std::string &msg) {

  const char *p = msg.c_str();
  size_t to_write = msg.size();
  size_t wrote = 0;
  while (to_write > 0) {
    ssize_t ret = write(client_desc_, static_cast<const void *>(p + wrote), to_write);
    if (ret <= 0)
      return false;

    to_write -= ret;
    wrote += ret;
  }

  return true;
}

bool TcpServer::WriteLn(const std::string &msg, const std::string &eol) {
  if (Write(msg))
    return Write(eol);
  else return false;
}

void TcpServer::Disconnect() {
  if (client_desc_ != -1) {
    close(client_desc_);
    client_desc_ = -1;
  }
}


}  // namespace kaldi
```



