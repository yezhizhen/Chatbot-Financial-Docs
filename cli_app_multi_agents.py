import pickle
from query_data import get_chain
from constants import *
import dotenv
from os import path
dotenv.load_dotenv()

if __name__ == "__main__":
    chains = []
    for STORE in STORES:
        with open(path.join('embedded_store', STORE + ".pkl"), "rb") as f:
            vectorstore = pickle.load(f)
        chains.append(get_chain(vectorstore))


    #limit the length of history
    print("Ask questions related to corporate finance!")
    while True:
        print("Human:")
        question = input()
        for i, chain in enumerate(chains):
            result = chain({"question": question})
            print(f"Agent {i}:")
            print(result["answer"])
            print(f"Above result is from documents: {[path.split(doc.metadata['source'])[1] for doc in result['source_documents']]}\n")
            #date ordering
            print("---------------")
            