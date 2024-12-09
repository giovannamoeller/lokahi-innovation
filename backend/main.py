# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from services.data_processor import HealthDataProcessor, HealthAnalysisEngine
from services.ai_service import HealthLLMAnalyzer
from models.schemas import AnalysisRequest, ComparisonRequest
from datetime import datetime
import os

processor = None
analysis_engine = None
llm_analyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize components only if not already initialized
    global processor, analysis_engine, llm_analyzer
    print("Initializing components...")
    processor = HealthDataProcessor()
    processor.load_data()
    metrics = processor.generate_health_risk_metrics()
    analysis_engine = HealthAnalysisEngine(metrics)
    llm_analyzer = HealthLLMAnalyzer()
    print("Initialization complete!")
    yield

app = FastAPI(lifespan=lifespan)

# Add your endpoints here...

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def test():
    return {
        "message": "Hello, World!"
    }

@app.get("/api/msas")
async def get_available_msas():
    """Get list of available MSAs for analysis."""
    try:
        msas = processor.members_df['MEM_MSA_NAME'].unique().tolist()
        return {
            "msas": msas,
            "count": len(msas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_msa(request: AnalysisRequest):
    """Generate health analysis for a specific MSA."""
    try:
        risk_profile = analysis_engine.generate_community_risk_profile(request.msa_name)
        
        if not risk_profile:
            raise HTTPException(status_code=404, detail="No data found for specified MSA")
        
        response = {
            "msa_name": request.msa_name,
            "timestamp": datetime.now().isoformat(),
            "health_metrics": risk_profile
        }
        
        if request.include_llm_analysis:
            llm_result = llm_analyzer.analyze_community_health(request.msa_name, risk_profile)
            if llm_result:
                response["llm_analysis"] = llm_result
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare")
async def compare_msas(request: ComparisonRequest):
    """Compare health metrics between multiple MSAs."""
    try:
        profiles = {}
        for msa in [request.base_msa] + request.comparison_msas:
            profile = analysis_engine.generate_community_risk_profile(msa)
            if profile:
                profiles[msa] = profile
        
        if not profiles:
            raise HTTPException(status_code=404, detail="No data found for specified MSAs")
        
        comparison = llm_analyzer.compare_regions(request.base_msa, profiles)
        
        return {
            "base_msa": request.base_msa,
            "compared_msas": request.comparison_msas,
            "timestamp": datetime.now().isoformat(),
            "profiles": profiles,
            "analysis": comparison
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
    
@app.get("/api/stats")
async def get_stats():
    """Get overall statistics."""
    try:
        return {
            "total_members": len(processor.members_df),
            "total_records": len(processor.services_df),
            "total_msas": len(processor.members_df['MEM_MSA_NAME'].unique()),
            "total_states": len(processor.members_df['MEM_STATE'].unique())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)