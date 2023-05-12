import pickle
from os import path
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

def convert(STORE_NAME):
    with open(path.join('embedded_store_old', STORE_NAME + ".pkl"), "rb") as f:
        vectorstore = pickle.load(f)
        FAISS.save_local(vectorstore, path.join("embedded_store", STORE_NAME))