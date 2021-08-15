# kaldi 분석

## Kaldi I/O

### kaldi 클래스의 입출력 스타일

```c++
class SomeKaldiClass {
    public:
    	// bool binary 1 == 기계어, 0 == text
    	void Read(std::istream &is, bool binary);
    	void Write(std::ostream &os, bool binary);
}
```

### 기본/STL유형에 대한 입력/출력 메커니즘

```c++
// low-level I/O function

template<class T>
void WriteBasicType(std::ostream &os, bool binary, T t) {}
void ReadBasicType(std::istream &is, bool binary, T t) {}
// >> bool, float, double, integer ...를 다루는 템플릿
```

```c++
// kaldi에서 차용 (class member를 int32로 가정)
void SomeKaldiClass:Read(std::istream &is, bool binary) {
    ReadBasicType(is, binary, &class_member_)
}

void SomeKaldiClass:Read(std::istream &is, bool binary) {
    ReadBasicType(is, binary, &class_member_)
}
```

> 알려진 크기의 int형만 사용 가능
>
> 디버깅 시, 용이함을 위해 자동 casting을 허용하지 않았음
>
> binary read 말고도 vector에 대해서도 마찬가지



```c++
// token을 읽고 쓰는 방식

void ReadTokenvoid ReadToken(std::istream &is, bool binary, std::string *token);
void WriteToken(std::ostream &os, bool binary, const std::string & token);

// in writing code:
WriteToken(os, binary, "<MyClassName>");

// in reading code:
ExpectToken(is, binary, "<MyClassName>");

// or, if a class has multiple forms:
std::string token;
ReadToken(is, binary, &token);
if(token == "<OptionA>") { ... }
else if(token == "<OptionB>") { ... }
...
```



### Kaldi Object가 파일에 저장되는 방식

> kaldi 읽기 코드는 binary인지 text인지 알아야 하며, 이를 user가 판단하게 하고싶지 않다.
>
> 따라서 binary kaldi file은 앞에 "\\0B" 문자열로 시작 (text의 경우 헤더가 붙을 수 없으므로 패스)
>
> 따라서 이 header를 처리해야함



### Kaldi에서 파일을 여는 방법

> 오류 처리의 용이 및 다양한 확장 파일이름을 지원하기 위해
>
> 중괄호를 사용하여 Input, Output class가 끝나는대로 file이 닫히게 하였다.
>
> 또한 "rxfilename" "wxfilename" 파일 이름을 사용하여 확장을 위한 파일임을 user에게 상기시킨다.

```c++
// kaldi 객체를 열 때

{	//input
    bool binary_in;
    Input ki(some_rxfilename, &binary_in);
    my_object.Read(ki.Stream(), binary_in);
    
    // 파일에 둘 이상의 객체를 가질 수 있음
    my_other_object.Read(ki.Stream(), binary_in);
}

{	//output. 참고로 "binary"는 아마도 명령줄 옵션
    Output ko(some_wxfilename, binary);
    my_object.Write(ko.Stream(), binary);
}
```



### 확장된 파일 이름

> "rxfilename", "wxfilename"은 각각 입/출력 클래스가 읽기/쓰기용 확장 파일이름으로 해석할 문자열이다.

- rxfilename의 유형

  - "-" 또는 ""는 표준 입력을 의미합니다.
  - "일부 명령 |" 입력 파이프된 명령을 의미합니다. 즉, "|"를 제거합니다. 나머지 문자열을 popen()을 통해 쉘에 제공하십시오.
  - "/some/filename:12345"는 파일에 대한 오프셋을 의미합니다. 즉, 파일을 열고 위치 12345를 찾습니다.
  - "/some/filename" ... 위의 패턴과 일치하지 않는 모든 것은 일반 파일 이름으로 처리됩니다(그러나 일부 명백하게 잘못된 것은 열려고 시도하기 전에 오류로 인식됩니다).

