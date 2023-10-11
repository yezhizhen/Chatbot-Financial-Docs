import streamlit as st

import sys


@st.cache_data
def add_path():
    import dotenv

    # to be changed
    dotenv.load_dotenv()
    sys.path.insert(0, ".")


add_path()

import openai
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from os import path
import json


@st.cache_resource(show_spinner="Loading corresponding vectorstore...")
def get_vectorstore(market):  # n, k
    # print(f"Using vectorestore {args.vectorstore}, looking back {args.n} years earlier than the latest found, among {args.k} closest docs")
    print(f"Getting vectorstore in {market}")

    with open(
        path.join(st.session_state.relative_dir_name, "market_to_index.json"), "r"
    ) as f:
        index_name = json.load(f)[market.lower()]
    vectorstore = FAISS.load_local(
        path.join("embedded_store", index_name), OpenAIEmbeddings()
    )
    return vectorstore
    # qa_chain = get_chain(vectorstore, args.n, args.k)


@st.cache_resource(show_spinner="Loading ChatCX retriever...")
def get_retriever(window_length_of_years, num_initial_docs, market):
    from query_data import latest_n_year_retriever

    print(
        f"Getting retriever with window length: {window_length_of_years}, docs limit: {num_initial_docs}, in {market}"
    )
    vectorstore = get_vectorstore(market)
    return latest_n_year_retriever(
        vectorstore.as_retriever(
            search_kwargs={"k": num_initial_docs}, search_type="mmr"
        ),
        window_length_of_years,
        st.session_state.education_mode,
    )


@st.cache_resource(show_spinner="Loading ChatCX resources...")
def get_qa_chain(market, window_length_of_years, num_initial_docs):
    print(
        f"Getting chain with window length: {window_length_of_years}, docs limit: {num_initial_docs}, in {market}"
    )
    from query_data import get_chain
    from langchain.prompts.prompt import PromptTemplate

    template = """You are an analyst, evaluating corporate performance. Use the following context to provide an answer to the question at the end.

    Context: {context}

    ###
    Question: {question}   Answer:
    """

    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    return get_chain(
        get_vectorstore(market),
        window_length_of_years,
        num_initial_docs,
        prompt,
        st.session_state.education_mode,
    )


def get_response(chat_history: list[str]):
    from constants import MODEL

    [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {
            "role": "assistant",
            "content": "The Los Angeles Dodgers won the World Series in 2020.",
        },
        {"role": "user", "content": "Where was it played?"},
    ]

    res = openai.ChatCompletion.create(model=MODEL, messages=chat_history)
    return res["choices"][0]["message"]["content"]


def get_chat_response(question, window_length_of_years, num_initial_docs, market, ric):
    """
    Return answer and source
    """
    qa_chain = get_qa_chain(market, window_length_of_years, num_initial_docs)
    result = qa_chain(
        {
            "question": question,
            "chat_history": st.session_state.chat_history,
            "ric": ric,
        }
    )
    # chat_history.append((question, result["answer"]))
    return result["answer"], result["source_documents"]

    # if True:
    #    print(f"Above result is from documents: {[PureWindowsPath(doc.metadata['source']).parts[-1]  for doc in result['source_documents']]}\n")

    # class Document(BaseModel):
    """
    Document

    page_content: str
    metadata: dict = Field(default_factory=dict)
    """

    """
    #first rephrase the question with context
    if len(st.session_state.chat_history)==0:
        rephrased_question = question
    else:
        rephrased_question = get_response([chatcx_rephrase_message, st.session_state.chat_history])


    retriever.get_relevant_documents(rephrased_question)

    get_response([chatcx_system_message, *chat_history])
    """
    # Gotta rephrase. Better use the old way.
