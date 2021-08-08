# Shell Script

---



## 출력

#### 1. 명령의 실행 결과를 변수에 저장하는 법

```shell
VAR=`cmd` 또는 VAR=$(cmd)
```



#### 2. 표준/오류 출력

##### 2-1) 표준 오류 출력만을 변수로 설정

```shell
VAR=`cmd 2>&1 >/dev/null` 또는 VAR=$(cmd 2>&1 >/dev/null)
```

```/dev/null ```을 이용하여 표준 출력을 버리며, ``` 2>&1 ``` 으로 표준 오류 출력을 표준 출력으로 리디렉션하여, 표준 오류 출력만을 변수로 설정

##### 2-2) 표준 출력 / 표준 오류 출력을 모두 변수로 설정

```shell
VAR=`cmd 2>&1` 또는 VAR=$(cmd 2>&1)
```



#### 3. 변수 출력

##### 3-1) 변수 값 참조

| 표현                | 설명                       |
| ------------------- | -------------------------- |
| echo $VAR1          | VAR1의 값 출력             |
| echo ${VAR}1        | VAR의 값 + "1" 출력        |
| echo ${VAR2}${VAR3} | VAR2의 값과 VAR3의 값 출력 |

##### 3-2) 특수 참조

| 표현        | 설명                                                         |
| ----------- | ------------------------------------------------------------ |
| ${VAR=aaa}  | 변수 VAR이 아예 정의되어있지 않는 경우에만 "aaa" 대입        |
| ${VAR:=aaa} | 변수 VAR이 정의되어있지않거나, NULL인 경우에만 "aaa" 대입    |
| ${VAR-aaa}  | 변수 VAR이 정의되지않은 경우에만 "aaa" 반환하나, 대입은 이뤄지지 않음. |
| ${VAR:-aaa} | 변수 VAR이 정의되지않았거나, NULL인 경우에 "aaa" 반환하나, 대입은 이뤄지지않음 |
| ${VAR+aaa}  | 변수 VAR이 정의 된 경우, "aaa" 반환하고 아닌 경우 NULL 반환. 대입은 이뤄지지 않음 |
| ${VAR:+aaa} | 변수 VAR이 정의되었고, NULL이 아닌경우 "aaa" 반환하며 아닌 경우엔 NULL 반환, 대입은 이뤄지지않음 |

##### 3-3) 특수 변수 참조

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

#### 1. 환경변수

##### 1-1) export

> 사용자 환경변수를 전역변수로 설정
>
> : 환경 변수 설정은 현재의 세션에만 유효하기 때문에 모든 세션에 적용하기 위해서는 
>
> .bashrc나 .profile과 같은 설정 파일에 선언해야함

##### 1-2) env

> 전역 변수 설정 및 조회

##### 1-3) set

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



#### 2. 변수 제거

``` shell
unset VAR # 변수의 값이 아닌 변수를 지울것이기 때문에 $ 없이 변수명만 입력
```

---



## 명령어

#### 1. find

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





#### 2. awk

##### 2-1) Option

| 옵션 | 설명                                      |
| ---- | ----------------------------------------- |
| F    | 문자열을 분리할 기준이 되는 분리문자 입력 |
| v    | 파라미터 전달                             |

##### 2-2) 내장 함수

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

##### 2-3) 예시

**print**

```
$ echo "Hello World" | awk '{ print $0 }'
Hello World

$ echo "Hello World" | awk '{ print $1 }'
Hello

$ echo "Hello World" | awk '{ print $2 }'
World

$ echo "Hello,World" | awk -F "," '{ print $2 }'
World
```

**sub**

```
$ echo "i have a water." | awk -F " " '{ sub("a", "b", $4); print $4 }'
wbter.
```

**gsub**

```
$ echo "i have a water." | awk -F " " '{ gsub("a", "b"); print $1" "$2" "$3" "$4 }'
i hbve b wbter.
```

**print**

```
$ echo "Hello World" | awk '{ print $0 }'
Hello World

$ echo "Hello World" | awk '{ print $1 }'
Hello

$ echo "Hello World" | awk '{ print $2 }'
World

$ echo "Hello,World" | awk -F "," '{ print $2 }'
World
```

**sub**

```
$ echo "i have a water." | awk -F " " '{ sub("a", "b", $4); print $4 }'
wbter.
```

**gsub**

```
$ echo "i have a water." | awk -F " " '{ gsub("a", "b"); print $1" "$2" "$3" "$4 }'
i hbve b wbter.
```

**index**

```
$ echo "i have a water." | awk -F " " '{ print index($4, "a") }'
2
```

**length**

```
$ echo "i have a water." | awk -F " " '{ print length($4) }'
6
```

**substr**

```
$ echo "1234567890" | awk -F " " '{ print substr($1, 3, 2) }'
34
```

**split**

```
$ echo "A/B/C/D/E/F/G" | awk -F " " '{ print split($1, array, "/");print array[1];print array[3]; }'
7
A
C
```

**printf**

```
$ echo | awk '{ printf("%.1f + %.2f = %.3f\n", 40.1, 20.2, 40.1 + 20.2); }'
40.1 + 20.20 = 60.300
```

**system**

```
# system으로 추가 명령어 실행 
$ echo "Hello World" | awk '{ system("echo "$1) }'
Hello
```



#### 3. cut

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

---



## 프롬프트 스트링

> 사용자의 입력을 대기할 때 나타나는 문자

#### 1. PS1

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



#### 2. PS2

>긴 문자열을 나타낼 때 사용함

```shell
# 사용예시
ramesh@dev-db ~> myisamchk --silent --force --fast --update-state \
> --key_buffer_size=512M --sort_buffer_size=512M \
> --read_buffer_size=4M --write_buffer_size=4M \
> /var/lib/mysql/bugs/*.MYI
[Note: This uses the default ">" for continuation prompt]
```



#### 3. PS3

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



#### 4. PS4

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

#### 1. 파일 연산자

| 문자            | 설명                                                         |
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



#### 2. 논리 연산자

| 문자     | 설명     |
| -------- | -------- |
| &&, -a   | 논리 AND |
| \|\|, -o | 논리 OR  |

---



### 조건문



출력 1-3 https://shlee1990.tistory.com/917

변수 1 https://wikidocs.net/24935

find https://recipes4dev.tistory.com/156

각종 문자열 https://wikidocs.net/36834

PS https://www.thegeekstuff.com/2008/09/bash-shell-take-control-of-ps1-ps2-ps3-ps4-and-prompt_command/





if문 https://blackinkgj.github.io/shell-program/
