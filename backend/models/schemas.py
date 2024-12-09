from pydantic import BaseModel
from typing import List

class AnalysisRequest(BaseModel):
  msa_name: str
  include_llm_analysis: bool = True

class ComparisonRequest(BaseModel):
  base_msa: str
  comparison_msas: List[str]