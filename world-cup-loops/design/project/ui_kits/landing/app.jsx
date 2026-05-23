/* eslint-disable */
// pitch.predict landing page

const { useState, useEffect } = React;

// --- Data (would be Supabase in production) ---
const RACES = [
  {
    code: "WC1.a",
    title: "Bracket Plinko — Top 16",
    sub: "Refreshed 2h ago · 32 → 1",
    hook: "Who lifts the trophy?",
    round: "QF",
    plays: "1.2M",
    pickRate: "60%",
    marbles: [
      { c: "esp", x: 18, y: 22 }, { c: "fra", x: 40, y: 18 },
      { c: "bra", x: 62, y: 24 }, { c: "arg", x: 30, y: 44 },
      { c: "ger", x: 56, y: 50 }, { c: "eng", x: 22, y: 64 },
    ],
  },
  {
    code: "WC2.D",
    title: "Group D — Predictor",
    sub: "T-12 days · pre-tournament",
    hook: "Group D survives?",
    round: "R32",
    plays: "846K",
    pickRate: "47%",
    marbles: [
      { c: "arg", x: 22, y: 28 }, { c: "fra", x: 48, y: 30 },
      { c: "esp", x: 30, y: 56 }, { c: "ger", x: 60, y: 60 },
    ],
  },
  {
    code: "WC5",
    title: "Polymarket Live",
    sub: "Snapshot · 24h cadence",
    hook: "What the money says",
    round: "LIVE",
    plays: "612K",
    pickRate: "—",
    marbles: [
      { c: "bra", x: 16, y: 20 }, { c: "fra", x: 44, y: 26 },
      { c: "esp", x: 30, y: 50 }, { c: "arg", x: 58, y: 52 },
      { c: "eng", x: 22, y: 72 },
    ],
  },
];

const ODDS = [
  { name: "Spain",     code: "ESP", color: "#AA151B", pm: 20, pk: 22 },
  { name: "France",    code: "FRA", color: "#0055A4", pm: 18, pk: 19 },
  { name: "Brazil",    code: "BRA", color: "#009C3B", pm: 14, pk: 13 },
  { name: "Argentina", code: "ARG", color: "#74ACDF", pm: 12, pk: 14 },
  { name: "England",   code: "ENG", color: "#cf142b", pm:  9, pk:  8 },
  { name: "Germany",   code: "GER", color: "#000000", pm:  7, pk:  6 },
];

const FORMATS = [
  { code: "WC1", ttl: "Bracket Plinko",     sub: "32 → 16 → 8 → 4 → 2 → 1. Survivors visualized round by round." },
  { code: "WC2", ttl: "Group Predictor",    sub: "Four marbles per group. Top two advance with current GD." },
  { code: "WC3", ttl: "Per-Match Race",     sub: "Two marbles, horizontal track. Goals = boosts forward." },
  { code: "WC4", ttl: "Top Scorer",         sub: "Player marbles. Position equals goals. Daily refresh." },
  { code: "WC5", ttl: "Polymarket Live",    sub: "Marble size scales with prediction-market probability." },
  { code: "WC6", ttl: "Will X Advance?",    sub: "Single team path through bracket scenarios. Reactive." },
  { code: "WC7", ttl: "Country-Food Race",  sub: "Marbles labelled with national dishes. Lower stakes, higher share." },
  { code: "WC8", ttl: "Hopium Loop",        sub: "Ring expansion. Your country's path to the final, visualised." },
];

// --- Components ---

function Nav() {
  return (
    <nav className="lp-nav lp-wrap">
      <div className="lp-nav-brand">
        <img src="assets/logo-lockup.svg" alt="pitch.predict"/>
      </div>
      <div className="lp-nav-links">
        <a href="#races">Latest race</a>
        <a href="#odds">Odds widget</a>
        <a href="#formats">Formats</a>
        <a href="#signup">Newsletter</a>
        <button className="pp-cta" style={{padding: "10px 14px", fontSize: 13}}>Follow daily →</button>
      </div>
    </nav>
  );
}

