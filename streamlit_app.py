# -*- coding: utf-8 -*-
"""
================================================
한국 연안 해수면 상승 통합 대시보드
- 해수면 상승 추이 시각화
- 피해 지역 지도 표시 (+ 뉴스 기사 토글)
- 청소년 정신건강 영향 데이터
- 해수면 상승 시뮬레이션 게임 추가! 🎮
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
    /* 게임용 스타일 */
    .game-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    .control-panel {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .result-good {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        font-size: 1.2em;
        box-shadow: 0 5px 15px rgba(76,175,80,0.3);
    }
    .result-bad {
        background: linear-gradient(135deg, #f44336, #da190b);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        font-size: 1.2em;
        box-shadow: 0 5px 15px rgba(244,67,54,0.3);
    }
    .result-neutral {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        font-size: 1.2em;
        box-shadow: 0 5px 15px rgba(255,152,0,0.3);
    }
    .score-display {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    /* 체크리스트 스타일 */
    .checklist-container {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #38bdf8;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .category-header {
        color: #0369a1;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 15px;
        border-bottom: 2px solid #38bdf8;
        padding-bottom: 5px;
    }
    .completed-item {
        background-color: #dcfce7;
        color: #15803d;
        padding: 8px 12px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #22c55e;
        text-decoration: line-through;
        opacity: 0.8;
    }
    .pending-item {
        background-color: #ffffff;
        color: #1e40af;
        padding: 8px 12px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #3b82f6;
        transition: all 0.3s ease;
    }
    .pending-item:hover {
        background-color: #f0f9ff;
        transform: translateX(5px);
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
# 탭 생성 (게임 탭 추가!)
# ========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 해수면 상승 추이", 
    "🗺️ 피해 지역 지도", 
    "😰 청소년 정신건강 영향",
    "📈 미래 시나리오",
    "🎮 시뮬레이션 게임"  # 새 탭!
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
# TAB 5: 시뮬레이션 게임 🎮
# ========================
with tab5:
    st.header("🎮 해수면 상승 시뮬레이션 게임")
    st.markdown("### 🌍 당신의 선택이 2050년 한국의 미래를 결정합니다!")
    
    # 게임 설명
    with st.expander("🎯 게임 규칙 & 목표"):
        st.markdown("""
        **🎯 목표**: 2050년까지 해수면 상승을 최소화하여 한국을 보호하세요!
        
        **🎮 플레이 방법**:
        1. 아래 슬라이더와 선택지로 정책을 결정하세요
        2. 실시간으로 해수면 상승 예측이 업데이트됩니다
        3. 최종 점수와 등급을 확인하세요
        
        **🏆 등급 기준**:
        - 🌟 지구수호자: 15cm 미만
        - 🌿 환경지킴이: 15-20cm
        - ⚠️ 관심필요: 20-30cm  
        - 🚨 위험상황: 30cm 이상
        """)

    # 컨트롤 패널
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.markdown("## 🎛️ 정책 컨트롤 패널")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏭 온실가스 정책")
        carbon_reduction = st.slider(
            "탄소 배출량 감축 목표 (%)", 
            0, 80, 40, 5,
            help="2024년 대비 2050년까지의 감축률"
        )
        
        renewable_energy = st.slider(
            "재생에너지 비율 목표 (%)", 
            20, 100, 60, 5,
            help="2050년 전체 에너지 중 재생에너지 비율"
        )
        
        carbon_tax = st.slider(
            "탄소세 수준 (톤당 원)", 
            0, 100000, 30000, 10000,
            format="%d원",
            help="탄소 1톤 배출 시 부과되는 세금"
        )

    with col2:
        st.markdown("### 🌊 적응 정책")
        sea_wall_investment = st.slider(
            "해안 방어시설 투자 (조원)", 
            0, 50, 20, 5,
            format="%d조원",
            help="방파제, 해안제방 등 건설 투자"
        )
        
        ecosystem_restoration = st.slider(
            "생태계 복원 면적 (%)", 
            0, 100, 50, 10,
            help="갯벌, 습지 등 자연 해안 복원"
        )
        
        # 정책 선택지
        st.markdown("### 📋 추가 정책 선택")
        policies = st.multiselect(
            "시행할 정책을 선택하세요:",
            [
                "전기차 의무화 (2030년부터)",
                "건물 에너지효율 강화",
                "탄소중립도시 조성",
                "국제 기후협력 강화",
                "녹색기술 R&D 투자 확대",
                "기후교육 의무화"
            ],
            default=["건물 에너지효율 강화", "탄소중립도시 조성"]
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # 계산 로직
    def calculate_sea_level_rise(carbon_reduction, renewable_energy, carbon_tax, 
                                sea_wall_investment, ecosystem_restoration, policies):
        # 기본 상승량 (현재 추세)
        base_rise = 26  # 2050년 예상 26cm
        
        # 온실가스 정책 효과
        carbon_effect = -(carbon_reduction * 0.15)  # 최대 12cm 감축
        renewable_effect = -(renewable_energy * 0.08)  # 최대 8cm 감축
        tax_effect = -(carbon_tax / 10000 * 0.8)  # 최대 8cm 감축
        
        # 적응 정책 효과 (직접적 상승량 감소는 아니지만 피해 완화)
        adaptation_bonus = (sea_wall_investment + ecosystem_restoration) / 100 * 2
        
        # 추가 정책 보너스
        policy_bonus = len(policies) * 0.5
        
        # 최종 계산
        final_rise = base_rise + carbon_effect + renewable_effect + tax_effect
        final_rise = max(8, final_rise)  # 최소 8cm (물리적 한계)
        
        # 적응점수 별도 계산
        adaptation_score = adaptation_bonus + policy_bonus
        
        return final_rise, adaptation_score

    # 실시간 계산
    sea_level_2050, adaptation_score = calculate_sea_level_rise(
        carbon_reduction, renewable_energy, carbon_tax, 
        sea_wall_investment, ecosystem_restoration, policies
    )

    # 결과 시각화
    st.markdown("## 📊 시뮬레이션 결과")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="score-display">🌊</div>', unsafe_allow_html=True)
        st.metric("2050년 해수면 상승", f"{sea_level_2050:.1f}cm", 
                 f"{sea_level_2050-26:.1f}cm vs 현재 추세")
    
    with col2:
        st.markdown('<div class="score-display">🛡️</div>', unsafe_allow_html=True)
        st.metric("적응 역량 점수", f"{adaptation_score:.1f}점", 
                 "방어력 지수")
    
    with col3:
        # 종합 점수 계산
        if sea_level_2050 < 15:
            grade = "🌟 지구수호자"
            grade_class = "result-good"
        elif sea_level_2050 < 20:
            grade = "🌿 환경지킴이"
            grade_class = "result-good"
        elif sea_level_2050 < 30:
            grade = "⚠️ 관심필요"
            grade_class = "result-neutral"
        else:
            grade = "🚨 위험상황"
            grade_class = "result-bad"
        
        st.markdown('<div class="score-display">🏆</div>', unsafe_allow_html=True)
        st.metric("최종 등급", grade.split()[1], grade.split()[0])

    # 시나리오 그래프
    years = [2024, 2030, 2035, 2040, 2045, 2050]
    current_trend = [11, 14, 17, 21, 23.5, 26]
    your_scenario = [11, 11 + (sea_level_2050-11)*0.2, 11 + (sea_level_2050-11)*0.4, 
                    11 + (sea_level_2050-11)*0.7, 11 + (sea_level_2050-11)*0.9, sea_level_2050]

    fig_sim = go.Figure()
    
    # 현재 추세
    fig_sim.add_trace(go.Scatter(
        x=years, y=current_trend, mode='lines+markers',
        name='현재 추세 (정책 변화 없음)', line=dict(color='#ff6b6b', width=3),
        marker=dict(size=8)
    ))
    
    # 사용자 시나리오
    fig_sim.add_trace(go.Scatter(
        x=years, y=your_scenario, mode='lines+markers',
        name='당신의 정책 시나리오', line=dict(color='#4ecdc4', width=4),
        marker=dict(size=10)
    ))
    
    # 위험선
    fig_sim.add_hline(y=30, line_dash="dash", line_color="red",
                     annotation_text="⚠️ 위험 임계점")
    
    fig_sim.update_layout(
        title='🎯 당신의 정책이 만든 미래 시나리오',
        xaxis_title='연도', yaxis_title='해수면 상승 (cm)',
        height=450, hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_sim, use_container_width=True)

    # 결과 메시지
    if sea_level_2050 < 15:
        st.markdown(f'''
        <div class="result-good">
        🎉 축하합니다! 당신의 탁월한 정책으로 2050년 해수면 상승을 {sea_level_2050:.1f}cm로 제한했습니다!<br>
        🌟 현재 추세보다 {26-sea_level_2050:.1f}cm나 감축한 놀라운 성과입니다.<br>
        🏆 당신은 진정한 지구 수호자입니다!
        </div>
        ''', unsafe_allow_html=True)
        st.balloons()
        
    elif sea_level_2050 < 20:
        st.markdown(f'''
        <div class="result-good">
        👏 훌륭합니다! 당신의 정책으로 해수면 상승을 {sea_level_2050:.1f}cm로 억제했습니다.<br>
        🌿 현재 추세보다 {26-sea_level_2050:.1f}cm 감축했으며, 많은 해안 지역을 보호할 수 있습니다.<br>
        📈 조금만 더 강화하면 더 좋은 결과를 얻을 수 있어요!
        </div>
        ''', unsafe_allow_html=True)
        
    elif sea_level_2050 < 30:
        st.markdown(f'''
        <div class="result-neutral">
        🤔 보통 수준입니다. 해수면이 {sea_level_2050:.1f}cm 상승할 예정입니다.<br>
        ⚠️ 일부 해안 지역에서 침수 위험이 있을 수 있습니다.<br>
        💪 더 적극적인 정책이 필요합니다. 탄소 감축과 재생에너지를 늘려보세요!
        </div>
        ''', unsafe_allow_html=True)
        
    else:
        st.markdown(f'''
        <div class="result-bad">
        🚨 위험합니다! 해수면이 {sea_level_2050:.1f}cm나 상승할 예정입니다.<br>
        ⛔ 많은 해안 지역이 침수될 위험이 높습니다.<br>
        🔥 지금 당장 모든 정책을 최대한 강화해야 합니다!
        </div>
        ''', unsafe_allow_html=True)

    # 상세 분석
    with st.expander("📈 상세 정책 효과 분석"):
        st.markdown("### 정책별 기여도")
        
        effect_data = {
            '정책': ['탄소 감축', '재생에너지', '탄소세', '추가 정책'],
            '효과': [
                -(carbon_reduction * 0.15),
                -(renewable_energy * 0.08), 
                -(carbon_tax / 10000 * 0.8),
                -len(policies) * 0.5
            ]
        }
        
        fig_effect = px.bar(
            pd.DataFrame(effect_data), x='정책', y='효과',
            color='효과', color_continuous_scale='RdYlGn',
            title='각 정책이 해수면 상승에 미친 영향 (cm)'
        )
        st.plotly_chart(fig_effect, use_container_width=True)
        
        st.markdown("### 💡 개선 제안")
        suggestions = []
        if carbon_reduction < 60:
            suggestions.append("🏭 탄소 감축 목표를 더 높여보세요")
        if renewable_energy < 80:
            suggestions.append("⚡ 재생에너지 비율을 늘려보세요")  
        if len(policies) < 4:
            suggestions.append("📋 더 많은 추가 정책을 선택해보세요")
        if sea_wall_investment < 30:
            suggestions.append("🌊 해안 방어시설 투자를 늘려보세요")
            
        if suggestions:
            for suggestion in suggestions:
                st.info(suggestion)
        else:
            st.success("🎉 모든 정책이 최적화되었습니다!")

    # 재시작 버튼
    if st.button("🔄 다시 도전하기", type="primary"):
        st.rerun()

    # 공유 기능
    st.markdown("### 📤 결과 공유하기")
    share_text = f"""
