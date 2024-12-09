import React, { ReactNode } from 'react';
import { Brain, Users, Target, Flag, LucideIcon } from 'lucide-react';

interface AnalysisSectionProps {
  icon: LucideIcon;
  title: string;
  children: ReactNode;
}

const AnalysisSection = ({ icon: Icon, title, children }: AnalysisSectionProps) => (
  <div className="mb-8">
    <div className="flex items-center space-x-3 mb-4">
      <div className="bg-blue-50 p-2 rounded-lg">
        <Icon className="h-5 w-5 text-blue-600" />
      </div>
      <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
    </div>
    <div className="space-y-4 ml-10">
      {children}
    </div>
  </div>
);

interface BulletPointProps {
  children: ReactNode;
}

const BulletPoint = ({ children }: BulletPointProps) => (
  <div className="flex items-start space-x-3">
    <div className="mt-1.5 h-1.5 w-1.5 rounded-full bg-blue-600 flex-shrink-0" />
    <p className="text-gray-600">{children}</p>
  </div>
);

interface NumberedItemProps {
  number: string | number;
  children: ReactNode;
}

const NumberedItem = ({ number, children }: NumberedItemProps) => (
  <div className="flex items-start space-x-3">
    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
      <span className="text-sm font-medium text-blue-600">{number}</span>
    </div>
    <p className="text-gray-600">{children}</p>
  </div>
);

interface AIAnalysisProps {
  analysis: string;
}

export default function AIAnalysis({ analysis }: AIAnalysisProps) {
  // Parse the analysis text into sections
  const sections = analysis.split(/\d+\.\s/).filter(Boolean);

  // Helper function to get section title
  const getSectionTitle = (section: string): string => {
    return section.split(':')[0].trim();
  };

  // Helper function to get section content
  const getSectionContent = (section: string): string[] => {
    const content = section.split(':').slice(1).join(':').trim();
    return content.split('\n').filter(line => line.trim());
  };

  // Map sections to appropriate icons
  const sectionIcons: { [key: string]: LucideIcon } = {
    'Key Health Challenges': Brain,
    'Healthcare Access Analysis': Users,
    'Recommendations': Target,
    'Priority Areas': Flag,
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-8 space-y-8">
      {sections.map((section, index) => {
        const title = getSectionTitle(section);
        const content = getSectionContent(section);
        const icon = sectionIcons[title] || Brain;

        return (
          <AnalysisSection key={index} icon={icon} title={title}>
            {content.map((line, lineIndex) => {
              console.log(line)
              if (line.match(/^\d+\.\s/)) {
                // Numbered items (primarily in Priority Areas)
                const [number, ...textParts] = line.split('.');
                const text = textParts.join('.').trim();
                return <NumberedItem key={lineIndex} number={number}>{text}</NumberedItem>;
              } else if (line.startsWith('-')) {
                // Bullet points
                return <BulletPoint key={lineIndex}>{line.substring(1).trim()}</BulletPoint>;
              } else {
                // Regular text
                return (
                  <p key={lineIndex} className="text-gray-600">
                    {line.trim()}
                  </p>
                );
              }
            })}
          </AnalysisSection>
        );
      })}
    </div>
  );
}