from datetime import datetime
from typing import Dict, List
import json
from langchain_groq import ChatGroq
import os
from langchain.schema import HumanMessage, SystemMessage
from config import settings

class HealthLLMAnalyzer:
    def __init__(self):
        """Initialize the LLM analyzer with ChatGroq."""
        self.chat_model = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=4096
        )
        
    def format_health_data(self, risk_profile: Dict) -> str:
        """Format the risk profile data for LLM consumption."""
        formatted_data = []
        
        # Format disease information
        formatted_data.append("Top Health Conditions:")
        for condition in risk_profile['summary']['high_risk_conditions']['top_conditions']:
            formatted_data.append(
                f"- {condition['condition']}: "
                f"{condition['prevalence']:.1f}% prevalence, "
                f"affecting {condition['affected_population']:,} people"
            )
        
        # Format cost information
        cost_analysis = risk_profile['summary']['cost_analysis']
        formatted_data.append("\nHealthcare Costs:")
        formatted_data.append(
            f"- Average out-of-pocket cost: ${cost_analysis['avg_out_of_pocket']:.2f}"
        )
        formatted_data.append(
            f"- Total patient population: {cost_analysis['total_patients']:,}"
        )
        
        # Format disparity information if available
        if 'disparities' in risk_profile['summary']:
            formatted_data.append("\nHealthcare Disparities:")
            disparities = risk_profile['summary']['disparities']
            for category, data in disparities.items():
                formatted_data.append(f"\n{category.replace('_', ' ').title()}:")
                for group in data:
                    formatted_data.append(
                        f"- {group['group']}: "
                        f"avg {group['avg_claims']:.1f} claims per patient, "
                        f"population: {group['population']:,}"
                    )
        
        return "\n".join(formatted_data)
    
    def analyze_community_health(self, msa_name: str, risk_profile: Dict) -> Dict:
        """Generate comprehensive health analysis using LLM."""
        try:
            # Format data for LLM
            formatted_data = self.format_health_data(risk_profile)
            
            # Prepare messages
            messages = [
                SystemMessage(content="You are a public health expert specialized in analyzing healthcare data and providing actionable insights."),
                HumanMessage(content=f"""
                Analyze the following health data for {msa_name} and provide key insights and recommendations:

                Health Data:
                {formatted_data}

                Please provide analysis in the following format:
                1. Key Health Challenges:
                   - Identify the most pressing health issues
                   - Analyze prevalence patterns
                   - Highlight concerning trends
                
                2. Healthcare Access Analysis:
                   - Evaluate cost barriers
                   - Identify access disparities
                   - Assess healthcare utilization patterns
                
                3. Recommendations:
                   - Suggest specific public health interventions
                   - Propose community-specific solutions
                   - Outline preventive care strategies

                4. Priority Areas:
                   - List top 3 immediate action items
                   - Suggest resource allocation priorities
                   - Identify areas needing further investigation
                """)
            ]
            
            # Generate analysis using ChatGroq
            response = self.chat_model.invoke(messages)
            
            return {
                "msa_name": msa_name,
                "analysis": response.content,
                "source_data": risk_profile,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating LLM analysis: {str(e)}")
            return None
    
    def compare_regions(self, msa_name: str, profiles: Dict[str, Dict]) -> Dict:
        """Generate comparative analysis between regions."""
        try:
            # Format comparative data
            comparative_data = []
            for region, profile in profiles.items():
                comparative_data.append(f"\nMetrics for {region}:")
                comparative_data.append(
                    self.format_health_data(profile)
                )
            
            # Prepare messages
            messages = [
                SystemMessage(content="You are a public health expert specialized in comparing regional health metrics and identifying opportunities for improvement."),
                HumanMessage(content=f"""
                Compare the health metrics of {msa_name} with similar regions:

                Comparative Data:
                {' '.join(comparative_data)}

                Provide insights on:
                1. Relative Performance
                2. Unique Challenges
                3. Best Practices to Consider
                4. Opportunities for Improvement
                """)
            ]
            
            # Generate analysis using ChatGroq
            response = self.chat_model.invoke(messages)
            
            return {
                "base_region": msa_name,
                "comparative_analysis": response.content,
                "regions_compared": list(profiles.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating comparative analysis: {str(e)}")
            return None