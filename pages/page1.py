import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.io as pio
from io import BytesIO
import base64

def plot_to_base64(fig):
    img_base64 = base64.b64encode(pio.to_image(fig, format="png")).decode("utf-8")
    return img_base64

def app():
    st.title("How it works")

    dummy_data = pd.DataFrame({"ThreeGroup": ["A"] * 5 + ["B"] * 5 + ["C"] * 5,
                               "TwoGroup": ["X"] * 7 + ["Y"] * 8,
                               "DifferentValues": [10, 12, 9, 11, 13, 20, 21, 19, 18, 22, 30, 29, 31, 28, 32],
                               "SimilarValues": [5, 6, 5, 6, 7, 6, 5, 7, 6, 5, 7, 5, 6, 6, 7]})

    # Filter columns based on dtype
    string_columns = dummy_data.select_dtypes(include=['object']).columns
    numeric_columns = dummy_data.select_dtypes(include=[np.number]).columns

    if st.button("Load Dummy Data"):
        st.session_state.data_loaded = True

        if 'group_col' not in st.session_state:
            st.session_state.group_col = string_columns[0]

        if 'value_col' not in st.session_state:
            st.session_state.value_col = numeric_columns[0]

    if 'data_loaded' in st.session_state and st.session_state.data_loaded:
        st.write(dummy_data)

        st.session_state.group_col = st.selectbox("Select the column for grouping (categorical):", string_columns, index=list(string_columns).index(st.session_state.group_col))
        st.session_state.value_col = st.selectbox("Select the column for values (numerical):", numeric_columns, index=list(numeric_columns).index(st.session_state.value_col))

        if st.button("Perform ANOVA analysis for dummy data"):
            # Perform ANOVA analysis for the dummy data
            groups = dummy_data[st.session_state.group_col].unique()
            data = [dummy_data[dummy_data[st.session_state.group_col] == g][st.session_state.value_col].values for g in groups]
            f_stat, p_value = stats.f_oneway(*data)

            st.session_state.f_stat = f_stat
            st.session_state.p_value = p_value

            alpha = 0.05
            if p_value < alpha:
                st.session_state.result = "<h3 style='color: red;'>There is a statistically significant difference between the groups.</h3>"
            else:
                st.session_state.result = "<h3 style='color: blue;'>There is no statistically significant difference between the groups.</h3>"

            if "f_stat" in st.session_state:
                st.write(f"F-statistic: {st.session_state.f_stat}")
                st.write(f"P-value: {st.session_state.p_value}")
                st.markdown(st.session_state.result, unsafe_allow_html=True)

            # Plot the violin plot for the dummy data
            fig_dummy = px.violin(dummy_data, x=st.session_state.group_col, y=st.session_state.value_col, box=True, points="all", title="Violin Plot")
            fig_dummy.update_layout(autosize=True, margin=dict(l=0, r=0, t=30, b=0), width=None)
            st.plotly_chart(fig_dummy, use_container_width=True)
            img_base64_dummy = plot_to_base64(fig_dummy)
            st.download_button(
                label="Download Violin Plot",
                data=BytesIO(base64.b64decode(img_base64_dummy)),
                file_name="violin_plot_dummy_data.png",
                mime="image/png",
            )