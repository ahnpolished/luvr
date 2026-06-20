import { Button, Card, PageShell } from '../components'
import logo from '../assets/logo.svg'
import './LandingScreen.css'

export interface LandingScreenProps {
  onGetStarted: () => void
}

const HOW_IT_WORKS = [
  {
    number: '01',
    title: 'Just text it',
    body: "Type out the question, the spiral, the whole situation. Luvr replies like a friend who's actually paying attention.",
  },
  {
    number: '02',
    title: 'Send the screenshot',
    body: "Drop in the confusing thread or the bio that's giving mixed signals. Luvr reads the room so you don't have to guess.",
  },
  {
    number: '03',
    title: 'Or just talk',
    body: 'Some things are too long or too raw to type. Send a voice memo. Luvr listens and texts you back.',
  },
]

export function LandingScreen({ onGetStarted }: LandingScreenProps) {
  return (
    <PageShell>
      <Card wide>
        <nav className="lv-landing__nav">
          <span className="lv-landing__wordmark">
            <img src={logo} alt="Luvr" className="lv-landing__logo" />
            Luvr<span className="lv-landing__dot">.</span>
          </span>
          <div className="lv-landing__nav-links">
            <a href="#how-it-works">How it works</a>
            <a href="#privacy">Privacy</a>
            <a href="#telegram">Telegram</a>
            <Button onClick={onGetStarted}>Start texting</Button>
          </div>
        </nav>

        <section className="lv-landing__hero">
          <div className="lv-landing__hero-copy">
            <div className="lv-landing__eyebrow">
              <span className="lv-landing__dot-mark" />
              AI dating advice · over text
            </div>
            <h1>Dating is confusing. Your advice shouldn&apos;t be.</h1>
            <p className="lv-landing__lede">
              Luvr is an AI you text like a friend. Send a question, a screenshot of a
              conversation going nowhere, or a voice memo about a date that went
              sideways — and get honest, real advice back.
            </p>
            <div className="lv-landing__cta-row">
              <Button size="lg" onClick={onGetStarted}>
                Start texting Luvr
              </Button>
              <Button size="lg" variant="secondary">
                See how it works
              </Button>
            </div>
            <div className="lv-landing__fineprint">
              No swiping. No profiles. No therapy-speak.
            </div>
          </div>

          <div className="lv-landing__chat">
            <div className="lv-landing__chat-header">
              <span className="lv-landing__chat-avatar">L</span>
              <span className="lv-landing__chat-name">Luvr</span>
              <span className="lv-landing__chat-status">now active</span>
            </div>
            <div className="lv-landing__bubble lv-landing__bubble--user">
              he said "we should hang sometime" then went quiet for 4 days. do i text
              him??
            </div>
            <div className="lv-landing__bubble lv-landing__bubble--luvr">
              Four days of silence after a vague "sometime" is information, not an
              accident.
            </div>
            <div className="lv-landing__bubble lv-landing__bubble--luvr">
              Text once if you want — keep it light, no essay. If the same energy
              comes back, you&apos;ve got your answer. You&apos;re not chasing,
              you&apos;re checking.
            </div>
            <div className="lv-landing__bubble lv-landing__bubble--user">
              ok that&apos;s fair. brutal but fair 😭
            </div>
          </div>
        </section>

        <section id="how-it-works" className="lv-landing__section">
          <div className="lv-landing__eyebrow">
            <span className="lv-landing__dot-mark" />
            However you want to say it
          </div>
          <div className="lv-landing__grid">
            {HOW_IT_WORKS.map((step) => (
              <div className="lv-landing__step-card" key={step.number}>
                <div className="lv-landing__step-number">{step.number}</div>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="lv-landing__section">
          <div className="lv-landing__quote-panel">
            <blockquote>
              "Your group chat loves you, but they're rooting for the story. Luvr is
              rooting for you — even when the honest answer isn't the one you
              wanted."
            </blockquote>
          </div>
        </section>

        <section id="telegram" className="lv-landing__section">
          <div className="lv-landing__eyebrow">
            <span className="lv-landing__dot-mark" />
            Start where you already text
          </div>
          <div className="lv-landing__channels">
            <div className="lv-landing__channel-card">
              <div className="lv-landing__channel-head">
                <h3>Telegram</h3>
                <span className="lv-landing__badge">Available now</span>
              </div>
              <p>Add Luvr to Telegram and start texting in under a minute. No app to download.</p>
              <Button variant="secondary" onClick={onGetStarted}>
                Open in Telegram
              </Button>
            </div>
            <div className="lv-landing__channel-card lv-landing__channel-card--muted">
              <div className="lv-landing__channel-head">
                <h3>iMessage</h3>
                <span className="lv-landing__badge lv-landing__badge--soon">Coming soon</span>
              </div>
              <p>Luvr in your iMessage thread, no extra app required.</p>
              <Button variant="secondary" disabled>
                Notify me
              </Button>
            </div>
          </div>
        </section>
      </Card>
    </PageShell>
  )
}
