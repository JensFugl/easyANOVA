import streamlit as st

def app():
    st.header("Welcome to easyANOVA")
    st.write(
        "ANOVA (Analysis of Variance) is a statistical method for comparing three or more "
        "groups to determine whether their means are significantly different from one another. "
        "For example, you might use it to check whether a new automated process in a QC lab "
        "produces results that are equivalent to the existing manual process — or to compare "
        "multiple formulations, batches, or treatment conditions at once."
    )

    st.subheader("When to use ANOVA")
    st.write(
        "Use one-way ANOVA when you have one categorical grouping variable and one continuous "
        "outcome variable, and you want to test whether the group means differ. If you only have "
        "two groups, a t-test is sufficient. If you need to account for multiple factors "
        "simultaneously, consider two-way ANOVA."
    )

    st.subheader("ANOVA assumptions")
    st.markdown(
        "For ANOVA results to be valid, three assumptions should hold:\n"
        "1. **Normality** — the values within each group are approximately normally distributed "
        "(check with a Shapiro-Wilk test; less critical with large samples).\n"
        "2. **Homogeneity of variance** — the variance is roughly equal across groups "
        "(check with Levene's test).\n"
        "3. **Independence** — observations are independent of each other.\n\n"
        "This app checks the first two automatically. If normality or equal variance is violated, "
        "consider the non-parametric Kruskal-Wallis test instead."
    )

    st.subheader("Interpreting results")
    st.markdown(
        "ANOVA produces an **F-statistic** (the ratio of between-group variance to within-group "
        "variance) and a **p-value**.\n\n"
        "- If **p < α** (default α = 0.05): there is a statistically significant difference "
        "between at least two groups. Use the post-hoc Tukey HSD test to find which pairs differ.\n"
        "- If **p ≥ α**: there is no statistically significant difference between the groups.\n\n"
        "**Effect size (η²)** indicates the proportion of total variance explained by the grouping. "
        "A rough guide: η² ≈ 0.01 small, ≈ 0.06 medium, ≈ 0.14 large."
    )

    st.subheader("How to get started")
    st.write(
        "Use the **Demo** page to explore a built-in example dataset, or go straight to the "
        "**App** page to upload your own CSV file and run an analysis."
    )
