import streamlit as st
from pages import page1, page2, page3

PAGES = {
    "Demo": page1,
    "About": page2,
    "App": page3,
}


st.set_page_config(
    page_title="easyANOVA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session state variable if it doesn't exist
if 'selection' not in st.session_state:
    st.session_state.selection = 'Demo'

# Create columns for radio buttons
with st.container():
    cols = st.columns(3)

    with cols[0]:
        if st.button("Demo"):
            st.session_state.selection = "Demo"

    with cols[1]:
        if st.button("About"):
            st.session_state.selection = "About"

    with cols[2]:
        if st.button("App"):
            st.session_state.selection = "App"

if st.session_state.selection:
    page = PAGES.get(st.session_state.selection)
    page.app()
else:
    st.header("Please select a page from the navigation ribbon above.")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .reportview-container .main .block-container {max-width: 100% !important;}
            .css-17eq0hr {display: none !important;}
            .css-1v3fvcr {margin-left: 0 !important;}
            </style>
            """

st.markdown(hide_st_style, unsafe_allow_html=True)
