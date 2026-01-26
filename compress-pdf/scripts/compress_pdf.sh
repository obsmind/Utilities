#!/bin/zsh
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $(basename "$0") <file1.pdf> [file2.pdf ...]" >&2
  exit 1
fi

GS="/opt/homebrew/bin/gs"
if [[ ! -x "$GS" ]]; then
  if [[ -x "/usr/local/bin/gs" ]]; then
    GS="/usr/local/bin/gs"
  else
    GS="$(command -v gs || true)"
  fi
fi
if [[ -z "${GS:-}" ]]; then
  echo "Ghostscript (gs) not found. Install with: brew install ghostscript" >&2
  exit 1
fi

PDFSETTINGS="${PDFSETTINGS:-/ebook}"

ok_count=0
fail_count=0

for inpath in "$@"; do
  if [[ ! -f "$inpath" ]]; then
    echo "Missing file: $inpath" >&2
    fail_count=$((fail_count + 1))
    continue
  fi

  if [[ "${inpath:l}" != *.pdf ]]; then
    echo "Skipping non-PDF: $inpath" >&2
    continue
  fi

  dir="${inpath:h}"
  base="${inpath:t:r}"
  tmpdir="$(mktemp -d -t compresspdf)"
  tmp="$tmpdir/out.pdf"

  if "$GS" -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dBATCH \
      -dPDFSETTINGS=${PDFSETTINGS} \
      -sOutputFile="$tmp" "$inpath"; then
    mv -f "$tmp" "$inpath"
    ok_count=$((ok_count + 1))
  else
    rm -f "$tmp"
    echo "Ghostscript failed: $inpath" >&2
    fail_count=$((fail_count + 1))
  fi

  rm -rf "$tmpdir"
done

if (( fail_count > 0 )); then
  echo "Done: ok=${ok_count} fail=${fail_count}" >&2
  exit 1
fi

echo "Done: ok=${ok_count}"
