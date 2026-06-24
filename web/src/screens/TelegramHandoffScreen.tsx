import { Button, Card, PageShell, StepHeader } from '../components'
import './TelegramHandoffScreen.css'

const BOT_USERNAME = import.meta.env.VITE_TELEGRAM_BOT_USERNAME ?? 'LuvrBot'
const START_PARAM = import.meta.env.VITE_TELEGRAM_START_PARAM ?? 'demo-onboarding-token'
const DEFAULT_DEEP_LINK = `https://t.me/${BOT_USERNAME}?start=${START_PARAM}`

export interface TelegramHandoffScreenProps {
  /** Override deep link — defaults to VITE_TELEGRAM_BOT_USERNAME env var. */
  deepLink?: string
}

export function TelegramHandoffScreen({
  deepLink = DEFAULT_DEEP_LINK,
}: TelegramHandoffScreenProps) {
  return (
    <PageShell>
      <Card>
        <StepHeader currentStep={3} totalSteps={3} eyebrow="Last step" />
        <div className="lv-handoff__body">
          <h2>You&apos;re all set. Now say hi on Telegram.</h2>
          <p className="lv-handoff__lede">
            Tap below to open Luvr on Telegram — it&apos;ll already know who you
            are. That&apos;s where the actual texting happens.
          </p>

          <Button
            fullWidth
            onClick={() => window.open(deepLink, '_blank', 'noopener,noreferrer')}
          >
            Open in Telegram
          </Button>

          <div className="lv-handoff__link-box">
            <span className="lv-handoff__link-label">Or use this link</span>
            <code className="lv-handoff__link">{deepLink}</code>
          </div>
        </div>
      </Card>
    </PageShell>
  )
}
