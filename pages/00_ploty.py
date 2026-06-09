import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="글로벌 Top 10 주식 대시보드",
    page_icon="📈",
    layout="wide"
)

st.title("📈 글로벌 시가총액 Top 10 주식 대시보드")
st.markdown("야후 파이낸스(yfinance) 데이터를 활용한 최근 1개년 주가 추이 및 수익률 비교 대시보드입니다.")

# 글로벌 시가총액 Top 10 기업 지정 (티커 기준)
TOP_10_STOCKS = {
    "Microsoft (MSFT)": "MSFT",
    "Apple (AAPL)": "AAPL",
    "NVIDIA (NVDA)": "NVDA",
    "Alphabet / Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Saudi Aramco (2222.SR)": "2222.SR",
    "Meta Platforms (META)": "META",
    "TSMC (TSM)": "TSM",
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "Tesla (TSLA)": "TSLA"
}

# 사이드바 설정
st.sidebar.header("⚙️ 설정 항목")
selected_companies = st.sidebar.multiselect(
    "시각화할 기업을 선택하세요 (기본 전체 선택)",
    options=list(TOP_10_STOCKS.keys()),
    default=list(TOP_10_STOCKS.keys())
)

# 데이터 기준일 계산 (최근 1년)
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

# 데이터 로드 함수 (캐싱 처리로 속도 향상)
@st.cache_data(ttl=3600)  # 1시간 동안 캐시 유지
def load_data(tickers):
    data = yf.download(tickers, start=start_date, end=end_date)
    # yfinance 결과에서 Close 컬럼만 추출
    if 'Close' in data.columns:
        return data['Close']
    return pd.DataFrame()

if selected_companies:
    # 선택된 기업의 티커 리스트 추출
    tickers_to_fetch = [TOP_10_STOCKS[name] for name in selected_companies]
    
    with st.spinner('야후 파이낸스에서 데이터를 불러오는 중입니다...'):
        df = load_data(tickers_to_fetch)
    
    if not df.empty:
        # 데이터프레임 단일 티커 예외 처리 (1개 선택 시 Series로 반환되는 경우 방지)
        if len(tickers_to_fetch) == 1:
            df = df.to_frame(name=tickers_to_fetch[0])
            
        # 탭 레이아웃 구성
        tab1, tab2, tab3 = st.tabs(["📊 주가 추이 (정규화)", "💰 실제 종가 추이", "📋 최근 데이터 테이블"])
        
        with tab1:
            st.subheader("1년 전 기준 누적 수익률 비교 (%)")
            st.caption("시작일(1년 전) 주가를 100으로 맞추어 어떤 주식이 가장 많이 올랐는지 비교합니다.")
            
            # 정규화 (누적 수익률 계산: (현재가 / 시작가) * 100 - 100)
            df_normalized = (df / df.iloc[0] - 1) * 100
            
            fig_norm = go.Figure()
            for col in df_normalized.columns:
                # 티커명을 기업명으로 매핑
                display_name = [k for k, v in TOP_10_STOCKS.items() if v == col][0]
                # ERROR FIX: mode를 'l'에서 'lines'로 수정 완료
                fig_norm.add_trace(go.Scatter(x=df_normalized.index, y=df_normalized[col], mode='lines', name=display_name))
            
            fig_norm.update_layout(
                xaxis_title="날짜",
                yaxis_title="수익률 (%)",
                hovermode="x unified",
                template="plotly_white",
                height=600
            )
            st.plotly_chart(fig_norm, use_container_width=True)
            
        with tab2:
            st.subheader("실제 주가 추이 (USD / SAR)")
            st.caption("각 주식의 실제 종가 추이입니다. (아람코는 사우디 리얄(SAR), 나머지는 달러(USD) 기준)")
            
            fig_close = go.Figure()
            for col in df.columns:
                display_name = [k for k, v in TOP_10_STOCKS.items() if v == col][0]
                # ERROR FIX: mode를 'l'에서 'lines'로 수정 완료
                fig_close.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=display_name))
                
            fig_close.update_layout(
                xaxis_title="날짜",
                yaxis_title="주가",
                hovermode="x unified",
                template="plotly_white",
                height=600
            )
            st.plotly_chart(fig_close, use_container_width=True)
            
        with tab3:
            st.subheader("가장 최근 10영업일 종가 데이터")
            # 디스플레이용 이름으로 컬럼 변경
            df_display = df.copy()
            df_display.columns = [[k for k, v in TOP_10_STOCKS.items() if v == col][0] for col in df_display.columns]
            st.dataframe(df_display.tail(10).round(2), use_container_width=True)
            
    else:
        st.error("데이터를 불러오지 못했습니다. 티커를 확인하거나 잠시 후 다시 시도해주세요.")
else:
    st.warning("왼쪽 사이드바에서 기업을 하나 이상 선택해주세요.")
