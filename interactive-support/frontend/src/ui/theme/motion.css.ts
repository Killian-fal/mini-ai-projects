import { createVar, keyframes, style } from "@vanilla-extract/css";
import { vars } from "./tokens.css";

const noMotionPreference = "(prefers-reduced-motion: no-preference)";

export const riseDistance = createVar();

const fadeIn = keyframes({ from: { opacity: 0 } });

const riseIn = keyframes({
  from: { opacity: 0, transform: `translateY(${riseDistance})` },
});

function enter(distance: string, duration: string, easing: string) {
  return style({
    vars: { [riseDistance]: distance },
    animation: `${fadeIn} ${duration} ${easing} both`,
    "@media": { [noMotionPreference]: { animationName: riseIn } },
  });
}

export const enterMessage = enter("8px", vars.motion.enter, vars.motion.easeOut);
export const enterCard = enter("12px", vars.motion.card, vars.motion.cardEase);
export const enterOption = enter("6px", vars.motion.enter, vars.motion.easeOut);
export const enterRow = enter("6px", vars.motion.enter, vars.motion.easeOut);

export const fade = style({
  animation: `${fadeIn} 0.4s ${vars.motion.easeOut} both`,
});

export const pulse = keyframes({
  "0%, 80%, 100%": { opacity: 0.2 },
  "40%": { opacity: 1 },
});

export const motionQuery = noMotionPreference;
