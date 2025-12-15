MEMORY
{
  IMEM (rx)  : ORIGIN = 0x00000000, LENGTH = 4K
  DMEM (rw)  : ORIGIN = 0x00001000, LENGTH = 4K
}

SECTIONS
{
  .text : ALIGN(4) {
    *(.text*)
  } > IMEM

  .rodata : ALIGN(4) {
    *(.rodata*)
  } > DMEM

  .data : ALIGN(4) {
    *(.data*)
  } > DMEM
}
