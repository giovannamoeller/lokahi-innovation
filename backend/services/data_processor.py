import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from services.ai_service import HealthLLMAnalyzer
from config import settings
import s3fs

class HealthDataProcessor:
    def __init__(self):
        self.services_df = None
        self.members_df = None
        self.enrollment_df = None
        self.providers_df = None
        
        self.s3 = s3fs.S3FileSystem(
            key=settings.AWS_ACCESS_KEY_ID,
            secret=settings.AWS_SECRET_ACCESS_KEY,
            client_kwargs={'region_name': settings.AWS_REGION}
        )
        
    def load_data(self) -> None:
        """Load all necessary data files from S3."""
        print("Loading data from S3...")
        try:
            base_path = f's3://{settings.S3_BUCKET}'
            
            # Load Enrollment data
            print("Loading Enrollment data...")
            enrollment_files = self.s3.glob(f"{settings.S3_BUCKET}/Claims_Enrollment/*.parquet")
            self.enrollment_df = pd.concat([
                pd.read_parquet(f"s3://{f}", filesystem=self.s3) 
                for f in enrollment_files
            ])
            
            # List files in each directory to get exact paths
            print("Loading Services data...")
            services_files = self.s3.glob(f"{settings.S3_BUCKET}/Claims_Services/*.parquet")
            self.services_df = pd.concat([
                pd.read_parquet(f"s3://{f}", filesystem=self.s3) 
                for f in services_files
            ])
            
            print("Loading Members data...")
            members_files = self.s3.glob(f"{settings.S3_BUCKET}/Claims_Member/*.parquet")
            self.members_df = pd.concat([
                pd.read_parquet(f"s3://{f}", filesystem=self.s3) 
                for f in members_files
            ])
            
            print("Loading Providers data...")
            providers_files = self.s3.glob(f"{settings.S3_BUCKET}/Claims_Provider/*.parquet")
            self.providers_df = pd.concat([
                pd.read_parquet(f"s3://{f}", filesystem=self.s3) 
                for f in providers_files
            ])
            
            # Clean the data after loading
            self.clean_data()
            print("Data loaded and cleaned successfully.")
            
        except Exception as e:
            print(f"Error loading data from S3: {str(e)}")
            raise
        
    def clean_data(self) -> None:
        """Clean and prepare the data for analysis."""
        # Convert dates
        date_columns = ['FROM_DATE', 'TO_DATE', 'PAID_DATE', 'ADM_DATE', 'DIS_DATE']
        for col in date_columns:
            if col in self.services_df.columns:
                self.services_df[col] = pd.to_datetime(self.services_df[col])
        
        # Clean demographic data
        self.members_df['MEM_RACE'] = self.members_df['MEM_RACE'].map({
            '1': 'Asian',
            '2': 'Black',
            '3': 'Caucasian',
            '4': 'Other/Unknown'
        })
        
        self.members_df['MEM_ETHNICITY'] = self.members_df['MEM_ETHNICITY'].map({
            '1': 'Hispanic',
            '2': 'Not Hispanic',
            '3': 'Unknown'
        })
    
    def calculate_disease_prevalence(self) -> pd.DataFrame:
        """Calculate disease prevalence rates by geographic area."""
        # Merge services with members to get geographic info
        merged_df = self.services_df.merge(
            self.members_df[['PRIMARY_PERSON_KEY', 'MEM_MSA_NAME', 'MEM_STATE']],
            on='PRIMARY_PERSON_KEY',
            how='left'
        )
        
        # Group by geography and primary diagnosis
        prevalence = (
            merged_df.groupby(['MEM_MSA_NAME', 'DIAG_CCS_1_LABEL'])
            .agg({
                'PRIMARY_PERSON_KEY': 'nunique',  # unique patients
                'CLAIM_ID_KEY': 'count'  # number of claims
            })
            .reset_index()
        )
        
        # Calculate total patients per MSA for rates
        total_patients = (
            merged_df.groupby('MEM_MSA_NAME')
            ['PRIMARY_PERSON_KEY'].nunique()
            .reset_index()
        )
        
        # Merge and calculate rates
        prevalence = prevalence.merge(total_patients, on='MEM_MSA_NAME')
        prevalence['prevalence_rate'] = (
            prevalence['PRIMARY_PERSON_KEY_x'] / 
            prevalence['PRIMARY_PERSON_KEY_y'] * 100
        )
        
        return prevalence
    
    def analyze_cost_barriers(self) -> pd.DataFrame:
        """Analyze financial barriers to healthcare access."""
        # First merge services with members to get geographic info
        merged_df = self.services_df.merge(
            self.members_df[['PRIMARY_PERSON_KEY', 'MEM_MSA_NAME']],
            on='PRIMARY_PERSON_KEY',
            how='left'
        )
        
        # Calculate total patient cost
        merged_df['total_patient_cost'] = merged_df[['AMT_COPAY', 'AMT_DEDUCT', 'AMT_COINS']].sum(axis=1)
        
        # Now perform the groupby on the merged dataframe
        cost_analysis = merged_df.groupby(['MEM_MSA_NAME', 'SERVICE_SETTING']).agg({
            'AMT_COPAY': 'mean',
            'AMT_DEDUCT': 'mean',
            'AMT_COINS': 'mean',
            'AMT_PAID': 'mean',
            'PRIMARY_PERSON_KEY': 'nunique',
            'total_patient_cost': 'mean'
        }).reset_index()
        
        return cost_analysis
    
    def analyze_service_utilization(self) -> pd.DataFrame:
        """Analyze healthcare service utilization patterns."""
        # Merge with members data to get demographics and MSA
        merged_df = self.services_df.merge(
            self.members_df[['PRIMARY_PERSON_KEY', 'MEM_RACE', 'MEM_ETHNICITY', 
                           'MEM_GENDER', 'MEM_MSA_NAME']],
            on='PRIMARY_PERSON_KEY',
            how='left'
        )
        
        # Calculate utilization metrics
        utilization = merged_df.groupby(
            ['MEM_MSA_NAME', 'MEM_RACE', 'MEM_ETHNICITY', 'MEM_GENDER', 'SERVICE_SETTING']
        ).agg({
            'PRIMARY_PERSON_KEY': 'nunique',  # unique patients
            'CLAIM_ID_KEY': 'count',  # number of claims
            'AMT_PAID': 'sum',  # total costs
        }).reset_index()
        
        # Calculate average claims per patient
        utilization['claims_per_patient'] = (
            utilization['CLAIM_ID_KEY'] / 
            utilization['PRIMARY_PERSON_KEY']
        )
        
        return utilization
    
    def generate_health_risk_metrics(self) -> Dict[str, pd.DataFrame]:
        """Generate comprehensive health risk metrics for LLM analysis."""
        return {
            'disease_prevalence': self.calculate_disease_prevalence(),
            'cost_barriers': self.analyze_cost_barriers(),
            'service_utilization': self.analyze_service_utilization()
        }
        

