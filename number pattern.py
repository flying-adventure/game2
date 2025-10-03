import streamlit as st
import random
import base64

# 전역 상수 설정
MAP_WIDTH = 20         # 맵의 가로 길이
PLAYER_START_X = 0     # 마리오 시작 위치
WIN_COINS = 5          
FLAG_POSITION = MAP_WIDTH - 1 

# 이미지 표시 크기 (400으로 유지)
IMG_WIDTH = 400 

# --- 로컬 이미지 파일 경로 설정 및 Base64 인코딩 함수 ---
def get_image_as_base64(filepath):
    """로컬 이미지 파일을 base64로 인코딩하여 HTML img src에 바로 사용할 수 있도록 반환"""
    try:
        with open(filepath, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        if filepath.lower().endswith(".png"):
            mime = "image/png"
        elif filepath.lower().endswith(".jpg") or filepath.lower().endswith(".jpeg"):
            mime = "image/jpeg"
        elif filepath.lower().endswith(".gif"):
            mime = "image/gif"
        else:
            mime = "image/webp"
        return f"data:{mime};base64,{encoded_string}"
    except FileNotFoundError:
        # 파일이 없으면 빈 문자열 반환 (div로 대체)
        return '' 

# --- 모든 이미지 파일을 Base64로 미리 인코딩 ---
PLAYER_IMG_B64 = get_image_as_base64("mario.jpg")       
PLAYER_JUMP_IMG_B64 = get_image_as_base64("mario.jpg")  
COIN_IMG_B64 = get_image_as_base64("coin.jpg")          
PIPE_IMG_B64 = get_image_as_base64("bomb.png")          
EMPTY_BLOCK_IMG_B64 = get_image_as_base64("block.jpg")  
FLAG_IMG_B64 = get_image_as_base64("flag.png")          

# 투명한 1x1 픽셀 GIF 이미지는 이제 사용하지 않습니다.
# ==============================================================================
# 로직 함수 (Base64 변수명만 사용하며 동일)
# ==============================================================================

def generate_map():
    num_coins = WIN_COINS
    num_pipes = 4
    
    available_positions = list(range(1, MAP_WIDTH - 1))
    random.shuffle(available_positions)
    
    map_objects = [''] * MAP_WIDTH # 빈 공간은 빈 문자열로 처리
    
    coins_placed = 0
    while coins_placed < num_coins:
        if not available_positions: break 
        pos = random.choice(available_positions)
        if map_objects[pos] == '': 
            map_objects[pos] = COIN_IMG_B64 
            coins_placed += 1
            available_positions.remove(pos)

    pipes_placed = 0
    temp_available_for_pipes = list(available_positions) 
    random.shuffle(temp_available_for_pipes)

    for _ in range(num_pipes * 2): 
        if pipes_placed >= num_pipes: break
        if not temp_available_for_pipes: break

        pos = random.choice(temp_available_for_pipes)
        
        is_safe_to_place = True
        if map_objects[pos] != '': is_safe_to_place = False
        
        if pos > 0 and map_objects[pos-1] == PIPE_IMG_B64: is_safe_to_place = False
        if pos < MAP_WIDTH - 1 and map_objects[pos+1] == PIPE_IMG_B64: is_safe_to_place = False
            
        if is_safe_to_place:
            map_objects[pos] = PIPE_IMG_B64 
            pipes_placed += 1
            if pos in temp_available_for_pipes:
                temp_available_for_pipes.remove(pos)

    map_objects[FLAG_POSITION] = FLAG_IMG_B64 

    coins_set_actual = {i for i, obj in enumerate(map_objects) if obj == COIN_IMG_B64}
    pipes_set_actual = {i for i, obj in enumerate(map_objects) if obj == PIPE_IMG_B64}

    ground_map_elements = [EMPTY_BLOCK_IMG_B64] * MAP_WIDTH
        
    return map_objects, ground_map_elements, coins_set_actual, pipes_set_actual

def check_action(player_x, action, map_objects, coins_set, pipes_set):
    # ... (중략: 게임 로직 함수는 Base64 변수명만 사용하며 이전 버전과 동일) ...
    new_x = player_x
    feedback = ""
    coin_gained = 0
    game_over = False
    is_player_jumping = st.session_state.get('jump_active_for_next_move', False)

    if action == 'move_right':
        new_x = min(player_x + 1, MAP_WIDTH - 1)
    elif action == 'move_left':
        new_x = max(player_x - 1, 0)
        
    if action == 'move_right' or action == 'move_left':
        current_object_at_new_x = map_objects[new_x]
        
        if current_object_at_new_x == COIN_IMG_B64:
            coin_gained = 1
            map_objects[new_x] = '' 
            if new_x in coins_set:
                coins_set.remove(new_x) 
            feedback = "💰 코인을 획득했습니다!"
            
        elif current_object_at_new_x == PIPE_IMG_B64:
            if is_player_jumping:
                feedback = "✅ 함정을 멋지게 뛰어넘었습니다!"
            else:
                feedback = "💥 함정에 빠졌습니다! 게임 오버!"
                game_over = True
            
        elif current_object_at_new_x == FLAG_IMG_B64 and new_x == FLAG_POSITION:
            feedback = "🏁 깃발에 도착했습니다! 임무 성공!" 
            st.session_state.game_state = 'victory'
            
        elif new_x != player_x: 
            feedback = "➡️ 안전하게 이동했습니다."
            
        elif new_x == player_x: 
            feedback = "벽에 막혀 더 이상 이동할 수 없습니다."
            
    elif action == 'jump':
        current_object_at_player_x = map_objects[player_x]
        
        if current_object_at_player_x == PIPE_IMG_B64:
            feedback = "✅ (준비) 함정 위에서 점프 준비! 이제 이동하여 넘으세요."
        elif current_object_at_player_x == COIN_IMG_B64:
             feedback = "점프! 코인을 획득하려면 점프하지 않고 지나가야 합니다."
        elif current_object_at_player_x == FLAG_IMG_B64:
            feedback = "점프! 깃발을 향해 점프했습니다!"
        else:
             feedback = "점프! 별 일 없었습니다."
        
    return new_x, coin_gained, game_over, feedback

# ==============================================================================
# 맵 그리기 함수 (Base64 + 빈 div로 경고 완전 차단 시도)
# ==============================================================================

def get_map_row_html(row_elements, player_x, is_jumping, is_top_row):
    """주어진 이미지 Base64 리스트를 HTML 문자열로 반환"""
    
    html_parts = []
    
    for i in range(MAP_WIDTH):
        current_img_src = ""
        
        if is_top_row and i == player_x:
            current_img_src = PLAYER_JUMP_IMG_B64 if is_jumping else PLAYER_IMG_B64
        else:
            img_b64 = row_elements[i]
            current_img_src = img_b64 # Base64 URL or empty string
        
        if current_img_src == '':
            # ★★★ 빈 공간은 빈 DIV로 처리하여 Streamlit의 이미지 로직 개입 차단 ★★★
            element_html = f"""
                <div style="
                    display: inline-block; 
                    width: {IMG_WIDTH}px; 
                    height: {IMG_WIDTH}px; 
                    margin: 0; padding: 0; 
                    line-height: 0; 
                    vertical-align: top;
                "></div>
            """
        else:
            # 이미지가 있는 경우 IMG 태그 사용
            element_html = f"""
                <div style="
                    display: inline-block; 
                    width: {IMG_WIDTH}px; 
                    height: {IMG_WIDTH}px; 
                    margin: 0; padding: 0; 
                    line-height: 0; 
                    vertical-align: top;
                ">
                    <img src="{current_img_src}" style="width: 100%; height: 100%; object-fit: cover; display: block;"/>
                </div>
            """
        html_parts.append(element_html)
        
    return "".join(html_parts)

def draw_map(map_objects, ground_map_elements, player_x, is_jumping):
    
    st.markdown("### 🗺️ 마리오 맵")
    
    # 윗줄 렌더링
    top_row_html = get_map_row_html(map_objects, player_x, is_jumping, is_top_row=True)
    st.markdown(top_row_html, unsafe_allow_html=True)

    # 아랫줄 렌더링
    bottom_row_html = get_map_row_html(ground_map_elements, -1, False, is_top_row=False)
    st.markdown(bottom_row_html, unsafe_allow_html=True)


# ==============================================================================
# 메인 게임 루프
# ==============================================================================

def mario_map_game():
    
    st.set_page_config(layout="wide") 
    st.title("🍄 마리오 맵 훈련 로봇")
    st.markdown(f"##### **좌우 이동**과 **점프**를 사용해 함정을 피하고 **깃발({FLAG_POSITION}번 칸)**에 도착하세요!")
    st.markdown("---")
    
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'playing'
        st.session_state.player_x = PLAYER_START_X
        st.session_state.coins_collected = 0
        st.session_state.map_objects, st.session_state.ground_map_elements, st.session_state.coins_set, st.session_state.pipes_set = generate_map()
        st.session_state.last_feedback = "게임을 시작합니다! 오른쪽으로 이동해 보세요."
        st.session_state.is_jumping_display = False 
        st.session_state.jump_active_for_next_move = False 

    if st.session_state.game_state != 'playing' and st.button("🔄 게임 다시 시작", key="reset_game"): 
        st.session_state.game_state = 'playing'
        st.session_state.player_x = PLAYER_START_X
        st.session_state.coins_collected = 0
        st.session_state.map_objects, st.session_state.ground_map_elements, st.session_state.coins_set, st.session_state.pipes_set = generate_map()
        st.session_state.last_feedback = "게임을 다시 시작합니다! 오른쪽으로 이동해 보세요."
        st.session_state.is_jumping_display = False
        st.session_state.jump_active_for_next_move = False
        st.rerun()

    
    st.info(f"💰 **획득 코인:** {st.session_state.coins_collected}개") 
    
    draw_map(st.session_state.map_objects, st.session_state.ground_map_elements, st.session_state.player_x, st.session_state.is_jumping_display)
    
    if st.session_state.is_jumping_display:
        st.session_state.is_jumping_display = False 


    if st.session_state.game_state != 'playing':
        if st.session_state.game_state == 'victory':
            st.success(f"🏆 **승리!** 깃발에 도착했습니다! 획득 코인: {st.session_state.coins_collected}개")
            st.balloons()
        elif st.session_state.game_state == 'game_over':
            st.error(f"💣 **게임 오버!** {st.session_state.last_feedback}")
        return

    st.markdown(f"💬 **피드백:** {st.session_state.last_feedback}")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    def handle_action(action):
        
        if action == 'jump':
            st.session_state.is_jumping_display = True 
            st.session_state.jump_active_for_next_move = True 
        
        new_x, coin_gained, game_over, feedback = check_action(
            st.session_state.player_x, action, st.session_state.map_objects, 
            st.session_state.coins_set, st.session_state.pipes_set
        )
        
        st.session_state.player_x = new_x
        st.session_state.coins_collected += coin_gained
        st.session_state.last_feedback = feedback
        
        if action != 'jump':
             st.session_state.jump_active_for_next_move = False
            
        if game_over:
            st.session_state.game_state = 'game_over'
            
        st.rerun()
        
    with col1:
        if st.button("⬅️ 왼쪽으로 이동"):
            handle_action('move_left')
    
    with col2:
        if st.button("⬆️ 점프", help="점프 버튼을 누른 후, 이동 버튼을 눌러 함정을 뛰어넘으세요."):
            handle_action('jump')
    
    with col3:
        if st.button("➡️ 오른쪽으로 이동"):
            handle_action('move_right')

if __name__ == "__main__":
    mario_map_game()