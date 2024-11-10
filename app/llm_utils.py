from transformers import LlamaTokenizer
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain_chroma.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
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

tokenizer = LlamaTokenizer.from_pretrained('meta-llama/Llama-2-7b-chat-hf')
llm = LlamaCpp(
    model_path=r"",
    n_gpu_layers=40,
    n_batch=512,
    verbose=True,
    n_ctx=2048
)

template = """Document: {document}

Query: {query}

Answer: Let's work this out step-by-step to get the right answer."""
prompt = PromptTemplate(template=template, input_variables=["document", "query"])
llm_chain = LLMChain(llm=llm, prompt=prompt)

embedding_function = HuggingFaceEmbeddings()
chroma_index = Chroma(embedding_function=embedding_function)
UPLOAD_FOLDER = "./temp_files_2/"

def parse_document(file_path):
    try:
        elements = partition_pdf(filename=file_path)
        return "\n".join([element.text for element in elements if element.text])
    except Exception as e:
        raise ValueError(f"Error parsing document: {str(e)}")

def index_documents():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        document_text = parse_document(file_path)
        chroma_index.add_texts([document_text], metadatas=[{"source": filename}])

index_documents()
retriever = chroma_index.as_retriever(search_type='similarity')
retrieval_chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=retriever, return_source_documents=True)
