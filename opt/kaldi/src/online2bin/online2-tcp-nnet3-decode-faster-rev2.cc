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
#include <sys/un.h>


//------------Add------------//
#define MAX_SEN 100

// MAX_CLNT = 보내줄 소켓(n) + 음성소켓 (1)
#define MAX_CLNT 

// 띄어쓰기 서버 = 0 / tts 서버 = 1 / 채팅 서버 = 2
#define SPACE_SV 0
#define TTS_SV 1
#define CHAT_SV 2
#define VOICE_SV 3

// read buffer size
#define BUFF_SIZE 1024


std::string* rescoreStr[MAX_SEN];
std::string gsttStr;


int id = 1;
int clnt_cnt = 0;
int clnt_socks[MAX_CLNT];


typedef struct _threadPack{
  int id;
  int* clnt_socks;
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

  bool Write(const std::string &msg, int clnt_sock); // write to accepted client
  bool WriteLn(const std::string &msg, const std::string &eol = "\n", int clnt_sock = clnt_socks[0]); // write line to accepted client

  void Disconnect();
  

 private:
  struct ::sockaddr_in serv_addr;
  struct ::sockaddr_in clnt_addr;
  int serv_sock, clnt_sock;
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

  rescoreBuf[rescoreId] = (char*)calloc(1280, sizeof(char));
  rescoreStr[rescoreId] = new std::string();

  // popen을 이용하여 rescore를 진행하고, rescoreBuf에 담기
  FILE* stream=popen("/opt/zeroth/s5/local/test.sh | grep 000","r");
  fgets(rescoreBuf[rescoreId], 1280, stream);

  
  
  // rescoreBuf 단어가 숫자로 이루어져있기때문에, 문자로 변환해줘야함
  // 변환 값은 rescoreStr에 저장됨
  int num[250];
  char tok[] = " ";
  char *token;
  token = strtok(rescoreBuf[rescoreId], tok);
  int i;

  for(i = 0; token = strtok(NULL, tok); i++){
    num[i]=atoi(token);
  }

  std::vector<int32> words(num, num + i);

  // 토큰 추가
  rescoreStr[rescoreId]->append("R{");
  rescoreStr[rescoreId]->append(std::to_string(rescoreId));
  rescoreStr[rescoreId]->append("}");
  
  for (int j = 0; j < i; j++) {
    std::string s = word_syms.Find(words[j]);
    if (s.empty()) {
      KALDI_WARN << "Word-id " << words[j] << " not in symbol table.";
    } else {
      rescoreStr[rescoreId]->append(s);
      rescoreStr[rescoreId]->append(" ");
    }
  }
  
  // KALDI_LOG << *rescoreStr[rescoreId];

  // 저장공간 해제
  free(rescoreBuf[rescoreId]);

  char to_send[BUFF_SIZE];
  int* send_clnt;
  send_clnt = rescorePack->clnt_socks;

  strcpy(to_send, rescoreStr[rescoreId]->c_str());
  int len = strlen(to_send);

  // // 0번 1번 클라이언트에 각각 보내기
  // for(int j = 0; j < MAX_CLNT - 1; j++) {
  //   send(*(send_clnt + j), to_send, len, 0);
  // }
  send(*(send_clnt + SPACE_SV), to_send, len, 0);
  delete rescoreStr[rescoreId];

  return 0;
}



// 내장된 read 함수를 이용하여 띄어쓰기 된 데이터 수신
void* recv_msg_space(void* _Package) {
  // int* recv_clnt;
  // // KALDI_LOG << "ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ";
  // threadPack* sockPack = (threadPack *)_Package;
  // recv_clnt = sockPack->clnt_socks;
  
  // char to_recv_space[BUFF_SIZE];

  //   // 0번이 띄어쓰기 서버
  //   // @@ 무작정 1000개까지 다 읽어와도 되는건가?
  // int ret = read(*(recv_clnt + SPACE_SV), to_recv_space, BUFF_SIZE);
  // int len = strlen(to_recv_space);
  // if(ret) {
  //   send(*(recv_clnt + CHAT_SV), to_recv_space, len, 0);
  //   KALDI_LOG << to_recv_space;
  //   // KALDI_LOG << "ooooooooooooooooooooooooooooooooooooooooooooooo";
  // }
}

