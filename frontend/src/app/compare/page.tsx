// app/compare/page.tsx
'use client';

import { useState } from 'react';
import RegionSelector from '@/components/RegionSelector';
import ComparisonDisplay from '@/components/ComparisonDisplay';

export default function ComparePage() {
  const [selectedMsas, setSelectedMsas] = useState<string[]>([]);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold">Region Comparison</h1>
        
        <RegionSelector
          onSelect={setSelectedMsas}
          multiple={true}
          selected={selectedMsas}
        />
        
        {selectedMsas.length > 1 && (
          <ComparisonDisplay 
            baseMsa={selectedMsas[0]}
            comparisonMsas={selectedMsas.slice(1)}
          />
        )}
      </div>
    </main>
  );
}