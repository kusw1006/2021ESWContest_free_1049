arpa2fst.cc 코드 분석

## KALDI_ASSERT -> kaldi-error.h
```c++
#ifndef NDEBUG
#define KALDI_ASSERT(cond)                                                     \
  do {                                                                         \
    if (cond)                                                                  \
      (void)0;                                                                 \
    else                                                                       \
      ::kaldi::KaldiAssertFailure_(__func__, __FILE__, __LINE__, #cond);       \
  } while (0)
#else
#define KALDI_ASSERT(cond) (void)0
#endif
```
에러 문구 출력

우선 ParseOptions를 po(usage)로 선언

## ParseOtions 중첩 클래스
```c++
ParseOptions::ParseOptions(const std::string &prefix,
                           OptionsItf *other):
    print_args_(false), help_(false), usage_(""), argc_(0), argv_(NULL) {
  ParseOptions *po = dynamic_cast<ParseOptions*>(other);
  //*po를 other로 다운 캐스팅
  if (po != NULL && po->other_parser_ != NULL) {
    // we get here if this constructor is used twice, recursively.
    other_parser_ = po->other_parser_;
  } else {
    other_parser_ = other;
  }
  //po가 NULL이 아니고 other_parser가 NULL이 아니면 other_parser에 other의 other_parser를 넣어줌
  //그리고 만약 NULL이면 other_parser에 other를 넣어준다.(처음에만 해당)
  if (po != NULL && po->prefix_ != "") {
    prefix_ = po->prefix_ + std::string(".") + prefix;
  } else {
    prefix_ = prefix;
  }
  //po가 NULL이 아니고 po->prefix_가 ""이 아니라면 prefix_는 기존 prefix에 .을 찍고 인자로 받아온
  //prefix를 더해줌. 만약 처음이라면 prefix_는 인자로 받아온 prefix이다.
}
```

ArpaParseOptions options로 선언
options.Register(&po)

## arpaparseOptions
```c++
struct ArpaParseOptions {
  enum OovHandling {
    kRaiseError,     ///< Abort on OOV words
    kAddToSymbols,   ///< Add novel words to the symbol table.
    kReplaceWithUnk,  ///< Replace OOV words with <unk>.
    kSkipNGram       ///< Skip n-gram with OOV word and continue.
  };

  ArpaParseOptions():
      bos_symbol(-1), eos_symbol(-1), unk_symbol(-1),
      oov_handling(kRaiseError), max_warnings(30) { }

  void Register(OptionsItf *opts) {
    // Registering only the max_warnings count, since other options are
    // treated differently by client programs: some want integer symbols,
    // while other are passed words in their command line.
    opts->Register("max-arpa-warnings", &max_warnings,
                   "Maximum warnings to report on ARPA parsing, "
                   "0 to disable, -1 to show all");
  }

  int32 bos_symbol;  ///< Symbol for <s>, Required non-epsilon.
  int32 eos_symbol;  ///< Symbol for </s>, Required non-epsilon.
  int32 unk_symbol;  ///< Symbol for <unk>, Required for kReplaceWithUnk.
  OovHandling oov_handling;  ///< How to handle OOV words in the file.
  int32 max_warnings;  ///< Maximum warnings to report, <0 unlimited.
};
```

각종 option flag 선언

## flag
```c++
std::string bos_symbol = "<s>";	// begin of sequence
std::string eos_symbol = "</s>";	// end of sequence
std::string disambig_symbol;
std::string read_syms_filename;
std::string write_syms_filename;
bool keep_symbols = false;
bool ilabel_sort = true;
```

parseoptions에 있는 register 함수를 활용해 bos, eos, disambig 심볼과
read-symbol, write-symbol, keep-symbols 테이블, ilabel-sort 함수 선언

