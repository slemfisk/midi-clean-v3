#!/usr/bin/env python3
"""
MIDI Clean V3
Algorithmic MIDI Reconstruction for Production-Grade Workflows

Command-line utility for surgical MIDI reconstruction with deterministic
quantization, harmonic forcing, velocity conditioning, and vertical alignment.
"""

import argparse
import sys
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

try:
    import mido
    from mido import MidiFile, MidiTrack, Message, MetaMessage
except ImportError:
    print("Error: mido library not found. Install with: pip install mido python-rtmidi")
    sys.exit(1)


# Musical constants
SCALE_PATTERNS = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'aeolian': [0, 2, 3, 5, 7, 8, 10],
    'locrian': [0, 1, 3, 5, 6, 8, 10],
}

NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']


@dataclass
class NoteEvent:
    """Represents a MIDI note with timing and velocity."""
    pitch: int
    velocity: int
    start_tick: int
    end_tick: int
    channel: int
    track_idx: int


class MIDIProcessor:
    """Core MIDI reconstruction engine."""
    
    def __init__(self, midi_file: MidiFile, args: argparse.Namespace):
        self.midi = midi_file
        self.args = args
        self.ticks_per_beat = midi_file.ticks_per_beat
        self.notes: List[NoteEvent] = []
        
    def parse_notes(self) -> List[NoteEvent]:
        """Extract note events from MIDI file."""
        notes = []
        active_notes = {}  # (track, channel, pitch) -> start_tick
        
        for track_idx, track in enumerate(self.midi.tracks):
            current_tick = 0
            
            for msg in track:
                current_tick += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    key = (track_idx, msg.channel, msg.note)
                    active_notes[key] = current_tick
                    
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    key = (track_idx, msg.channel, msg.note)
                    if key in active_notes:
                        start_tick = active_notes.pop(key)
                        notes.append(NoteEvent(
                            pitch=msg.note,
                            velocity=msg.velocity if msg.type == 'note_on' else 64,
                            start_tick=start_tick,
                            end_tick=current_tick,
                            channel=msg.channel,
                            track_idx=track_idx
                        ))
        
        return notes
    
    def get_quantize_ticks(self, division: str) -> int:
        """Convert division string (e.g., '1/16') to tick resolution."""
        numerator, denominator = map(int, division.split('/'))
        return int(self.ticks_per_beat * 4 * numerator / denominator)
    
    def quantize_tick(self, tick: int, grid_ticks: int) -> int:
        """Quantize a tick value to nearest grid division."""
        return round(tick / grid_ticks) * grid_ticks
    
    def straighten_chords(self, notes: List[NoteEvent], window_ticks: int = 20) -> List[NoteEvent]:
        """Align vertically staggered chord notes to their average onset."""
        if not notes:
            return notes
        
        # Group notes by temporal proximity
        sorted_notes = sorted(notes, key=lambda n: n.start_tick)
        clusters = []
        current_cluster = [sorted_notes[0]]
        
        for note in sorted_notes[1:]:
            if note.start_tick - current_cluster[-1].start_tick <= window_ticks:
                current_cluster.append(note)
            else:
                clusters.append(current_cluster)
                current_cluster = [note]
        clusters.append(current_cluster)
        
        # Align each cluster to mean onset
        aligned_notes = []
        for cluster in clusters:
            if len(cluster) > 1:
                mean_onset = sum(n.start_tick for n in cluster) // len(cluster)
                for note in cluster:
                    duration = note.end_tick - note.start_tick
                    note.start_tick = mean_onset
                    note.end_tick = mean_onset + duration
            aligned_notes.extend(cluster)
        
        return aligned_notes
    
    def apply_swing(self, notes: List[NoteEvent], swing_amount: float) -> List[NoteEvent]:
        """Apply swing timing offset to off-beat notes."""
        grid_ticks = self.get_quantize_ticks('1/16')
        
        for note in notes:
            beat_position = note.start_tick % (grid_ticks * 2)
            if beat_position >= grid_ticks * 0.9:  # Off-beat detection
                offset = int(grid_ticks * swing_amount)
                duration = note.end_tick - note.start_tick
                note.start_tick += offset
                note.end_tick = note.start_tick + duration
        
        return notes
    
    def humanize_timing(self, notes: List[NoteEvent], amount: int = 10) -> List[NoteEvent]:
        """Add micro-timing variance to note onsets."""
        for note in notes:
            offset = random.randint(-amount, amount)
            duration = note.end_tick - note.start_tick
            note.start_tick = max(0, note.start_tick + offset)
            note.end_tick = note.start_tick + duration
        
        return notes
    
    def scale_velocity(self, notes: List[NoteEvent], scale: float) -> List[NoteEvent]:
        """Scale all velocities by a factor."""
        for note in notes:
            note.velocity = max(1, min(127, int(note.velocity * scale)))
        return notes
    
    def clamp_velocity(self, notes: List[NoteEvent], min_vel: int, max_vel: int) -> List[NoteEvent]:
        """Clamp velocities to specified range."""
        for note in notes:
            note.velocity = max(min_vel, min(max_vel, note.velocity))
        return notes
    
    def humanize_velocity(self, notes: List[NoteEvent], variance: int = 15) -> List[NoteEvent]:
        """Add random variance to velocity values."""
        for note in notes:
            offset = random.randint(-variance, variance)
            note.velocity = max(1, min(127, note.velocity + offset))
        return notes
    
    def parse_key(self, key_str: str) -> Tuple[int, str]:
        """Parse key string like 'Dminor' into (root, mode)."""
        key_str = key_str.replace(' ', '').lower()
        
        # Extract mode
        mode = 'major'
        for scale_mode in SCALE_PATTERNS.keys():
            if key_str.endswith(scale_mode):
                mode = scale_mode
                key_str = key_str[:-len(scale_mode)]
                break
        
        # Parse root note
        root_map = {name.lower(): i for i, name in enumerate(NOTE_NAMES)}
        root = root_map.get(key_str, 0)
        
        return root, mode
    
    def force_to_scale(self, notes: List[NoteEvent], root: int, mode: str) -> List[NoteEvent]:
        """Constrain all notes to specified scale."""
        scale_degrees = SCALE_PATTERNS[mode]
        scale_notes = [(root + degree) % 12 for degree in scale_degrees]
        
        for note in notes:
            pitch_class = note.pitch % 12
            if pitch_class not in scale_notes:
                # Find nearest scale tone
                distances = [(abs(pitch_class - sc), sc) for sc in scale_notes]
                distances.sort()
                nearest = distances[0][1]
                
                # Calculate shift
                shift = nearest - pitch_class
                if shift > 6:
                    shift -= 12
                elif shift < -6:
                    shift += 12
                
                note.pitch = max(0, min(127, note.pitch + shift))
        
        return notes
    
    def deduplicate(self, notes: List[NoteEvent]) -> List[NoteEvent]:
        """Remove duplicate notes at same time/pitch."""
        seen = set()
        unique_notes = []
        
        for note in notes:
            key = (note.pitch, note.start_tick, note.channel)
            if key not in seen:
                seen.add(key)
                unique_notes.append(note)
        
        return unique_notes
    
    def fix_legato(self, notes: List[NoteEvent]) -> List[NoteEvent]:
        """Repair overlapping notes of same pitch."""
        # Group by channel and pitch
        pitch_groups = defaultdict(list)
        for note in notes:
            pitch_groups[(note.channel, note.pitch)].append(note)
        
        fixed_notes = []
        for group in pitch_groups.values():
            sorted_group = sorted(group, key=lambda n: n.start_tick)
            
            for i in range(len(sorted_group) - 1):
                current = sorted_group[i]
                next_note = sorted_group[i + 1]
                
                # If overlap detected, trim current note
                if current.end_tick > next_note.start_tick:
                    current.end_tick = next_note.start_tick
            
            fixed_notes.extend(sorted_group)
        
        return fixed_notes
    
    def process(self) -> List[NoteEvent]:
        """Apply all enabled processing steps."""
        print(f"Parsing MIDI file...")
        notes = self.parse_notes()
        print(f"  Found {len(notes)} notes")
        
        # Timing operations
        if self.args.straighten:
            print("  Straightening chords...")
            notes = self.straighten_chords(notes)
        
        if self.args.quantize:
            print(f"  Quantizing to {self.args.quantize}...")
            grid_ticks = self.get_quantize_ticks(self.args.quantize)
            for note in notes:
                duration = note.end_tick - note.start_tick
                note.start_tick = self.quantize_tick(note.start_tick, grid_ticks)
                note.end_tick = note.start_tick + duration
        
        if self.args.swing:
            print(f"  Applying swing ({self.args.swing})...")
            notes = self.apply_swing(notes, self.args.swing)
        
        if self.args.humanize:
            print("  Humanizing timing...")
            notes = self.humanize_timing(notes)
        
        # Velocity operations
        if self.args.vel_scale:
            print(f"  Scaling velocity by {self.args.vel_scale}...")
            notes = self.scale_velocity(notes, self.args.vel_scale)
        
        if self.args.vel_clamp:
            min_v, max_v = self.args.vel_clamp
            print(f"  Clamping velocity to {min_v}-{max_v}...")
            notes = self.clamp_velocity(notes, min_v, max_v)
        
        if self.args.vel_human:
            print("  Humanizing velocity...")
            notes = self.humanize_velocity(notes)
        
        # Reconstruction operations
        if self.args.force_key:
            root, mode = self.parse_key(self.args.force_key)
            print(f"  Forcing to {NOTE_NAMES[root]} {mode}...")
            notes = self.force_to_scale(notes, root, mode)
        
        if self.args.dedupe:
            print("  Removing duplicates...")
            original_count = len(notes)
            notes = self.deduplicate(notes)
            print(f"    Removed {original_count - len(notes)} duplicates")
        
        if self.args.legato_fix:
            print("  Fixing legato overlaps...")
            notes = self.fix_legato(notes)
        
        return notes
    
    def reconstruct_midi(self, notes: List[NoteEvent]) -> MidiFile:
        """Rebuild MIDI file from processed notes."""
        new_midi = MidiFile(ticks_per_beat=self.ticks_per_beat)
        
        # Group notes by track
        track_notes = defaultdict(list)
        for note in notes:
            track_notes[note.track_idx].append(note)
        
        # Recreate tracks
        for track_idx in range(len(self.midi.tracks)):
            new_track = MidiTrack()
            new_midi.tracks.append(new_track)
            
            # Copy meta messages from original track
            for msg in self.midi.tracks[track_idx]:
                if msg.is_meta:
                    new_track.append(msg.copy())
            
            # Add processed notes
            if track_idx in track_notes:
                events = []
                
                for note in track_notes[track_idx]:
                    events.append((note.start_tick, 'note_on', note))
                    events.append((note.end_tick, 'note_off', note))
                
                events.sort(key=lambda x: (x[0], x[1] == 'note_off'))  # note_on before note_off
                
                current_tick = 0
                for tick, event_type, note in events:
                    delta = tick - current_tick
                    
                    if event_type == 'note_on':
                        new_track.append(Message(
                            'note_on',
                            note=note.pitch,
                            velocity=note.velocity,
                            time=delta,
                            channel=note.channel
                        ))
                    else:
                        new_track.append(Message(
                            'note_off',
                            note=note.pitch,
                            velocity=0,
                            time=delta,
                            channel=note.channel
                        ))
                    
                    current_tick = tick
        
        return new_midi


