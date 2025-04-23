import streamlit as st
import pandas as pd
from datetime import timedelta

# 페이지 설정
st.set_page_config(page_title="판매 예측 대시보드", layout="wide")
st.title("📈 판매 예측 대시보드")

# 예측 함수
def run_prediction(sales_df, stock_df):
    """
    판매 데이터와 재고 데이터를 기반으로 예측을 수행하는 함수
    - 재고율(재고/판매) 계산
    - 결과를 데이터프레임으로 반환
    """
    try:
        # 데이터프레임 병합 (product_id 기준)
        merged_df = pd.merge(sales_df, stock_df, on='product_id', how='inner')
        
        # 재고율 계산
        merged_df['inventory_ratio'] = merged_df['inventory'] / merged_df['sales']
        
        # 결과 테이블 생성
        result_df = merged_df[['product_id', 'sales', 'inventory', 'inventory_ratio']]
        
        return result_df
        
    except Exception as e:
        st.error(f"❌ 예측 계산 중 오류 발생: {str(e)}")
        return None

# 판매 데이터 업로드
st.subheader("📊 판매 데이터 업로드")
uploaded_sales = st.file_uploader("📁 판매 데이터 파일을 업로드하세요 (CSV 또는 Excel)", type=["csv", "xlsx"], key="sales")

if uploaded_sales is not None:
    try:
        if uploaded_sales.name.endswith('.csv'):
            sales_df = pd.read_csv(uploaded_sales)
        elif uploaded_sales.name.endswith('.xlsx'):
            sales_df = pd.read_excel(uploaded_sales)
        else:
            raise ValueError("지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 업로드해주세요.")
            
        st.success(f"✅ 판매 데이터 업로드 성공! (파일명: {uploaded_sales.name})")
        
        st.subheader("판매 데이터 미리보기 (상위 5개 행)")
        st.dataframe(sales_df.head())

        st.subheader("판매 데이터 통계 요약")
        st.write(sales_df.describe())

    except Exception as e:
        st.error(f"❌ 판매 데이터 처리 중 오류 발생: {str(e)}")

# 재고 데이터 업로드
st.subheader("📦 재고 데이터 업로드")
uploaded_stock = st.file_uploader("📁 재고 데이터 파일을 업로드하세요 (CSV 또는 Excel)", type=["csv", "xlsx"], key="stock")

if uploaded_stock is not None:
    try:
        if uploaded_stock.name.endswith('.csv'):
            stock_df = pd.read_csv(uploaded_stock)
        elif uploaded_stock.name.endswith('.xlsx'):
            stock_df = pd.read_excel(uploaded_stock)
        else:
            raise ValueError("지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 업로드해주세요.")
            
        st.success(f"✅ 재고 데이터 업로드 성공! (파일명: {uploaded_stock.name})")
        
        st.subheader("재고 데이터 미리보기 (상위 5개 행)")
        st.dataframe(stock_df.head())

        st.subheader("재고 데이터 통계 요약")
        st.write(stock_df.describe())

    except Exception as e:
        st.error(f"❌ 재고 데이터 처리 중 오류 발생: {str(e)}")

# 예측 실행 및 결과 표시 (두 파일이 모두 업로드된 경우)
if uploaded_sales is not None and uploaded_stock is not None:
    st.divider()
    st.subheader("🎯 예측 실행")
    
    if st.button("예측 실행하기", type="primary"):
        try:
            result_df = run_prediction(sales_df, stock_df)
            if result_df is not None:
                st.subheader("📊 재고율 분석 결과")
                st.dataframe(result_df)
                
                # 결과 다운로드 버튼
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 예측 결과 다운로드",
                    data=csv,
                    file_name="prediction_result.csv",
                    mime="text/csv",
                )
                
                # 과잉 재고 경고 메시지
                high_inventory = result_df[result_df['inventory_ratio'] >= 1.5]
                if not high_inventory.empty:
                    st.subheader("⚠️ 과잉 재고 경고")
                    for _, row in high_inventory.iterrows():
                        st.warning(f"⚠️ 과잉 재고 주의: {row['product_id']} (재고율: {row['inventory_ratio']:.2f})")
                
                st.subheader("📈 재고율 통계")
                st.write(result_df['inventory_ratio'].describe())
                
                # 재고율 바 차트
                st.subheader("📊 제품별 재고율 시각화")
                # product_id를 인덱스로 설정하여 x축으로 사용
                chart_data = result_df.set_index('product_id')['inventory_ratio']
                st.bar_chart(chart_data)
                
        except Exception as e:
            st.error(f"❌ 예측 실행 중 오류 발생: {str(e)}")
else:
    st.info("판매 데이터와 재고 데이터 파일을 모두 업로드해주세요. (CSV 또는 Excel 형식)")
