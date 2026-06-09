import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="인공지능 수학 - 따릉이 최적화 실습", layout="wide")
st.title("🚲 실시간 따릉이 데이터를 활용한 선형 회귀와 최적화")

st.write("이 앱은 서울시 실시간 따릉이 데이터를 활용하여 거치대 개수(X)와 주차된 자전거 수(Y) 사이의 관계를 모델링하고, 인공지능이 오차를 최소화하는 최적화(Optimization) 과정을 배우기 위한 교사용/학생용 수업 도구입니다.")

# 2. 데이터 가져오기 함수 (서울시 오픈 API - 키 불필요 sample 주소 사용)
@st.cache_data(ttl=60)
def load_bike_data():
    url = "http://openapi.seoul.go.kr:8088/sample/json/bikeList/1/50/"
    try:
        response = requests.get(url)
        data = response.json()
        row_data = data['rentBikeStatus']['row']
        
        df = pd.DataFrame(row_data)
        df['rackTotCnt'] = df['rackTotCnt'].astype(int)
        df['parkingBikeTotCnt'] = df['parkingBikeTotCnt'].astype(int)
        return df[['stationName', 'rackTotCnt', 'parkingBikeTotCnt']]
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 데이터 로드 실행
df = load_bike_data()

# 데이터 유효성 검사 및 메인 화면 구성
if df.empty:
    st.warning("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
else:
    # 화면 레이아웃 분할 (좌측: 컨트롤러 / 우측: 시각화)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("🎛️ 인공지능 모델 튜닝")
        st.write("가정된 예측 직선 공식: y = ax + b")
        
        # 슬라이더 컨트롤러
        a_input = st.slider("기울기 (a) 조절", min_value=-2.0, max_value=4.0, value=1.0, step=0.1)
        b_input = st.slider("Y절편 (b) 조절", min_value=-20.0, max_value=20.0, value=0.0, step=1.0)
        
        st.write("---")
        
        # 수학적 계산 및 손실함수 정의
        X = df['rackTotCnt'].values
        Y = df['parkingBikeTotCnt'].values
        Y_pred = a_input * X + b_input
        
        # MSE 계산
        mse = np.mean((Y - Y_pred) ** 2)
        st.metric(label="현재 나의 모델 오차 (MSE)", value=f"{mse:.2f}")
        
        # Scikit-learn을 이용한 AI 정답 계산
        model = LinearRegression()
        model.fit(X.reshape(-1, 1), Y)
        ai_a = model.coef_[0]
        ai_b = model.intercept_
        ai_pred = ai_a * X + ai_b
        ai_mse = np.mean((Y - ai_pred) ** 2)
        
        # 정답 확인 체크박스 토글 제어
        show_ai = False
        if st.checkbox("🤖 인공지능이 찾은 최적의 직선(정답) 확인하기"):
            st.success(f"최적의 기울기(a): {ai_a:.2f}")
            st.success(f"최적의 Y절편(b): {ai_b:.2f}")
            st.info(f"최소 오차 (최적 MSE): {ai_mse:.2f}")
            show_ai = True

    with col2:
        st.header("📊 데이터 및 회귀 직선 시각화")
        
        fig = go.Figure()
        
        # 1. 실제 데이터 플로팅
        fig.add_trace(go.Scatter(
            x=df['rackTotCnt'], y=df['parkingBikeTotCnt'],
            mode='markers', name='실제 따릉이 데이터',
            text=df['stationName'],
            marker=dict(color='darkcyan', size=8)
        ))
        
        # 2. 학생의 예측 직선 플로팅
        x_range = np.linspace(df['rackTotCnt'].min() - 5, df['rackTotCnt'].max() + 5, 100)
        y_range_student = a_input * x_range + b_input
        fig.add_trace(go.Scatter(
            x=x_range, y=y_range_student,
            mode='lines', name='나의 예측 직선',
            line=dict(color='orange', width=3)
        ))
        
        # 3. AI 정답 직선 플로팅 (
