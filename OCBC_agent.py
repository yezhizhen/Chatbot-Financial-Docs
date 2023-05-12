import pickle
from query_data import get_chain
from constants import *
import dotenv
from os import path
import argparse

dotenv.load_dotenv()

def pre_process():
    parser = argparse.ArgumentParser(description='A cli app for interacting with financial documents')
    parser.add_argument('--source', action='store_true', help='enable source tracking')
    args = parser.parse_args()
    return args.source


if __name__ == "__main__":
    history = pre_process()
    with open(path.join('embedded_store', "faq_ocbc.pkl"), "rb") as f:
        vectorstore = pickle.load(f)
    qa_chain = get_chain(vectorstore)
    #limit the length of history
    print("I am your agents answering questions about trade limits. How may I help?")
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
