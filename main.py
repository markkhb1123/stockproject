import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 스타일
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --border: #1e1e2e;
    --accent: #00e5ff;
    --accent2: #ff6b35;
    --green: #00e676;
    --red: #ff1744;
    --text: #e8e8f0;
    --muted: #5a5a7a;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* 헤더 */
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    letter-spacing: 0.08em;
    background: linear-gradient(120deg, var(--accent), #7b61ff, var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-size: 0.85rem;
    color: var(--muted);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    font-weight: 300;
}

/* 메트릭 카드 */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
}
.metric-label {
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1;
}
.metric-delta-pos {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--green);
    margin-top: 0.2rem;
}
.metric-delta-neg {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--red);
    margin-top: 0.2rem;
}

/* 섹션 제목 */
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 0.1em;
    color: var(--accent);
    border-left: 3px solid var(--accent);
    padding-left: 0.7rem;
    margin: 1.5rem 0 1rem;
}

/* 태그 */
.tag {
    display: inline-block;
    background: rgba(0,229,255,0.1);
    border: 1px solid rgba(0,229,255,0.3);
    color: var(--accent);
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    padding: 0.15rem 0.6rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    margin-right: 0.3rem;
}
.tag-us {
    background: rgba(255,107,53,0.1);
    border-color: rgba(255,107,53,0.3);
    color: var(--accent2);
}

