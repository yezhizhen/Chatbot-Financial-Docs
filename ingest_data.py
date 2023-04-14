from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pickle
import dotenv
import os
from constants import *

#load openai_api_key
dotenv.load_dotenv()

FOLDER_PATH = os.path.join(".", DOCUMENT_ID) 

raw_documents = []
# Load Data
for file in os.listdir(FOLDER_PATH):
    loader = UnstructuredFileLoader(os.path.join(FOLDER_PATH, file))
    raw_documents += loader.load()

# Split text
text_splitter = RecursiveCharacterTextSplitter(chunk_size= 3400, chunk_overlap = 50)
documents = text_splitter.split_documents(raw_documents)


# Load Data to vectorstore
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)


# Save vectorstore
with open(DOCUMENT_ID + ".pkl", "wb") as f:
    pickle.dump(vectorstore, f)
