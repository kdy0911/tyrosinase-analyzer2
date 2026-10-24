import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =====================================
# 1. 앱 기본 설정
# =====================================
st.set_page_config(
    page_title="티로시나아제 분석",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 티로시나아제 억제율 분석 프로그램")
st.write(
    "흡광도 데이터를 입력하면 억제율을 계산하고 "
    "실험 결과의 이상 여부와 점검 사항을 안내합니다."
)

st.info(
    "입력된 예시값은 실제 실험 결과가 아닙니다. "
    "분석할 때 반드시 직접 측정한 값으로 바꿔 주세요."
)

# =====================================
# 2. 대조군 데이터 입력
# =====================================
st.header("1. 대조군 흡광도")

col1, col2 = st.columns(2)

with col1:
    control = st.number_input(
        "대조군 반응액 흡광도",
        min_value=0.0,
        value=0.800,
        step=0.001,
        format="%.3f"
    )

with col2:
    control_blank = st.number_input(
        "대조군 블랭크 흡광도",
        min_value=0.0,
        value=0.100,
        step=0.001,
        format="%.3f"
    )

# =====================================
# 3. 천연물 데이터 입력
# =====================================
st.header("2. 천연물별 흡광도 입력")

example = pd.DataFrame({
    "천연물": ["계피", "녹차", "블루베리", "마늘"],
    "시료 흡광도": [0.500, 0.600, 0.450, 0.650],
    "시료 블랭크": [0.100, 0.120, 0.080, 0.100]
})

data = st.data_editor(
    example,
    num_rows="dynamic",
    use_container_width=True,
    key="sample_table"
)

st.caption(
    "시료 흡광도와 시료 블랭크에는 같은 측정 조건에서 "
    "얻은 값을 입력하세요."
)

# =====================================
# 4. 계산 실행
# =====================================
if st.button("📊 억제율 계산 및 결과 진단", type="primary"):

    # 입력값 검사
    if control <= control_blank:
        st.error(
            "대조군의 보정 흡광도가 0 이하입니다. "
            "대조군과 블랭크의 값 및 입력 조건을 확인하세요."
        )

    elif data.empty:
        st.error("분석할 천연물 데이터를 입력하세요.")

    elif data.isnull().any().any():
        st.error("비어 있는 셀이 있습니다. 모든 값을 입력하세요.")

    elif (data["시료 흡광도"] < 0).any() or (
        data["시료 블랭크"] < 0
    ).any():
        st.error("흡광도에는 음수가 아닌 값을 입력하세요.")

    elif (data["시료 흡광도"] < data["시료 블랭크"]).any():
        st.error(
            "시료 흡광도가 시료 블랭크보다 작습니다. "
            "측정값과 블랭크 구성을 확인하세요."
        )

    elif (data["천연물"].astype(str).str.strip() == "").any():
        st.error("천연물 이름을 모두 입력하세요.")

    else:
        # ---------------------------------
        # 5. 흡광도 보정 및 억제율 계산
        # ---------------------------------
        result = data.copy()

        result["보정 흡광도"] = (
            result["시료 흡광도"]
            - result["시료 블랭크"]
        )

        control_corrected = control - control_blank

        result["억제율 (%)"] = (
            1
            - result["보정 흡광도"] / control_corrected
        ) * 100

        # ---------------------------------
        # 6. 결과 표
        # ---------------------------------
        st.header("3. 분석 결과")

        st.dataframe(
            result.style.format({
                "시료 흡광도": "{:.3f}",
                "시료 블랭크": "{:.3f}",
                "보정 흡광도": "{:.3f}",
                "억제율 (%)": "{:.2f}"
            }),
            use_container_width=True
        )

        # ---------------------------------
        # 7. 결과 진단 및 피드백
        # ---------------------------------
        st.header("4. 실험 결과 진단 및 피드백")

        st.caption(
            "수치에서 확인되는 특징과 점검할 사항을 안내합니다. "
            "실제 원인을 확정하는 기능은 아닙니다."
        )

        for _, row in result.iterrows():
            name = str(row["천연물"])
            corrected = row["보정 흡광도"]
            rate = row["억제율 (%)"]

            with st.expander(f"🔎 {name} 결과 점검"):
                issues = []

                if corrected == 0:
                    issues.append(
                        "보정 흡광도가 0입니다. "
                        "시료 반응액과 블랭크의 측정값을 확인하세요."
                    )

                if rate < 0:
                    issues.append(
                        "음수 억제율이 관찰됩니다. "
                        "시료의 보정 흡광도가 대조군보다 높습니다. "
                        "시료의 색이나 탁도, 반응 시간, 온도, "
                        "블랭크 설정 및 대조군 조건을 확인하세요."
                    )

                if rate > 100:
                    issues.append(
                        "억제율이 100%를 초과합니다. "
                        "보정 흡광도가 음수로 계산된 것은 아닌지, "
                        "입력값과 블랭크 구성을 확인하세요."
                    )

                if 0 <= rate <= 100:
                    st.success(
                        f"계산된 억제율은 {rate:.2f}%입니다. "
                        "이 범위에 있다는 사실만으로 "
                        "실험의 정확성이 보장되지는 않습니다."
                    )

                if issues:
                    for issue in issues:
                        st.warning(issue)

                st.markdown("**추가로 확인할 사항**")
                st.markdown(
                    "- 시료와 대조군의 반응 시간 및 온도가 같았는가?\n"
                    "- 시료별 블랭크가 시료 자체의 색과 탁도를 "
                    "적절히 반영하는가?\n"
                    "- 같은 조건에서 반복 측정해도 비슷한 결과가 "
                    "나타나는가?"
                )

        # ---------------------------------
        # 8. 천연물별 그래프
        # ---------------------------------
        st.header("5. 천연물별 억제율 비교")

        fig, ax = plt.subplots(figsize=(9, 5))

        ax.bar(
            result["천연물"],
            result["억제율 (%)"]
        )

        ax.set_xlabel("천연물")
        ax.set_ylabel("티로시나아제 억제율 (%)")
        ax.set_title("천연물별 티로시나아제 억제 효과")
        ax.axhline(0, linewidth=0.8)

        plt.xticks(rotation=25)
        fig.tight_layout()

        st.pyplot(fig)

        # ---------------------------------
        # 9. CSV 다운로드
        # ---------------------------------
        st.header("6. 분석 결과 저장")

        csv = result.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="📥 결과 CSV 다운로드",
            data=csv,
            file_name="tyrosinase_results.csv",
            mime="text/csv"
        )

        st.success(
            "분석이 완료되었습니다. "
            "이상 징후는 실험 조건을 추가로 확인해 주세요."
        )
