import 'lucide-react';
import * as React from 'react';

declare module 'lucide-react' {
  export interface LucideProps extends React.SVGAttributes<SVGSVGElement> {
    size?: string | number;
    color?: string;
    strokeWidth?: string | number;
    absoluteStrokeWidth?: boolean;
    className?: string;
    children?: React.ReactNode;
  }
}
