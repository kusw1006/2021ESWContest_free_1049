# 통화 시스템 분석
## 유선 전화 환경
- E1(ITU-T G.723) 사용
> 샘플링 주파수 : 8kHz
> <br>채널 대역폭 : DS0 64Kbps
> <br>채널 개수 : 32개 (2048Mbps)

- 음성 전달 방식
아날로그 신호 -> 표본화 -> 양자화 -> 부호화(아날로그 부호화)

- 표본화, 양자화, 부호화
> 사람의 음성 주파수 300Hz ~ 3400Hz이므로 최대 주파수는 나이퀴스트 법칙에 의해 6800Hz
><br>잡음을 막기 위해서 8Khz를 사용
><br>이후 양자화와 부호화 과정을 거치는데 이 때 PCM 펄스 부호 변조 신호는 8비트
><br>64Kbps의 대역폭 필요

- PSTN 방식으로 PCM 데이터 전달

- 유선 전화가 음질이 안좋은 이유 -> 아날로그를 활용한 통신이라 감쇠현상 발생

## 무선 전화 환경
- 위 방식과 동일하지만 디지털 부호화를 거치고 PSDN 방식으로 데이터 전달

## 이후 처리 방식
- 부호화 된 디지털 신호를 DAC 과정을 거쳐 스피커로 출력한다.
- 일반 전화 샘플링 8000Hz, VoIP 16000Hz