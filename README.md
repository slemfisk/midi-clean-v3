# MIDI Clean V3

**Algorithmic MIDI Reconstruction for Production-Grade Workflows**

MIDI Clean V3 is a command-line utility designed to surgically reconstruct expressive or noisy MIDI data into production-ready sequences. Built on top of the Python `mido` ecosystem, the tool provides deterministic quantization, harmonic forcing, velocity conditioning, and vertical alignment logic suitable for scoring, sound design, and asset pipelines.

Rather than acting as a basic grid quantizer, MIDI Clean V3 applies reconstruction heuristics to reshape timing, structure, and harmonic context while preserving musical intent. The engine is optimized for batch pipelines and repeatable processing across large MIDI collections.

## Value Proposition

- **Deterministic cleanup** for live-played MIDI recordings
- **Structural alignment** of chords and layered articulations
- **Harmonic constraint enforcement** for orchestration workflows
- **Velocity field shaping** for mix predictability
- **CLI-native** for integration with DAWs, build scripts, and asset pipelines

Target users include producers, orchestrators, technical composers, and developers managing MIDI datasets or score exports.

## Installation

### Requirements

- Python 3.9+
- pip

### Setup

```bash
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

pip install mido python-rtmidi
```

Clone repository and install:

```bash
git clone https://github.com/slemfisk/midi-clean-v3.git
cd midi-clean-v3
pip install -r requirements.txt
```

Verify installation:

```bash
python midi_clean.py --help
```

## Quick Start

Clean timing and export reconstructed file:

```bash
python midi_clean.py input.mid output.mid --quantize 1/16
```

Fix staggered chords and normalize velocity:

```bash
python midi_clean.py take.mid clean.mid --straighten --vel-scale 0.8
```

Batch process directory:

```bash
for f in *.mid; do
  python midi_clean.py "$f" "clean/$f" --quantize 1/32 --humanize
done
```

## CLI Arguments Reference

### Input / Output

| Argument | Description |
|----------|-------------|
| `input.mid` | Source MIDI file |
| `output.mid` | Destination file |
| `--overwrite` | Replace existing output |
| `--dry-run` | Execute logic without writing |

### Timing

| Argument | Description |
|----------|-------------|
| `--quantize DIV` | Grid-lock notes to division |
| `--straighten` | Align chord onsets vertically |
| `--swing AMT` | Apply swing offset |
| `--humanize` | Inject micro-timing variance |

### Dynamics

| Argument | Description |
|----------|-------------|
| `--vel-scale X` | Scale velocities |
| `--vel-clamp MIN MAX` | Clamp velocity range |
| `--vel-human` | Randomize velocity |

### Reconstruction

| Argument | Description |
|----------|-------------|
| `--force-key KEY` | Constrain notes to scale |
| `--dedupe` | Remove stacked duplicates |
| `--legato-fix` | Repair overlapping notes |

## Primary Workflows

### Perfect Score

Use when exporting MIDI to notation engines or orchestral templates.

```bash
python midi_clean.py score.mid out.mid --quantize 1/32 --straighten --dedupe
```

**Effects:**
- Eliminates staggered onset drift
- Locks durations to grid
- Produces engraving-ready output

### Natural Groove

Use when retaining human feel but improving clarity.

```bash
python midi_clean.py jam.mid out.mid --humanize --vel-human --vel-scale 0.9
```

**Effects:**
- Smooth timing inconsistencies
- Preserves expressive velocity variation
- Avoids robotic quantization artifacts

### Orchestrator

Use when enforcing harmonic constraints on sketch material.

```bash
python midi_clean.py sketch.mid out.mid --force-key Dminor --legato-fix
```

**Effects:**
- Corrects out-of-scale pitches
- Stabilizes transitions
- Prepares for template routing

## Smart Reconstruction Logic

### Onset Straightening

When `--straighten` is enabled:

1. Notes are grouped by temporal proximity window
2. Average onset time is calculated
3. All notes in cluster are shifted to mean

This resolves vertical drift in chord recordings without rigid quantization.

### Quantization Engine

- Converts MIDI ticks to musical grid units
- Finds nearest division
- Applies deterministic shift
- Preserves duration relationships when possible

### Velocity Humanization vs Timing Humanization

**`--humanize`**
- Alters timing offsets
- Injects micro deviations in onset

**`--vel-human`**
- Alters velocity values only
- Leaves timing intact

These operate independently to prevent overlap of intent.

### Harmonic Forcing

`--force-key` maps notes to nearest scale tone:

1. Detect pitch class
2. Compute minimal interval shift
3. Reassign note number

Designed for sketch cleanup rather than theoretical reharmonization.

### Technical Note

The engine uses `mido` for message parsing and reconstruction:

- Reads note-on/off pairs
- Maintains tick resolution
- Rewrites message stream after transformation

Timing shifts are applied before message serialization to ensure deterministic ordering and reproducibility across environments.

## Batch Processing and Safety

### Recommendations

- Avoid `--overwrite` during testing
- Keep raw backups
- Use `--dry-run` to validate settings

### Example safe batch:

```bash
mkdir processed
for f in *.mid; do
  python midi_clean.py "$f" "processed/$f"
done
```

## Positioning

MIDI Clean V3 should be viewed as a **reconstruction instrument** rather than a convenience quantizer. Its role is to enforce structural clarity, harmonic discipline, and velocity predictability in contexts where downstream accuracy impacts scoring, rendering, or gameplay systems.

## License

MIT License - see LICENSE file for details.

## Contributions

Pull requests should include before/after MIDI examples and timing diff metrics where applicable.

## Repository

[https://github.com/slemfisk/midi-clean-v3](https://github.com/slemfisk/midi-clean-v3)
