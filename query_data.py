from langchain.prompts.prompt import PromptTemplate

# from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.schema import BaseRetriever
from langchain.chat_models import ChatOpenAI
import re
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from os import path
from utility import my_util
from constants import *

# Answer "I don't have the answer to this question" if there is no answer from the context.
# If you don't know the answer, just say "I'm not sure." Don't try to make up an answer.
# Summarize in no more than 150 words and in complete sentences.
# (except about financial performance and comparsion)
template = """You are a corporate performance analyst. Use the following context to provide the answer to the question at the end. Any question about stock recommendation, must be answered with "please contact the Trading Representative of your broker".

{context}

Question: {question}   Answer:
"""

default_prompt = PromptTemplate(
    template=template, input_variables=["context", "question"]
)

# combine_docs in qa_chain needs the openAI.
# question_generator needs the openAI.

# a wrapper around default retriever, with priority on latest
# return documents in latest the year among results
class latest_n_year_retriever(BaseRetriever):
    retriever: VectorStoreRetriever
    date_pattern = re.compile(r"(\d+).txt")
    ratios_store = FAISS.load_local(
        path.join("embedded_store", "Ratios"), OpenAIEmbeddings()
    )
    financial_definition_store = FAISS.load_local(
        path.join("embedded_store", "financial_definition"), OpenAIEmbeddings()
    )

    def get_date(self, doc):
        res = self.date_pattern.search(doc.metadata["source"])
        return res.group(1)

    def __init__(self, _retriever, _n) -> None:
        super().__init__()
        self.retriever = _retriever
        self.n = _n

    def get_relevant_documents(self, query: str):
        # can be paralleled
        # score is the distance
        ratio_docs = self.ratios_store.similarity_search_with_score(query, k=1)
        def_docs = self.financial_definition_store.similarity_search_with_score(
            query, k=2
        )
        # [(ratio1(page_content, doc),score), ...]
        # print(f"score for ratio doc is: {ratio_doc[0][1]}\n\nWith content {ratio_doc[0][0].page_content}\n\n")
        # print(f"score for financial definition doc is: {def_docs[0][1]}\n\nWith content {def_docs[0][0].page_content}\n\n")
        # print(f"score for financial definition doc is: {def_doc[1][1]}\n\nWith content {def_doc[1][0].page_content}\n")

        # Can try MMR next
        initial_docs = self.retriever.get_relevant_documents(query)

        def key_func(doc):
            return self.get_date(doc)

        initial_docs.sort(key=key_func, reverse=True)

        # return those with highest years
        latest_year = self.get_date(initial_docs[0])[:4]
        res = initial_docs
        for i in range(1, len(initial_docs)):
            if int(self.get_date(initial_docs[i])[:4]) < int(latest_year) - self.n:
                res = initial_docs[:i]
                break
        # put ratio in the middle, in case it takes priority response
        fin = (
            [doc[0] for doc in ratio_docs if doc[1] < RATIO_THRESHOLD]
            + [doc[0] for doc in def_docs if doc[1] < DEFINITION_THRESHOLD]
            + res
        )
        return fin

    async def aget_relevant_documents(self, query: str):
        raise NotImplementedError


# combine_docs in qa_chain needs the openAI.

# return documents in latest the year among results


def get_chain(vectorstore, n=1, k=6, prompt=default_prompt):
    template_token = my_util.num_tokens_from_string(template, MODEL)
    print(f"Template occpuies {template_token} tokens")
    qa_chain = ConversationalRetrievalChain.from_llm(
        # openAI(temperature=0), #default as text-davinci-003.
        ChatOpenAI(temperature=0, model_name=MODEL),
        # OpenAI(temperature=0),
        # default retriever:
        # vectorstore.as_retriever(),
        latest_n_year_retriever(vectorstore.as_retriever(search_kwargs={"k": k}), n),
        condense_question_prompt=chatcx_rephrase_message,
        # remove memory and pass in "chat_history" when calling for manual passing
        # memory = ConversationBufferWindowMemory(k = MAX_HISTORY_LEN, memory_key="chat_history", return_messages=True, output_key='answer'),
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},
        max_tokens_limit=4096 - 270 - template_token
        # verbose= True
    )

    return qa_chain
