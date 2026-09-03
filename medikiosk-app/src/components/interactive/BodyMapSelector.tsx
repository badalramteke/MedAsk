/**
 * MediKiosk — Interactive Body Map Component
 * Interactive anatomical model for symptom localization.
 * Patient taps on body regions or clicks directly to place a pinpoint pain marker.
 */

'use client';

import { useState } from 'react';
import { MapPin } from 'lucide-react';

interface BodyMapSelectorProps {
  selectedRegion: string | null;
  onSelectRegion: (region: string) => void;
}

const BODY_REGIONS = [
  { id: 'head', name: 'Head & Face', x: '50%', y: '14%' },
  { id: 'throat', name: 'Throat & Neck', x: '50%', y: '24%' },
  { id: 'chest', name: 'Chest / Heart', x: '50%', y: '35%' },
  { id: 'abdomen', name: 'Abdomen / Stomach', x: '50%', y: '48%' },
  { id: 'back', name: 'Upper & Lower Back', x: '78%', y: '42%' },
  { id: 'arms', name: 'Arms & Hands', x: '22%', y: '45%' },
  { id: 'pelvis', name: 'Pelvis / Groin', x: '50%', y: '60%' },
  { id: 'legs', name: 'Legs & Knees', x: '38%', y: '78%' },
  { id: 'feet', name: 'Feet & Ankles', x: '38%', y: '92%' },
];

export default function BodyMapSelector({
  selectedRegion,
  onSelectRegion,
}: BodyMapSelectorProps) {
  const [clickPoint, setClickPoint] = useState<{ x: number; y: number } | null>(null);

  const handleDiagramClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setClickPoint({ x, y });

    // Infer nearest anatomical region based on Y coordinates
    if (y < 20) onSelectRegion('head');
    else if (y < 28) onSelectRegion('throat');
    else if (y < 42) onSelectRegion('chest');
    else if (y < 55) onSelectRegion('abdomen');
    else if (y < 68) onSelectRegion('pelvis');
    else if (y < 85) onSelectRegion('legs');
    else onSelectRegion('feet');
  };

  return (
    <div
      id="kiosk-body-map-container"
      data-element="symptom-body-map"
      data-testid="symptom-body-map"
      className="flex flex-col md:flex-row items-center justify-center gap-8 w-full max-w-4xl mx-auto p-4"
    >
      {/* Visual Anatomical Diagram Box */}
      <div
        onClick={handleDiagramClick}
        className="relative w-72 h-96 bg-[#eceeee] rounded-3xl border-2 border-[#bdc9c5] shadow-inner flex items-center justify-center overflow-hidden cursor-crosshair group active:scale-99 transition-transform"
      >
        {/* Stylized Human Anatomy Silhouette SVG */}
        <svg
          viewBox="0 0 200 400"
          className="w-full h-full p-6 text-[#005f53]/25 group-hover:text-[#005f53]/35 transition-colors"
          fill="currentColor"
        >
          {/* Head */}
          <circle cx="100" cy="45" r="28" />
          {/* Neck */}
          <rect x="92" y="70" width="16" height="18" rx="4" />
          {/* Torso */}
          <path d="M 60 90 Q 100 85 140 90 L 132 210 Q 100 215 68 210 Z" />
          {/* Left Arm */}
          <path d="M 58 92 L 35 170 L 26 230" stroke="currentColor" strokeWidth="16" strokeLinecap="round" fill="none" />
          {/* Right Arm */}
          <path d="M 142 92 L 165 170 L 174 230" stroke="currentColor" strokeWidth="16" strokeLinecap="round" fill="none" />
          {/* Pelvis */}
          <path d="M 68 210 L 132 210 L 122 250 L 78 250 Z" />
          {/* Left Leg */}
          <path d="M 82 250 L 78 330 L 74 385" stroke="currentColor" strokeWidth="18" strokeLinecap="round" fill="none" />
          {/* Right Leg */}
          <path d="M 118 250 L 122 330 L 126 385" stroke="currentColor" strokeWidth="18" strokeLinecap="round" fill="none" />
        </svg>

        {/* Dynamic Click Point Marker */}
        {clickPoint && (
          <div
            className="absolute z-20 -translate-x-1/2 -translate-y-1/2 pointer-events-none"
            style={{ left: `${clickPoint.x}%`, top: `${clickPoint.y}%` }}
          >
            <div className="w-6 h-6 rounded-full bg-[#aa0a17] text-white flex items-center justify-center animate-ping" />
            <MapPin className="w-7 h-7 text-[#aa0a17] -mt-7 -ml-0.5 drop-shadow-md" />
          </div>
        )}

        <div className="absolute bottom-3 text-center w-full text-[11px] font-semibold text-[#3e4946] bg-white/75 backdrop-blur-xs py-1">
          Tap on body where pain occurs
        </div>
      </div>

      {/* Quick-Tap Region Buttons Grid */}
      <div className="flex-1 grid grid-cols-2 sm:grid-cols-3 gap-3 w-full max-w-lg">
        {BODY_REGIONS.map((reg) => {
          const isSelected = selectedRegion?.toLowerCase() === reg.id;
          return (
            <button
              key={reg.id}
              type="button"
              id={`body-region-${reg.id}`}
              data-element={`body-region-${reg.id}`}
              data-voice-action={`select-region-${reg.id}`}
              data-testid={`body-region-${reg.id}`}
              onClick={() => onSelectRegion(reg.id)}
              className={`h-16 px-4 rounded-2xl font-bold text-sm flex items-center justify-center text-center transition-all cursor-pointer border ${
                isSelected
                  ? 'bg-[#005f53] text-white border-transparent shadow-md scale-102 ring-2 ring-[#005f53]/30'
                  : 'bg-white hover:bg-[#eceeee] text-[#191c1d] border-[#bdc9c5]/60 hover:border-[#005f53]'
              }`}
            >
              {reg.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
