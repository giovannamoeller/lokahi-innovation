import { useState, useEffect } from 'react';
import { Search, MapPin } from 'lucide-react';
import { healthApi } from '../services/api';

export default function RegionSelector({ 
  onSelect, 
  multiple = false,
  selected = [] 
}: { 
  onSelect: (msas: string[]) => void;
  multiple?: boolean;
  selected?: string[];
}) {
  const [msas, setMsas] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const loadMSAs = async () => {
      try {
        const data = await healthApi.getMSAs();
        setMsas(data.msas);
      } catch (error) {
        console.error('Failed to load MSAs:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMSAs();
  }, []);

  const filteredMSAs = msas.filter(msa => 
    msa.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelectionChange = (msa: string) => {
    if (multiple) {
      const newSelection = selected.includes(msa)
        ? selected.filter(m => m !== msa)
        : [...selected, msa];
      onSelect(newSelection);
    } else {
      onSelect([msa]);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="Search regions..."
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredMSAs.map((msa) => (
          <button
            key={msa}
            onClick={() => handleSelectionChange(msa)}
            className={`relative group p-4 rounded-lg text-left transition-all duration-200 ${
              selected.includes(msa)
                ? 'bg-blue-50 border-blue-500 border-2 shadow-md'
                : 'bg-white border border-gray-200 hover:border-blue-300 hover:shadow-md'
            }`}
          >
            <div className="flex items-start space-x-3">
              <MapPin className={`h-5 w-5 mt-0.5 ${
                selected.includes(msa) ? 'text-blue-500' : 'text-gray-400 group-hover:text-blue-500'
              }`} />
              <span className={`font-medium ${
                selected.includes(msa) ? 'text-blue-700' : 'text-gray-900'
              }`}>
                {msa}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}