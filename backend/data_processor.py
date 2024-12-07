import pandas as pd

class DataProcessor:
  def __init__(self):
    self.services_df = pd.read_parquet('data/Claims_Services/')
    self.members_df = pd.read_parquet('data/Claims_Member/')
    self.providers_df = pd.read_parquet('data/Claims_Provider/')
    
  def calculate_provider_metrics(self):
    # Group by provider to calculate key metrics
    provider_metrics = self.services_df.groupby('ProviderID').agg({
      'AMT_PAID': ['mean', 'std'],
      'SV_STAT': lambda x: (x == 'P').mean(),
      'SERVICE_LINE': 'count'
    }).reset_index()
    
    provider_details = provider_metrics.merge(
      self.providers_df,
      on='PROV_KEY',
      how='left'
    )
    
    return provider_details
  
  