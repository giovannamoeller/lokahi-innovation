import { useEffect, useState } from 'react';
import { Activity, Heart, Users, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { healthApi } from '../services/api';

export default function AnalysisDisplay({ 
  msa, 
  includeLlm = true 
}: { 
  msa: string;
  includeLlm?: boolean;
}) {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        const data = await healthApi.analyzeRegion({ 
          msa_name: msa, 
          include_llm_analysis: includeLlm 
        });
        setAnalysis(data);
        setError(null);
      } catch (err) {
        setError('Failed to load analysis');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (msa) {
      fetchAnalysis();
    }
  }, [msa, includeLlm]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 rounded-lg flex items-center space-x-3 text-red-600">
        <AlertTriangle className="h-5 w-5" />
        <span>{error}</span>
      </div>
    );
  }

  if (!analysis) return null;

  const chartData = analysis.health_metrics.summary.high_risk_conditions.top_conditions
    .map((condition: any) => ({
      name: condition.condition.split(';')[0],
      value: condition.prevalence
    }));

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center space-x-3 text-blue-600 mb-4">
            <Users className="h-6 w-6" />
            <h3 className="text-lg font-semibold">Population</h3>
          </div>
          <div className="text-3xl font-bold">
            {analysis.health_metrics.summary.cost_analysis.total_patients.toLocaleString()}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center space-x-3 text-green-600 mb-4">
            <Heart className="h-6 w-6" />
            <h3 className="text-lg font-semibold">Health Conditions</h3>
          </div>
          <div className="text-3xl font-bold">
            {analysis.health_metrics.summary.high_risk_conditions.count}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center space-x-3 text-purple-600 mb-4">
            <Activity className="h-6 w-6" />
            <h3 className="text-lg font-semibold">Avg Cost</h3>
          </div>
          <div className="text-3xl font-bold">
            ${analysis.health_metrics.summary.cost_analysis.avg_out_of_pocket.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Prevalence Chart */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-xl font-semibold mb-6">Health Conditions Prevalence</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis label={{ value: 'Prevalence (%)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Conditions */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-xl font-semibold mb-6">Top Health Conditions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analysis.health_metrics.summary.high_risk_conditions.top_conditions.map((condition: any, index: number) => (
            <div key={index} className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900">{condition.condition}</h4>
              <div className="mt-2 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Prevalence</p>
                  <p className="text-lg font-semibold text-blue-600">{condition.prevalence.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Affected</p>
                  <p className="text-lg font-semibold text-blue-600">
                    {condition.affected_population.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Analysis */}
      {analysis.llm_analysis && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h3 className="text-xl font-semibold mb-6">AI Analysis</h3>
          <div className="prose max-w-none">
            {analysis.llm_analysis.analysis.split('\n\n').map((paragraph: string, index: number) => (
              <div key={index} className="mb-4">
                {paragraph.split('\n').map((line: string, lineIndex: number) => (
                  <p 
                    key={lineIndex} 
                    className={`${line.startsWith('-') ? 'ml-4 text-gray-600' : 'font-medium text-gray-900'}`}
                  >
                    {line}
                  </p>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}