import { useCallback } from 'react';
import { EmberField } from '../../components/tarot';
import { useTarot } from '../../state/tarot-context';
import './ReflectScreen.css';

export function ReflectScreen() {
  const { messages } = useTarot();

  const synthMessage = messages.find((m) => m.context === 'synth');
  const takeawayMessage = messages.find((m) => m.context === 'takeaway');

  const synthesis = synthMessage?.text ?? 'The cards have spoken in their own way. Let the reading settle.';
  const takeaway = takeawayMessage?.text ?? 'Trust what you already know.';

  const handleNewReading = useCallback(() => {
    window.location.reload();
  }, []);

  const handleSave = useCallback(() => {
    alert('Save this reading by taking a screenshot! \u{1F4F8}');
  }, []);

  return (
    <div className="reflect">
      <EmberField />

      <div className="reflect__header">
        <p className="reflect__header-text">The cards have spoken</p>
      </div>

      <p className="reflect__narrative">{synthesis}</p>

      <div className="reflect__takeaway">
        <span className="reflect__takeaway-label">The takeaway</span>
        <p className="reflect__takeaway-text">{takeaway}</p>
      </div>

      <div className="reflect__actions">
        <button
          className="reflect__action-btn reflect__action-btn--primary"
          onClick={handleNewReading}
        >
          New reading
        </button>
        <button
          className="reflect__action-btn reflect__action-btn--secondary"
          onClick={handleSave}
        >
          Save
        </button>
      </div>
    </div>
  );
}
