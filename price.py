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
    
    # 0. 문제 size 후보군 정의 (1~10 사이)
    all_possible_sizes = set(range(1, 11))
    
    if step == 1:
        # 목표: SCALE_FACTOR (크기 가중치)와 빨강 보너스 찾기
        required_color = '🔴 빨강'
        
        # 3개의 예시 size를 4~10 중에서 선택
        example_sizes = random.sample(range(4, 11), 3) 
        for size in example_sizes:
            price, _ = calculate_price(size, required_color)
            examples.append({'size': size, 'color': required_color, 'price': price})
        
        # 문제 size는 예시 size와 겹치지 않는 범위에서 선택 (1~10 사이)
        problem_size_candidates = list(all_possible_sizes - set(example_sizes)) 
        
        if problem_size_candidates:
            problem_size = random.choice(problem_size_candidates)
        else:
            # 예외 상황 대비 (4~10 중 3개를 이미 썼으므로, 1~3은 항상 남음)
            problem_size = random.choice(list(all_possible_sizes)) 

        problem_color = required_color
        step_hint = "빨간색 물건들만 보고 '크기 점수 가중치'와 '빨강 보너스'를 찾아내세요."
        
    elif step == 2:
        # 목표: 노랑 보너스 찾기 
        required_color = '🟡 노랑'
        
        # 예시 size 후보군: 7, 5
        example_sizes = [7, 5]
        
        examples.append({'size': 7, 'color': '🔴 빨강', 'price': calculate_price(7, '🔴 빨강')[0]})
        examples.append({'size': 7, 'color': '🟡 노랑', 'price': calculate_price(7, '🟡 노랑')[0]})
        examples.append({'size': 5, 'color': '🔴 빨강', 'price': calculate_price(5, '🔴 빨강')[0]})
        
        # 문제 size는 4~9 중에서 예시 size와 겹치지 않게 선택
        size_range = set(range(4, 10)) # 4, 5, 6, 7, 8, 9
        problem_size_candidates = list(size_range - set(example_sizes)) # 4, 6, 8, 9
        
        if problem_size_candidates:
            problem_size = random.choice(problem_size_candidates)
        else:
            problem_size = random.choice(list(size_range)) # 안전 장치
            
        problem_color = required_color
        step_hint = f"크기 가중치({SCALE_FACTOR}원)와 빨강 보너스를 이용해 '노랑 보너스'를 찾아내세요."

    elif step == 3:
        # 목표: 파랑 보너스 찾기
        required_color = '🔵 파랑'
        
        # 예시 size 후보군: 8, 6
        example_sizes = [8, 6]
        
        examples.append({'size': 8, 'color': '🔴 빨강', 'price': calculate_price(8, '🔴 빨강')[0]})
        examples.append({'size': 8, 'color': '🟡 노랑', 'price': calculate_price(8, '🟡 노랑')[0]})
        examples.append({'size': 6, 'color': '🔵 파랑', 'price': calculate_price(6, '🔵 파랑')[0]})
        
        # 문제 size는 3~10 중에서 예시 size와 겹치지 않게 선택
        size_range = set(range(3, 11)) # 3, 4, 5, 6, 7, 8, 9, 10
        problem_size_candidates = list(size_range - set(example_sizes)) # 3, 4, 5, 7, 9, 10
        
        if problem_size_candidates:
            problem_size = random.choice(problem_size_candidates)
        else:
            problem_size = random.choice(list(size_range)) # 안전 장치

        problem_color = required_color
        step_hint = "크기 가중치와 이미 알고 있는 색깔 보너스를 활용해 '파랑 보너스'를 찾아내세요."
        
    elif step == 4:
        # 목표: 두 가지 색깔 혼합 문제 (최종 점검)
        
        # 예시 size 후보군: 7
        example_sizes = [7] 
        
        # 3가지 색깔의 예시 모두 제시 (모두 크기 7)
        all_colors = REQUIRED_COLORS
        for color in all_colors:
             examples.append({'size': 7, 'color': color, 'price': calculate_price(7, color)[0]})
        
        # 문제 size는 4~9 중에서 예시 size와 겹치지 않게 선택
        size_range = set(range(4, 10)) # 4, 5, 6, 7, 8, 9
        problem_size_candidates = list(size_range - set(example_sizes)) # 4, 5, 6, 8, 9
        
        if problem_size_candidates:
            problem_size = random.choice(problem_size_candidates)
        else:
            problem_size = random.choice(list(size_range)) # 안전 장치

        # 문제: 두 가지 색깔을 무작위로 선택하여 혼합
        mixed_colors = random.sample(REQUIRED_COLORS, 2)
        
        problem_color = mixed_colors # 이제 problem_color는 리스트가 됨
        
        step_hint = "모든 색깔의 보너스를 합하고 크기 가중치를 적용하여, 두 가지 색깔이 혼합된 물건의 가격을 예측하세요!"
        
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
    st.title("💰 가격 추론 훈련 AI (회귀 분석)")
    st.markdown(f"#### 추론 능력을 길러줘!")
    
    st.markdown(f"##### 단계별로 숨겨진 가격 규칙을 유추해 보세요. 총 {TARGET_SCORE}단계를 통과하면 승리합니다.")
    st.markdown("---")
    
    # 1. 게임 상태 관리 및 초기화
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.step = 1
        st.session_state.target_score = TARGET_SCORE
        start_new_question() 

    # --- 승리 화면 (통합된 로직) ---
    if st.session_state.game_state == 'victory':
        st.success("🏆🏆🏆 게임 승리! 🏆🏆🏆")
        st.header(f"🎉 축하합니다! 모든 가격 규칙을 성공적으로 학습했어요!")

        # 힌트 문구 출력 (가장 명확하게 보이도록 배치)
        st.warning("""
        **💡 힌트 문장:** 다른 성과 달리 지붕이 검은 철판으로 덮여 있다.
        """)

        st.markdown(f"(이 문장을 메모장 등에 기록해두세요!)")
        
        # '게임 처음부터 다시 시작' 버튼을 이 블록 안에 위치시켜 렌더링을 보장합니다.
        if st.button("🔄 게임 처음부터 다시 시작", key="reset_game_victory"): 
            st.session_state.game_state = 'init'
            st.session_state.score = 0
            st.session_state.step = 1
            start_new_question()
            st.rerun()

        st.markdown("게임을 다시 시작하려면 위에 있는 **'게임 처음부터 다시 시작'** 버튼을 눌러주세요.")
        st.markdown("---")
        st.info(f"🏆 **최종 점수:** {st.session_state.score} / {st.session_state.target_score}점")
        return # 승리 화면이 출력되면 나머지 코드는 실행하지 않음


    # --- 훈련 데이터 (예시) 표시 ---
    if st.session_state.game_state in ['playing', 'checking', 'finished', 'init']:
        st.subheader(f"🧠 **Step {min(st.session_state.step, TARGET_SCORE)}** (현재 단계): 규칙 유추 훈련")
        
        # 예시 데이터 테이블로 표시
        data = {
            "물건": [f"예시 {i+1}" for i in range(len(st.session_state.examples))],
            "크기 점수 (x)": [ex['size'] for ex in st.session_state.examples],
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
            # 입력이 빈 값일 때를 대비하여 체크
            if user_guess is not None and user_guess >= 0:
                st.session_state.user_guess = user_guess
                st.session_state.game_state = 'checking'
                st.rerun() 
            else:
                 st.error("가격을 입력해 주세요!")

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
            # Step 4의 경우 (혼합 색상)
            for color in st.session_state.problem_color:
                 bonus_detail.append(f"({color} {COLOR_BONUS.get(color, 0):,}원)")
            bonus_str = ' + '.join(bonus_detail)
        else:
             # Step 1, 2, 3의 경우 (단일 색상)
             bonus_str = f"({st.session_state.display_color} {total_bonus:,}원)"
        
        feedback_text = st.session_state.feedback
        feedback_text += f"\n\n**✅ 정답 공식**: 가격 = ({st.session_state.problem_size} x {SCALE_FACTOR}원) + {bonus_str} = {st.session_state.correct_answer:,}원"
        
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

    # --- 점수판 표시 ---
    st.markdown("---")
    current_step_display = min(st.session_state.step, TARGET_SCORE)
    st.info(f"🏆 **현재 단계:** Step {current_step_display} / {TARGET_SCORE} (정답 {st.session_state.score}개)")

if __name__ == "__main__":
    price_prediction_game()


