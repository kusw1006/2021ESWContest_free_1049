# path.sh

> 작성자: 이찬현



새로운 Local Storage를 사용한다면 아래와 같이 path.sh를 꼭 수정해줘야함

(비정상적으로 shell 코드를 작성한 경우가 있어, 아래의 PATH등록을 하지않으면 symbolic linking된 추가 스토리지 접근 시 오류 발생)

```shell
export PATH=/data/s5:data/s5/utils
```