## register
```c++
po.Register("bos-symbol", &bos_symbol,
                "Beginning of sentence symbol");
po.Register("eos-symbol", &eos_symbol,
                "End of sentence symbol");
po.Register("disambig-symbol", &disambig_symbol,
                "Disambiguator. If provided (e. g. #0), used on input side of "
                "backoff links, and <s> and </s> are replaced with epsilons");
po.Register("read-symbol-table", &read_syms_filename,
                "Use existing symbol table");
po.Register("write-symbol-table", &write_syms_filename,
                "Write generated symbol table to a file");
po.Register("keep-symbols", &keep_symbols,
                "Store symbol table with FST. Symbols always saved to FST if "
                "symbol tables are neither read or written (otherwise symbols "
                "would be lost entirely)");
po.Register("ilabel-sort", &ilabel_sort,
                "Ilabel-sort the output FST");
```

Register들은 registerTmpl로 이루어져있음

## RegisterTmpl

```c++
template<typename T>
void ParseOptions::RegisterTmpl(const std::string &name, T *ptr,
                                const std::string &doc) {
  if (other_parser_ == NULL) {
    this->RegisterCommon(name, ptr, doc, false);
  } else {
    KALDI_ASSERT(prefix_ != "" &&
                 "Cannot use empty prefix when registering with prefix.");
    std::string new_name = prefix_ + '.' + name;  // name becomes prefix.name
    other_parser_->Register(new_name, ptr, doc);
  }
}
```

other_parser_가 Null이면 registercommon으로 가고 아니면 새로운 이름 추가 후 register 재선언
other_parser는 parse-options.h에 있는 변수로 OptionsItf *other_parser 형태로 선언되어있다.
처음 선언되었을 때에는 other_parser가 NULL인 상태

## OptionsItf
```c++
class ParseOptions : public OptionsItf {
 public:
  explicit ParseOptions(const char *usage) :
    print_args_(true), help_(false), usage_(usage), argc_(0), argv_(NULL),
    prefix_(""), other_parser_(NULL) {
#if !defined(_MSC_VER) && !defined(__CYGWIN__) // This is just a convenient place to set the stderr to line
//_MSC_VER과 __CYGWIN__ 매크로는 kaldi-utils.h에 있음 뜻은 해석 못함
    setlinebuf(stderr);  // buffering mode, since it's called at program start.
#endif  // This helps ensure different programs' output is not mixed up.
    RegisterStandard("config", &config_, "Configuration file to read (this "
                     "option may be repeated)");
    RegisterStandard("print-args", &print_args_,
                     "Print the command line arguments (to stderr)");
    RegisterStandard("help", &help_, "Print out usage message");
    RegisterStandard("verbose", &g_kaldi_verbose_level,
                     "Verbose level (higher->more logging)");
    //도움말
  }
  ```

  registerstandard는 registercommon을 불러온다. is_standard는 true

## registercommon
```c++
template<typename T>
void ParseOptions::RegisterCommon(const std::string &name, T *ptr,
                                  const std::string &doc, bool is_standard) {
  KALDI_ASSERT(ptr != NULL);
  //ptr이 NULL이면 에러문구 출력
  std::string idx = name;
  NormalizeArgName(&idx);
  if (doc_map_.find(idx) != doc_map_.end())
    KALDI_WARN << "Registering option twice, ignoring second time: " << name;
    //만약 map에서 idx를 못찾으면 WARN 문구 출력
  this->RegisterSpecific(name, idx, ptr, doc, is_standard);
}

```

## doc_map -> DocMapType doc_map
typedef std::map<std::string, DocInfo> DocMapType;

```c++
  struct DocInfo {
    DocInfo() {}
    DocInfo(const std::string &name, const std::string &usemsg)
      : name_(name), use_msg_(usemsg), is_standard_(false) {}
    DocInfo(const std::string &name, const std::string &usemsg,
            bool is_standard)
      : name_(name), use_msg_(usemsg),  is_standard_(is_standard) {}

    std::string name_;
    std::string use_msg_;
    bool is_standard_;
  };
  ```

## registerspecific

