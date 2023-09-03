import json
import dotenv

dotenv.load_dotenv()
from query_data import get_chain
from constants import *
from googletrans import Translator

from os import path
import argparse
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import PromptTemplate
from flask import Flask
from flask import request
import sys
from collections import deque


vectorstore = FAISS.load_local(
    path.join("embedded_store", STORE_NAME), OpenAIEmbeddings()
)
qa_chain = get_chain(vectorstore)
translator = Translator()

user_list = deque(maxlen=10)
history_list = deque(maxlen=10)
app = Flask(__name__)


class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def index_of(val, in_list):
    try:
        return in_list.index(val)
    except ValueError:
        return -1


def getAnswer(question, user, lang):
    global user_list
    global history_list
    u = index_of(user, user_list)
    if u == -1:
        user_list.append(user)
        history_list.append(deque(maxlen=3))
        u = len(user_list) - 1
    result = qa_chain({"question": question, "chat_history": history_list[u]})
    history_list[u].append((question, result["answer"]))
    """
  Using deque with maxlen. No need for pop now.
  if len(history_list[u])>3:
    history_list[u].pop(0)
  if len(user_list)>10:
    user_list.pop(0)
    history_list.pop(0)
  """
    print(history_list[u])
    sys.stdout.flush()
    print(result["answer"])
    sys.stdout.flush()
    response = Object()
    if lang != "en":
        print(lang)
        sys.stdout.flush()
        response.answer = translator.translate(
            result["answer"], src="en", dest=lang
        ).text
        print(response.answer)
        sys.stdout.flush()
    else:
        response.answer = result["answer"]
    response.source = result["source_documents"]
    print(response)
    sys.stdout.flush()
    jsonStr = response.toJSON()
    return jsonStr


@app.route("/")
def answer():
    print(request.args.get("question"))
    sys.stdout.flush()
    print(request.args.get("user"))
    sys.stdout.flush()
    # set default response to 'en'
    return getAnswer(
        request.args.get("question"),
        request.args.get("user"),
        request.args.get("lang", "en"),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3030)
