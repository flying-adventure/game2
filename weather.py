import streamlit as st
import random

# 전역 상수 설정
WEATHER_EMOJIS = ['☀️', '🌧️', '☁️']
HISTORY_LENGTH = 6  # 과거 6일
TARGET_SCORE = 3

# 6가지 명확한 시퀀스 규칙 정의
# 키(Key): 패턴 이름, 값(Value): [시퀀스 리스트, 다음 예측 날씨, 규칙 설명]
RULES = {
    "R1_비비맑음반복": [['🌧️', '🌧️', '☀️'], '🌧️', "비(2회) - 맑음(1회) 패턴이 반복됩니다."],
    "R2_구비맑음반복": [['☁️', '🌧️️', '☀️'], '☁️', "구름 - 비 - 맑음 패턴이 반복됩니다."],
    "R3_맑구름반복": [['☀️', '☁️'], '☀️', "맑음 - 구름 패턴이 반복됩니다."],
    "R4_비구름반복": [['🌧️', '☁️', '☁️'], '🌧️', "비(1회) - 구름(2회) 패턴이 반복됩니다."],
    "R5_역순구름": [['☁️', '☀️', '🌧️'], '☁️', "구름 - 맑음 - 비의 역순 패턴이 반복됩니다."],
    "R6_비맑음맑음": [['🌧️', '☀️', '☀️'], '🌧️', "비(1회) - 맑음(2회) 패턴이 반복됩니다."],
}

def generate_weather_history(last_rule_name):
    """
    6가지 규칙 중 하나를 선택하여 과거 6일의 날씨 이력을 생성합니다.
    (이전에 사용된 규칙은 제외하고 선택합니다.)
    """
    
    # 사용 가능한 규칙 목록을 만듭니다 (이전에 사용된 규칙은 제외).
    available_rules = list(RULES.keys())
    
    # 규칙이 2개 이상일 경우에만 마지막 규칙을 제외
    if last_rule_name and len(available_rules) > 1:
        # 안전하게 제거: last_rule_name이 실제로 available_rules에 있는지 확인
        if last_rule_name in available_rules:
             available_rules.remove(last_rule_name)
    
    # 1. 사용할 규칙 무작위 선택
    rule_name = random.choice(available_rules)
    sequence, _, _ = RULES[rule_name]
    
    sequence_len = len(sequence)
    
    # 2. 과거 6일 이력 생성
    history = []
    # 패턴을 HISTORY_LENGTH 만큼 반복하여 생성
    for i in range(HISTORY_LENGTH):
        history.append(sequence[i % sequence_len])
        
    # 3. 정답 (내일 날씨) 결정
    # 다음 순서는 패턴의 길이(sequence_len)로 나눈 나머지 인덱스
    correct_forecast = sequence[HISTORY_LENGTH % sequence_len] 
    
    return history, correct_forecast, rule_name


def get_forecast_and_rule(correct_forecast, rule_name):
    """결정된 규칙 정보를 반환합니다."""
    
    _, _, rule_description = RULES[rule_name]
    
    # 1. 정답 날씨의 확률을 100%로 설정
    probabilities = {correct_forecast: 1.0}
    
    # 2. 나머지 날씨를 찾아 0%로 설정
    other_emojis = [w for w in WEATHER_EMOJIS if w != correct_forecast]
    
    for emoji in other_emojis:
        probabilities[emoji] = 0.0

    # 3. 확률이 0보다 큰 값만 남김
    final_probabilities = {k: v for k, v in probabilities.items() if v > 0}
    
    return correct_forecast, final_probabilities, rule_description


def start_new_question():
    """새로운 문제 생성 및 상태 저장을 위한 헬퍼 함수"""
    
    # 마지막으로 사용된 규칙 이름을 가져옵니다. (초기 실행 시는 None)
    last_rule_name = st.session_state.get('last_rule_name')

    weather_history, correct_forecast_raw, rule_name = generate_weather_history(last_rule_name)
    
    # 새로운 규칙 이름을 'last_rule_name'으로 저장 (중복 방지)
    st.session_state.last_rule_name = rule_name
    
    correct_forecast, probabilities, rule_description = get_forecast_and_rule(
        correct_forecast_raw, rule_name)
    
    # 상태 저장
    st.session_state.correct_answer = correct_forecast
    st.session_state.weather_history = weather_history
    st.session_state.probabilities = probabilities
    st.session_state.rule_description = rule_description
    
    st.session_state.game_state = 'playing'
    st.session_state.feedback = ""
    st.session_state.input_key = random.random()

