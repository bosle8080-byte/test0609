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
        
        # 3. AI 정답 직선 플로팅 (활성화 시)
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

    # 3. 데이터프레임 노출
    st.write("---")
    st.header("🗂️ 실시간 수집된 데이터 행렬 (Matrix)")
    st.dataframe(df, use_container_width=True)

    # 4. 토론 문항 탭 구성
    st.write("---")
    st.header("🧠 수업 내 탐구 활동 및 토론 질문")
    
    with st.expander("❓ 질문 1. 오차를 그냥 더하지 않고 '제곱'해서 더하는(오차 제곱합) 수학적 이점은 무엇일까?"):
        st.write("**힌트 및 답변 가이드:**")
        st.write("1. 부호 제거: 실제 값보다 예측값이 크거나 작을 때 발생하는 양수/음수 오차가 서로 상쇄되는 것을 막아줍니다. 절댓값과 달리 전 구간 미분이 가능하다는 장점이 있습니다.")
        st.write("2. 큰 오차에 패널티 부여: 오차가 1일 때 제곱하면 1이지만, 오차가 4일 때 제곱하면 16이 됩니다. 모델이 터무니없는 대형 예측 오차를 내지 않도록 수학적으로 규제하는 효과가 있습니다.")
        st.write("3. 최적화 용이성: 제곱함수는 부드러운 곡선 형태를 가지므로 미분이 용이하여 경사하강법 알고리즘을 적용하기에 매우 유리합니다.")
        
    with st.expander("❓ 질문 2. 이차함수 형태의 손실함수 그래프에서 최솟값(꼭짓점)을 찾기 위해 순간변화율(미분계수)을 어떻게 이용할까?"):
        st.write("**힌트 및 답변 가이드:**")
        st.write("1. 선형 회귀의 손실함수(MSE) 그래프는 아래로 볼록한 그릇 모양(이차 곡선 형태)을 가집니다.")
        st.write("2. 오차가 최소가 되는 지점은 그릇의 가장 바닥(꼭짓점)이며, 수학적으로 이 지점의 접선 기울기인 순간변화율(미분계수)은 정확히 0이 됩니다.")
        st.write("3. 인공지능은 현재 위치에서 미분을 계산하여 기울기가 양수이면 음의 방향으로, 음수이면 양의 방향으로 가중치를 조금씩 이동시키며 기울기가 0인 최적 지점으로 다가갑니다.")

    with st.expander("❓ 질문 3. 학습률(Learning Rate)이 너무 크거나 작을 때 완벽한 모델을 위해 이를 어떻게 조율해야 할까?"):
        st.write("**힌트 및 답변 가이드:**")
        st.write("1. 학습률이 너무 크면: 한 걸음의 보폭이 너무 커서 바닥(최솟값)을 지나치고 반대편 벽으로 튕겨 나가는 오버슈팅(Overshooting)이 발생하여 모델이 발산합니다.")
        st.write("2. 학습률이 너무 작으면: 보폭이 너무 작아 미분계수가 0인 지점까지 가는 데 너무 오랜 시간이 걸려 연산 효율이 극도로 떨어집니다.")
        st.write("3. 조율 방법: 학습 초기에는 보폭을 크게 조절하다가 최솟값에 가까워질수록 보폭을 서서히 줄여나가는 스케줄링(Learning Rate Decay) 기법이나, Adam 같은 적응형 최적화(Optimizer) 알고리즘을 사용합니다.")
