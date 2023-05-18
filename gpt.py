from query_data2 import get_chain
from constants import *
import dotenv
from os import path
import argparse
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import PromptTemplate
from flask import Flask
from flask import request
import sys

dotenv.load_dotenv()
vectorstore = FAISS.load_local(path.join('embedded_store', STORE_NAME), OpenAIEmbeddings())
qa_chain = get_chain(vectorstore)

user_list = []
history_list = []
app = Flask(__name__)


def index_of(val, in_list):
  try:
    return in_list.index(val)
  except ValueError:
    return -1

def getAnswer(question,user):
  global user_list
  global history_list
  u = index_of(user,user_list)
  if u==-1:
    user_list.append(user)
    history_list.append([])
    u = len(user_list) - 1
  result = qa_chain({"question": question,"chat_history":history_list[u]})
  history_list[u].append((question, result["answer"]))
  if len(history_list[u])>3:
    history_list[u].pop(0)
  if len(user_list)>10:
    user_list.pop(0)
    history_list.pop(0)
  print(history_list)
  sys.stdout.flush()
  return result["answer"]


@app.route("/")
def answer():
  print(request.args.get('question'))
  sys.stdout.flush()
  print(request.args.get('user'))
  sys.stdout.flush()
  return  getAnswer(request.args.get('question'),request.args.get('user'))


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3030)
