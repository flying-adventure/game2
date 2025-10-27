import streamlit as st
import random
import pandas as pd

# ===== 기본 설정 =====
TARGET_SCORE = 3
SCALE_FACTOR = 100  # 크기당 100원
COLOR_BONUS = {
    '🔴 빨강': 10,
    '🔵 파랑': 5
}

# ===== 가격 계산 함수 =====
def calculate_price(size, colors=None):
    """크기와 색깔 보너스로 가격 계산"""
    base_price = size * SCALE_FACTOR
    bonus = 0
    if colors:
        if isinstance(colors, str):
            bonus += COLOR_BONUS.get(colors, 0)
        elif isinstance(colors, list):
            bonus += sum(COLOR_BONUS.get(c, 0) for c in colors)
    return base_price + bonus

# ===== 단계별 문제 생성 =====
def generate_step_data(step):
    examples = []

    if step == 1:
        # 1단계: 크기 비례 규칙 찾기
        sizes = [2, 4, 6]
        for s in sizes:
            examples.append({'size': s, 'color': '⚪ (색 없음)', 'price': calculate_price(s)})
        problem_size = 5
        problem_color = None
        problem_answer = calculate_price(problem_size)
        hint = "크기가 커질수록 가격이 커져요. 크기 1당 가격을 맞춰볼까요?"
    
    elif step == 2:
        # 2단계: 색깔별 보너스 찾기
        examples.append({'size': 5, 'color': '⚪ (색 없음)', 'price': calculate_price(5)})
        examples.append({'size': 5, 'color': '🔴 빨강', 'price': calculate_price(5, '🔴 빨강')})
        examples.append({'size': 5, 'color': '🔵 파랑', 'price': calculate_price(5, '🔵 파랑')})
        problem_size = 5
        problem_color = '🔴 빨강'
        problem_answer = calculate_price(problem_size, problem_color)
        hint = "색깔마다 가격이 달라요! 색깔 보너스 가격을 찾아보세요."
    
    elif step == 3:
        # 3단계: 크기 + (빨강+파랑) 규칙 적용
        examples.append({'size': 3, 'color': '🔴 빨강', 'price': calculate_price(3, '🔴 빨강')})
        examples.append({'size': 4, 'color': '🔵 파랑', 'price': calculate_price(4, '🔵 파랑')})
        examples.append({'size': 2, 'color': '🔴 빨강 + 🔵 파랑', 'price': calculate_price(2, ['🔴 빨강', '🔵 파랑'])})
        problem_size = 5
        problem_color = ['🔴 빨강', '🔵 파랑']
        problem_answer = calculate_price(problem_size, problem_color)
        hint = "이제 크기와 두 가지 색깔 보너스가 모두 포함돼요!"
    
    else:
        return [], 0, None, 0, "단계 오류"

    return examples, problem_size, problem_color, problem_answer, hint

# ===== 문제 초기화 =====
def start_new_question():
    step = st.session_state.get('step', 1)
    examples, size, color, answer, hint = generate_step_data(step)
    st.session_state.examples = examples
    st.session_state.problem_size = size
    st.session_state.problem_color = color
    st.session_state.correct_answer = answer
    st.session_state.step_hint = hint
    st.session_state.game_state = 'playing'
    st.session_state.input_key = random.random()

# ===== 메인 게임 함수 =====
def price_prediction_game():
    st.set_page_config(layout="centered")

    # 제목
    st.title("💰 가격의 비밀을 찾아라!")
    st.markdown("#### 크기와 색깔에 따라 가격이 달라지는 규칙을 추론해보세요!")
    st.markdown(f"##### 총 {TARGET_SCORE}단계를 모두 맞히면 성공이에요! 메모장에 써보면서 풀어볼까요?")
    st.markdown("---")

    # 초기화
    if 'game_state' not in st.session_state:
        st.session_state.step = 1
        st.session_state.score = 0
        st.session_state.game_state = 'init'
        start_new_question()

    # 승리 화면
    if st.session_state.game_state == 'victory':
        st.success("🎉 모든 단계를 완료했습니다!")
        st.header("아하! 크기당 100원, 빨강은 +10원, 파랑은 +5원이군요!")
        st.markdown("제가 규칙을 완벽하게 알아낼 수 있도록 도와줘서 고마워요!")
        if st.button("🔄 다시 하기"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        return

    # 예시 표시
    st.subheader(f"🧩 Step {st.session_state.step} / {TARGET_SCORE}")
    df = pd.DataFrame([{
        "물건": f"예시 {i+1}",
        "크기": ex['size'],
        "색깔": ex['color'],
        "가격": f"{ex['price']}원"
    } for i, ex in enumerate(st.session_state.examples)])
    st.dataframe(df, hide_index=True)

    st.markdown(f"**힌트:** {st.session_state.step_hint}")
    st.markdown("---")

    # 문제 표시
    if st.session_state.game_state == 'playing':
        st.header("📈 문제")
        color_text = ""
        if st.session_state.problem_color is None:
            color_text = "⚪ (색 없음)"
        elif isinstance(st.session_state.problem_color, str):
            color_text = st.session_state.problem_color
        else:
            color_text = " + ".join(st.session_state.problem_color)

        st.info(f"크기: {st.session_state.problem_size}")
        st.info(f"색깔: {color_text}")

        guess = st.number_input("가격을 예측해보세요 (원):", min_value=0, step=5, key=st.session_state.input_key)
        if st.button("🚀 정답 제출"):
            st.session_state.user_guess = guess
            st.session_state.game_state = 'checking'
            st.rerun()

    # 채점
    if st.session_state.game_state == 'checking':
        guess = st.session_state.user_guess
        correct = guess == st.session_state.correct_answer
        answer = st.session_state.correct_answer
        color = st.session_state.problem_color
        if color is None:
            color_str = "(색 없음)"
        elif isinstance(color, list):
            color_str = " + ".join(color)
        else:
            color_str = color

        formula = f"({st.session_state.problem_size} × 100) + 색깔 보너스({color_str}) = {answer}원"

        if correct:
            st.success(f"정답이에요! ✅ {formula}")
            st.session_state.score += 1
            st.session_state.step += 1
        else:
            st.error(f"아쉬워요! 정답은 {answer}원이었어요.\n\n{formula}")
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

# ===== 실행 =====
if __name__ == "__main__":
    price_prediction_game()




