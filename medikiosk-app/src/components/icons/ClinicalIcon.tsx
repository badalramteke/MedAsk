/**
 * MediKiosk — Clinical Icon System
 * Unifies healthicons-react and lucide-react to power an icon-driven kiosk experience.
 * Allows patients to recognize symptoms, body regions, and choices purely by visual iconography.
 */

'use client';

import React from 'react';
import {
  HeartOrgan,
  Fever,
  Coughing,
  Headache,
  Stomach,
  Lungs,
  Joints,
  Vomiting,
  Head,
  Spine,
  Arm,
  Leg,
  Foot,
  Bladder,
  Pain,
  Stethoscope as HealthStethoscope,
  HospitalSymbol,
  Medicines,
  PrescriptionDocument,
  BloodBag,
  TestTubes,
  MedicalRecords,
  Xray,
  ExerciseYoga,
  Person,
  Man,
  Woman,
  Transgender,
  Elderly,
  Happy,
  Sad,
  Crying,
  Ambulance,
  EmergencyPost,
  Microscope,
  Ok,
  NotOk,
  Yes,
  No,
  Positive,
  Negative,
  QrCode as HealthQrCode,
  CreditCard as HealthCreditCard,
  Mobile as HealthMobile,
  Doctor,
  Nurse,
  SecurityWorker,
  HealthDataSecurity,
  BloodDrop,
  Tooth,
  Ear,
  Eye,
  Nose,
  Mouth,
} from 'healthicons-react';

import {
  Activity,
  Zap,
  Clock,
  CircleDot,
  CheckCircle2,
  AlertTriangle,
  FileText,
  ShieldCheck,
  Languages,
  HelpCircle,
} from 'lucide-react';

/**
 * Visual Medical Icon for Chief Complaints
 */
export function SymptomIcon({
  id,
  className = 'w-10 h-10',
}: {
  id: string;
  className?: string;
}) {
  switch (id) {
    case 'chest_pain':
      return <HeartOrgan className={`${className} text-[#aa0a17]`} />;
    case 'fever':
      return <Fever className={`${className} text-[#e65100]`} />;
    case 'cough':
      return <Coughing className={`${className} text-[#0f7a6b]`} />;
    case 'headache':
      return <Headache className={`${className} text-[#5b21b6]`} />;
    case 'abdominal_pain':
      return <Stomach className={`${className} text-[#b45309]`} />;
    case 'shortness_of_breath':
      return <Lungs className={`${className} text-[#0284c7]`} />;
    case 'joint_pain':
      return <Joints className={`${className} text-[#0f7a6b]`} />;
    case 'vomiting':
      return <Vomiting className={`${className} text-[#15803d]`} />;
    default:
      return <Activity className={`${className} text-[#005f53]`} />;
  }
}

/**
 * Anatomical Body Region Icons for Localization
 */
export function BodyRegionIcon({
  region,
  className = 'w-6 h-6',
}: {
  region: string;
  className?: string;
}) {
  const norm = region.toLowerCase();
  switch (norm) {
    case 'head':
      return <Head className={className} />;
    case 'throat':
      return <Mouth className={className} />;
    case 'chest':
      return <Lungs className={className} />;
    case 'abdomen':
      return <Stomach className={className} />;
    case 'back':
      return <Spine className={className} />;
    case 'arms':
      return <Arm className={className} />;
    case 'pelvis':
      return <Bladder className={className} />;
    case 'legs':
      return <Leg className={className} />;
    case 'feet':
      return <Foot className={className} />;
    default:
      return <Activity className={className} />;
  }
}

/**
 * Medical Document Scanner Types
 */
export function DocTypeIcon({
  type,
  className = 'w-7 h-7',
}: {
  type: string;
  className?: string;
}) {
  switch (type) {
    case 'PRESCRIPTION':
      return <PrescriptionDocument className={className} />;
    case 'LAB_REPORT':
      return <BloodBag className={className} />;
    case 'DISCHARGE_SUMMARY':
      return <MedicalRecords className={className} />;
    case 'IMAGING':
      return <Xray className={className} />;
    default:
      return <FileText className={className} />;
  }
}

/**
 * Intelligent Choice Icon Resolver for Clinical SOCRATES / Multi-Choice questions
 */
