import streamlit as st

st.set_page_config(page_title="칼로리 기록기", page_icon="🍎")

# 1. 간단한 음식 데이터베이스 (임의 데이터)
food_db = {
    "사과": 95, "바나나": 105, "밥": 300, "닭가슴살": 165,
    "계란": 78, "라면": 500, "김치": 30, "샐러드": 150
}

st.title("🍎 음식 칼로리 계산기")
st.write("오늘 먹은 음식을 추가해서 총 칼로리를 확인하세요!")

# 세션 상태 초기화 (음식 리스트 저장용)
if 'meal_log' not in st.session_state:
    st.session_state.meal_log = []

# 2. 음식 선택 및 추가
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        food_name = st.selectbox("음식을 선택하세요", list(food_db.keys()))
    with col2:
        st.write("") # 간격 맞춤
        st.write("")
        add_btn = st.button("추가")

if add_btn:
    st.session_state.meal_log.append(food_name)

# 3. 결과 표시 및 삭제
st.divider()
st.subheader("오늘의 식단")

if st.session_state.meal_log:
    total_kcal = 0
    for idx, item in enumerate(st.session_state.meal_log):
        kcal = food_db[item]
        total_kcal += kcal
        st.write(f"{idx+1}. {item}: **{kcal} kcal**")
    
    st.success(f"현재까지 총 섭취 칼로리: **{total_kcal} kcal**")
    
    if st.button("기록 초기화"):
        st.session_state.meal_log = []
        st.rerun()
else:
    st.info("아직 기록된 음식이 없습니다.")
