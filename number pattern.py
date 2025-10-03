import streamlit as st
import random

def generate_arithmetic_sequence(start, diff, length):
    """시작 숫자, 공차(차이), 길이를 이용해 등차수열을 생성합니다. (더 넓은 범위의 숫자 사용)"""
    sequence = [start + i * diff for i in range(length)]
    return sequence

def generate_geometric_sequence(start, ratio, length):
    """시작 숫자, 공비(비율), 길이를 이용해 등비수열을 생성합니다."""
    # 초등학생에게 너무 어려운 큰 숫자가 나오는 것을 방지하기 위해 최대값 체크
    sequence = []
    current = start
    current_int = int(current) 
    
    for _ in range(length):
        if current_int > 10000 or current_int < -10000: # 결과가 너무 커지거나 작아지면 중단 (범위 확장)
             return []
        sequence.append(current_int)
        current_int *= ratio
        
    return sequence

def start_new_question():
    """새로운 문제 생성 및 상태 저장을 위한 헬퍼 함수 (난이도 상향 및 규칙 중복 방지 로직 포함)"""
    
    # 이전 패턴 규칙 가져오기 (초기화 시에는 None)
    last_pattern_rule = st.session_state.get('last_pattern_rule', None)

    # 1. 패턴 타입 선택 (등차 vs 등비)
    pattern_choices = ['arithmetic', 'geometric']
    
    # 이전 패턴 타입과 동일한 타입이 연속으로 나오지 않게 하거나, 
    # 최소한 같은 규칙(공차/공비)이 반복되지 않게 함.
    if last_pattern_rule and last_pattern_rule['type'] in pattern_choices:
        # 이전에 사용된 패턴 타입을 후보에서 제거하거나, 다른 패턴 타입을 우선 선택
        # 여기서는 같은 타입이 연속될 경우, 아래에서 반드시 다른 공차/공비가 나오도록 보장
        
        # 난이도 조절을 위해 무작위로 선택하되, 아래에서 구체적인 규칙을 조정
        pattern_type = random.choice(pattern_choices)
    else:
        pattern_type = random.choice(pattern_choices)


    if pattern_type == 'arithmetic':
        
        difference_candidates = [1, 2, 3, 5, 10, 15, -1, -2, -5, -10]
        
        # 이전 규칙이 등차수열이었고, 공차가 동일한 경우 제외
        if last_pattern_rule and last_pattern_rule['type'] == 'arithmetic':
            # 이전 공차와 동일한 공차를 후보에서 제거
            prev_diff = last_pattern_rule['rule_value']
            difference_candidates = [d for d in difference_candidates if d != prev_diff]
            
            # 만약 모든 후보가 제거되었다면 (발생 가능성 낮음), 강제로 다른 값을 사용
            if not difference_candidates:
                difference_candidates = [20, -20] # 매우 다른 값 추가
        
        start_num = random.randint(1, 50) 
        difference = random.choice(difference_candidates)
        sequence_length = random.randint(5, 7)
        
        full_sequence = generate_arithmetic_sequence(start_num, difference, sequence_length)
        pattern_rule_desc = f"{abs(difference)}씩 {'커지는' if difference > 0 else '작아지는'} (더하기/빼기) 패턴"
        
        # 유효하지 않은(너무 짧은) 수열 방지
        while len(full_sequence) < 5:
            start_num = random.randint(1, 50)
            difference = random.choice(difference_candidates)
            full_sequence = generate_arithmetic_sequence(start_num, difference, sequence_length)
        
        new_pattern_rule = {'type': 'arithmetic', 'rule_value': difference}
        
    else: # geometric (곱하기 규칙)
        
        ratio_candidates = [2, 3, 4]
        
        # 이전 규칙이 등비수열이었고, 공비가 동일한 경우 제외
        if last_pattern_rule and last_pattern_rule['type'] == 'geometric':
            prev_ratio = last_pattern_rule['rule_value']
            ratio_candidates = [r for r in ratio_candidates if r != prev_ratio]
            
            # 만약 모든 후보가 제거되었다면, 강제로 다시 선택 (등비수열은 후보가 적으므로, 이럴 경우 등차수열로 강제 변경도 고려 가능하나 여기서는 안전하게 재선택)
            if not ratio_candidates:
                 ratio_candidates = [2, 3, 4] 
        
        start_num = random.randint(1, 10) 
        ratio = random.choice(ratio_candidates)
        sequence_length = random.randint(4, 6) 
        
        full_sequence = []
        # 유효한 수열이 생성될 때까지 반복
        while len(full_sequence) < 4: 
            full_sequence = generate_geometric_sequence(start_num, ratio, sequence_length)
            if len(full_sequence) < 4: # 생성 실패 (숫자가 너무 커지거나 짧아짐) 시 다시 시도
                start_num = random.randint(1, 10)
        
        pattern_rule_desc = f"{ratio}씩 곱하는 패턴"
        new_pattern_rule = {'type': 'geometric', 'rule_value': ratio}


    # 빈칸 위치를 무작위로 선택
    blank_index = random.randint(2, len(full_sequence) - 2)
    
    # 상태 저장
    st.session_state.correct_answer = full_sequence[blank_index]
    st.session_state.pattern_type = pattern_type
    
    # 다음에 사용할 수 있도록 현재 규칙 저장
    st.session_state.last_pattern_rule = new_pattern_rule 
    
    display_sequence = list(map(str, full_sequence))
    display_sequence[blank_index] = '?'
    st.session_state.display_sequence_str = " → ".join(display_sequence) 
    st.session_state.full_sequence_str = " → ".join(map(str, full_sequence))
    st.session_state.pattern_rule = pattern_rule_desc # 규칙 설명 저장
    
    st.session_state.game_state = 'playing'
    st.session_state.feedback = ""
    st.session_state.submitted = False
    
    # 입력 필드 초기화를 위해 키 값 변경
    st.session_state.input_key = random.random()

