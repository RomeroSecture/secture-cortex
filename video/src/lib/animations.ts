import { interpolate, spring, Easing } from "remotion";

export function fadeIn(
  frame: number,
  start: number,
  duration: number = 15
): number {
  return interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
}

export function fadeOut(
  frame: number,
  start: number,
  duration: number = 15
): number {
  return interpolate(frame, [start, start + duration], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
}

export function slideUp(
  frame: number,
  start: number,
  duration: number = 20,
  distance: number = 40
): number {
  return interpolate(frame, [start, start + duration], [distance, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
}

export function slideLeft(
  frame: number,
  start: number,
  duration: number = 20,
  distance: number = 40
): number {
  return interpolate(frame, [start, start + duration], [-distance, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
}

export function bounceIn(
  frame: number,
  fps: number,
  delay: number = 0,
  damping: number = 8
): number {
  return spring({
    frame: frame - delay,
    fps,
    config: { damping, stiffness: 200 },
  });
}

export function countUp(
  frame: number,
  start: number,
  duration: number,
  target: number
): number {
  const raw = interpolate(frame, [start, start + duration], [0, target], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return Math.round(raw);
}

export function wipeIn(
  frame: number,
  start: number,
  duration: number = 20
): string {
  const progress = interpolate(frame, [start, start + duration], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return `${progress}%`;
}

export function pulse(frame: number, speed: number = 0.1): number {
  return 0.5 + 0.5 * Math.sin(frame * speed);
}

export function typewriter(
  frame: number,
  start: number,
  text: string,
  speed: number = 0.35
): string {
  const charsVisible = interpolate(
    frame,
    [start, start + text.length * speed],
    [0, text.length],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  return text.slice(0, Math.floor(charsVisible));
}
