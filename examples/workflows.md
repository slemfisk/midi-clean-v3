# MIDI Clean V3 - Common Workflows

Practical examples for different production scenarios.

## 1. Score Export (Notation Software)

**Goal:** Prepare MIDI for import into Sibelius, Finale, or Dorico.

```bash
python midi_clean.py raw_score.mid notation_ready.mid \
  --quantize 1/32 \
  --straighten \
  --dedupe \
  --vel-clamp 64 100
```

**Why:**
- Tight quantization ensures proper notation rendering
- Straightening aligns chord voicings
- Deduplication prevents double notes
- Velocity clamping creates consistent dynamics

---

## 2. Orchestral Template Prep

**Goal:** Clean sketch MIDI before sending to orchestral VI templates.

```bash
python midi_clean.py sketch.mid template_ready.mid \
  --force-key Gmajor \
  --legato-fix \
  --vel-scale 0.85 \
  --straighten
```

**Why:**
- Key forcing ensures harmonic consistency
- Legato fix prevents sample overlap issues
- Velocity scaling accounts for template response curves
- Straightening locks ensemble timing

---

## 3. Live Recording Cleanup

**Goal:** Clean up live keyboard performance while preserving feel.

```bash
python midi_clean.py live_take.mid cleaned_take.mid \
  --quantize 1/16 \
  --humanize \
  --vel-human \
  --vel-scale 0.9
```

**Why:**
- Light quantization tightens groove without roboticizing
- Humanization adds natural micro-timing
- Velocity humanization prevents mechanical feel
- Scaling brings dynamics into usable range

---

## 4. Game Audio Asset Pipeline

**Goal:** Generate deterministic MIDI for procedural music systems.

```bash
python midi_clean.py source.mid asset.mid \
  --quantize 1/16 \
  --dedupe \
  --vel-clamp 80 110 \
  --force-key Cminor
```

**Why:**
- Strict quantization enables grid-based playback
- Deduplication prevents engine conflicts
- Velocity clamping ensures consistent mixing
- Key forcing supports dynamic music systems

---

## 5. EDM/Electronic Production

**Goal:** Perfect timing for electronic music with hard quantization.

```bash
python midi_clean.py melody.mid grid_locked.mid \
  --quantize 1/32 \
  --straighten \
  --vel-clamp 90 120 \
  --dedupe
```

**Why:**
- 1/32 quantization locks to DAW grid
- Straightening ensures sample-accurate triggering
- Velocity range optimized for electronic sounds
- Deduplication prevents phase issues

---

## 6. Remix/Reharmonization

**Goal:** Force existing MIDI to new key and add subtle groove.

```bash
python midi_clean.py original.mid reharmonized.mid \
  --force-key Ebmajor \
  --swing 0.15 \
  --vel-scale 0.95
```

**Why:**
- Key forcing transposes to target key
- Swing adds rhythmic variation
- Velocity scaling adjusts overall energy

---

## 7. Batch Processing (Directory)

**Unix/Linux/macOS:**

```bash
mkdir cleaned
for file in raw_midi/*.mid; do
  output="cleaned/$(basename "$file")"
  python midi_clean.py "$file" "$output" \
    --quantize 1/16 \
    --straighten \
    --vel-scale 0.9
done
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType Directory -Force -Path cleaned
Get-ChildItem raw_midi\*.mid | ForEach-Object {
  $output = "cleaned\$($_.Name)"
  python midi_clean.py $_.FullName $output `
    --quantize 1/16 `
    --straighten `
    --vel-scale 0.9
}
```

---

## 8. A/B Testing Workflow

**Goal:** Compare different processing settings.

```bash
# Original
cp input.mid test_original.mid

# Version A: Tight
python midi_clean.py input.mid test_tight.mid \
  --quantize 1/32 --straighten

# Version B: Loose
python midi_clean.py input.mid test_loose.mid \
  --quantize 1/16 --humanize --vel-human

# Version C: Hybrid
python midi_clean.py input.mid test_hybrid.mid \
  --quantize 1/16 --straighten --vel-human
```

---

## 9. Dry Run Testing

**Goal:** Preview changes without writing files.

```bash
python midi_clean.py input.mid output.mid \
  --quantize 1/16 \
  --straighten \
  --dry-run
```

Review console output, then remove `--dry-run` to commit.

---

## 10. Film Scoring Prep

**Goal:** Lock timing to picture while preserving expression.

```bash
python midi_clean.py cue_sketch.mid cue_final.mid \
  --quantize 1/32 \
  --legato-fix \
  --vel-scale 0.9 \
  --force-key Aminor
```

**Why:**
- Precise quantization syncs to picture
- Legato fix prevents articulation overlap
- Key forcing ensures harmonic continuity
- Velocity scaling matches orchestral dynamics
