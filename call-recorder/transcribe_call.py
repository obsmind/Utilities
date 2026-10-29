#!/usr/bin/env python3
"""
transcribe_call.py — transcribe a stereo call recording made by record-call.sh.

The recorder puts the two parties on separate channels (LEFT = this Mac's mic,
RIGHT = the far end via BlackHole). soniox/transcribe.py would downmix that to mono
and guess speakers; this script keeps the split instead: each channel is transcribed
on its own, so "who said what" comes from the wiring, not from diarization.

Usage (with the soniox venv's python):
    ~/Projects/Utilities/soniox/.venv/bin/python transcribe_call.py <call.wav> [output_dir] [--me NAME]

Writes <stem> transcript.md and <stem> soniox raw.json next to the recording
(or in output_dir).
"""

import difflib
import json
import pathlib
import re
import subprocess
import sys
import tempfile

SONIOX_DIR = pathlib.Path(__file__).resolve().parent.parent / "soniox"
sys.path.insert(0, str(SONIOX_DIR))
import transcribe as sx  # noqa: E402  (reuses its key lookup and API calls)

# A pause longer than this starts a new line for the same speaker.
GAP_MS = 1500


def split_channel(wav: str, channel: int, out: pathlib.Path) -> str:
    path = out / f"ch{channel}.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
         "-af", f"pan=mono|c0=c{channel}", "-ar", "16000", "-c:a", "pcm_s16le", str(path)],
        check=True,
    )
    return str(path)


def utterances(tokens: list, label_for) -> list:
    """Group one channel's tokens into (start_ms, label, lang, text) lines."""
    out, cur = [], None
    for t in tokens:
        if t.get("is_audio_event") or not t.get("text", "").strip():
            continue
        label = label_for(t)
        start, end = t.get("start_ms", 0), t.get("end_ms", t.get("start_ms", 0))
        if cur and cur["label"] == label and start - cur["end"] <= GAP_MS:
            cur["text"].append(t["text"])
            cur["end"] = end
        else:
            if cur:
                out.append(cur)
            cur = {"start": start, "end": end, "label": label,
                   "lang": t.get("language", ""), "text": [t["text"]]}
    if cur:
        out.append(cur)
    return out


def words(u) -> list:
    return re.findall(r"\w+", "".join(u["text"]).lower())


def is_echo(u, far: list) -> bool:
    """On speakers the Mac's mic also hears the other side (the capture has no echo
    cancellation), so their words show up on the left channel too. Drop a left line
    that repeats an overlapping right line. Short lines ("ok", "yes") are kept: those
    are as likely to be a real reply."""
    mine = words(u)
    if len(mine) < 3:
        return False
    for f in far:
        if f["start"] - 2000 <= u["start"] <= f["end"] + 2000:
            if difflib.SequenceMatcher(None, mine, words(f)).ratio() >= 0.7:
                return True
    return False


def main():
    args = [a for a in sys.argv[1:]]
    # Label for the mic side: --me, else the first name of this Mac's user account.
    full = subprocess.run(["id", "-F"], capture_output=True, text=True).stdout.split()
    me = full[0] if full else "Me"
    if "--me" in args:
        i = args.index("--me")
        me = args[i + 1]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        sys.exit(1)

    wav = args[0]
    stem = sx.safe_filename(pathlib.Path(wav).stem)
    out_dir = pathlib.Path(args[1]) if len(args) > 1 else pathlib.Path(wav).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    key = sx.resolve_api_key()
    if not key:
        print("SONIOX_API_KEY not found (see soniox/transcribe.py for where it looks).")
        sys.exit(1)

    jobs = {}
    with tempfile.TemporaryDirectory() as tmp:
        for ch in (0, 1):
            file_id = sx.upload_file(key, split_channel(wav, ch, pathlib.Path(tmp)))
            jobs[ch] = (file_id, sx.create_transcription(key, file_id))

    tokens = {}
    for ch, (file_id, job_id) in jobs.items():
        sx.poll_until_done(key, job_id)
        tokens[ch] = sx.get_transcript_tokens(key, job_id)
        sx.delete_file(key, file_id)

    # The far end can be several people (a group call), so keep diarization there.
    far_speakers = {t.get("speaker") for t in tokens[1] if t.get("text", "").strip()}

    def far_label(t):
        return "Other side" if len(far_speakers) <= 1 else f"Other side {t.get('speaker', '?')}"

    far = utterances(tokens[1], far_label)
    mine = [u for u in utterances(tokens[0], lambda t: me) if not is_echo(u, far)]
    lines = mine + far
    lines.sort(key=lambda u: u["start"])

    md = [f"# Call transcript: {pathlib.Path(wav).name}\n",
          f"Left channel = {me} (this Mac's microphone), right channel = the other side.\n"]
    for u in lines:
        text = "".join(u["text"]).strip()
        lang = f" `{u['lang']}`" if u["lang"] else ""
        md.append(f"\n**[{sx.ms_to_hms(u['start'])}] {u['label']}{lang}:**  \n{text}\n")
    if not lines:
        md.append("\n_No speech found on either channel._\n")

    md_path = out_dir / f"{stem} transcript.md"
    md_path.write_text("".join(md), encoding="utf-8")
    raw_path = out_dir / f"{stem} soniox raw.json"
    raw_path.write_text(json.dumps(
        {"left": {"job_id": jobs[0][1], "tokens": tokens[0]},
         "right": {"job_id": jobs[1][1], "tokens": tokens[1]}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Transcript: {md_path}")


if __name__ == "__main__":
    main()
