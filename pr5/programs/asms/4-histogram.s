.section .data
	.align 2
count:
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
	.word 0
marks:
	.word 2
	.word 3
	.word 0
	.word 5
	.word 10
	.word 7
	.word 1
	.word 10
	.word 10
	.word 8
	.word 9
	.word 6
	.word 7
	.word 8
	.word 2
	.word 4
	.word 5
	.word 0
	.word 9
	.word 1
n:
	.word 20

.section .text
.globl main
main:
	la t0, marks       
	lw t1, n           
  	la t2, count       

loop:
    	beq t1, x0, halt
    	lw t3, 0(t0)		# mark [i]
    	li t4, 4
    	mul t5, t3, t4		# mark * 4 = no of bytes from base to this mark's location
    	add t5, t2, t5		# t5 has location of count [i] now
    	
    	lw t6, 0(t5)
    	addi t6, t6, 1
    	sw t6, 0(t5)		# load count[marks[i]], increment it by 1, store it back in same address
    	
    	addi t0, t0, 4
    	addi t1, t1, -1
    	
    	j loop



halt:
	j halt
