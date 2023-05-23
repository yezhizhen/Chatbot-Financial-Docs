from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.schema import BaseRetriever
import re

template = """Answer only within the context below.  If you don't know the answer, just say "I'm not sure." Don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])

#combine_docs in qa_chain needs the openAI.
# question_generator needs the openAI.

#a wrapper around default retriever, with priority on latest
class date_ordered_retriever(BaseRetriever):
    retriever: VectorStoreRetriever
    date_pattern = re.compile(r'(\d+).txt')
    
    def get_date(self, doc):
        return self.date_pattern.search(doc.metadata["source"]).group(1) 

    def __init__(self, _retriever) -> None:
        super().__init__()
        self.retriever = _retriever
    
    def get_relevant_documents(self, query: str):
        initial_docs = self.retriever.get_relevant_documents(query)
        
        def key_func(doc):
            return self.get_date(doc)

        initial_docs.sort(key= key_func, reverse= True)
        #return those with highest years 
        latest_year = self.get_date(initial_docs[0])[:4]
        for i in range(1, len(initial_docs)):
            if self.get_date(initial_docs[i])[:4] != latest_year:
                return initial_docs[:i]

        return initial_docs


    async def aget_relevant_documents(self, query: str):
        raise NotImplementedError


def get_chain(vectorstore):
    qa_chain = ConversationalRetrievalChain.from_llm(
        OpenAI(temperature=0),
        #default retriever: vectorstore.as_retriever()
        date_ordered_retriever(vectorstore.as_retriever()),
        #remove memory and pass in "chat_history" when calling for manual passing
        memory = ConversationBufferWindowMemory(k = 2, memory_key="chat_history", return_messages=True, output_key='answer'),
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt}
        #verbose= True
    )
    qa_chain.max_tokens_limit = 4095
    return qa_chain
