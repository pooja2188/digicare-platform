# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Optional
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv
# from fastapi.responses import Response

# # Load your environment variables from the parent Backend directory if available
# load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'Backend', '.env'))
# api_key = os.getenv("GEMINI_API_KEY")

# app = FastAPI(title="DigiCare Doctor Multi-Agent SmartScan API", version="1.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# if api_key:
#     genai.configure(api_key=api_key)

# class SmartScanRequest(BaseModel):
#     fullName: str
#     age: int
#     gender: str
#     bloodGroup: str
#     dateOfBirth: Optional[str] = "N/A"
#     medicalHistory: Optional[str] = "None"
#     currentMedications: Optional[str] = "None"
#     familyMedicalHistory: Optional[str] = "None"
#     documents: Optional[List[str]] = []

# @app.post("/smartscan")
# async def generate_smart_scan(request: SmartScanRequest):
#     if not api_key:
#         raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured inside environment properties.")
        
#     try:
#         # Agent 1: Clinical Data Extractor & Metrics Validator
#         model = genai.GenerativeModel('gemini-2.5-flash')
        
#         agent_prompt = f"""
#         You are an elite clinical data verification AI agent. Analyze the following patient matrix data:
#         - Patient Name: {request.fullName}
#         - Age/Gender: {request.age} years old / {request.gender}
#         - Blood Group: {request.bloodGroup}
#         - Medical History: {request.medicalHistory}
#         - Current Medications: {request.currentMedications}
#         - Family Medical History: {request.familyMedicalHistory}
        
#         Compile a professional, highly detailed, text-based diagnostic summary report. Include a clear evaluation of chronic indicators, potential metric risks, and precise medical surveillance advice. 
#         """
        
#         response = model.generate_content(agent_prompt)
#         report_text = response.text

#         # Standard clean fallback plain-text layout delivery structure
#         return Response(
#             content=report_text.encode('utf-8'),
#             media_type="text/plain",
#             headers={"Content-Disposition": f"attachment; filename=SmartScan_{request.fullName.replace(' ', '_')}.txt"}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Agent grid system error: {str(e)}")

# @app.get("/")
# async def health():
#     return {"status": "healthy", "service": "SmartScan Multi-Agent System"}


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from fastapi.responses import Response

# Modern Google GenAI Client Stack
from google import genai
from google.genai import errors

# Load environment variables dynamically looking up path branches safely
env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Backend', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()  # Fallback to current runtime root path folder directory

# Initialize FastAPI app
app = FastAPI(title="DigiCare Doctor Multi-Agent SmartScan API", version="2.0.0")

# ✅ FIXED: Replaced forbidden wildcard origin array to pass allow_credentials processing blocks smoothly
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

# Initialize Modern Google GenAI Client Structure
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing or empty inside .env configuration profiles.")
client = genai.Client(api_key=api_key)

# Request Data Models
class SmartScanRequest(BaseModel):
    fullName: str
    age: int
    gender: str
    bloodGroup: str
    dateOfBirth: Optional[str] = "N/A"
    medicalHistory: Optional[str] = "None"
    currentMedications: Optional[str] = "None"
    familyMedicalHistory: Optional[str] = "None"
    documents: Optional[List[str]] = []

# ==========================================
# CORE CONTROLLER ROUTE ENDPOINT
# ==========================================

@app.post("/smartscan")
async def generate_smart_scan(request: SmartScanRequest):
    """
    Consumes unified structural clinical matrix inputs, generates diagnostic tracking insights via Gemini 2.5,
    and returns a professional download text file stream dynamically attached to the doctor user viewport panel.
    """
    try:
        # Agent 1 Prompt Formulation Layout
        agent_prompt = f"""
        You are an elite clinical data verification AI agent. Analyze the following patient matrix data:
        - Patient Name: {request.fullName}
        - Age/Gender: {request.age} years old / {request.gender}
        - Blood Group: {request.bloodGroup}
        - Medical History: {request.medicalHistory}
        - Current Medications: {request.currentMedications}
        - Family Medical History: {request.familyMedicalHistory}
        
        Compile a professional, highly detailed, text-based diagnostic summary report. Include a clear evaluation of chronic indicators, potential metric risks, and precise medical surveillance advice. 
        """
        
        # ✅ FIXED: Modern unified API content synthesis generation strategy sequence layout call
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=agent_prompt
        )
        report_text = response.text

        # Standard clean fallback plain-text layout delivery structure
        safe_filename = request.fullName.replace(' ', '_')
        return Response(
            content=report_text.encode('utf-8'),
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=SmartScan_{safe_filename}.txt",
                "Access-Control-Expose-Headers": "Content-Disposition"  # Crucial anchor allowing frontend JS to parse filename
            }
        )
    except errors.APIError as e:
        raise HTTPException(status_code=502, detail=f"Gemini API core routing failure: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent grid system engine execution breakdown: {str(e)}")

@app.get("/")
async def health():
    """Service verification gateway endpoint route"""
    return {"status": "healthy", "service": "SmartScan Multi-Agent System Engine Instance"}
