import {Composition, registerRoot} from 'remotion';
import {CuracaoGap} from './CuracaoGap';

const RemotionRoot = () => (
  <>
    <Composition
      id="Curacao"
      component={CuracaoGap}
      durationInFrames={90}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);

registerRoot(RemotionRoot);
