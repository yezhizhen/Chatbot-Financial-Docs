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
from utility import my_util
from constants import MODEL

# If you don't know the answer, just say "I'm not sure." Don't try to make up an answer.
template = """
Only use the following context to provide the answer to the question at the end.  Must reply I don't have the answer to this question if there is no answer from the context or the question is about tagline.
Any question about investment recommendation or stock trading advice (except about financial performance and comparsion), must answer please contact the Trading Representative of your broker.

{context}

Question: {question}. Summarize in not more than 150 words.
Helpful  Answer:"""

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
        #can be paralleled
        ratio_doc = self.ratios_store.similarity_search_with_score(query, k = 1)
        #[(ratio1(page_content, doc),score), ...]
        #print(ratio_doc)
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
        fin= res[:int(len(res)/3)] + [ratio_doc[0][0]] + res[int(len(res)/3):]  
        return fin

    async def aget_relevant_documents(self, query: str):
        raise NotImplementedError


#combine_docs in qa_chain needs the openAI.

#return documents in latest the year among results

def get_chain(vectorstore, n = 1, k = 6):
    qa_chain = ConversationalRetrievalChain.from_llm(
        OpenAI(temperature=0), #add model_name
        #default retriever: vectorstore.as_retriever()
        latest_n_year_retriever(vectorstore.as_retriever(search_kwargs={"k":k}), n),
        #remove memory and pass in "chat_history" when calling for manual passing
        memory = ConversationBufferWindowMemory(k = MAX_HISTORY_LEN, memory_key="chat_history", return_messages=True, output_key='answer'),
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},
        #max_tokens_limit = 4097 - 256 - Base.get_num_tokens(template)
        #verbose= True
    )

    template_token = my_util.num_tokens_from_string(template, MODEL)
    print(f"Template occpuies {template_token} tokens")
    qa_chain.max_tokens_limit = 4097 - 270 - template_token
    return qa_chain
