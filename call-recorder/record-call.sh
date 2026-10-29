#!/bin/bash
# record-call.sh — record both sides of a WhatsApp/VoIP call on this Mac, then transcribe.
#
# HOW IT WORKS
#   ffmpeg opens TWO avfoundation inputs at once and merges them into one stereo file:
#     LEFT  = your microphone            (your voice)
#     RIGHT = BlackHole 2ch              (everything the Mac plays, i.e. the far end)
#
#   Keeping the two parties on SEPARATE CHANNELS is the point. transcribe_call.py sends
#   each channel to Soniox on its own, so who said what comes from the wiring, not from
#   diarization guesswork. (soniox/transcribe.py would downmix to mono and lose this.)
#
#   This is why there is no Aggregate Device to build: ffmpeg does the merge, so the
#   only thing you set up by hand is the Multi-Output Device (so you can still HEAR
#   the call while BlackHole captures it).
#
# ONE-TIME SETUP: see SETUP.md (Multi-Output Device = speakers/headphones + BlackHole 2ch,
#   selected as the system output before a call).
#
# USAGE
#   ./record-call.sh                 # record until Ctrl-C, then transcribe
#   ./record-call.sh --no-transcribe # just record
#   ./record-call.sh --seconds 10    # stop by itself after 10 s (for a test)
#   ./record-call.sh --list          # show audio devices and exit
#
# NOTE ON CONSENT: this records the other party. Tell them at the start of the call.

set -uo pipefail

# Recordings hold other people's voices: keep them out of this (public) repo.
OUT_DIR="${CALL_RECORDER_DIR:-$HOME/Documents/Call recordings}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SONIOX_PY="$HERE/../soniox/.venv/bin/python"   # key comes from soniox/.env
TRANSCRIBE=1
DURATION=()

while [ $# -gt 0 ]; do
  arg="$1"; shift
  case "$arg" in
    --no-transcribe) TRANSCRIBE=0 ;;
    --seconds) DURATION=(-t "$1"); shift ;;
    --list) ffmpeg -f avfoundation -list_devices true -i "" 2>&1 | sed -n '/audio devices/,$p'; exit 0 ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
  esac
done

# Resolve device indices by NAME, never by hard-coded number — avfoundation renumbers
# devices whenever anything is plugged in, and a wrong index silently records the
# wrong source (which you only discover when the transcript is half empty).
devices=$(ffmpeg -f avfoundation -list_devices true -i "" 2>&1 | sed -n '/audio devices/,$p')
mic_idx=$(echo "$devices"  | grep -iE '\[[0-9]+\].*(microphone|built-in|macbook)' | head -1 | sed -E 's/.*\[([0-9]+)\].*/\1/')
bh_idx=$(echo "$devices"   | grep -i  'BlackHole'                                  | head -1 | sed -E 's/.*\[([0-9]+)\].*/\1/')

if [ -z "${bh_idx:-}" ]; then
  echo "FATAL: BlackHole not found among audio devices."
  echo "Install it:  brew install --cask blackhole-2ch   (then log out and back in)"
  echo; echo "$devices"
  exit 1
fi
if [ -z "${mic_idx:-}" ]; then
  echo "FATAL: could not find a microphone. Devices seen:"; echo "$devices"; exit 1
fi

mkdir -p "$OUT_DIR"
stamp=$(date +%Y-%m-%d_%H%M%S)
wav="$OUT_DIR/call_$stamp.wav"

echo "mic         : device [$mic_idx]  -> LEFT channel"
echo "BlackHole   : device [$bh_idx]  -> RIGHT channel (far end)"
echo "recording to: $wav"
echo
echo "  >> Make sure the system output is your Multi-Output Device, or the far end"
echo "     will be silent in the recording (and you will not hear them either)."
echo
echo "Press Ctrl-C to stop."
echo

# A handler (not '' which the child would inherit as "ignore") keeps this script alive
# after Ctrl-C, so the transcription below still runs once ffmpeg has finished the file.
trap ':' INT

# Each source is made mono first, then joined as LEFT/RIGHT. (The old amerge + -ac 2
# merged the mic with BlackHole's two channels into three and downmixed them, so both
# channels came out identical; found on the first real test, 2026-10-29.)
# 16 kHz mono-per-channel is plenty for speech and keeps the file small.
ffmpeg -hide_banner -loglevel warning -stats \
  -f avfoundation -i ":$mic_idx" \
  -f avfoundation -i ":$bh_idx" \
  -filter_complex "[0:a]pan=mono|c0=c0[me];[1:a]pan=mono|c0=0.5*c0+0.5*c1[far];[me][far]join=inputs=2:channel_layout=stereo:map=0.0-FL|1.0-FR[a]" -map "[a]" \
  -ar 16000 -c:a pcm_s16le ${DURATION[@]+"${DURATION[@]}"} \
  "$wav" </dev/null
trap - INT

# ffmpeg exits non-zero on SIGINT; that is the normal way to stop, not a failure.
if [ ! -s "$wav" ]; then
  echo "No audio captured — the file is empty. Check the Multi-Output Device selection."
  exit 1
fi

size=$(du -h "$wav" | cut -f1)
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$wav" 2>/dev/null | cut -d. -f1)
echo; echo "saved: $wav  (${size}, ${dur:-?}s)"

if [ "$TRANSCRIBE" = "1" ]; then
  echo "transcribing each channel (Soniox EU)..."
  "$SONIOX_PY" "$HERE/transcribe_call.py" "$wav" "$OUT_DIR"
fi
