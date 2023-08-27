#to run this
# hide the three dots setting list
# streamlit run <script_name> --server.port <your port> --client.toolbarMode minimal --browser.gatherUsageStats False
# streamlit run chatbot.py --server.port 4000 --client.toolbarMode minimal --browser.gatherUsageStats False
# forever start -c "streamlit run" chatbot.py --server.port 4000 --client.toolbarMode minimal --browser.gatherUsageStats False
import streamlit as st
import pandas as pd
from util import hide_footer
from PIL import Image
import json



def heading():
    st.set_page_config(
        page_title="WealthCX Chatbot V1",
        # 👋
        page_icon=r"icon.png",
        menu_items={
        'About': "# A chatbot for financial statements/documents"
        }
        )
    st.title('ChatCX')


def state_init():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = ["I am here to query to ask for your help.","Nice to meet you"]

    
    

def body():
    col1, col2 = st.columns(2)
    with col1:
        market = st.selectbox("Select market:", ["HKG", "SGP","US","all"]).lower()

    with col2:
        with open("stocks.json","r") as f:
            stocks = json.load(f)
            if market == "all":
                ric = st.selectbox("Stock:", sorted([val for vals in stocks.values() for val in vals]))
            else:
                ric = st.selectbox("Stock:", sorted(stocks[market]))

    st.caption(f"Selected stock: {ric}")
    

      # 👈 Draw the string 'x' and then the value of x
    
    with st.expander("Chat History", expanded=True):
        for ind, item in enumerate(st.session_state.chat_history):
            # Human turn
            if ind % 2 == 0:
                st.warning(item, icon=st.session_state.avatar)
            # bots turn
            else:
                st.success(item,icon="🤖")
            

    user_input = st.text_area("Your turn", help="Type your message. Click 'Chat' to get response")

    def chat_handler():
        st.session_state.chat_history.append(user_input)

        # chat through openai

        #add response to history
        st.session_state.chat_history.append("My answer expected to deliver in this week")

    _, chat, reset = st.columns([0.8,1,1])
    with chat:
        st.button('Chat', on_click=chat_handler)  
    with reset:
        st.button('Reset', on_click= lambda: st.session_state.chat_history.clear())
        
        
        

def side_bar():
    st.sidebar.markdown("# User config 🦄")
    st.sidebar.selectbox("Your avatar:", ["👧","👦","👸","🤴"], key="avatar")
    st.sidebar.text_input("Your name", key="user_name")

heading()
side_bar()
state_init()
hide_footer()


body()


