#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/references/papers"
FAILED_LOG="$ROOT_DIR/references/download_failed.txt"
mkdir -p "$OUT_DIR"
: > "$FAILED_LOG"

# URL<TAB>OUTPUT
readarray -t ITEMS <<'LINES'
https://arxiv.org/pdf/1801.07698.pdf	ArcFace_Additive_Angular_Margin_Loss.pdf
https://arxiv.org/pdf/1801.09414.pdf	CosFace_Large_Margin_Cosine_Loss.pdf
https://arxiv.org/pdf/1503.03832.pdf	FaceNet_Unified_Embedding.pdf
https://arxiv.org/pdf/1704.08063.pdf	SphereFace_Angular_Softmax_Loss.pdf
https://arxiv.org/pdf/1907.04047.pdf	Silent-Face_Anti-Spoofing.pdf
https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63-3.pdf	NIST_SP_800-63-3_Digital_Identity_Guidelines.pdf
https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8525.pdf	NIST_IR_8525_FRTE_1N_Identification.pdf
LINES

ok=0
fail=0

for row in "${ITEMS[@]}"; do
  url="${row%%$'\t'*}"
  output="${row##*$'\t'}"
  echo "[download] $output"
  if curl -fL --retry 2 --connect-timeout 20 "$url" -o "$OUT_DIR/$output"; then
    ok=$((ok + 1))
  else
    fail=$((fail + 1))
    rm -f "$OUT_DIR/$output"
    echo "$url -> $output" >> "$FAILED_LOG"
    echo "  [warn] failed"
  fi
done

echo "Done. success=$ok failed=$fail"
if [[ $fail -gt 0 ]]; then
  echo "Failed list: $FAILED_LOG"
fi
