from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .data_processor import DataProcessor
from .ai_service import DoctorRecommendationService

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

data_processor = DataProcessor()
provider_metrics = data_processor.calculate_provider_metrics()
ai_service = DoctorRecommendationService(provider_metrics)

class SearchRequest(BaseModel):
  query: str
  
@app.post("/search-doctors")
async def search_doctors(request: SearchRequest):
  search_params = ai_service.analyze_query(request.query)
  
  filtered_providers = provider_metrics[
    (provider_metrics['PROV_TAXONOMY'].str.contains(search_params['specialty_needed'], na=False)) &
    (provider_metrics['AMT_PAID']['mean'] <= search_params.get('max_cost', float('inf')))
  ]
  
  ranked_results = ai_service.rank_providers(search_params, filtered_providers)

  return ranked_results