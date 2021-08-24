# Grammar : src/lmbin/arpa2fst

<br>

## po & options

> arpa2fst [options] < input-arpa> < output-fst>
>
> eg) arpa2fst  --disambig-symbol=#0  --read-symbol-table=data/lang/words.txt   lm/input.arpa   G.fst

```c++
ParseOptions po(usage);

ArpaParseOptions options;
options.Register(&po);
```

<헤더파일>

ParseOptions: src/util/parse-options.h

ArpaParseOptions: src/lm/arpa-file-parser.h

OptionsItf : src/itf/options-itf.h

<br>

- ArpaParseOptions 
>  src/lm/arpa-file-parser.h

```c++
## src/lm/arpa-file-parser.h
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

Parseoptions -> ArpaParseOptions.Register 로 max-arpa-warnings 전달

<br>

<br>

## symbol 정의

```c++
    std::string bos_symbol = "<s>";
    std::string eos_symbol = "</s>";
    std::string disambig_symbol;
    std::string read_syms_filename;
    std::string write_syms_filename;
    bool keep_symbols = false;
    bool ilabel_sort = true;

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

ParseOptions의 Register 함수

Register은 일반적으로 RegisterTmpl 을 따름(다양한 변수형을 위해)

> template< typename T>
>
> void RegisterTmpl(const std::string &name, T *ptr, const std::string &doc);

<br>

- Register 함수 && RegisterTmpl
> src/util/parse-options.cc

```c++
void ParseOptions::Register(const std::string &name,
                            bool *ptr, const std::string &doc) {
  RegisterTmpl(name, ptr, doc);
}

void ParseOptions::Register(const std::string &name,
                            int32 *ptr, const std::string &doc) {
  RegisterTmpl(name, ptr, doc);
}

void ParseOptions::Register(const std::string &name,
                            uint32 *ptr, const std::string &doc) {
  RegisterTmpl(name, ptr, doc);
}

void ParseOptions::Register(const std::string &name,
                            float *ptr, const std::string &doc) {
  RegisterTmpl(name, ptr, doc);
}

void ParseOptions::Register(const std::string &name,
                            double *ptr, const std::string &doc) {
  RegisterTmpl(name, ptr, doc);
}

void ParseOptions::Register(const std::string &name,
                            std::string *ptr, const std::string &doc) {
  RegisterTmpl(name, ptr, doc);
}

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

other_parser_ != NULL 이면 prefix.name으로 다시 Register로

other_parser_==NULL 이면 RegisterCommon

첫 선언 때는 NULL임

<br>

- RegisterCommon(name, ptr, doc, is_standard)

> src/util/parse-options.cc

```c++
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

name으로 index찾기 

doc_map_에서 idx찾기 ->있으면 전에 한번 들어갔던거임(두번째는 무시)

없으면 RegisterSpecific에 넣기

<br>

- NormalizeArgName(&idx)

```c++
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

이름에서 _는 -로 바꿈

<br>

- RegisterSpecific(name, idx, ptr, doc, is_standard)

> src/util/parse-options.cc 
>
> ptr이 가리키는 자료형마다 RegisterSpecific이 다 다름

```c++
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

만약 문자열이면 위의 코드

string_map에 idx & string 추가

doc_map에 idx& DocInfo추가

<br>

<br>

## Read

> int ParseOptions::Read(int argc, const char *const argv[]) -> src/util/parse-options.cc


```c++
    po.Read(argc, argv);

    if (po.NumArgs() != 1 && po.NumArgs() != 2) {
      po.PrintUsage();
      exit(1);
    }
    std::string arpa_rxfilename = po.GetArg(1),
        fst_wxfilename = po.GetOptArg(2);
	
	int64 disambig_symbol_id = 0;
```

argc(인자 수),  argv(인자 포인터)

받은 인자 수가 1이나 2가 아니면 종료

첫번째 인자-> arpa_rxfilename  두번째 인자->fst_wxfilename

disambig_symbol_id 자료형 지정, 초기화

<br>

<br>

## fst:: SymbolTable 

