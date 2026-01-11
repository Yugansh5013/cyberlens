"use client";

import FloatingAudioButton from "./FloatingAudioButton";

interface DualLanguageAudioProps {
  englishSrc?: string;
  hindiSrc?: string;
}

export default function DualLanguageAudio({
  englishSrc = "/audio/fiscal-en.mp3",
  hindiSrc = "/audio/fiscal-hi.mp3",
}: DualLanguageAudioProps) {
  return (
    <>
      {/* Hindi Audio - Bottom Left */}
      <FloatingAudioButton src={hindiSrc} label="हिन्दी ऑडियो" position="left" />

      {/* English Audio - Bottom Right */}
      <FloatingAudioButton src={englishSrc} label="English Audio" position="right" />
    </>
  );
}
