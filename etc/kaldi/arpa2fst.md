arpa2fst.cc 코드 분석

우선 ParseOptions를 po(usage)로 선언
ArpaParseOptions options로 선언
options.Register(&po)

각종 option flag 선언

## flag
    std::string bos_symbol = "<s>";
    std::string eos_symbol = "</s>";
    std::string disambig_symbol;
    std::string read_syms_filename;
    std::string write_syms_filename;
    bool keep_symbols = false;
    bool ilabel_sort = true;

parseoptions에 있는 register 함수를 활용해 bos, eos, disambig 심볼과
read-symbol, write-symbol, keep-symbols 테이블, ilabel-sort 함수 선언

## register
```
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
```
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

## registercommon
```
template<typename T>
void ParseOptions::RegisterCommon(const std::string &name, T *ptr,
                                  const std::string &doc, bool is_standard) {
  KALDI_ASSERT(ptr != NULL);
  std::string idx = name;
  NormalizeArgName(&idx);
  if (doc_map_.find(idx) != doc_map_.end())
    KALDI_WARN << "Registering option twice, ignoring second time: " << name;
  this->RegisterSpecific(name, idx, ptr, doc, is_standard);
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
```
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
    \\가 존재하는지 찾기
#else
    const char *c = strrchr(argv[0], '/');
    /가 존재하는지 찾기
#endif
    SetProgramName(c == NULL ? argv[0] : c + 1);
  }
  // first pass: look for config parameter, look for priority
  for (i = 1; i < argc; i++) {
    if (std::strncmp(argv[i], "--", 2) == 0) {
      if (std::strcmp(argv[i], "--") == 0) {
        // a lone "--" marks the end of named options
        break;
        --만 있으면 break
      }
      bool has_equal_sign;
      SplitLongArg(argv[i], &key, &value, &has_equal_sign);
      스플릿하는 함수 사용
      NormalizeArgName(&key);
      Trim(&value);
      if (key.compare("config") == 0) {
        ReadConfigFile(value);
      }
      if (key.compare("help") == 0) {
        PrintUsage();
        exit(0);
      }
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
```
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
    예외 처리
  } else if (pos == 2) {  // we also don't allow empty keys: --=value
    PrintUsage(true);
    KALDI_ERR << "Invalid option (no key): " << in;
    키가 없는 경우
  } else {  // normal case: --option=value
    *key = in.substr(2, pos-2);  // 2 because starts with --.
    *value = in.substr(pos + 1);
    *has_equal_sign = true;
    정상적인 경우 key와 value, has_equal_sign 값을 저장
  }
}
```

## normalizeargname
```
void ParseOptions::NormalizeArgName(std::string *str) {
  std::string out;
  std::string::iterator it;

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

_를 -로 바꿔주는 함수