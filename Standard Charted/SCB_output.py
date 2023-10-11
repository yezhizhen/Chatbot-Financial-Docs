import pandas as pd
from langchain.chat_models import ChatOpenAI
import dotenv
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
import asyncio


async def main():
    dotenv.load_dotenv("../.env")

    filename="events.xlsx"
    MODEL_NAME="gpt-3.5-turbo"
    events = pd.read_excel(filename, sheet_name="Events", header=None)[0]

    llm = ChatOpenAI(temperature=0, model_name=MODEL_NAME)

    '''target output
    for Company name:
    {Company Name} has {(col -> Sheet2.Name(col)) for col in sheet1 columns} {col.val}, , , .
    '''

    prompt1 = "Summarize the below for an university student in 100 words or less."
    prompt2 = "Summarize the below for a begginer investor, by providing wider explanation and context in 4 bulletpoints. In less than 50 characters, the first bulletpoint should be an overall summary. In less than 50 characters, the second bulletpoint should be an investors analysis of current status. In less than 50 characters, the third bulletpoint should describe what investors expect to happen. In less than 50 characters, the fourth bulletpoint should focus on why this information may be important to any scheduled economic calendar events."
    messages1 = []
    messages2 = []
    for event in events:
        messages1.append([SystemMessage(content=prompt1), HumanMessage(content=event)]) 
        messages2.append([SystemMessage(content=prompt2), HumanMessage(content=event)]) 

    res1 = asyncio.create_task(llm.agenerate(messages1))
    print("Prompt 1 task created")
    res2 = asyncio.create_task(llm.agenerate(messages2))
    print("Prompt 2 task created")
    res1_list = []
    res2_list = []
    
    res1 = await res1
    for item in res1.generations:
        res1_list.append(item[0].text)

    res2 = await res2
    for item in res2.generations:
        res2_list.append(item[0].text)
        

    with pd.ExcelWriter("result.xlsx") as writer:
        pd.DataFrame(res1_list).to_excel(writer, sheet_name='Prompt1 output', header=False, index= False)
        pd.DataFrame(res2_list).to_excel(writer, sheet_name='Prompt2 output', header= False, index= False)

if __name__=="__main__":
    asyncio.run(main())