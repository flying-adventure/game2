import streamlit as st
import random

def generate_arithmetic_sequence(start, diff, length):
    """시작 숫자, 공차(차이), 길이를 이용해 등차수열을 생성합니다. (양수 공차만 사용)"""
    # diff는 무조건 양수이므로 '커지는' 패턴만 생성됨
    sequence = [start + i * diff for i in range(length)]
    return sequence

def generate_geometric_sequence(start, ratio, length):
    """시작 숫자, 공비(비율), 길이를 이용해 등비수열을 생성합니다. (양수 공비만 사용)"""
    sequence = []
    current = start
    
    # 초등학생 수준에 맞게 최대값 제한을 엄격하게 유지
    max_value = 5000 
    
    for _ in range(length):
        current_int = int(current)
        
        # 결과가 너무 커지면 중단 (음수 체크 불필요)
        if current_int > max_value:
             return [] 
        
        # 0 또는 음수 시작 방지
        if current_int <= 0:
            return []
            
        sequence.append(current_int)
        current *= ratio
            
    # 최소 길이를 만족하는지 확인
    if len(sequence) < 4:
        return []
        
    return sequence

def start_new_question():
    """새로운 문제 생성 및 상태 저장을 위한 헬퍼 함수"""
    
    last_pattern_rule = st.session_state.get('last_pattern_rule', None)

    # 1. 패턴 타입 선택 (등차 vs 등비)
    pattern_choices = ['arithmetic', 'geometric']
    pattern_type = random.choice(pattern_choices)

    if pattern_type == 'arithmetic':
        
        # 요청하신 덧셈 규칙만 사용 (2, 5, 10)
        difference_candidates = [2, 5, 10]
        
        # 규칙 중복 방지
        if last_pattern_rule and last_pattern_rule['type'] == 'arithmetic':
            prev_diff = last_pattern_rule['rule_value']
            difference_candidates = [d for d in difference_candidates if d != prev_diff]
            
            if not difference_candidates:
                difference_candidates = [2, 5, 10] # 2, 5, 10이 모두 사용됐다면 다시 선택
        
        start_num = random.randint(1, 100)
        difference = random.choice(difference_candidates)
        sequence_length = random.randint(5, 7)
        
        full_sequence = generate_arithmetic_sequence(start_num, difference, sequence_length)
        pattern_rule_desc = f"{difference}씩 커지는 (더하기) 패턴"
        
        # 유효하지 않은(너무 짧은) 수열 방지 (재시도)
        while len(full_sequence) < 5:
            start_num = random.randint(1, 100)
            difference = random.choice(difference_candidates)
            full_sequence = generate_arithmetic_sequence(start_num, difference, sequence_length)
            
        new_pattern_rule = {'type': 'arithmetic', 'rule_value': difference}
        
    else: # geometric (곱하기 규칙)
        
        # 요청하신 곱셈 규칙만 사용 (2, 4, 5)
        ratio_candidates = [2, 4, 5]
        
        # 규칙 중복 방지
        if last_pattern_rule and last_pattern_rule['type'] == 'geometric':
            prev_ratio = last_pattern_rule['rule_value']
            ratio_candidates = [r for r in ratio_candidates if r != prev_ratio]
            
            if not ratio_candidates:
                 ratio_candidates = [2, 4, 5] # 2, 4, 5가 모두 사용됐다면 다시 선택
        
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
    st.session_state.last_pattern_rule = new_pattern_rule
    
    display_sequence = list(map(str, full_sequence))
    display_sequence[blank_index] = '?'
    st.session_state.display_sequence_str = " → ".join(display_sequence) 
    st.session_state.full_sequence_str = " → ".join(map(str, full_sequence))
    st.session_state.pattern_rule = pattern_rule_desc
    
    st.session_state.game_state = 'playing'
    st.session_state.feedback = ""
    
    # 입력 필드 초기화를 위해 키 값 변경
    st.session_state.input_key = random.random()

def pattern_robot_web_game():
    st.set_page_config(layout="centered")
    
    # --- 제목 및 설명 ---
    st.title("🤖 뿅뿅! 숫자 패턴 로봇 🤖 ")
    st.markdown("##### 3문제를 연속으로 맞히면 게임에서 승리합니다! **더하기(2, 5, 10)와 곱하기(2, 4, 5)** 규칙이 숨어있어요.")
    st.markdown("---")
    
    # 1. 게임 상태 관리 및 초기화
    if 'game_state' not in st.session_state or 'target_score' not in st.session_state:
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.target_score = 3
        st.session_state.input_key = 0 
        st.session_state.last_pattern_rule = None 
        start_new_question() 
        st.rerun()

    # --- 승리 화면 표시 ---
    if st.session_state.game_state == 'victory':
        st.balloons()
        st.success("🏆🏆🏆 게임 승리! 🏆🏆🏆")
        st.header(f"🎉 축하합니다! 목표인 {st.session_state.target_score}문제를 모두 맞혔어요!")
        
        # 힌트 문장 추가
        st.warning("""
        **💡 힌트 문장:** 성벽 위에는 뾰족한 가시 장식이 빽빽하게 솟아 있다.
        \n(이 문장을 메모장 등에 기록해두세요!)
        """)
        
        if st.button("🔄 게임 처음부터 다시 시작", key="reset_game"): 
            st.session_state.game_state = 'init'
            st.session_state.score = 0
            st.session_state.last_pattern_rule = None 
            start_new_question()
            st.rerun()
        
        st.markdown("---")
        st.info(f"🏆 **최종 점수:** {st.session_state.score} / {st.session_state.target_score}점")
        return 


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
        
        # 정답 제출 버튼 - 리런 최소화를 위해 로직 내장
        if st.button("🚀 정답 제출"):
            
            # 1. 정답 확인 로직
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
            
            # 2. 게임 상태 업데이트 및 리런
            st.session_state.feedback_display_text = feedback_text
            st.session_state.game_state = 'finished'
            
            # 승리 조건 즉시 체크
            if st.session_state.score >= st.session_state.target_score:
                st.session_state.game_state = 'victory'
            
            st.rerun() 

    # --- 피드백 처리 및 표시 (Finished 상태) ---
    if st.session_state.game_state == 'finished':
        
        # 피드백 표시
        if st.session_state.feedback_type == 'success':
            st.balloons()
            st.success(st.session_state.feedback_display_text)
        else:
            st.error(st.session_state.feedback_display_text)
        
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
