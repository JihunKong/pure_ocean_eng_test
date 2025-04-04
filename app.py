import streamlit as st
import pandas as pd
import re
import random
import time
from datetime import datetime

# 제목 설정
st.title('영어 단어 스피드 퀴즈')

# 마크다운 파일 로드 및 데이터 추출 함수
@st.cache_data
def load_vocabulary():
    with open('eng.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 정규표현식으로 테이블 파싱
    pattern = r'\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|'
    matches = re.findall(pattern, content)
    
    # 데이터프레임 생성
    df = pd.DataFrame(matches, columns=['번호', '영어 단어', '한국어 뜻'])
    
    # 공백 제거
    df['영어 단어'] = df['영어 단어'].str.strip()
    df['한국어 뜻'] = df['한국어 뜻'].str.strip()
    
    return df

# 데이터 불러오기
vocab_df = load_vocabulary()

# 세션 상태 초기화
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'quiz_words' not in st.session_state:
    st.session_state.quiz_words = []
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'quiz_in_progress' not in st.session_state:
    st.session_state.quiz_in_progress = False
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 20
if 'time_limit_mode' not in st.session_state:
    st.session_state.time_limit_mode = False
if 'time_limit' not in st.session_state:
    st.session_state.time_limit = 60
if 'records' not in st.session_state:
    st.session_state.records = []
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'time_expired' not in st.session_state:
    st.session_state.time_expired = False

# 사이드바에 설정
st.sidebar.header("퀴즈 설정")
quiz_mode = st.sidebar.radio("퀴즈 모드 선택", 
                             ["영어 → 한국어", "한국어 → 영어"],
                             index=0)
total_questions = st.sidebar.slider("문제 수", min_value=5, max_value=50, value=20, step=5)
st.session_state.total_questions = total_questions

# 시간 제한 모드 설정
st.session_state.time_limit_mode = st.sidebar.checkbox("시간 제한 모드", value=False)
if st.session_state.time_limit_mode:
    st.session_state.time_limit = st.sidebar.slider("제한 시간(초)", min_value=30, max_value=300, value=60, step=10)

# 이름 입력
player_name = st.sidebar.text_input("플레이어 이름", value="Player")

# 퀴즈 시작 함수
def start_quiz():
    st.session_state.score = 0
    st.session_state.current_question = 0
    # 단어 중복 제거 후 무작위 추출
    all_words = vocab_df.drop_duplicates(subset=['영어 단어'])
    st.session_state.quiz_words = all_words.sample(st.session_state.total_questions).reset_index(drop=True)
    st.session_state.start_time = time.time()
    st.session_state.quiz_in_progress = True
    st.session_state.time_expired = False

# 퀴즈 종료 함수
def end_quiz():
    st.session_state.quiz_in_progress = False
    elapsed_time = time.time() - st.session_state.start_time
    st.success(f"퀴즈 종료! 점수: {st.session_state.score}/{st.session_state.total_questions}")
    st.info(f"소요 시간: {elapsed_time:.2f}초")
    
    # 기록 저장
    record = {
        "이름": player_name,
        "모드": quiz_mode,
        "점수": st.session_state.score,
        "총 문제": st.session_state.total_questions,
        "소요 시간": f"{elapsed_time:.2f}초",
        "정답률": f"{(st.session_state.score / st.session_state.total_questions) * 100:.1f}%",
        "날짜": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.records.append(record)

# 정답 제출 콜백 함수
def submit_answer():
    try:
        current_word = st.session_state.quiz_words.iloc[st.session_state.current_question]
        
        if quiz_mode == "영어 → 한국어":
            answer = current_word['한국어 뜻']
            user_answer = st.session_state.get(f"answer_{st.session_state.current_question}", "")
        else:
            answer = current_word['영어 단어']
            user_answer = st.session_state.get(f"answer_{st.session_state.current_question}", "")
        
        if user_answer.strip().lower() in answer.lower():
            st.session_state.score += 1
            st.session_state.answer_correct = True
        else:
            st.session_state.answer_correct = False
            st.session_state.correct_answer = answer
        
        st.session_state.current_question += 1
        st.session_state.submitted = True
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
        st.session_state.submitted = False

# 스타트 버튼
if not st.session_state.quiz_in_progress:
    if st.button("퀴즈 시작하기"):
        start_quiz()

# 퀴즈 진행
if st.session_state.quiz_in_progress:
    # 시간 제한 모드 타이머 표시
    if st.session_state.time_limit_mode:
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = max(0, st.session_state.time_limit - elapsed_time)
        time_progress = 1 - (remaining_time / st.session_state.time_limit)
        
        # 진행바 색상 변경 (시간이 적을수록 빨간색으로)
        if remaining_time < 10:
            st.markdown(
                f"""
                <div style="background-color: #ff4b4b; height: 20px; width: {time_progress*100}%;
                border-radius: 3px;"></div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.progress(time_progress)
        
        st.write(f"남은 시간: {int(remaining_time)}초")
        
        # 시간 초과 확인
        if remaining_time <= 0 and not st.session_state.time_expired:
            st.error("시간 초과!")
            st.session_state.time_expired = True
            end_quiz()
    
    if st.session_state.current_question < st.session_state.total_questions:
        # 진행 상황 표시
        st.progress(st.session_state.current_question / st.session_state.total_questions)
        st.write(f"진행 상황: {st.session_state.current_question + 1}/{st.session_state.total_questions}")
        
        # 현재 단어 정보
        current_word = st.session_state.quiz_words.iloc[st.session_state.current_question]
        
        # 퀴즈 출제 방식
        if quiz_mode == "영어 → 한국어":
            question = current_word['영어 단어']
            st.subheader(f"Q: {question}")
            st.text_input("한국어 뜻을 입력하세요:", key=f"answer_{st.session_state.current_question}", 
                         on_change=submit_answer)
        else:
            question = current_word['한국어 뜻']
            st.subheader(f"Q: {question}")
            st.text_input("영어 단어를 입력하세요:", key=f"answer_{st.session_state.current_question}", 
                         on_change=submit_answer)
        
        # 제출 버튼 (추가적인 옵션으로 제공)
        st.button("제출", key=f"submit_{st.session_state.current_question}", on_click=submit_answer)
        
        # 정답/오답 피드백 표시
        if st.session_state.submitted:
            if st.session_state.answer_correct:
                st.success("정답입니다! 👍")
            else:
                st.error(f"오답입니다. 정답은 '{st.session_state.correct_answer}' 입니다.")
            st.session_state.submitted = False
    else:
        end_quiz()

# 퀴즈 중간에 포기 버튼
if st.session_state.quiz_in_progress:
    if st.button("퀴즈 포기"):
        end_quiz()

# 점수 표시
if st.session_state.quiz_in_progress:
    st.sidebar.metric("현재 점수", st.session_state.score)

# 단어장 전체 보기 옵션
if st.sidebar.checkbox("단어장 전체 보기"):
    st.dataframe(vocab_df)

# 기록 보기
if st.sidebar.checkbox("기록 보기"):
    if st.session_state.records:
        records_df = pd.DataFrame(st.session_state.records)
        st.subheader("퀴즈 기록")
        st.dataframe(records_df)
    else:
        st.info("아직 기록이 없습니다.") 