- wxfilename의 유형

  - "-" 또는 ""는 표준 입력을 의미합니다.
  - "| some command"는 출력 파이프된 명령을 의미합니다. 즉, "|"를 제거합니다. 나머지 문자열을 popen()을 통해 쉘에 제공하십시오.
  - "/some/filename" ... 위의 패턴과 일치하지 않는 모든 파일은 일반 파일 이름으로 처리됩니다(다시 말하지만 명백한 오류 제외).

  

###  Table concept

> c++의 class와 유사하게, 파일을 string으로 인덱싱 하는것이다

- collection of feature files (float형 행렬 형식)은 utt_id로 인덱싱된다
- collection of transcriptions (int32 vector 형식)은 utt_id로 인덱싱된다
- collection of Constrained MLLR transforms (float형 행렬 형식)은 spk_id로 인덱싱 된다.



> 테이블은 TableWriter, SequentialTableReader, RandomAccessTableReader, 
>
> (RandomAccessTableReaderMapped) 세(네) 가지 방법으로 접근 할 수 있다.
>
> 테이블이 어떤식으로 읽혀야 하는지에 대한 내용이며,
>
> 테이블 유형을 알기 위해 wspecifiers, rspecifiers 문자열을 제공해야함
>
> 문자열에 옵션을 주어 오류 허용 범위 및 데이터 형식을 지정해줄 수 있음

```c++
std::string feature_rspecifier = "scp:/tmp/my_orig_features.scp",
   transform_rspecifier = "ark:/tmp/transforms.ark",
   feature_wspecifier = "ark,t:/tmp/new_features.ark";	//  t 옵션 추가 (==text)

// there are actually more convenient typedefs for the types below,
// e.g. BaseFloatMatrixWriter, SequentialBaseFloatMatrixReader, etc.
TableWriter<BaseFloatMatrixHolder> feature_writer(feature_wspecifier);
SequentialTableReader<BaseFloatMatrixHolder> feature_reader(feature_rspecifier);
RandomAccessTableReader<BaseFloatMatrixHolder> transform_reader(transform_rspecifier);
for(; !feature_reader.Done(); feature_reader.Next()) {
   std::string utt = feature_reader.Key();
   if(transform_reader.HasKey(utt)) {
      Matrix<BaseFloat> new_feats(feature_reader.Value());
      ApplyFmllrTransform(new_feats, transform_reader.Value(utt));
      feature_writer.Write(utt, new_feats);
   }
}
```



### Kaldi Script 형식

> <string\> <rxfilename\>
>
> offset은 객체의 시작부분을 가리킴 (이진파일의 경우 \\0B)

```shell
utt_id_01002 gunzip -c /usr/data/file_010001.wav.gz |

# 슬라이싱도 가능 (현재는 행렬형식의 데이터에만 지원)
utt_id_01002 foo.ark:89142[,89:100]	# 파일을 열고 위치 89142로 이동하여 해당 행렬의 89~100열 선택
```



### kaldi archive 형식

> token1 [somthing]
>
> token2 [somthing]
>
> …
>
>  
>
> something은 어떻게 쓰고 읽을지를 알려주는 holder에 의해 형식이 다름
>
> 일반적으로 holder는 text형식에서 something이 줄 바꿈으로 끝나는 문자열임을 보장해줌

```
// 정수를 저장하는데 사용하는 텍스트 아카이브 형식
utt_id_1 5
utt_id_2 7
...
```



### 테이블 형식 지정 (w/r specifier)

> Table을 어떤식으로 읽고 쓸지 정해주는게 holder class였다면, 해당 홀더 클래스에 어떤 유형의 테이블인지 알려주기 위해 w/r specifier를 전달해 주어야했다.
>
> 문자열이 TableWriter 홀더 클래스에 전달된 경우 wspecifier라고 부르며
>
> RandomAccessTableReader 또는 SequentialTableReader 홀더 클래스에 전달된 경우 rspecifier라고 한다.

```c++
std::string rspecifier1 = "scp:data/train.scp" ; // 스크립트 파일
std::string rspecifier2 = "ark:-" ; // archive read from stdin (SoX 파이프라인 만들었던거 생각)

std::string wspecifier1 = "ark,t:| gzip -c > /some/dir/foo.ark.gz" ; // gzip으로 압축된 텍스트 아카이브에 write
std::string wspecifier2 = "ark,scp:data/my.ark,data/my.scp" ;	//  스크립트에 write
```



