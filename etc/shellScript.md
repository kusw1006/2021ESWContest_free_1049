# Shell Script

## 목차

[TOC]



- [출력](#출력)
  + [1. 명령의 실행 결과 저장](#1-명령의-실행-결과-저장)
  + [2. 표준/오류 출력](#2-표준오류-출력)
    - [2-1) 표준 오류 출력만을 변수로 설정](#2-1-표준-오류-출력만을-변수로-설정)
    - [2-2) 표준 출력 / 표준 오류 출력을 모두 변수로 설정](#2-2-표준-출력-/-표준-오류-출력을-모두-변수로-설정)
  + [3. 변수 출력](#3-변수-출력)
    - [3-1) 변수 값 참조](#3-1-변수-값-참조)
    - [3-2) 특수 참조](#3-2-특수-참조)
    - [3-3) 특수 변수 참조](#3-3-특수-변수-참조)
- [변수](#변수)
  + [1. 환경변수](#1-환경-변수)
    - [1-1) export](#1-1-export)
    - [1-2) env](#1-2-env)
    - [1-3) set](#1-3-set)
  + [2. 변수 제거](#2-변수-제거)
- [명령어](#명령어)
  + [1. find](#1-find)
  + [2. awk](#2-awk)
    - [2-1) Option](#2-1-option)
    - [2-2) RegEX](#2-2-regex)
    - [2-3) BEGIN/pattern/END](#2-3-beginpatternend)
    - [2-4) 내장함수](#2-4-내장함수)
    - [2-5) 예시](#2-5-예시)
  + [3. cut](#3-cut)
  + [4. grep](#4-grep)
- [프롬프트 스트링](#프롬프트-스트링)
  + [1. PS1](#1-ps1)
  + [2. PS2](#2-ps2)
  + [3. PS3](#3-ps3)
  + [4. PS4](#4-ps4)
- [기타 연산자](#기타-연산자)
  + [1. 파일 연산자](#1-파일-연산자)
  + [2. 논리 연산자](#2-논리-연산자)
  + [3. 문자열 비교](#3-문자열-비교)
  + [4. 정규표현식](#4-정규표현식)
- [문법](#문법)
  - [1. 호출관련](1-호출관련)
    - [1-1) 인용](#1-1-인용)
    - [1-2) 괄호](#1-2-괄호)
    - [1-3) Redirection](#1-3-redirection)
    - [1-4) 다중명령](#1-4-다중명령)
  - [2. if문](#2-if문)

---



## 출력

### 1. 명령의 실행 결과 저장

```shell
VAR=`cmd` 또는 VAR=$(cmd)
```



### 2. 표준/오류 출력

#### 2-1) 표준 오류 출력만을 변수로 설정

```shell
VAR=`cmd 2>&1 >/dev/null` 또는 VAR=$(cmd 2>&1 >/dev/null)
```

```/dev/null ```을 이용하여 표준 출력을 버리며, ``` 2>&1 ``` 으로 표준 오류 출력을 표준 출력으로 리디렉션하여, 표준 오류 출력만을 변수로 설정

#### 2-2) 표준 출력 / 표준 오류 출력을 모두 변수로 설정

```shell
VAR=`cmd 2>&1` 또는 VAR=$(cmd 2>&1)
```



### 3. 변수 출력

#### 3-1) 변수 값 참조

| 표현                | 설명                       |
| ------------------- | -------------------------- |
| echo $VAR1          | VAR1의 값 출력             |
| echo ${VAR}1        | VAR의 값 + "1" 출력        |
| echo ${VAR2}${VAR3} | VAR2의 값과 VAR3의 값 출력 |

#### 3-2) 특수 참조

| 표현        | 설명                                                         |
| ----------- | ------------------------------------------------------------ |
| ${VAR=aaa}  | 변수 VAR이 아예 정의되어있지 않는 경우에만 "aaa" 대입        |
| ${VAR:=aaa} | 변수 VAR이 정의되어있지않거나, NULL인 경우에만 "aaa" 대입    |
| ${VAR-aaa}  | 변수 VAR이 정의되지않은 경우에만 "aaa" 반환하나, 대입은 이뤄지지 않음. |
| ${VAR:-aaa} | 변수 VAR이 정의되지않았거나, NULL인 경우에 "aaa" 반환하나, 대입은 이뤄지지않음 |
| ${VAR+aaa}  | 변수 VAR이 정의 된 경우, "aaa" 반환하고 아닌 경우 NULL 반환. 대입은 이뤄지지 않음 |
| ${VAR:+aaa} | 변수 VAR이 정의되었고, NULL이 아닌경우 "aaa" 반환하며 아닌 경우엔 NULL 반환, 대입은 이뤄지지않음 |

#### 3-3) 특수 변수 참조

| 표현      | 설명                                                         | 비고                                                   |
| --------- | ------------------------------------------------------------ | ------------------------------------------------------ |
| $?        | 이전에 실행된 명령의 종료 상태가 설정되는 변수               | 명령에 성공할 경우 "0", 실패할 경우 "0 이외의 수" 출력 |
| $!        | 백그라운드에서 실행 된 명령의 프로세스 ID가 설정되는 변수    |                                                        |
| $-        | set 명령으로 설정된 플래그 또는 쉘을 시작할 때 지정된 플래그 목록을 설정하는 변수 | $- 실행 결과 "abc"면, 플래그가 "-abc"라는 것           |
| $$        | 명령 자신의 PID가 설정되는 변수                              | 현재 매개변수의 개수 출력                              |
| $#        | 인수의 개수가 설정되는 변수                                  |                                                        |
| $@        | 쉘 스크립트 실행시 또는 set 명령 실행시 지정된 모든 매개 변수가 설정되는 변수 | "$@" 실행 시, 매개변수 각각 호출가능                   |
| $\*       | 쉘 스크립트 실행시 또는 set 명령 실행시 지정된 모든 매개 변수가 설정되는 변수 | "$\*" 실행 시, 모든 매개변수가 하나로 묶여서 출력      |
| $1, $2, … | set 명령 또는 쉘 스크립트의 N개의 인수 호출                  | $10으로 호출하면 $1로 먼저 해석되어 ${10}으로 호출     |

---



## 변수

### 1. 환경변수

#### 1-1) export

> 사용자 환경변수를 전역변수로 설정
>
> : 환경 변수 설정은 현재의 세션에만 유효하기 때문에 모든 세션에 적용하기 위해서는 
>
> .bashrc나 .profile과 같은 설정 파일에 선언해야함

#### 1-2) env

> 전역 변수 설정 및 조회

#### 1-3) set

> 사용자 환경 변수 설정 및 조회

```shell
set [ -abCefFjlmntuvx- ] [ -o option ] [ argument ... ] # 옵션 설정
set [ +abCefFjlmntuvx- ] [ +o option ] [ argument ... ] # 옵션 설정 취소
```

```shell
set -x	# xtrace 옵션 설정
set +x	# xtrace 옵션 취소
set alpha beta gamma	# 위치 매개변수 설정
set --	# 모든 위치 매개변수 설정 취소
```

| 옵션            | 설명                                                         |
| --------------- | ------------------------------------------------------------ |
| -a (all export) | 생성, 변경되는 변수를 export                                 |
| -e              | 명령이 실패하면 즉시 스크립트 종료                           |
| -x              | 각 명령이 실행되기 전에 출력                                 |
| -c              | 다음의 명령어 실행 (bash -c date, bash -c "echo 'A'", …)     |
| -o              | 옵션 설정 (set -o vi)                                        |
| 기타 옵션       | [링크](https://www.ibm.com/docs/ko/i/7.3?topic=variables-set) |



### 2. 변수 제거

``` shell
unset VAR # 변수의 값이 아닌 변수를 지울것이기 때문에 $ 없이 변수명만 입력
```

---



## 명령어

### 1. find

```shell
find [OPTION...] [PATH] [EXPRESSION...]
    OPTION
      -P        : 심볼릭 링크를 따라가지 않고, 심볼릭 링크 자체 정보 사용.
      -L        : 심볼릭 링크에 연결된 파일 정보 사용.
      -H        : 심볼릭 링크를 따라가지 않으나, Command Line Argument를 처리할 땐 예외.
      -D        : 디버그 메시지 출력.
    EXPRESSION
      -name     : 지정된 문자열 패턴에 해당하는 파일 검색.
      -empty    : 빈 디렉토리 또는 크기가 0인 파일 검색.
      -delete   : 검색된 파일 또는 디렉토리 삭제.
      -exec     : 검색된 파일에 대해 지정된 명령 실행.
      -path     : 지정된 문자열 패턴에 해당하는 경로에서 검색.
      -print    : 검색 결과를 출력. 검색 항목은 newline으로 구분. (기본 값)
      -print0   : 검색 결과를 출력. 검색 항목은 null로 구분.
      -size     : 파일 크기를 사용하여 파일 검색.
      -type     : 지정된 파일 타입에 해당하는 파일 검색.
      -mindepth : 검색을 시작할 하위 디렉토리 최소 깊이 지정.
      -maxdepth : 검색할 하위 디렉토리의 최대 깊이 지정.
      -atime    : 파일 접근(access) 시각을 기준으로 파일 검색.
      -ctime    : 파일 내용 및 속성 변경(change) 시각을 기준으로 파일 검색.
      -mtime    : 파일의 데이터 수정(modify) 시각을 기준으로 파일 검색.
```

| 사용 예                                                     | 옵션                                        |
| ----------------------------------------------------------- | ------------------------------------------- |
| 현재 디렉토리에 있는 파일 및 디렉토리 리스트 표시           | find                                        |
| 대상 디렉토리에 있는 파일 및 디렉토리 리스트 표시           | find [PATH]                                 |
| 대상 디렉토리 아래 모든 파일 및 하위 디렉토리에서 파일 검색 | find [PATH] -name [FILE]                    |
| 파일 또는 디렉토리만 검색                                   | find [PATH] -name [FILE] -type [f, d, …]    |
| 검색된 파일에 대한 상세 정보 출력                           | find [PATH] -name [FILE] - exec ls -l {} \; |
| 검색된 파일의 라인 수 출력                                  | find [PATH] -name -exec wc -l {} \;         |
| 하위 디렉토리 검색하지 않기                                 | find . -maxdepth 1 -name [FILE]             |

| 표현식                                                       | 설명                        |
| ------------------------------------------------------------ | --------------------------- |
| (expression)                                                 | expression 우선순위 지정.   |
| !expression -not expression                                  | expression 결과에 NOT 연산. |
| expression -a expression expression -and expression expression expression | expression 간 AND 연산.     |
| expression -o expression expression -or expression           | expression 간 OR 연산.      |

```shell
# 사용예시
find [PATH] ! -name [FILE] ! -name [FILE1] ...

1. PATH 경로 및 경로 안의 폴더/파일 출력
2. 이때 해당/하위 디렉토리에 [FILE]이름을 가진 파일명은 제외
3. 마찬가지로 [FILE1]이름을 가진 파일명은 제외
```



### 2. awk

#### 2-1) Option

| 옵션 | 설명                                      |
| ---- | ----------------------------------------- |
| F    | 문자열을 분리할 기준이 되는 분리문자 입력 |
| v    | 파라미터 전달                             |

#### 2-2) RegEX

> awk '행번호~/.../' 형식으로 사용

``` shell
# 사용예시

-- c.txt --
a b c
d e f
g h i
-----------

cat c.txt | awk '$2 ~ /^e/'
# 2번째 행에서 e로 시작하는 문자가 있는 경우 2번째 행 출력
```

#### 2-3) BEGIN/pattern/END

> **변수/배열 할당, 출력 명령, 내장 함수 및 제어 흐름문을 조작할 수 있음**

1. BEGIN {cmd} : 변수 초기화, 출력 테이블 헤더 인쇄 등 조작 수행전 실행
2. pattern {cmd} : 파일 또는 표준 입력에서 1줄을 읽은 후 pattern 블록을 실행하며, 파일을 끝까지 읽을 때까지 1줄씩 스캔하여 프로세스를 반복함
3. END {cmd} : 입력 스트림을 끝까지 읽었을때 END {cmd} 블록 실행, 집계 정보 처리 등을 주로 수행

#### 2-4) 내장함수

| 함수   | 설명                                          |
| ------ | --------------------------------------------- |
| sub    | 지정한 문자열 치환                            |
| gsub   | 문자열 일괄 치환                              |
| index  | 주어진 문자열과 일치하는 문자의 인덱스를 반환 |
| length | 문자열의 길이를 반환                          |
| substr | 시작위치에서 주어진 길이 만큼의 문자열 반환   |
| split  | 문자열을 분리하여 배열로 반환                 |
| print  | 문자열 출력                                   |
| printf | 지정한 포맷에 따라 함수 출력                  |



| 내장함수    | 설명                                             |
| ----------- | ------------------------------------------------ |
| $n          | 현재 레코드의 n번째 필드                         |
| $0          | 읽고있는 현재 줄의 텍스트 내용을 포함            |
| ARGC        | 명령 줄 인수의 수                                |
| ARGIND      | 명령 줄에서 현재 파일의 위치 (0부터 계산)        |
| ARGV        | 명령 줄 인수를 포함하는 배열                     |
| CONVFMT     | 숫자 변환 형식 (기본값은 %.6g)                   |
| ENVIRON     | 환경 변수의 연관 배열                            |
| ERRNO       | 마지막 스스템 오류에 대한 설명                   |
| FIELDWIDTHS | 필드 너비 목록 (공백 막대로 구분)                |
| FILENAME    | 현재 입력 파일의 이름                            |
| NR          | 실행 중 현재 줄 번호에 해당하는 레코드 수        |
| FNR         | NR과 동일하나 현재 파일을 기준                   |
| FS          | 필드 구분 기호 (기본값은 공백)                   |
| IGNORECASE  | true인 경우 대소문자를 구분하지 않는 일치가 수행 |
| NF          | 필드 수를 나타내며 실행 중 현재 필드 수에 해당   |
| OFMT        | 숫자 출력 형식 (기본 값은 %.6g)                  |
| OFS         | 출력 필드 구분 기호 (기본값은 공백)              |
| ORS         | 출력 레코드 구분 기호 (기본값은 줄바꿈)          |
| RS          | 레코드 구분 기호 (기본값은 줄 바꿈)              |
| RSTART      | 일치 함수와 일치하는 문자열의 첫 번째 위치       |
| RLENGTH     | 일치 함수와 일치하는 문자열의 길이               |
| SUBSEP      | 배열 인덱스 구분 기호 (기본값은 34)              |



#### 2-5) 예시

- **print**

```shell
$ echo "Hello World" | awk '{ print $0 }'
Hello World

$ echo "Hello World" | awk '{ print $1 }'
Hello

$ echo "Hello World" | awk '{ print $2 }'
World

$ echo "Hello,World" | awk -F "," '{ print $2 }'
World
```

- **sub**

```shell
$ echo "i have a water." | awk -F " " '{ sub("a", "b", $4); print $4 }'
wbter.
```

- **gsub**

```shell
$ echo "i have a water." | awk -F " " '{ gsub("a", "b"); print $1" "$2" "$3" "$4 }'
i hbve b wbter.
```

- **print**

```shell
$ echo "Hello World" | awk '{ print $0 }'
Hello World

$ echo "Hello World" | awk '{ print $1 }'
Hello

$ echo "Hello World" | awk '{ print $2 }'
World

$ echo "Hello,World" | awk -F "," '{ print $2 }'
World
```

- **sub**

```shell
$ echo "i have a water." | awk -F " " '{ sub("a", "b", $4); print $4 }'
wbter.
```

- **gsub**

```shell
$ echo "i have a water." | awk -F " " '{ gsub("a", "b"); print $1" "$2" "$3" "$4 }'
i hbve b wbter.
```

- **index**

```shell
$ echo "i have a water." | awk -F " " '{ print index($4, "a") }'
2
```

- **length**

```shell
$ echo "i have a water." | awk -F " " '{ print length($4) }'
6
```

- **substr**

```shell
$ echo "1234567890" | awk -F " " '{ print substr($1, 3, 2) }'
34
```

- **split**

```shell
$ echo "A/B/C/D/E/F/G" | awk -F " " '{ print split($1, array, "/");print array[1];print array[3]; }'
7
A
C
```

- **printf**

```shell
$ echo | awk '{ printf("%.1f + %.2f = %.3f\n", 40.1, 20.2, 40.1 + 20.2); }'
40.1 + 20.20 = 60.300
```

- **system**

```shell
# system으로 추가 명령어 실행 
$ echo "Hello World" | awk '{ system("echo "$1) }'
Hello
```



- 외부변수 전달

```SHELL
VAR=10000

echo | awk -v VARIABLE=${VAR} '{print VARIABLE}'
```

- 외부 변수를 수신할 내부 변수 정의

```shell
var1="var1"
var2="var2"
echo | awk '{print v1, v2}' v1=$var1 v2=$var2
```

- 입력 파일에서 올 때

```shell
awk '{print v1, v2}' v1=$var1 v2=$var2 Exam.txt
```

- BEGIN에서 정규식 사용

```shell
awk \
'BEGIN { 
		a="100test";
		if(a~/^100*/) {
			print "ok";
		}
	   }'
```

- 배열 사용

```shell
awk \
	'BEGIN {
	info="테스트";
	lens=split(info, tempArray, "");
	print length(tempArray), lens;
	}'
```





### 3. cut

| 옵션 | 내용                        |
| ---- | --------------------------- |
| -c   | 지정한 행을 출력            |
| -d   | 딜리미터를 지정             |
| -f   | 딜리미터로 잘라진 행을 출력 |

```shell
# 사용 예시

# 기본 구분자 이용
$ echo "A:B:C" | cut -c 1
A

$ echo "A:B:C" | cut -c 2
:

$ echo "A:B:C" | cut -c 3
B

$ echo "A:B:C" | cut -c 2-3
:B


# 구분자 지정
$ echo "A:B:C" | cut -d":" -f 2
B

$ echo "A:B:C" | cut -d":" -f 3
C
```



### 4. grep

>grep [OPTION...] PATTERN [FILE...]

```shell
-E        : PATTERN을 확장 정규 표현식(Extended RegEx)으로 해석.
-F        : PATTERN을 정규 표현식(RegEx)이 아닌 일반 문자열로 해석.
-G        : PATTERN을 기본 정규 표현식(Basic RegEx)으로 해석.
-P        : PATTERN을 Perl 정규 표현식(Perl RegEx)으로 해석.
-e        : 매칭을 위한 PATTERN 전달.
-f        : 파일에 기록된 내용을 PATTERN으로 사용.
-i        : 대/소문자 무시.
-v        : 매칭되는 PATTERN이 존재하지 않는 라인 선택.
-w        : 단어(word) 단위로 매칭.
-x        : 라인(line) 단위로 매칭.
-z        : 라인을 newline(\n)이 아닌 NULL(\0)로 구분.
-m        : 최대 검색 결과 갯수 제한.
-b        : 패턴이 매치된 각 라인(-o 사용 시 문자열)의 바이트 옵셋 출력.
-n        : 검색 결과 출력 라인 앞에 라인 번호 출력.
-H        : 검색 결과 출력 라인 앞에 파일 이름 표시.
-h        : 검색 결과 출력 시, 파일 이름 무시.
-o        : 매치되는 문자열만 표시.
-q        : 검색 결과 출력하지 않음.
-a        : 바이너리 파일을 텍스트 파일처럼 처리.
-I        : 바이너리 파일은 검사하지 않음.
-d        : 디렉토리 처리 방식 지정. (read, recurse, skip)
-D        : 장치 파일 처리 방식 지정. (read, skip)
-r        : 하위 디렉토리 탐색.
-R        : 심볼릭 링크를 따라가며 모든 하위 디렉토리 탐색.
-L        : PATTERN이 존재하지 않는 파일 이름만 표시.
-l        : 패턴이 존재하는 파일 이름만 표시.
-c        : 파일 당 패턴이 일치하는 라인의 갯수 출력.
```



---



## 프롬프트 스트링

> 사용자의 입력을 대기할 때 나타나는 문자

### 1. PS1

> 기본 프롬프트 스트링

```shell
PROMPTING
       When executing interactively, bash displays the primary prompt PS1 when it is ready to read a command, and the
       secondary  prompt  PS2 when it needs more input to complete a command.  Bash allows these prompt strings to be
       customized by inserting a number of backslash-escaped special characters that are decoded as follows:
              \a     an ASCII bell character (07)
              \d     the date in "Weekday Month Date" format (e.g., "Tue May 26")
              \D{format}
                     the format is passed to strftime(3) and the result is inserted into the prompt string; an  empty
                     format results in a locale-specific time representation.  The braces are required
              \e     an ASCII escape character (033)
              \h     the hostname up to the first ‘.’
              \H     the hostname
              \j     the number of jobs currently managed by the shell
              \l     the basename of the shell’s terminal device name
              \n     newline
              \r     carriage return
              \s     the name of the shell, the basename of $0 (the portion following the final slash)
              \t     the current time in 24-hour HH:MM:SS format
              \T     the current time in 12-hour HH:MM:SS format
              \@     the current time in 12-hour am/pm format
              \A     the current time in 24-hour HH:MM format
              \u     the username of the current user
              \v     the version of bash (e.g., 2.00)
              \V     the release of bash, version + patch level (e.g., 2.00.0)
              \w     the  current  working  directory,  with  $HOME  abbreviated  with a tilde (uses the value of the
                     PROMPT_DIRTRIM variable)
              \W     the basename of the current working directory, with $HOME abbreviated with a tilde
              \!     the history number of this command
              \#     the command number of this command
              \$     if the effective UID is 0, a #, otherwise a $
              \nnn   the character corresponding to the octal number nnn
              \\     a backslash
              \[     begin a sequence of non-printing characters, which could be used to  embed  a  terminal  control
                     sequence into the prompt
              \]     end a sequence of non-printing characters
```

| 기호 | 비고            |
| ---- | --------------- |
| \u   | 사용자명        |
| \h   | 호스트명        |
| \W   | 현재 디렉토리명 |



``` shell
# 색 코드
PURPLE="\[\033[0;35m\]"
WHITE="\[\033[1;37m\]"
GREEN="\[\033[1;32m\]"
NON_COLOR="\[\033[0m\]"

# 예시
export PS1="[$GREEN\u$WHITE@$PURPLE\h$WHITE \W]\$$NON_COLOR "
```



### 2. PS2

>긴 문자열을 나타낼 때 사용함

```shell
# 사용예시
ramesh@dev-db ~> myisamchk --silent --force --fast --update-state \
> --key_buffer_size=512M --sort_buffer_size=512M \
> --read_buffer_size=4M --write_buffer_size=4M \
> /var/lib/mysql/bugs/*.MYI
[Note: This uses the default ">" for continuation prompt]
```



### 3. PS3

> select 옵션을 처리할 때 나타나는 문자열

```shell
# 사용예시
ramesh@dev-db ~> cat ps3.sh

select i in mon tue wed exit
do
  case $i in
    mon) echo "Monday";;
    tue) echo "Tuesday";;
    wed) echo "Wednesday";;
    exit) exit;;
  esac
done

ramesh@dev-db ~> ./ps3.sh

1) mon
2) tue
3) wed
4) exit
#? 1
Monday
#? 4
[Note: This displays the default "#?" for select command prompt]
```



### 4. PS4

> 실행을 디버깅 할 때 출력되는 문자열, 명령어가 수행되기전 명령어를 출력해주는 set -x 사용 시 나타남

```shell
# 사용 예시
ramesh@dev-db ~> cat ps4.sh

export PS4='$0.$LINENO+ '
set -x
echo "PS4 demo script"
ls -l /etc/ | wc -l
du -sh ~

ramesh@dev-db ~> ./ps4.sh
../ps4.sh.3+ echo 'PS4 demo script'
PS4 demo script
../ps4.sh.4+ ls -l /etc/
../ps4.sh.4+ wc -l
243
../ps4.sh.5+ du -sh /home/ramesh
48K     /home/ramesh
[Note: This displays the modified "{script-name}.{line-number}+"
       while tracing the output using set -x]
```

---



## 기타 연산자

### 1. 파일 연산자

| 문자 [FILE]     | 설명                                                         |
| --------------- | ------------------------------------------------------------ |
| -e              | 파일이 존재                                                  |
| -f              | 파일이 존재하고 일반 파일인 경우(디렉토리 혹은 장치파일이 아닌 경우) |
| -s              | 파일이 존재하고 0보다 큰 경우                                |
| -d              | 파일이 존재하고 디렉토리인 경우                              |
| -b              | 파일이 존재하고 블록장치 파일인 경우                         |
| -c              | 파일이 존재하고 캐릭터 장치 파일인 경우                      |
| -p              | 파일이 존재하고 FIFO인 경우                                  |
| -h              | 파일이 존재하고 한 개 이상의 심볼릭 링크가 설정된 경우       |
| -L              | 파일이 존재하고 한 개 이상의 심볼릭 링크가 설정된 경우       |
| -S              | 파일이 소켓 디바이스인 경우                                  |
| -t              | 파일이 디스크립터가 터미널 디바이스와 연관이 있음            |
| -r              | 파일이 존재하고 읽기 가능한 경우                             |
| -w              | 파일이 존재하고 쓰기가 가능한 경우                           |
| -x              | 파일이 존재하고 실행 가능한 경우                             |
| -g              | 파일이 존재하고 SetGID가 설정된 경우                         |
| -u              | 파일이 존재하고 SetUID가 설정된 경우                         |
| -k              | 파일이 존재하고 스티키 비트(Sticky bit)가 설정된 경우        |
| -O              | 자신이 소유자임                                              |
| -G              | 그룹 아이디가 자신과 같음                                    |
| -N              | 마지막으로 읽힌 후에 변경 됐음                               |
| file1 -nt file2 | file1 파일이 file2 파일보다 최신임                           |
| file1 -ot file2 | file1 파일이 file2 파일보다 예전것임                         |
| file1 -ef file2 | file1 파일과 file2 파일이 같은 파일을 하드 링크하고 있음     |
| !               | 조건이 안 맞으면 참(예: ! -e file)                           |



### 2. 논리 연산자

| 문자     | 설명     |
| -------- | -------- |
| &&, -a   | 논리 AND |
| \|\|, -o | 논리 OR  |



### 3. 문자열 비교

| 표현                   | 설명                    |
| ---------------------- | ----------------------- |
| [String1] = [String2]  | 두 문자열이 같다면 참   |
| [String1] != [String2] | 두 문자열이 다르면 참   |
| -n [String]            | 빈 문자열이 아니라면 참 |
| -z [String]            | 빈 문자열이면 참        |



### 4. 정규표현식

| 표현     | 의미                                                         |
| -------- | ------------------------------------------------------------ |
| ^x       | 문자열의 시작을 표현하며 x 문자로 시작됨을 의미              |
| x$       | 문자열의 종료를 표현하며 x 문자로 종료됨을 의미              |
| .x       | 임의의 한 문자의 자리수를 표현하며 문자열이 x 로 끝난다는 것을 의미 |
| x+       | 반복을 표현하며 x 문자가 한번 이상 반복됨을 의미             |
| x?       | 존재여부를 표현하며 x 문자가 존재할 수도, 존재하지 않을 수도 있음을 의미 |
| x*       | 반복여부를 표현하며 x 문자가 0번 또는 그 이상 반복됨을 의미  |
| x\|y     | or 를 표현하며 x 또는 y 문자가 존재함을 의미                 |
| (x)      | 그룹을 표현하며 x 를 그룹으로 처리함을 의미                  |
| (x)(y)   | 그룹들의 집합을 표현하며 앞에서 부터 순서대로 번호를 부여하여 관리하고 x, y 는 각 그룹의 데이터로 관리됨 |
| (x)(?:y) | 그룹들의 집합에 대한 예외를 표현하며 그룹 집합으로 관리되지 않음을 의미한 |
| x{n}     | 반복을 표현하며 x 문자가 n번 반복됨을 의미                   |
| x{n,}    | 반복을 표현하며 x 문자가 n번 이상 반복됨을 의미              |
| {n,m}    | 반복을 표현하며 x 문자가 최소 n번 이상 최대 m 번 이하로 반복됨을 의미 |



| 표현  | 의미                                                         |
| ----- | ------------------------------------------------------------ |
| [xy]  | 문자선택을 표현하며 x와 y중의 하나를 의미                    |
| [^xy] | not을 표현하며 x및 y를 제외한 문자를 의미                    |
| [x-z] | range를 표현하며 x~z 사이의 문자를 의미                      |
| \\^   | escape를 의미하며 ^를 문자로 사용함을 의미                   |
| \\b   | word boundary를 표현하며 문자와 공백사이의 문자를 의미       |
| \\B   | non word boundary를 표현하며 문자와 공백사이가 아닌 문자를 의미 |
| \\d   | digit을 표현하며 숫자를 의미                                 |
| \\D   | non digit을 표현하며 숫자가 아닌 것을 의미                   |
| \\s   | space를 표현하며 공백 문자를 의미                            |
| \\S   | non space를 표현하며 공백문자가 아닌것을 의미                |
| \\t   | tab을 표현하며 탭 문자를 의미                                |
| \\v   | vertical tab을 표현하며 수직 탭 문자를 의미                  |
| \\w   | word를 표현하며 알파벳 + 숫자 + _ 중의 한 문자임을 의미      |
| \\W   | non word를 표현하며 알파벳 + 숫자 + _가 아닌문자를 의미      |
| ~     | 정규 표현식과 일치                                           |
| ~!    | 정규 표현식과 불일치                                         |



| Flag | 의미                                                         |
| ---- | ------------------------------------------------------------ |
| g    | Global 의 표현하며 대상 문자열내에 모든 패턴들을 검색하는 것을 의미한다. |
| i    | Ignore case 를 표현하며 대상 문자열에 대해서 대/소문자를 식별하지 않는 것을 의미한다. |
| m    | Multi line을 표현하며 대상 문자열이 다중 라인의 문자열인 경우에도 검색하는 것을 의미한다. |



``` shell
# 이메일에서의 사용 예시/^[0-9a-zA-Z]([-_\.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_\.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3}$/i1.시작을  0~9 사이 숫자 or a-z A-Z 알바펫 아무거나로 시작하고  /  중간에 - _  . 같은 문자가 있을수도 있고 없을수도 있으며2. 그 후에 0~9 사이 숫자 or a-z A-Z 알바펫중 하나의 문자가 없거나 연달아 나올수 있으며 /  @ 가 반드시 존재하고  3. 0-9a-zA-Z 여기서 하나가 있고  /  중간에 - _  . 같은 문자가 있을수도 있고 없을수도 있으며 / 그 후에 0~9 사이 숫자 or a-z A-Z 알바펫중 하나의 4. 문자가 없거나 연달아 나올수 있으며 /  반드시  .  이 존재하고  / [a-zA-Z] 의 문자가 2개나 3개가 존재 /   이 모든것은 대소문자 구분안함 
```

---



## 문법

### 1. 호출관련

#### 1-1) 인용

| 문자      | 설명                                                         |
| --------- | ------------------------------------------------------------ |
| ' '       | 모든 특수문자를 일반 문자로 인식                             |
| " "       | 일부 특수문자를 일반 문자로 인식 ($()와 ` `(명령어 대체 특수문자), $ (변수 값 대체 특수문자), \ (quotation 특수문자) 등은 예외) |
| \         | 특수문자 바로 앞에 사용되는데 해당 특수문자의 효과를 없애고 일반 문자처럼 처리 (뒤에 한 특수문자만 쿼팅) |
| ` ` \` \` | 역 따옴표는 따옴표 안에 있는 명령문의 실행하여 실행결과를 대입 |

#### 1-2) 괄호

| 문자 | 설명                                                         |
| ---- | ------------------------------------------------------------ |
| ()   | 함수 인수의 시작과 끝, 서브 쉘 작성 (스크립트의 다른 곳에서는 소괄호 안 서브 쉘에 들어있는 변수를 볼 수 없음), 배열 초기화 |
| (()) | **산술 연산**에 사용                                         |
| {}   | 명령 블록의 시작과 끝, 각종 변수의 존재범위도 연관됨, 매개변수 확장, 반복되는 문자열 목록 작성, 변수를 명확하게 식별 |
| []   | 배열 인덱스, 테스트 조건을 정의                              |
| [[]] | 기본적으로 단일 대괄호와 동일한 기능을 수행하지만 bash 내장  |

#### 1-3) Redirection

| 문자 | 설명                                                 |
| ---- | ---------------------------------------------------- |
| <    | 입력 재지정                                          |
| >    | 출력 재지정 (표준 출력 파일을 바꿈)                  |
| >>   | 출력 재지정 (파일의 내용을 추가하는 역할, 이어 쓰기) |

#### 1-4) 다중명령

| 문자 | 설명                                                         |
| ---- | ------------------------------------------------------------ |
| \|   | 명령과 명령을 연결 (왼쪽 명령의 실행결과를 오른쪽 명령어의 입력으로 전달) |
| ;    | 명령과 명령을 연결 (연결된 명령을 왼쪽부터 차례로 실행)      |
| &&   | 이전 명령이 정상 종료인 0의 값을 반환할 경우, 다음 명령 실행 (AND 연산) |
| \|\| | 이전 명령이 비정상 종료인 1의 값을 반환할 경우, 다음 명령 실행 (OR 연산) |



https://linuxgazette.net/18/bash.html

The Bash Man Page





### 2. if문









출력 1-3 https://shlee1990.tistory.com/917

변수 1 https://wikidocs.net/24935

find https://recipes4dev.tistory.com/156

각종 문자열 https://wikidocs.net/36834

PS https://www.thegeekstuff.com/2008/09/bash-shell-take-control-of-ps1-ps2-ps3-ps4-and-prompt_command/

awk https://shlee1990.tistory.com/487

정규표현식 https://hamait.tistory.com/342

호출관련 https://coding-chobo.tistory.com/54

if문 https://blackinkgj.github.io/shell-program/



<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>