/* Streamlit 기본 위젯 스타일 덮어쓰기 */
.stMultiSelect [data-baseweb="tag"] {
    background-color: rgba(0,229,255,0.15) !important;
}
div[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
div[data-testid="stMetric"] label { color: var(--muted) !important; font-size: 0.75rem !important; }
div[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; }

/* 구분선 */
hr { border-color: var(--border) !important; }

/* 테이블 */
.stDataFrame { background: var(--surface) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 종목 데이터베이스
# ─────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "현대차": "005380.KS",
    "POSCO홀딩스": "005490.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "셀트리온": "068270.KS",
    "기아": "000270.KS",
    "KB금융": "105560.KS",
    "LG화학": "051910.KS",
    "삼성바이오로직스": "207940.KS",
    "KOSPI 지수": "^KS11",
    "KOSDAQ 지수": "^KQ11",
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan Chase": "JPM",
    "Visa": "V",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "Gold": "GC=F",
}

PERIOD_MAP = {
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
}

COLOR_PALETTE = [
    "#00e5ff", "#ff6b35", "#7b61ff", "#00e676",
    "#ffab40", "#f06292", "#4fc3f7", "#aed581",
    "#ff7043", "#26c6da", "#ab47bc", "#66bb6a",
]

# ─────────────────────────────────────────────
# 데이터 로딩
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_stock_data(tickers: list, period: str) -> dict:
    result = {}
    for ticker in tickers:
        try:
            data = yf.download(ticker, period=period, auto_adjust=True, progress=False)
            if not data.empty:
                result[ticker] = data
        except Exception:
            pass
    return result

@st.cache_data(ttl=300)
def get_stock_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        return info
    except Exception:
        return {}

def compute_returns(df: pd.DataFrame) -> pd.Series:
    close = df["Close"].squeeze()
    return (close / close.iloc[0] - 1) * 100

def get_current_price(df: pd.DataFrame) -> float:
    return float(df["Close"].squeeze().iloc[-1])

def get_daily_change(df: pd.DataFrame) -> float:
    close = df["Close"].squeeze()
    if len(close) < 2:
        return 0.0
    return float((close.iloc[-1] / close.iloc[-2] - 1) * 100)

def get_period_return(df: pd.DataFrame) -> float:
    close = df["Close"].squeeze()
    return float((close.iloc[-1] / close.iloc[0] - 1) * 100)

def get_volatility(df: pd.DataFrame) -> float:
    close = df["Close"].squeeze()
    daily_ret = close.pct_change().dropna()
    return float(daily_ret.std() * np.sqrt(252) * 100)

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:2rem">📈 STOCK<br>RADAR</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub" style="margin-bottom:1.5rem">글로벌 주식 비교 대시보드</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("### 🇰🇷 한국 주식")
    selected_kr = st.multiselect(
        "종목 선택",
        options=list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "KOSPI 지수"],
        key="kr_stocks",
        label_visibility="collapsed",
    )

    st.markdown("### 🇺🇸 미국 주식")
    selected_us = st.multiselect(
        "종목 선택",
        options=list(US_STOCKS.keys()),
        default=["NVIDIA", "Apple", "S&P 500"],
        key="us_stocks",
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### ⏱ 기간")
    period_label = st.select_slider(
        "기간 선택",
        options=list(PERIOD_MAP.keys()),
        value="1년",
        label_visibility="collapsed",
    )
    period = PERIOD_MAP[period_label]

    st.divider()
    st.markdown("### 📊 차트 옵션")
    chart_type = st.radio(
        "차트 타입",
        ["수익률 비교", "주가 추이", "캔들차트"],
        label_visibility="collapsed",
    )
    show_volume = st.checkbox("거래량 표시", value=False)

    st.divider()
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("데이터: Yahoo Finance")

# ─────────────────────────────────────────────
# 메인 콘텐츠
# ─────────────────────────────────────────────
st.markdown('<div class="hero-title">GLOBAL STOCK RADAR</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">한국 · 미국 주요 주식 실시간 비교 분석</div>', unsafe_allow_html=True)
st.markdown("")

# 선택 종목 준비
all_selected = []
ticker_name_map = {}
ticker_market_map = {}

for name in selected_kr:
    ticker = KR_STOCKS[name]
    all_selected.append(ticker)
    ticker_name_map[ticker] = name
    ticker_market_map[ticker] = "KR"

for name in selected_us:
    ticker = US_STOCKS[name]
    all_selected.append(ticker)
    ticker_name_map[ticker] = name
    ticker_market_map[ticker] = "US"

if not all_selected:
    st.warning("👈 사이드바에서 종목을 1개 이상 선택해주세요.")
    st.stop()

# 데이터 로딩
with st.spinner("시장 데이터 수신 중..."):
    stock_data = load_stock_data(all_selected, period)

loaded_tickers = list(stock_data.keys())
if not loaded_tickers:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
    st.stop()

# ─────────────────────────────────────────────
# 요약 메트릭 카드
# ─────────────────────────────────────────────
st.markdown(f'<div class="section-title">SNAPSHOT — {period_label}</div>', unsafe_allow_html=True)

metric_cols = st.columns(min(len(loaded_tickers), 4))
for i, ticker in enumerate(loaded_tickers):
    df = stock_data[ticker]
    name = ticker_name_map.get(ticker, ticker)
    market = ticker_market_map.get(ticker, "")
    ret = get_period_return(df)
    daily = get_daily_change(df)
    price = get_current_price(df)
    vol = get_volatility(df)

    with metric_cols[i % 4]:
        tag_class = "tag-us" if market == "US" else "tag"
        delta_class = "metric-delta-pos" if ret >= 0 else "metric-delta-neg"
        arrow = "▲" if ret >= 0 else "▼"
        daily_arrow = "▲" if daily >= 0 else "▼"
        daily_class = "metric-delta-pos" if daily >= 0 else "metric-delta-neg"

        st.markdown(f"""
        <div class="metric-card">
            <span class="{tag_class}">{market}</span>
            <div class="metric-label" style="margin-top:0.5rem">{name}</div>
            <div class="metric-value">{ret:+.2f}%</div>
            <div class="{delta_class}">{arrow} {abs(ret):.2f}% ({period_label})</div>
            <div class="{daily_class}" style="font-size:0.75rem">{daily_arrow} {abs(daily):.2f}% 일간변화</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

# ─────────────────────────────────────────────
# 메인 차트
# ─────────────────────────────────────────────
st.markdown(f'<div class="section-title">{chart_type.upper()}</div>', unsafe_allow_html=True)

colors = {ticker: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, ticker in enumerate(loaded_tickers)}

if chart_type == "수익률 비교":
    rows = 2 if show_volume else 1
    row_heights = [0.75, 0.25] if show_volume else [1]
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, row_heights=row_heights)

    for ticker in loaded_tickers:
        df = stock_data[ticker]
        returns = compute_returns(df)
        name = ticker_name_map.get(ticker, ticker)
        color = colors[ticker]
        market = ticker_market_map.get(ticker, "")
        display_name = f"{'🇰🇷' if market=='KR' else '🇺🇸'} {name}"

        fig.add_trace(go.Scatter(
            x=returns.index, y=returns.values,
            name=display_name,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{display_name}</b><br>날짜: %{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}%<extra></extra>",
        ), row=1, col=1)

        if show_volume and "Volume" in df.columns:
            volume = df["Volume"].squeeze()
            fig.add_trace(go.Bar(
                x=volume.index, y=volume.values,
                name=f"{name} 거래량",
                marker_color=color,
                opacity=0.4,
                showlegend=False,
            ), row=2, col=1)

    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.2)", row=1, col=1)
    fig.update_yaxes(title_text="수익률 (%)", row=1, col=1)
    if show_volume:
        fig.update_yaxes(title_text="거래량", row=2, col=1)

elif chart_type == "주가 추이":
    rows = 2 if show_volume else 1
    row_heights = [0.75, 0.25] if show_volume else [1]
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, row_heights=row_heights)

    for ticker in loaded_tickers:
        df = stock_data[ticker]
        close = df["Close"].squeeze()
        name = ticker_name_map.get(ticker, ticker)
        color = colors[ticker]
        market = ticker_market_map.get(ticker, "")
        display_name = f"{'🇰🇷' if market=='KR' else '🇺🇸'} {name}"

        fig.add_trace(go.Scatter(
            x=close.index, y=close.values,
            name=display_name,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{display_name}</b><br>날짜: %{{x|%Y-%m-%d}}<br>가격: %{{y:,.2f}}<extra></extra>",
        ), row=1, col=1)

        if show_volume and "Volume" in df.columns:
            volume = df["Volume"].squeeze()
            fig.add_trace(go.Bar(
                x=volume.index, y=volume.values,
                name=f"{name} 거래량",
                marker_color=color,
                opacity=0.4,
                showlegend=False,
            ), row=2, col=1)

    fig.update_yaxes(title_text="주가", row=1, col=1)

elif chart_type == "캔들차트":
    # 캔들차트는 종목 1개씩 탭으로 표시
    tabs = st.tabs([f"{'🇰🇷' if ticker_market_map.get(t,'')=='KR' else '🇺🇸'} {ticker_name_map.get(t, t)}" for t in loaded_tickers])
    for tab, ticker in zip(tabs, loaded_tickers):
        with tab:
            df = stock_data[ticker]
            name = ticker_name_map.get(ticker, ticker)
            market = ticker_market_map.get(ticker, "")
            color = colors[ticker]

            rows = 2 if show_volume else 1
            row_heights = [0.75, 0.25] if show_volume else [1]
            cfig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                                 vertical_spacing=0.04, row_heights=row_heights)

            open_ = df["Open"].squeeze() if "Open" in df.columns else df["Close"].squeeze()
            high_ = df["High"].squeeze() if "High" in df.columns else df["Close"].squeeze()
            low_ = df["Low"].squeeze() if "Low" in df.columns else df["Close"].squeeze()
            close_ = df["Close"].squeeze()

            cfig.add_trace(go.Candlestick(
                x=close_.index,
                open=open_, high=high_, low=low_, close=close_,
                increasing_line_color="#00e676",
                decreasing_line_color="#ff1744",
                name=name,
            ), row=1, col=1)

            # 20일 이동평균
            ma20 = close_.rolling(20).mean()
            ma60 = close_.rolling(60).mean()
            cfig.add_trace(go.Scatter(x=ma20.index, y=ma20.values,
                                      line=dict(color="#ffab40", width=1.5, dash="dot"),
                                      name="MA20"), row=1, col=1)
            cfig.add_trace(go.Scatter(x=ma60.index, y=ma60.values,
                                      line=dict(color="#4fc3f7", width=1.5, dash="dot"),
                                      name="MA60"), row=1, col=1)

            if show_volume and "Volume" in df.columns:
                volume = df["Volume"].squeeze()
                cfig.add_trace(go.Bar(
                    x=volume.index, y=volume.values,
                    marker_color=color, opacity=0.5,
                    name="거래량", showlegend=False,
                ), row=2, col=1)

            cfig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(10,10,20,0.8)",
                font=dict(family="DM Sans", color="#e8e8f0"),
                xaxis_rangeslider_visible=False,
                legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
                hovermode="x unified",
                height=520,
                margin=dict(l=0, r=0, t=20, b=0),
            )
            cfig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.1)")
            cfig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.1)")

            st.plotly_chart(cfig, use_container_width=True)
    fig = None  # 이미 렌더링 완료

if chart_type != "캔들차트":
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,10,20,0.8)",
        font=dict(family="DM Sans", color="#e8e8f0"),
        legend=dict(
            bgcolor="rgba(18,18,26,0.9)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        ),
        hovermode="x unified",
        height=500 if not show_volume else 620,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.1)")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 성과 비교 테이블
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">PERFORMANCE TABLE</div>', unsafe_allow_html=True)

table_data = []
for ticker in loaded_tickers:
    df = stock_data[ticker]
    name = ticker_name_map.get(ticker, ticker)
    market = ticker_market_map.get(ticker, "")
    close = df["Close"].squeeze()

    ret_1m = get_period_return(yf.download(ticker, period="1mo", auto_adjust=True, progress=False)) if period != "1mo" else get_period_return(df)
    ret_total = get_period_return(df)
    daily = get_daily_change(df)
    vol = get_volatility(df)
    price = get_current_price(df)
    drawdown = float(((close / close.cummax()) - 1).min() * 100)

    table_data.append({
        "시장": "🇰🇷 KR" if market == "KR" else "🇺🇸 US",
        "종목": name,
        "현재가": f"{price:,.2f}",
        f"수익률 ({period_label})": f"{ret_total:+.2f}%",
        "일간 변화": f"{daily:+.2f}%",
        "연간변동성": f"{vol:.1f}%",
        "최대낙폭 (MDD)": f"{drawdown:.2f}%",
    })

table_df = pd.DataFrame(table_data)

def color_ret(val):
    if "+" in str(val):
        return "color: #00e676; font-weight:600"
    elif "-" in str(val):
        return "color: #ff1744; font-weight:600"
    return ""

styled = table_df.style.applymap(
    color_ret,
    subset=[f"수익률 ({period_label})", "일간 변화", "최대낙폭 (MDD)"]
).set_properties(**{
    "background-color": "#12121a",
    "color": "#e8e8f0",
    "border": "1px solid #1e1e2e",
}).set_table_styles([
    {"selector": "th", "props": [
        ("background-color", "#0a0a0f"),
        ("color", "#00e5ff"),
        ("font-family", "'Bebas Neue', sans-serif"),
        ("letter-spacing", "0.1em"),
        ("font-size", "0.85rem"),
    ]},
])

st.dataframe(table_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# 상관관계 히트맵
# ─────────────────────────────────────────────
if len(loaded_tickers) >= 2:
    st.markdown('<div class="section-title">CORRELATION MATRIX</div>', unsafe_allow_html=True)

    ret_df = pd.DataFrame()
    for ticker in loaded_tickers:
        close = stock_data[ticker]["Close"].squeeze()
        ret_df[ticker_name_map.get(ticker, ticker)] = close.pct_change()

    corr = ret_df.corr()

    hfig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale=[[0, "#ff1744"], [0.5, "#12121a"], [1, "#00e5ff"]],
        zmin=-1, zmax=1,
    )
    hfig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#e8e8f0", size=12),
        height=420,
        margin=dict(l=0, r=0, t=20, b=0),
        coloraxis_colorbar=dict(
            tickfont=dict(color="#e8e8f0"),
            title=dict(text="상관계수", font=dict(color="#e8e8f0")),
        ),
    )
    hfig.update_traces(textfont=dict(color="white", size=11))
    st.plotly_chart(hfig, use_container_width=True)

# ─────────────────────────────────────────────
# 리스크-수익률 산점도
# ─────────────────────────────────────────────
if len(loaded_tickers) >= 2:
    st.markdown('<div class="section-title">RISK — RETURN MATRIX</div>', unsafe_allow_html=True)

    scatter_data = []
    for ticker in loaded_tickers:
        df = stock_data[ticker]
        market = ticker_market_map.get(ticker, "")
        scatter_data.append({
            "종목": ticker_name_map.get(ticker, ticker),
            "수익률 (%)": get_period_return(df),
            "연간변동성 (%)": get_volatility(df),
            "시장": "한국" if market == "KR" else "미국",
            "색상": "#00e5ff" if market == "KR" else "#ff6b35",
        })

    sdf = pd.DataFrame(scatter_data)

    sfig = px.scatter(
        sdf,
        x="연간변동성 (%)", y="수익률 (%)",
        text="종목",
        color="시장",
        color_discrete_map={"한국": "#00e5ff", "미국": "#ff6b35"},
        size=[20] * len(sdf),
    )
    sfig.update_traces(textposition="top center", textfont=dict(size=11, color="white"))
    sfig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.2)")
    sfig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,10,20,0.8)",
        font=dict(family="DM Sans", color="#e8e8f0"),
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(bgcolor="rgba(18,18,26,0.9)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
    )
    sfig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", title="리스크 (연간변동성 %)")
    sfig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", title="수익률 (%)")
    st.plotly_chart(sfig, use_container_width=True)

# ─────────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#5a5a7a; font-size:0.75rem; letter-spacing:0.15em; padding:1rem 0">
    GLOBAL STOCK RADAR &nbsp;|&nbsp; DATA: YAHOO FINANCE &nbsp;|&nbsp; FOR INFORMATIONAL PURPOSES ONLY
</div>
""", unsafe_allow_html=True)
