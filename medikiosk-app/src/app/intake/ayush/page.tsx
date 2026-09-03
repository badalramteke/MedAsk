/**
 * MediKiosk — Ayurvedic Dashavidha Pariksha Intake (/intake/ayush)
 * Screen 07: Traditional Ayurvedic diagnostic parameters:
 * Prakriti, Vikriti, Agni (digestive fire), and Koshtha (bowel habits).
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import OptionCard from '@/components/interactive/OptionCard';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { t } from '@/lib/i18n';
import { Flower2, Flame, Wind, Droplets } from 'lucide-react';

export default function AyushPage() {
  const router = useRouter();
  const { language } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { ayushAnswers, setAyushAnswer } = useIntakeStore();

  const [activePrakriti, setActivePrakriti] = useState<string>(
    ayushAnswers.prakriti || 'VATA_PITTA'
  );
  const [activeAgni, setActiveAgni] = useState<string>(
    ayushAnswers.agni || 'SAMAGNI'
  );

  const handleSelectPrakriti = (prakriti: string) => {
    setActivePrakriti(prakriti);
    setAyushAnswer('prakriti', prakriti);
  };

  const handleSelectAgni = (agni: string) => {
    setActiveAgni(agni);
    setAyushAnswer('agni', agni);
  };

  const handleProceed = () => {
    setCurrentScreen('document_scanner');
    router.push('/documents/scan');
  };

  const handleBack = () => {
    setCurrentScreen('chief_complaint');
    router.push('/intake/symptoms');
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader onBack={handleBack} />
      <StepProgressBar />

      <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-8 flex flex-col justify-between overflow-y-auto">
        <div className="text-center mb-4">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#005f53]/10 text-[#005f53] font-bold text-xs uppercase tracking-wider mb-2">
            <Flower2 className="w-4 h-4" />
            <span>AIIA Ayurvedic Dashavidha Pariksha</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-[#191c1d] tracking-tight">
            Ayurvedic Constitutional Assessment
          </h1>
          <p className="text-xs md:text-sm text-[#3e4946] mt-1">
            Assess Prakriti (constitution), Agni (digestion), and Koshtha.
          </p>
        </div>

        {/* Section 1: Prakriti / Dosha Evaluation */}
        <div className="my-auto space-y-6">
          <div>
            <h3 className="text-lg font-bold text-[#191c1d] mb-3">
              1. Predominant Prakriti (Body Constitution)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <OptionCard
                id="prakriti-vata"
                title="Vata (वात)"
                subtitle="Light, dry, fast-moving. Prone to dry skin, joint stiffness, anxiety."
                selected={activePrakriti === 'VATA'}
                onSelect={() => handleSelectPrakriti('VATA')}
                icon={<Wind className="w-6 h-6" />}
              />
              <OptionCard
                id="prakriti-pitta"
                title="Pitta (पित्त)"
                subtitle="Warm, sharp, intense. Prone to acidity, heat intolerance, inflammation."
                selected={activePrakriti === 'PITTA'}
                onSelect={() => handleSelectPrakriti('PITTA')}
                icon={<Flame className="w-6 h-6" />}
              />
              <OptionCard
                id="prakriti-kapha"
                title="Kapha (कफ)"
                subtitle="Heavy, stable, slow. Prone to sluggish digestion, mucus, weight gain."
                selected={activePrakriti === 'KAPHA'}
                onSelect={() => handleSelectPrakriti('KAPHA')}
                icon={<Droplets className="w-6 h-6" />}
              />
            </div>
          </div>

          {/* Section 2: Agni Status */}
          <div>
            <h3 className="text-lg font-bold text-[#191c1d] mb-3">
              2. Agni (Digestive Capacity)
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { id: 'SAMAGNI', title: 'Samagni', desc: 'Balanced & regular digestion' },
                { id: 'MANDAGNI', title: 'Mandagni', desc: 'Sluggish / heavy after meals' },
                { id: 'TIKSHNAGNI', title: 'Tikshnagni', desc: 'Excess heat / frequent burning' },
                { id: 'VISHAMAGNI', title: 'Vishamagni', desc: 'Irregular / bloating' },
              ].map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleSelectAgni(item.id)}
                  className={`p-4 rounded-2xl text-left border transition-all cursor-pointer ${
                    activeAgni === item.id
                      ? 'bg-[#005f53] text-white border-transparent shadow-md scale-102'
                      : 'bg-white hover:bg-[#eceeee] text-[#191c1d] border-[#bdc9c5]/60'
                  }`}
                >
                  <h4 className="font-bold text-sm md:text-base">{item.title}</h4>
                  <p
                    className={`text-xs mt-1 ${
                      activeAgni === item.id ? 'text-white/80' : 'text-[#3e4946]'
                    }`}
                  >
                    {item.desc}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>

      <KioskFooter
        onNext={handleProceed}
        onBack={handleBack}
        nextText="Proceed to Document Scan"
      />
    </div>
  );
}
