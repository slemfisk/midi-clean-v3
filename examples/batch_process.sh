#!/bin/bash
# Batch MIDI processing script for Unix/Linux/macOS

set -e

INPUT_DIR="${1:-.}"
OUTPUT_DIR="${2:-processed}"

echo "MIDI Clean V3 - Batch Processor"
echo "================================"
echo "Input:  $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Count files
total=$(find "$INPUT_DIR" -maxdepth 1 -name "*.mid" -o -name "*.midi" | wc -l)
current=0

echo "Found $total MIDI files"
echo ""

# Process each MIDI file
for file in "$INPUT_DIR"/*.mid "$INPUT_DIR"/*.midi; do
    [ -e "$file" ] || continue
    
    current=$((current + 1))
    filename=$(basename "$file")
    
    echo "[$current/$total] Processing: $filename"
    
    python midi_clean.py "$file" "$OUTPUT_DIR/$filename" \
        --quantize 1/16 \
        --straighten \
        --vel-scale 0.9 \
        --dedupe
    
    echo ""
done

echo "✓ Batch processing complete"
echo "  Processed: $current files"
echo "  Output: $OUTPUT_DIR/"
