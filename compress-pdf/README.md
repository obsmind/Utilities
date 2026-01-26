# Compress PDF (Ghostscript /ebook)

Compress PDFs in place using Ghostscript. Includes:
- a CLI script, and
- a Finder Quick Action (Automator workflow) that overwrites the original file.

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

Default is `/ebook`.

## Quick Action setup

1) Copy the workflow into your Services folder:

```
cp -R "automator/Compress PDF.workflow" "$HOME/Library/Services/"
```

2) Relaunch Finder so it picks up the Quick Action.
3) Right-click a PDF in Finder → Quick Actions → Compress PDF.

### Permissions (macOS)
If you see "Operation not permitted" while overwriting:
- System Settings → Privacy & Security → Full Disk Access
- Add and enable:
  - `/System/Applications/Automator.app`
  - `/System/Library/CoreServices/Automator Application Stub.app`

### Logs
The Quick Action logs to:
`~/Library/Logs/CompressPDF.log`

## Notes
- The Quick Action overwrites the original PDF.
- For locked files, unlock in Finder (Get Info → Locked).