class HealthAnalysisEngine:
    def __init__(self, metrics: Dict[str, pd.DataFrame]):
        self.metrics = metrics
        
    def analyze_disease_patterns(self, msa: str) -> List[Dict]:
        """Analyze disease patterns for a specific MSA."""
        df = self.metrics['disease_prevalence']
        msa_data = df[df['MEM_MSA_NAME'] == msa]
        
        # Sort by prevalence rate to get top conditions
        top_conditions = msa_data.nlargest(10, 'prevalence_rate')
        
        concerns = []
        for _, row in top_conditions.iterrows():
            concerns.append({
                'condition': row['DIAG_CCS_1_LABEL'],
                'prevalence_rate': float(row['prevalence_rate']),
                'affected_population': int(row['PRIMARY_PERSON_KEY_x']),
                'total_claims': int(row['CLAIM_ID_KEY'])
            })
        
        return concerns

    def analyze_cost_barriers(self, msa: str) -> Dict:
        """Analyze financial barriers to healthcare access."""
        df = self.metrics['cost_barriers']
        msa_data = df[df['MEM_MSA_NAME'] == msa]
        
        analysis = {
            'overall_metrics': {
                'avg_out_of_pocket': float(msa_data['total_patient_cost'].mean()),
                'total_patients': int(msa_data['PRIMARY_PERSON_KEY'].sum())
            },
            'service_setting_analysis': []
        }
        
        for setting in msa_data['SERVICE_SETTING'].unique():
            setting_data = msa_data[msa_data['SERVICE_SETTING'] == setting]
            analysis['service_setting_analysis'].append({
                'setting': setting,
                'avg_cost': float(setting_data['AMT_PAID'].mean()),
                'patient_count': int(setting_data['PRIMARY_PERSON_KEY'].sum())
            })
        
        return analysis

    def analyze_access_disparities(self, msa: str) -> Dict:
        """Analyze healthcare access disparities."""
        df = self.metrics['service_utilization']
        msa_data = df[df['MEM_MSA_NAME'] == msa]
        
        return {
            'racial_disparities': self._analyze_demographic_group(msa_data, 'MEM_RACE'),
            'ethnic_disparities': self._analyze_demographic_group(msa_data, 'MEM_ETHNICITY'),
            'gender_disparities': self._analyze_demographic_group(msa_data, 'MEM_GENDER')
        }
    
    def _analyze_demographic_group(self, df: pd.DataFrame, group_col: str) -> List[Dict]:
        """Analyze disparities for a demographic group."""
        group_stats = df.groupby(group_col).agg({
            'claims_per_patient': 'mean',
            'PRIMARY_PERSON_KEY': 'nunique',
            'AMT_PAID': 'mean'
        }).reset_index()
        
        return [
            {
                'group': row[group_col],
                'avg_claims': float(row['claims_per_patient']),
                'population': int(row['PRIMARY_PERSON_KEY']),
                'avg_cost': float(row['AMT_PAID'])
            }
            for _, row in group_stats.iterrows()
        ]

    def generate_community_risk_profile(self, msa: str) -> Dict:
        """Generate a comprehensive risk profile for a specific MSA."""
        try:
            disease_risks = self.analyze_disease_patterns(msa)
            cost_barriers = self.analyze_cost_barriers(msa)
            access_disparities = self.analyze_access_disparities(msa)
            
            return {
                'summary': {
                    'msa_name': msa,
                    'high_risk_conditions': {
                        'count': len(disease_risks),
                        'top_conditions': [
                            {
                                'condition': risk['condition'],
                                'prevalence': risk['prevalence_rate'],
                                'affected_population': risk['affected_population']
                            }
                            for risk in disease_risks[:5]
                        ]
                    },
                    'cost_analysis': cost_barriers['overall_metrics'],
                    'disparities': access_disparities
                },
                'detailed_analysis': {
                    'disease_risks': disease_risks,
                    'cost_barriers': cost_barriers,
                    'access_disparities': access_disparities
                }
            }
            
        except Exception as e:
            print(f"Error generating risk profile: {str(e)}")
            return None