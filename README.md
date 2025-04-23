# 판매 예측 대시보드

Streamlit을 활용한 판매 및 재고 데이터 분석 대시보드입니다.

## 주요 기능

- CSV 및 Excel 형식의 판매 데이터와 재고 데이터 업로드
- 재고율(재고/판매) 분석 및 시각화
- 과잉 재고 경고 기능
- 분석 결과 CSV 다운로드

## 설치 방법

1. 저장소 클론:
```bash
git clone [repository-url]
cd [repository-name]
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

## 데이터 형식

### 판매 데이터 (CSV 또는 Excel)
- product_id: 제품 ID
- sales: 판매량

### 재고 데이터 (CSV 또는 Excel)
- product_id: 제품 ID
- inventory: 재고량

## 라이센스

MIT License 