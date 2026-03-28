import React from "react";
import { Audio, interpolate, staticFile } from "remotion";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";
import { TransitionSeries, linearTiming, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { ProductVideoProps } from "../types";
import { Scene1Hook } from "./scenes/Scene1Hook";
import { Scene2LogoReveal } from "./scenes/Scene2LogoReveal";
import { Scene3MeetingDemo } from "./scenes/Scene3MeetingDemo";
import { Scene4Pipeline } from "./scenes/Scene4Pipeline";
import { Scene5Features } from "./scenes/Scene5Features";
import { Scene6CTA } from "./scenes/Scene6CTA";
import "../global.css";

loadInter();
loadJetBrainsMono();

/*
 * Scene timing (total = 900 frames @ 30fps = 30s):
 *
 * Scene 1 (Hook):       120 frames (4.0s)
 * Scene 2 (Logo):       150 frames (5.0s)
 * Scene 3 (Demo):       290 frames (9.7s) — HERO
 * Scene 4 (Pipeline):   150 frames (5.0s)
 * Scene 5 (Features):   150 frames (5.0s)
 * Scene 6 (CTA):        115 frames (3.8s)
 *
 * Sum sequences: 975, transitions: 5×15 = 75
 * Total: 975 - 75 = 900 ✓
 */

export const ProductVideo: React.FC<ProductVideoProps> = (props) => {
  return (
    <>
      {/* Background music — fade in 1s, sustain at 0.30, fade out last 2s */}
      <Audio
        src={staticFile("bg-music.mp3")}
        volume={(f) => {
          const fadeIn = interpolate(f, [0, 30], [0, 0.30], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const fadeOut = interpolate(f, [840, 900], [0.30, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return Math.min(fadeIn, fadeOut);
        }}
      />

      <TransitionSeries>
        {/* Scene 1 - Hook */}
        <TransitionSeries.Sequence durationInFrames={120}>
          <Scene1Hook text={props.hookText} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 15 })}
        />

        {/* Scene 2 - Logo Reveal */}
        <TransitionSeries.Sequence durationInFrames={150}>
          <Scene2LogoReveal tagline={props.tagline} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={slide({ direction: "from-bottom" })}
          timing={springTiming({ config: { damping: 20, stiffness: 100 }, durationInFrames: 15 })}
        />

        {/* Scene 3 - Meeting Demo (HERO) */}
        <TransitionSeries.Sequence durationInFrames={290}>
          <Scene3MeetingDemo
            transcription={props.demoTranscription}
            insights={props.demoInsights}
          />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={wipe({ direction: "from-left" })}
          timing={linearTiming({ durationInFrames: 15 })}
        />

        {/* Scene 4 - Pipeline Architecture */}
        <TransitionSeries.Sequence durationInFrames={150}>
          <Scene4Pipeline />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 15 })}
        />

        {/* Scene 5 - Features + Stats */}
        <TransitionSeries.Sequence durationInFrames={150}>
          <Scene5Features features={props.features} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 15 })}
        />

        {/* Scene 6 - CTA */}
        <TransitionSeries.Sequence durationInFrames={115}>
          <Scene6CTA ctaText={props.ctaText} ctaUrl={props.ctaUrl} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </>
  );
};
