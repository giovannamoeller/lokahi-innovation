// app/analyze/page.tsx
'use client';

import { useState } from 'react';
import RegionSelector from '@/components/RegionSelector';
import AnalysisDisplay from '@/components/AnalysisDisplay';

export default function AnalyzePage() {
  const [selectedMsa, setSelectedMsa] = useState<string[]>([]);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold">Region Analysis</h1>
        
        <RegionSelector
          onSelect={setSelectedMsa}
          selected={selectedMsa}
        />
        
        {selectedMsa.length > 0 && (
          <AnalysisDisplay 
            msa={selectedMsa[0]} 
            includeLlm={true}
          />
        )}
      </div>
    </main>
  );
}