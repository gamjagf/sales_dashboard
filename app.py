import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="마트 판매 분석 대시보드",
    page_icon="🛒",
    layout="wide"
)

# 필수 컬럼 정의
REQUIRED_SALES_COLS = ['제품명', '판매일자', '판매량', '판매금액']
REQUIRED_STOCK_COLS = ['제품명', '재고량']

def load_data(uploaded_file):
    """파일 업로드 및 데이터 로드"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {str(e)}")
        return None

def check_required_columns(df, required_cols):
    """필수 컬럼 존재 여부 확인"""
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")
        return False
    return True

def process_dates(df):
    """날짜 데이터 처리"""
    try:
        df['판매일자'] = pd.to_datetime(df['판매일자'])
        df['년월'] = df['판매일자'].dt.strftime('%Y-%m')
        df['년'] = df['판매일자'].dt.year
        return df
    except Exception as e:
        st.error(f"날짜 처리 중 오류 발생: {str(e)}")
        return None

# 메인 타이틀
st.title("🛒 마트 판매 분석 대시보드")

# 데이터 업로드 섹션
st.header("📁 데이터 업로드")
col1, col2 = st.columns(2)

with col1:
    sales_file = st.file_uploader("판매 데이터 파일 업로드", type=['csv', 'xlsx'])
    if sales_file:
        sales_df = load_data(sales_file)
        if sales_df is not None and check_required_columns(sales_df, REQUIRED_SALES_COLS):
            sales_df = process_dates(sales_df)
            st.success("✅ 판매 데이터 업로드 성공!")

with col2:
    stock_file = st.file_uploader("재고 데이터 파일 업로드", type=['csv', 'xlsx'])
    if stock_file:
        stock_df = load_data(stock_file)
        if stock_df is not None and check_required_columns(stock_df, REQUIRED_STOCK_COLS):
            st.success("✅ 재고 데이터 업로드 성공!")

# 데이터가 모두 업로드된 경우에만 분석 진행
if 'sales_df' in locals() and 'stock_df' in locals():
    # 상단 요약 지표
    st.header("📊 주요 지표")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = sales_df['판매금액'].sum()
        st.metric("총매출", f"{total_sales:,.0f}원")
    
    with col2:
        avg_price = sales_df['판매금액'].sum() / sales_df['판매량'].sum()
        st.metric("평균단가", f"{avg_price:,.0f}원")
    
    with col3:
        total_quantity = sales_df['판매량'].sum()
        st.metric("총판매량", f"{total_quantity:,.0f}개")
    
    with col4:
        best_month = sales_df.groupby('년월')['판매금액'].sum().idxmax()
        st.metric("최고매출월", best_month)

    # 탭 구성
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "월별 베스트 상품", "제품별 판매 추이", "월별 고객 선호도",
        "제품 판매 예측", "판매 vs 재고 비교", "꽃님이 추천 분석"
    ])

    with tab1:
        st.header("📈 월별 베스트 상품")
        col1, col2 = st.columns(2)
        
        with col1:
            n_products = st.slider("상위 제품 수", 1, 10, 5)
        
        with col2:
            selected_year = st.selectbox(
                "연도 선택",
                ["전체"] + sorted(sales_df['년'].unique().tolist())
            )
        
        # 데이터 필터링
        if selected_year != "전체":
            filtered_df = sales_df[sales_df['년'] == selected_year]
        else:
            filtered_df = sales_df
        
        # 월별 상위 제품 분석
        monthly_top_products = filtered_df.groupby(['년월', '제품명'])['판매량'].sum().reset_index()
        monthly_top_products = monthly_top_products.sort_values(['년월', '판매량'], ascending=[True, False])
        top_products = monthly_top_products.groupby('년월').head(n_products)
        
        # 시각화
        fig = px.bar(
            top_products,
            x='년월',
            y='판매량',
            color='제품명',
            title=f'월별 상위 {n_products}개 제품 판매량'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("📊 제품별 판매 추이")
        
        # 제품 선택
        selected_product = st.selectbox(
            "제품 선택",
            sorted(sales_df['제품명'].unique()),
            key='trend_product'
        )
        
        try:
            # 선택된 제품의 데이터 필터링 및 날짜 정렬
            product_data = sales_df[sales_df['제품명'] == selected_product].copy()
            product_data['판매일자'] = pd.to_datetime(product_data['판매일자'])
            product_data = product_data.sort_values('판매일자')
            
            # 날짜별로 데이터 집계 (중복 제거)
            daily_data = product_data.groupby('판매일자').agg({
                '판매량': 'sum',
                '판매금액': 'sum'
            }).reset_index()
            
            # 그래프 생성
            fig = go.Figure()
            
            # 판매량 (막대그래프)
            fig.add_trace(go.Bar(
                x=daily_data['판매일자'],
                y=daily_data['판매량'],
                name='판매량',
                yaxis='y',
                marker_color='#1f77b4',
                opacity=0.7
            ))
            
            # 매출액 (선그래프)
            fig.add_trace(go.Scatter(
                x=daily_data['판매일자'],
                y=daily_data['판매금액'],
                name='매출액',
                yaxis='y2',
                line=dict(color='#ff7f0e', width=2)
            ))
            
            # 레이아웃 설정
            fig.update_layout(
                title=f'{selected_product} 판매 추이',
                xaxis=dict(
                    title='날짜',
                    tickangle=45,
                    showgrid=True,
                    gridcolor='lightgray'
                ),
                yaxis=dict(
                    title='판매량(개)',
                    titlefont=dict(color='#1f77b4'),
                    tickfont=dict(color='#1f77b4'),
                    showgrid=True,
                    gridcolor='lightgray'
                ),
                yaxis2=dict(
                    title='매출액(원)',
                    titlefont=dict(color='#ff7f0e'),
                    tickfont=dict(color='#ff7f0e'),
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='x unified',
                plot_bgcolor='white',
                barmode='group',
                bargap=0.15,
                bargroupgap=0.1
            )
            
            # 호버 템플릿 설정
            fig.update_traces(
                hovertemplate="<br>".join([
                    "날짜: %{x}",
                    "판매량: %{y:,.0f}개",
                    "매출액: %{y2:,.0f}원"
                ])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 요약 통계 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "총 판매량",
                    f"{daily_data['판매량'].sum():,.0f}개"
                )
            with col2:
                st.metric(
                    "총 매출액",
                    f"{daily_data['판매금액'].sum():,.0f}원"
                )
            with col3:
                avg_price = daily_data['판매금액'].sum() / daily_data['판매량'].sum()
                st.metric(
                    "평균 단가",
                    f"{avg_price:,.0f}원"
                )
        
        except Exception as e:
            st.error(f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
            st.info("데이터 형식이 올바른지 확인해주세요.")

    with tab3:
        st.header("🍩 월별 고객 선호도")
        selected_month = st.selectbox(
            "월 선택",
            sorted(sales_df['년월'].unique())
        )
        
        month_data = sales_df[sales_df['년월'] == selected_month]
        product_sales = month_data.groupby('제품명')['판매량'].sum().reset_index()
        
        fig = px.pie(
            product_sales,
            values='판매량',
            names='제품명',
            title=f'{selected_month} 제품별 판매 비율'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("🔮 제품 판매 예측")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_product = st.selectbox(
                "예측할 제품 선택",
                sales_df['제품명'].unique(),
                key='pred_product'
            )
        
        with col2:
            months = st.slider("예측 개월 수", 3, 6, 3)
        
        # 선택된 제품의 시계열 데이터 준비
        product_data = sales_df[sales_df['제품명'] == selected_product].copy()
        product_data = product_data.set_index('판매일자')['판매량'].resample('D').sum().fillna(0)
        
        # SARIMA 모델 학습 및 예측
        try:
            # SARIMA 모델 파라미터 (기본값 설정)
            model = SARIMAX(
                product_data,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 30),  # 30일 계절성
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            results = model.fit(disp=False)
            
            # 예측 기간 설정
            forecast_steps = months * 30  # 월별 예측을 일별로 변환
            forecast = results.get_forecast(steps=forecast_steps)
            
            # 신뢰구간 계산
            forecast_mean = forecast.predicted_mean
            conf_int = forecast.conf_int()
            
            # 예측 결과 시각화
            fig = go.Figure()
            
            # 실제 데이터
            fig.add_trace(go.Scatter(
                x=product_data.index,
                y=product_data.values,
                name='실제 판매량',
                line=dict(color='blue')
            ))
            
            # 예측 데이터
            fig.add_trace(go.Scatter(
                x=forecast_mean.index,
                y=forecast_mean.values,
                name='예측 판매량',
                line=dict(color='red')
            ))
            
            # 신뢰구간
            fig.add_trace(go.Scatter(
                x=conf_int.index,
                y=conf_int.iloc[:, 1],
                name='상한선',
                line=dict(color='gray', dash='dash'),
                fill=None
            ))
            
            fig.add_trace(go.Scatter(
                x=conf_int.index,
                y=conf_int.iloc[:, 0],
                name='하한선',
                line=dict(color='gray', dash='dash'),
                fill='tonexty'
            ))
            
            fig.update_layout(
                title=f'{selected_product} {months}개월 판매량 예측',
                xaxis_title='날짜',
                yaxis_title='판매량'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 예측 성능 지표 표시
            if len(product_data) > 30:  # 최소 30일 데이터가 있는 경우
                train_size = len(product_data) - 30
                train_data = product_data[:train_size]
                test_data = product_data[train_size:]
                
                # 검증용 모델 학습
                validation_model = SARIMAX(
                    train_data,
                    order=(1, 1, 1),
                    seasonal_order=(1, 1, 1, 30),
                    enforce_stationarity=False,
                    enforce_invertibility=False
                ).fit(disp=False)
                
                # 검증 예측
                validation_forecast = validation_model.get_forecast(steps=30)
                mae = mean_absolute_error(test_data, validation_forecast.predicted_mean)
                
                st.info(f"모델 성능 (최근 30일 MAE): {mae:.2f}")
        
        except Exception as e:
            st.error(f"예측 중 오류가 발생했습니다: {str(e)}")
            st.info("데이터가 충분하지 않거나, 시계열 패턴을 찾기 어려울 수 있습니다.")

    with tab5:
        st.header("📊 판매 vs 재고 비교")
        
        try:
            # 재고소진률 계산 (판매량이 있는 경우)
            if '판매량' in sales_df.columns:
                merged_data = pd.merge(
                    sales_df.groupby('제품명')['판매량'].mean().reset_index(),
                    stock_df,
                    on='제품명'
                )
                merged_data['재고소진률'] = (merged_data['판매량'] / merged_data['재고량']) * 100
                
                # 판매량과 재고량 비교 시각화
                fig = px.bar(
                    merged_data,
                    x='제품명',
                    y=['판매량', '재고량'],
                    title='제품별 평균 판매량과 재고량 비교',
                    barmode='group',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e']
                )
                
                fig.update_layout(
                    yaxis_title='수량',
                    xaxis_title='제품명'
                )
                
                # 재고소진률 시각화
                fig2 = px.bar(
                    merged_data,
                    x='제품명',
                    y='재고소진률',
                    title='제품별 재고소진률',
                    color='재고소진률',
                    color_continuous_scale='RdYlGn_r'
                )
                
                fig2.update_layout(
                    yaxis_title='재고소진률 (%)',
                    xaxis_title='제품명'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
            
            else:
                # 판매량이 없는 경우, 재고량만 시각화
                st.warning("⚠️ 판매량 데이터가 없어 재고량만 표시합니다.")
                
                # 재고량 기준으로 정렬
                sorted_stock = stock_df.sort_values('재고량', ascending=False)
                
                fig = px.bar(
                    sorted_stock,
                    x='제품명',
                    y='재고량',
                    title='제품별 재고량 (재고량 순)',
                    color='재고량',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(
                    yaxis_title='재고량',
                    xaxis_title='제품명'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
            st.info("데이터 형식이 올바른지 확인해주세요.")

    with tab6:
        st.subheader("🌸 꽃님이 추천 분석")
        
        try:
            # 최근 30일 데이터 필터링
            recent_date = sales_df['판매일자'].max()
            start_date = recent_date - timedelta(days=30)
            recent_sales = sales_df[sales_df['판매일자'] >= start_date]
            
            # 판매량 기준 상위 5개 제품 선택
            top_products = recent_sales.groupby('제품명')['판매량'].sum().nlargest(5).reset_index()
            
            # 재고 데이터와 병합
            recommendations = pd.merge(
                top_products,
                stock_df,
                on='제품명',
                how='inner'
            )
            
            # 평균 재고량 계산
            avg_stock = stock_df['재고량'].mean()
            
            # 평균 재고량 이상인 제품만 필터링
            recommendations = recommendations[recommendations['재고량'] >= avg_stock]
            
            if len(recommendations) > 0:
                # 결과 표시
                st.success("🌼 꽃님이 추천하는 인기 제품 TOP 5 (재고도 충분해요!)")
                
                # 추천 제품 시각화
                fig = px.bar(
                    recommendations,
                    x='제품명',
                    y=['판매량', '재고량'],
                    title='추천 제품 판매량 및 재고량',
                    barmode='group',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e']
                )
                
                fig.update_layout(
                    yaxis_title='수량',
                    xaxis_title='제품명'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 상세 정보 표시
                recommendations = recommendations.rename(columns={
                    '제품명': '추천 제품',
                    '판매량': '최근 30일 판매량',
                    '재고량': '현재 재고량'
                })
                
                st.dataframe(
                    recommendations,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("😢 현재 재고가 충분한 인기 제품이 없습니다.")
                st.info("재고를 보충하거나 새로운 제품을 추천해주세요.")
        
        except Exception as e:
            st.error(f"추천 분석 중 오류가 발생했습니다: {str(e)}")
            st.info("데이터가 충분하지 않거나 형식이 올바르지 않을 수 있습니다.")