export function QuestionChoiceIcon({
  code,
  text = '',
  className = 'w-6 h-6',
}: {
  code?: string;
  text?: string;
  className?: string;
}) {
  const query = `${code || ''} ${text || ''}`.toLowerCase();

  // Affirmative / Negative
  if (query.includes('yes') || query.includes('haan') || query.includes('true') || query.includes('present')) {
    return <Positive className={`${className} text-[#006e1c]`} />;
  }
  if (query.includes('no') || query.includes('nahi') || query.includes('false') || query.includes('absent') || query.includes('none')) {
    return <Negative className={`${className} text-[#aa0a17]`} />;
  }

  // Onset & Timing
  if (query.includes('sudden') || query.includes('acute') || query.includes('abrupt')) {
    return <Zap className={`${className} text-[#e65100]`} />;
  }
  if (query.includes('gradual') || query.includes('chronic') || query.includes('slow')) {
    return <Clock className={`${className} text-[#0f7a6b]`} />;
  }

  // Pain Character
  if (query.includes('sharp') || query.includes('stabbing') || query.includes('crushing')) {
    return <Activity className={`${className} text-[#aa0a17]`} />;
  }
  if (query.includes('dull') || query.includes('aching') || query.includes('mild')) {
    return <CircleDot className={`${className} text-[#0f7a6b]`} />;
  }
  if (query.includes('burning')) {
    return <Fever className={`${className} text-[#ce2b2c]`} />;
  }

  // Frequency
  if (query.includes('constant') || query.includes('continuous')) {
    return <Clock className={`${className} text-[#005f53]`} />;
  }
  if (query.includes('intermittent') || query.includes('comes and goes')) {
    return <Activity className={`${className} text-[#0f7a6b]`} />;
  }

  // Family members
  if (query.includes('father') || query.includes('pita') || query.includes('dad') || query.includes('baba')) {
    return <Man className={`${className} text-[#005f53]`} />;
  }
  if (query.includes('mother') || query.includes('mata') || query.includes('mom') || query.includes('aai')) {
    return <Woman className={`${className} text-[#005f53]`} />;
  }

  // Chronic conditions & Diagnoses
  if (query.includes('diabetes') || query.includes('sugar') || query.includes('insulin')) {
    return <BloodDrop className={`${className} text-[#aa0a17]`} />;
  }
  if (query.includes('hypertension') || query.includes('blood pressure') || query.includes('bp')) {
    return <HeartOrgan className={`${className} text-[#aa0a17]`} />;
  }
  if (query.includes('heart') || query.includes('cardiac') || query.includes('stent') || query.includes('bypass') || query.includes('attack')) {
    return <HeartOrgan className={`${className} text-[#aa0a17]`} />;
  }
  if (query.includes('asthma') || query.includes('respiratory') || query.includes('breath') || query.includes('dama')) {
    return <Lungs className={`${className} text-[#0f7a6b]`} />;
  }
  if (query.includes('cancer') || query.includes('tumor') || query.includes('oncology')) {
    return <Microscope className={`${className} text-[#5b21b6]`} />;
  }
  if (query.includes('joint') || query.includes('arthritis') || query.includes('bone') || query.includes('fracture') || query.includes('orthopedic')) {
    return <Joints className={`${className} text-[#0f7a6b]`} />;
  }

  // Substances
  if (query.includes('smoke') || query.includes('smoking') || query.includes('cigarette') || query.includes('bidi') || query.includes('tobacco') || query.includes('gutkha')) {
    return <Fever className={`${className} text-[#e65100]`} />;
  }
  if (query.includes('alcohol') || query.includes('drink') || query.includes('liquor') || query.includes('sharab')) {
    return <TestTubes className={`${className} text-[#b45309]`} />;
  }
  if (query.includes('paan') || query.includes('supari') || query.includes('betel')) {
    return <Tooth className={`${className} text-[#b45309]`} />;
  }

  // Surgical & Anatomy
  if (query.includes('abdominal') || query.includes('gallbladder') || query.includes('appendix') || query.includes('stomach')) {
    return <Stomach className={`${className} text-[#b45309]`} />;
  }
  if (query.includes('eye') || query.includes('cataract') || query.includes('vision')) {
    return <Eye className={`${className} text-[#0f7a6b]`} />;
  }
  if (query.includes('csection') || query.includes('delivery') || query.includes('pregnancy') || query.includes('pregnant') || query.includes('children')) {
    return <Woman className={`${className} text-[#005f53]`} />;
  }

  // Allergies
  if (query.includes('dust') || query.includes('pollen') || query.includes('sneez') || query.includes('cold')) {
    return <Nose className={`${className} text-[#0f7a6b]`} />;
  }
  if (query.includes('rash') || query.includes('skin') || query.includes('itch') || query.includes('hives')) {
    return <Arm className={`${className} text-[#e65100]`} />;
  }
  if (query.includes('food') || query.includes('egg') || query.includes('milk') || query.includes('nut')) {
    return <Stomach className={`${className} text-[#e65100]`} />;
  }

  // Fallback
  return <CircleDot className={`${className} text-[#005f53]/70`} />;
}

// Re-export core Health Icons for direct consumption in pages
export {
  HeartOrgan,
  Fever,
  Coughing,
  Headache,
  Stomach,
  Lungs,
  Joints,
  Vomiting,
  Head,
  Spine,
  Arm,
  Leg,
  Foot,
  Bladder,
  Pain,
  HealthStethoscope,
  HospitalSymbol,
  Medicines,
  PrescriptionDocument,
  BloodBag,
  TestTubes,
  MedicalRecords,
  Xray,
  ExerciseYoga,
  Person,
  Man,
  Woman,
  Transgender,
  Elderly,
  Happy,
  Sad,
  Crying,
  Ambulance,
  EmergencyPost,
  Microscope,
  Ok,
  NotOk,
  Yes,
  No,
  Positive,
  Negative,
  HealthQrCode,
  HealthCreditCard,
  HealthMobile,
  Doctor,
  Nurse,
  SecurityWorker,
  HealthDataSecurity,
  BloodDrop,
};
