import streamlit as st
import pandas as pd
import plotly.express as px

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 1 - 시간")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 열을 실제 날짜형으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    # 숫자형 열 정리
    numeric_columns = ["순위", "영화코드", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values(["날짜", "순위"]).reset_index(drop=True)


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.exception(e)
    st.stop()


# ─────────────────────────────────────────────
# 그래프 1. 영화별 시간에 따른 일관객 변화
# ─────────────────────────────────────────────
st.header("그래프 1. 영화별 일관객 변화")

movie_names = sorted(df["영화명"].dropna().unique())
selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_names,
    key="movie_selector",
)

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
    .copy()
)

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    labels={
        "날짜": "날짜",
        "일관객": "일관객",
    },
    title=f"'{selected_movie}' 날짜별 일관객 변화",
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
    },
)

fig.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 (명)",
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.caption("선택한 영화의 날짜별 관객 규모와 흥행 추이의 변화를 한눈에 볼 수 있습니다.")


# ─────────────────────────────────────────────
# 그래프 2. 기간 중 일관객 합계 TOP 5 영화 비교
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 2. 일관객 합계 TOP 5 영화 비교")

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)["영화명"]
    .tolist()
)

top5_df = (
    df[df["영화명"].isin(top5_movies)]
    .sort_values(["날짜", "영화명"])
    .copy()
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    labels={
        "날짜": "날짜",
        "일관객": "일관객",
        "영화명": "영화",
    },
    title="이 기간 일관객 합계 TOP 5 영화의 날짜별 일관객",
    hover_data={
        "날짜": "|%Y-%m-%d",
        "영화명": True,
        "일관객": ":,",
    },
)

fig2.update_traces(
    hovertemplate="영화: %{fullData.name}<br>날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 (명)",
    legend_title="영화",
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.caption("전체 기간 동안 일관객 합계가 가장 큰 5편의 날짜별 흥행 추이를 서로 비교할 수 있습니다.")


# ─────────────────────────────────────────────
# 그래프 3. 날짜별 TOP 10 일관객 합계
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 3. 날짜별 TOP 10 일관객 합계")

daily_top10 = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_top10.nlargest(3, "일관객")
    .sort_values("일관객", ascending=False)
)

fig3 = px.area(
    daily_top10,
    x="날짜",
    y="일관객",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계",
    },
    title="날짜별 영화 TOP 10 일관객 합계",
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,",
    },
)

fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>10위권 일관객 합계: %{y:,}명<extra></extra>"
)

# 합계가 가장 컸던 3일을 그래프 위에 날짜와 함께 표시
for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=f"{row['날짜'].strftime('%Y-%m-%d')}",
        showarrow=True,
        arrowhead=2,
        yshift=12,
    )

fig3.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계 (명)",
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.caption("날짜별로 그날 박스오피스 10위권 영화가 기록한 전체 관객 규모와 관객이 가장 많이 몰린 날을 볼 수 있습니다.")


# ─────────────────────────────────────────────
# 그래프 4. 기간 누적 일관객 TOP 10
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 4. 기간 누적 일관객 TOP 10")

movie_summary = (
    df.groupby("영화명")
    .agg(
        기간_일관객=("일관객", "sum"),
        10위권_등장일수=("날짜", "nunique"),
    )
    .reset_index()
    .sort_values("기간_일관객", ascending=False)
    .head(10)
    .sort_values("기간_일관객", ascending=True)
)

fig4 = px.bar(
    movie_summary,
    x="기간_일관객",
    y="영화명",
    orientation="h",
    labels={
        "기간_일관객": "기간 일관객 합계",
        "영화명": "영화",
    },
    title="이 기간 일관객 합계 TOP 10",
    hover_data={
        "기간_일관객": ":,",
        "10위권_등장일수": True,
    },
)

fig4.update_traces(
    hovertemplate=(
        "영화: %{y}<br>"
        "기간 일관객 합계: %{x:,}명<br>"
        "10위권 등장일수: %{customdata[0]}일"
        "<extra></extra>"
    ),
    customdata=movie_summary[["10위권_등장일수"]].to_numpy(),
)

fig4.update_layout(
    xaxis_title="기간 일관객 합계 (명)",
    yaxis_title="영화",
    yaxis={"categoryorder": "array", "categoryarray": movie_summary["영화명"].tolist()},
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.caption("전체 기간 동안 누적 관객이 많은 영화 TOP 10과 각 영화가 박스오피스 10위권에 등장한 날수를 함께 비교할 수 있습니다.")


# ─────────────────────────────────────────────
# 그래프 5. 월 × 요일별 일관객 합계 히트맵
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 5. 월 × 요일별 일관객 합계")

heatmap_df = df.copy()
heatmap_df["월"] = heatmap_df["날짜"].dt.month
heatmap_df["요일"] = heatmap_df["날짜"].dt.dayofweek

weekday_names = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

heatmap_summary = (
    heatmap_df.groupby(["월", "요일"], as_index=False)["일관객"]
    .sum()
)

heatmap_pivot = (
    heatmap_summary
    .pivot(index="월", columns="요일", values="일관객")
    .reindex(columns=range(7))
    .fillna(0)
)

# Plotly 히트맵은 go.Heatmap을 사용해 요일 순서와 색상 강도를 명확하게 지정
import plotly.graph_objects as go

fig5 = go.Figure(
    data=go.Heatmap(
        z=heatmap_pivot.values,
        x=weekday_names,
        y=[f"{month}월" for month in heatmap_pivot.index],
        colorscale="Blues",
        hovertemplate=(
            "%{y} %{x}<br>"
            "일관객 합계: %{z:,}명"
            "<extra></extra>"
        ),
        colorbar=dict(title="일관객"),
    )
)

fig5.update_layout(
    title="월 × 요일별 일관객 합계",
    xaxis_title="요일",
    yaxis_title="월",
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:**")
st.caption("월과 요일의 조합에 따라 박스오피스 10위권 영화의 일관객 규모가 어떻게 달라지는지 볼 수 있습니다.")


# ─────────────────────────────────────────────
# 앞으로 추가할 그래프 영역
# ─────────────────────────────────────────────
st.divider()
st.header("그래프 6")
st.info("다음 그래프를 여기에 추가하세요.")
