.section .data
.global myArr
	 .align 2
	 
myArr:
	.skip 40	# this allocated 40bytes, (i.e) 10 words * 4 bytes


.section .text
.globl main
main:
	la x5, myArr
	li x6, 10
	li x7, 0x0003
	
loop:
	sw x7, 0(x5)
	addi x5, x5, 4	# go to next array element, (i.e) x[i+1]
	addi x6, x6, -1	# decreasing the loop, (i.e) i--
	bnez x6, loop	# when i!=0, loop iterates


halt:
	j halt