def pattern_robot_web_game():
    st.set_page_config(layout="centered")
    
    # --- 제목 및 설명 ---
    st.title("☀️ 날씨 트렌드 예측 로봇 (패턴 찾기)")
    st.markdown(f"##### **과거 6일**의 날씨를 보고 다음 날씨를 예측하세요.  **{TARGET_SCORE}번** 정답을 맞히면 승리합니다.")
    st.markdown("---")
    
    # 1. 게임 상태 관리 및 초기화
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.target_score = TARGET_SCORE
        # last_rule_name은 start_new_question에서 초기화됨
        start_new_question() 
        st.rerun()

    # '다시 시작' 버튼 로직 (승리 후)
    if st.session_state.game_state == 'victory' and st.button("🔄 게임 처음부터 다시 시작", key="reset_game"): 
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        del st.session_state['last_rule_name'] # 규칙 중복 방지 기록 초기화
        start_new_question()
        st.rerun()

    # --- 문제 표시 ---
    if st.session_state.game_state == 'playing':
        st.header(f"👀 과거 {HISTORY_LENGTH}일간의 날씨 트렌드: ({st.session_state.score + 1}번째 문제)")
        
        # 날씨 이모지 크기를 키워서 표시 
        history_str_large = ' '.join([f'<span style="font-size: 40px;">{emo}</span>' for emo in st.session_state.weather_history])
        st.markdown(f"**과거 날씨 (6일 전 → 어제):**")
        st.markdown(history_str_large, unsafe_allow_html=True)
        
        st.success(f"## 내일 날씨는?")
        
        # --- 사용자 예측 (입력) ---
        user_guess = st.radio(
            "내일 날씨를 선택하세요:", 
            WEATHER_EMOJIS,
            key=st.session_state.input_key
        )
        
        # 정답 제출 버튼
        if st.button("🚀 정답 제출"):
            st.session_state.user_guess = user_guess
            st.session_state.game_state = 'checking'
            st.rerun() 

    # --- 피드백 처리 및 표시 ---
    if st.session_state.game_state == 'checking':
        
        user_guess = st.session_state.user_guess
        
        # 3. 피드백 및 결과 확인
        is_correct = (user_guess == st.session_state.correct_answer)
        if is_correct:
            st.session_state.score += 1
            st.session_state.feedback = f"🎉 **정답입니다!** 패턴을 정확히 찾았어요!"
            st.session_state.feedback_type = 'success'
        else:
            st.session_state.feedback = f"❌ **틀렸어요.** 정답은 **{st.session_state.correct_answer}** 였어요."
            st.session_state.feedback_type = 'error'
        
        # 피드백 내용 구성 
        feedback_text = st.session_state.feedback
        feedback_text += f"\n\n**✅ 규칙:** 이 문제에 숨어있던 패턴은 **{st.session_state.rule_description}** 였습니다."
        
        # 피드백 표시
        if st.session_state.feedback_type == 'success':
            st.balloons()
            st.success(feedback_text)
        else:
            st.error(feedback_text)
        
        st.session_state.game_state = 'finished'
    
    # 'finished' 상태일 때 다음 문제 또는 승리 화면 표시
    if st.session_state.game_state == 'finished':
        
        # 승리 조건 체크
        if st.session_state.score >= st.session_state.target_score:
            st.session_state.game_state = 'victory'
            st.rerun() 
        else:
            # 새로운 문제 시작 버튼 표시
            st.markdown("---")
            if st.button("✨ 새로운 문제 시작", key="new_game_finished_button"):
                start_new_question()
                st.rerun()

    # --- 승리 화면 ---
    if st.session_state.game_state == 'victory':
        st.success("🏆🏆🏆 게임 승리! 🏆🏆🏆")
        st.header(f"🎉 축하합니다! 목표인 {st.session_state.target_score}문제를 모두 맞혔어요!")
        
        # 힌트 문구 출력 위치를 명확히 했습니다.
        st.warning("""
        **💡 힌트 문장:** 붉은 용암빛이 성문의 돌 틈새로 새어 나온다.
        """)
        
        # 힌트 문구가 출력된 후, 안내 문구를 추가합니다.
        st.markdown(f"""
        (이 문장을 메모장 등에 기록해두세요!)
        \n게임을 다시 시작하려면 위에 있는 **'게임 처음부터 다시 시작'** 버튼을 눌러주세요.
        """)


    # --- 점수판 표시 ---
    st.markdown("---")
    st.info(f"🏆 **현재 점수:** {st.session_state.score} / {st.session_state.target_score}점")

if __name__ == "__main__":
    pattern_robot_web_game()