void* recv_msg_chat(void* _Package) {
  int* recv_clnt;

  threadPack* sockPack = (threadPack *)_Package;
  recv_clnt = sockPack->clnt_socks;
  
  char to_recv_chat[BUFF_SIZE];
  
    // 0번이 띄어쓰기 서버
    // @@ 무작정 1000개까지 다 읽어와도 되는건가?
    // 수정해야함 SPACE_SV -> CHAT_SV
  int ret = read(*(recv_clnt + CHAT_SV), to_recv_chat, BUFF_SIZE);
  int len = strlen(to_recv_chat);
  if(ret) {
    send(*(recv_clnt + TTS_SV), to_recv_chat, len, 0);
  }
}

void* recv_msg_gstt(void* _Package) {
  int* recv_clnt;

  threadPack* sockPack = (threadPack *)_Package;
  recv_clnt = sockPack->clnt_socks;
  
  char to_recv_gstt[BUFF_SIZE];
  ;
    // 0번이 띄어쓰기 서버
    // @@ 무작정 1000개까지 다 읽어와도 되는건가?
    // 수정해야함 SPACE_SV -> CHAT_SV
  int ret = read(*(recv_clnt + gSTT_SV), to_recv_gstt, BUFF_SIZE);
  std::string temp_str = to_recv_gstt;
  gsttStr.append(temp_str);
  
}

// void* recv_wav(void* _Package) {
//   int* recv_clnt;

//   threadPack* sockPack = (threadPack *)_Package;
//   recv_clnt = sockPack->clnt_socks;
  
//   char to_recv_wav[BUFF_SIZE];

