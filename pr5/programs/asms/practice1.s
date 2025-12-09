.section .data
	 .align 2
.global sum
	 .align 2
	 
sum:
	.word 0

num1:
	.word 0x0003	#9
num2:
	.word 0x0002	#7
	 
.section .text

.global main

main:
	lw x1, num1
	lw x2, num2	
	la x13, sum

	add x11, x1, x2	#64
	
	sw x11, 0(x13)
	
halt:
	j halt
