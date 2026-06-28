from flask import current_app
from threading import Thread
from queue import Queue
from app.chat.callbacks.stream import StreamingHandler

class StreamableChain:
    def __init__(self, chain):
        self.chain = chain

    def __getattr__(self, name):
        return getattr(self.chain, name)

    def invoke(self, input, config=None, **kwargs):
        return self.chain.invoke(input, config=config, **kwargs)

    def stream(self, input, config=None):

        token_queue = Queue()
        handler = StreamingHandler(token_queue)

        def task(app_context):
            app_context.push()
            try:
                cfg = dict(config or {})
                cfg.setdefault("callbacks", [])
                cfg["callbacks"].insert(0, handler)

                self.invoke(input, config=cfg)

            except Exception:
                token_queue.put(None)
                raise

        worker = Thread(target=task, args=[current_app.app_context()], daemon=True)
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
