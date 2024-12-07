from pydantic import BaseModel, Field
from typing import List
from langchain_groq import ChatGroq
from langchain.output_parsers import PydanticOutputParser
import os
from langchain.prompts.chat import (
  ChatPromptTemplate,
  HumanMessagePromptTemplate
)
from langchain_core.messages import HumanMessage

class UserHealthCarePreference(BaseModel):
  specialty_needed: str = Field(..., example="Cardiologist")
  max_cost: int = Field(..., example=500)
  location_preference: str = Field(..., example="New York, NY")
  other_preferences: List[str] = Field(..., example=["Accepts insurance", "Speaks Spanish"])

class DoctorRecommendationService:
  def __init__(self, provider_metrics):
    self.client = ChatGroq(model="gpt-3.5-turbo", api_key=os.environ['GROQ_API_KEY'])
    self.provider_metrics = provider_metrics
    self.parser = PydanticOutputParser(pydantic_object=UserHealthCarePreference)
  
  async def analyze_query(self, user_input) -> UserHealthCarePreference:
    human_prompt = HumanMessagePromptTemplate.from_template("{request}\n{format_instructions}")
    chat_prompt = ChatPromptTemplate.from_messages([human_prompt])
    
    request = chat_prompt.format_prompt(
      request=f"""
        You are a healthcare expert. Analyze this query and extract search parameters. Query: "{user_input}"
        """,
      format_instructions=self.parser.get_format_instructions()
    ).to_messages()
    
    results = self.client.invoke(request)
    results_values = self.parser.parse(results.content)
    
    return results_values
  
  async def rank_providers(self, search_params, provider_data):
    provider_descriptions = []
    for _, provider in provider_data.iterrows():
      desc = f"""
      Provider: {provider['PROV_KEY']}
      Specialty: {provider['PROV_TAXONOMY']}
      Success Rate: {provider['SV_STAT']*100:.1f}%
      Avg Cost: ${provider['AMT_PAID']['mean']:.2f}
      Location: {provider['PROV_CLINIC_ZIP']}
      """
      provider_descriptions.append(desc)

    prompt = f"""
    Given these provider details and user preferences:
    Search Parameters: {search_params}
        
    Providers:
    {provider_descriptions[:5]}  # Limiting to 5 for example
        
    Rank these providers and explain why they match. Return JSON with rankings and explanations.
    """
    
    response = self.client.invoke(prompt)
    return response.content
      
    