```c++
void ParseOptions::RegisterSpecific(const std::string &name,
                                    const std::string &idx,
                                    bool *b,
                                    const std::string &doc,
                                    bool is_standard) {
  bool_map_[idx] = b;
  doc_map_[idx] = DocInfo(name, doc + " (bool, default = "
                          + ((*b)? "true)" : "false)"), is_standard);
}

void ParseOptions::RegisterSpecific(const std::string &name,
                                    const std::string &idx,
                                    int32 *i,
                                    const std::string &doc,
                                    bool is_standard) {
  int_map_[idx] = i;
  std::ostringstream ss;
  ss << doc << " (int, default = " << *i << ")";
  doc_map_[idx] = DocInfo(name, ss.str(), is_standard);
}

void ParseOptions::RegisterSpecific(const std::string &name,
                                    const std::string &idx,
                                    uint32 *u,
                                    const std::string &doc,
                                    bool is_standard) {
  uint_map_[idx] = u;
  std::ostringstream ss;
  ss << doc << " (uint, default = " << *u << ")";
  doc_map_[idx] = DocInfo(name, ss.str(), is_standard);
}

void ParseOptions::RegisterSpecific(const std::string &name,
                                    const std::string &idx,
                                    float *f,
                                    const std::string &doc,
                                    bool is_standard) {
  float_map_[idx] = f;
  std::ostringstream ss;
  ss << doc << " (float, default = " << *f << ")";
  doc_map_[idx] = DocInfo(name, ss.str(), is_standard);
}

void ParseOptions::RegisterSpecific(const std::string &name,
                                    const std::string &idx,
                                    double *f,
                                    const std::string &doc,
                                    bool is_standard) {
  double_map_[idx] = f;
  std::ostringstream ss;
  ss << doc << " (double, default = " << *f << ")";
  doc_map_[idx] = DocInfo(name, ss.str(), is_standard);
}

void ParseOptions::RegisterSpecific(const std::string &name,
                                    const std::string &idx,
                                    std::string *s,
                                    const std::string &doc,
                                    bool is_standard) {
  string_map_[idx] = s;
  doc_map_[idx] = DocInfo(name, doc + " (string, default = \"" + *s + "\")",
                          is_standard);
}

```


## NormalizeArgName
```c++
void ParseOptions::NormalizeArgName(std::string *str) {
  std::string out;
  std::string::iterator it;
  //c++ 반복자 (포인터)

  for (it = str->begin(); it != str->end(); ++it) {
    if (*it == '_')
      out += '-';  // convert _ to -
    else
      out += std::tolower(*it);
  }
  *str = out;

  KALDI_ASSERT(str->length() > 0);
}
```

## po.read
po.Read(argc, argv);

## read

