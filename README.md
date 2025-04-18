# 영어 단어 스피드 퀴즈 앱

이 앱은 eng.md 파일에서 영어 단어와 한국어 뜻을 추출하여 스피드 퀴즈 형태로 제공합니다.

## 기능

- 영어→한국어 또는 한국어→영어 모드 선택 가능
- 문제 수 조절 가능 (5~50문제)
- 퀴즈 진행 상황 및 소요 시간 표시
- 단어장 전체 보기 기능

## 실행 방법

1. 필요한 패키지 설치:
```
pip install -r requirements.txt
```

2. 스트림릿 앱 실행:
```
streamlit run app.py
```

3. 웹 브라우저에서 앱 확인 (기본 URL: http://localhost:8501)

## 퀴즈 모드

- **영어→한국어**: 영어 단어가 제시되면 한국어 뜻을 입력해야 합니다.
- **한국어→영어**: 한국어 뜻이 제시되면 영어 단어를 입력해야 합니다.

## 점수 계산

- 입력한 답변이 정답에 포함되어 있으면 정답으로 인정됩니다.
- 최종 점수와 소요 시간은 퀴즈 종료 후 확인할 수 있습니다. 