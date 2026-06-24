import './ChoiceChip.css';

interface ChoiceChipProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export function ChoiceChip({ label, onClick, disabled = false }: ChoiceChipProps) {
  return (
    <button
      className="choice-chip"
      onClick={onClick}
      disabled={disabled}
      type="button"
    >
      {label}
    </button>
  );
}
