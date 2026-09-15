import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화 (1907년~)", page_icon="🌡️", layout="wide"
)

st.title("🌡️ 서울 연평균 기온 변화 (1907년 이후)")
st.markdown(
    "기상청 서울 기상 관측 데이터(`seoul.csv`)를 바탕으로 **1907년 이후 연평균 기온의"
    " 변화 추이**를 선 그래프로 보여줍니다."
)


# 데이터 로드 함수 (캐싱 적용으로 성능 향상)
@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"
  # 한글 인코딩 깨짐 방지를 위해 utf-8 시도 후 실패 시 cp949 시도
  try:
    df = pd.read_csv(url, encoding="utf-8")
  except UnicodeDecodeError:
    df = pd.read_csv(url, encoding="cp949")
  return df


# 데이터 불러오기 및 전처리
try:
  with st.spinner("데이터를 불러오는 중입니다... 잠시만 기다려 주세요."):
    df = load_data()

  # 컬럼명 앞뒤 공백 제거
  df.columns = df.columns.str.strip()

  # 날짜 및 평균기온 컬럼 자동 탐색
  date_col = [col for col in df.columns if "날짜" in col][0]
  temp_col = [col for col in df.columns if "평균기온" in col][0]

  # 날짜 형식을 datetime으로 변환 후 연도 추출
  df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
  df["연도"] = df[date_col].dt.year

  # 연도별 평균기온 집계
  annual_temp = (
      df.groupby("연도")[temp_col].mean().reset_index(name="연평균기온")
  )
  annual_temp = annual_temp.dropna()

  # 시각화 섹션
  st.subheader("📈 연도별 서울 평균기온 추이")
  st.line_chart(annual_temp.set_index("연도")["연평균기온"])

  # 주요 통계 요약 메트릭
  st.markdown("---")
  st.subheader("📊 주요 통계 요약")

  col1, col2, col3 = st.columns(3)
  with col1:
    max_year_row = annual_temp.loc[annual_temp["연평균기온"].idxmax()]
    st.metric(
        label="가장 더웠던 연도",
        value=f"{int(max_year_row['연도'])}년",
        delta=f"{max_year_row['연평균기온']:.2f}°C",
    )
  with col2:
    min_year_row = annual_temp.loc[annual_temp["연평균기온"].idxmin()]
    st.metric(
        label="가장 추웠던 연도",
        value=f"{int(min_year_row['연도'])}년",
        delta=f"{min_year_row['연평균기온']:.2f}°C",
    )
  with col3:
    avg_temp = annual_temp["연평균기온"].mean()
    st.metric(label="전체 기간 평균 기온", value=f"{avg_temp:.2f}°C")

  # 상세 데이터 테이블 확인용 익스팬더
  with st.expander("원본 연도별 평균기온 데이터 테이블 보기"):
    st.dataframe(
        annual_temp.style.format({"연평균기온": "{:.2f}"}),
        use_container_width=True,
    )
except Exception as e:
  st.error(
      "데이터를 처리하는 동안 오류가 발생했습니다. 파일 구조를 확인해주세요."
  )
  st.error(f"상세 오류 내용: {e}")
