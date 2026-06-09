import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(
    page_title="중2 과학 - 지진 탐구 대시보드",
    page_icon="🌋",
    layout="wide"
)

# 제목 및 수업 탐구 주제 안내
st.title("🌋 실시간 지진 데이터를 통한 '지권의 변화' 탐구")
st.subheader("❓ 탐구 질문: 지진은 왜 특정 지역에 몰려서 발생할까?")
st.markdown("""
학생 여러분! 아래의 지도를 보며 지진이 자주 발생하는 지역이 어디인지 찾아보세요.
이 지역들은 과학 시간에 배운 **'판의 경계(지진대)'**와 어떤 관련이 있을까요?
""")

st.divider()

# 2. 사이드바 - 학생들이 조절할 필터 설정
st.sidebar.header("🔍 탐구 조건 설정하기")

# 기간 선택 (1일, 7일, 30일)
days_option = st.sidebar.selectbox(
    "1. 데이터 분석 기간을 선택하세요.",
    options=[1, 7, 30],
    format_func=lambda x: f"최근 {x}일"
)

# 최소 규모(Magnitude) 선택 슬라이더
min_magnitude = st.sidebar.slider(
    "2. 탐구할 최소 지진 규모(Magnitude)를 선택하세요.",
    min_value=1.0,
    max_value=7.0,
    value=4.0,  # 기본값 4.0 (전 세계 지진대를 뚜렷하게 보기 좋은 규모)
    step=0.5
)

# 3. USGS Earthquake API 데이터 불러오기
@st.cache_data(ttl=600)  # 10분간 캐싱하여 API 부하 감소 및 로딩 속도 향상
def get_earthquake_data(days, min_mag):
    # 날짜 계산
    endtime = datetime.now().strftime("%Y-%m-%d")
    starttime = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # API 요청 주소 및 파라미터 구성
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": starttime,
        "endtime": endtime,
        "minmagnitude": min_mag
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # GeoJSON 데이터를 판다스 데이터프레임으로 변환
        features = data['features']
        quake_list = []
        for f in features:
            props = f['properties']
            geom = f['geometry']
            quake_list.append({
                "place": props['place'],
                "magnitude": props['mag'],
                "time": pd.to_datetime(props['time'], unit='ms'),
                "longitude": geom['coordinates'][0],
                "latitude": geom['coordinates'][1],
                "depth": geom['coordinates'][2]
            })
        return pd.DataFrame(quake_list)
    except Exception as e:
        return pd.DataFrame()

# 데이터 로딩 실행
df = get_earthquake_data(days_option, min_magnitude)

# 4. 화면 레이아웃 구성 및 시각화
if not df.empty:
    # 상단 요약 지표 (Metric)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📊 감지된 총 지진 횟수", value=f"{len(df)}건")
    with col2:
        st.metric(label="💥 가장 강력한 지진 규모", value=f"M {df['magnitude'].max()}")
    with col3:
        st.metric(label="📍 주 탐구 지역", value="환태평양 지진대 등")

    st.markdown("### 🗺️ 세계 지진 발생 지도")
    st.caption("💡 팁: 지도를 드래그하여 움직이거나 마우스 휠로 확대/축소해 보세요. 점이 모여 선을 이루는 곳이 바로 지진대입니다.")

    # Plotly Scatter Mapbox를 이용한 지도 시각화
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        size="magnitude",          # 규모가 클수록 점의 크기가 커짐
        color="depth",             # 진원의 깊이에 따라 색상 변화 (천발/심발 지진 시각화)
        color_continuous_scale=px.colors.sequential.Thermal,
        hover_name="place",
        hover_data={"magnitude": True, "depth": True, "time": True, "latitude": False, "longitude": False},
        zoom=1,
        height=650
    )

    # 오픈스트리트맵(오픈소스) 스타일 적용
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(title="지진 깊이 (km)")
    )
    
    # 스트림릿 웹 앱에 지도 출력
    st.plotly_chart(fig, use_container_width=True)

    # 5. 학생들을 위한 탐구 및 토론 질문 세션
    st.divider()
    st.markdown("### 📝 학생 탐구 활동 가이드")
    
    with st.expander("🔍 [활동 1] 지진대 찾기"):
        st.write("""
        1. 지도를 멀리서 보았을 때, 지진이 발생하는 곳들은 어떤 모양을 띠고 있나요? (예: 무작위로 흩어져 있다, 특정 선을 따라 모여 있다)
        2. 특히 태평양을 둘러싼 거대한 고리 모양의 지진대를 무엇이라고 부를까요? 교과서에서 찾아봅시다.
        """)
        
    with st.expander("🤔 [활동 2] 규모(Magnitude)별 비교하기"):
        st.write("""
        1. 왼쪽 사이드바에서 최소 규모를 **2.0**으로 낮추었을 때와 **5.5** 이상으로 높였을 때, 지도상의 점들의 개수와 분포는 어떻게 달라지나요?
        2. 큰
