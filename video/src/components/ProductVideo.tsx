import React from "react";
import { Audio, interpolate, staticFile } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { ProductVideoProps } from "../types";
import { Scene1POV } from "./scenes/Scene1POV";
import { Scene2Pain } from "./scenes/Scene2Pain";
import { Scene3Enter } from "./scenes/Scene3Enter";
import { Scene4Demo } from "./scenes/Scene4Demo";
import { Scene5SpeedRun } from "./scenes/Scene5SpeedRun";
import { Scene6CTA } from "./scenes/Scene6CTA";
import "../global.css";

loadInter();
loadJetBrainsMono();

/*
 * RELAXED PACING — 1400 frames @ 30fps = 46.7s
 *
 * Scene 1 (POV):      200 frames (6.7s)
 * Scene 2 (Pain):     180 frames (6.0s)
 * Scene 3 (Enter):    220 frames (7.3s)
 * Scene 4 (Demo):     420 frames (14.0s)
 * Scene 5 (Speed):    260 frames (8.7s)
 * Scene 6 (CTA):      220 frames (7.3s)
 *
 * Sum: 1500, transitions: 5×20 = 100
 * Total: 1500 - 100 = 1400 ✓
 */

export const ProductVideo: React.FC<ProductVideoProps> = (props) => {
  const T = 20; // longer transitions for smoother feel

  return (
    <>
      <Audio
        src={staticFile("bg-music.mp3")}
        volume={(f) => {
          const fadeIn = interpolate(f, [0, 45], [0, 0.28], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const fadeOut = interpolate(f, [1320, 1400], [0.28, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return Math.min(fadeIn, fadeOut);
        }}
        loop
      />

      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={200}>
          <Scene1POV />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={180}>
          <Scene2Pain />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={slide({ direction: "from-right" })}
          timing={linearTiming({ durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={220}>
          <Scene3Enter />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={slide({ direction: "from-bottom" })}
          timing={linearTiming({ durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={420}>
          <Scene4Demo
            transcription={props.demoTranscription}
            insights={props.demoInsights}
          />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={260}>
          <Scene5SpeedRun />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={220}>
          <Scene6CTA ctaText={props.ctaText} ctaUrl={props.ctaUrl} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </>
  );
};
