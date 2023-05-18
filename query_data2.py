from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory


template = """Answer only within the context below.  If you don't know the answer, just say "I'm not sure." Don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""



prompt = PromptTemplate(template=template, input_variables=["context", "question"])

def get_chain(vectorstore):
    qa_chain = ConversationalRetrievalChain.from_llm(
        OpenAI(temperature=0),
        vectorstore.as_retriever(),
        return_source_documents=True,
        combine_docs_chain_kwargs = {"prompt": prompt}
        #verbose= True
    )
    qa_chain.max_tokens_limit = 4095
    return qa_chain
