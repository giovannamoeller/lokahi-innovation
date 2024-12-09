'use client';

import { useEffect, useState } from 'react';
import { healthApi } from '../services/api';

export default function ComparisonDisplay({
  baseMsa,
  comparisonMsas
}: {
  baseMsa: string;
  comparisonMsas: string[];
}) {
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        setLoading(true);
        const data = await healthApi.compareRegions({
          base_msa: baseMsa,
          comparison_msas: comparisonMsas
        });
        setComparison(data);
        setError(null);
      } catch (err) {
        setError('Failed to load comparison');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (baseMsa && comparisonMsas.length > 0) {
      fetchComparison();
    }
  }, [baseMsa, comparisonMsas]);

  if (loading) {
    return <div className="p-4 text-center">Loading comparison...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  if (!comparison) {
    return null;
  }

  return (
    <div className="space-y-6 p-4">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Regional Comparison</h2>
        
        {/* Comparison Analysis */}
        <div className="prose max-w-none">
          {comparison.analysis.comparative_analysis.split('\n\n').map((section: string, index: number) => (
            <div key={index} className="mb-6">
              {section.split('\n').map((line: string, lineIndex: number) => (
                <p key={lineIndex} className="mb-2">
                  {line}
                </p>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}