들어오는 argument는
```
src/lmbin/arpa2fst \
--disambig-symbol=#0 \
--read-symbol-table=data/lang/words.txt \
2gram.arpa \
G.fst
```
```c++
int ParseOptions::Read(int argc, const char *const argv[]) {
  argc_ = argc;
  argv_ = argv;
  std::string key, value;
  int i;
  if (argc > 0) {
    // set global "const char*" g_program_name (name of the program)
    // so it can be printed out in error messages;
    // it's useful because often the stderr of different programs will
    // be mixed together in the same log file.
#ifdef _MSC_VER
    const char *c = strrchr(argv[0], '\\');
    //만약 _MSC_VER가 사전에 정의되어 있다면 \\가 존재하는지 찾기
#else
    const char *c = strrchr(argv[0], '/');
    //만약 _MSC_VER가 사전에 정의되어 있지 않다면 /가 존재하는지 찾기
#endif
    SetProgramName(c == NULL ? argv[0] : c + 1);
  }
  // first pass: look for config parameter, look for priority
  for (i = 1; i < argc; i++) {
    if (std::strncmp(argv[i], "--", 2) == 0) {
      if (std::strcmp(argv[i], "--") == 0) {
        // a lone "--" marks the end of named options
        break;
        //--만 있으면 break
      }
      bool has_equal_sign;
      SplitLongArg(argv[i], &key, &value, &has_equal_sign);
      //스플릿하는 함수 사용
      NormalizeArgName(&key);
      Trim(&value);
      if (key.compare("config") == 0) {
        ReadConfigFile(value);
      }
      //만약 key 값이 config라면
      if (key.compare("help") == 0) {
        PrintUsage();
        exit(0);
      }
      //만약 key 값이 help라면
    }
  }
  bool double_dash_seen = false;
  // second pass: add the command line options
  for (i = 1; i < argc; i++) {
    if (std::strncmp(argv[i], "--", 2) == 0) {
      if (std::strcmp(argv[i], "--") == 0) {
        // A lone "--" marks the end of named options.
        // Skip that option and break the processing of named options
        i += 1;
        double_dash_seen = true;
        break;
      }
      bool has_equal_sign;
      SplitLongArg(argv[i], &key, &value, &has_equal_sign);
      NormalizeArgName(&key);
      Trim(&value);
      if (!SetOption(key, value, has_equal_sign)) {
        PrintUsage(true);
        KALDI_ERR << "Invalid option " << argv[i];
      }
    } else {
      break;
    }
  }

  // process remaining arguments as positional
  for (; i < argc; i++) {
    if ((std::strcmp(argv[i], "--") == 0) && !double_dash_seen) {
      double_dash_seen = true;
    } else {
      positional_args_.push_back(std::string(argv[i]));
    }
  }

  // if the user did not suppress this with --print-args = false....
  if (print_args_) {
    std::ostringstream strm;
    for (int j = 0; j < argc; j++)
      strm << Escape(argv[j]) << " ";
    strm << '\n';
    std::cerr << strm.str() << std::flush;
  }
  return i;
}
```
## SplitLongArg
스플릿하는 함수
```c++
void ParseOptions::SplitLongArg(const std::string &in,
                                std::string *key,
                                std::string *value,
                                bool *has_equal_sign) {
  KALDI_ASSERT(in.substr(0, 2) == "--");  // precondition.
  size_t pos = in.find_first_of('=', 0);
  = 위치 찾기
  if (pos == std::string::npos) {  // we allow --option for bools
    // defaults to empty.  We handle this differently in different cases.
    *key = in.substr(2, in.size()-2);  // 2 because starts with --.
    *value = "";
    *has_equal_sign = false;
    //예외 처리
  } else if (pos == 2) {  // we also don't allow empty keys: --=value
    PrintUsage(true);
    KALDI_ERR << "Invalid option (no key): " << in;
    //키가 없는 경우
  } else {  // normal case: --option=value
    *key = in.substr(2, pos-2);  // 2 because starts with --.
    *value = in.substr(pos + 1);
    *has_equal_sign = true;
    //정상적인 경우 key와 value, has_equal_sign 값을 저장
  }
}
```

## Trim
```c++
void Trim(std::string *str) {
  const char *white_chars = " \t\n\r\f\v";

  std::string::size_type pos = str->find_last_not_of(white_chars);
  if (pos != std::string::npos)  {
    str->erase(pos + 1);
    pos = str->find_first_not_of(white_chars);
    if (pos != std::string::npos) str->erase(0, pos);
  } else {
    str->erase(str->begin(), str->end());
  }
}
```
" \t\n\r\f\v"에 해당하는 문자는 모두 삭제

## NumArgs 개수가 1이나 2가 아니라면 exit
```c++
if (po.NumArgs() != 1 && po.NumArgs() != 2) {
  po.PrintUsage();
  exit(1);
}
```
## GetArg는 positional_args_[i-1] 불어오기, 
```c++
std::string arpa_rxfilename = po.GetArg(1),
    fst_wxfilename = po.GetOptArg(2);
```

  std::string GetOptArg(int param) const {
    return (param <= NumArgs() ? GetArg(param) : "");
  }

  fst::SymbolTable* symbols;
  openfst에서 symbolTable class 선언
