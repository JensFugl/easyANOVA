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

DUMMY_DATA = pd.DataFrame({
    "ThreeGroup": ["A"] * 5 + ["B"] * 5 + ["C"] * 5,
    "TwoGroup": ["X"] * 7 + ["Y"] * 8,
    "DifferentValues": [10, 12, 9, 11, 13, 20, 21, 19, 18, 22, 30, 29, 31, 28, 32],
    "SimilarValues": [5, 6, 5, 6, 7, 6, 5, 7, 6, 5, 7, 5, 6, 6, 7],
})


def app():
    st.title("How it works")

    string_columns = DUMMY_DATA.select_dtypes(include=["object"]).columns.tolist()
    numeric_columns = DUMMY_DATA.select_dtypes(include=[np.number]).columns.tolist()

    if st.button("Load Dummy Data"):
        st.session_state.demo_data_loaded = True
        st.session_state.demo_group_col = string_columns[0]
        st.session_state.demo_value_col = numeric_columns[0]

    if not st.session_state.get("demo_data_loaded"):
        return

    st.dataframe(DUMMY_DATA, use_container_width=True)

    group_col = st.selectbox(
        "Select the column for grouping (categorical):",
        string_columns,
        index=string_columns.index(st.session_state.demo_group_col),
        key="demo_group_col",
    )
    value_col = st.selectbox(
        "Select the column for values (numerical):",
        numeric_columns,
        index=numeric_columns.index(st.session_state.demo_value_col),
        key="demo_value_col",
    )
    alpha = st.selectbox(
        "Significance level (α):",
        [0.01, 0.05, 0.10],
        index=1,
        key="demo_alpha",
    )

    st.subheader("Group summary")
    st.dataframe(group_summary(DUMMY_DATA, group_col, value_col), use_container_width=True, hide_index=True)

    checks = run_assumption_checks(DUMMY_DATA, group_col, value_col)
    render_assumption_checks(checks, alpha)

    if st.button("Perform ANOVA analysis for dummy data"):
        result = run_anova(DUMMY_DATA, group_col, value_col, alpha)
        render_results(result)

        if result["significant"]:
            render_tukey(DUMMY_DATA, group_col, value_col)

        render_violin(DUMMY_DATA, group_col, value_col, "violin_plot_dummy_data.png")
