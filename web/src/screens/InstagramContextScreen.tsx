import { useState } from 'react'
import { Button, Card, PageShell, StepHeader, TextInput } from '../components'
import './InstagramContextScreen.css'

export interface InstagramContextScreenProps {
  onContinue: (context: { handle?: string; selfSummary?: string }) => void
}

export function InstagramContextScreen({ onContinue }: InstagramContextScreenProps) {
  const [mode, setMode] = useState<'instagram' | 'self-summary'>('instagram')
  const [handle, setHandle] = useState('')
  const [selfSummary, setSelfSummary] = useState('')

  return (
    <PageShell>
      <Card>
        <StepHeader currentStep={2} totalSteps={3} eyebrow="Context (not login)" />
        <div className="lv-context__body">
          <span className="lv-context__eyebrow">Context</span>
          <h2>Give Luvr some context.</h2>

          {mode === 'instagram' ? (
            <>
              <p className="lv-context__lede">
                Drop your public Instagram handle. Luvr reads your bio and the vibe
                of your page so its advice actually fits you.
              </p>

              <TextInput
                label="Instagram handle"
                placeholder="yourhandle"
                adornment="@"
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                helperText="Public profiles only. We read your bio and themes — never your DMs, never anything private."
              />

              <div className="lv-context__note">
                <span className="lv-context__note-dot" />
                <p>
                  Luvr keeps a short, readable summary of your vibe — not a copy of
                  your account. You can see and edit it anytime.
                </p>
              </div>

              <Button fullWidth onClick={() => onContinue({ handle })} className="lv-context__primary">
                Continue
              </Button>
              <Button variant="ghost" onClick={() => setMode('self-summary')}>
                I&apos;d rather describe myself
              </Button>
            </>
          ) : (
            <>
              <p className="lv-context__lede">
                No Instagram? No problem. Just tell Luvr a little about yourself —
                a couple sentences is plenty.
              </p>

              <TextInput
                label="About you"
                placeholder="e.g. into hiking, bad at texting back, just got out of something long-term..."
                value={selfSummary}
                onChange={(e) => setSelfSummary(e.target.value)}
              />

              <Button fullWidth onClick={() => onContinue({ selfSummary })} className="lv-context__primary">
                Continue
              </Button>
              <Button variant="ghost" onClick={() => setMode('instagram')}>
                Actually, use my Instagram
              </Button>
            </>
          )}
        </div>
      </Card>
    </PageShell>
  )
}
