import streamlit as st
import random

def generate_arithmetic_sequence(start, diff, length):
    """시작 숫자, 공차(차이), 길이를 이용해 등차수열을 생성합니다. (더 넓은 범위의 숫자 사용)"""
    sequence = [start + i * diff for i in range(length)]
    return sequence

# 난이도 상향을 위해 추가된 함수: 등비수열 생성
def generate_geometric_sequence(start, ratio, length):
    """시작 숫자, 공비(비율), 길이를 이용해 등비수열을 생성합니다."""
    # 초등학생에게 너무 어려운 큰 숫자가 나오는 것을 방지하기 위해 최대값 체크
    sequence = []
    current = start
    for _ in range(length):
        if current > 1000 or current < 0: # 결과가 너무 커지거나 작아지면 중단
             return []
        sequence.append(current)
        current *= ratio
    return sequence

def start_new_question():
    """새로운 문제 생성 및 상태 저장을 위한 헬퍼 함수 (난이도 상향 로직 포함)"""
    
    # 등차수열과 등비수열 중 무작위로 선택
    pattern_type = random.choice(['arithmetic', 'geometric'])

    if pattern_type == 'arithmetic':
        # 난이도 상향: 시작 숫자의 범위를 넓힘, 공차에 큰 숫자 추가
        start_num = random.randint(1, 20)
        difference = random.choice([1, 2, 5, 10]) 
        sequence_length = random.randint(5, 7)
        full_sequence = generate_arithmetic_sequence(start_num, difference, sequence_length)
        pattern_rule = f"{abs(difference)}씩 {'커지는' if difference > 0 else '작아지는'} (더하기/빼기) 패턴"
        
    else: # geometric (곱하기 규칙)
        # 난이도 상향: 곱하기 규칙 추가 (쉬운 정수 비율만 사용)
        start_num = random.randint(1, 5)
        ratio = random.choice([2, 3, 4]) # 공비는 2, 3, 4 중 하나
        sequence_length = random.randint(4, 6) # 등비수열은 길이가 짧아도 숫자가 빨리 커짐
        
        full_sequence = []
        # 유효한 수열이 생성될 때까지 반복
        while len(full_sequence) < 4: 
            full_sequence = generate_geometric_sequence(start_num, ratio, sequence_length)
            if len(full_sequence) < 4: # 생성 실패 (숫자가 너무 커짐) 시 다시 시도
                start_num = random.randint(1, 5)
        
        pattern_rule = f"{ratio}씩 곱하는 패턴"


    # 빈칸 위치를 무작위로 선택
    blank_index = random.randint(2, len(full_sequence) - 2)
    
    # 상태 저장
    st.session_state.correct_answer = full_sequence[blank_index]
    st.session_state.difference = difference if pattern_type == 'arithmetic' else ratio # 규칙 저장 (등차일 경우 차이, 등비일 경우 비율)
    st.session_state.pattern_type = pattern_type
    
    display_sequence = list(map(str, full_sequence))
    display_sequence[blank_index] = '?'
    st.session_state.display_sequence_str = " -> ".join(display_sequence)
    st.session_state.full_sequence_str = " -> ".join(map(str, full_sequence))
    st.session_state.pattern_rule = pattern_rule # 규칙 설명 저장
    
    st.session_state.game_state = 'playing'
    st.session_state.feedback = ""
    st.session_state.submitted = False
    
    # 입력 필드 초기화를 위해 키 값 변경
    st.session_state.input_key = random.random()

def pattern_robot_web_game():
    st.set_page_config(layout="centered")
    
    # --- 제목 및 설명 ---
    st.title("🤖 뿅뿅! 숫자 패턴 로봇")
    st.markdown("##### 3문제를 연속으로 맞히면 게임에서 승리합니다! 더하기와 곱하기 규칙이 숨어있어요.")
    st.markdown("---")
    
    # 1. 게임 상태 관리 및 초기화
    if 'game_state' not in st.session_state or 'target_score' not in st.session_state:
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.target_score = 3
        st.session_state.difficulty = 1 
        st.session_state.input_key = 0 
        start_new_question() 
        st.rerun()

    # '다시 시작' 버튼을 눌렀을 때 초기화 (Victory 화면에서 사용)
    if st.session_state.game_state == 'victory' and st.button("🔄 게임 처음부터 다시 시작", key="reset_game"): 
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        start_new_question()
        st.rerun()

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
        
        # 피드백 내용 구성 (패턴 규칙 설명은 저장된 rule 사용)
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
        st.balloons()
        st.success("🏆🏆🏆 게임 승리! 🏆🏆🏆")
        st.header(f"🎉 축하합니다! 목표인 {st.session_state.target_score}문제를 모두 맞혔어요!")
        st.markdown("게임을 다시 시작하려면 위에 있는 **'게임 처음부터 다시 시작'** 버튼을 눌러주세요.")


    # --- 점수판 표시 ---
    st.markdown("---")
    st.info(f"🏆 **현재 점수:** {st.session_state.score} / {st.session_state.target_score}점")

if __name__ == "__main__":

    pattern_robot_web_game()
