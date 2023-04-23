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

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        st.write(data)
        group_col = st.selectbox("Select the column for grouping (categorical):", [col.strip() for col in data.columns])
        value_col = st.selectbox("Select the column for values (numerical):", [col.strip() for col in data.columns])


        if st.button("Perform ANOVA analysis"):
            # Perform ANOVA analysis for the uploaded data
            groups = data[group_col].unique()
            data = [data[data[group_col] == g][value_col].values for g in groups]
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

            # Plot the violin plot for the uploaded data
            fig_data = px.violin(data_frame=data, x=str(group_col), y=str(value_col), box=True, points="all", title="Violin Plot")
            fig_data.update_layout(autosize=True, margin=dict(l=0, r=0, t=30, b=0), width=None)
            st.plotly_chart(fig_data, use_container_width=True)
            img_base64_data = plot_to_base64(fig_data)
            st.download_button(
                label="Download Violin Plot",
                data=BytesIO(base64.b64decode(img_base64_data)),
                file_name="violin_plot_data.png",
                mime="image/png",
            )
