import { useId } from "react";

type LogoProps = {
  size?: number | string;
  className?: string;
};

export function Logo({ size = 36, className }: LogoProps) {
  const clip = useId();
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 48 48"
      role="img"
      aria-label="Bhumi logo"
    >
      <defs>
        <clipPath id={clip}>
          <rect width="48" height="48" rx="12" />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clip})`}>
        <rect width="48" height="48" fill="#2f3b2c" />
        <circle cx="31" cy="18" r="6.5" fill="#d08a5c" />
        <path d="M0 28 C9 23 17 23.5 24 26 C31 28.5 39 25 48 21.5 V48 H0 Z" fill="#3d5a40" />
        <g stroke="#f3ebe0" strokeWidth="1.7" strokeLinecap="round" opacity="0.9">
          <path d="M21.5 28 L3 48" />
          <path d="M23 28.4 L15 48" />
          <path d="M25 28.6 L28 48" />
          <path d="M26.5 28.4 L41 48" />
        </g>
        <path d="M0 28 C9 23 17 23.5 24 26 C31 28.5 39 25 48 21.5" fill="none" stroke="#b5673d" strokeWidth="1.6" />
      </g>
    </svg>
  );
}
