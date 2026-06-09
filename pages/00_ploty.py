import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="인공지능 수학 - 따릉이 최적화 실습", layout="wide")
st.title("🚲 실시간 따릉이 데이터를 활용한 선형 회귀와 최적화")
st.markdown("""
이 앱은 서울시 실시간 따릉이 데이터를 활용하여 **거치대 개수($x$)**와 **주차된 자전거 수($y$)** 사이의 관계를 모델링하고, 
인공지능이 오차를 최소화하는 **최적화(Optimization)** 과정을 배우기 위한 교사용/학생용 수업 도구입니다.
""")

# 2. 데이터 가져오기 함수 (서울시 오픈 API - 키 불필요 sample 주소 사용)
@st.cache_data(ttl=60) # 60초 동안 데이터 캐싱 (실시간 데이터 과부하 방지)
def load_bike_data():
    # 1번부터 50번 대여소까지 조금 더 풍부한 데이터를 가져옵니다.
    url = "http://openapi.seoul.go.kr:8088/sample/json/bikeList/1/50/"
    try:
        response = requests.get(url)
        data = response.json()
        row_data = data['rentBikeStatus']['row']
        
        # 데이터프레임 변환 및 자료형 변환
        df = pd.DataFrame(row_data)
        df['rackTotCnt'] = df['rackTotCnt'].astype(int)          # 거치대 개수 (X)
        df['parkingBikeTotCnt'] = df['parkingBikeTotCnt'].astype(int)  # 주차된 자전거 수 (Y)
        return df[['stationName', 'rackTotCnt', 'parkingBikeTotCnt']]
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df = load_bike_data()

if df.empty:
    st.warning("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
else:
    # 화면 레이아웃 분할 (좌측: 컨트롤러 / 우측: 시각화 및 수식)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("🎛️ 인공지능 모델 튜닝")
        st.markdown("가정된 예측 직선:  \n$$y = ax + b$$")
        
        # 학생들이 직접 조절할 기울기(a)와 Y절편(b) 슬라이더
        a_input = st.slider("기울기 (a) 조절", min_value=-2.0, max_value=4.0, value=1.0, step=0.1)
        b_input = st.slider("Y절편 (b) 조절", min_value=-20.0, max_value=20.0, value=0.0, step=1.0)
        
        st.write("---")
        
        # 수학적 계산 및 손실함수 정의
        X = df['rackTotCnt'].values
        Y = df['parkingBikeTotCnt'].values
        Y_pred = a_input * X + b_input
        
        # MSE (평균제곱오차) 계산
        mse = np.mean((Y - Y_pred) ** 2)
        
        st.metric(label="현재 나의 모델 오차 (MSE)", value=f"{mse:.2f}")
        
        # 인공지능이 찾은 최적의 정답 해 구하기 (scikit-learn 회귀분석)
        model = LinearRegression()
        model.fit(X.reshape(-1, 1), Y)
        ai_a = model.coef_[0]
        ai_b = model.intercept_
        ai_pred = ai_a * X + ai_b
        ai_mse = np.mean((Y - ai_pred) ** 2)
        
        # 정답 공개 버튼
        if st.checkbox("🤖 인공지능이 찾은 최적의 직선(정답) 확인하기"):
            st.success(f"최적의 기울기(a): {ai_a:.2f}")
            st.success(f"최적의 Y절편(b): {ai_b:.2f}")
            st.info(f"최소 오차 (최적 MSE): {ai_mse:.2f}")
            show_ai = True
        else:
            show_ai = False

    with col2:
        st.header("📊 데이터 및 회귀 직선 시각화")
        
        # Plotly를 이용한 동적 산점도 및 그래프 시각화
        fig = go.Figure()
        
        # 1. 실제 데이터 산점도
        fig.add_trace(go.Scatter(
            x=df['rackTotCnt'], y=df['parkingBikeTotCnt'],
            mode='markers', name='실제 따릉이 데이터',
            text=df['stationName'],
            marker=dict(color='darkcyan', size=8)
        ))
        
        # 2. 학생이 제안한 예측 직선
        x_range = np.linspace(df['rackTotCnt'].min() - 5, df['rackTotCnt'].max() + 5, 100)
        y_range_student = a_input * x_range + b_input
        fig.add_trace(go.Scatter(
            x=x_range, y=y_range_student,
            mode='lines', name='나의 예측 직선',
            line=dict(color='orange', width=3)
        ))
        
        # 3. AI의 최적 회귀 직선 (체크 시 활성화)
        if show_ai:
            y_range_ai = ai_a * x_range + ai_b
            fig.add_trace(go.Scatter(
                x=x_range, y=y_range_ai,
                mode='lines', name='AI 최적 직선 (경사하강법 결과)',
                line=dict(color='crimson', width=3, dash='dash')
            ))
            
        fig.update_layout(
            xaxis_title="거치대 개수 (rackTotCnt)",
            yaxis_title="주차된 자전거 수 (parkingBikeTotCnt)",
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

    # 3. 실시간 Raw Data 행렬 확인 탭
    st.write("---")
    st.header("🗂️ 실시간 수집된 데이터 행렬 (Matrix)")
    st.dataframe(df, use_container_width=True)

    # 4. 학생 탐구 질문 섹션
    st.write("---")
    st.header("🧠 수업 내 탐구 활동 및 토론 질문")
    
    with st.expander("❓ 질문 1. 오차를 그냥 더하지 않고 '제곱'해서 더하는(오차 제곱합) 수학적 이점은 무엇일까
