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

if "selection" not in st.session_state:
    st.session_state.selection = "Demo"

cols = st.columns(3)
with cols[0]:
    if st.button("Demo", use_container_width=True):
        st.session_state.selection = "Demo"
with cols[1]:
    if st.button("About", use_container_width=True):
        st.session_state.selection = "About"
with cols[2]:
    if st.button("App", use_container_width=True):
        st.session_state.selection = "App"

# Active page indicator
st.markdown(
    f"<p style='text-align:center; color: #2E7CFF; margin-top: -8px; font-size: 0.85rem;'>"
    f"▲ {st.session_state.selection}</p>",
    unsafe_allow_html=True,
)
st.divider()

PAGES[st.session_state.selection].app()

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)