> [fst::SymbolTable -> symbol-table.h](http://www.openfst.org/doxygen/fst/html/symbol-table_8h_source.html) , line 299

```c++
    fst::SymbolTable* symbols;
    if (!read_syms_filename.empty()) {
      // Use existing symbols. Required symbols must be in the table.
      kaldi::Input kisym(read_syms_filename);
      symbols = fst::SymbolTable::ReadText(
          kisym.Stream(), PrintableWxfilename(read_syms_filename));
      if (symbols == NULL)
        KALDI_ERR << "Could not read symbol table from file "
                  << read_syms_filename;

      options.oov_handling = ArpaParseOptions::kSkipNGram;
      if (!disambig_symbol.empty()) {
        disambig_symbol_id = symbols->Find(disambig_symbol);
        if (disambig_symbol_id == -1) // fst::kNoSymbol
          KALDI_ERR << "Symbol table " << read_syms_filename
                    << " has no symbol for " << disambig_symbol;
      }
    } else {
      // Create a new symbol table and populate it from ARPA file.
      symbols = new fst::SymbolTable(PrintableWxfilename(fst_wxfilename));
      options.oov_handling = ArpaParseOptions::kAddToSymbols;
      symbols->AddSymbol("<eps>", 0);
      if (!disambig_symbol.empty()) {
        disambig_symbol_id = symbols->AddSymbol(disambig_symbol);
      }
    }

	// Add or use existing BOS and EOS.
    options.bos_symbol = symbols->AddSymbol(bos_symbol);
    options.eos_symbol = symbols->AddSymbol(eos_symbol);
```

SymbolTable이 비어있지 않으면 SymbolTable 내에 있는 symbol만 사용

SymbolTable 구조: symbol (,key)

[PrintableWxfilename](https://github.com/kaldi-asr/kaldi/blob/cbed4ff688a172a7f765493d24771c1bd57dcd20/src/util/kaldi-io.cc), line 73

: read_syms_filename에서 ""나 "-"가 아니라면 해당 이름 return해줌 -> ReadText의 name이 됨

impl이 return돼서 symbols에 들어감

<br>

oov 옵선 = kSkipNGram : oov 단어 나오면 n-gram skip하고 넘어감

Symbol Table의 disambig_symbol이 비어있지 않으면 

symbols와 같은  disambig_symbol을 Symbol Table에서 찾아서 key값 disambig_symbol_id에 넣음 -> 없으면 -1

Find(@): @가 key면 symbol찾아서 리턴, symbol이면 key 리턴

<br>

Symbol Table이 비어있다면 -> 새 symbol table 만들고 ARPA file로 채워야함

symbols = fst::SymbolTable 새로 할당해서 wxfilename넣은 

oov 옵션 = kAddToSymbols: 새 단어 symbol table에 추가함

eps추가

disambig& bos& eos addsymbol : symbol값 -1에서 0으로(사용안함에서 사용으로 변경 )

<br>

- fst::SymbolTable::ReadText 

> [symbol-table.h](http://www.openfst.org/doxygen/fst/html/symbol-table_8h_source.html) , line 374

```c++
static SymbolTable* ReadText(
    std::istream & strm, const std::string& name, 
    const SymbolTableTextOptions & opts = SymbolTableTextOptions()) {
    
    auto impl = 
        fst::WrapUnique(internal::SymbolTableImpl::ReadText(strm, name, opts));
    return impl ? new SymbolTable(std::move(impl)) : nullptr;
    
}
```

SymbolTable* ReadText: istream로부터 Symbol Table의 text representation을 읽음

WrapUnique: unique_ptr로 변환

SymbolTableTextOptions(): 음수라벨링 & 필드 구분자

impl=있으면 -> new SymbolTable(std::move(impl))  ~~-> 새로운 심볼받는 느낌~~

impl=없으면 -> nullptr

move: impl값이 return으로 들어가고 impl은 빈 문자열 됨

<br>

- SymbolTable(impl)

> [symbol-table.h](http://www.openfst.org/doxygen/fst/html/symbol-table_8h_source.html) , line 496

```c++
 SymbolTable(std::shared_ptr<internal::SymbolTableImplBase> impl)
 : impl_(std::move(impl)) {}
```

unique_ptr: 하나의 스마트 포인터만이 특정 객체를 소유할 수 있게 소유권 개념을 도입한 스마트 포인터

shared_ptr: 하나의 특정 객체를 참조하는 스마트 포인터가 몇 개인지 참조하는 스마트 포인터

~~impl_이 몇 번 참조되는지 counting -> fst state 개수를 나타내지 않을까~~

결국 kisym.stream()을 읽었을 때 자료가 존재하면 현재 impl에 넣고 이는 symbols에 들어감 

자료가 존재하지 않는다면 symbols에 nullptr반환

<br>

- AddSymbol(symbol, key)

> [symbol-table.h](http://www.openfst.org/doxygen/fst/html/symbol-table_8h_source.html) , line 418

```c++
virtual int64 AddSymbol(std::string_view symbol, int64 key) = 0;

int64 AddSymbol(std::string_view symbol, int64 key) {
     MutateCheck();
     return impl_->AddSymbol(symbol, key);
}
```

0을 리턴하게 됨(사용하겠다는 의미)

AddSymbol("symbol")에서 symbol이 이미 SymbolTable에 존재하면 그것을 사용하고 아니면 추가해준다는 의미

<br>

- MutateCheck()

> [symbol-table.h](http://www.openfst.org/doxygen/fst/html/symbol-table_8h_source.html) , line 511

```c++
void MutateCheck() {
    if (impl_.unique() || !impl_->IsMutable()) return;
    std::unique_ptr<internal::SymbolTableImplBase> copy = impl_->Copy();
    CHECK(copy != nullptr);
    impl_ = std::move(copy);
}
```

impl_이 unique하거나 mutable하지않으면 (mutable=값이 변할 수 있는) 종료

위의 조건이 아니라면 unique ptr로 만들고 종료

<br>

<br>

## keep_symbols

```c++
    // If producing new (not reading existing) symbols and not saving them,
    // need to keep symbols with FST, otherwise they would be lost.
    if (read_syms_filename.empty() && write_syms_filename.empty())
      keep_symbols = true;
```

keep_symbols = FST를 사용해서 symbol Table 저장. symbol table을 읽거나 쓰지 않으면 FST에 저장함

​	 						(안하면 사라짐)

<br>

<br>

## Complie LM

```c++
    KALDI_ASSERT (symbols != NULL);
    ArpaLmCompiler lm_compiler(options, disambig_symbol_id, symbols);
    {
      Input ki(arpa_rxfilename);
      lm_compiler.Read(ki.Stream());
    }
```

ArpaLmCompiler class의 lm_compiler(options, disambig_symbol_id, symbols)정의

arpa_rxfilename 내용 가져오고 

ki.Stream()의 ARPA LM file 읽어오기

<br>

- Read(stream)

> [arpa-file-parser.h](https://github.com/kaldi-asr/kaldi/blob/master/src/lm/arpa-file-parser.h) line 96

```c++
class ArpaFileParser{
	public:
		/// Read ARPA LM file from a stream
		void Read(std::istream &is);
}
```

stream에서 ARPA LM file을 읽어옴

<br>

<br>

## Sort FST

```c++
    // Sort the FST in-place if requested by options.
    if (ilabel_sort) {
      fst::ArcSort(lm_compiler.MutableFst(), fst::StdILabelCompare());
  	}
```

<br>

- lm_compiler.MutableFst() 

> [arpa-lm-compiler.h](https://github.com/kaldi-asr/kaldi/blob/master/src/lm/arpa-lm-compiler.h) line 42

```c++
  fst::StdVectorFst* MutableFst() { return &fst_; }
```

코드내에서 현재 돌고있는 fst의 pointer



- fst::StdILabelCompare()

> [arcsort.h](http://www.openfst.org/doxygen/fst/html/arcsort_8h_source.html) line 184 & line 223

```c++
 using StdILabelCompare = ILabelCompare<StdArc>;
 
 // Compare class for comparing input labels of arcs.
 template < class Arc>
 class ILabelCompare {
 public:
     constexpr ILabelCompare() {}

     constexpr bool operator()(const Arc& lhs, const Arc& rhs) const {
         return std::forward_as_tuple(lhs.ilabel, lhs.olabel) <
             std::forward_as_tuple(rhs.ilabel, rhs.olabel);

     }

     constexpr uint64 Properties(uint64 props) const {
         return (props & kArcSortProperties) | kILabelSorted |
             (props & kAcceptor ? kOLabelSorted : 0);

     }

 };
```

ILabelCompare()은 input label을 비교하기 위한 것.. constexpr이 붙었으므로 상수값이 될 예정



- fst::ArcSort  :  comp에 따라 arc 정렬(입력 수정)

> [arcsort.h](http://www.openfst.org/doxygen/fst/html/arcsort_8h_source.html) , line 102

```c++
template < class Arc, class Compare>
void ArcSort(MutableFst < Arc> *fst, Compare comp){
	ArcSortMapper< Arc, Compare> mapper(*fst, comp);
	StateMap(fst, mapper);
}
```

<br>

- ArcSortMapper

> [arcsort.h](http://www.openfst.org/doxygen/fst/html/arcsort_8h_source.html) , line 45

```
constexpr ArcSortMapper(const Fst<Arc>& fst, const Compare& comp)
    : fst_(fst), comp_(comp), i_(0) {}
```

fst_ 에는 입력받은 fst, comp_에도 ILabelCompare, i에는 0



- StateMap

> [state-map.h](http://www.openfst.org/doxygen/fst/html/state-map_8h_source.html), line 91 : input fst 수정

```c++
// Maps an arc type A using a mapper function object C, passed by pointer. This
// version modifies the input FST.
template < class A, class C>
void StateMap(MutableFst<A> * fst, C * mapper) {
    if (mapper->InputSymbolsAction() == MAP_CLEAR_SYMBOLS) {
        fst->SetInputSymbols(nullptr);
    }
    if (mapper->OutputSymbolsAction() == MAP_CLEAR_SYMBOLS) {
        fst->SetOutputSymbols(nullptr);
    }
    if (fst->Start() == kNoStateId) return;
    const auto props = fst->Properties(kFstProperties, false);
    fst->SetStart(mapper->Start());
    for (StateIterator<Fst<A>> siter(*fst); !siter.Done(); siter.Next()) {
        const auto state = siter.Value();
        mapper->SetState(state);
        fst->DeleteArcs(state);
        for (; !mapper->Done(); mapper->Next()) {
            fst->AddArc(state, mapper->Value());
        }
        fst->SetFinal(state, mapper->Final(state));
    }
    fst->SetProperties(mapper->Properties(props), kFstProperties);
}
```

mapper의 InputSymbolsAction()이 MAP_CLEAR_SYMBOLS면 isymbols=nullptr

fst의 start state가 유효하지 않은 id라면 종료

kFstProperties = all properties (binary & trinary)    [properties.h](http://www.openfst.org/doxygen/fst/html/properties_8h_source.html#l00324)

mapper의 start로 fst start 설정

State iterator가 현재 pointer에서 null이 될때까지

state= siter의 base(pointer)에 해당하는 value(state)

mapper state 설정

state에 해당하는 fst arc 지우기

mapper pointer가 null을 가리킬 때까지



> [cache.h](http://www.openfst.org/doxygen/fst/html/cache_8h_source.html#l00182) line 358 line 145

```c++
 void AddArc(State *state, const Arc &arc) { state->AddArc(arc); }
 
 void AddArc(const Arc &arc) {
      IncrementNumEpsilons(arc);
      arcs_.push_back(arc);
    }

void IncrementNumEpsilons(const Arc &arc) {
      if (arc.ilabel == 0) ++niepsilons_;
      if (arc.olabel == 0) ++noepsilons_;
    }

```



> [cache.h](http://www.openfst.org/doxygen/fst/html/cache_8h_source.html#l00182) line 365 line 182

```c++
// Deletes all arcs.
    void DeleteArcs(State *state) { state->DeleteArcs(); }
// Deletes all arcs.
    void DeleteArcs() {
      niepsilons_ = 0;
      noepsilons_ = 0;
      arcs_.clear();
    }
```



- InputSymbolsAction

> InputSymbolsAction: [state-map.h](http://www.openfst.org/doxygen/fst/html/state-map_8h_source.html)  (예시) line 434
>
> MapSymbolsAction: [arc-map.h](http://www.openfst.org/doxygen/fst/html/arc-map_8h_source.html) line 53

```c++
constexpr MapSymbolsAction InputSymbolsAction() const {
      return MAP_@@@_SYMBOLS;	//1
    }

// Determines how symbol tables are mapped.
enum MapSymbolsAction {
    // Symbols should be cleared in the result by the map.
    MAP_CLEAR_SYMBOLS,
    // Symbols should be copied from the input FST by the map.
    MAP_COPY_SYMBOLS,
    // Symbols should not be modified in the result by the map itself.
    // (They may set by the mapper).
    MAP_NOOP_SYMBOLS

};
```



- SetInputSymbols

> [fst.h](http://www.openfst.org/doxygen/fst/html/fst_8h_source.html#l00768) line 768

```c++
void SetInputSymbols(const SymbolTable *isyms) {
	isymbols_.reset(isyms ? isyms->Copy() : nullptr);
}
```

nullptr 받아왔으니까 nullptr로 isymbols_ 교체 (reset: 포인터 교체)



- start

> [fst.h](http://www.openfst.org/doxygen/fst/html/fst_8h_source.html#l00768) line 152 & line 187

```c++
int64 Start() const { return start_; }

int64 start_;          // Start state.
```





```c++
template < class FST>
class StateIterator {
public:
    using Arc = typename FST::Arc;
    using StateId = typename Arc::StateId;

    explicit StateIterator(const FST& fst) : s_(0) {
        fst.InitStateIterator(&data_);
    }
    
    bool Done() const {
        return data_.base ? data_.base->Done() : s_ >= data_.nstates;
    }

    StateId Value() const { return data_.base ? data_.base->Value() : s_; }

    void Next() {
        if (data_.base) {
            data_.base->Next();
        }
        else {
            ++s_;
        }
    }

    void Reset() {
        if (data_.base) {
            data_.base->Reset();
        }
        else {
            s_ = 0;
        }
    }

private:
    StateIteratorData<Arc> data_;
    StateId s_;
};
```

StateIterator에서 사용하는 data는 StateIteratorData의 data임



```c++
template < class Arc>
struct StateIteratorData {
    using StateId = typename Arc::StateId;

    // Specialized iterator if non-null.
    std::unique_ptr<StateIteratorBase<Arc>> base;
    // Otherwise, the total number of states.
    StateId nstates;

    StateIteratorData() : base(nullptr), nstates(0) {}

    StateIteratorData(const StateIteratorData&) = delete;
    StateIteratorData& operator=(const StateIteratorData&) = delete;

};
```



<br>

<br>

## Write symbols

```c++
    // Write symbols if requested.
    if (!write_syms_filename.empty()) {
      kaldi::Output kosym(write_syms_filename, false);
      symbols->WriteText(kosym.Stream());
    }
```

Dumps a text representation of the symbol table via a stream.

strm과 파일에 저장

<br>

- WriteText(source)
> [symbol-table.cc](http://www.openfst.org/doxygen/fst/html/symbol-table_8cc_source.html), line 392

```c++
bool SymbolTable::WriteText(const std::string& source) const {
    if (!source.empty()) {
        std::ofstream strm(source);
        if (!strm) {
            LOG(ERROR) << "SymbolTable::WriteText: Can't open file: " << source;
            return false;
        }
        if (!WriteText(strm, SymbolTableTextOptions())) {
            LOG(ERROR) << "SymbolTable::WriteText: Write failed: " << source;
            return false;
        }
        return true;
    }
    else {
        return WriteText(std::cout, SymbolTableTextOptions());
    }
}
```

kosym.Stream()이 비어있으면 WriteText(std::cout, SymbolTableTextOptions())

<br>

비어있지 않으면 std::ofstream strm(source) = file에 적기

strm 없으면 Error (can't open file)

WriteText(strm,option)이 false로 반환되면 Error (write failed)

<br>

strm있고 WriteText(strm,option)도 true로 반환되면 true 반환

<br>

- WriteText(strm, options)

> [symbol-table.cc](http://www.openfst.org/doxygen/fst/html/symbol-table_8cc_source.html), line 372

```c++
bool SymbolTable::WriteText(std::ostream& strm,
                                 const SymbolTableTextOptions & opts) const {
    if (opts.fst_field_separator.empty()) {
        LOG(ERROR) << "Missing required field separator";
        return false;

    }
    bool once_only = false;
    for (const auto& item : *this) {
        std::ostringstream line;
        if (item.Label() < 0 && !opts.allow_negative_labels && !once_only) {
            LOG(WARNING) << "Negative symbol table entry when not allowed";
            once_only = true;
        }
        line << item.Symbol() << opts.fst_field_separator[0] << item.Label()
            << '\n';
        strm.write(line.str().data(), line.str().length());
    }
    return true;
    
}
```

구분자 옵션 필요

ostringstream: 문자열 format을 조합하여 저장할 때

현재 위치의 label이 음수면 warning(음수라벨 허용 안될때)

"symbol [구분자] label [개행]" 순으로 저장

저장한거 strm에 적어주기

<br>

<br>

## Write LM FST

```c++
    // Write LM FST.
    bool write_binary = true, write_header = false;
    kaldi::Output kofst(fst_wxfilename, write_binary, write_header);
    fst::FstWriteOptions wopts(PrintableWxfilename(fst_wxfilename));
    wopts.write_isymbols = wopts.write_osymbols = keep_symbols;
    lm_compiler.Fst().Write(kofst.Stream(), wopts);
```

keep_symbols가 false면 input, ouput symbols은 write 안함

LM Fst에 kofst.Stream() 적기? -> lm_compiler.Fst().Write 찾아야함

<br>

- FstWriteOptions

> [fst.h](http://www.openfst.org/doxygen/fst/html/fst_8h_source.html) ,line 101

```c++
struct FstWriteOptions {
    std::string source;   // Where you're writing to.
    bool write_header;    // Write the header?
    bool write_isymbols;  // Write input symbols?
    bool write_osymbols;  // Write output symbols?
    bool align;           // Write data aligned (may fail on pipes)?
    bool stream_write;    // Avoid seek operations in writing.

    explicit FstWriteOptions(std::string_view source = "<unspecified>",
        bool write_header = true, bool write_isymbols = true,
        bool write_osymbols = true,
        bool align = FST_FLAGS_fst_align,
        bool stream_write = false)
        : source(source),
        write_header(write_header),
        write_isymbols(write_isymbols),
        write_osymbols(write_osymbols),
        align(align),
        stream_write(stream_write) {}

};
```

<br>

<br>

## delete

```c++
    delete symbols;
  } catch(const std::exception &e) {
    std::cerr << e.what();
    return -1;
  }
}
```

symbols 지우고 예외있는지 확인

<br>

<br>

- lm_compiler.Fst()
> [alpa-lm-compiler.h](https://github.com/kaldi-asr/kaldi/blob/master/src/lm/arpa-lm-compiler.h) ,line 41
```c++
const fst::StdVectorFst& Fst() const { return fst_; }
```

- StdVectorFst
> [fst-decl.h](http://www.openfst.org/doxygen/fst/html/fst-decl_8h_source.html) ,line 215
```c++
using StdVectorFst = VectorFst<StdArc>;

bool Write(std::ostream &strm, const FstWriteOptions &opts) const override {
  return WriteFst(*this, strm, opts);
```

- WriteFst
> [vector-fst.h](http://www.openfst.org/doxygen/fst/html/fst-decl_8h_source.html) ,line 630
```c++
template <class Arc, class State>
template <class FST>
bool VectorFst<Arc, State>::WriteFst(const FST &fst, std::ostream &strm, const FstWriteOptions &opts){
  static constexpr int file_version = 2;
  bool update_header = true;
  FstHeader hdr;
  hdr.SetStart(fst.Start());
  hdr.SetNumStates(kNoStateId);
  std::streampos start_offset = 0;
  if(fst.Properties(kExpanded, false) || opts.stream_write || (start_offset = strm.tellp()) != -1){
    hdr.SetNumStates(CountStates(fst));
    update_header = false;
  }
  const auto properties = fst.Properties(kCopyProperties, false) | Impl::kStaticProperties;
  internal::FstImpl<Arc>::WriteFstHeader(fst, strm, opts, file_version, "vector", properties, &hdr);
  Stateld num_states = 0;
  for(StateIterator<FST> siter(fst); !siter.Done(); siter.Next()){
    const auto s = siter.Value();
    fst.Final(s).Write(strm);
    const int64 narcs = fst.NumArcs(s);
    WriteType(strm, narcs);
    for(ArcIterator<FST> aiter(fst,s); !aiter.Done(); aiter.Next()){
      const auto &arc = aiter.Value();
      WriteType(strm, arc.ilabel);
      WriteType(strm, arc.olabel);
      arc.weight.Write(strm);
      WriteType(strm, arc.nextstate);
    }
    ++num_states;
  }
  strm.flush();
  if(!strm){
    LOG(ERROR) << "VectorFst::Write: Write failed: " << opts.source;
    return false;
  }
  if(update_header){
    hdr.SetNumStates(num_states);
    return internal::FstImpl<Arc>::UpdateFstHeader(fst, strm, opts, file_version, "vector", properties, &hdr, start_offset);
  } else{
    if(num_states != hdr.NumStates()){
      LOG(ERROR) << "Inconsistent number of states observed during write";
      return false;
    }
  }
  return true;
}
```

