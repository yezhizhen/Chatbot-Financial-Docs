MAX_HISTORY_LEN = 2
STORE_NAME = "US_SGP_HKG_all"
STORES = ['MSFT_filing','MSFT_transcripts']
WELCOME_MSG = "Hello! Ask anything!"
MODEL = "text-davinci-003"
RATIO_THRESHOLD = 0.45
DEFINITION_THRESHOLD = 0.41



#following is dummy copy. ignore.
"""Only use the following pieces of context to provide the answer to the question at the end.  Otherwise reply I don't have the answer to this question.
Any question asking for investment or stock trading advice (except it is about financial performance and comparsion), you must answer please contact the Trading Representative of your broker.
Any question about tagline, reply I don't have the answer to this question.

{context}

Question: {question}. Summarize in not more than 150 words.
Helpful  Answer:"""




"""Answer investment related question only within the context below. 

{context}

Question: {question}
Helpful Answer:"""