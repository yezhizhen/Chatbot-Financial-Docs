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



raw_documents = []
# Load Data
for root, dirs, files in os.walk(FOLDER_PATH):
    source_files = [file for file in files if os.path.splitext(file)[1] == '.txt']
    for file in source_files:
        try:
            loader = UnstructuredFileLoader(os.path.join(root, file))
            raw_documents += loader.load()
        except Exception as e:
            print(f"{file} has failed, in {root}")
            print(e)

# Split text
text_splitter = RecursiveCharacterTextSplitter(chunk_size= 3400, chunk_overlap = 0)
documents = text_splitter.split_documents(raw_documents)


# Load Data to vectorstore
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)


# Save vectorstore
with open(STORE_NAME + ".pkl", "wb") as f:
    pickle.dump(vectorstore, f)
