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
            formatted_data = self.format_health_data(risk_profile)
            
            # More structured prompt
            messages = [
                SystemMessage(content="""You are a public health expert specialized in analyzing healthcare data. 
                You MUST ALWAYS provide analysis in the exact format requested, with all sections present and properly numbered.
                Each section must contain at least 3 bullet points.
                If data is missing for any section, provide general recommendations based on available information."""),
                
                HumanMessage(content=f"""
                Analyze the following health data for {msa_name}. 
                
                Health Data:
                {formatted_data}

                You MUST provide your analysis using EXACTLY these sections and format:

                1. Key Health Challenges:
                - Most prevalent conditions with exact percentages from the data
                - Population impact numbers
                - Concerning patterns and trends
                
                2. Healthcare Access Analysis:
                - Cost analysis using provided figures
                - Access disparities across demographics
                - Utilization patterns
                
                3. Recommendations:
                - Specific interventions for top health challenges
                - Solutions for identified disparities
                - Preventive care strategies
                
                4. Priority Areas:
                - Three specific, actionable items
                - Resource allocation suggestions
                - Areas needing immediate investigation

                Remember: All sections MUST be present and numbered exactly as shown above.
                Use bullet points (-) for each item within sections.
                Reference specific numbers and percentages from the data whenever possible.
                """)
            ]

            # Generate analysis
            response = self.chat_model.invoke(messages)
            
            # Validate and fix response if needed
            validated_response = self.validate_and_fix_response(response.content)
            
            return {
                "msa_name": msa_name,
                "analysis": validated_response,
                "source_data": risk_profile,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating LLM analysis: {str(e)}")
            return None

    def validate_and_fix_response(self, content: str) -> str:
        """Validate and fix LLM response to ensure all sections are present."""
        required_sections = [
            "1. Key Health Challenges:",
            "2. Healthcare Access Analysis:",
            "3. Recommendations:",
            "4. Priority Areas:"
        ]
        
        # Check if all sections are present
        fixed_content = content
        sections_present = all(section in content for section in required_sections)
        
        if not sections_present:
            # Try to fix missing sections
            sections = content.split('\n\n')
            fixed_sections = []
            
            for required in required_sections:
                section_found = False
                for section in sections:
                    if required.strip('1234. :') in section:
                        fixed_sections.append(section)
                        section_found = True
                        break
                
                if not section_found:
                    # Add default content for missing section
                    fixed_sections.append(self.get_default_section(required))
            
            fixed_content = '\n\n'.join(fixed_sections)
        
        return fixed_content

    def get_default_section(self, section_title: str) -> str:
        """Provide default content for missing sections."""
        defaults = {
            "1. Key Health Challenges:": """1. Key Health Challenges:
            - Review of most common conditions in the region
            - Analysis of affected population numbers
            - Identification of concerning health trends""",

                    "2. Healthcare Access Analysis:": """2. Healthcare Access Analysis:
            - Evaluation of current healthcare costs
            - Assessment of service utilization
            - Analysis of demographic access patterns""",

                    "3. Recommendations:": """3. Recommendations:
            - Implement targeted health screening programs
            - Develop community health education initiatives
            - Enhance healthcare access programs""",

                    "4. Priority Areas:": """4. Priority Areas:
            - Establish comprehensive health monitoring system
            - Develop targeted intervention programs
            - Implement regular health outcome assessments"""
        }
    
        return defaults.get(section_title, "")
    
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