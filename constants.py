MAX_HISTORY_LEN = 2
STORE_NAME = "US_SGP_HKG_all"
STORES = ['MSFT_filing','MSFT_transcripts']
WELCOME_MSG = "Hello! Ask anything!"
MODEL = "gpt-3.5-turbo"
RATIO_THRESHOLD = 0.45
DEFINITION_THRESHOLD = 0.41

print(f"Using model {MODEL}")

from langchain.prompts.prompt import PromptTemplate

_template = """Given the following conversation about corporate status, rephrase the follow up question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
chatcx_rephrase_message = PromptTemplate.from_template(_template)

chatcx_system_message = {"role": "system", "content": 'You will be provided context to answer question regarding corporate financial status. Any question about investment recommendation or stock trading advice, must be answered with "please contact the Trading Representative of your broker'}