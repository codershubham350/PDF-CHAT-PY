from functools import partial
from .pinecone import build_retriever

retriever_map={
    "pinecone_2": partial(build_retriever, k=2),
    "pinecone_3": partial(build_retriever, k=3),
    "pinecone_4": partial(build_retriever, k=4)
}