def main():
    parser = argparse.ArgumentParser(
        description='MIDI Clean V3 - Algorithmic MIDI Reconstruction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python midi_clean.py input.mid output.mid --quantize 1/16
  python midi_clean.py take.mid clean.mid --straighten --vel-scale 0.8
  python midi_clean.py score.mid out.mid --quantize 1/32 --straighten --dedupe
        """
    )
    
    # Input/Output
    parser.add_argument('input', type=str, help='Source MIDI file')
    parser.add_argument('output', type=str, help='Destination MIDI file')
    parser.add_argument('--overwrite', action='store_true', help='Replace existing output')
    parser.add_argument('--dry-run', action='store_true', help='Execute logic without writing')
    
    # Timing
    parser.add_argument('--quantize', type=str, metavar='DIV',
                       help='Grid-lock notes to division (e.g., 1/16, 1/32)')
    parser.add_argument('--straighten', action='store_true',
                       help='Align chord onsets vertically')
    parser.add_argument('--swing', type=float, metavar='AMT',
                       help='Apply swing offset (0.0-1.0)')
    parser.add_argument('--humanize', action='store_true',
                       help='Inject micro-timing variance')
    
    # Dynamics
    parser.add_argument('--vel-scale', type=float, metavar='X',
                       help='Scale velocities by factor')
    parser.add_argument('--vel-clamp', type=int, nargs=2, metavar=('MIN', 'MAX'),
                       help='Clamp velocity range')
    parser.add_argument('--vel-human', action='store_true',
                       help='Randomize velocity')
    
    # Reconstruction
    parser.add_argument('--force-key', type=str, metavar='KEY',
                       help='Constrain notes to scale (e.g., Dminor, Fmajor)')
    parser.add_argument('--dedupe', action='store_true',
                       help='Remove stacked duplicates')
    parser.add_argument('--legato-fix', action='store_true',
                       help='Repair overlapping notes')
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Check output
    output_path = Path(args.output)
    if output_path.exists() and not args.overwrite and not args.dry_run:
        print(f"Error: Output file exists: {args.output}")
        print("Use --overwrite to replace")
        sys.exit(1)
    
    # Load and process
    try:
        print(f"Loading: {args.input}")
        midi_file = MidiFile(args.input)
        
        processor = MIDIProcessor(midi_file, args)
        processed_notes = processor.process()
        
        if args.dry_run:
            print("\n[DRY RUN] No file written")
            print(f"Would output {len(processed_notes)} notes to: {args.output}")
        else:
            print(f"\nReconstructing MIDI file...")
            new_midi = processor.reconstruct_midi(processed_notes)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            new_midi.save(args.output)
            print(f"✓ Saved: {args.output}")
        
    except Exception as e:
        print(f"Error processing MIDI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
