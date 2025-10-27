import streamlit as st
import random
import pandas as pd

# --- 전역 상수 ---
TARGET_SCORE = 3  # 총 3단계
SCALE_FACTOR = 800  # 크기 가중치

# 색깔별 보너스 정의
COLOR_BONUS = {
    '🔴 빨강': 1500,
    '🟡 노랑': 500,
    '🔵 파랑': 1000,
}
REQUIRED_COLORS = list(COLOR_BONUS.keys())

def calculate_price(size, colors):
    """크기 점수와 색상 조합으로 가격 계산"""
    if isinstance(colors, str):
        color_list = [colors]
    else:
        color_list = colors
    total_bonus = sum(COLOR_BONUS.get(c, 0) for c in color_list)
    price = (size * SCALE_FACTOR) + total_bonus
    return price, total_bonus

def generate_step_data(step):
    """단계별 문제 생성"""
    examples = []
    all_sizes = list(range(4, 11))

    if step == 1:
        # 빨강 보너스 및 크기 가중치 추론
        required_color = '🔴 빨강'
        example_sizes = random.sample(all_sizes, 3)
        for s in example_sizes:
            price, _ = calculate_price(s, required_color)
            examples.append({'size': s, 'color': required_color, 'price': price})
        problem_size = random.choice([x for x in all_sizes if x not in example_sizes])
        problem_color = required_color
        step_hint = "빨간색 물건만 보고 크기 가중치와 빨강 보너스를 유추하세요."

    elif step == 2:
        # 노랑 보너스 추론
        required_color = '🟡 노랑'
        size_yellow = 7
        size_red = 7
        size_ref = 5
        red_price, _ = calculate_price(size_red, '🔴 빨강')
        yellow_price, _ = calculate_price(size_yellow, '🟡 노랑')
        ref_price, _ = calculate_price(size_ref, '🔴 빨강')

        examples.append({'size': size_red, 'color': '🔴 빨강', 'price': f"{red_price:,}원"})
        examples.append({'size': size_yellow, 'color': '🟡 노랑', 'price': "?"})
        examples.append({'size': size_ref, 'color': '🔴 빨강', 'price': f"{ref_price:,}원"})

        problem_size = size_yellow
        problem_color = required_color
        step_hint = "1단계의 결과(빨강 보너스, 가중치)를 이용해 노랑 보너스를 계산하세요."

    elif step == 3:
        # 파랑 보너스 추론
        required_color = '🔵 파랑'
        example_sizes = [8, 6]
        examples.append({'size': 8, 'color': '🔴 빨강', 'price': calculate_price(8, '🔴 빨강')[0]})
        examples.append({'size': 8, 'color': '🔵 파랑', 'price': calculate_price(8, '🔵 파랑')[0]})
        examples.append({'size': 6, 'color': '🔵 파랑', 'price': calculate_price(6, '🔵 파랑')[0]})
        problem_size = random.choice([3, 4, 5, 7, 9, 10])
        problem_color = required_color
        step_hint = "이제 파랑 보너스를 찾아내세요. 모든 규칙이 완성됩니다!"

    else:
        return [], 0, "", 0, "오류"

    problem_price, _ = calculate_price(problem_size, problem_color)
    return examples, problem_size, problem_color, problem_price, step_hint

def start_new_question():
    """문제 새로 생성"""
    step = st.session_state.get('step', 1)
    examples, size, color, answer, hint = generate_step_data(step)
    st.session_state.examples = examples
    st.session_state.correct_answer = answer
    st.session_state.problem_size = size
    st.session_state.problem_color = color
    st.session_state.step_hint = hint
    st.session_state.display_color = color
    st.session_state.game_state = 'playing'
    st.session_state.input_key = random.random()

def price_prediction_game():
    st.set_page_config(layout="centered")
    st.title("💰 가격 추론 훈련 AI")
    st.markdown("#### 빨강 → 노랑 → 파랑 순서로 가격 규칙을 유추하세요!")
    st.markdown("---")

    # 초기화
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'init'
        st.session_state.score = 0
        st.session_state.step = 1
        start_new_question()

    # 승리 화면
    if st.session_state.game_state == 'victory':
        st.success("🏆 모든 단계를 완료했습니다!")
        st.header("아하 ! 크기 가중치는 800원, 빨강은 1500원, 노랑은 500원, 파랑은 1000원이군요!")
        st.markdown("덕분에 학습을 완료했어요!")
        if st.button("🔄 다시 시작"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        return

    # 예시 표시
    st.subheader(f"Step {st.session_state.step} / {TARGET_SCORE}")
    df = pd.DataFrame([{
        "물건": f"예시 {i+1}",
        "크기 점수": ex['size'],
        "색깔": ex['color'],
        "가격": ex['price'] if isinstance(ex['price'], str) else f"{ex['price']:,}원"
    } for i, ex in enumerate(st.session_state.examples)])
    st.dataframe(df, hide_index=True)
    st.markdown(f"**힌트:** {st.session_state.step_hint}")
    st.markdown("---")

    # 문제 표시
    if st.session_state.game_state == 'playing':
        st.header("📈 문제")
        st.info(f"크기 점수: {st.session_state.problem_size}")
        st.info(f"색깔: {st.session_state.display_color}")
        st.success("예상 가격을 입력하세요 (원)")
        guess = st.number_input("가격 입력:", min_value=0, step=100, key=st.session_state.input_key)
        if st.button("🚀 정답 제출"):
            st.session_state.user_guess = guess
            st.session_state.game_state = 'checking'
            st.rerun()

    # 채점
    if st.session_state.game_state == 'checking':
        guess = st.session_state.user_guess
        answer = st.session_state.correct_answer
        correct = (guess == answer)
        price, bonus = calculate_price(st.session_state.problem_size, st.session_state.problem_color)
        color = st.session_state.problem_color
        formula = f"({st.session_state.problem_size} x {SCALE_FACTOR}) + {COLOR_BONUS[color]:,} = {answer:,}원"
        if correct:
            st.success(f"정답입니다! ✅\n\n{formula}")
            st.session_state.score += 1
            st.session_state.step += 1
        else:
            st.error(f"틀렸어요. 정답은 {answer:,}원 입니다.\n\n{formula}")
        st.session_state.game_state = 'finished'

    # 다음 단계
    if st.session_state.game_state == 'finished':
        if st.session_state.score >= TARGET_SCORE:
            st.session_state.game_state = 'victory'
            st.rerun()
        else:
            if st.button("다음 단계로 이동"):
                start_new_question()
                st.rerun()

    st.markdown("---")
    st.info(f"현재 점수: {st.session_state.score} / {TARGET_SCORE}")

if __name__ == "__main__":
    price_prediction_game()
