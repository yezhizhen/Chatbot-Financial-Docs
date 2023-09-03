import streamlit as st


def hide_footer():
    # #MainMenu {visibility: hidden;}
    hide_streamlit_style = """
                <style>
                
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
