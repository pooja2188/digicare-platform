# from fastapi import FastAPI, HTTPException, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, HttpUrl
# from typing import Optional
# import google.generativeai as genai
# from langchain_community.document_loaders import PyPDFLoader
# import requests
# import tempfile
# import os
# from google.api_core import exceptions
# from dotenv import load_dotenv
# import time

# # Load environment variables
# load_dotenv()

# # Initialize FastAPI app
# app = FastAPI(
#     title="Medical Report Analysis API",
#     description="API service for analyzing medical reports using Gemini AI",
#     version="1.0.0"
# )

# # ✅ FIXED: Replaced the forbidden wildcard ["*"] with explicit local Vite origin arrays.
# # This complies with the 'allow_credentials=True' browser constraint, clearing the CORS firewall blocker!
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://localhost:5174",
#         "http://127.0.0.1:5173",
#         "http://127.0.0.1:5174"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Configuration
# MAX_RETRIES = 3
# RETRY_DELAY = 2  # seconds

# # Get API key from environment
# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     raise ValueError("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")

# # Configure Gemini
# genai.configure(api_key=api_key)
# # model = genai.GenerativeModel('gemini-1.5-flash')
# model = genai.GenerativeModel('gemini-2.5-flash')

# # Models for request and response
# class PDFAnalysisRequest(BaseModel):
#     pdf_url: HttpUrl
    
# class AnalysisResponse(BaseModel):
#     status: str
#     analysis: Optional[str] = None
#     error: Optional[str] = None

# def analyze_medical_report(content):
#     """Uses Gemini AI to analyze medical report content"""
#     prompt = """You are an AI medical assistant that answers queries based on the given context and relevant medical knowledge. 
#     Here are some guidelines:
#     - Prioritize information from the provided documents but supplement with general medical knowledge when necessary.
#     - Ensure accuracy, citing sources from the document where applicable.
#     - Provide confidence scoring based on probability and reasoning.
#     - Be concise, informative, and avoid speculation.
#     YOU WILL ANALYSE ONLY MEDICAL DATA, if other CONTEXT is PASSED you will say "Provide Relevant Medical Data. Thanks"
#     Answer:
#     - **Response:** 
#     - **Reasoning:** (explain why this answer is correct and any potential limitations)
# """
    
#     for attempt in range(MAX_RETRIES):
#         try:
#             response = model.generate_content(f"{prompt}\n\n{content}")
#             return response.text
#         except exceptions.GoogleAPIError as e:
#             if attempt < MAX_RETRIES - 1:
#                 time.sleep(RETRY_DELAY)
#             else:
#                 return fallback_analysis(content)

# def fallback_analysis(content):
#     """Provides a fallback analysis when API has issues"""
#     word_count = len(content.split())
#     return f"""
#     Fallback Analysis:
#     1. Document Type: Text-based medical report
#     2. Word Count: Approximately {word_count} words
#     3. Content: The document appears to contain medical information, but detailed analysis is unavailable due to technical issues.
#     4. Recommendation: Please review the document manually or consult with a healthcare professional for accurate interpretation.
#     5. Note: This is a simplified analysis due to temporary unavailability of the AI service. For a comprehensive analysis, please try again later.
#     """

# def extract_text_from_pdf(pdf_url):
#     """Downloads a PDF from a URL and extracts its text content"""
#     # Download the PDF from the URL
#     response = requests.get(pdf_url, timeout=30)
#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail=f"Failed to download the PDF from URL: {pdf_url}")
    
#     # Save the PDF to a temporary file
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
#         tmp_file.write(response.content)
#         tmp_file_path = tmp_file.name
    
#     try:
#         # Use PyPDFLoader to load the PDF
#         loader = PyPDFLoader(tmp_file_path)
#         docs = loader.load()
        
#         # Extract text from documents
#         if docs and isinstance(docs, list):
#             text = "\n".join([doc.page_content for doc in docs])
#             return text
#         return None
#     finally:
#         # Clean up the temporary file
#         if os.path.exists(tmp_file_path):
#             os.unlink(tmp_file_path)

# @app.post("/analyze-pdf", response_model=AnalysisResponse)
# async def analyze_pdf(request: PDFAnalysisRequest):
#     """
#     Analyze a medical PDF report from a given URL
    
#     - **pdf_url**: Full URL to a PDF file containing medical data
    
#     Returns the analysis result or an error message
#     """
#     try:
#         # Extract text from the PDF
#         pdf_text = extract_text_from_pdf(request.pdf_url)
        
#         if not pdf_text:
#             return AnalysisResponse(
#                 status="error",
#                 error="Failed to extract text from PDF or PDF was empty"
#             )
            
#         # Perform analysis
#         analysis = analyze_medical_report(pdf_text)
        
#         return AnalysisResponse(
#             status="success",
#             analysis=analysis
#         )
#     except Exception as e:
#         return AnalysisResponse(
#             status="error",
#             error=f"Error processing request: {str(e)}"
#         )

# @app.get("/")
# async def health_check():
#     """Simple health check endpoint"""
#     return {"status": "healthy", "service": "Medical Report Analysis API"}


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
import os
import uuid
import time
import tempfile
import requests
from dotenv import load_dotenv

# Modern Google GenAI & Vector Database Stack (Zero LangChain Dependencies)
from google import genai
from google.genai import errors
from pypdf import PdfReader
import chromadb

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Digital Healthcare Report Management API",
    description="API service for parsing, indexing, and analyzing medical records via Gemini AI and ChromaDB",
    version="2.0.0"
)

# Configure CORS Firewall Constraints 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fallback configurations
MAX_RETRIES = 3
RETRY_DELAY = 2 

