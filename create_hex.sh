#!/bin/bash

# ============================================================
#   RISC-V HEX GENERATION SCRIPT (Verilog + Raw Hex formats)
# ============================================================

if [ $# -ne 1 ]; then
    echo "Usage: $0 <path/to/file.s>"
    exit 1
fi

SRC_PATH="$1"
SRC_NAME="$(basename "$SRC_PATH")"
BASE_NAME="${SRC_NAME%.*}"        
SCRIPT_DIR="$(dirname "$0")"

LINKER_SCRIPT="${SCRIPT_DIR}/link.ld"

OUT_DIR="${BASE_NAME}"
mkdir -p "$OUT_DIR"

echo "==> Output directory: $OUT_DIR"

cp "$SRC_PATH" "$OUT_DIR/${BASE_NAME}.s"
cp "$LINKER_SCRIPT" "$OUT_DIR/link.ld"

cd "$OUT_DIR" || exit 1

# ============================================================
# Assemble + Link
# ============================================================

echo "==> Assembling..."
riscv-none-elf-as "${BASE_NAME}.s" -o "${BASE_NAME}.o"

echo "==> Linking..."
riscv-none-elf-ld -T link.ld "${BASE_NAME}.o" -o "${BASE_NAME}.elf"

# ============================================================
# METHOD A — Verilog-format hex using objcopy
# ============================================================

echo "==> Generating instr.hex (Verilog)..."
riscv-none-elf-objcopy -O verilog \
    --verilog-data-width=4 \
    --only-section=.text \
    "${BASE_NAME}.elf" instr.hex

echo "==> Generating data.hex (Verilog)..."
riscv-none-elf-objcopy -O verilog \
    --verilog-data-width=4 \
    --only-section=.data \
    "${BASE_NAME}.elf" data.hex

# ============================================================
# METHOD B — Raw Hex (simple 32-bit words, simulator-safe)
# ============================================================

echo "==> Creating RAW hex from full binary..."

riscv-none-elf-objcopy -O binary "${BASE_NAME}.elf" "${BASE_NAME}.bin"

echo "==> Full raw dump: full_raw.hex"
hexdump -ve '1/4 "%08x\n"' "${BASE_NAME}.bin" > ${BASE_NAME}_full_raw.hex

# Extract TEXT region only (0x0000–0x0FFF)
echo "==> instr_raw.hex (raw binary ONLY .text)..."
dd if="${BASE_NAME}.bin" bs=1 count=$((0x1000)) status=none \
| hexdump -ve '1/4 "%08x\n"' > ${BASE_NAME}_instr_raw.hex

# Extract DATA region (starting at 0x1000)
echo "==> data_raw.hex (raw binary ONLY .data)..."
dd if="${BASE_NAME}.bin" bs=1 skip=$((0x1000)) status=none \
| hexdump -ve '1/4 "%08x\n"' > ${BASE_NAME}_data_raw.hex

# ============================================================

echo "==> Completed!"
echo "Generated files:"
ls -l
