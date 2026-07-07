# from langchain_community.document_loaders import PyPDFLoader
# from langchain.schema import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# import os
# import uuid
# import requests
# import tempfile
# import json
# from dotenv import load_dotenv
# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")

# def store_chroma(docs, collection_name=None):

#     embeddings = GoogleGenerativeAIEmbeddings(
#         model="models/embedding-001",
#         google_api_key=api_key
#     )
#     session_id = collection_name or str(uuid.uuid4())
#     persist_directory = f"./chroma_db/{session_id}"

#     vector_db = Chroma.from_documents(
#         docs, 
#         embedding=embeddings, 
#         persist_directory=persist_directory
#     )
#     retrieved_docs = vector_db.get()
#     return session_id, vector_db

# def chunk_texts(docs):
#     splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
#     return splitter.split_documents(docs)


# def fetch_and_extract_pdf_text(cloudinary_url):
#     response = requests.get(cloudinary_url)
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#         tmp_file.write(response.content)
#         loader = PyPDFLoader(tmp_file.name)
#         docs = loader.load()
#     return docs

# def report_(pdf_link):
#     doc = []

#     pdf_doc = fetch_and_extract_pdf_text(pdf_link)
#     doc.extend(pdf_doc)
    
#     # Chunking
#     chunked_docs = chunk_texts(doc)

#     # store to chroma
#     session_id, _ = store_chroma(chunked_docs)


#     return session_id

from langchain_text_splitters import RecursiveCharacterTextSplitter  # ✅ FIXED: Modern standalone import
from pypdf import PdfReader                                          # ✅ FIXED: Native lightweight PDF reader
import chromadb                                                      # ✅ FIXED: Native ChromaDB client
from google import genai                                            # ✅ FIXED: Modern unified Google SDK
import os
import uuid
import requests
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ FIXED: Initialize the modern unified Gemini Client instance
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
client = genai.Client(api_key=api_key)

def get_gemini_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates vectors using the current production standard text-embedding-004 model"""
    # ✅ FIXED: Shifted from models/embedding-001 to text-embedding-004 using modern client syntax
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=texts
    )
    return [e.values for e in response.embeddings]

def store_chroma(chunks, collection_name=None):
    """Stores text chunks into a native local persistent Chroma DB"""
    session_id = collection_name or str(uuid.uuid4())
    persist_directory = f"./chroma_db/{session_id}"

    # ✅ FIXED: Direct Native PersistentClient configuration bypassing LangChain wrappers
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    collection = chroma_client.get_or_create_collection(name="medical_reports")

    # Isolate plain text data strings and metadatas for native database consumption
    text_contents = [doc.page_content for doc in chunks]
    metadatas = [doc.metadata for doc in chunks]
    ids = [str(uuid.uuid4()) for _ in chunks]

    # Generate high-fidelity embeddings via official Google GenAI SDK
    embeddings = get_gemini_embeddings(text_contents)

    # Insert elements into the collection safely
    collection.add(
        documents=text_contents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    return session_id, collection

def chunk_texts(docs):
    """Splits documents using structural recursive token splitting strategy"""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    return splitter.split_documents(docs)

def fetch_and_extract_pdf_text(cloudinary_url):
    """Downloads a PDF and builds structural schemas natively using pypdf"""
    from langchain.schema import Document  # Isolated structural container schema for the splitter
    
    response = requests.get(cloudinary_url, timeout=30)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch file from cloud storage: {response.status_code}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    docs = []
    try:
        # ✅ FIXED: Replaced legacy PyPDFLoader with standalone native pypdf reader
        reader = PdfReader(tmp_file_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                # Keeps structural metadata intact for downstream text splitters compatibility
                docs.append(Document(
                    page_content=text, 
                    metadata={"source": cloudinary_url, "page": page_num}
                ))
    finally:
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
            
    return docs

def report_(pdf_link):
    """Main pipeline execution workflow entry point"""
    doc = []

    # Download and extract PDF content layout structures
    pdf_doc = fetch_and_extract_pdf_text(pdf_link)
    doc.extend(pdf_doc)
    
    # Execute semantic text chunking
    chunked_docs = chunk_texts(doc)

    # Persist chunks inside ChromaDB vectors index
    session_id, _ = store_chroma(chunked_docs)

    return session_id
