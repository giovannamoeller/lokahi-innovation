// app/page.tsx
'use client';

import { ArrowRightIcon, ChartBarIcon, ArrowRightLeftIcon } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { healthApi } from '../services/api';

interface Stats {
 total_members: number;
 total_records: number;
 total_msas: number;
 total_states: number;
}

export default function Home() {
 const [stats, setStats] = useState<Stats | null>(null);
 const [loading, setLoading] = useState(true);

 useEffect(() => {
   const fetchStats = async () => {
     try {
       const data = await healthApi.getStats();
       setStats(data);
     } catch (error) {
       console.error('Failed to fetch stats:', error);
     } finally {
       setLoading(false);
     }
   };

   fetchStats();
 }, []);

 return (
   <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
     <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
       {/* Hero Section */}
       <div className="py-12 sm:py-20">
         <div className="text-center">
           <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
             Healthcare Analytics
             <span className="text-blue-600"> Reimagined</span>
           </h1>
           <p className="mt-6 text-lg leading-8 text-gray-600 max-w-2xl mx-auto">
             Unlock powerful insights from healthcare data using advanced analytics and AI. 
             Make informed decisions for better community health outcomes.
           </p>
         </div>
       </div>

       {/* Features Grid */}
       <div className="grid grid-cols-1 md:grid-cols-2 gap-8 py-12">
         <Link 
           href="/analyze" 
           className="group relative bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 p-8 border border-gray-100"
         >
           <div className="flex items-center justify-between mb-4">
             <ChartBarIcon className="h-8 w-8 text-blue-600" />
             <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
           </div>
           <h2 className="text-2xl font-semibold mb-2">Regional Analysis</h2>
           <p className="text-gray-600">
             Deep dive into health metrics for specific regions. Get AI-powered insights and recommendations.
           </p>
         </Link>
         
         <Link 
           href="/compare" 
           className="group relative bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 p-8 border border-gray-100"
         >
           <div className="flex items-center justify-between mb-4">
             <ArrowRightLeftIcon className="h-8 w-8 text-blue-600" />
             <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
           </div>
           <h2 className="text-2xl font-semibold mb-2">Region Comparison</h2>
           <p className="text-gray-600">
             Compare health metrics across different regions. Identify patterns and disparities.
           </p>
         </Link>
       </div>

       {/* Stats Section */}
       <div className="py-12 border-t">
         <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
           <div className="text-center">
             <div className="text-3xl font-bold text-blue-600">
               {loading ? (
                 <div className="animate-pulse bg-blue-100 h-8 w-24 mx-auto rounded"></div>
               ) : (
                 `${(stats?.total_members || 0).toLocaleString()}+`
               )}
             </div>
             <div className="text-sm text-gray-600 mt-1">Members Analyzed</div>
           </div>
           <div className="text-center">
             <div className="text-3xl font-bold text-blue-600">
               {loading ? (
                 <div className="animate-pulse bg-blue-100 h-8 w-24 mx-auto rounded"></div>
               ) : (
                 `${((stats?.total_records || 0) / 1_000_000).toFixed(1)}M+`
               )}
             </div>
             <div className="text-sm text-gray-600 mt-1">Records Processed</div>
           </div>
           <div className="text-center">
             <div className="text-3xl font-bold text-blue-600">
               {loading ? (
                 <div className="animate-pulse bg-blue-100 h-8 w-24 mx-auto rounded"></div>
               ) : (
                 stats?.total_states || 0
               )}
             </div>
             <div className="text-sm text-gray-600 mt-1">States Covered</div>
           </div>
           <div className="text-center">
             <div className="text-3xl font-bold text-blue-600">
               {loading ? (
                 <div className="animate-pulse bg-blue-100 h-8 w-24 mx-auto rounded"></div>
               ) : (
                 stats?.total_msas || 0
               )}
             </div>
             <div className="text-sm text-gray-600 mt-1">MSA Regions</div>
           </div>
         </div>
       </div>
     </main>
   </div>
 );
}