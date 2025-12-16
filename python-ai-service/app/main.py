from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

from app.agent.orchestrator import AgentOrchestrator
from app.llm.client import LLMClient

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Shopify Analytics AI Service",
    description="LLM-powered agent for Shopify analytics queries",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM client and orchestrator
llm_client = LLMClient()
orchestrator = AgentOrchestrator(llm_client)


# Request/Response models
class AnalyzeRequest(BaseModel):
    store_id: str = Field(..., description="Shopify store domain")
    question: str = Field(..., description="Natural language question")
    access_token: Optional[str] = Field(None, description="Shopify access token")
    use_mock: bool = Field(False, description="Use mock data for testing")


class AnalyzeResponse(BaseModel):
    answer: str = Field(..., description="Business-friendly answer")
    confidence: str = Field(..., description="Confidence level: low, medium, high")
    shopify_query: Optional[str] = Field(None, description="Generated ShopifyQL")
    reasoning: List[str] = Field(default_factory=list, description="Agent reasoning steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "python-ai-service",
        "llm_provider": os.getenv("LLM_PROVIDER", "openai")
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_question(request: AnalyzeRequest):
    """
    Analyze a natural language question about Shopify store data.
    
    The agent will:
    1. Classify the intent
    2. Plan required data
    3. Generate ShopifyQL
    4. Execute queries
    5. Process results
    6. Generate explanation
    """
    try:
        print(f"📥 Received question: {request.question}")
        print(f"🏪 Store: {request.store_id}")
        print(f"🧪 Mock mode: {request.use_mock}")

        # Run the agent orchestrator
        result = await orchestrator.process({
            "store_id": request.store_id,
            "question": request.question,
            "access_token": request.access_token,
            "use_mock": request.use_mock
        })

        return AnalyzeResponse(**result)

    except ValueError as e:
        # User input errors
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Internal errors
        print(f"❌ Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Shopify Analytics AI Service",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
