const Logo = ({ size = 40, spinning = false }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      className={`logo ${spinning ? 'logo-spinning' : ''}`}
      aria-label="Decarceration Lab Logo"
    >
      {/* Outer ring - represents breaking barriers */}
      <circle 
        cx="50" 
        cy="50" 
        r="45" 
        fill="none" 
        stroke="var(--accent)" 
        strokeWidth="2"
        strokeDasharray="8 4"
      />
      
      {/* Inner geometric shape - open hexagon representing freedom */}
      <path
        d="M50 15 L78 32.5 L78 67.5 L50 85 L22 67.5 L22 32.5 Z"
        fill="none"
        stroke="var(--foreground)"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
      
      {/* Break in the structure - symbolizing decarceration */}
      <path
        d="M50 15 L50 35"
        stroke="var(--accent)"
        strokeWidth="3"
        strokeLinecap="round"
      />
      
      {/* Central node */}
      <circle 
        cx="50" 
        cy="50" 
        r="8" 
        fill="var(--accent)"
      />
      
      {/* Radiating lines - knowledge spreading */}
      <g stroke="var(--muted-foreground)" strokeWidth="1.5" strokeLinecap="round">
        <line x1="50" y1="42" x2="50" y2="28" />
        <line x1="57" y1="46" x2="68" y2="38" />
        <line x1="57" y1="54" x2="68" y2="62" />
        <line x1="50" y1="58" x2="50" y2="72" />
        <line x1="43" y1="54" x2="32" y2="62" />
        <line x1="43" y1="46" x2="32" y2="38" />
      </g>
    </svg>
  )
}

export default Logo