// Animated hero reel (just a CSS-driven marble bounce loop)
function HeroReel() {
  return (
    <div className="lp-reel">
      <div className="lp-reel-bezel">
        <div className="lp-reel-vp">
          <div className="lp-reel-band-top"><div className="h">Polymarket vs. Plinko</div></div>
          <img className="lp-reel-wm" src="assets/logo-icon.svg"/>
          <div className="lp-reel-odds"><div className="lbl">Polymarket</div><div className="num">18%</div></div>
          <div className="lp-reel-round">R32</div>

          <img className="lp-reel-marble m-bra" src="assets/marble-bra.svg" style={{left: "12%", top: "20%", animation: "bra-bounce 6s ease-in-out infinite"}}/>
          <img className="lp-reel-marble m-arg" src="assets/marble-arg.svg" style={{left: "42%", top: "28%", animation: "arg-bounce 5.5s ease-in-out infinite"}}/>
          <img className="lp-reel-marble m-esp" src="assets/marble-esp.svg" style={{left: "55%", top: "42%", width: 52, height: 52, animation: "esp-bounce 7s ease-in-out infinite"}}/>
          <img className="lp-reel-marble m-fra" src="assets/marble-fra.svg" style={{left: "20%", top: "52%", animation: "fra-bounce 6.4s ease-in-out infinite"}}/>
          <img className="lp-reel-marble m-ger" src="assets/marble-ger.svg" style={{left: "48%", top: "65%", animation: "ger-bounce 6.8s ease-in-out infinite"}}/>

          <div className="lp-reel-band-bot"><div className="h">Comment your pick</div><div className="f">→ Follow</div></div>
        </div>
      </div>
      <style>{`
        @keyframes bra-bounce { 0%, 100% { transform: translate(0,0); } 30% { transform: translate(-4px, 16px); } 60% { transform: translate(6px, 32px); } 80% { transform: translate(0, 48px); } }
        @keyframes arg-bounce { 0%, 100% { transform: translate(0,0); } 25% { transform: translate(10px, 22px); } 55% { transform: translate(-4px, 38px); } 80% { transform: translate(6px, 56px); } }
        @keyframes esp-bounce { 0%, 100% { transform: translate(0,0); } 30% { transform: translate(-6px, 20px); } 60% { transform: translate(10px, 12px); } }
        @keyframes fra-bounce { 0%, 100% { transform: translate(0,0); } 30% { transform: translate(12px, -10px); } 60% { transform: translate(-6px, 18px); } 80% { transform: translate(4px, -6px); } }
        @keyframes ger-bounce { 0%, 100% { transform: translate(0,0); } 30% { transform: translate(-10px, 8px); } 60% { transform: translate(6px, 22px); } 80% { transform: translate(-4px, 4px); } }
      `}</style>
    </div>
  );
}

function Hero() {
  return (
    <section className="lp-hero lp-wrap">
      <div>
        <div className="lp-hero-eyebrow"><span className="dot"/>T-19 to FIFA World Cup 2026</div>
        <h1>Brackets that <span className="accent">play themselves.</span></h1>
        <p>The football prediction-market visualiser. Polymarket odds, Elo ratings, and a decade of league data — turned into 15-second marble races people can't scroll past.</p>
        <div className="lp-hero-cta-row">
          <button className="pp-cta">Watch the latest race</button>
          <button className="pp-cta pp-cta--ghost">Read the system</button>
        </div>
        <div className="lp-hero-meta">
          <div><div className="num">42,889</div><div className="lbl">Standings snapshots</div></div>
          <div><div className="num">13,137</div><div className="lbl">Elo ratings</div></div>
          <div><div className="num">6,569</div><div className="lbl">Historical matches</div></div>
        </div>
      </div>
      <HeroReel/>
    </section>
  );
}

function RaceCard({ race }) {
  return (
    <article className="lp-race-card">
      <div className="lp-race-preview">
        <div className="top-band">{race.hook}</div>
        <div className="marbles">
          {race.marbles.map((m, i) => (
            <img key={i} src={`assets/marble-${m.c}.svg`} style={{left: `${m.x}%`, top: `${m.y}%`}}/>
          ))}
        </div>
        <div className="round">{race.round}</div>
      </div>
      <div className="lp-race-meta">
        <div className="ttl">{race.title}</div>
        <div className="sub">{race.sub}</div>
        <div className="stats">
          <div><div className="v">{race.plays}</div><div className="l">Plays</div></div>
          <div><div className="v">{race.pickRate}</div><div className="l">Survives</div></div>
          <div><div className="v">{race.code}</div><div className="l">Format</div></div>
        </div>
      </div>
    </article>
  );
}

