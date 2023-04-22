import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.io as pio
from io import BytesIO
import base64


st.set_page_config(
    page_title="ANOVA Analysis and Violin Plot Web App",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="auto",
)


def plot_to_base64(fig):
    img_base64 = base64.b64encode(pio.to_image(fig, format="png")).decode("utf-8")
    return img_base64


def main_app():
    st.title("Easy ANOVA")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.write("The first 5 rows of the dataset:")
        st.write(df.head())

        group_col = st.selectbox("Select the column for grouping (categorical):", df.columns)
        value_col = st.selectbox("Select the column for values (numerical):", df.columns)

        if st.button("Perform ANOVA analysis"):
            groups = df[group_col].unique()
            data = [df[df[group_col] == g][value_col].values for g in groups]
            f_stat, p_value = stats.f_oneway(*data)

            st.write(f"F-statistic: {f_stat}")
            st.write(f"P-value: {p_value}")

            alpha = 0.05
            if p_value < alpha:
                st.write("There is a statistically significant difference between the groups.")
            else:
                st.write("There is no statistically significant difference between the groups.")

            fig = px.violin(df, x=group_col, y=value_col, box=True, points="all", title="Violin Plot")
            st.plotly_chart(fig, use_container_width=True)

            img_base64 = plot_to_base64(fig)
            st.download_button(
                label="Download Violin Plot",
                data=BytesIO(base64.b64decode(img_base64)),
                file_name="violin_plot.png",
                mime="image/png",
            )


def how_it_works():
    st.title("How it works")

    st.write("""
    The app takes a CSV file with two columns: one for categorical data (grouping) and one for numerical data (values).
    The app performs an ANOVA analysis to determine if there's a statistically significant difference between the groups.
    The data is also visualized using a violin plot.
    """)

    st.write("Here's an example using the following dummy data:")
    dummy_data = pd.DataFrame({"Group": ["A"] * 5 + ["B"] * 5 + ["C"] * 5,
                               "Value": [10, 12, 9, 11, 13, 20, 21, 19, 18, 22, 30, 29, 31, 28, 32]})
    
    if st.button("Load Dummy Data"):
        st.write(dummy_data)
    
    st.write("The categorical column (Group) has three groups: A, B, and C.")
    st.write("The numerical column (Value) contains the values associated with each group.")

    if len(dummy_data.columns) > 2:
        group_col = st.selectbox("Select the column for grouping (categorical):", dummy_data.columns)
        value_col = st.selectbox("Select the column for values (numerical):", dummy_data.columns)
    else:
        group_col, value_col = dummy_data.columns

    if st.button("Perform ANOVA analysis for dummy data"):
        # Perform ANOVA analysis for the dummy data
        groups = dummy_data[group_col].unique()
        data = [dummy_data[dummy_data[group_col] == g][value_col].values for g in groups]
        f_stat, p_value = stats.f_oneway(*data)

        st.session_state.f_stat = f_stat
        st.session_state.p_value = p_value

        alpha = 0.05
        if p_value < alpha:
            st.session_state.result = "There is a statistically significant difference between the groups."
        else:
            st.session_state.result = "There is no statistically significant difference between the groups."
        if "f_stat" in st.session_state:
            st.write(f"F-statistic: {st.session_state.f_stat}")
            st.write(f"P-value: {st.session_state.p_value}")
            st.write(st.session_state.result)

        # Plot the violin plot for the dummy data
        fig_dummy = px.violin(dummy_data, x=group_col, y=value_col, box=True, points="all", title="Violin Plot")
        st.plotly_chart(fig_dummy)

        img_base64_dummy = plot_to_base64(fig_dummy)
        st.download_button(
            label="Download Violin Plot",
            data=BytesIO(base64.b64decode(img_base64_dummy)),
            file_name="violin_plot_dummy_data.png",
            mime="image/png",
        )




# Create a navigation menu with the main app and the how_it_works page
pages = {
    "Easy ANOVA": main_app,
    "How it Works": how_it_works,
}

st.sidebar.title("")
page = st.sidebar.radio("", list(pages.keys()))

# Display the selected page
pages[page]()

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)