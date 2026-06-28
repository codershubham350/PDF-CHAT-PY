from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain_classic.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import Runnable
from dotenv import load_dotenv
from threading import Thread
from queue import Queue

load_dotenv()

class StreamingHandler(BaseCallbackHandler):
    def __init__(self, queue):
        self.queue = queue
    def on_llm_new_token(self, token, **kwargs):
        self.queue.put(token)
    def on_llm_end(self, response, **kwargs):
        self.queue.put(None)

    def on_llm_error(self, error, **kwargs):
        self.queue.put(None)        

chat = ChatOpenAI(streaming=True)

prompt = ChatPromptTemplate.from_messages([
    ("human", "{content}")
])

base_chain = prompt | chat | StrOutputParser()

class StreamableChain:
    def __init__(self, chain):
        self.chain = chain

    def invoke(self, input, config=None, **kwargs):
        return self.chain.invoke(input, config=config, **kwargs)

    def stream(self, input, config=None):

        token_queue = Queue()
        handler = StreamingHandler(token_queue)

        def task():
            try:
                cfg = dict(config or {})
                cfg["callbacks"] = [handler] + cfg.get("callbacks", [])

                self.invoke(input, config=cfg)

            except Exception:
                token_queue.put(None)
                raise

        worker = Thread(target=task, daemon=True)
        worker.start()

        while True:
            token = token_queue.get()

            if token is None:
                break

            yield token

        worker.join()

        # for chunk in self.chain.stream(input, config=config):
        #     yield chunk

        # print("Finished stream")

class StreamingChain(StreamableChain, Runnable[dict, str]):
    pass

chain = StreamingChain(base_chain)
for chunk in chain.stream({"content": "tell me a good news"}):
   print(chunk, end="", flush=True)
