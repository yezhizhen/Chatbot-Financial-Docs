import pickle
from query_data import get_chain
from constants import *
import dotenv
from os import path
dotenv.load_dotenv()


if __name__ == "__main__":
    with open(path.join('embedded_store', STORE_NAME + ".pkl"), "rb") as f:
        vectorstore = pickle.load(f)
    qa_chain = get_chain(vectorstore)
    #limit the length of history
    print("Ask questions related to corporate finance!")
    while True:
        print("Human:")
        question = input()
        result = qa_chain({"question": question})
        print("AI:")
        print(result["answer"])
        print("")
        print(f"Above result is from documents: {[path.split(doc.metadata['source'])[1]  for doc in result['source_documents']]}\n")