//     // 0번이 띄어쓰기 서버
//     // @@ 무작정 1000개까지 다 읽어와도 되는건가?
//   int ret = read(*(recv_clnt + TTS_SV), to_recv_wav, BUFF_SIZE);
//   int len = strlen(to_recv_wav);
//   if(ret) {
//     KALDI_LOG << to_recv_wav;
//     send(*(recv_clnt + TTS_RESV), to_recv_wav, len, 0);
//   }
// }

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
    
    
    pthread_t reThreadId[MAX_SEN]; // for multi threading
    pthread_t clntThreadId[MAX_CLNT];      // for multi socket
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


    // 클라이언트 접속 대기 구간 (오디오 신호를 기다리는 밑의 문장때문에 대기)
    while (true) {
      
      // 여기서 클라이언트 대기가 없어서 stream over... 이 계속 뜨는거였다니 ㅇ..ㅇ
      while(clnt_cnt!=MAX_CLNT) {
        int clnt_sock_temp = server.Accept();
        int check=0;
        for(int cnt=0; cnt<clnt_cnt; cnt++) {
          if(clnt_socks[cnt]==clnt_sock_temp) {
            check=cnt;
            break;
          }
          else {
            check++;
          }
        }
        if(check == clnt_cnt) {
            clnt_socks[clnt_cnt]=clnt_sock_temp;
            clnt_cnt++;
        }
        KALDI_LOG<<"@@@@@@Successfully connected client: "<<clnt_cnt;
      }

      //-------------Add-----------//
      //---------------------------//



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
          
          Package.clnt_socks = clnt_socks;
          // Package.id = id;

          // 띄어쓰기 서버와 채팅서버로 보내줄 데이터
          // 띄어쓰기 서버에서 받아올 데이터
          pthread_create(&clntThreadId[0], NULL, recv_msg_space, (void *)&Package);
          pthread_detach(clntThreadId[0]);

          pthread_create(&clntThreadId[1], NULL, recv_msg_chat, (void *)&Package);
          pthread_detach(clntThreadId[1]);

          pthread_create(&clntThreadId[2], NULL, recv_msg_gstt, (void *)&Package);
          pthread_detach(clntThreadId[2]);

          // pthread_create(&clntThreadId[2], NULL, recv_wav, (void *)&Package);
          // pthread_detach(clntThreadId[2]);
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

              //---------------------임시-----------------------//

              KALDI_VLOG(1) << "EndOfAudio, sending message: " << msg;
              //server.WriteLn(msg,"#####\n", clnt_socks[1]);
            } else
              //server.Write("@@@@@\n", clnt_socks[1]);
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
              std::string token_msg = "A{";
              token_msg.append(std::to_string(id));
              token_msg.append("}");
              std::string msg = LatticeToString(lat, *word_syms);
              token_msg.append(msg);
              char temp_msg[BUFF_SIZE];
              strcpy(temp_msg, msg.c_str());
              // get time-span after previous endpoint,`
              if (produce_time) {
                int32 t_beg = frame_offset;
                int32 t_end = frame_offset + GetLatticeTimeSpan(lat);
                msg = GetTimeString(t_beg, t_end, frame_shift * frame_subsampling) + " " + msg;
              }
              //--------------------임시----------------------//
              KALDI_VLOG(1) << "Temporary transcript: " << msg;
              
              if(strlen(temp_msg))
                server.WriteLn(token_msg, "\r", clnt_socks[CHAT_SV]);

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
              Package._word_syms = word_syms;
              Package.id = id;
              
              std::string to_send_str = "D{";
              to_send_str.append(std::to_string(id));
              to_send_str.append("}");
              gsttStr.append("\n");
              to_send_str.append(gsttStr);
              char gstt[BUFF_SIZE];
              strcpy(gstt, to_send_str.c_str());
              gsttStr.clear();
              to_send_str.clear();
              
              std::string token_msg = "T{";
              token_msg.append(std::to_string(id));
              token_msg.append("}");
              token_msg.append(msg);
              
              
              // KALDI_LOG << msg << "@@@@@@@@@@@@@@@@@@@@@@$$$$$$$$$$$$$$$$$$$$$$";
              //pthread_create(&reThreadId[id], NULL, rescoring, (void *)word_syms);
              pthread_create(&reThreadId[id], NULL, rescoring, (void *)&Package);
              pthread_detach(reThreadId[id]);

              
              char temp2[BUFF_SIZE];
              strcpy(temp2, token_msg.c_str());
              int len = strlen(temp2);

              send(*(clnt_socks + SPACE_SV), temp2, len, 0);
              send(*(clnt_socks + CHAT_SV), temp2, len, 0);
              

              send(*(clnt_socks + CHAT_SV), gstt, strlen(gstt), 0);

              id = (id % MAX_SEN) + 1;
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
  serv_addr.sin_addr.s_addr = INADDR_ANY;
  serv_addr.sin_port = htons(port);
  serv_addr.sin_family = AF_INET;

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

  if (bind(server_desc_, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) == -1) {
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
  client_desc_ = accept(server_desc_, (struct sockaddr *) &clnt_addr, &len);
  

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
    // 음성데이터에서 데이터를 읽어들였을때 데이터가 없으면
    ret = read(clnt_socks[VOICE_SV], static_cast<void *>(samp_buf_p + has_read_), to_read);
    if (ret <= 0) {
      // KALDI_WARN << "Stream over...";
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

bool TcpServer::Write(const std::string &msg, int clnt_sock) {

  const char *p = msg.c_str();
  size_t to_write = msg.size();
  size_t wrote = 0;
  while (to_write > 0) {
    // ssize_t ret = write(clnt_sock, static_cast<const void *>(p + wrote), to_write);
    ssize_t ret = send(clnt_sock, static_cast<const void *>(p + wrote), to_write, 0);
    if (ret <= 0)
      return false;

    to_write -= ret;
    wrote += ret;
  }

  return true;
}

bool TcpServer::WriteLn(const std::string &msg, const std::string &eol, int clnt_sock) {
  if (Write(msg, clnt_sock))
    return Write(eol, clnt_sock);
  else return false;
}

void TcpServer::Disconnect() {
  if (client_desc_ != -1) {
    close(client_desc_);
    client_desc_ = -1;
  }
}


}  // namespace kaldi
