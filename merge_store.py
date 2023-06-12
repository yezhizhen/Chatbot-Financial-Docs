from os import path
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
import dotenv

dotenv.load_dotenv()

STORES = ["transcript", "filing_all"]
FINAL_STORE = "filing_transcript_all"

res = None
for store in STORES:
    cur = FAISS.load_local(path.join('embedded_store', store), OpenAIEmbeddings())
    if res is None:    
        res = cur
    else:
        res.merge_from(cur)


res.save_local(path.join('embedded_store', FINAL_STORE))