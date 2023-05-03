from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

'''
template = """Answering questions about the corporate financial status and providing investment advise, 
with the following extracted parts and a question.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
Question: {question}
=========
{context}
=========
Answer:"""
QA_PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])
'''

#combine_docs in qa_chain needs the openAI.
# question_generator needs the openAI.

def get_chain(vectorstore):
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        OpenAI(temperature=0),
        vectorstore.as_retriever(),
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key='answer'),
        return_source_documents=True
    )
    return qa_chain
