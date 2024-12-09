import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass

@dataclass
class DisparityMetric:
    """Class for storing disparity analysis results."""
    metric_name: str
    demographic_group: str
    value: float
    comparison_value: float
    percent_difference: float
    statistical_significance: float
    severity: str  # 'High', 'Medium', 'Low'

class HealthcareAnalyzer:
    def __init__(self, pipeline_data: Dict[str, pd.DataFrame]):
        """
        Initialize the healthcare analyzer with processed data from the pipeline.
        
        Args:
            pipeline_data: Dictionary containing preprocessed dataframes
        """
        self.data = pipeline_data
        self.logger = logging.getLogger('HealthcareAnalyzer')
        self.disparity_metrics: List[DisparityMetric] = []
        
    def analyze_cost_disparities(self) -> List[DisparityMetric]:
        """Analyze cost disparities across demographic groups."""
        df = self.data['services']
        members = self.data['members']
        
        # Merge with member demographics
        combined = pd.merge(
            df,
            members[['PRIMARY_PERSON_KEY', 'MEM_RACE', 'MEM_ETHNICITY', 'MEM_ZIP3']],
            on='PRIMARY_PERSON_KEY',
            how='left'
        )
        
        metrics = []
        
        # Analyze by race
        for race in combined['MEM_RACE'].unique():
            race_group = combined[combined['MEM_RACE'] == race]
            others = combined[combined['MEM_RACE'] != race]
            
            # Calculate average costs
            race_costs = race_group['TOTAL_OOP_COST'].mean()
            other_costs = others['TOTAL_OOP_COST'].mean()
            
            # Perform statistical test
            t_stat, p_value = stats.ttest_ind(
                race_group['TOTAL_OOP_COST'].dropna(),
                others['TOTAL_OOP_COST'].dropna()
            )
            
            # Calculate percent difference
            pct_diff = ((race_costs - other_costs) / other_costs) * 100
            
            # Determine severity
            severity = self._calculate_severity(pct_diff, p_value)
            
            metrics.append(DisparityMetric(
                metric_name='Average Out-of-Pocket Cost',
                demographic_group=race,
                value=race_costs,
                comparison_value=other_costs,
                percent_difference=pct_diff,
                statistical_significance=p_value,
                severity=severity
            ))
            
        return metrics
    
    def analyze_access_patterns(self) -> List[DisparityMetric]:
        """Analyze healthcare access patterns and barriers."""
        df = self.data['services']
        members = self.data['members']
        
        # Calculate key access metrics
        access_metrics = []
        
        # Analyze in-network utilization
        network_utilization = self._analyze_network_utilization(df, members)
        access_metrics.extend(network_utilization)
        
        # Analyze service delays
        service_delays = self._analyze_service_delays(df, members)
        access_metrics.extend(service_delays)
        
        # Analyze provider availability
        provider_availability = self._analyze_provider_availability(df, members)
        access_metrics.extend(provider_availability)
        
        return access_metrics
    
    def analyze_treatment_patterns(self) -> Dict[str, pd.DataFrame]:
        """Analyze patterns in treatment and procedures."""
        df = self.data['services']
        members = self.data['members']
        
        # Merge datasets
        combined = pd.merge(
            df,
            members[['PRIMARY_PERSON_KEY', 'MEM_RACE', 'MEM_ETHNICITY']],
            on='PRIMARY_PERSON_KEY',
            how='left'
        )
        
        # Analyze procedure frequencies
        procedure_patterns = combined.groupby(['MEM_RACE', 'CPT_CCS_LABEL']).agg({
            'PROC_CODE': 'count',
            'AMT_PAID': 'mean'
        }).reset_index()
        
        # Analyze diagnosis patterns
        diagnosis_patterns = combined.groupby(['MEM_RACE', 'DIAG_CCS_1_LABEL']).agg({
            'PRIMARY_PERSON_KEY': 'nunique',
            'AMT_PAID': 'mean'
        }).reset_index()
        
        return {
            'procedure_patterns': procedure_patterns,
            'diagnosis_patterns': diagnosis_patterns
        }
    
    def identify_critical_disparities(self) -> List[Dict]:
        """Identify the most critical disparities for intervention."""
        all_metrics = []
        all_metrics.extend(self.analyze_cost_disparities())
        all_metrics.extend(self.analyze_access_patterns())
        
        # Filter for high-severity disparities
        critical_disparities = [
            {
                'metric': metric.metric_name,
                'group': metric.demographic_group,
                'difference': metric.percent_difference,
                'significance': metric.statistical_significance,
                'severity': metric.severity
            }
            for metric in all_metrics
            if metric.severity == 'High' and metric.statistical_significance < 0.05
        ]
        
        return sorted(
            critical_disparities,
            key=lambda x: abs(x['difference']),
            reverse=True
        )
    
    def generate_intervention_recommendations(self) -> List[Dict]:
        """Generate recommendations for addressing identified disparities."""
        critical_disparities = self.identify_critical_disparities()
        recommendations = []
        
        for disparity in critical_disparities:
            recommendation = {
                'target_group': disparity['group'],
                'metric': disparity['metric'],
                'severity': disparity['severity'],
                'suggested_interventions': self._generate_interventions(disparity)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_severity(self, percent_difference: float, p_value: float) -> str:
        """Calculate severity of disparity based on difference and statistical significance."""
        if abs(percent_difference) > 30 and p_value < 0.01:
            return 'High'
        elif abs(percent_difference) > 15 and p_value < 0.05:
            return 'Medium'
        else:
            return 'Low'
    
    def _analyze_network_utilization(self, df: pd.DataFrame, members: pd.DataFrame) -> List[DisparityMetric]:
        """Analyze in-network vs out-of-network utilization patterns."""
        # Implementation details...
        return []
    
    def _analyze_service_delays(self, df: pd.DataFrame, members: pd.DataFrame) -> List[DisparityMetric]:
        """Analyze delays between service request and delivery."""
        # Implementation details...
        return []
    
    def _analyze_provider_availability(self, df: pd.DataFrame, members: pd.DataFrame) -> List[DisparityMetric]:
        """Analyze provider availability across demographic groups."""
        # Implementation details...
        return []
    
    def _generate_interventions(self, disparity: Dict) -> List[str]:
        """Generate specific intervention recommendations based on disparity type."""
        interventions = {
            'Average Out-of-Pocket Cost': [
                'Implement targeted financial assistance programs',
                'Review and adjust cost-sharing policies',
                'Develop payment plan options'
            ],
            'Provider Access': [
                'Expand provider network in underserved areas',
                'Implement telehealth solutions',
                'Create mobile health clinics'
            ],
            'Treatment Patterns': [
                'Develop cultural competency training',
                'Review treatment protocols for bias',
                'Implement decision support tools'
            ]
        }
        
        return interventions.get(disparity['metric'], ['Review and develop targeted interventions'])