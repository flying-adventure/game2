import streamlit as st
import random
import pandas as pd
import itertools

# 전역 상수 및 규칙 설정
TARGET_SCORE = 4 # 총 4문제를 맞춰야 승리 (빨강, 노랑, 파랑 + 혼합)
SCALE_FACTOR = 800 # 크기에 곱해지는 가중치

# 색깔별 기본 보너스 정의
COLOR_BONUS = {
    '🔴 빨강': 1500,
    '🔵 파랑': 1000,
    '🟡 노랑': 500,
}
REQUIRED_COLORS = list(COLOR_BONUS.keys()) 

def calculate_price(size, colors):
    """크기 점수와 1~2개의 색깔 이름을 이용해 가격을 계산하는 공식"""
    
    # colors는 단일 색상 이름 문자열 또는 [색상1, 색상2] 리스트일 수 있음
    if isinstance(colors, str):
        color_list = [colors]
    else:
        color_list = colors
        
    total_bonus = 0
    for color_name in color_list:
        total_bonus += COLOR_BONUS.get(color_name, 0)
        
    # 정답 공식: 가격 = (크기 점수 * 가중치) + 총 색깔 보너스
    price = (size * SCALE_FACTOR) + total_bonus
    return price, total_bonus

def generate_step_data(step):
    """단계별로 필요한 예시 데이터와 문제 데이터를 생성합니다."""
    
    examples = []
    
    if step == 1:
        # 목표: SCALE_FACTOR (크기 가중치)와 빨강 보너스 찾기
        required_color = '🔴 빨강'
        sizes = random.sample(range(4, 10), 3)
        for size in sizes:
            price, _ = calculate_price(size, required_color)
            examples.append({'size': size, 'color': required_color, 'price': price})
        
        problem_size = random.choice([2, 10])
        problem_color = required_color
        step_hint = "빨간색 물건들만 보고 **'크기 점수 가중치'**와 **'빨강 보너스'**를 찾아내세요."
        
    elif step == 2:
        # 목표: 노랑 보너스 찾기 
        required_color = '🟡 노랑'
        examples.append({'size': 7, 'color': '🔴 빨강', 'price': calculate_price(7, '🔴 빨강')[0]})
        examples.append({'size': 7, 'color': '🟡 노랑', 'price': calculate_price(7, '🟡 노랑')[0]})
        examples.append({'size': 5, 'color': '🔴 빨강', 'price': calculate_price(5, '🔴 빨강')[0]})

        problem_size = random.randint(4, 9)
        problem_color = required_color
        step_hint = f"크기 가중치({SCALE_FACTOR}원)와 빨강 보너스를 이용해 **'노랑 보너스'**를 찾아내세요."

    elif step == 3:
        # 목표: 파랑 보너스 찾기
        required_color = '🔵 파랑'
        examples.append({'size': 8, 'color': '🔴 빨강', 'price': calculate_price(8, '🔴 빨강')[0]})
        examples.append({'size': 8, 'color': '🟡 노랑', 'price': calculate_price(8, '🟡 노랑')[0]})
        examples.append({'size': 6, 'color': '🔵 파랑', 'price': calculate_price(6, '🔵 파랑')[0]})

        problem_size = random.randint(3, 10)
        problem_color = required_color
        step_hint = "크기 가중치와 이미 알고 있는 색깔 보너스를 활용해 **'파랑 보너스'**를 찾아내세요."
        
    elif step == 4:
        # 목표: 두 가지 색깔 혼합 문제 (최종 점검)
        
        # 3가지 색깔의 예시 모두 제시
        all_colors = REQUIRED_COLORS
        for color in all_colors:
             examples.append({'size': 7, 'color': color, 'price': calculate_price(7, color)[0]})
        
        # 문제: 두 가지 색깔을 무작위로 선택하여 혼합
        mixed_colors = random.sample(REQUIRED_COLORS, 2)
        
        problem_size = random.randint(4, 9)
        problem_color = mixed_colors # 이제 problem_color는 리스트가 됨
        
        step_hint = "모든 색깔의 보너스를 합하고 크기 가중치를 적용하여, **두 가지 색깔이 혼합된 물건**의 가격을 예측하세요!"
        
    else:
        return [], 0, "", 0, "오류: 게임 단계 초과"

    # 최종 문제의 정답 계산
    problem_price, _ = calculate_price(problem_size, problem_color)
    
    return examples, problem_size, problem_color, problem_price, step_hint

def start_new_question():
    """새로운 문제 생성 및 상태 저장을 위한 헬퍼 함수"""
    
    current_step = st.session_state.get('step', 1)
    
    examples, problem_size, problem_color, problem_price, step_hint = generate_step_data(current_step)
    
    # 문제 색깔 표시용 문자열 생성 (단일 색상 or 혼합 색상)
    if isinstance(problem_color, list):
        display_color = f"{problem_color[0]} + {problem_color[1]}"
    else:
        display_color = problem_color
    
    # 상태 저장
    st.session_state.step = current_step
    st.session_state.examples = examples
    st.session_state.correct_answer = problem_price
    st.session_state.problem_size = problem_size
    st.session_state.problem_color = problem_color # 실제 계산에 사용
    st.session_state.display_color = display_color # 표시용
    st.session_state.step_hint = step_hint
    
    st.session_state.game_state = 'playing'
    st.session_state.feedback = ""
    st.session_state.input_key = random.random() 

