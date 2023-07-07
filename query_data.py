from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.schema import BaseRetriever
import re
from constants import MAX_HISTORY_LEN
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from os import path

# If you don't know the answer, just say "I'm not sure." Don't try to make up an answer.
template = """You are investment advisor.
Assume audience are novice investors. 
You are also tasked with making sure they understand the answer, and if they need any other help.
Answer only in the third person.
If question is unrelated to financial markets, and related to investment advice or how to trade - you must tell the user to contact their OSPL Trading Representative.
Answer and explain related questions only within the context below. 

{context}

Question: {question}
Helpful Answer:"""




"""Answer investment related question only within the context below. 

{context}

Question: {question}
Helpful Answer:"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])

#combine_docs in qa_chain needs the openAI.
# question_generator needs the openAI.

#a wrapper around default retriever, with priority on latest
#return documents in latest the year among results
class latest_n_year_retriever(BaseRetriever):
    retriever: VectorStoreRetriever
    date_pattern = re.compile(r'(\d+).txt')
    ratios_store = FAISS.load_local(path.join('embedded_store', "Ratios"), OpenAIEmbeddings())

    def get_date(self, doc):
        res = self.date_pattern.search(doc.metadata["source"])
        return res.group(1) 

    def __init__(self, _retriever, _n) -> None:
        super().__init__()
        self.retriever = _retriever
        self.n = _n
    
    def get_relevant_documents(self, query: str):
        ratio_doc = self.ratios_store.similarity_search(query, k = 1)
        
        initial_docs = self.retriever.get_relevant_documents(query)

        def key_func(doc):
            return self.get_date(doc)

        initial_docs.sort(key= key_func, reverse= True)
        
        #return those with highest years 
        latest_year = self.get_date(initial_docs[0])[:4]
        res = initial_docs
        for i in range(1, len(initial_docs)):
            if int(self.get_date(initial_docs[i])[:4]) < int(latest_year) - self.n:
                res =  initial_docs[:i]
                break
        #put ratio in the middle, in case it takes priority response
        return res[:int(len(res)/2)] + [ratio_doc[0]] + res[int(len(res)/2):]  

    async def aget_relevant_documents(self, query: str):
        raise NotImplementedError


#combine_docs in qa_chain needs the openAI.

#return documents in latest the year among results


def get_chain(vectorstore, n = 1, k = 6):
    qa_chain = ConversationalRetrievalChain.from_llm(
        OpenAI(temperature=0),
        #default retriever: vectorstore.as_retriever()
        latest_n_year_retriever(vectorstore.as_retriever(search_kwargs={"k":k}), n),
        #remove memory and pass in "chat_history" when calling for manual passing
        memory = ConversationBufferWindowMemory(k = MAX_HISTORY_LEN, memory_key="chat_history", return_messages=True, output_key='answer'),
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},
        #verbose= True
    )
    qa_chain.max_tokens_limit = 4097 - 30 - qa_chain.combine_docs_chain.llm_chain.llm.get_num_tokens(template)
    return qa_chain
