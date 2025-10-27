import streamlit as st
import pandas as pd
import random

# ----- 기본 설정 -----
TARGET_SCORE = 3
BASKET_PRICE = 100  # 바구니 크기 1당 100원
ITEM_PRICE = {
    '🍬 사탕': 10,
    '🍫 초콜릿': 5
}

# ----- 가격 계산 -----
def calculate_price(size, items=None):
    """바구니 크기와 과자 종류로 가격 계산"""
    price = size * BASKET_PRICE
    if items:
        if isinstance(items, str):
            price += ITEM_PRICE.get(items, 0)
        elif isinstance(items, list):
            for i in items:
                price += ITEM_PRICE.get(i, 0)
    return price

# ----- 단계별 문제 생성 -----
def generate_step_data(step):
    examples = []

    if step == 1:
        # 바구니 크기만 다름
        sizes = [2, 4, 6]
        for s in sizes:
            examples.append({'basket': s, 'item': '❌ 없음', 'price': calculate_price(s)})
        problem_size = 5
        problem_items = None
        answer = calculate_price(problem_size)
        hint = "바구니가 클수록 가격이 커져요! 바구니 1칸은 100원이에요."

    elif step == 2:
        # 같은 크기, 다른 간식
        examples.append({'basket': 5, 'item': '❌ 없음', 'price': calculate_price(5)})
        examples.append({'basket': 5, 'item': '🍬 사탕', 'price': calculate_price(5, '🍬 사탕')})
        examples.append({'basket': 5, 'item': '🍫 초콜릿', 'price': calculate_price(5, '🍫 초콜릿')})
        problem_size = 5
        problem_items = '🍬 사탕'
        answer = calculate_price(problem_size, problem_items)
        hint = "같은 바구니라도, 사탕이나 초콜릿이 들어가면 조금 더 비싸져요!"

    elif step == 3:
        # 크기와 간식이 모두 다름
        examples.append({'basket': 3, 'item': '🍬 사탕', 'price': calculate_price(3, '🍬 사탕')})
        examples.append({'basket': 4, 'item': '🍫 초콜릿', 'price': calculate_price(4, '🍫 초콜릿')})
        examples.append({'basket': 2, 'item': '🍬 사탕 + 🍫 초콜릿', 'price': calculate_price(2, ['🍬 사탕', '🍫 초콜릿'])})
        problem_size = 5
        problem_items = ['🍬 사탕', '🍫 초콜릿']
        answer = calculate_price(problem_size, problem_items)
        hint = "이제 큰 바구니에 사탕과 초콜릿을 모두 넣어요. 두 개 다 더해보세요!"

    else:
        return [], 0, None, 0, "단계 오류"

    return examples, problem_size, problem_items, answer, hint

# ----- 문제 새로 만들기 -----
def start_new_question():
    step = st.session_state.get('step', 1)
    examples, size, items, answer, hint = generate_step_data(step)
    st.session_state.examples = examples
    st.session_state.problem_size = size
    st.session_state.problem_items = items
    st.session_state.correct_answer = answer
    st.session_state.step_hint = hint
    st.session_state.game_state = 'playing'
    st.session_state.input_key = random.random()

# ----- 메인 게임 -----
def basket_game():
    st.set_page_config(layout="centered")

    # 제목
    st.title("💰 가격 추론 훈련 AI (회귀 분석)")
    st.markdown("#### 바구니 크기와 간식을 보고 가격의 규칙을 찾아보세요!")
    st.markdown(f"##### 총 {TARGET_SCORE}단계를 모두 맞히면 승리합니다!")
    st.markdown("---")

    # 초기화
    if 'game_state' not in st.session_state:
        st.session_state.step = 1
        st.session_state.score = 0
        st.session_state.game_state = 'init'
        start_new_question()

    # 승리 화면
    if st.session_state.game_state == 'victory':
        st.balloons()
        st.success("🎉 모든 단계를 완성했어요!")
        st.header("정답 요약 💡")
        st.markdown("""
        - 바구니 1칸은 **100원**  
        - 🍬 사탕은 **10원 추가**  
        - 🍫 초콜릿은 **5원 추가**
        """)
        st.markdown("내가 추론 능력을 기를 수 있도록 도와줘서 고마워 !👑")
        if st.button("🔄 다시 하기"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        return

    # 예시 표
    st.subheader(f"🧩 Step {st.session_state.step} / {TARGET_SCORE}")
    df = pd.DataFrame([{
        "예시": f"예시 {i+1}",
        "바구니 크기": ex['basket'],
        "들어있는 것": ex['item'],
        "가격": f"{ex['price']}원"
    } for i, ex in enumerate(st.session_state.examples)])
    st.dataframe(df, hide_index=True)
    st.markdown(f"**힌트:** {st.session_state.step_hint}")
    st.markdown("---")

    # 문제 구간
    if st.session_state.game_state == 'playing':
        st.header("📦 이번 손님 주문!")
        if st.session_state.problem_items is None:
            item_text = "❌ 없음"
        elif isinstance(st.session_state.problem_items, list):
            item_text = " + ".join(st.session_state.problem_items)
        else:
            item_text = st.session_state.problem_items

        st.info(f"바구니 크기: {st.session_state.problem_size}")
        st.info(f"들어있는 것: {item_text}")
        guess = st.number_input("💰 이 바구니의 가격은 얼마일까요? (원)", min_value=0, step=5, key=st.session_state.input_key)

        if st.button("🚀 정답 제출"):
            st.session_state.user_guess = guess
            st.session_state.game_state = 'checking'
            st.rerun()

    # 정답 확인
    if st.session_state.game_state == 'checking':
        guess = st.session_state.user_guess
        correct = guess == st.session_state.correct_answer
        answer = st.session_state.correct_answer

        if correct:
            st.success(f"정답이에요! ✅ 가격은 {answer}원이었어요!")
            st.session_state.score += 1
            st.session_state.step += 1
        else:
            st.error(f"아쉬워요 😢 정답은 {answer}원이었어요.")
        st.session_state.game_state = 'finished'

    # 다음 단계
    if st.session_state.game_state == 'finished':
        if st.session_state.score >= TARGET_SCORE:
            st.session_state.game_state = 'victory'
            st.rerun()
        else:
            if st.button("다음 손님 계산하기"):
                start_new_question()
                st.rerun()

    # 현재 점수
    st.markdown("---")
    st.info(f"현재 계산한 손님 수: {st.session_state.score} / {TARGET_SCORE}")

# 실행
if __name__ == "__main__":
    basket_game()