def price_prediction_game():
    st.set_page_config(layout="centered")
    
    # --- 제목 및 설명 ---
    st.title("💰 가격 예측 훈련 로봇 (회귀 분석)")
    st.markdown(f"##### 단계별로 숨겨진 가격 규칙을 유추해 보세요. **총 {TARGET_SCORE}단계**를 통과하면 승리합니다.")
    st.markdown("---")
    
    # 1. 게임 상태 관리 및 초기화
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.step = 1
        st.session_state.target_score = TARGET_SCORE
        start_new_question() 
        st.rerun()

    # '다시 시작' 버튼 로직 (승리 후)
    if st.session_state.game_state == 'victory' and st.button("🔄 게임 처음부터 다시 시작", key="reset_game"): 
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.step = 1
        start_new_question()
        st.rerun()

    # --- 훈련 데이터 (예시) 표시 ---
    if st.session_state.game_state in ['playing', 'checking', 'finished']:
        st.subheader(f"🧠 **Step {st.session_state.step}**: 규칙 유추 훈련")
        
        # 예시 데이터 테이블로 표시
        data = {
            "물건": [f"예시 {i+1}" for i in range(len(st.session_state.examples))],
            "크기 점수 (x)": [ex['size'] for ex in st.session_state.examples],
            # Step 4에서는 색깔이 3개 모두 나오므로, 예측에 필요한 모든 정보가 들어있음
            "색깔": [ex['color'] for ex in st.session_state.examples],
            "가격 (y)": [f"{ex['price']:,}원" for ex in st.session_state.examples]
        }
        st.dataframe(pd.DataFrame(data), hide_index=True)
        
        st.markdown(f"**힌트**: {st.session_state.step_hint}")
        st.markdown(f"**기본 공식**: 가격 = (크기 점수 x **?원**) + (**색깔별 보너스**) ")
        st.markdown("---")


    # --- 문제 표시 ---
    if st.session_state.game_state == 'playing':
        st.header(f"📈 오늘의 예측 물건: (문제 {st.session_state.step} / {TARGET_SCORE})")
        
        # 문제 특징 시각화
        st.info(f"**크기 점수:** {st.session_state.problem_size} / 10점 만점")
        # 혼합 색깔 또는 단일 색깔 표시
        st.info(f"**색깔:** {st.session_state.display_color}")
        
        st.success("## 예상 가격은 얼마일까요? (원)")
        
        # --- 사용자 예측 (입력) ---
        user_guess = st.number_input(
            "정답이라고 생각하는 가격을 입력하세요 (숫자만):", 
            key=st.session_state.input_key, 
            min_value=0, 
            step=100, 
            format="%d"
        )
        
        # 정답 제출 버튼
        if st.button("🚀 정답 제출"):
            if user_guess is not None:
                st.session_state.user_guess = user_guess
                st.session_state.game_state = 'checking'
                st.rerun() 

    # --- 피드백 처리 및 표시 ---
    if st.session_state.game_state == 'checking':
        
        user_guess = st.session_state.user_guess
        correct_price_str = f"{st.session_state.correct_answer:,}원"
        is_correct = (user_guess == st.session_state.correct_answer)
        
        # 정답 공식 계산 상세
        price, total_bonus = calculate_price(st.session_state.problem_size, st.session_state.problem_color)
        
        if is_correct:
            st.session_state.score += 1
            st.session_state.feedback = f"🎉 **정답입니다!** 다음 단계로 넘어갑니다!"
            st.session_state.feedback_type = 'success'
        else:
            st.session_state.feedback = f"❌ **틀렸어요.** 규칙을 다시 확인해 보세요. 정답은 **{correct_price_str}** 였어요."
            st.session_state.feedback_type = 'error'
        
        # 피드백 내용 구성 (정답 규칙 상세 표시)
        bonus_detail = []
        if isinstance(st.session_state.problem_color, list):
            # Step 4의 경우
            for color in st.session_state.problem_color:
                 bonus_detail.append(f"({color} {COLOR_BONUS.get(color, 0):,}원)")
            bonus_str = ' + '.join(bonus_detail)
        else:
             # Step 1, 2, 3의 경우
            bonus_str = f"({st.session_state.display_color} {total_bonus:,}원)"
        
        feedback_text = st.session_state.feedback
        feedback_text += f"\n\n**✅ 정답 공식**: 가격 = ({st.session_state.problem_size} x {SCALE_FACTOR}원) + {bonus_str}"
        
        # 피드백 표시
        if st.session_state.feedback_type == 'success':
            st.balloons()
            st.success(feedback_text)
            st.session_state.step += 1 # 다음 단계로 이동
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
            st.markdown("---")
            # 점수가 올랐다면 다음 단계로, 틀렸다면 현재 단계 재시작
            button_label = "다음 단계 문제 시작" if st.session_state.feedback_type == 'success' else f"Step {st.session_state.step} 재도전"
            if st.button(f"✨ {button_label}", key="next_step_button"):
                start_new_question()
                st.rerun()

    # --- 승리 화면 ---
    if st.session_state.game_state == 'victory':
        st.success("🏆🏆🏆 게임 승리! 🏆🏆🏆")
        st.header(f"🎉 축하합니다! 모든 가격 규칙을 성공적으로 학습했어요!")
        st.markdown("게임을 다시 시작하려면 위에 있는 **'게임 처음부터 다시 시작'** 버튼을 눌러주세요.")


    # --- 점수판 표시 ---
    st.markdown("---")
    st.info(f"🏆 **현재 단계:** Step {min(st.session_state.step, TARGET_SCORE)} / {TARGET_SCORE}")

if __name__ == "__main__":
    price_prediction_game()