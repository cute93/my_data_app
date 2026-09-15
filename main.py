import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="서울 기온 데이터 분석", page_icon="🌡️", layout="wide"
)

st.title("🌡️ 서울 기온 데이터 분석 앱")
st.markdown(
    "기상청 서울 기상 관측 데이터(`seoul.csv`)를 활용하여 연평균 기온 변화와"
    " **일별 평균기온 분포(히스토그램)**를 확인합니다."
)


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"
  try:
    df = pd.read_csv(url, encoding="utf-8")
  except UnicodeDecodeError:
    df = pd.read_csv(url, encoding="cp949")
  return df


try:
  with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data()

  # 컬럼명 공백 제거
  df.columns = df.columns.str.strip()

  # 컬럼 탐색
  date_col = [col for col in df.columns if "날짜" in col][0]
  temp_col = [col for col in df.columns if "평균기온" in col][0]

  # 데이터 전처리
  df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
  df["연도"] = df[date_col].dt.year
  df[temp_col] = pd.to_numeric(df[temp_col], errors="coerce")

  # 탭(Tab)을 이용해 화면 분리
  tab1, tab2 = st.tabs(["📈 연평균 기온 변화", "📊 일별 평균기온 히스토그램"])

  # ---------------- 탭 1: 연평균 기온 변화 ----------------
  with tab1:
    st.subheader("1907년 이후 연도별 서울 평균기온 추이")
    annual_temp = (
        df.groupby("연도")[temp_col].mean().reset_index(name="연평균기온")
    )
    annual_temp = annual_temp.dropna()

    st.line_chart(annual_temp.set_index("연도")["연평균기온"])

    col1, col2, col3 = st.columns(3)
    with col1:
      max_row = annual_temp.loc[annual_temp["연평균기온"].idxmax()]
      st.metric(
          "최고 연평균기온",
          f"{int(max_row['연도'])}년",
          f"{max_row['연평균기온']:.2f}°C",
      )
    with col2:
      min_row = annual_temp.loc[annual_temp["연평균기온"].idxmin()]
      st.metric(
          "최저 연평균기온",
          f"{int(min_row['연도'])}년",
          f"{min_row['연평균기온']:.2f}°C",
      )
    with col3:
      mean_val = annual_temp["연평균기온"].mean()
      st.metric("전체 기간 평균", f"{mean_val:.2f}°C")

  # ---------------- 탭 2: 일별 평균기온 히스토그램 ----------------
  with tab2:
    st.subheader("일별 평균기온 분포 현황")
    st.markdown(
        "전체 관측 기간 동안 **일별 평균기온**이 어느 온도 구간에 가장 많이"
        " 몰려 있는지 보여줍니다."
    )

    # 슬라이더로 구간(Bins) 개수 조절 기능 추가
    bins = st.slider("히스토그램 구간(Bin) 개수 선택", min_value=10, max_value=100, value=50)

    clean_df = df.dropna(subset=[temp_col])

    # Matplotlib을 이용한 히스토그램 생성
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(
        clean_df[temp_col],
        bins=bins,
        color="skyblue",
        edgecolor="black",
        alpha=0.7,
    )
    ax.set_xlabel("평균기온 (°C)", fontsize=12)
    ax.set_ylabel("일수 (빈도)", fontsize=12)
    ax.set_title("서울 일별 평균기온 히스토그램", fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    st.pyplot(fig)

    # 간단한 기술 통계 제공
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("기록된 총 일수", f"{len(clean_df):,}일")
    c2.metric("전체 일평균 기온", f"{clean_df[temp_col].mean():.2f}°C")
    c3.metric("가장 낮았던 일기온", f"{clean_df[temp_col].min():.2f}°C")
    c4.metric("가장 높았던 일기온", f"{clean_df[temp_col].max():.2f}°C")

except Exception as e:
  st.error(f"오류가 발생했습니다: {e}")
