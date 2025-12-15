.section .data
	.align 2
a:  .word 10

.section .text
.globl main
main:
	la x13, a
	lw x11, 0(x13)     # a
	li x10, 0          # result
	li x28, 3          # divisor
	li t1, 2

	ble x11, t1, not_prime  # n <= 2 => not prime
	beq x11, t1, prime      # n == 2 => prime
	beqz x11, not_prime     # n == 0 => not prime

	rem x30, x11, t1
	beqz x30, not_prime

loop:
	mul x31, x28, x28
	bgt x31, x11, prime
	rem x30, x11, x28
	beqz x30, not_prime
	addi x28, x28, 2
	j loop

prime:
	li x10, 1
	j done

not_prime:
	li x10, -1

done:
	j done
