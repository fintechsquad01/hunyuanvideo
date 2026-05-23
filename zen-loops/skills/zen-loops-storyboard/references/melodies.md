# Melody library — zen-loops Ring Expansion

The 11 melodies currently encoded in `zen-loops/engines/audio_reactive/collision_audio.py`. The storyboard skill picks one of these by name.

All are public domain. Funnel-safe.

## Available melodies

| Key | Title | Notes | Mood | Recognition |
|---|---|---|---|---|
| `twinkle` | Twinkle Twinkle Little Star | 14 notes | warm, nostalgic | universal |
| `ode_to_joy` | Ode to Joy (Beethoven 9th) | 15 notes | triumphant, uplifting | universal |
| `fur_elise` | Für Elise (Beethoven) | 16 notes | dramatic, classical | universal |
| `pachelbel` | Pachelbel's Canon in D | 16 notes | epic, ceremonial | high |
| `greensleeves` | Greensleeves | 16 notes | wistful, minor-key | mid |
| `frere_jacques` | Frère Jacques | 14 notes | childhood, simple | universal |
| `mary_had_lamb` | Mary Had a Little Lamb | 20 notes | childhood, simple | universal |
| `old_macdonald` | Old MacDonald | 12 notes | playful, repetitive | universal |
| `amazing_grace` | Amazing Grace | 16 notes | emotional, contemplative | mid-high |
| `happy_birthday` | Happy Birthday (PD since 2016) | 25 notes | celebratory | universal |
| `minor_arp` | Minor arpeggio loop | 18 notes | dark, suspenseful | abstract |

## Picking a melody for the storyboard

Match by mood + recognition:

- **Want universal "I got it!" comment-bait** → Twinkle, Frère Jacques, Mary Had a Little Lamb, Happy Birthday, Old MacDonald
- **Want triumphant / hype** → Ode to Joy, Pachelbel
- **Want dramatic / serious** → Für Elise, Amazing Grace
- **Want minor / suspenseful** → Greensleeves, minor_arp
- **Want celebratory / birthday-themed** → Happy Birthday

## Hook variants per melody type

| Melody mood | Hook variant |
|---|---|
| Childhood (Twinkle, Frère Jacques) | "GUESS THE SONG · MOST GET IT BY NOTE 6" |
| Triumphant (Ode to Joy, Pachelbel) | "WAIT FOR THE BEAT DROP" |
| Dramatic (Für Elise) | "ONLY 1 IN 10 GETS THIS ONE" |
| Minor / dark | "WHY DOES THIS FEEL SAD?" |
| Birthday | "TAG SOMEONE WHO'S BIRTHDAY IT IS" |

## Adding a new melody

Encode as a list of note names (e.g., `["C4", "G4", "A4", ...]`) in `collision_audio.py:MELODIES`. Add the title to `MELODY_TITLES`. The ring-expansion engine handles the rest.

For **Suno-generated original melodies** (for funnel-driving posts that need brand-owned music):

1. Generate in Suno with prompt template: *"15-second instrumental hook, [mood], [tempo] BPM, no vocals, no drums, repeating 8–12 note melody, [key signature]"*
2. Use Spotify Basic Pitch to convert to MIDI
3. Transcribe note names manually or via MIDI library
4. Add to MELODIES dict with new key
5. Document in this file with `source: suno_original_YYYYMMDD`

## Anti-patterns

- **Don't pick a melody longer than 20 notes** for a 15-second ring expansion — too many collisions, audio becomes noise
- **Don't synthesize copyrighted melodies** ("Megalovania", Pokémon themes, "Lavender Town") on funnel-driving posts — the composition copyright is real even if the recording is synthetic
- **Don't claim Suno-generated melodies as PD** — they're brand-owned, not public domain. Document the commercial license.
