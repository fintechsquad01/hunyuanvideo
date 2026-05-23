/* eslint-disable */
// pitch.predict — Video Chrome components (one file for tightness).
// Loaded as text/babel.

const { useState, useEffect, useMemo } = React;

// --- Chrome primitives ---

function HookBand({ children }) {
  return <div className="vc-band vc-band--hook"><div className="vc-hook-text">{children}</div></div>;
}

function CtaBand({ text = "Comment your pick", follow = "→ Follow" }) {
  return (
    <div className="vc-band vc-band--cta">
      <div className="vc-cta-text">{text}</div>
      <div className="vc-cta-follow">{follow}</div>
    </div>
  );
}

function Watermark() {
  return <img className="vc-watermark" src="assets/logo-icon.svg" alt=""/>;
}

function OddsBadge({ items = [] }) {
  return (
    <div className="vc-odds">
      {items.map(it => (
        <div className="vc-odds-chip" key={it.label}>
          <div className="lbl">{it.label}</div>
          <div className="num">{it.value}</div>
        </div>
      ))}
    </div>
  );
}

function RoundIndicator({ round = "R32" }) {
  return <div className={`vc-round ${round === "FINAL" ? "vc-round--final" : ""}`}>{round}</div>;
}

function LowerThird({ eyebrow = "Round of 32", title = "Group D Predictor" }) {
  return (
    <div className="vc-lower-third">
      <div className="eyebrow">{eyebrow}</div>
      <div className="title">{title}</div>
    </div>
  );
}

function WinnerBanner({ team = "SPAIN", primary = "#AA151B", secondary = "#7a0e13", sub = "Champions · Bracket Plinko" }) {
  return (
    <div className="vc-winner-screen">
      <div className="vc-winner-bg" style={{ background: `linear-gradient(180deg, ${primary} 0%, ${secondary} 100%)` }}/>
      <div className="vc-winner-card">
        <div className="crown">WINNER</div>
        <div className="name">{team}</div>
        <div className="sub">{sub}</div>
      </div>
    </div>
  );
}

function StingerFlash() {
  return <div className="vc-stinger"><img src="assets/logo-icon.svg" alt=""/></div>;
}

function Outro() {
  return (
    <div className="vc-outro">
      <img className="mark" src="assets/logo-lockup.svg" alt=""/>
      <div className="sub">Follow daily.</div>
    </div>
  );
}

// --- Demo marble stage (purely visual; not a real physics engine) ---

function MarbleStage({ marbles }) {
  return (
    <div className="vc-stage-marbles">
      {marbles.map((m, i) => (
        <img
          key={i}
          className="vc-marble"
          src={`assets/marble-${m.code.toLowerCase()}.svg`}
          alt={m.code}
          style={{ left: `${m.x}%`, top: `${m.y}%`, width: m.size || 56, height: m.size || 56 }}
        />
      ))}
    </div>
  );
}

// --- VideoFrame: the 9:16 bezel + viewport ---

function VideoFrame({ children, label }) {
  return (
    <div className="vc-bezel">
      {label && <div className="vc-frame-label">{label}</div>}
      <div className="vc-viewport">
        <div className="vc-inner">{children}</div>
      </div>
    </div>
  );
}

// --- The six frames ---

const SAMPLE_MARBLES_PLINKO = [
  { code: "BRA", x: 10, y: 25 },
  { code: "ARG", x: 30, y: 35 },
  { code: "ESP", x: 50, y: 20, size: 64 },
  { code: "FRA", x: 70, y: 45 },
  { code: "GER", x: 18, y: 55 },
  { code: "ENG", x: 60, y: 65 },
];

const SAMPLE_MARBLES_LATE = [
  { code: "ESP", x: 35, y: 30, size: 84 },
  { code: "FRA", x: 60, y: 30, size: 84 },
];

const FRAMES = [
  {
    key: "intro",
    label: "0.5s · Intro stinger",
    render: () => (<StingerFlash/>),
  },
  {
    key: "hook",
    label: "Frame 1 · Hook + watermark",
    render: () => (
      <>
        <MarbleStage marbles={SAMPLE_MARBLES_PLINKO}/>
        <HookBand>Who survives Group D?</HookBand>
        <Watermark/>
      </>
    ),
  },
  {
    key: "mid",
    label: "Mid render · odds + round",
    render: () => (
      <>
        <MarbleStage marbles={SAMPLE_MARBLES_PLINKO}/>
        <HookBand>Polymarket vs. Plinko</HookBand>
        <Watermark/>
        <OddsBadge items={[
          { label: "POLYMARKET", value: "18%" },
          { label: "PLINKO",     value: "20%" },
          { label: "ELO",        value: "1842" },
        ]}/>
        <RoundIndicator round="R32"/>
        <CtaBand text="Comment your pick"/>
      </>
    ),
  },
  {
    key: "lower",
    label: "Lower third reveal",
    render: () => (
      <>
        <MarbleStage marbles={SAMPLE_MARBLES_PLINKO}/>
        <HookBand>Group D Predictor</HookBand>
        <Watermark/>
        <OddsBadge items={[
          { label: "POLYMARKET", value: "18%" },
          { label: "PLINKO",     value: "20%" },
        ]}/>
        <LowerThird eyebrow="Round of 32" title="Group D — Predictor"/>
        <RoundIndicator round="R32"/>
      </>
    ),
  },
  {
    key: "winner",
    label: "Winner reveal",
    render: () => (
      <>
        <WinnerBanner team="SPAIN" primary="#AA151B" secondary="#7a0e13" sub="Champions · Bracket Plinko"/>
        <Watermark/>
        <RoundIndicator round="FINAL"/>
      </>
    ),
  },
  {
    key: "outro",
    label: "0.6s · Outro stinger",
    render: () => (
      <>
        <MarbleStage marbles={SAMPLE_MARBLES_LATE}/>
        <Outro/>
      </>
    ),
  },
];

function App() {
  const [idx, setIdx] = useState(2);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "ArrowRight") setIdx(i => Math.min(FRAMES.length - 1, i + 1));
      if (e.key === "ArrowLeft")  setIdx(i => Math.max(0, i - 1));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const F = FRAMES[idx];

  return (
    <div className="vc-stage">
      <div className="vc-stage-inner">
        <VideoFrame label={F.label}>
          {F.render()}
        </VideoFrame>
      </div>
      <div className="vc-nav">
        {FRAMES.map((f, i) => (
          <button key={f.key} className={i === idx ? "active" : ""} onClick={() => setIdx(i)}>{f.key}</button>
        ))}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