#### ark(아카이브), scp(스크립트) 파일을 동시에 쓰기

> wspecifier의 특별한 case
>
> , (콜론)으로 구별하며, 이때 꼭 **ark가 scp보다 먼저 위치하여야 한다**

```shell
"ark, scp:/some/dir/foo.ark,/some/dir/foo.scp"
```

: ark가 scp처럼 동작할 수 있게 함

- utt_id /somedir/foo.ark:1234 와 같이 오프셋 지정 가능
- 스크립트 파일을 segment로 나누는 것을 포함한 원하는 모든 작업 수행 가능



#### wspecifier의 옵션

- "b"(바이너리)는 바이너리 모드로 쓰기를 의미합니다(현재는 항상 기본값이므로 불필요).
- "t"(텍스트)는 텍스트 모드에서 쓰기를 의미합니다.
- "f"(플러시)는 각 쓰기 작업 후에 스트림을 플러시하는 것을 의미합니다.
- "nf"(플러시 없음)는 각 쓰기 작업 후에 스트림을 플러시하지 않음을 의미합니다(현재 무의미하지만 호출 코드가 기본값을 변경할 수 있음).
- "p"는 허용 모드를 의미하며 scp 파일에 일부 항목이 누락된 "scp:" wspecifiers에 영향을 줍니다. "p" 옵션을 사용하면 이러한 파일에 대해 아무 것도 쓰지 않고 오류를 보고하지 않습니다.

```shell
"ark, t, f:data/my.ark"
"ark, scp, t, f:data/my.ark, |gzip -c > data/my.scp.gz"
```



#### rspecifier의 옵션

> ark를 읽을 때, 대부분이 파이프라인으로 구성되어있기 때문에, 원하는 것을 찾기위해 메모리에 많은 데이터가 저장되어 안 내려올 수 있어 아래의 옵션을 사용할 경우가 발생함

- "o"(한 번)는 각 키가 한 번만 쿼리될 것임을 [RandomAccessTableReader](https://kaldi-asr.org/doc/classkaldi_1_1RandomAccessTableReader.html) 코드 에 하는 사용자 방법입니다 . 이렇게 하면 다시 필요한 경우에 대비하여 이미 읽은 개체를 메모리에 보관하지 않아도 됩니다.
- "p"(허용)는 오류를 무시하고 가능한 데이터만 제공하도록 코드에 지시합니다. 유효하지 않은 데이터는 존재하지 않는 것으로 처리됩니다. scp 파일에서 이것은 HasKey()에 대한 쿼리가 해당 파일을 강제로 로드하므로 파일이 손상된 경우 코드가 false를 반환하도록 알 수 있습니다. 아카이브에서 이 옵션은 아카이브가 손상되거나 잘린 경우 예외가 발생하는 것을 중지합니다(해당 시점에서 읽기가 중지됨).
- "s"(정렬됨)는 읽고 있는 아카이브의 키가 정렬된 문자열 순서로 되어 있음을 코드에 지시합니다. 대한 [RandomAccessTableReader](https://kaldi-asr.org/doc/classkaldi_1_1RandomAccessTableReader.html) , HasKey ()가 아니라 아카이브에 어떤 키를 호출 할 때 그것은 "높은"키를 발견, 그것은 곧으로 false를 반환 할 수있는이 수단; 끝까지 읽을 필요가 없습니다.
- "cs"(호출 정렬)는 HasKey() 및 Value()에 대한 호출이 정렬된 문자열 순서로 될 것임을 코드에 지시합니다. 따라서 이러한 함수 중 하나가 일부 문자열에 대해 호출되면 읽기 코드에서 더 낮은 번호의 키에 대한 개체를 삭제할 수 있습니다. 이것은 메모리를 절약합니다. 실제로 "cs"는 프로그램이 반복할 수 있는 다른 아카이브가 자체적으로 정렬되어 있다는 사용자의 주장을 나타냅니다.