from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader, TextLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import dotenv
import os
from constants import *
import time

# load openai_api_key
dotenv.load_dotenv()

# take 1.6465 seconds to chunk each file, params 3000, 0
# 0.22s to embed.
output_name = "financial_definition"

raw_documents = []
start = time.time()
FOLDER_PATH = r"D:\OneDrive - The Chinese University of Hong Kong\Affair\Job\WealthCX\project\Refinitiv API\Filings API\tutorial\python\documents\financial_definition"
# Load Data
for root, dirs, files in os.walk(FOLDER_PATH):
    source_files = [file for file in files if os.path.splitext(file)[1] == ".txt"]
    print(f"Found {len(source_files)} to load in {root}")
    for file in source_files:
        try:
            loader = TextLoader(os.path.join(root, file), encoding="utf8")
            # loader = UnstructuredFileLoader(os.path.join(root, file), encoing='utf8')
            raw_documents += loader.load()
        except Exception as e:
            print(f"{file} has failed, in {root}")
            print(e)


# Split text
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2200, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)

print(f"Took {time.time()-start}s to chunk files.")

start = time.time()
# Load Data to vectorstore
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
print(f"Took {time.time()-start}s to create embedding {output_name}")


# Save vectorstore
vectorstore.save_local(os.path.join("embedded_store", output_name))