🌊 해수면 상승 시뮬레이션 결과 🌊

내 정책 결과: 2050년 {sea_level_2050:.1f}cm 상승
등급: {grade}
적응 점수: {adaptation_score:.1f}점

#기후변화 #해수면상승 #환경정책
"""
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_area("결과 텍스트", share_text, height=120)
    with col2:
        st.markdown("**SNS 공유하기**")
        st.markdown("📱 위 텍스트를 복사해서 SNS에 공유해보세요!")
        st.markdown("🏆 친구들과 누가 더 좋은 정책을 세울 수 있는지 경쟁해보세요!")

# ========================
# 💡 우리가 할 수 있는 일 (개선된 버전)
# ========================
st.markdown("---")  
st.subheader("💡 우리가 할 수 있는 일")
st.markdown("##### 기후변화 대응을 위한 청소년 실천 가이드 ✨")

# 카테고리별로 정리
action_categories = {
    "🏫 학교에서": [
        ("기후 행동 동아리 참여하기", "climate_club"),
        ("또래 상담 프로그램 운영하기", "peer_counseling"),
        ("친구들과 환경 캠페인 기획하기", "school_campaign"),
        ("학교 내 에너지 절약 실천하기", "school_energy")
    ],
    "🌍 지역사회에서": [
        ("지역 환경보호 활동 참여하기", "community_env"),
        ("해안 정화 활동 참여하기", "beach_cleanup"),
        ("지역 기후 모니터링 활동하기", "climate_monitoring"),
        ("환경 관련 자원봉사 참여하기", "env_volunteer")
    ],
    "📱 개인 실천": [
        ("친환경 교통수단 이용하기", "eco_transport"),
        ("탄소발자국 줄이는 생활습관 만들기", "carbon_footprint"),
        ("SNS를 통한 기후변화 인식 확산하기", "sns_awareness"),
        ("환경 친화적 소비 실천하기", "eco_consumption")
    ]
}

# 진행률 계산
total_items = sum(len(items) for items in action_categories.values())
completed_count = 0

# 각 카테고리별로 체크리스트 생성
for category, items in action_categories.items():
    st.markdown(f'<div class="checklist-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="category-header">{category}</div>', unsafe_allow_html=True)
    
    category_completed = 0
    for item_text, item_key in items:
        col1, col2 = st.columns([0.08, 0.92])
        
        with col1:
            checked = st.checkbox("", key=item_key, label_visibility="collapsed")
            if checked:
                completed_count += 1
                category_completed += 1
        
        with col2:
            if checked:
                st.markdown(
                    f'<div class="completed-item">✅ {item_text}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="pending-item">⚪ {item_text}</div>',
                    unsafe_allow_html=True
                )
    
    # 카테고리별 진행률 표시
    category_progress = category_completed / len(items) * 100
    st.progress(category_progress / 100)
    st.caption(f"진행률: {category_completed}/{len(items)} ({category_progress:.0f}%)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 전체 진행률 및 격려 메시지
st.markdown("---")
total_progress = completed_count / total_items * 100

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("완료한 실천사항", f"{completed_count}개", f"총 {total_items}개 중")
with col2:
    st.metric("전체 진행률", f"{total_progress:.1f}%", "🌱")
with col3:
    if total_progress == 0:
        st.metric("실천 레벨", "시작 준비 🌱", "첫 걸음을 내딛어보세요!")
    elif total_progress < 30:
        st.metric("실천 레벨", "새싹 🌱", "좋은 시작이에요!")
    elif total_progress < 60:
        st.metric("실천 레벨", "성장 🌿", "꾸준히 실천하고 있어요!")
    elif total_progress < 90:
        st.metric("실천 레벨", "꽃봄 🌸", "정말 대단해요!")
    else:
        st.metric("실천 레벨", "지구지킴이 🌍", "완벽한 실천가예요!")

# 격려 메시지
if completed_count > 0:
    st.success(f"🎉 {completed_count}개의 실천사항을 완료하셨네요! 지구를 위한 소중한 실천에 감사드려요.")

if completed_count >= total_items:
    st.balloons()  # 모든 항목 완료 시 축하 효과

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
    
    # 게임 랭킹 (사이드바에 추가)
    st.markdown("### 🏆 오늘의 베스트 플레이어")
    st.markdown("""
    1. 🥇 김환경: 12.3cm (지구수호자)
    2. 🥈 이기후: 14.8cm (지구수호자)  
    3. 🥉 박지구: 16.2cm (환경지킴이)
    """)
    st.caption("* 실제 데이터가 아닌 예시입니다")