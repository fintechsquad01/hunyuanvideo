import {AbsoluteFill, interpolate, useCurrentFrame, spring, useVideoConfig, staticFile, delayRender, continueRender} from 'remotion';
import {useEffect, useState} from 'react';

// Load brand fonts from public/ via staticFile (no remote allowlist issue)
const useFonts = () => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    const css = `
      @font-face { font-family: 'Anton'; src: url('${staticFile('Anton-Regular.ttf')}'); }
      @font-face { font-family: 'Inter'; src: url('${staticFile('Inter-Bold.otf')}'); font-weight: 700; }
      @font-face { font-family: 'Inter'; src: url('${staticFile('Inter-SemiBold.otf')}'); font-weight: 600; }
      @font-face { font-family: 'Roboto Condensed'; src: url('${staticFile('RobotoCondensed-Bold.ttf')}'); font-weight: 700; }
    `;
    const style = document.createElement('style');
    style.innerHTML = css;
    document.head.appendChild(style);
    document.fonts.ready.then(() => {
      setReady(true);
      continueRender(handle);
    });
  }, [handle]);
  return ready;
};

const TOKENS = {
  bgTop: '#0d2818',
  bgMid: '#08180e',
  bgBot: '#020a05',
  green: '#0f9d58',
  yellow: '#ffd400',
  danger: '#ff4d4d',
  curBlue: '#0033a0',
  gerRed: '#cf142b',
};

