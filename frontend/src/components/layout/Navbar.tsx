// components/layout/Navbar.tsx
import Link from 'next/link';
import { HomeIcon, ChartBarIcon, ArrowRightLeftIcon } from 'lucide-react';

export function Navbar() {
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link 
              href="/" 
              className="flex items-center px-2 py-2 text-gray-900 hover:text-blue-600"
            >
              <HomeIcon className="h-5 w-5 mr-2" />
              <span className="font-semibold">FindCare AI</span>
            </Link>
          </div>
          
          <div className="flex space-x-4">
            <Link
              href="/analyze"
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-900 hover:text-blue-600"
            >
              <ChartBarIcon className="h-5 w-5 mr-2" />
              Analyze
            </Link>
            <Link
              href="/compare"
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-900 hover:text-blue-600"
            >
              <ArrowRightLeftIcon className="h-5 w-5 mr-2" />
              Compare
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}