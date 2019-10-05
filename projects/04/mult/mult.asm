// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)


	// a = R0
	@R0
	D=M
	@a
	M=D

	// i = R1
	@R1
	D=M
	@i
	M=D

	// sum = 0
	@sum
	M=0

(LOOP)

	// if i == 0 write result
	@i
	D=M
	@WRITE
	D;JEQ

	// otherwise
	// sum += a
	@a
	D=M
	@sum
	M=M+D

	// i--
	@i
	M=M-1

	@LOOP
	0;JMP


(WRITE)

	// R2 = sum
	@sum
	D=M
	@R2
	M=D

(END)

	@END
	0;JMP