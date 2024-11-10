import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from transformers import LlamaTokenizer
from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain_chroma.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from fastapi.middleware.cors import CORSMiddleware
import autogen

embedding_function = HuggingFaceEmbeddings()
chroma_index = Chroma(embedding_function=embedding_function)

def parse_document(file_path):
    try:
        elements = partition_pdf(filename=file_path)
        return "\n".join([element.text for element in elements if element.text])
    except Exception as e:
        raise ValueError(f"Error parsing document: {str(e)}")

def index_documents(document_text, filename):
    chroma_index.add_texts([document_text], metadatas=[{"source": filename}])
