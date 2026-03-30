"""Shared utilities for easyANOVA pages."""

import base64
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
from scipy import stats


def fig_to_png_bytes(fig) -> BytesIO:
    """Convert a Plotly figure to PNG bytes suitable for st.download_button."""
    return BytesIO(pio.to_image(fig, format="png"))


def group_summary(data: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Return descriptive statistics (count, mean, std, min, max) per group."""
    summary = (
        data.groupby(group_col)[value_col]
        .agg(Count="count", Mean="mean", Std="std", Min="min", Max="max")
        .reset_index()
        .rename(columns={group_col: "Group"})
    )
    return summary.round(4)


def run_anova(data: pd.DataFrame, group_col: str, value_col: str, alpha: float) -> dict:
    """
    Run a one-way ANOVA and return a results dict.

    Returns:
        f_stat, p_value, eta_squared, significant (bool), result_html (str)
    """
    groups = data[group_col].unique()
    group_data = [data[data[group_col] == g][value_col].dropna().values for g in groups]

    f_stat, p_value = stats.f_oneway(*group_data)

    # Eta-squared: SS_between / SS_total
    grand_mean = data[value_col].dropna().mean()
    ss_total = ((data[value_col].dropna() - grand_mean) ** 2).sum()
    ss_between = sum(
        len(g) * (g.mean() - grand_mean) ** 2 for g in group_data if len(g) > 0
    )
    eta_squared = ss_between / ss_total if ss_total > 0 else float("nan")

    significant = p_value < alpha
    if significant:
        result_html = (
            "<h3 style='color: #e05252;'>There is a statistically significant difference "
            "between the groups.</h3>"
        )
    else:
        result_html = (
            "<h3 style='color: #5285e0;'>There is no statistically significant difference "
            "between the groups.</h3>"
        )

    return {
        "f_stat": f_stat,
        "p_value": p_value,
        "eta_squared": eta_squared,
        "significant": significant,
        "result_html": result_html,
    }


def run_assumption_checks(data: pd.DataFrame, group_col: str, value_col: str) -> dict:
    """
    Run ANOVA assumption checks.

    Returns:
        shapiro: dict of {group_name: (stat, p_value)} — Shapiro-Wilk normality per group
        levene: (stat, p_value) — Levene's test for homogeneity of variance
    """
    groups = data[group_col].unique()
    group_data = {g: data[data[group_col] == g][value_col].dropna().values for g in groups}

    shapiro_results = {}
    for g, vals in group_data.items():
        if len(vals) >= 3:
            stat, p = stats.shapiro(vals)
            shapiro_results[g] = (round(stat, 4), round(p, 4))
        else:
            shapiro_results[g] = (None, None)  # too few observations

    all_vals = [v for v in group_data.values() if len(v) >= 2]
    if len(all_vals) >= 2:
        lev_stat, lev_p = stats.levene(*all_vals)
        levene_result = (round(lev_stat, 4), round(lev_p, 4))
    else:
        levene_result = (None, None)

    return {"shapiro": shapiro_results, "levene": levene_result}


def run_tukey(data: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """
    Run Tukey HSD post-hoc test and return a DataFrame of pairwise comparisons.

    Requires scipy >= 1.8. Returns DataFrame with columns:
        Group 1, Group 2, p-value, Significant
    """
    groups = data[group_col].unique()
    if len(groups) < 2:
        return pd.DataFrame()

    group_data = [data[data[group_col] == g][value_col].dropna().values for g in groups]

    result = stats.tukey_hsd(*group_data)

    rows = []
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            p = result.pvalue[i][j]
            rows.append({
                "Group 1": groups[i],
                "Group 2": groups[j],
                "p-value": round(p, 4),
                "Significant": "Yes" if p < 0.05 else "No",
            })

    return pd.DataFrame(rows)


def render_results(anova_result: dict):
    """Display F-statistic, p-value, eta-squared, and the significance verdict."""
    col1, col2, col3 = st.columns(3)
    col1.metric("F-statistic", f"{anova_result['f_stat']:.4f}")
    col2.metric("p-value", f"{anova_result['p_value']:.4f}")
    col3.metric("Effect size (η²)", f"{anova_result['eta_squared']:.4f}")
    st.markdown(anova_result["result_html"], unsafe_allow_html=True)


def render_assumption_checks(checks: dict, alpha: float = 0.05):
    """Render assumption check results inside an expander."""
    with st.expander("Assumption checks", expanded=False):
        st.markdown(
            "ANOVA assumes **normality** within each group (Shapiro-Wilk) and "
            "**homogeneity of variance** across groups (Levene's test). "
            f"Results flagged ⚠️ have p < {alpha}, suggesting a potential violation."
        )

        # Shapiro-Wilk
        st.markdown("**Normality (Shapiro-Wilk) — per group**")
        shapiro_rows = []
        for group, (stat, p) in checks["shapiro"].items():
            if stat is None:
                shapiro_rows.append({"Group": group, "Statistic": "N/A", "p-value": "N/A", "Note": "Too few observations"})
            else:
                flag = " ⚠️" if p < alpha else ""
                shapiro_rows.append({"Group": group, "Statistic": stat, "p-value": p, "Note": f"p < {alpha}{flag}" if p < alpha else "OK"})
        st.dataframe(pd.DataFrame(shapiro_rows), use_container_width=True, hide_index=True)

        # Levene
        st.markdown("**Homogeneity of variance (Levene's test)**")
        lev_stat, lev_p = checks["levene"]
        if lev_stat is None:
            st.write("Could not compute Levene's test (insufficient data).")
        else:
            flag = " ⚠️" if lev_p < alpha else ""
            st.write(f"Statistic: {lev_stat} | p-value: {lev_p}{flag}")
            if lev_p < alpha:
                st.caption("Unequal variances detected. Consider Welch's ANOVA for more robust results.")


def render_tukey(data: pd.DataFrame, group_col: str, value_col: str):
    """Render Tukey HSD post-hoc results inside an expander."""
    with st.expander("Post-hoc analysis (Tukey HSD)", expanded=False):
        st.write(
            "The ANOVA result is significant. Tukey's HSD test identifies which specific "
            "group pairs are different from each other."
        )
        tukey_df = run_tukey(data, group_col, value_col)
        if tukey_df.empty:
            st.write("Not enough groups for post-hoc analysis.")
        else:
            st.dataframe(tukey_df, use_container_width=True, hide_index=True)


def render_violin(data: pd.DataFrame, group_col: str, value_col: str, download_filename: str):
    """Draw a violin + box plot and provide a PNG download button."""
    fig = px.violin(
        data,
        x=group_col,
        y=value_col,
        box=True,
        points="all",
        title="Violin Plot",
    )
    fig.update_layout(autosize=True, margin=dict(l=0, r=0, t=30, b=0), width=None)
    st.plotly_chart(fig, use_container_width=True)
    st.download_button(
        label="Download Violin Plot",
        data=fig_to_png_bytes(fig),
        file_name=download_filename,
        mime="image/png",
    )
