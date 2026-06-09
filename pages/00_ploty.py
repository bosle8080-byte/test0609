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
st.markdown("학생 여러분! 아래의 지도를 보며 지진이 자주 발생하는 지역이 어디인지 찾아보세요. 이 지역들은 과학 시간에 배운 **'판의 경계(지진대)'**와 어떤 관련이 있을까요?")

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
    value=4.0,
    step=0.5
)

# 3. USGS Earthquake API 데이터 불러오기
@st.cache_data(ttl=600)
def get_earthquake_data(days, min_mag):
    endtime = datetime.now().strftime("%Y-%m-%d")
    starttime = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
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
        
        features = data.get('features', [])
        quake_list = []
        for f in features:
            props = f.get('properties', {})
            geom = f.get('geometry', {})
            coords = geom.get('coordinates', [0, 0, 0])
            
            quake_list.append({
                "place": props.get('place', '알 수 없는 위치'),
                "magnitude": props.get('mag', 0.0),
                "time": pd.to_datetime(props.get('time', 0), unit='ms'),
                "longitude": coords[0],
                "latitude": coords[1],
                "depth": coords[2]
            })
        return pd.DataFrame(quake_list)
    except Exception as e:
        return pd.DataFrame()

# 데이터 로딩 실행
df = get_earthquake_data(days_option, min_magnitude)

# 4. 화면 레이아웃 구성 및 시각화
if not df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📊 감지된 총 지진 횟수", value=f"{len(df)}건")
    with col2:
        st.metric(label="💥 가장 강력한 지진 규모", value=f"M {df['magnitude'].max()}")
    with col3:
        st.metric(label="📍 주 탐구 지역", value="환태평양 지진대 등")

    st.markdown("### 🗺️ 세계 지진 발생 지도")
    st.caption("💡 팁: 지도를 드래그하여 움직이거나 마우스 휠로 확대/축소해 보세요. 점이 모여 선을 이루는 곳이 바로 지진대입니다.")

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        size="magnitude",
        color="depth",
        color_continuous_scale=px.colors.sequential.thermal,
        hover_name="place",
        hover_data={"magnitude": True, "depth": True, "time": True, "latitude": False, "longitude": False},
        zoom=1,
        height=650
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="지진 깊이 (km)")
    )
    
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("### 📝 학생 탐구 활동 가이드")
    
    with st.expander("🔍 [활동 1] 지진대 찾기"):
        st.write("1. 지도를 멀리서 보았을 때, 지진이 발생하는 곳들은 어떤 모양을 띠고 있나요? (예: 무작위로 흩어져 있다, 특정 선을 따라 모여 있다)")
        st.write("2. 특히 태평양을 둘러싼 거대한 고리 모양의 지진대를 무엇이라고 부를까요? 교과서에서 찾아봅시다.")
        
    with st.expander("🤔 [활동 2] 규모(Magnitude)별 비교하기"):
        st.write("1. 왼쪽 사이드바에서 최소 규모를 2.0으로 낮추었을 때와 5.5 이상으로 높였을 때, 지도상의 점들의 개수와 분포는 어떻게 달라지나요?")
        st.write("2. 큰 규모의 지진이 자주 일어나는 위험한 지역은 어디인지 지도를 확대해 찾아보세요.")
        
    with st.expander("💡 [과학 개념 체크] 지진은 왜 여기서만 날까?"):
        st.info("지구의 겉 부분은 여러 개의 거대한 '판(Plate)'으로 나누어져 있습니다. 이 판들은 매년 수 센티미터씩 매우 느리게 움직입니다. 이때 판และ 판이 만나는 경계면에서 서로 부딪히거나, 갈라지거나, 어긋나면서 엄청난 에너지가 쌓이게 되고, 이 에너지가 한 번에 터져 나오는 현상이 바로 지진입니다. 따라서 지진은 판의 경계(지진대)를 따라 띠 모양으로 집중되어 발생합니다!")

else:
    st.warning("선택한 조건에 해당하는 지진 데이터가 없거나 API 연결에 실패했습니다. 조건을 변경해 주세요.")
