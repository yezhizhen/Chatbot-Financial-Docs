from query_data import get_chain
from constants import *
import dotenv
from os import path
import argparse
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

dotenv.load_dotenv()


def pre_process():
    parser = argparse.ArgumentParser(description='A app for interacting with pre compiled documents')
    parser.add_argument('--source', action='store_true', help='enable source tracking')
    parser.add_argument('-n', help="Filter Retrieved documents, within n years earlier than the latest returned", default=0, type=int)
    parser.add_argument('-v',"--vectorstore", default=STORE_NAME, type=str, help="index to be used")
    parser.add_argument('-k', default=6, type=int, help="number of initial documents retrieved")
    args = parser.parse_args()
    
    return args

if __name__ == "__main__":
    args = pre_process()
    history = args.source
    if history:
        print("Source enabled!")
    
    print(f"Using vectorestore {args.vectorstore}, looking back {args.n} years earlier than the latest found, among {args.k} initial docs")
    vectorstore = FAISS.load_local(path.join('embedded_store', args.vectorstore), OpenAIEmbeddings())
    qa_chain = get_chain(vectorstore, args.n, args.k)
    #limit the length of history
    print(WELCOME_MSG)
    while True:
        print("Human:")
        question = input()
        result = qa_chain({"question": question})
        print("AI:")
        print(result["answer"])
        print("")
        if history:
            print(f"Above result is from documents: {[path.split(doc.metadata['source'])[1]  for doc in result['source_documents']]}\n")
        print("------")
