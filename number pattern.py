import streamlit as st
import random

# 미리 정의된 고정 수열 목록 (총 10개)
# 형식: {
#   '문제 ID': {
#       'sequence': [수열 값], 
#       'blank_index': 정답(빈칸)의 인덱스, 
#       'type': 'arithmetic' 또는 'geometric',
#       'diff_ratio': 공차/공비 값,
#       'rule_desc': "규칙 설명"
#   }
# }
FIXED_SEQUENCES = {
    # 덧셈 (+1, +5, +10) - 5개
    'A1': {'sequence': [10, 11, 12, 13, 14, 15], 'blank_index': 3, 'type': 'arithmetic', 'diff_ratio': 1, 'rule_desc': "1씩 커지는 (더하기) 패턴"},
    'A2': {'sequence': [5, 10, 15, 20, 25, 30], 'blank_index': 2, 'type': 'arithmetic', 'diff_ratio': 5, 'rule_desc': "5씩 커지는 (더하기) 패턴"},
    'A3': {'sequence': [100, 110, 120, 130, 140, 150], 'blank_index': 4, 'type': 'arithmetic', 'diff_ratio': 10, 'rule_desc': "10씩 커지는 (더하기) 패턴"},
    'A4': {'sequence': [23, 25, 27, 29, 31], 'blank_index': 2, 'type': 'arithmetic', 'diff_ratio': 2, 'rule_desc': "2씩 커지는 (더하기) 패턴"},
    'A5': {'sequence': [7, 17, 27, 37, 47, 57], 'blank_index': 3, 'type': 'arithmetic', 'diff_ratio': 10, 'rule_desc': "10씩 커지는 (더하기) 패턴"},
    
    # 곱셈 (x2, x4, x5) - 5개
    'G1': {'sequence': [2, 4, 8, 16, 32], 'blank_index': 3, 'type': 'geometric', 'diff_ratio': 2, 'rule_desc': "2씩 곱하는 패턴"},
    'G2': {'sequence': [3, 15, 75, 375, 1875], 'blank_index': 2, 'type': 'geometric', 'diff_ratio': 5, 'rule_desc': "5씩 곱하는 패턴"},
    'G3': {'sequence': [1, 4, 16, 64, 256], 'blank_index': 3, 'type': 'geometric', 'diff_ratio': 4, 'rule_desc': "4씩 곱하는 패턴"},
    'G4': {'sequence': [5, 10, 20, 40, 80], 'blank_index': 4, 'type': 'geometric', 'diff_ratio': 2, 'rule_desc': "2씩 곱하는 패턴"},
    'G5': {'sequence': [4, 20, 100, 500, 2500], 'blank_index': 3, 'type': 'geometric', 'diff_ratio': 5, 'rule_desc': "5씩 곱하는 패턴"},
}

def start_new_question():
    """미리 정의된 수열 중 하나를 선택하여 새로운 문제를 생성하고 상태를 저장합니다."""
    
    # 사용된 질문 목록 초기화
    if 'used_questions' not in st.session_state:
        st.session_state.used_questions = set()

    # 사용 가능한 질문 목록
    available_q_ids = list(FIXED_SEQUENCES.keys() - st.session_state.used_questions)
    
    # 1. 문제 선택
    if not available_q_ids:
        # 모든 문제를 다 풀었을 경우 (재시작 또는 오류 방지)
        st.session_state.game_state = 'complete' 
        st.error("모든 문제가 소진되었습니다. 게임을 다시 시작해 주세요!")
        return
        
    question_id = random.choice(available_q_ids)
    q_data = FIXED_SEQUENCES[question_id]
    
    # 2. 상태 업데이트
    full_sequence = q_data['sequence']
    blank_index = q_data['blank_index']
    
    # 사용된 질문 목록에 추가
    st.session_state.used_questions.add(question_id)
    
    # 3. 상태 저장
    st.session_state.correct_answer = full_sequence[blank_index]
    st.session_state.pattern_type = q_data['type']
    
    # 마지막 규칙 정보 저장 (규칙 중복 방지 로직은 삭제, 전체 문제 중복 방지 로직으로 대체)
    st.session_state.last_pattern_rule = {'type': q_data['type'], 'rule_value': q_data['diff_ratio']}
    
    display_sequence = list(map(str, full_sequence))
    display_sequence[blank_index] = '?'
    st.session_state.display_sequence_str = " → ".join(display_sequence) 
    st.session_state.full_sequence_str = " → ".join(map(str, full_sequence))
    st.session_state.pattern_rule = q_data['rule_desc']
    
    st.session_state.game_state = 'playing'
    st.session_state.feedback = ""
    st.session_state.input_key = random.random()

def pattern_robot_web_game():
    st.set_page_config(layout="centered")
    
    # --- 제목 및 설명 ---
    st.title("🤖 뿅뿅! 숫자 패턴 로봇 🤖 ")
    st.markdown("##### 3문제를 연속으로 맞히면 게임에서 승리합니다!")
    st.markdown("---")
    
    # 1. 게임 상태 관리 및 초기화
    if 'game_state' not in st.session_state or 'target_score' not in st.session_state:
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.target_score = 3
        st.session_state.input_key = 0 
        st.session_state.last_pattern_rule = None 
        # used_questions 상태는 start_new_question에서 초기화됨
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
            st.session_state.used_questions = set() # 사용된 문제 초기화
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
        # 사용 가능한 문제가 남아있는지 확인
        if len(st.session_state.used_questions) < len(FIXED_SEQUENCES):
             if st.button("✨ 다음 문제 시작", key="new_game_finished_button"):
                start_new_question()
                st.rerun()
        else:
            st.warning("모든 문제가 소진되었습니다. '게임 처음부터 다시 시작' 버튼을 눌러주세요.")


    # --- 점수판 표시 ---
    st.markdown("---")
    st.info(f"🏆 **현재 점수:** {st.session_state.score} / {st.session_state.target_score}점")

if __name__ == "__main__":
    pattern_robot_web_game()
