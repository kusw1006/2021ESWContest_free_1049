# 필요 라이브러리
> requirements.txt 참고



# prepare_data

> AI HUB 감정 분석 데이터셋 이용
>
> 국립국어원 모두의 말뭉치 구어체 말뭉치 이용
- 큰/작은 따옴표 제거 과정 필수
- "불안 " -> "불안"으로 변경해줄 필요있음
- csv 파일은 문장 | label로 구성되어있으면 됨
- AI HUB 데이터셋에 없는 평서문을 추가하기 위해 모두의 말뭉치 구어체 말뭉치 이용



### Label

```python
# 0: 평서문, 불안, 당황
# 1: 기쁨, 
# 2: 분노, 상처
# 3: 슬픔
```



# train.py

```python
data_train = BERTDataset(dataset_train_list, 0, 1, tok, max_len, True, False)
```

> 0 = 문장
>
> 1 = label