function RaceCarousel() {
  return (
    <section id="races" className="lp-section lp-wrap">
      <div className="lp-section-h">
        <div>
          <div className="lp-eyebrow">Latest race</div>
          <h2>Three new renders today.</h2>
        </div>
        <p>Refreshed from our Supabase feed. Watch on TikTok, IG, YouTube Shorts, or right here.</p>
      </div>
      <div className="lp-race-grid">
        {RACES.map(r => <RaceCard key={r.code} race={r}/>)}
      </div>
    </section>
  );
}

function OddsWidget() {
  const maxPk = Math.max(...ODDS.map(o => o.pk));
  return (
    <section id="odds" className="lp-section lp-wrap">
      <div className="lp-section-h">
        <div>
          <div className="lp-eyebrow">Live odds</div>
          <h2>Polymarket vs. Plinko.</h2>
        </div>
        <p>The world's largest prediction market reading next to ours, side by side. Updated every 4 hours.</p>
      </div>
      <div className="lp-odds">
        <div className="lp-odds-card">
          <h3>Outright winner <span className="src">FIFA WC 2026</span></h3>
          {ODDS.map(o => (
            <div className="lp-odds-row" key={o.code}>
              <div className="swatch" style={{background: o.color}}/>
              <div className="name">{o.name} <span style={{color: "var(--pp-fg-3)", fontSize: 12, marginLeft: 8, letterSpacing: "0.10em"}}>{o.code}</span></div>
              <div className="pm">{o.pm}%</div>
              <div className="pk">{o.pk}%</div>
            </div>
          ))}
          <div style={{display: "flex", justifyContent: "space-between", marginTop: 16, font: "600 11px var(--pp-ff-body)", letterSpacing: "0.10em", textTransform: "uppercase", color: "var(--pp-fg-3)"}}>
            <span>Polymarket</span>
            <span style={{color: "var(--pp-yellow)"}}>Plinko</span>
          </div>
        </div>
        <div className="lp-odds-card">
          <h3>Spread <span className="src">By simulation</span></h3>
          {ODDS.map(o => (
            <div key={o.code} style={{padding: "12px 0", borderTop: "1px solid var(--pp-line)"}}>
              <div style={{display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 6}}>
                <div className="name" style={{font: "700 14px var(--pp-ff-hook)", letterSpacing: "-0.01em", textTransform: "uppercase"}}>{o.name}</div>
                <div style={{font: "700 16px var(--pp-ff-num)", color: "var(--pp-fg-2)"}}>{o.pk}%</div>
              </div>
              <div className="lp-odds-bar"><div className="fill" style={{width: `${(o.pk / maxPk) * 100}%`}}/></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FormatGrid() {
  return (
    <section id="formats" className="lp-section lp-wrap">
      <div className="lp-section-h">
        <div>
          <div className="lp-eyebrow">Format library</div>
          <h2>Eight ways to look at a bracket.</h2>
        </div>
        <p>Every video is built from one of these engines. Read the spec in <code style={{fontSize: 13, fontFamily: "var(--pp-ff-num)"}}>docs/format-library.md</code>.</p>
      </div>
      <div className="lp-formats">
        {FORMATS.map(f => (
          <div className="lp-format" key={f.code}>
            <div className="code">{f.code}</div>
            <div>
              <div className="ttl">{f.ttl}</div>
              <div className="sub">{f.sub}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function AppStrip() {
  return (
    <section className="lp-section lp-wrap">
      <div className="lp-app-strip">
        <div>
          <div className="lp-eyebrow" style={{color: "var(--pp-yellow)", fontSize: 13, fontFamily: "var(--pp-ff-num)", letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 12}}>Phase 2 · coming soon</div>
          <h2>Build your own bracket.</h2>
          <p>FlickPlinko: a one-tap simulator that lets you flick a marble through the World Cup bracket. Free to play. No betting, no wagers — just predictions, glory, and a leaderboard.</p>
        </div>
        <div className="lp-badge-row">
          <div className="lp-badge"><span className="glyph">{/* Apple */}<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg></span><div><div className="l1">Coming soon to</div><div className="l2">App Store</div></div></div>
          <div className="lp-badge"><span className="glyph">{/* Play */}<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M3 20.5V3.5c0-.74.4-1.39 1-1.73l11.62 11.62L4 24.23c-.6-.34-1-1-1-1.73v-2zm14.05-7.61L20.16 11c.74-.42.74-1.58 0-2L17.05 7.11l-3.36 3.36 3.36 3.42zM4.5 1.5 14.34 11l-9.84 9.5L4.5 1.5z"/></svg></span><div><div className="l1">Coming soon to</div><div className="l2">Google Play</div></div></div>
        </div>
      </div>
    </section>
  );
}

function Newsletter() {
  const [email, setEmail] = useState("");
  const [done, setDone] = useState(false);
  return (
    <section id="signup" className="lp-section lp-wrap" style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28}}>
      <div>
        <div className="lp-eyebrow" style={{color: "var(--pp-yellow)", fontSize: 13, fontFamily: "var(--pp-ff-num)", letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 12}}>Daily digest</div>
        <h2 style={{fontFamily: "var(--pp-ff-display)", fontSize: 48, fontWeight: 400, lineHeight: 0.95, letterSpacing: "-0.02em", textTransform: "uppercase", margin: "0 0 12px"}}>One race a day.<br/>Three minutes to read.</h2>
        <p style={{font: "500 15px/1.5 var(--pp-ff-body)", color: "var(--pp-fg-3)", margin: 0, maxWidth: 440}}>The day's marble race in your inbox, with the prediction-market read. No betting. No spam. Unsubscribe anytime.</p>
      </div>
      <div className="lp-newsletter">
        <h3>Subscribe</h3>
        <p>One email · 7am ET · matchdays only.</p>
        {done ? (
          <div style={{padding: 12, color: "var(--pp-green-bright)", font: "600 14px var(--pp-ff-body)"}}>You're in. Check your inbox.</div>
        ) : (
          <form className="lp-form" onSubmit={e => { e.preventDefault(); setDone(true); }}>
            <input type="email" required placeholder="you@team.com" value={email} onChange={e => setEmail(e.target.value)}/>
            <button className="pp-cta">Subscribe</button>
          </form>
        )}
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="lp-footer lp-wrap">
      <div className="lp-footer-grid">
        <div className="lp-footer-brand">
          <img src="assets/logo-lockup.svg" alt="pitch.predict"/>
          <p>Brackets that play themselves. Football prediction-market visualisation, daily.</p>
        </div>
        <div>
          <h4>Watch</h4>
          <a href="https://tiktok.com/@pitch.predict">TikTok</a>
          <a href="https://instagram.com/pitch.predict">Instagram</a>
          <a href="https://youtube.com/@pitch.predict">YouTube Shorts</a>
          <a href="https://x.com/pitch_predict">X / Twitter</a>
        </div>
        <div>
          <h4>Read</h4>
          <a href="#">Format library</a>
          <a href="#">Data sources</a>
          <a href="#">Methodology</a>
          <a href="#">Changelog</a>
        </div>
        <div>
          <h4>Company</h4>
          <a href="#">About</a>
          <a href="#">Press</a>
          <a href="mailto:hello@pitch.predict">hello@pitch.predict</a>
          <a href="#">Privacy</a>
        </div>
      </div>
      <div className="lp-footer-bottom">
        <span>© 2026 pitch.predict · Not affiliated with FIFA. Country names and flag colours used for editorial reference only.</span>
        <span>Built with Polymarket + Elo + Supabase</span>
      </div>
    </footer>
  );
}

function App() {
  return (
    <>
      <Nav/>
      <Hero/>
      <RaceCarousel/>
      <OddsWidget/>
      <FormatGrid/>
      <AppStrip/>
      <Newsletter/>
      <Footer/>
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
