# to run this
# hide the three dots setting list
# streamlit run <script_name> --server.port <your port> --client.toolbarMode minimal --browser.gatherUsageStats False
# streamlit run "Front End OCBC/chatbot.py" --server.port 4000 --client.toolbarMode minimal --browser.gatherUsageStats False
# forever start -c "streamlit run" "Front End OCBC/chatbot.py" --server.port 4000 --client.toolbarMode minimal --browser.gatherUsageStats False
import streamlit as st
from util import *

import json
from os import path


if "relative_dir_name" not in st.session_state:
    st.session_state.relative_dir_name = path.basename(path.dirname(__file__))


def heading():
    st.set_page_config(
        page_title="WealthCX Chatbot V2",
        # 👋
        page_icon=path.join(st.session_state.relative_dir_name, "icon.png"),
        menu_items={"About": "# A chatbot for financial statements/documents"},
        initial_sidebar_state="collapsed",
        layout="centered",
    )
    st.title("ChatCX")


def state_init():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def body():
    col1, col2 = st.columns(2)
    with col1:
        market = st.selectbox("Select market:", ["HKG", "SGP", "US", "all"]).lower()

    with col2:
        with open(
            path.join(st.session_state.relative_dir_name, "stocks.json"), "r"
        ) as f:
            stocks = json.load(f)
            if market == "all":
                ric = st.selectbox(
                    "Stock:", sorted([val for vals in stocks.values() for val in vals])
                )
            else:
                ric = st.selectbox("Stock:", sorted(stocks[market]))

    # window_length_of_years, num_initial_docs
    col1, col2 = st.columns(2)
    with col1:
        # window_length_of_years, num_initial_docs
        window_len = st.slider(
            # ":rainbow[Window size of years]",
            "Number of historical years",
            min_value=1,
            max_value=4,
            value=1,
            help='If set to N, then will look into "latest N years" among search results',
        )
    with col2:
        doc_num = st.slider(
            # ":rainbow[Max limit of documents used]",
            "Number of documents",
            min_value=1,
            max_value=8,
            value=4,
            help="If set to N, will at most use N documents: with total token under model limits",
        )

    st.caption(f"✅Selected stock: **:rainbow[{ric}]**")

    # 👈 Draw the string 'x' and then the value of x

    with st.expander("Chat History", expanded=True):
        for item in st.session_state.chat_history:
            # Human turn
            st.warning(item[0], icon=st.session_state.avatar)
            # bots turn
            st.success(item[1], icon="🤖")

    user_input = st.text_area(
        "Your turn",
        help="Type your message. Click 'Chat' to get response",
        placeholder="Type your questions",
    )

    def chat_handler():
        with st.spinner("Waiting for response..."):
            if user_input.strip() == "":
                st.toast("Done!", icon="⚠️")
                # st.warning("Empty input not allowed", icon="⚠️")
                return
            # add plain question to chat_history, to avoid long context
            # chat through openai
            response, sources = get_chat_response(
                user_input, window_len, doc_num, market
            )
            # add response to history
            st.session_state.chat_history.append((user_input, response))
            st.toast("Done!", icon="✅")

    _, chat, reset = st.columns([0.8, 1, 1])
    with chat:
        st.button("Chat", on_click=chat_handler)
    with reset:
        st.button("Reset", on_click=lambda: st.session_state.chat_history.clear())


def side_bar():
    st.sidebar.markdown("# User config 🦄")
    st.sidebar.selectbox(
        "Your avatar:", ["🧍‍♀️", "🧍‍♂️", "👧", "👦", "👸", "🤴"], key="avatar"
    )
    st.sidebar.text_input("Your name", key="user_name")


heading()
from chat_core import *

hide_footer()
side_bar()
state_init()


body()
