import dotenv
dotenv.load_dotenv()
from query_data import get_chain
from constants import *
from pathlib import PureWindowsPath
from os import path
import argparse
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings




def pre_process():
    parser = argparse.ArgumentParser(description='A app for interacting with pre compiled documents')
    parser.add_argument('--no_source', action='store_true', help='disable source tracking')
    parser.add_argument('-n', help="Filter Retrieved documents, within N years earlier than the latest returned", default=1, type=int)
    parser.add_argument('-v',"--vectorstore", default=STORE_NAME, type=str, help="index to be used. e.g., SGP_all")
    parser.add_argument('-k', default=6, type=int, help="number of initial documents retrieved")
    args = parser.parse_args()
    
    return args

if __name__ == "__main__":
    args = pre_process()
    history = not args.no_source
    if history:
        print("Source enabled!")
    
    print(f"Using vectorestore {args.vectorstore}, looking back {args.n} years earlier than the latest found, among {args.k} closest docs")
    vectorstore = FAISS.load_local(path.join('embedded_store', args.vectorstore), OpenAIEmbeddings())
    qa_chain = get_chain(vectorstore, args.n, args.k)

    #Always load ratios data as well
    

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
            print(f"Above result is from documents: {[PureWindowsPath(doc.metadata['source']).parts[-1]  for doc in result['source_documents']]}\n")
        print("------")
