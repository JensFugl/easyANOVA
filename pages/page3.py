import numpy as np
import pandas as pd
import streamlit as st

from pages.utils import (
    group_summary,
    render_assumption_checks,
    render_results,
    render_tukey,
    render_violin,
    run_anova,
    run_assumption_checks,
)

MAX_FILE_SIZE_MB = 10


def app():
    st.title("Run Analysis")

    st.caption(
        "Upload a CSV file with at least one categorical column (groups) and one numeric column "
        "(values). Each row should represent a single observation."
    )

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is None:
        return

    if uploaded_file.size > MAX_FILE_SIZE_MB * 1_000_000:
        st.warning(
            f"File is larger than {MAX_FILE_SIZE_MB} MB. Analysis may be slow. "
            "Consider using a smaller sample."
        )

    try:
        data = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read the file: {e}")
        return

    if data.empty:
        st.error("The uploaded file is empty.")
        return

    data.columns = data.columns.str.strip()

    st.write(f"Loaded **{len(data):,} rows × {len(data.columns)} columns**.")
    st.dataframe(data.head(10), use_container_width=True)

    string_columns = data.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()

    if not string_columns:
        st.error("No categorical columns found. Please ensure your CSV has a text/categorical grouping column.")
        return
    if not numeric_columns:
        st.error("No numeric columns found. Please ensure your CSV has a numeric values column.")
        return

    group_col = st.selectbox("Select the column for grouping (categorical):", string_columns)
    value_col = st.selectbox("Select the column for values (numerical):", numeric_columns)
    alpha = st.selectbox("Significance level (α):", [0.01, 0.05, 0.10], index=1)

    # Drop rows with missing values in the selected columns
    analysis_data = data[[group_col, value_col]].dropna()
    dropped = len(data) - len(analysis_data)
    if dropped > 0:
        st.caption(f"Note: {dropped} row(s) with missing values were excluded from the analysis.")

    if analysis_data[group_col].nunique() < 2:
        st.error("At least 2 groups are required for ANOVA.")
        return

    st.subheader("Group summary")
    st.dataframe(group_summary(analysis_data, group_col, value_col), use_container_width=True, hide_index=True)

    checks = run_assumption_checks(analysis_data, group_col, value_col)
    render_assumption_checks(checks, alpha)

    if st.button("Perform ANOVA analysis"):
        result = run_anova(analysis_data, group_col, value_col, alpha)
        render_results(result)

        if result["significant"]:
            render_tukey(analysis_data, group_col, value_col)

        render_violin(analysis_data, group_col, value_col, "violin_plot.png")
