import React, { useState, useEffect } from 'react';
import { ArrowRight } from 'lucide-react';
import FileTypeIcon from './FileTypeIcon';
import { ConversionService } from '../services/ConversionService';

type ConversionPath = {
  source: string;
  target: string;
};

type ConversionCategory = 'document' | 'image' | 'audio' | 'video' | 'special';

interface ConversionGroup {
  category: ConversionCategory;
  title: string;
  conversions: ConversionPath[];
}

const ConversionDashboard: React.FC = () => {
  const [conversionGroups, setConversionGroups] = useState<ConversionGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchConversions = async () => {
      setIsLoading(true);
      try {
        // Create an instance of ConversionService
        const conversionService = new ConversionService();
        
        // Get supported conversions
        const supportedConversions = conversionService.getSupportedConversions();
        
        // Transform the data from Record<string, string[]> to ConversionPath[]
        const conversionPaths: ConversionPath[] = [];
        Object.entries(supportedConversions).forEach(([source, targets]) => {
          targets.forEach(target => {
            conversionPaths.push({ source, target });
          });
        });
        
        // Organize conversions into groups
        const documentConversions: ConversionPath[] = [];
        const imageConversions: ConversionPath[] = [];
        const audioConversions: ConversionPath[] = [];
        const videoConversions: ConversionPath[] = [];
        const specialConversions: ConversionPath[] = [];
        
        conversionPaths.forEach((conversion: ConversionPath) => {
          const source = conversion.source.toLowerCase();
          const target = conversion.target.toLowerCase();
          
          if (['pdf', 'docx', 'doc'].includes(source) || ['pdf', 'docx', 'doc'].includes(target)) {
            documentConversions.push(conversion);
          } else if (['jpg', 'jpeg', 'png', 'gif'].includes(source) || ['jpg', 'jpeg', 'png', 'gif'].includes(target)) {
            imageConversions.push(conversion);
          } else if (['mp3', 'wav'].includes(source) || ['mp3', 'wav'].includes(target)) {
            audioConversions.push(conversion);
          } else if (['mp4', 'mov'].includes(source) || ['mp4', 'mov'].includes(target)) {
            videoConversions.push(conversion);
          } else {
            specialConversions.push(conversion);
          }
        });
        
        const groups: ConversionGroup[] = [];
        
        if (documentConversions.length > 0) {
          groups.push({
            category: 'document',
            title: 'Document Conversions',
            conversions: documentConversions
          });
        }
        
        if (imageConversions.length > 0) {
          groups.push({
            category: 'image',
            title: 'Image Conversions',
            conversions: imageConversions
          });
        }
        
        if (audioConversions.length > 0) {
          groups.push({
            category: 'audio',
            title: 'Audio Conversions',
            conversions: audioConversions
          });
        }
        
        if (videoConversions.length > 0) {
          groups.push({
            category: 'video',
            title: 'Video Conversions',
            conversions: videoConversions
          });
        }
        
        if (specialConversions.length > 0) {
          groups.push({
            category: 'special',
            title: 'Other Conversions',
            conversions: specialConversions
          });
        }
        
        setConversionGroups(groups);
        
        // Clean up ConversionService when done
        conversionService.dispose();
      } catch (error) {
        console.error('Failed to fetch supported conversions:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchConversions();
  }, []);

  if (isLoading) {
    return <div className="p-4 text-center text-gray-500">Loading supported conversions...</div>;
  }

  return (
    <div className="w-full p-6 bg-gray-50 rounded-lg">
      <h2 className="text-2xl font-semibold mb-6 text-center text-gray-800">Supported Conversions</h2>
      
      {conversionGroups.length === 0 ? (
        <div className="text-center text-gray-500">No supported conversions found.</div>
      ) : (
        <div className="space-y-8">
          {conversionGroups.map((group, groupIndex) => (
            <div key={groupIndex} className="mb-8">
              <h3 className="text-lg font-medium mb-4 text-gray-700 border-b pb-2">{group.title}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {group.conversions.map((conversion, index) => (
                  <div 
                    key={index} 
                    className="flex items-center justify-center bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow"
                  >
                    <div className="flex flex-col items-center">
                      <FileTypeIcon 
                        fileType={conversion.source} 
                        size="lg" 
                        className="mb-2" 
                      />
                      <span className="text-xs text-gray-500">Source</span>
                    </div>
                    
                    <ArrowRight className="mx-4 text-gray-400" size={24} />
                    
                    <div className="flex flex-col items-center">
                      <FileTypeIcon 
                        fileType={conversion.target} 
                        size="lg" 
                        className="mb-2" 
                      />
                      <span className="text-xs text-gray-500">Target</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConversionDashboard; 