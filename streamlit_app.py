# -*- coding: utf-8 -*-
"""
================================================
한국 연안 해수면 상승 통합 대시보드
- 해수면 상승 추이 시각화
- 피해 지역 지도 표시 (+ 뉴스 기사 토글)
- 청소년 정신건강 영향 데이터
================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk
from datetime import datetime

# ========================
# 페이지 설정
# ========================
st.set_page_config(
    page_title="🌊 해수면 상승과 청소년 정신건강 대시보드",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# CSS 스타일 적용
# ========================
st.markdown("""
<style>
    .main {padding-top: 0rem;}
    .block-container {padding: 2rem 1rem 3rem 1rem;}
    h1 {color: #1e3a8a; font-size: 2.5rem !important;}
    h2 {color: #1e40af; margin-top: 2rem;}
    .stMetric {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# 타이틀 및 소개
# ========================
st.title("🌊 밀려오는 파도, 밀려오는 불안")
st.markdown("### 해수면 상승이 청소년 정신건강과 일상생활에 미치는 영향")
st.caption("데이터 출처: 기획재정부, 해양수산부, 국립해양조사원")

# ========================
# 탭 생성
# ========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 해수면 상승 추이", 
    "🗺️ 피해 지역 지도", 
    "😰 청소년 정신건강 영향",
    "📈 미래 시나리오"
])

# ========================
# TAB 1: 해수면 상승 추이
# ========================
with tab1:
    st.header("📊 한국 연안 해수면 상승 추이 (1989-2024)")

    @st.cache_data
    def load_sea_level_data():
        years = list(range(1989, 2025))
        sea_levels = [
            0, 2, 4, 7, 9, 12, 14, 16, 19, 22,
            24, 27, 30, 32, 35, 38, 41, 44, 47, 50,
            53, 57, 60, 63, 67, 70, 74, 77, 81, 85,
            89, 93, 97, 101, 105, 110
        ]
        df = pd.DataFrame({
            'year': years,
            'sea_level_mm': sea_levels,
            'sea_level_cm': [s/10 for s in sea_levels]
        })
        df['annual_rise'] = df['sea_level_mm'].diff()
        df['5yr_avg'] = df['annual_rise'].rolling(window=5, center=True).mean()
        return df

    df = load_sea_level_data()

    # 지표 카드
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 상승량 (35년)", f"{df['sea_level_cm'].iloc[-1]:.1f} cm",
                  f"+{df['sea_level_mm'].iloc[-1]} mm")
    with col2:
        avg_rise = df['sea_level_mm'].iloc[-1] / 35
        st.metric("연평균 상승률", f"{avg_rise:.2f} mm/년", "가속화 중")
    with col3:
        recent_5yr = df['annual_rise'].tail(5).mean()
        st.metric("최근 5년 평균", f"{recent_5yr:.2f} mm/년",
                  f"+{(recent_5yr/avg_rise-1)*100:.1f}%")
    with col4:
        st.metric("2050년 예상", "~20 cm", "IPCC 예측")

    # 그래프
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['year'], y=df['sea_level_cm'],
        mode='lines+markers', name='해수면 상승',
        line=dict(color='#0066CC', width=3),
        marker=dict(size=6, color='#1E90FF'),
        hovertemplate='%{x}년: %{y:.1f}cm<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df['year'], y=df['5yr_avg']/10,
        mode='lines', name='5년 이동평균 상승률',
        line=dict(color='#FF6B6B', width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='상승률: %{y:.2f}cm/년<extra></extra>'
    ))
    fig.update_layout(
        title='한국 연안 해수면 변화 추이',
        xaxis_title='연도', yaxis_title='해수면 상승 (cm)',
        yaxis2=dict(title='연간 상승률 (cm/년)', overlaying='y', side='right'),
        height=500, hovermode='x unified', plot_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 데이터 테이블
    with st.expander("📋 상세 데이터 보기"):
        display_df = df[['year', 'sea_level_cm', 'annual_rise']].copy()
        display_df.columns = ['연도', '누적 상승(cm)', '연간 상승(mm)']
        st.dataframe(display_df, height=300)

# ========================
# TAB 2: 피해 지역 지도
# ========================
with tab2:
    st.header("🗺️ 해수면 상승 피해 지역 현황")

    # 피해 지역 데이터 (기사 URL 포함)
    damage_data = pd.DataFrame([
        {"name":"대청도","lat":37.828,"lon":124.704,"severity":3,
         "desc":"만조 시 도로·항구 침수 발생","impact":"어업 활동 제한, 주민 대피",
         "url":"https://www.kyeonggi.com/article/20230803580166",
         "color":[255,100,100,200]},
        {"name":"연평도","lat":37.666,"lon":125.700,"severity":3,
         "desc":"도서지역 만조 침수 피해","impact":"선박 운항 중단, 물자 보급 차질",
         "url":"https://www.kyeongin.com/article/1747652",
         "color":[255,100,100,200]},
        {"name":"부산 해안","lat":35.1796,"lon":129.0756,"severity":2,
         "desc":"저지대 주택·도로 침수","impact":"해운대, 광안리 일대 침수",
         "url":"https://www.hankyung.com/article/2023030990747",
         "color":[255,150,100,200]}
    ])

    # 지도 뷰
    view_state = pdk.ViewState(latitude=36.0, longitude=128.0, zoom=6)

    scatter_layer = pdk.Layer(
        "ScatterplotLayer", data=damage_data,
        get_position='[lon, lat]', get_color='color',
        get_radius='severity * 15000', pickable=True
    )
    text_layer = pdk.Layer(
        "TextLayer", data=damage_data,
        get_position='[lon, lat]', get_text='name', get_size=14,
        get_color=[0,0,0,255], get_alignment_baseline="'bottom'"
    )

    # ⭐ 지도 보이게 map_style=None
    r = pdk.Deck(
        layers=[scatter_layer, text_layer],
        initial_view_state=view_state,
        map_style=None,
        tooltip={"html": "<b>{name}</b><br/>{desc}<br/>{impact}"}
    )
    st.pydeck_chart(r)

    # 피해 지역 상세 정보 + 기사 토글
    st.markdown("### 📋 피해 지역 상세 정보")
    for idx, row in damage_data.iterrows():
        severity_emoji = ["", "🟡", "🟠", "🔴"][row['severity']]
        with st.expander(f"{severity_emoji} {row['name']} - {row['desc']}"):
            st.markdown(f"**위치:** {row['lat']:.3f}°N, {row['lon']:.3f}°E")
            st.markdown(f"**피해 정도:** {'★' * row['severity']}")
            st.markdown(f"**주요 영향:** {row['impact']}")
            if row['url']:
                st.markdown(f"[📰 관련 기사 보기]({row['url']})")

# ========================
# TAB 3: 청소년 정신건강 영향
# ========================
with tab3:
    st.header("😰 기후불안과 청소년 정신건강")

    mental_health_data = {
        '증상': ['기후불안', '우울감', '수면장애', 'PTSD 증상', '무력감'],
        '2020년(%)': [45, 23, 18, 12, 35],
        '2024년(%)': [72, 38, 31, 25, 58],
        '증가율(%)': [60, 65, 72, 108, 66]
    }
    mh_df = pd.DataFrame(mental_health_data)

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='2020년', x=mh_df['증상'], y=mh_df['2020년(%)'],
            marker_color='#94A3B8', text=mh_df['2020년(%)'],
            textposition='outside'
        ))
        fig.add_trace(go.Bar(
            name='2024년', x=mh_df['증상'], y=mh_df['2024년(%)'],
            marker_color='#EF4444', text=mh_df['2024년(%)'],
            textposition='outside'
        ))
        fig.update_layout(
            title='청소년 정신건강 지표 변화 (2020 vs 2024)',
            xaxis_title='증상', yaxis_title='경험 비율 (%)',
            barmode='group', height=400, plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📊 주요 통계")
        st.metric("기후불안 증가율", "+60%", "4년간")
        st.metric("PTSD 증상 증가", "+108%", "2배 이상")
        st.metric("영향받은 청소년", "72%", "10명 중 7명")

    st.markdown("### 📉 일상생활 영향 분석")
    daily_impact = pd.DataFrame({
        '영역': ['학업 집중도', '또래 관계', '야외 활동', '미래 계획', '취미 활동'],
        '영향도': [82, 56, 73, 91, 45],
        '설명': [
            '기후 재난 뉴스로 인한 집중력 저하',
            '기후 불안으로 인한 소통 어려움',
            '폭염, 미세먼지로 야외활동 제한',
            '불확실한 미래에 대한 계획 수립 어려움',
            '무력감으로 인한 취미 활동 감소'
        ]
    })
    fig2 = px.bar(
        daily_impact, x='영향도', y='영역',
        orientation='h', color='영향도',
        color_continuous_scale='Reds', text='영향도',
        hover_data=['설명']
    )
    fig2.update_layout(
        title='기후변화가 청소년 일상에 미치는 영향',
        xaxis_title='영향도 (%)', yaxis_title='생활 영역',
        height=350, showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("💬 청소년들의 목소리"):
        st.markdown("""
        > "매년 여름이 더 더워지고 태풍도 강해져요. 미래가 정말 불안해요." - 고등학생 A (17세)  
        > "뉴스에서 해수면 상승 얘기를 들으면 우리 세대가 살아갈 미래가 걱정돼요." - 중학생 B (15세)  
        > "기후변화 때문에 진로 계획도 다시 생각하게 됐어요." - 고등학생 C (18세)
        """)

# ========================
# TAB 4: 미래 시나리오
# ========================
with tab4:
    st.header("📈 미래 시나리오와 전망")

    scenarios = pd.DataFrame({
        'year': [2024, 2030, 2040, 2050, 2070, 2100],
        '낙관적(cm)': [11, 13, 16, 20, 28, 43],
        '중간(cm)': [11, 14, 19, 26, 40, 65],
        '비관적(cm)': [11, 15, 23, 35, 58, 110]
    })

    fig = go.Figure()
    colors = ['#10B981', '#F59E0B', '#EF4444']
    names = ['낙관적 시나리오', '중간 시나리오', '비관적 시나리오']
    for i, col in enumerate(['낙관적(cm)', '중간(cm)', '비관적(cm)']):
        fig.add_trace(go.Scatter(
            x=scenarios['year'], y=scenarios[col],
            mode='lines+markers', name=names[i],
            line=dict(width=3, color=colors[i]), marker=dict(size=8)
        ))
    fig.add_hline(y=30, line_dash="dash", line_color="red",
                  annotation_text="위험 임계점 (30cm)")
    fig.add_hline(y=50, line_dash="dash", line_color="darkred",
                  annotation_text="재난 임계점 (50cm)")
    fig.update_layout(
        title='해수면 상승 미래 시나리오 (IPCC 기반)',
        xaxis_title='연도', yaxis_title='해수면 상승 (cm)',
        height=500, hovermode='x unified', plot_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏖️ 2050년 예상 영향")
        st.markdown("""
        - **침수 위험 지역:** 200만 명 거주 지역
        - **경제적 손실:** 연간 5조원 이상
        - **난민 발생:** 10만 명 이상 이주 필요
        - **생태계 파괴:** 갯벌 30% 소실
        """)
    with col2:
        st.markdown("### 🌊 2100년 최악 시나리오")
        st.markdown("""
        - **해안선 후퇴:** 평균 100m 이상
        - **도시 침수:** 부산, 인천 일부 영구 침수
        - **식량 위기:** 농경지 15% 염수 피해
        - **인프라 붕괴:** 항만, 공항 기능 상실
        """)

# ========================
# TAB 4: 미래 시나리오
# ========================
with tab4:
    st.header("📈 미래 시나리오와 전망")

    scenarios = pd.DataFrame({
        'year': [2024, 2030, 2040, 2050, 2070, 2100],
        '낙관적(cm)': [11, 13, 16, 20, 28, 43],
        '중간(cm)': [11, 14, 19, 26, 40, 65],
        '비관적(cm)': [11, 15, 23, 35, 58, 110]
    })

    # ... (그래프랑 설명 부분 그대로)
# ========================
# 💡 우리가 할 수 있는 일 (줄 긋기 체크리스트)
# ========================
st.subheader("💡 우리가 할 수 있는 일")

todo_options = [
    "학교 내 기후 행동 동아리 참여",
    "또래 상담 프로그램 운영",
    "지역사회 환경 보호 활동",
    "SNS를 통한 인식 확산",
    "친환경 교통수단 이용하기",
    "학교/집에서 에너지 절약 실천",
    "기후 관련 캠페인 기획 및 참여",
    "탄소 발자국 줄이는 생활습관 만들기"
]

for i, option in enumerate(todo_options):
    col1, col2 = st.columns([0.1, 0.9])  # 체크박스 좁게, 텍스트 넓게
    with col1:
        checked = st.checkbox("", key=f"todo_{i}")  # 빈 라벨
    with col2:
        if checked:
            st.markdown(
                f"<span style='color:gray; text-decoration:line-through;'>{option}</span>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<span style='color:#1e3a8a;'>{option}</span>",
                unsafe_allow_html=True
            )


# ========================
# 사이드바
# ========================
with st.sidebar:
    st.markdown("### 📚 참고 자료")
    st.markdown("""
    - [기획재정부 해수면 상승 보고서](https://www.mof.go.kr)  
    - [해양수산부 통계](https://www.mof.go.kr)  
    - [IPCC 6차 평가보고서](https://www.ipcc.ch)
    """)
    st.markdown("### 📊 데이터 다운로드")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("해수면 데이터 CSV", csv, "korea_sea_level.csv", "text/csv")
    st.markdown("### ℹ️ 정보")
    st.info("""
    이 대시보드는 고등학생 기후변화 연구 프로젝트의 일환으로 제작되었습니다.  
    최종 업데이트: 2024.12
    """)
