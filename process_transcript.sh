#!/bin/bash
# Quick script to process a transcript file

echo "🎯 The P.A. (Procrastinator's Assistant)"
echo "Processing transcript file..."
echo ""

# Check if file is provided
if [ -z "$1" ]; then
    echo "Usage: ./process_transcript.sh transcripts/your_file.txt"
    echo ""
    echo "Or process the example:"
    echo "./process_transcript.sh transcripts/meeting_transcript_example.txt"
    exit 1
fi

# Process the file
python3 -m meeting_router.main --process-file "$1"

echo ""
echo "✅ Done! Check the dashboard at http://localhost:8000"
