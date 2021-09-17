# Combine_ali_dirs.sh

> 작성자: 이찬현

- 변수 설정

```shell
tolerance=25	# default = 10
```

> ksponspeech를 진행할 때,
>
> 다량의 학습 데이터를 사용하게 되며, 불가피하게 utt에 비해 ali 파일들이 손상되는데 이때 tolerance를 높여 학습 중단을 방지