const AnimatedNumber: React.FC<{
  start: number;
  end: number;
  startFrame: number;
  endFrame: number;
  color: string;
  size: number;
}> = ({start, end, startFrame, endFrame, color, size}) => {
  const frame = useCurrentFrame();
  const v = Math.round(
    interpolate(frame, [startFrame, endFrame], [start, end], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );
  return (
    <span
      style={{
        fontFamily: 'Anton',
        fontSize: size,
        color,
        lineHeight: 0.95,
        letterSpacing: '-0.02em',
        fontVariantNumeric: 'tabular-nums',
        textShadow: '0 4px 24px rgba(0,0,0,0.6)',
      }}
    >
      {v}
    </span>
  );
};

export const CuracaoGap: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  // Beats (in frames at 30fps)
  const ELEMENTS_IN = 15;     // 0.5s — labels/flags slide in
  const PHASE1_END = 45;      // 1.5s — both counters reach 1436
  const CUR_LOCK_END = 51;    // 1.7s — beat hold
  const PHASE2_END = 78;      // 2.6s — Germany continues to 1923
  const GAP_REVEAL = 80;      // 2.66s — gap value appears
  const HOLD_END = 110;       // 3.66s — total duration ~3.7s

  // Slide-in helpers
  const slideIn = (start: number) =>
    spring({
      frame: frame - start,
      fps,
      config: {damping: 18, stiffness: 180},
    });

  const cur = slideIn(0);
  const ger = slideIn(2);

  // Curaçao Elo value
  const curValue = interpolate(frame, [ELEMENTS_IN, PHASE1_END], [0, 1436], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Germany Elo value — climbs through phase 1 + 2
  const gerValue = interpolate(
    frame,
    [ELEMENTS_IN, PHASE1_END, PHASE2_END],
    [0, 1436, 1923],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  const showGap = frame >= GAP_REVEAL;
  const gapOpacity = interpolate(frame, [GAP_REVEAL, GAP_REVEAL + 8], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const gapScale = interpolate(frame, [GAP_REVEAL, GAP_REVEAL + 12], [0.85, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{
      background: `linear-gradient(180deg, ${TOKENS.bgTop} 0%, ${TOKENS.bgMid} 55%, ${TOKENS.bgBot} 100%)`,
    }}>
      {/* Top brand watermark */}
      <div style={{
        position: 'absolute',
        top: 28,
        left: 28,
        fontFamily: 'Inter',
        fontWeight: 700,
        fontSize: 28,
        color: 'rgba(255,255,255,0.6)',
        letterSpacing: '-0.01em',
      }}>
        pitch.predict
      </div>

      {/* TOP HALF: Curaçao */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '50%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        opacity: cur,
        transform: `translateY(${(1 - cur) * 40}px)`,
      }}>
        <div style={{
          fontFamily: 'Roboto Condensed',
          fontWeight: 700,
          fontSize: 32,
          color: '#8aa195',
          letterSpacing: '0.08em',
          marginBottom: 12,
        }}>#90 IN THE WORLD</div>
        <div style={{
          fontFamily: 'Anton',
          fontSize: 120,
          color: '#fff',
          letterSpacing: '-0.02em',
          lineHeight: 0.95,
        }}>CURAÇAO</div>
        <div style={{
          marginTop: 18,
          width: 220,
          height: 130,
          background: TOKENS.curBlue,
          borderRadius: 6,
          boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
        }} />
        <div style={{marginTop: 28}}>
          <AnimatedNumber
            start={0}
            end={1436}
            startFrame={ELEMENTS_IN}
            endFrame={PHASE1_END}
            color={frame >= CUR_LOCK_END ? TOKENS.yellow : '#fff'}
            size={200}
          />
        </div>
      </div>

      {/* Divider */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: 0,
        right: 0,
        height: 4,
        background: `linear-gradient(90deg, transparent, ${TOKENS.green}, transparent)`,
        opacity: 0.7,
        transform: `translateY(-2px)`,
      }} />

      {/* BOTTOM HALF: Germany */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: 0,
        right: 0,
        height: '50%',
        display: 'flex',
        flexDirection: 'column-reverse',
        justifyContent: 'center',
        alignItems: 'center',
        opacity: ger,
        transform: `translateY(${(1 - ger) * -40}px)`,
        paddingBottom: 64,
      }}>
        <div style={{
          fontFamily: 'Roboto Condensed',
          fontWeight: 700,
          fontSize: 32,
          color: '#8aa195',
          letterSpacing: '0.08em',
          marginTop: 12,
        }}>#11 IN THE WORLD · FIRST MATCH</div>
        <div style={{
          fontFamily: 'Anton',
          fontSize: 120,
          color: '#fff',
          letterSpacing: '-0.02em',
          lineHeight: 0.95,
        }}>GERMANY</div>
        <div style={{
          marginBottom: 18,
          width: 220,
          height: 130,
          background: TOKENS.gerRed,
          borderRadius: 6,
          boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
        }} />
        <div style={{marginBottom: 28}}>
          <AnimatedNumber
            start={0}
            end={1923}
            startFrame={ELEMENTS_IN}
            endFrame={PHASE2_END}
            color={frame >= PHASE2_END ? TOKENS.danger : '#fff'}
            size={200}
          />
        </div>
      </div>

      {/* GAP REVEAL — overlay center-screen */}
      {showGap && (
        <AbsoluteFill style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: gapOpacity,
        }}>
          <div style={{
            background: 'rgba(0,0,0,0.78)',
            padding: '48px 80px',
            borderRadius: 12,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            transform: `scale(${gapScale})`,
            boxShadow: `0 0 60px ${TOKENS.danger}55, 0 8px 40px rgba(0,0,0,0.6)`,
          }}>
            <div style={{
              fontFamily: 'Anton',
              fontSize: 48,
              color: '#fff',
              letterSpacing: '-0.02em',
              marginBottom: 8,
            }}>THE GAP</div>
            <div style={{
              fontFamily: 'Anton',
              fontSize: 280,
              color: TOKENS.danger,
              letterSpacing: '-0.04em',
              lineHeight: 0.9,
              textShadow: `0 0 30px ${TOKENS.danger}99`,
            }}>+487</div>
            <div style={{
              fontFamily: 'Anton',
              fontSize: 42,
              color: '#fff',
              letterSpacing: '-0.02em',
              marginTop: 8,
            }}>BIGGEST GAP IN WC HISTORY</div>
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