# Initialize Modern Google GenAI Client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing or empty.")
client = genai.Client(api_key=api_key)

# Pydantic Schemas for Requests and Responses
class PDFAnalysisRequest(BaseModel):
    pdf_url: HttpUrl
    
class AnalysisResponse(BaseModel):
    status: str
    session_id: Optional[str] = None
    analysis: Optional[str] = None
    error: Optional[str] = None

# Native Data Structure to replace LangChain's Document schema
class SimpleDocument(BaseModel):
    page_content: str
    metadata: dict

# ==========================================
# CORE WORKFLOW FUNCTIONS
# ==========================================

def get_gemini_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates high-fidelity vectors using the current standard gemini-embedding-2 model"""
    try:
        # ✅ FIXED: Upgraded to active production standard embedding model
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=texts
        )
        return [e.values for e in response.embeddings]
    except errors.APIError:
        # Emergency secondary fallback if your project tier restricts newer models
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts
        )
        return [e.values for e in response.embeddings]

def store_chroma(chunks: list[SimpleDocument], collection_name=None):
    """Stores split text chunks into a native local persistent Chroma DB"""
    session_id = collection_name or str(uuid.uuid4())
    persist_directory = f"./chroma_db/{session_id}"

    # Connect directly to native Chroma DB
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    collection = chroma_client.get_or_create_collection(name="medical_reports")

    # Format data fields for native database payload ingestion
    text_contents = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    ids = [str(uuid.uuid4()) for _ in chunks]

    # Generate Embeddings
    embeddings = get_gemini_embeddings(text_contents)

    # Ingest records
    collection.add(
        documents=text_contents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    return session_id

def chunk_texts(docs: list[SimpleDocument], chunk_size=1000, chunk_overlap=50) -> list[SimpleDocument]:
    """Pure Python character-based text splitter to eliminate LangChain completely"""
    chunked_docs = []
    
    for doc in docs:
        text = doc.page_content
        metadata = doc.metadata
        start = 0
        
        if len(text) <= chunk_size:
            chunked_docs.append(SimpleDocument(page_content=text, metadata=metadata))
            continue
            
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            chunked_docs.append(SimpleDocument(page_content=chunk_text, metadata=metadata))
            start += (chunk_size - chunk_overlap)
            
    return chunked_docs

def fetch_and_extract_pdf_text(pdf_url: str) -> list[SimpleDocument]:
    """Downloads a remote file and extracts text using lightweight standalone pypdf"""
    response = requests.get(pdf_url, timeout=30)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to fetch file from storage: {response.status_code}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name
    
    docs = []
    try:
        reader = PdfReader(tmp_file_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                docs.append(SimpleDocument(
                    page_content=text, 
                    metadata={"source": pdf_url, "page": page_num}
                ))
        return docs
    finally:
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

def analyze_medical_report(content: str) -> str:
    """Uses Gemini 2.5 Flash to analyze extracted report text with retry safety"""
    prompt = """You are an AI medical assistant that answers queries based on the given context and relevant medical knowledge. 
    Here are some guidelines:
    - Prioritize information from the provided documents but supplement with general medical knowledge when necessary.
    - Ensure accuracy, citing sources from the document where applicable.
    - Provide confidence scoring based on probability and reasoning.
    - Be concise, informative, and avoid speculation.
    YOU WILL ANALYSE ONLY MEDICAL DATA, if other CONTEXT is PASSED you will say "Provide Relevant Medical Data. Thanks"
    Answer:
    - **Response:** 
    - **Reasoning:** (explain why this answer is correct and any potential limitations)
"""
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{prompt}\n\n{content}"
            )
            return response.text
        except errors.APIError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return fallback_analysis(content)

def fallback_analysis(content: str) -> str:
    """Fallback text structural analysis if API rate-limiting or outages occur"""
    word_count = len(content.split())
    return f"""
    Fallback Analysis:
    1. Document Type: Text-based medical report
    2. Word Count: Approximately {word_count} words
    3. Content: The document contains text, but detailed analysis is unavailable due to temporary network issues.
    4. Recommendation: Please manually verify the charts or consult with a primary care practitioner.
    """

# ==========================================
# FASTAPI CONTROLLER ENDPOINTS
# ==========================================

@app.post("/analyze-pdf", response_model=AnalysisResponse)
async def analyze_pdf(request: PDFAnalysisRequest):
    """
    Downloads, chunks, embeds into ChromaDB, and extracts clinical insight from a PDF report.
    """
    try:
        url_str = str(request.pdf_url)
        
        # 1. Download and parse text content structure
        parsed_docs = fetch_and_extract_pdf_text(url_str)
        if not parsed_docs:
            return AnalysisResponse(status="error", error="Failed to extract readable text from the provided PDF file.")
            
        # 2. Convert to list text buffer for analysis
        full_extracted_text = "\n".join([d.page_content for d in parsed_docs])
        
        # 3. Perform text chunking operations 
        chunked_docs = chunk_texts(parsed_docs)
        
        # 4. Generate embeddings and persist chunks to local Vector DB
        session_id = store_chroma(chunked_docs)
        
        # 5. Execute Core Clinical LLM Insight Analysis
        analysis_result = analyze_medical_report(full_extracted_text)
        
        return AnalysisResponse(
            status="success",
            session_id=session_id,
            analysis=analysis_result
        )
    except Exception as e:
        return AnalysisResponse(
            status="error",
            error=f"Pipeline processing failed: {str(e)}"
        )

@app.get("/")
async def health_check():
    """Service status health check monitoring endpoint"""
    return {"status": "healthy", "service": "Integrated Medical Vector Storage & Analysis Engine"}