def pattern_robot_web_game():
    st.set_page_config(layout="centered")
    
    # --- 제목 및 설명 ---
    st.title("🤖 뿅뿅! 숫자 패턴 로봇 (난이도 UP! ⬆️)")
    st.markdown("##### 3문제를 연속으로 맞히면 게임에서 승리합니다! 더하기/빼기 외에 **곱하기 규칙**도 숨어있어요.")
    st.markdown("---")
    
    # 1. 게임 상태 관리 및 초기화
    if 'game_state' not in st.session_state or 'target_score' not in st.session_state:
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.target_score = 3
        st.session_state.difficulty = 1 
        st.session_state.input_key = 0 
        # last_pattern_rule 초기화 추가
        st.session_state.last_pattern_rule = None 
        start_new_question() 
        st.rerun()

    # '다시 시작' 버튼을 눌렀을 때 초기화 (Victory 화면에서 사용)
    if st.session_state.game_state == 'victory' and st.button("🔄 게임 처음부터 다시 시작", key="reset_game"): 
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.last_pattern_rule = None # 규칙 초기화
        start_new_question()
        st.rerun()

    # --- 승리 화면 표시 (최우선) ---
    if st.session_state.game_state == 'victory':
        st.balloons()
        st.success("🏆🏆🏆 게임 승리! 🏆🏆🏆")
        st.header(f"🎉 축하합니다! 목표인 {st.session_state.target_score}문제를 모두 맞혔어요!")
        st.markdown("게임을 다시 시작하려면 위에 있는 **'게임 처음부터 다시 시작'** 버튼을 눌러주세요.")
        st.markdown("---")
        st.info(f"🏆 **최종 점수:** {st.session_state.score} / {st.session_state.target_score}점")
        return # 승리 상태에서는 문제 표시를 건너뜀


    # --- 문제 표시 ---
    if st.session_state.game_state == 'playing':
        st.header(f"👀 문제 패턴: ({st.session_state.score + 1}번째 문제)")
        st.success(f"## {st.session_state.display_sequence_str}")
        
        # --- 사용자 입력 ---
        user_guess = st.number_input(
            "정답이라고 생각하는 숫자를 입력하세요:", 
            key=st.session_state.input_key, 
            step=1, 
            format="%d"
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
            st.session_state.feedback = f"🎉 **정답입니다!**"
            st.session_state.feedback_type = 'success'
        else:
            st.session_state.feedback = f"❌ **틀렸어요.** 정답은 **{st.session_state.correct_answer}** 였어요."
            st.session_state.feedback_type = 'error'
        
        # 피드백 내용 구성
        feedback_text = st.session_state.feedback
        feedback_text += f"\n\n**✅ 규칙:** 이 패턴의 규칙은 **{st.session_state.pattern_rule}** 이랍니다."
        feedback_text += f"\n\n**전체 패턴:** {st.session_state.full_sequence_str}"

        # 피드백 표시
        if st.session_state.feedback_type == 'success':
            st.balloons()
            st.success(feedback_text)
        else:
            st.error(feedback_text)
        
        st.session_state.game_state = 'finished'
        
        # 승리 조건 즉시 체크 및 리런 
        if st.session_state.score >= st.session_state.target_score:
            st.session_state.game_state = 'victory'
            st.rerun()


    # 'finished' 상태일 때 다음 문제 또는 승리 화면 표시
    if st.session_state.game_state == 'finished':
        
        # 새로운 문제 시작 버튼 표시
        st.markdown("---")
        if st.button("✨ 다음 문제 시작", key="new_game_finished_button"):
            start_new_question()
            st.rerun()

    # --- 점수판 표시 ---
    st.markdown("---")
    st.info(f"🏆 **현재 점수:** {st.session_state.score} / {st.session_state.target_score}점")

if __name__ == "__main__":
    pattern_robot_web_game()
