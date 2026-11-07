# Mothership victory melody correction

SHA-256: `8a157fbc2d12bbea76719f3a92c96a5cf4355c0a5afe82fe9a6000be68699cd3`.
Based on Phoenix5200 v0.31, the seven-large-bird/five-escort release candidate.

The score bonus can award an extra life. Its repeated beep overwrites the
sound-B latch, which previously erased the one-time selection of Für Elise.
The correction restores the arcade's 255-tick score-display melody latch
(ROM $255B and $3923). The repeating extra-life beep is suppressed while the victory melody plays.
Its timer continues to expire, so the suppressed beep is never delayed until
after the music. The extra life and unrelated sound effects are retained.
No new notes, changed explosion sound, gameplay changes or artwork changes.

`tests/victory_audio.py` executes the real core-hit -> award -> extra life ->
next-wave routines, with and without a threshold crossing. Both cases reach
56 sequencer positions and 12 lead pitches. The old threshold-crossing case
reaches zero notes. The existing audio regression also passes: 4,200 tune
ticks, 1,744 pitch cases, 8,192 large-bird control ticks, 2,048 formation cases,
and all eight sound fallback banks.

`tests/victory_live.py --machine 5200` records the emulator's actual mixed
POKEY output through the victory, score and next-wave transition. It uses
normal boot/start plus an explicit victory fixture, not a human playthrough.
The 780-frame run reached 55 sequencer positions and wave 6, with the extra
life awarded. It recorded zero late VBI, audio underruns, missing sound updates
or layout faults; the actual POKEY recording is 13.02 seconds long.
The emulator, SDK and original 5200 BIOS are external dependencies.

Arcade reference: https://www.computerarcheology.com/Arcade/Phoenix/Code.html

Hand-drawn artwork: T1X. Existing notices and provenance remain in the source.
No physical-console test
or new human listening comparison with arcade hardware is claimed.

The targeted `tests/victory_beeps.py` compares 720 audio ticks with and without
bonus timers. All nine POKEY output bytes match; 320 bonus ticks are silent.
Ordinary bonus sounds outside victory and gunshots during music remain active.
