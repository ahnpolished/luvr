import './ReaderBubble.css';

interface ReaderBubbleProps {
  text: string;
  isPast?: boolean;
  isUser?: boolean;
}

export function ReaderBubble({ text, isPast = false, isUser = false }: ReaderBubbleProps) {
  const classes = [
    'reader-bubble',
    isPast && 'reader-bubble--past',
    isUser && 'reader-bubble--user',
  ]
    .filter(Boolean)
    .join(' ');

  return <div className={classes}>{text}</div>;
}
