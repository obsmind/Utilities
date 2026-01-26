# Compress PDF (Ghostscript /ebook)

Fast, local PDF compression for macOS. Includes:
- a CLI script for batch use, and
- a Finder Quick Action (Automator workflow) for one-click compression.

Use cases:
- shrink manuals before emailing or uploading
- reduce archive size without leaving macOS
- keep a quick, repeatable compression workflow

## Requirements
- Ghostscript installed via Homebrew: `brew install ghostscript`

## CLI usage

```bash
./scripts/compress_pdf.sh "/path/to/file.pdf"
```

Optional quality override:

```bash
PDFSETTINGS=/screen ./scripts/compress_pdf.sh "file.pdf"
```

Default is `/ebook`. Common alternatives:
- `/screen` smaller files, lower quality
- `/printer` higher quality, larger files
- `/prepress` highest quality, largest files

## Quick Action setup

1) Copy the workflow into your Services folder:

```
cp -R "automator/Compress PDF.workflow" "$HOME/Library/Services/"
```

2) Relaunch Finder so it picks up the Quick Action.
3) Right-click a PDF in Finder → Quick Actions → Compress PDF.

The Quick Action overwrites the original file in place.

### Permissions (macOS)
If you see "Operation not permitted" while overwriting:
- System Settings → Privacy & Security → Full Disk Access
- Add and enable:
  - `/System/Applications/Automator.app`
  - `/System/Library/CoreServices/Automator Application Stub.app`

### Logs
The Quick Action logs to:
`~/Library/Logs/CompressPDF.log`

### Troubleshooting
- If nothing happens, relaunch Finder to reload the workflow.
- If overwrite fails, confirm the file is not locked and re-check Full Disk Access.

## Notes
- For locked files, unlock in Finder (Get Info → Locked).
