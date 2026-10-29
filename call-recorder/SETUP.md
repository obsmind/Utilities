# Call recorder: setup and use

Records both sides of a WhatsApp (or any VoIP) call on this Mac into one stereo file:
LEFT = the Mac's microphone (you), RIGHT = whatever the Mac plays (the other side,
captured by BlackHole). `transcribe_call.py` then transcribes each channel on its own,
so the transcript says who spoke from the wiring, not from guessing.

## One-time setup

1. **BlackHole 2ch** must be installed (`brew install --cask blackhole-2ch`, then log
   out and back in). `./record-call.sh --list` should show `BlackHole 2ch`.
2. **Multi-Output Device**, so you still hear the call while BlackHole copies it:
   1. Open **Audio MIDI Setup** (Applications → Utilities).
   2. Click **+** at the bottom left → **Create Multi-Output Device**.
   3. Tick your speakers or headphones **first**, then **BlackHole 2ch**.
   4. Set **Primary Device** to the speakers/headphones. In the **Sync** column
      BlackHole 2ch then shows a blue lock (drift correction on); the primary device's
      clock icon stays grey, because it is the reference. Nothing to click there.
   5. Optional: double-click the name and call it `Call recording`.

## Each call

1. Make the Multi-Output Device the output: Control Center → Sound, or
   System Settings → Sound → Output. (The volume keys don't work on a Multi-Output
   Device: set the volume on the speakers/headphones before switching.)
2. Tell the other side the call is being recorded.
3. Start recording, then the call:
   ```
   ~/Projects/Utilities/call-recorder/record-call.sh
   ```
4. Ctrl-C after the call. The transcript is written next to the recording.
5. Switch the output back to your speakers/headphones.

Recordings and transcripts go to `~/Documents/Call recordings/` (override with
`CALL_RECORDER_DIR`). They are kept out of this repo because it is public.

## Traps

- **Switch the output back after the call.** While the Multi-Output Device is the
  default output, apps that use macOS voice processing on the mic (echo cancellation)
  can fail to start their audio: TypeWhisper dictation failed with avfaudio error
  560227702 ('!dev') on 2026-10-29 until the output was changed back.

- **The mic channel is the Mac's built-in microphone.** If you take the call on
  AirPods or a headset mic, your side is recorded from the built-in mic instead, which
  works only if it can still hear you.
- **Headphones give the cleanest result.** On speakers the built-in mic also hears the
  other side (the capture has no echo cancellation). `transcribe_call.py` drops a left
  line that repeats an overlapping right line, which fixed the 2026-10-29 test, but
  partial echoes and crosstalk can still slip through.
- **No sound on the right channel** means the output was not the Multi-Output Device.
- Test without a call: `./record-call.sh --seconds 6` while something plays.
